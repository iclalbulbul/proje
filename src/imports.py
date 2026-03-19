import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
import lightgbm as lgb
import joblib
from sklearn.metrics import f1_score, roc_auc_score, confusion_matrix, precision_recall_curve
import shap
import matplotlib.pyplot as plt
import seaborn as sns

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src/ klasörü
PROJECT_DIR = os.path.dirname(BASE_DIR)  
results_path = os.path.join(PROJECT_DIR, "results")
os.makedirs(results_path, exist_ok=True)