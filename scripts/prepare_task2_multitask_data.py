import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "ielts_writing_dataset.csv"
OUTPUT_DATA_PATH = PROJECT_ROOT / "data" / "ielts_task2_multitask.csv"

def prepare_clean_data():
    if not RAW_DATA_PATH.exists():
        print(f"Source file not found: {RAW_DATA_PATH}")
        return

    df = pd.read_csv(RAW_DATA_PATH)
    print(f"Initial data rows: {len(df)}")

    if 'Task_Type' in df.columns:
        df = df[df['Task_Type'] == 2].copy()
        print(f"Remaining after filtering Task 1: {len(df)}")


    df = df.drop_duplicates(subset=['Essay'], keep='first')
    print(f"Remaining after removing duplicates: {len(df)}")

    rename_mapping = {
        "Question": "question",
        "Essay": "essay",
        "Task_Response": "task_response",
        "Coherence_Cohesion": "coherence_cohesion",
        "Lexical_Resource": "lexical_resource",
        "Range_Accuracy": "grammar_range_accuracy",
        "Overall": "overall_band"
    }

    missing_cols = [col for col in rename_mapping.keys() if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df = df.rename(columns=rename_mapping)

    contract_columns = list(rename_mapping.values())
    df = df[contract_columns]

    df = df.dropna()

    OUTPUT_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_DATA_PATH, index=False)
    
    print(f"\nData cleaning completed! {len(df)} high-quality Task 2 samples preserved.")
    print(f"File saved to: {OUTPUT_DATA_PATH}")

if __name__ == "__main__":
    prepare_clean_data()