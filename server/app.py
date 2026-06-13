import sys
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from model.tf_multitask_predictor import predict_band, word_count


MIN_TASK2_WORDS_FOR_PREDICTION = 50

app = Flask(__name__)
CORS(app)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "message": "IELTS Task 2 Predictor Backend is running.",
            "target": "ielts_task2",
        }
    )


@app.route("/api/analyze", methods=["POST"])
def analyze_essay():
    data = request.get_json(silent=True) or {}

    question = str(data.get("question") or data.get("prompt") or "").strip()
    essay = str(data.get("essay") or "").strip()

    if not question:
        return jsonify({"error": "Question is required."}), 400
    if not essay:
        return jsonify({"error": "Essay is required."}), 400
    if word_count(essay) < MIN_TASK2_WORDS_FOR_PREDICTION:
        return jsonify({"error": "Essay is too short for IELTS Task 2 prediction."}), 400

    try:
        return jsonify(predict_band(question, essay)), 200
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except ModuleNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"Prediction failed: {exc}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
