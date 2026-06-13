from functools import lru_cache
from pathlib import Path
import re

import numpy as np
import pandas as pd

from model.feedback_rules import build_suggestions

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "ielts_task2_multitask.csv"
DEFAULT_ARTIFACT_PATH = Path(__file__).resolve().parent / "artifacts" / "ielts_task2_multitask_model.keras"

CRITERIA_KEYS = [
    "task_response",
    "coherence_cohesion",
    "lexical_resource",
    "grammar_range_accuracy",
]

REQUIRED_COLUMNS = [
    "question",
    "essay",
    "task_response",
    "coherence_cohesion",
    "lexical_resource",
    "grammar_range_accuracy",
    "overall_band",
]

OLD_COLUMN_NAMES = {
    "Question": "question",
    "Essay": "essay",
    "Task_Response": "task_response",
    "Coherence_Cohesion": "coherence_cohesion",
    "Lexical_Resource": "lexical_resource",
    "Range_Accuracy": "grammar_range_accuracy",
    "Overall": "overall_band",
}


def round_to_half_band(score):
    clipped = min(max(float(score), 0.0), 9.0)
    return round(clipped * 2) / 2


def word_count(text):
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", str(text)))


def clean_text(text):
    text = str(text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text).strip()


def build_model_input(question, essay):
    return f"Question: {clean_text(question)} Essay: {clean_text(essay)}"


# 【特征工程大升级】：加入精确对应雅思评分标准的专家特征
def extract_features(essay):
    essay_str = str(essay).lower()
    words = re.findall(r"\b\w+\b", essay_str)
    
    word_count_value = len(words)
    sentence_count = max(1, len(re.findall(r"[.!?]+", essay_str)))
    
    # 1. 词汇丰富度 (Unique Ratio)
    unique_ratio = len(set(words)) / max(word_count_value, 1)

    # 2. 平均句长 (Average Sentence Length - 对应 GRA/CC)
    avg_sentence_length = word_count_value / sentence_count

    # 3. 长词比例 (Long Word Ratio - 对应 Lexical Resource)
    long_word_count = sum(1 for word in words if len(word) >= 6)
    long_word_ratio = long_word_count / max(word_count_value, 1)

    # 4. 连接词数量 (Discourse Markers Count - 对应 Coherence & Cohesion)
    discourse_markers = [
        "however", "therefore", "moreover", 
        "furthermore", "in addition", "on the other hand"
    ]
    discourse_marker_count = 0
    for marker in discourse_markers:
        # 使用 \b 确保匹配的是完整的词或词组
        discourse_marker_count += len(re.findall(rf"\b{marker}\b", essay_str))

    # 依然必须做特征缩放 (Normalization)，否则网络无法收敛
    return [
        float(word_count_value) / 400.0,       # 假设常规作文 400 词左右
        float(unique_ratio),                   # 已经是 0~1
        float(avg_sentence_length) / 30.0,     # 假设最长平均句长 30 词左右
        float(long_word_ratio),                # 已经是 0~1
        float(discourse_marker_count) / 10.0,  # 假设常规作文最多用 10 个高级连接词
    ]


def prepare_numeric_features(df):
    return np.asarray(
        [extract_features(row.essay) for row in df.itertuples(index=False)],
        dtype=np.float32,
    )


def get_tensorflow():
    try:
        import tensorflow as tf
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("TensorFlow is not installed. Install requirements.txt first.") from exc
    return tf


def load_task2_dataframe(data_path=DEFAULT_DATA_PATH):
    data_path = Path(data_path)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset is missing: {data_path}")

    df = pd.read_csv(data_path).rename(columns=OLD_COLUMN_NAMES)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    df = df[REQUIRED_COLUMNS].dropna(subset=["question", "essay", "overall_band"]).copy()
    for column in ["overall_band", *CRITERIA_KEYS]:
        df[column] = pd.to_numeric(df[column], errors="coerce").clip(0, 9)

    df = df.dropna(subset=CRITERIA_KEYS).reset_index(drop=True)
    if df.empty:
        raise ValueError("Dataset has no usable Task 2 rows.")
    return df


def split_dataframe(df, test_size=0.2, random_state=42):
    rng = np.random.default_rng(random_state)
    indexes = np.arange(len(df))
    rng.shuffle(indexes)

    test_count = max(1, int(len(df) * test_size))
    test_indexes = indexes[:test_count]
    train_indexes = indexes[test_count:]
    return df.iloc[train_indexes].reset_index(drop=True), df.iloc[test_indexes].reset_index(drop=True)


def prepare_texts(df):
    return np.asarray(
        [build_model_input(row.question, row.essay) for row in df.itertuples(index=False)],
        dtype=object,
    )


def prepare_labels(df):
    return df[CRITERIA_KEYS].astype("float32").to_numpy() / 9.0


def build_tf_model(vectorizer):
    tf = get_tensorflow()

    # 文本输入
    text_input = tf.keras.Input(shape=(1,), dtype=tf.string, name="essay_text")

    # 【改动】：人工特征输入维度从 3 提升到了 5
    feature_input = tf.keras.Input(shape=(5,), dtype=tf.float32, name="numeric_features")

    x = vectorizer(text_input)
    x = tf.keras.layers.Embedding(input_dim=5000, output_dim=64, name="embedding")(x)
    x = tf.keras.layers.GlobalAveragePooling1D(name="average_pooling")(x)
    x = tf.keras.layers.Dense(128, activation="relu", name="dense_128")(x)

    # 特征分支
    f = tf.keras.layers.Dense(16, activation="relu", name="feature_dense")(feature_input)

    # 合并
    merged = tf.keras.layers.Concatenate()([x, f])
    merged = tf.keras.layers.Dense(64, activation="relu", name="dense_64")(merged)
    
    score_output = tf.keras.layers.Dense(4, activation="sigmoid", name="criteria_scores")(merged)

    model = tf.keras.Model(inputs=[text_input, feature_input], outputs=score_output)

    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.Huber(),
        metrics=["mae"]
    )

    return model


def mean_absolute_error(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=np.float32)
    y_pred = np.asarray(y_pred, dtype=np.float32)
    return float(np.mean(np.abs(y_true - y_pred)))


def train_model(data_path=DEFAULT_DATA_PATH, artifact_path=DEFAULT_ARTIFACT_PATH, random_state=42, epochs=30):
    tf = get_tensorflow()
    df = load_task2_dataframe(data_path)
    train_df, test_df = split_dataframe(df, test_size=0.2, random_state=random_state)

    train_texts = prepare_texts(train_df)
    test_texts = prepare_texts(test_df)
    
    train_features = prepare_numeric_features(train_df)
    test_features = prepare_numeric_features(test_df)

    y_train = prepare_labels(train_df)
    y_test = prepare_labels(test_df)

    vectorizer = tf.keras.layers.TextVectorization(
        max_tokens=5000,
        output_mode="int",
        output_sequence_length=350,
        name="text_vectorization",
    )
    vectorizer.adapt(train_texts)

    tf.keras.utils.set_random_seed(random_state)
    model = build_tf_model(vectorizer)

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=3,
        restore_best_weights=True,
        verbose=1,
    )

    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=2,
        min_lr=1e-5,
        verbose=1,
    )

    model.fit(
        [train_texts, train_features],
        y_train,
        validation_data=([test_texts, test_features], y_test),
        epochs=epochs,
        batch_size=32,
        callbacks=[early_stopping, reduce_lr],
        verbose=1,
    )

    predictions = model.predict([test_texts, test_features], verbose=0) * 9.0
    y_true = y_test * 9.0
    
    dimension_mae = {
        criterion: mean_absolute_error(y_true[:, index], predictions[:, index])
        for index, criterion in enumerate(CRITERIA_KEYS)
    }

    artifact_path = Path(artifact_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(artifact_path)

    return {
        "rows": int(len(df)),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "mae": mean_absolute_error(np.mean(y_true, axis=1), np.mean(predictions, axis=1)),
        "dimension_mae": dimension_mae,
        "artifact_path": str(artifact_path),
    }


@lru_cache(maxsize=1)
def load_model(artifact_path=str(DEFAULT_ARTIFACT_PATH)):
    tf = get_tensorflow()
    artifact_path = Path(artifact_path)
    if not artifact_path.exists():
        raise FileNotFoundError("Model file is missing. Please train the model first.")
    return tf.keras.models.load_model(artifact_path)


def predict_band(question, essay, artifact_path=DEFAULT_ARTIFACT_PATH):
    text = build_model_input(question, essay)
    model = load_model(str(artifact_path))
    
    features = np.asarray([extract_features(essay)], dtype=np.float32)

    prediction = model.predict(
        [
            np.asarray([text], dtype=object),
            features
        ],
        verbose=0
    )[0] * 9.0

    raw_scores = {}
    criteria_scores = {}
    for index, criterion in enumerate(CRITERIA_KEYS):
        score = min(max(float(prediction[index]), 0.0), 9.0)
        raw_scores[criterion] = round(score, 2)
        criteria_scores[criterion] = round_to_half_band(score)

    return {
        "overall_band": round_to_half_band(sum(criteria_scores.values()) / len(CRITERIA_KEYS)),
        "criteria_scores": criteria_scores,
        "raw_scores": raw_scores,
        "word_count": word_count(essay),
        "suggestions": build_suggestions(raw_scores),
        "model_info": {
            "model_type": "tensorflow_multitask_wide_deep",
            "target": "ielts_task2",
            "criteria_count": 4,
        },
    }