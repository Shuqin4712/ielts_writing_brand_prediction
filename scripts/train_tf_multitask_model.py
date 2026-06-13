import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from model.tf_multitask_predictor import DEFAULT_ARTIFACT_PATH, DEFAULT_DATA_PATH, train_model


def main():
    parser = argparse.ArgumentParser(description="Train the IELTS Task 2 TensorFlow multitask scorer.")
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH), help="Path to data/ielts_task2_multitask.csv.")
    parser.add_argument("--output", default=str(DEFAULT_ARTIFACT_PATH), help="Path for the trained Keras model.")
    parser.add_argument("--epochs", default=15, type=int, help="Training epochs.")
    args = parser.parse_args()

    metrics = train_model(data_path=args.data, artifact_path=args.output, epochs=args.epochs)
    print("IELTS Task 2 TensorFlow multitask model trained.")
    print(f"Rows: {metrics['rows']} | Train: {metrics['train_rows']} | Test: {metrics['test_rows']}")
    print(f"Overall MAE: {metrics['mae']:.3f}")
    for criterion, score in metrics["dimension_mae"].items():
        print(f"{criterion} MAE: {score:.3f}")
    print(f"Saved to: {metrics['artifact_path']}")


if __name__ == "__main__":
    main()
