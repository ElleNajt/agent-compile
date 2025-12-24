"""Example: Machine learning text classifier system.

This demonstrates how modules can describe entire systems, not just low-level functions.
Each module is a complete subsystem with its own behavior and tests.
"""

from src.core import Module

# High-level system: Text classifier
text_classifier = Module(
    name="text_classifier",
    purpose="""A complete text classification system using TF-IDF and logistic regression.

The system should provide a simple interface for training and prediction:
- Training: Takes list of (text, label) pairs, trains a model
- Prediction: Takes a trained model and text, returns predicted label and confidence
- Model persistence: Can save/load trained models to disk

Implementation requirements:
- Use scikit-learn's TfidfVectorizer for feature extraction
- Use scikit-learn's LogisticRegression for classification
- Support multi-class classification (not just binary)
- Normalize confidence scores to probabilities (use predict_proba)
""",
    tests=[
        "Train on sentiment data: classifier.train([('great product', 'positive'), ('terrible service', 'negative'), ('love it', 'positive')]) should return a trained model object",
        "Predict with confidence: classifier.predict(model, 'awesome experience') should return ('positive', confidence >= 0.5)",
        "Multi-class support: Can train and predict on 3+ classes (positive/negative/neutral)",
        "Model persistence: classifier.save_model(model, 'model.pkl') then classifier.load_model('model.pkl') should reconstruct the same model",
        "Empty training data: classifier.train([]) should raise ValueError",
        "Prediction before training: Attempting to predict with None/uninitialized model should raise ValueError",
        "Confidence scores: All predictions should return confidence in range [0, 1]",
    ],
)

# Data preprocessing system
text_preprocessor = Module(
    name="text_preprocessor",
    purpose="""Text preprocessing pipeline for ML tasks.

Provides utilities to clean and normalize text before classification:
- Lowercase conversion
- Punctuation removal (keep only alphanumeric and spaces)
- Extra whitespace normalization (collapse multiple spaces to single space)
- Optional stopword removal (common words like 'the', 'is', 'and')

Should be composable - each step can be toggled on/off.
""",
    tests=[
        "Basic cleaning: preprocess('Hello World!') with defaults should return 'hello world'",
        "Whitespace normalization: preprocess('too   many    spaces') should return 'too many spaces'",
        "Punctuation removal: preprocess('wow!!! amazing...') should return 'wow amazing'",
        "Stopword removal: preprocess('the cat is here', remove_stopwords=True) should return 'cat' (assuming 'the', 'is', 'here' are stopwords)",
        "Preserve numbers: preprocess('order 123') should keep the number: 'order 123'",
        "Empty string: preprocess('') should return ''",
        "Only punctuation: preprocess('!!!') should return ''",
    ],
)

# Model evaluation system
model_evaluator = Module(
    name="model_evaluator",
    purpose="""Evaluation metrics for classification models.

Computes standard ML metrics given predictions and ground truth labels:
- Accuracy: (correct predictions / total predictions)
- Precision: Per-class and macro-averaged
- Recall: Per-class and macro-averaged  
- F1-score: Per-class and macro-averaged
- Confusion matrix: 2D array showing prediction vs actual counts

Returns a dictionary with all metrics for easy interpretation.
""",
    tests=[
        "Perfect predictions: evaluate(y_true=['a', 'b', 'c'], y_pred=['a', 'b', 'c']) should return accuracy=1.0, all precision/recall/f1=1.0",
        "All wrong: evaluate(y_true=['a', 'b'], y_pred=['b', 'a']) should return accuracy=0.0",
        "Binary classification: evaluate with 2 classes should compute all metrics correctly",
        "Multi-class: evaluate with 3+ classes should compute macro-averaged metrics",
        "Confusion matrix shape: For n classes, confusion matrix should be (n, n) array",
        "Mismatched lengths: evaluate(y_true=['a'], y_pred=['a', 'b']) should raise ValueError",
        "Empty inputs: evaluate(y_true=[], y_pred=[]) should raise ValueError",
    ],
)

# Complete ML pipeline (depends on the above)
ml_pipeline = Module(
    name="ml_pipeline",
    purpose="""End-to-end ML pipeline that combines preprocessing, training, and evaluation.

Provides a high-level interface to:
1. Preprocess training and test data
2. Train a classifier on preprocessed data
3. Evaluate the model on test set
4. Return trained model + evaluation metrics

This is the main entry point users would interact with.
""",
    dependencies=[text_preprocessor, text_classifier, model_evaluator],
    tests=[
        "Full pipeline: pipeline.run(train_data=[('good', 'pos'), ('bad', 'neg')], test_data=[('great', 'pos')]) should return (model, metrics_dict)",
        "Metrics included: Output metrics should include accuracy, precision, recall, f1, confusion_matrix",
        "Preprocessing applied: Text should be cleaned before training (verified by model working on messy test input)",
        "Model is trained: Returned model should be usable for predictions via text_classifier.predict()",
        "Empty train data: pipeline.run(train_data=[], test_data=X) should raise ValueError",
        "Empty test data: pipeline.run(train_data=X, test_data=[]) should raise ValueError",
    ],
)
