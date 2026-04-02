# AI-Driven Health Risk and Disease Prediction System
## BSc (Hons) Computing - Level 6 Production Project
### Student: Aarson Subba | ID: 77466898

---

## COMPLETE WORKFLOW GUIDE

Follow this step-by-step guide in order. Each step builds on the previous one.

---

### STEP 1: SETUP (You've already done this!)
```
✅ Created virtual environment (venv)
✅ Installed dependencies (requirements.txt)
✅ Created folder structure
✅ Created empty Python files
```

---

### STEP 2: DOWNLOAD DATASETS
Put these CSV files in `data/raw/`:
- heart.csv (from Kaggle Heart Disease Dataset)
- diabetes.csv (from Kaggle Pima Indians Diabetes)
- dataset.csv (from Kaggle Disease Symptom Prediction)

---

### STEP 3: JUPYTER NOTEBOOKS (Do these in order!)

Open terminal, activate venv, run `jupyter notebook`, navigate to `notebooks/`

#### Notebook 1: 01_data_exploration
- Load and explore all datasets
- Check shapes, types, missing values
- Visualise distributions and correlations
- Creates: EDA charts and understanding of data

#### Notebook 2: 02_preprocessing
- Clean data (remove duplicates, handle missing values)
- Feature engineering (age groups, risk scores, BMI categories)
- Encode categorical variables
- Scale features with StandardScaler
- Split into train/validation/test (70/15/15)
- Apply SMOTE for class imbalance
- Creates: Files in `data/processed/`

#### Notebook 3: 03_model_training
- Train 7 models (Logistic Regression, Decision Tree, Random Forest, SVM, KNN, XGBoost, Gradient Boosting)
- Compare all models on validation set
- Hyperparameter tuning with GridSearchCV
- Save best models
- Creates: Model files in `models/`

#### Notebook 4: 04_evaluation
- Load best models and test data
- Final evaluation on test set
- Confusion matrices, ROC curves, precision-recall curves
- Feature importance analysis
- Creates: Evaluation charts for your report

#### Notebook 5: 05_shap_explainability
- SHAP analysis for model interpretability
- Feature contribution plots
- Individual prediction explanations
- Create explanation function for Flask app
- Creates: Explainability charts for your report

---

### STEP 4: ML MODULE FILES
After notebooks are complete, the `ml/` folder contains:
- `preprocess.py` - Data cleaning and preprocessing functions
- `train_model.py` - Model training functions
- `predict.py` - Prediction and risk scoring functions
- `evaluate.py` - Evaluation metric functions

---

### STEP 5: FLASK APPLICATION
The `app/` folder contains:
- `__init__.py` - App factory (creates Flask app)
- `routes/auth.py` - Login, register, logout
- `routes/predict.py` - Prediction form and results
- `routes/dashboard.py` - Analytics dashboard
- `models/database.py` - SQLAlchemy database models

To run: `python run.py` → Open http://127.0.0.1:5000

---

### STEP 6: HTML TEMPLATES (Build after Flask routes)
Create these in `app/templates/`:
- `base.html` - Base template with navbar
- `home.html` - Landing page
- `login.html` - Login form
- `register.html` - Registration form
- `predict.html` - Prediction input form
- `results.html` - Prediction results display
- `dashboard.html` - Analytics dashboard with charts
- `history.html` - Prediction history table

---

### STEP 7: TESTING
Create test files in `tests/`:
- `test_models.py` - Test ML model predictions
- `test_routes.py` - Test Flask API endpoints
- `test_database.py` - Test database operations

Run tests: `pytest tests/ -v`

---

### STEP 8: DOCUMENTATION & SUBMISSION
- Write project report (8 chapters)
- Create user guide
- Record demo video
- Final submission

---

## FOLDER STRUCTURE
```
health-risk-prediction-system/
├── app/                         # Flask application
│   ├── __init__.py              # App factory
│   ├── routes/
│   │   ├── auth.py              # Authentication
│   │   ├── predict.py           # Prediction endpoints
│   │   └── dashboard.py         # Dashboard views
│   ├── models/
│   │   └── database.py          # Database models
│   ├── templates/               # HTML templates (Step 6)
│   ├── static/                  # CSS, JS, images
│   └── utils/                   # Helper functions
├── ml/                          # Machine learning module
│   ├── preprocess.py            # Data preprocessing
│   ├── train_model.py           # Model training
│   ├── predict.py               # Prediction logic
│   └── evaluate.py              # Model evaluation
├── data/
│   ├── raw/                     # Original CSV files
│   └── processed/               # Cleaned data + splits
├── models/                      # Saved .pkl model files
├── notebooks/                   # Jupyter notebooks (Step 3)
│   ├── 01_data_exploration.py
│   ├── 02_preprocessing.py
│   ├── 03_model_training.py
│   ├── 04_evaluation.py
│   └── 05_shap_explainability.py
├── tests/                       # Test files (Step 7)
├── config.py                    # App configuration
├── run.py                       # Entry point
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## TECH STACK
- Python 3.10+ | Flask 3.x | Scikit-learn | XGBoost
- SQLite | SQLAlchemy | Flask-Login
- Pandas | NumPy | Matplotlib | Seaborn | SHAP
- HTML5 | CSS3 | Bootstrap 5 | Chart.js
