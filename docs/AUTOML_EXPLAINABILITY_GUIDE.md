# AutoML & Model Explainability Guide

## Overview

This guide covers the AutoML capabilities, extended ML algorithms support, and model explainability features in the TRITIQ BOS.

## Table of Contents

1. [AutoML Features](#automl-features)
2. [ML Algorithms & Frameworks](#ml-algorithms--frameworks)
3. [Model Explainability](#model-explainability)
4. [API Reference](#api-reference)
5. [Best Practices](#best-practices)

---

## AutoML Features

AutoML (Automated Machine Learning) automatically selects the best model and hyperparameters for your data.

### Supported Tasks

- **Classification**: Binary and multi-class classification
- **Regression**: Continuous value prediction
- **Time Series**: Forecasting future values
- **Clustering**: Unsupervised grouping

### Supported Frameworks

- **Optuna**: Hyperparameter optimization framework (Default)
- **Auto-sklearn**: Automated ML with scikit-learn
- **TPOT**: Tree-based Pipeline Optimization Tool
- **H2O**: Scalable ML platform
- **AutoKeras**: AutoML for deep learning

### Creating an AutoML Run

```python
# API Endpoint: POST /api/v1/automl/runs

{
  "run_name": "Sales Forecast Model",
  "task_type": "regression",
  "target_column": "sales_amount",
  "feature_columns": ["product_id", "region", "season", "marketing_spend"],
  "metric": "rmse",
  "framework": "optuna",
  "time_budget": 3600,
  "max_trials": 100,
  "dataset_config": {
    "train_size": 0.8,
    "validation_size": 0.1,
    "test_size": 0.1
  }
}
```

### Monitoring AutoML Runs

- **Dashboard**: View all AutoML runs, their status, and progress
- **Leaderboard**: Top N models ranked by performance
- **Real-time Progress**: Current trial, best score, and progress percentage

### AutoML Run Lifecycle

1. **Pending**: Run is created but not started
2. **Running**: Actively training and evaluating models
3. **Completed**: All trials finished, best model selected
4. **Failed**: Run encountered an error
5. **Cancelled**: User cancelled the run

---

## ML Algorithms & Frameworks

### Supported Frameworks

#### 1. Scikit-learn
Traditional ML algorithms with excellent performance on tabular data.

**Algorithms:**
- RandomForest
- GradientBoosting
- LogisticRegression
- SVM (Support Vector Machines)
- KNN (K-Nearest Neighbors)
- DecisionTree

#### 2. CatBoost
Gradient boosting library with categorical feature support.

**Algorithms:**
- CatBoostClassifier
- CatBoostRegressor

**Key Features:**
- Handles categorical features automatically
- Built-in support for missing values
- GPU acceleration support

#### 3. LightGBM
Fast gradient boosting framework with high efficiency.

**Algorithms:**
- LGBMClassifier
- LGBMRegressor
- LGBMRanker

**Key Features:**
- Faster training speed
- Lower memory usage
- Better accuracy

#### 4. TensorFlow
Deep learning framework for neural networks.

**Model Types:**
- Sequential
- Functional API
- Custom Models

**Use Cases:**
- Image classification
- NLP tasks
- Complex pattern recognition

#### 5. PyTorch
Flexible deep learning framework with dynamic computation graphs.

**Model Types:**
- Sequential
- Custom Modules
- Transformer models

**Use Cases:**
- Research and experimentation
- Custom architectures
- Transfer learning

#### 6. XGBoost
Optimized gradient boosting library.

**Algorithms:**
- XGBClassifier
- XGBRegressor
- XGBRanker

### Creating Algorithm Configurations

```python
# API Endpoint: POST /api/v1/ml_algorithms/configs

{
  "config_name": "Production CatBoost Classifier",
  "framework": "catboost",
  "algorithm_name": "CatBoostClassifier",
  "category": "classification",
  "hyperparameters": {
    "iterations": 1000,
    "learning_rate": 0.1,
    "depth": 6,
    "l2_leaf_reg": 3
  },
  "preprocessing_config": {
    "handle_missing": "mean",
    "scale_features": true
  },
  "gpu_enabled": true
}
```

### Training Models

```python
# API Endpoint: POST /api/v1/ml_algorithms/training

{
  "training_name": "Customer Churn Model v2",
  "framework": "lightgbm",
  "algorithm_name": "LGBMClassifier",
  "dataset_config": {
    "data_path": "/datasets/customer_churn.csv",
    "target_column": "churned"
  },
  "training_params": {
    "early_stopping_rounds": 50,
    "eval_metric": "auc"
  },
  "hyperparameters": {
    "num_leaves": 31,
    "max_depth": -1,
    "learning_rate": 0.05,
    "n_estimators": 1000
  },
  "total_epochs": 1000,
  "gpu_used": true
}
```

---

## Model Explainability

Model explainability helps understand and interpret ML model predictions.

### Explainability Methods

#### 1. SHAP (SHapley Additive exPlanations)
Unified approach to explaining model predictions based on game theory.

**Features:**
- Model-agnostic
- Consistent and locally accurate
- Global and local explanations

**Use Cases:**
- Understanding feature importance
- Explaining individual predictions
- Model debugging

#### 2. LIME (Local Interpretable Model-agnostic Explanations)
Explains individual predictions by approximating the model locally.

**Features:**
- Works with any model
- Intuitive explanations
- Fast computation

**Use Cases:**
- Quick prediction explanations
- Understanding local behavior
- Model validation

#### 3. Feature Importance
Direct feature importance scores from tree-based models.

**Features:**
- Native to tree models
- Fast to compute
- Global view

### Creating Model Explainability

```python
# API Endpoint: POST /api/v1/explainability/models

{
  "model_id": 1,
  "model_type": "predictive_model",
  "model_name": "Sales Forecast Model",
  "method": "shap",
  "scope": "global",
  "config": {
    "background_samples": 100,
    "check_additivity": true
  }
}
```

### Explaining Predictions

```python
# API Endpoint: POST /api/v1/explainability/predictions

{
  "model_explainability_id": 1,
  "input_features": {
    "age": 35,
    "income": 75000,
    "credit_score": 720,
    "employment_length": 5,
    "debt_ratio": 0.3
  },
  "predicted_value": 0.85,
  "method": "shap",
  "confidence_score": 0.92
}
```

### Generating Reports

```python
# API Endpoint: POST /api/v1/explainability/reports

{
  "report_name": "Q4 2024 Model Analysis",
  "report_type": "global_summary",
  "model_ids": [1, 2, 3],
  "summary": {
    "total_models": 3,
    "average_score": 0.87,
    "common_features": ["age", "income", "credit_score"]
  },
  "key_insights": [
    "Credit score is the most important feature across all models",
    "Age has non-linear relationship with predictions",
    "Income threshold at $50,000 shows significant impact"
  ],
  "recommendations": [
    "Consider feature engineering for age variable",
    "Investigate income threshold behavior",
    "Monitor credit score data quality"
  ]
}
```

---

## API Reference

### AutoML Endpoints

- `GET /api/v1/automl/dashboard` - Get AutoML dashboard
- `POST /api/v1/automl/runs` - Create AutoML run
- `GET /api/v1/automl/runs` - List AutoML runs
- `GET /api/v1/automl/runs/{run_id}` - Get specific run
- `GET /api/v1/automl/runs/{run_id}/leaderboard` - Get top models
- `POST /api/v1/automl/runs/{run_id}/cancel` - Cancel running run

### ML Algorithms Endpoints

- `POST /api/v1/ml_algorithms/configs` - Create algorithm config
- `GET /api/v1/ml_algorithms/configs` - List algorithm configs
- `GET /api/v1/ml_algorithms/configs/{config_id}` - Get specific config
- `DELETE /api/v1/ml_algorithms/configs/{config_id}` - Delete config
- `GET /api/v1/ml_algorithms/training/dashboard` - Get training dashboard
- `POST /api/v1/ml_algorithms/training` - Create training session
- `GET /api/v1/ml_algorithms/training` - List training sessions
- `GET /api/v1/ml_algorithms/training/{training_id}` - Get specific training
- `GET /api/v1/ml_algorithms/frameworks/{framework}/algorithms` - Get framework algorithms

### Explainability Endpoints

- `GET /api/v1/explainability/dashboard` - Get explainability dashboard
- `POST /api/v1/explainability/models` - Create model explainability
- `GET /api/v1/explainability/models/{model_id}/{model_type}` - Get model explainability
- `POST /api/v1/explainability/predictions` - Create prediction explanation
- `GET /api/v1/explainability/predictions/{explainability_id}` - Get prediction explanations
- `POST /api/v1/explainability/reports` - Create explainability report
- `GET /api/v1/explainability/reports` - List reports
- `GET /api/v1/explainability/reports/{report_id}` - Get specific report

---

## Best Practices

### AutoML

1. **Data Preparation**
   - Clean and preprocess data before AutoML
   - Handle missing values appropriately
   - Remove highly correlated features

2. **Time Budget**
   - Start with shorter runs for testing (10-30 minutes)
   - Production runs: 1-6 hours depending on data size
   - Consider incremental runs for large datasets

3. **Metric Selection**
   - Classification: accuracy, f1, auc-roc
   - Regression: rmse, mae, r2
   - Match metric to business objective

### ML Algorithms

1. **Framework Selection**
   - Tabular data: CatBoost, LightGBM, XGBoost
   - Images/NLP: TensorFlow, PyTorch
   - General purpose: Scikit-learn

2. **Hyperparameter Tuning**
   - Use AutoML for initial tuning
   - Fine-tune manually for production
   - Monitor overfitting

3. **GPU Acceleration**
   - Enable for deep learning models
   - CatBoost and LightGBM support GPU
   - Significant speedup for large datasets

### Model Explainability

1. **Method Selection**
   - SHAP: Most accurate, slower computation
   - LIME: Faster, good for quick explanations
   - Feature Importance: Fastest, tree models only

2. **Scope Selection**
   - Global: Overall model behavior
   - Local: Individual prediction explanations
   - Cohort: Group-level analysis

3. **Interpretation**
   - Combine multiple methods for robustness
   - Validate explanations with domain experts
   - Document key findings

4. **Performance**
   - Cache explainability results
   - Use sampling for large datasets
   - Compute explanations asynchronously

---

## Troubleshooting

### Common Issues

1. **AutoML Run Fails**
   - Check data quality and format
   - Verify sufficient time budget
   - Review error messages in run details

2. **Poor Model Performance**
   - Check data preprocessing
   - Try different frameworks
   - Increase time budget or trials

3. **Explainability Computation Slow**
   - Reduce background samples
   - Use local scope instead of global
   - Enable caching

### Support

For additional support:
- Check the main User Guide
- Review API documentation
- Contact technical support team
