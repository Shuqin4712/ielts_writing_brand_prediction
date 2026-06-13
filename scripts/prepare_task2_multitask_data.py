import pandas as pd
from pathlib import Path

# 将路径定位到项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 【关键点1】源数据指向那个最高质量的文件
RAW_DATA_PATH = PROJECT_ROOT / "data" / "ielts_writing_dataset.csv"
# 输出数据严格遵循契约的路径
OUTPUT_DATA_PATH = PROJECT_ROOT / "data" / "ielts_task2_multitask.csv"

def prepare_clean_data():
    if not RAW_DATA_PATH.exists():
        print(f"找不到源文件: {RAW_DATA_PATH}")
        return

    # 读取原始数据
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"-> 初始读取数据量: {len(df)} 条")

    # 【关键点2】坚决过滤掉所有 Task 1 的小作文
    if 'Task_Type' in df.columns:
        df = df[df['Task_Type'] == 2].copy()
        print(f"-> 过滤 Task 1 后剩余: {len(df)} 条")

    # ================= 数据清洗 =================
    # 1. 杀掉所有重复作文（只保留第一篇），解决那 40 几条“同文不同分”的噪音
    df = df.drop_duplicates(subset=['Essay'], keep='first')
    print(f"-> 剔除重复文本后剩余: {len(df)} 条")
    
    # 注：已移除 `std > 0` 的过滤。因为在真实高质量数据中，四项同分（如全拿6.0）是正常现象。
    # ============================================

    # 【关键点3】重命名真实的考官小分列，严格匹配 INTERFACE_CONTRACT.md
    rename_mapping = {
        "Question": "question",
        "Essay": "essay",
        "Task_Response": "task_response",
        "Coherence_Cohesion": "coherence_cohesion",
        "Lexical_Resource": "lexical_resource",
        "Range_Accuracy": "grammar_range_accuracy", # 把原始表格的名称转为契约名称
        "Overall": "overall_band"
    }
    
    # 检查原始表格是否包含这些真实的列
    missing_cols = [col for col in rename_mapping.keys() if col not in df.columns]
    if missing_cols:
        raise ValueError(f"原始数据缺失关键列: {missing_cols}")

    df = df.rename(columns=rename_mapping)

    # 只提取我们需要的这 7 列
    contract_columns = list(rename_mapping.values())
    df = df[contract_columns]

    # 清理掉任何包含空值的脏数据
    df = df.dropna()

    # 导出给 TensorFlow 使用
    OUTPUT_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_DATA_PATH, index=False)
    
    print(f"\n✅ 数据清洗完成！最终共保留 {len(df)} 条高质量的 Task 2 数据。")
    print(f"文件已保存至: {OUTPUT_DATA_PATH}")

if __name__ == "__main__":
    prepare_clean_data()