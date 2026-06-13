# IELTS Writing Task 2 Predictor

This project is a runnable IELTS Writing Task 2 score prediction app. It includes:

- a React frontend for entering a Task 2 question and candidate essay
- a Flask backend API at `POST /api/analyze`
- a TensorFlow multitask model pipeline that predicts four IELTS writing criteria
- rule-based feedback messages for each criterion

The project scope is IELTS Writing Task 2 only.

## Project Structure

```text
ieltspredict/
  client/                               React web app
  data/
    ielts_task2_multitask.csv           Unified Task 2 dataset
  model/
    feedback_rules.py                   Criterion feedback messages
    tf_multitask_predictor.py           Training and inference logic
    artifacts/
      ielts_task2_multitask_model.keras Trained TensorFlow model
  scripts/
    prepare_task2_multitask_data.py     Dataset cleanup entry point
    train_tf_multitask_model.py         Model training entry point
  server/
    app.py                              Flask API
```

## API Contract

Request:

```json
{
  "question": "Some people believe universities should focus on employment skills. To what extent do you agree or disagree?",
  "essay": "Candidate essay text..."
}
```

Successful response:

```json
{
  "overall_band": 6.5,
  "criteria_scores": {
    "task_response": 6.0,
    "coherence_cohesion": 6.5,
    "lexical_resource": 6.5,
    "grammar_range_accuracy": 6.0
  },
  "raw_scores": {
    "task_response": 6.12,
    "coherence_cohesion": 6.43,
    "lexical_resource": 6.58,
    "grammar_range_accuracy": 6.21
  },
  "word_count": 278,
  "suggestions": [
    {
      "criterion": "task_response",
      "title": "Task Response",
      "message": "Develop your main ideas with more specific examples."
    }
  ],
  "model_info": {
    "model_type": "tensorflow_multitask",
    "target": "ielts_task2",
    "criteria_count": 4
  }
}
```

## Setup

Create and activate a Python virtual environment, then install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Install frontend dependencies:

```powershell
cd client
npm install
```

## Prepare Data

If `data/ielts_task2_multitask.csv` is missing or needs to be regenerated:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_task2_multitask_data.py
```

The unified dataset must contain:

```text
question
essay
task_response
coherence_cohesion
lexical_resource
grammar_range_accuracy
overall_band
```

## Train The Model

Run this from the project root:

```powershell
.\.venv\Scripts\python.exe scripts\train_tf_multitask_model.py
```

The trained model is saved to:

```text
model/artifacts/ielts_task2_multitask_model.keras
```

## Run The Application

Start the backend:

```powershell
.\.venv\Scripts\python.exe .\server\app.py
```

Start the frontend in a second terminal:

```powershell
cd client
npm start
```

Open:

```text
http://localhost:3000
```
