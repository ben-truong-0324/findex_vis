
import re
import time
import os
import datetime
import unittest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate 
import pickle
import random
from copy import deepcopy
import hypotheses
# from src.models import *
# from src.models_reg import *
from config import *
import plots as plots
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.inspection import permutation_importance

import joblib
# import optuna

import math
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier


from scipy.stats import ttest_1samp
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix,precision_score, \
                        recall_score,classification_report, \
                        accuracy_score, f1_score, log_loss, \
                       confusion_matrix, ConfusionMatrixDisplay,\
                          roc_auc_score, matthews_corrcoef, average_precision_score
from sklearn.cluster import KMeans, AgglomerativeClustering,DBSCAN,Birch,MeanShift, SpectralClustering

from sklearn.mixture import GaussianMixture
from sklearn.model_selection import ParameterSampler

#import dimension reduction modules
from sklearn.decomposition import PCA, FastICA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.random_projection import GaussianRandomProjection, SparseRandomProjection

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold


from torch import nn, optim
import torch
from torch.utils.data import DataLoader, TensorDataset

def set_random_seed(seed): #use for torch nn training in MC simulation
    torch.manual_seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)  # Set seed for all GPUs
        torch.backends.cudnn.deterministic = True  # Ensures deterministic behavior
        torch.backends.cudnn.benchmark = False  

def set_output_dir(outpath):
    os.makedirs(outpath, exist_ok=True)
    return outpath

def purity_score(y_true, y_pred):
    # Matrix of contingency
    contingency_matrix = np.zeros((len(set(y_true)), len(set(y_pred))))
    for i, label in enumerate(y_true):
        contingency_matrix[label, y_pred[i]] += 1
    # Take the max label count for each cluster, sum them, and divide by total samples
    return np.sum(np.amax(contingency_matrix, axis=0)) / np.sum(contingency_matrix)

def get_metrics_of_hyperparm_set(y_preds):
    accuracies = []
    mcc_scores = []
    f1_scores = []
    roc_auc_scores = []
    pr_auc_scores = []

    # Iterate over all y_preds, assuming y_preds is a list of tuples (y_test, predicted)
    for y_test, predicted in y_preds:
        # Compute matches and row accuracies
        matches = (y_test == predicted)
        row_accuracies = np.mean(matches, axis=1)  # Mean across each row (for multi-label)
        
        # Compute overall accuracy for the current fold (mean of row accuracies)
        accuracies.append(np.mean(row_accuracies))

        # Compute MCC (Matthews Correlation Coefficient) for the current fold
        mcc = matthews_corrcoef(y_test.flatten(), predicted.flatten())  # Flatten if multi-label
        mcc_scores.append(mcc)

        # Compute F1 Score (for binary or multi-label)
        f1 = f1_score(y_test, predicted, average='macro')  # 'macro' averages F1 score across labels
        f1_scores.append(f1)

        # Compute AUC-ROC (Area Under the Receiver Operating Characteristic Curve)
        auc_roc = roc_auc_score(y_test, predicted, average='macro', multi_class='ovr')  # 'ovr' for one-vs-rest
        roc_auc_scores.append(auc_roc)

        # Compute AUC-PR (Area Under the Precision-Recall Curve)
        auc_pr = average_precision_score(y_test, predicted, average='macro')  # 'macro' averages PR score across labels
        pr_auc_scores.append(auc_pr)

    # Calculate the average of all metrics across folds
    avg_accuracy = np.mean(accuracies)
    std_accuracy = np.std(accuracies)  # Standard deviation for accuracy

    avg_mcc = np.mean(mcc_scores)
    avg_f1 = np.mean(f1_scores)
    avg_roc_auc = np.mean(roc_auc_scores)
    avg_pr_auc = np.mean(pr_auc_scores)
    return avg_accuracy, std_accuracy, avg_mcc, avg_f1, avg_roc_auc, avg_pr_auc



# Evaluation functions
def calculate_fin_metrics(y_pred, y_actual):
    num_samples, num_labels = y_pred.shape
    
    # Initialize lists to store individual metrics for each label
    label_accuracy = []
    auc_roc = []
    f1 = []
    mcc = []
    auprc = []
    
    for i in range(num_labels):
        # Calculate accuracy for each label
        acc = (y_pred[:, i] == y_actual[:, i]).mean()  # Mean accuracy for each label
        label_accuracy.append(acc)
        
        # Handle the AUC-ROC calculation only if both classes are present
        try:
            auc = roc_auc_score(y_actual[:, i], y_pred[:, i])
            auc_roc.append(auc)
        except ValueError:
            # Skip if only one class is present in y_true
            auc_roc.append(np.nan)
        
        # Calculate F1 score for each label
        f1_score_label = f1_score(y_actual[:, i], y_pred[:, i])
        f1.append(f1_score_label)
        
        # Calculate Matthews Correlation Coefficient (MCC) for each label
        mcc_score = matthews_corrcoef(y_actual[:, i], y_pred[:, i])
        mcc.append(mcc_score)
        
        # Calculate Average Precision (AU-PRC) for each label
        auprc_score = average_precision_score(y_actual[:, i], y_pred[:, i])
        auprc.append(auprc_score)
    
    # Overall accuracy for all 19 labels (mean of the per-label accuracies)
    overall_accuracy = np.mean(label_accuracy)
    
    return label_accuracy, auc_roc, f1, mcc, auprc, overall_accuracy

import pandas as pd
import numpy as np

def print_and_save_metrics(results, output_file):
    """
    Save and print the mean and standard deviation for each metric (excluding 'overall_accuracy')
    for each dataset and model.

    :param results: A dictionary containing dataset metrics with model names and their respective metric values.
    :param output_file: Path to the file where metrics will be saved.
    """
    print("hello")
    with open(output_file, 'w') as f:
        for dataset, models_metrics in results.items():
            f.write(f"Dataset: {dataset}\n")
            
            # Extracting the metrics for each model
            metrics_to_process = ['label_accuracy', 'auc_roc', 'f1', 'mcc', 'auprc']
            dataset_stats = {}
            model_stats = {}

            # Compute mean and std for each metric, per model
            for model_metrics in models_metrics:
                model_name = model_metrics["model"]
                model_stats[model_name] = {}

                for metric in metrics_to_process:
                    metric_values = model_metrics[metric]
                    mean_value = np.mean(metric_values)
                    std_value = np.std(metric_values)
                    model_stats[model_name][metric] = {"mean": mean_value, "std": std_value}
            
            # Now prepare the output for dataset-level statistics
            dataset_level_stats = {}

            for metric in metrics_to_process:
                # Gather all model mean values for the metric to calculate dataset-level mean and std
                model_mean_values = [model_stats[model][metric]["mean"] for model in model_stats]
                model_std_values = [model_stats[model][metric]["std"] for model in model_stats]

                dataset_level_stats[metric] = {
                    "mean": np.mean(model_mean_values),
                    "std": np.std(model_mean_values)
                }

            # Write out dataset-level stats
            f.write("Dataset-level statistics (mean and std of each model's metrics):\n")
            dataset_df = pd.DataFrame(dataset_level_stats).T
            dataset_df.index.name = 'Metric'
            f.write(dataset_df.to_string())
            f.write("\n\n")

            # Write out model-level stats (mean and std for each model and metric)
            f.write("Model-level statistics (mean and std for each model):\n")
            for model_name, stats in model_stats.items():
                f.write(f"Model: {model_name}\n")
                model_df = pd.DataFrame(stats).T
                model_df.index.name = 'Metric'
                f.write(model_df.to_string())
                f.write("\n\n")

            # Print the statistics to the console
            print(f"Metrics for dataset {dataset}:")
            print(dataset_df)
            for model_name, stats in model_stats.items():
                print(f"Model: {model_name}")
                print(pd.DataFrame(stats).T)

# Example usage
# print_and_save_metrics(results, 'metrics_summary.txt')


def check_data_info(X, y, X_train, X_test, y_train, y_test, show = False):
    if show:
        # Check data types and shapes for each of the variables
        data_info = {
            'X': {'dtype': type(X), 'shape': X.shape if isinstance(X, (np.ndarray, pd.DataFrame)) else 'Not an array-like object'},
            'y': {'dtype': type(y), 'shape': y.shape if isinstance(y, (np.ndarray, pd.Series)) else 'Not an array-like object'},
            'X_train': {'dtype': type(X_train), 'shape': X_train.shape if isinstance(X_train, (np.ndarray, pd.DataFrame)) else 'Not an array-like object'},
            'X_test': {'dtype': type(X_test), 'shape': X_test.shape if isinstance(X_test, (np.ndarray, pd.DataFrame)) else 'Not an array-like object'},
            'y_train': {'dtype': type(y_train), 'shape': y_train.shape if isinstance(y_train, (np.ndarray, pd.Series)) else 'Not an array-like object'},
            'y_test': {'dtype': type(y_test), 'shape': y_test.shape if isinstance(y_test, (np.ndarray, pd.Series)) else 'Not an array-like object'}
        }

        # Print the data type and shape for each variable
        for var, info in data_info.items():
            print(f'{var}: Type = {info["dtype"]}, Shape = {info["shape"]}')
            
        # Function to check columns, data types, and unique values
        def check_dataframe_info(df, name):
            if isinstance(df, (pd.DataFrame, pd.Series)):
                print(f"\n{name} DataFrame/Series:")
                # Check for NaN values
                nan_count = df.isnull().sum().sum() if isinstance(df, pd.DataFrame) else df.isnull().sum()
                print(f"  Total NaN Values: {nan_count}")
                # Iterate through columns to check unique counts
                if isinstance(df, pd.DataFrame):  # For DataFrame, check columns
                    for col in df.columns:
                        if df[col].dtype in ['int64', 'float64']:  # Numeric column
                            if df[col].nunique() > 10:  # Skip unique count if there are more than 10 unique values
                                print(f"Column '{col}': {df[col].dtype}, Numerical")
                            else:
                                print(f"Column '{col}': {df[col].dtype}, Unique Values = {df[col].nunique()}")
                        else:  # Categorical column (non-numeric)
                            print(f"Column '{col}': {df[col].dtype}, Unique Values = {df[col].nunique()}")
                else:  # For Series, just show unique counts
                    print(f"Unique Values: {df.nunique()}")

        # Check DataFrame info for X, X_train, and X_test (assuming they are DataFrames)
        if isinstance(X, (pd.DataFrame, pd.Series)):
            check_dataframe_info(X, 'X')
        if isinstance(X_train, (pd.DataFrame, pd.Series)):
            check_dataframe_info(X_train, 'X_train')
        if isinstance(X_test, (pd.DataFrame, pd.Series)):
            check_dataframe_info(X_test, 'X_test')
        if isinstance(y, (pd.Series, pd.DataFrame)):
            check_dataframe_info(y, 'y')
        if isinstance(y_train, (pd.Series, pd.DataFrame)):
            check_dataframe_info(y_train, 'y_train')
        if isinstance(y_test, (pd.Series, pd.DataFrame)):
            check_dataframe_info(y_test, 'y_test')

def train_nn_early_stop_classification(X_train, y_train, X_test, y_test, device,params_dict ,criterion, model_name="default"):
    input_dim = X_train.shape[1]
    output_dim = 1  
    unique_classes = y_train.unique()  
    n_classes = len(unique_classes)

    if n_classes == 2:
        criterion = nn.BCEWithLogitsLoss()  # for binary classification
    else:
        criterion = nn.CrossEntropyLoss()
   
    max_epochs = NN_MAX_EPOCH
    patience = 5
    # Create DataLoaders for training and testing
    train_dataset = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
    test_dataset = TensorDataset(torch.FloatTensor(X_test), torch.FloatTensor(y_test))
    batch_size = params_dict.get('batch_size', 256)  # Default batch size if not specified
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    if model_name == "MPL":
        model = NNMPL(
            input_dim,
            output_dim,
            hidden_dim=params_dict['hidden_dim'],
            dropout_rate=params_dict['dropout_rate']
        ).to(device)
    elif model_name == "LSTM":
        model = NNLSTM(input_dim, output_dim, hidden_dim=params_dict['hidden_dim'], num_layers=1, dropout_rate=params_dict['dropout_rate']).to(device)
    elif model_name == "BiLSTM":
        model = NNBiLSTM(input_dim, output_dim,hidden_dim=289, lstm_hidden_dim=150,dropout_rate=params_dict['dropout_rate']).to(device)
    elif model_name == "CNN":
        model = NNCNN(input_dim, output_dim, kernel_size=2, hidden_dim=params_dict['hidden_dim'], dropout_rate=params_dict['dropout_rate']).to(device)
   
    else:
        raise ValueError(f"Unsupported model type: {model_name}")
    optimizer = optim.Adam(model.parameters(), lr=params_dict['lr'], weight_decay=params_dict['weight_decay'])


    best_loss = float("inf")
    patience_counter = 0
    epoch_losses = []
    
    start_time = time.time()
    for epoch in range(max_epochs):
        print(f"Start of epoch {epoch}")
        epoch_start_time = time.time() 
        model.train()
        train_epoch_loss = 0.0
        for batch_idx, (batch_X, batch_y) in enumerate(train_loader):
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs_train = model(batch_X).squeeze()

            train_loss = criterion(outputs_train, batch_y)
            train_loss.backward()
            optimizer.step()
            train_epoch_loss += train_loss.item() * len(batch_X)  # Accumulate loss
            
           
        # Average train loss for the epoch
        train_epoch_loss /= len(train_loader.dataset)

        # Evaluate on test set
        model.eval()
        eval_epoch_loss = 0.0
        eval_predictions = []
        eval_labels = []
        with torch.no_grad():
            for batch_idx, (batch_X, batch_y) in enumerate(test_loader):
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs_eval = model(batch_X).squeeze()
                eval_loss = criterion(outputs_eval, batch_y)
                eval_epoch_loss += eval_loss.item() * len(batch_X)
                if criterion == nn.BCEWithLogitsLoss():
                    predictions = torch.sigmoid(outputs_eval) > 0.5  # Threshold at 0.5 for binary
                    predictions = predictions.long() 
                else:
                    if outputs_eval.ndimension() == 2:  # Check if it's multi-class (batch_size, num_classes)
                        _, predictions = torch.max(outputs_eval, dim=1)  # Get the class index with max logit
                    else:
                        # If it’s not multi-class, treat it as binary (this should not happen)
                        predictions = torch.sigmoid(outputs_eval) > 0.5
                        predictions = predictions.long() 
                
                
        # Average eval loss for the epoch
        eval_epoch_loss /= len(test_loader.dataset)
        epoch_losses.append((train_epoch_loss, eval_epoch_loss))
        epoch_runtime = time.time() - epoch_start_time
        print(f"Epoch {epoch + 1}/{max_epochs} - Train Loss: {train_epoch_loss:.4f}, Eval Loss: {eval_epoch_loss:.4f}, Runtime: {epoch_runtime:.2f} seconds")
        
        # Early stopping logic
        if eval_epoch_loss < best_loss:
            best_loss = eval_epoch_loss
            patience_counter = 0
            best_model_state = model.state_dict()  # Save the best model
        else:
            patience_counter += 1

        if patience_counter >= patience:
            print(f"Early stopping triggered at epoch {epoch + 1}")
            break

        # Store both training and evaluation losses
        epoch_losses.append({
            "epoch": epoch + 1,
            "train_loss": train_loss.item(),
            "eval_loss": eval_loss.item()
        })

    # Restore the best model
    model.load_state_dict(best_model_state)
    runtime = time.time() - start_time

    model.eval()
    outputs_list = []
    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            batch_outputs = model(batch_X.to(device))
            outputs_list.append(batch_outputs.cpu())  # Move outputs back to CPU to free GPU memory
    outputs = torch.cat(outputs_list, dim=0).cpu().numpy()


    if criterion == nn.BCEWithLogitsLoss():  # Binary classification
        predictions = (torch.sigmoid(torch.tensor(outputs)) > 0.5).int()
        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions)
        recall = recall_score(y_test, predictions)
        f1 = f1_score(y_test, predictions)
    else:  
        if len(np.unique(outputs)) == 2:  # Check if it's multi-class (batch_size, num_classes)
            _, predictions = torch.max(torch.tensor(outputs), dim=1)  # Get the class index with max logit
        else:
            # If it’s not multi-class, treat it as binary (this should not happen)
            predictions = torch.sigmoid(torch.tensor(outputs)) > 0.5
            predictions = predictions.int() 
        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average='macro')
        recall = recall_score(y_test, predictions, average='macro')
        f1 = f1_score(y_test, predictions, average='macro')

    if n_classes == 2:
        roc_auc = roc_auc_score(y_test, predictions)
    else:
        roc_auc = 0
        
    return accuracy, precision, recall, f1, roc_auc, runtime, model, epoch_losses, outputs

def train_nn_early_stop_regression(X_train, y_train, X_test, y_test, device,params_dict ,criterion, model_name="default"):
    input_dim = X_train.shape[1]
    if isinstance(criterion, (nn.MSELoss, nn.L1Loss)):  # Check if the criterion is a regression loss
        output_dim = 1  # Regression tasks always have a single continuous output
    else:
        if len(y_train.shape) > 1 and y_train.shape[1] > 1:
            output_dim = y_train.shape[1]  # Number of labels
        else:
            output_dim = len(np.unique(y_train.cpu()))
    max_epochs = NN_MAX_EPOCH
    patience = 5
    # Create DataLoaders for training and testing



    train_dataset = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
    test_dataset = TensorDataset(torch.FloatTensor(X_test), torch.FloatTensor(y_test))

    batch_size = params_dict.get('batch_size', 64)  # Default batch size if not specified
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    if model_name == "MPL":
        model = MLPRegression(
            input_dim,
            output_dim,
            hidden_dim=params_dict['hidden_dim'],
            dropout_rate=params_dict['dropout_rate']
        ).to(device)
    elif model_name == "LSTM":
        model = LSTMRegression(input_dim, output_dim, hidden_dim=params_dict['hidden_dim'], num_layers=1, dropout_rate=params_dict['dropout_rate']).to(device)
    elif model_name == "SalienceNN":
        model = SalienceNNRegression(input_dim, output_dim,hidden_dim=params_dict['hidden_dim'],dropout_rate=params_dict['dropout_rate']).to(device)
    elif model_name == "CNN":
        model = CNNRegression(input_dim, output_dim, kernel_size=2, hidden_dim=params_dict['hidden_dim'], dropout_rate=params_dict['dropout_rate']).to(device)
   
    else:
        raise ValueError(f"Unsupported model type: {model_name}")
    optimizer = optim.Adam(model.parameters(), lr=params_dict['lr'], weight_decay=params_dict['weight_decay'])

    best_loss = float("inf")
    patience_counter = 0
    epoch_losses = []
    
    start_time = time.time()
    for epoch in range(max_epochs):
        print(f"Start of epoch {epoch}")
        epoch_start_time = time.time() 
        model.train()
        train_epoch_loss = 0.0
        for batch_idx, (batch_X, batch_y) in enumerate(train_loader):
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs_train = model(batch_X).squeeze()
            train_loss = criterion(outputs_train, batch_y)
            train_loss.backward()
            optimizer.step()
            train_epoch_loss += train_loss.item() * len(batch_X)  # Accumulate loss
            
           
        # Average train loss for the epoch
        train_epoch_loss /= len(train_loader.dataset)

        # Evaluate on test set
        model.eval()
        eval_epoch_loss = 0.0
        with torch.no_grad():
            for batch_idx, (batch_X, batch_y) in enumerate(test_loader):
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs_eval = model(batch_X).squeeze()
                eval_loss = criterion(outputs_eval, batch_y)
                eval_epoch_loss += eval_loss.item() * len(batch_X)
                
                
        # Average eval loss for the epoch
        eval_epoch_loss /= len(test_loader.dataset)
        epoch_losses.append((train_epoch_loss, eval_epoch_loss))
        epoch_runtime = time.time() - epoch_start_time
        print(f"Epoch {epoch + 1}/{max_epochs} - Train Loss: {train_epoch_loss:.4f}, Eval Loss: {eval_epoch_loss:.4f}, Runtime: {epoch_runtime:.2f} seconds")
        

        # Early stopping logic
        if eval_epoch_loss < best_loss:
            best_loss = eval_epoch_loss
            patience_counter = 0
            best_model_state = model.state_dict()  # Save the best model
        else:
            patience_counter += 1

        if patience_counter >= patience:
            print(f"Early stopping triggered at epoch {epoch + 1}")
            break

        # Store both training and evaluation losses
        epoch_losses.append({
            "epoch": epoch + 1,
            "train_loss": train_loss.item(),
            "eval_loss": eval_loss.item()
        })

    # Restore the best model
    model.load_state_dict(best_model_state)
    runtime = time.time() - start_time

    model.eval()
    outputs_list = []
    model.eval()
    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            batch_outputs = model(batch_X.to(device))
            outputs_list.append(batch_outputs.cpu())  # Move outputs back to CPU to free GPU memory
    outputs = torch.cat(outputs_list, dim=0).cpu().numpy()


    mse = mean_squared_error(y_test, outputs)
    mae = mean_absolute_error(y_test, outputs)
    rmse = np.sqrt(mse)
    rmlse = np.sqrt(mean_squared_error(np.log1p(y_test), np.log1p(outputs)))
    r2 = r2_score(y_test, outputs)
    return mse, mae, rmse, r2,rmlse, runtime, model, epoch_losses, outputs

def do_plot_preds_of_fold(y_test, y_pred, model_name, fold):
    # if len(y_test) > 10000:
    #     y_test = pd.Series(y_test.numpy().squeeze()) if isinstance(y_test, torch.Tensor) else pd.Series(y_test.squeeze())
    #     y_pred = pd.Series(y_pred.squeeze()) if isinstance(y_pred, np.ndarray) else pd.Series(y_pred)

    #     random_indices = np.random.choice(len(y_test), 10000, replace=False)
    #     try:
    #         y_test_subset = pd.Series(y_test).iloc[random_indices]
    #         y_pred_subset = pd.Series(y_pred).iloc[random_indices]
    #     except Exception as e:
    #         print("Type of y_test:", type(y_test))
    #         print("Type of y_pred:", type(y_pred))
    #         print(e)
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     plots.plot_predictions( y_test_subset, y_pred_subset,fold, model_name,
    #             f"{AGGREGATED_OUTDIR}/{model_name}_{fold}_ypreds_first10k_{timestamp}.png")
    # else:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plots.plot_predictions( y_test, y_pred,fold, model_name,
            f"{AGGREGATED_OUTDIR}/{model_name}_{fold}_ypreds_{timestamp}.png")

def save_model_log_results(best_cv_perfs, best_params,best_eval_func,best_models_ensemble, model_name):
    print(f"Best Hyperparameters: {best_params}")
    print(f"Best {EVAL_FUNC_METRIC.upper()} across all folds: {best_eval_func:.4f}")
    for idx, model in enumerate(best_models_ensemble):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = os.path.join(
            MODELS_OUTDIR, 
            f"{model_name}_fold_{idx + 1}_{timestamp}.joblib"
        )
        joblib.dump(model, model_path)
        print(f"Saved model for fold {idx + 1} at: {model_path}")

    log_entry = (
        f"Model: {model_name}\n"
        f"Saved Path: {model_name}_fold_x_yymmddhhmmss.joblib\n"  
        f"Timestamp: {timestamp}\n"
        f"Best Hyperparameters: {best_params}\n"
        f"Cross-validation Performance:\n"
        f"    Accuracy: {best_cv_perfs['Accuracy']:.4f}\n"
        f"    Precision: {best_cv_perfs['Precision']:.4f}\n"
        f"    Recall: {best_cv_perfs['Recall']:.4f}\n"
        f"    F1 Score: {best_cv_perfs['F1_score']:.4f}\n"
        f"    ROC AUC: {best_cv_perfs['ROC_AUC']:.4f}\n"
        f"    Runtime: {best_cv_perfs['runtime']:.2f} seconds\n"
        f"{'#' * 50}\n"
    )
    
    with open(MODEL_ALL_LOG_FILE, "a") as log_file:
        log_file.write(log_entry)

def label_hyperparameter_tuning(X,y, device, model_name, do_cv=0):
    # Define hyperparameter grid
    param_grid = {
        'hidden_dim': [
                    1024,
                       10000,
                       ],
        'dropout_rate': [
            0.001,
                        0,
                         ],
        'lr': [
            .0005, 
               .0001],
        'weight_decay': [0.0,
                        .001,
                          ],
    }
    best_eval_func = -np.inf 
    best_params = None
    best_models_ensemble = None
    best_cv_perfs = None
    kf = KFold(n_splits=K_FOLD_CV, shuffle=True, random_state=GT_ID)

    # Loop through hyperparameters
    for hidden_dim in param_grid['hidden_dim']:
        for dropout_rate in param_grid['dropout_rate']:
            for weight_decay in param_grid['weight_decay']:
                for lr in param_grid['lr']:
                    params_dict = {
                        'hidden_dim': hidden_dim,
                        'dropout_rate': dropout_rate,
                        'weight_decay': weight_decay,
                        'lr': lr
                    }
                    criterion = nn.CrossEntropyLoss()
                    ############################# for kfold implemntation
                    avg_metrics_per_cv = {
                        "Accuracy": [],
                        "Precision": [],
                        "Recall": [],
                        "F1 Score": [],
                        "ROC AUC": [],
                        "runtime": []
                    }
                    cv_losses = []
                    fold_models = [] 
                    
                    for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X) if do_cv else [(range(len(X)), range(len(X)))]):
                        print(f"Starting fold {fold_idx + 1}")
                        X_train, X_val = X[train_idx], X[val_idx]
                        y_train, y_val = y[train_idx], y[val_idx]
                        accuracy, precision, recall, f1, roc_auc, runtime, model, epoch_losses, outputs = train_nn_early_stop_classification(
                            X_train, y_train, X_val, y_val, device, params_dict, criterion, model_name
                        )

                        avg_metrics_per_cv["Accuracy"].append(accuracy)
                        avg_metrics_per_cv["Precision"].append(precision)
                        avg_metrics_per_cv["Recall"].append(recall)
                        avg_metrics_per_cv["F1 Score"].append(f1)
                        avg_metrics_per_cv["ROC AUC"].append(roc_auc)
                        avg_metrics_per_cv["runtime"].append(runtime)
                        #####
                        cv_losses.append(epoch_losses)
                        fold_models.append(model)
                        ######
                        do_plot_preds_of_fold(y_val, outputs, model_name, fold_idx)
                        # plots.plot_epoch_losses(epoch_losses, f"{AGGREGATED_OUTDIR}/cv_losses_{model_name}_fold_{fold_idx}.png")
                        

                    #once get the average of all folds
                    for metric, values in avg_metrics_per_cv.items():
                        avg_metrics_per_cv[metric] = np.mean(values)
                    eval_metric_value = {
                        "accuracy": avg_metrics_per_cv["Accuracy"],
                        "precision": avg_metrics_per_cv["Precision"],
                        "recall": avg_metrics_per_cv["Recall"],
                        "f1": avg_metrics_per_cv["F1 Score"],
                        "roc_auc": avg_metrics_per_cv["ROC AUC"]
                    }.get(EVAL_FUNC_METRIC.lower(), avg_metrics_per_cv["Accuracy"])  # Default to MAE if metric is undefined

                    # Compare overall performance to global best
                    if eval_metric_value > best_eval_func:
                        print(f"New global best model found for {EVAL_FUNC_METRIC}: {eval_metric_value:.4f}")
                        best_eval_func = eval_metric_value
                        best_params = params_dict
                        best_cv_perfs = avg_metrics_per_cv
                        best_models_ensemble = fold_models
    save_model_log_results(best_cv_perfs, best_params,best_eval_func,best_models_ensemble, model_name)
    return best_cv_perfs, best_params,best_eval_func, best_models_ensemble

def compute_weights(y_train):
    # Initialize an array of weights with default value of 1
    weights = np.ones_like(y_train, dtype=float)
    
    # Define proximity thresholds for the target ranges
    # Adjust these thresholds as needed
    weight_decrease_range = 1200  # Decrease weight for values near 1200
    weight_increase_ranges = [50, 2500]  # Increase weight for values near 50 and 2500
    
    # Compute the weights
    for i, target_value in enumerate(y_train):
        # Decrease weight for values near 1200 (within a defined range)
        if abs(target_value - weight_decrease_range) < 100:  # Adjust proximity range as needed
            weights[i] = 0.1  # Reduce weight for values near 1200
        
        # Increase weight for values near 50 and 2500
        elif any(abs(target_value - x) < 100 for x in weight_increase_ranges):
            weights[i] = 3.0  # Increase weight for values near 50 or 2500
    
    return weights



# Custom Binning Transformer
class BinningTransformer:
    def __init__(self, bins):
        self.bins = bins

    def transform(self, y):
        # print("Original y before binning:", np.unique(y))
        y = np.ravel(y)  # Ensure 1D array
        bin_labels = pd.cut(y, bins=self.bins, labels=range(len(self.bins) - 1))
        bin_labels = bin_labels.astype(int)  # Ensure integer labels
        # print("Transformed bin labels (integers):", np.unique(bin_labels))
        return bin_labels

def brute_force_binning(X_train, y_train):
    print("Shapes of X_train and y_train:", X_train.shape, y_train.shape)

    # Define parameter grid
    binning_strategies = [
        # [0, 300, 500, 1000, 1300, 2000, 3000, np.inf],
        # [0, 200, 400, 800, 1200, 1600, 2000, 3000, np.inf],
        # [0, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, np.inf],
        # [0, 100, 500, 900, 1300, 1700, 2100, 2600, 3100, np.inf],
        # [0, 150, 300, 600, 1200, 1800, 2500, 3200, np.inf],
        [0, 400, 800, 1200, 2000, 3000, 4000, np.inf],
        # [0, 500, 1000, 1500, 2000, 2500, 3000, np.inf],
        # [0, 100, 300, 600, 900, 1200, 1800, 2400, 3000, np.inf],
        # [0, 200, 400, 600, 800, 1000, 1400, 1800, 2200, 3000, np.inf],
        # [0, 100, 250, 500, 1000, 2000, 3000, np.inf],
        # [0, 200, 450, 700, 950, 1200, 1700, 2300, 2900, np.inf],
        # [0, 100, 300, 500, 800, 1200, 2000, 3000, np.inf],
        # [0, 250, 500, 1000, 1500, 2000, 3000, np.inf],
        # [0, 50, 100, 250, 500, 1000, 1500, 2000, 3000, np.inf],
        # [0, 200, 400, 600, 800, 1200, 1600, 2000, 3000, np.inf],
        # [0, 300, 600, 900, 1200, 1500, 1800, 2100, 2400, 3000, np.inf],
        # [0, 200, 500, 1000, 1500, 2000, 2500, 3000, np.inf],
        # [0, 150, 400, 700, 1000, 1400, 1800, 2200, 3000, np.inf],
        # [0, 500, 1000, 2000, 3000, 4000, np.inf],
        # [0, 200, 600, 1200, 1800, 2400, 3000, np.inf],
        [0, 100, 400, 900, 1600, 2500, 3000, np.inf],
        [0, 200, 400, 900,1200, 1600,2000 ,2500, 3000, np.inf],
    ]
    learning_rates = [0.1,.25,.5]
    max_depths = [15,20,25]
    n_estimators = [50 ]

    # Splitting training data for evaluation
    X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
        X_train, y_train, test_size=0.2, random_state=GT_ID
    )

    best_score = 0
    best_params = {}

    # Brute-force grid search
    for bins in binning_strategies:
        binning_transformer = BinningTransformer(bins=bins)
        y_train_binned = binning_transformer.transform(y_train_split)
        y_val_binned = binning_transformer.transform(y_val_split)

        for learning_rate in learning_rates:
            for max_depth in max_depths:
                for n_estimator in n_estimators:
                    print(
                        f"Testing bins={bins}, learning_rate={learning_rate}, "
                        f"max_depth={max_depth}, n_estimators={n_estimator}"
                    )

                    # Train the model
                    model = XGBClassifier(
                        objective="multi:softmax",
                        learning_rate=learning_rate,
                        max_depth=max_depth,
                        n_estimators=n_estimator,
                        random_state=42
                    )
                    model.fit(X_train_split, y_train_binned)

                    # Predict and evaluate
                    y_val_pred = model.predict(X_val_split)
                    score = accuracy_score(y_val_binned, y_val_pred)

                    print(f"Accuracy: {score:.4f}")

                    # Update best parameters if this configuration is better
                    if score > best_score:
                        best_score = score
                        best_params = {
                            "bins": bins,
                            "learning_rate": learning_rate,
                            "max_depth": max_depth,
                            "n_estimators": n_estimator,
                        }

    print("Best Parameters:", best_params)
    print("Best Accuracy:", best_score)


def objective(trial, X_train, y_train):
    # Define binning strategies to choose from
    binning_strategies = [
        [0, 100, 400, 900, 1600, 2500, 3000, np.inf],
        [0, 200, 400, 900,1200, 1600,2000 ,2500, 3000, np.inf],
        [0, 400, 800, 1200, 2000, 3000, 4000, np.inf],
        [0, 100, 200,350,650,800, 1000, 1100,1200, 1300, 1600 ,2000, 2500, 3200, 4000, np.inf],
    ]

    # Split dataset
    X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42
    )

    # Sampling binning strategy
    bins = trial.suggest_categorical("bins", binning_strategies)
    binning_transformer = BinningTransformer(bins=bins)
    y_train_binned = binning_transformer.transform(y_train_split)
    y_val_binned = binning_transformer.transform(y_val_split)

    # Model hyperparameters
    learning_rate = trial.suggest_float("learning_rate", 0.5, 2)
    max_depth = trial.suggest_int("max_depth", 35, 60)
    n_estimators = trial.suggest_int("n_estimators", 100, 250, step=50)

    # Train model
    model = XGBClassifier(
        objective="multi:softmax",
        learning_rate=learning_rate,
        max_depth=max_depth,
        n_estimators=n_estimators,
        random_state=GT_ID,
    )
    model.fit(X_train_split, y_train_binned)

    # Evaluate
    y_val_pred = model.predict(X_val_split)
    score = accuracy_score(y_val_binned, y_val_pred)

    return score

# {'bins': [0, 100, 400, 900, 1600, 2500, 3000, inf], 'learning_rate': 0.11651199016626823, 'max_depth': 16, 'n_estimators': 75}. .364

# Best Params: {'bins': [0, 100, 400, 900, 1600, 2500, 3000, inf], 'learning_rate': 0.1506431538401803, 'max_depth': 32, 'n_estimators': 100}
# Best Accuracy: 0.3603535828474704
# def get_bayes_opt(X_train, y_train):

#     # Optimize
#     study = optuna.create_study(direction="maximize")
#     study.optimize(lambda trial: objective(trial, X_train, y_train), n_trials=50)

#     # Best results
#     print("Best Params:", study.best_params)
#     print("Best Accuracy:", study.best_value)


def ml_perf_eval_by_country(test_results_df, trained_models):
    

    metrics_list = []
    metrics_list_by_cluster = []
    feature_importance_list = []

    # Extract model prediction columns (e.g., y_pred_decision_tree)
    model_pred_cols = [col for col in test_results_df.columns if col.startswith("y_pred_")]
    print(f"🧠 Found model prediction columns: {model_pred_cols}")
    print(test_results_df.head())

    # Get feature columns (excluding y_test, economy_code, and model predictions)
    feature_columns = test_results_df.drop(columns=["y_test", "economy_code", "population", "regionwb"] + model_pred_cols).columns

    for model_col in model_pred_cols:
        model_name = model_col.replace("y_pred_", "")  # Extract model name
        grouped = test_results_df.groupby("economy_code")
        print("Running for ", model_name)

        for cluster_method in ["km_clus", "gmm_clus" ]: #"dbscan_clus"
            clustered = test_results_df.groupby(cluster_method)

            # For each cluster in the clustering method, calculate metrics
            for cluster_label, cluster_group in clustered:
                y_true = cluster_group["y_test"]
                y_pred = cluster_group[model_col]
                # Debug outputs
                

                # Compute performance metrics for each cluster
                accuracy = accuracy_score(y_true, y_pred)
                f1 = f1_score(y_true, y_pred, average="weighted")
                precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)

                cluster_size = len(cluster_group)

                metrics_list_by_cluster.append({
                    "model": model_name,
                    "cluster_method": cluster_method,  # Which clustering method was used
                    "cluster_label": cluster_label,  # Label of the current cluster
                    "cluster_size": cluster_size,  # Number of rows in this cluster
                    "accuracy": accuracy,
                    "f1_score": f1,
                    "precision": precision
                })


        for econ_code, group in grouped:
            y_true = group["y_test"]
            y_pred = group[model_col]
            X_subset = group[feature_columns]
            econ_code_size = len(group)
            population = group["population"].iloc[0]
            regionwb   = group["regionwb"].iloc[0]

            # Compute performance metrics
            accuracy = accuracy_score(y_true, y_pred)
            f1 = f1_score(y_true, y_pred, average="weighted")
            precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)

            metrics_list.append({
                "economy_code": econ_code,
                "econ_size": econ_code_size,
                "regionwb":     regionwb,
                "population":   population,
                "model": model_name,
                "accuracy": accuracy,
                "f1_score": f1,
                "precision": precision
            })

            # Compute feature importance using permutation importance
            if model_name in trained_models:
                model = trained_models[model_name]
                perm_importance = permutation_importance(model, X_subset, y_true, scoring="accuracy", n_repeats=5, random_state=42)

                for feature, importance in zip(feature_columns, perm_importance.importances_mean):
                    feature_importance_list.append({
                        "economy_code": econ_code,
                        "model": model_name,
                        "feature": feature,
                        "importance": importance
                    })

    # Convert lists to DataFrames
    metrics_df = pd.DataFrame(metrics_list)
    feature_importance_df = pd.DataFrame(feature_importance_list)

    return metrics_df, feature_importance_df, metrics_list_by_cluster



def save_trained_models(results, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for model_name, model_results in results.items():
        model_name_formatted = model_name.lower().replace(" ", "_")  # format model name
        model = model_results["model"]  # Extract the trained model from the results
        # Define the file path for saving the model
        model_save_path = os.path.join(output_dir, f"{model_name_formatted}_model.pkl")
        joblib.dump(model, model_save_path)
        print(f"Model '{model_name}' saved to: {model_save_path}")