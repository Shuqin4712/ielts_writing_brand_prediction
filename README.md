# IELTS Writing Task 2 Predictor - User Manual

## Overview

The IELTS Writing Task 2 Predictor is a machine learning application that automatically scores IELTS Writing Task 2 essays and provides detailed feedback. The system uses a TensorFlow-based deep learning model combined with linguistic feature engineering to predict scores across four official IELTS assessment criteria.

## What This Program Does

### Main Features

- **Automatic Essay Scoring**: Predicts scores for all 4 IELTS writing criteria:
  - Task Response (addressing the question)
  - Coherence and Cohesion (organization and flow)
  - Lexical Resource (vocabulary range and accuracy)
  - Grammatical Range and Accuracy (grammar control)

- **Overall Band Score**: Calculates the final IELTS band (0-9, including 0.5 increments)

- **Personalized Feedback**: Generates rule-based suggestions tailored to the predicted score level

- **Score History**: Maintains a record of all analyzed essays for tracking progress

- **Web Interface**: User-friendly React-based interface for easy interaction

- **REST API**: Backend Flask API for programmatic access

## How It Works

### System Architecture

The prediction system uses a **Wide & Deep Multitask Learning Model**:

1. **Text Processing**: The essay and question are cleaned and vectorized using TensorFlow's TextVectorization layer
2. **Feature Extraction**: Linguistic features are computed from the essay (word count, vocabulary diversity, sentence complexity, discourse markers)
3. **Deep Learning Branch**: A neural network processes the text embedding
4. **Wide Learning Branch**: Hand-crafted linguistic features are input directly
5. **Feature Fusion**: Both branches are merged and passed through dense layers
6. **Score Output**: Four regression heads output scores for each criterion

### Model Performance

The model achieves:

- Overall Mean Absolute Error (MAE): ~1.12 band points
- Individual criterion MAE: 1.11–1.16 band points

Note: IELTS scoring is inherently subjective and uses a discrete 0–9 scale with 0.5 increments. An error margin of ±1.0 band point is considered acceptable for automated essay scoring systems.

## User Requirements

### To Run This Application

#### System Requirements

- **Python 3.8 or higher**
- **Node.js 14.0 or higher** (for the web frontend)
- **Disk space**: ~500MB for TensorFlow and dependencies
- **RAM**: Minimum 4GB recommended

#### Software Dependencies

The application will automatically install required packages via pip and npm. Key dependencies include:

- TensorFlow 2.x
- Pandas (data processing)
- NumPy (numerical computing)
- Flask (backend API)
- React (frontend interface)

#### Input Data Requirements

To use this program, you need:

1. **An IELTS Writing Task 2 question** - A prompt that asks the student to write an opinion or analytical essay

2. **A candidate essay** - The student's written response (minimum ~150 words recommended for reliable scoring)

## Installation and Setup

### Backend Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Prepare data (if training or retraining the model):

```bash
python scripts/prepare_task2_multitask_data.py
```

3. Train the model (optional):

```bash
python scripts/train_tf_multitask_model.py
```

4. Start the Flask API server:

```bash
python server/app.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the client directory:

```bash
cd client
```

2. Install Node dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm start
```

The web interface will open at `http://localhost:3000`

### Production Deployment

To build for production:

```bash
cd client
npm run build
```

The optimized build files will be in the `client/build` directory.

## How to Use the Application

### Via Web Interface

1. Open `http://localhost:3000` in your browser
2. Enter the IELTS Writing Task 2 question in the "Question" field
3. Paste or write the candidate essay in the "Essay" field
4. Click "Score Essay" to get predictions
5. View the results in the report panel:
   - Overall band score
   - Individual criterion scores (0-9)
   - Personalized feedback suggestions
6. Use the history panel to review previous analyses

### Via REST API

Send a POST request to `http://localhost:5000/api/analyze`:

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "question": "To what extent do you agree that modern technology has improved our lives?",
    "essay": "Modern technology has dramatically changed society in both positive and negative ways..."
  }'
```

Response includes:

- `overall_band`: Final IELTS band score (0-9)
- `criteria_scores`: Individual scores for the 4 criteria
- `raw_scores`: Numerical predictions (0-9)
- `word_count`: Word count of the essay
- `suggestions`: Feedback for each criterion

## Dataset Information

The model is trained on the **IELTS Writing Dataset** from Kaggle:

**Source**: https://www.kaggle.com/datasets/xntrng15/ielts-writing-dataset

This dataset contains approximately 1,300 labeled IELTS Writing Task 2 essays with:

- Complete essay texts
- Four analytic scoring dimensions
- Overall band scores based on official IELTS rules

## Code References

This project references and builds upon concepts from **WriteRight**:

**Source**: https://github.com/PritK99/WriteRight

WriteRight provides a framework for automated essay evaluation and feedback generation. Our implementation extends this with:

- Multi-criterion regression instead of classification
- Linguistic feature engineering specific to IELTS criteria
- Fine-grained scoring (0-9 with 0.5 increments) instead of discrete grades

## Feedback System

The application provides score-specific feedback based on:

- **Below 5.5**: Identifies critical areas needing improvement
- **5.5-6.4**: Acknowledges progress and specific action items
- **6.5-7.4**: Confirms strengths and advanced refinement areas
- **7.5+**: Validates excellence and maintained performance

## Limitations and Disclaimers

- This tool provides **estimates** and should not be treated as official IELTS band scores
- Results are most reliable for essays in the 200-400 word range
- The model may show variance on essays with non-standard language, highly technical vocabulary, or unusual structures
- Professional human evaluation is recommended for high-stakes assessment
- This tool is designed to provide learning feedback, not formal certification

## Troubleshooting

### Port Already in Use

If port 5000 or 3000 is already in use, modify the port in:

- Backend: `server/app.py`
- Frontend: Set `PORT` environment variable before running npm start

### TensorFlow Installation Issues

On Windows, you may need to install Visual C++ Build Tools. See:
https://www.tensorflow.org/install/pip

### Model File Missing

Ensure `model/artifacts/ielts_task2_multitask_model.keras` exists. If missing, retrain:

```bash
python scripts/train_tf_multitask_model.py
```

## Support and Feedback

For issues, questions, or suggestions, please check:

- The application logs in the terminal
- Flask debug output for API errors
- Browser console for frontend issues

---

**Last Updated**: June 2026  
**Model Version**: 2.0 (Wide & Deep Multitask Learning)  
**License**: See LICENSE file for details
