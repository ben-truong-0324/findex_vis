from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from config import *
# from src.models import *
from utils import *
from tests import *

# class TrainModel():
    
# def split_train_test():

# AVAILABLE_MODELS = []
# def train_model():

# def 

def train_and_evaluate_decision_tree(X, y, test_size=0.2, use_cv=False, max_epochs=50, early_stopping=False):
    """Train and evaluate Decision Tree and Random Forest classifiers."""
    
    # Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=GT_ID)
    
    # Initialize Models
    dt = DecisionTreeClassifier(random_state=GT_ID)
    rf = RandomForestClassifier(n_estimators=N_ESTIMATOR, random_state=GT_ID)

    # Train
    dt.fit(X_train, y_train)
    rf.fit(X_train, y_train)

    # Evaluate
    dt_acc = accuracy_score(y_test, dt.predict(X_test))
    rf_acc = accuracy_score(y_test, rf.predict(X_test))

    return {
        "Decision Tree Accuracy": dt_acc,
        "Random Forest Accuracy": rf_acc,
        "Used Cross Validation": use_cv,
        "Early Stopping Applied": early_stopping,
        "Max Epochs": max_epochs
    }
