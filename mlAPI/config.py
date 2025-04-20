import socket

# Determine the hostname
hostname = socket.gethostname()
# if hostname == "Khais-MacBook-Pro.local" or hostname == "Khais-MBP.attlocal.net":  
#     from config_mac import *  
# else:
#     from config_cuda import * 

import os

TRAIN_PATH_big = os.path.join(os.getcwd(), 'data', 'dataset_2025-02-24T21_33_33.716368723Z_DEFAULT_INTEGRATION_IMF.STA_FAS_1.0.1.csv')
# TRAIN_PATH_2011 = os.path.join(os.getcwd(), 'data', 'findex2011_micro_WORLD.csv')
# TRAIN_PATH_2014 = os.path.join(os.getcwd(), 'data', 'findex2014_micro_world.csv') #schema mismatch, need manual patch :(
TRAIN_PATH_2017 = os.path.join(os.getcwd(), 'data', 'findex2017_micro_world.csv')
TRAIN_PATH_2021 = os.path.join(os.getcwd(), 'data', 'findex2021_micro_world_139countries.csv')
GT_ID = 42

TEST_PATH = os.path.join(os.getcwd(), 'data', 'test.csv')
PROCESSED_TEST_PATH = os.path.join(os.getcwd(), 'data', 'test_processed.csv')

DATASET_SELECTION = "findex"
PRED_TYPE = "classifier" #or "regression", "classifier"

EVAL_FUNC_METRIC = 'accuracy' #'mae'  #rmse #'f1' # 'accuracy' 
N_ESTIMATOR = 14
TEST_SIZE = .3
TARGET_COL = "fin7" #fin7, fin8b - criteria: <40% null rows and interesting
UL_CLUSTER_COUNT = 6 #3, 5, 7, 12 - criteria: ~ arbitrary
##############################
TRAIN_PATH = TRAIN_PATH_2021
YEAR_FILTER = 2021 #2021, 2017, 2014, 2011 - criteria: use whatever year is in main name of csv

##############################
ECONOMY_SAVE_PATH = os.path.join(os.getcwd(), 'data', f'economies_survey_year{YEAR_FILTER}.pkl')
PROCESSED_TRAIN_PATH = os.path.join(os.getcwd(), 'data', f'train_processed_{TARGET_COL}_target_{UL_CLUSTER_COUNT}_clusters_{YEAR_FILTER}_year.pkl')
DRAFT_VER_A3 = f"_{TARGET_COL}_target_{UL_CLUSTER_COUNT}_clusters_{TEST_SIZE}_test_{YEAR_FILTER}_year"

EVAL_MODELS = [
                # 'default',
                'MPL',
                'CNN', 
                'LSTM', 
                'bi-LSTM',
                'conv-LSTM', 
                #'seg-gru',
                ]

PARAM_GRID = {
    'lr': [0.01, 0.005, 0.0005],
    'batch_size': [16, 32],
    
    # 'hidden_layers': [[75,19]],
    'dropout_rate': [0, 0.005, 0.01, ],
    'hidden_layers': [[64, 32], [128, 64, 32], [64],[75]],
    # 'activation_function': just use relu
}

GRAPH_COL_NUM = 4

from pathlib import Path
def set_output_dir(path):
    # Ensure the directory exists
    os.makedirs(path, exist_ok=True)
    return path

project_root = Path(__file__).resolve().parent.parent
OUTPUT_DIR_A3 = project_root / 'outputs' 
# Set the directories using set_output_dir
AGGREGATED_OUTDIR = set_output_dir(OUTPUT_DIR_A3 / f'ver{DRAFT_VER_A3}_{EVAL_FUNC_METRIC}/aggregated_graphs')
Y_PRED_OUTDIR = set_output_dir(OUTPUT_DIR_A3 / f'ver{DRAFT_VER_A3}_{EVAL_FUNC_METRIC}/y_pred_graphs')
CV_LOSSES_PKL_OUTDIR = set_output_dir(OUTPUT_DIR_A3 / f'ver{DRAFT_VER_A3}_{EVAL_FUNC_METRIC}/pkl_cv')
PERFM_PKL_OUTDIR = set_output_dir(OUTPUT_DIR_A3 / f'ver{DRAFT_VER_A3}_{EVAL_FUNC_METRIC}/perf_pkl')
MODELS_OUTDIR = set_output_dir(OUTPUT_DIR_A3 / f'ver{DRAFT_VER_A3}_{EVAL_FUNC_METRIC}/saved_models')
LABEL_ENCODERS_PKL_OUTDIR = set_output_dir(OUTPUT_DIR_A3 / f'ver{DRAFT_VER_A3}_{EVAL_FUNC_METRIC}/label_encoders')
SOLUTIONS_OUTDIR = set_output_dir(OUTPUT_DIR_A3 / f'ver{DRAFT_VER_A3}_{EVAL_FUNC_METRIC}/solutions')
TXT_OUTDIR = set_output_dir(OUTPUT_DIR_A3 / f'ver{DRAFT_VER_A3}_{EVAL_FUNC_METRIC}/txt_stats')
OUTPUT_DIR_RAW_DATA_A3 =set_output_dir(OUTPUT_DIR_A3 / f'ver{DRAFT_VER_A3}_{EVAL_FUNC_METRIC}/raw_data_assessments')

MODEL_ALL_LOG_FILE = os.path.join(os.getcwd(), TXT_OUTDIR, 'all_models_logs.txt')


#ML PARAMS
K_FOLD_CV = 5



#findex col des
FINDEX_DATA_DICT = {
    "economy": "Economy",
    "economycode": "Economy Code",
    "regionwb": "Regional code",
    "pop_adult": "Population 15+, 2020, WDI",
    "wpid_random": "Gallup World Poll identifier",
    "wgt": "Weight",
    "female": "Respondent is female",
    "age": "Respondent age",
    "educ": "Respondent education level",
    "inc_q": "Within-economy household income quintile",
    "emp_in": "Respondent is in workforce",
    "urbanicity_f2f": "Respondent lives in rural area",
    "account": "Has an account",
    "account_fin": "Has an account at a financial institution",
    "account_mob": "Has a mobile money account",
    "fin1_1a": "Opened first account to receive a wage payment",
    "fin1_1b": "Opened first account to receive money from the government",
    "fin2": "Has a debit card",
    "fin3": "If has debit card: card in own name",
    "fin4": "Used a debit card",
    "fin4a": "Used a debit card in-store",
    "fin5": "Used a mobile phone or internet to access account",
    "fin6": "Used a mobile phone or internet to check account balance",
    "fin7": "Has a credit card",
    "fin8": "Used a credit card",
    "fin8a": "Used a credit card in-store",
    "fin8b": "Paid credit card balances in full",
    "fin9": "Made any deposit into the account",
    "fin9a": "Make deposits into the account two or more times per month",
    "fin10": "Withdrew from the account",
    "fin10_1a": "Reason for inactive account: too far",
    "fin10_1b": "Reason for inactive account: no need",
    "fin10_1c": "Reason for inactive account: lack money",
    "fin10_1d": "Reason for inactive account: not comfortable using it",
    "fin10_1e": "Reason for inactive account: lack trust",
    "fin10a": "Withdrew from the account two or more times per month",
    "fin10b": "Used account to store money",
    "fin11_1": "Unbanked: use account without help",
    "fin11a": "Reason for no account: too far",
    "fin11b": "Reason for no account: too expensive",
    "fin11c": "Reason for no account: lack documentation",
    "fin11d": "Reason for no account: lack trust",
    "fin11e": "Reason for no account: religious reasons",
    "fin11f": "Reason for no account: lack money",
    "fin11g": "Reason for no account: family member already has one",
    "fin11h": "Reason for no account: no need for financial services",
    "fin13_1a": "Reason for no mobile money account: too far",
    "fin13_1b": "Reason for no mobile money account: too expensive",
    "fin13_1c": "Reason for no mobile money account: lack documentation",
    "fin13_1d": "Reason for no mobile money account: lack of money",
    "fin13_1e": "Reason for no mobile money account: use agent",
    "fin13_1f": "Reason for no mobile money account: no mobile phone",
    "fin13a": "Use mobile money account two or more times a month",
    "fin13b": "Use mobile money account to store money",
    "fin13c": "Use mobile money account to borrow money",
    "fin13d": "Use mobile money account without help",
    "fin14_1": "Use mobile phone to pay for a purchase in-store",
    "fin14_2": "Paid digitally for an in-store purchase for the first time after COVID-19",
    "fin14_2_China": "Paid digitally for an in-store purchase for the first time since 2020",
    "fin14a": "Made bill payments online using the Internet",
    "fin14a1": "Send money to a relative or friend online using the Internet",
    "fin14b": "Bought something online using the Internet",
    "fin14c": "Paid online or in cash at delivery",
    "fin14c_2": "Paid online for an online purchase for the first time after COVID-19",
    "fin14c_2_China": "Paid online for an online purchase for the first time since 2020",
    "fin15": "Saved in past 12 months: for farm/business purposes",
    "fin16": "Saved for old age",
    "fin17a": "Saved using an account at a financial institution",
    "fin17a1": "Saved using a mobile money account",
    "fin17b": "Saved using an informal savings club",
    "fin19": "Has loan from a financial institution for home, apartment, or land",
    "fin20": "Borrowed for medical purposes",
    "fin21": "Borrowed in past 12 months: for farm/business purposes",
    "fin22a": "Borrowed from a financial institution",
    "fin22b": "Borrowed from family or friends",
    "fin22c": "Borrowed from an informal savings club",
    "fin24": "Main source of emergency funds in 30 days",
    "fin24a": "Difficulty of emergency funds in 30 days",
    "fin24b": "Difficulty of emergency funds in 7 days",
    "fin26": "Sent domestic remittances",
    "fin27_1": "Sent domestic remittances through an account",
    "fin27c1": "Sent domestic remittances in cash",
    "fin27c2": "Sent domestic remittances through an MTO",
    "fin28": "Received domestic remittances",
    "fin29_1": "Received domestic remittances through an account",
    "fin29c1": "Received domestic remittances in cash",
    "fin29c2": "Received domestic remittances through an MTO",
    "fin30": "Paid a utility bill",
    "fin31a": "Paid a utility bill using an account",
    "fin31b": "Paid a utility bill using a mobile phone",
    "fin31b1": "Paid a utility bill from an account or mobile phone for the first time after the",
    "fin31b1_China": "Paid a utility bill from an account or mobile phone for the first time since 202",
    "fin31c": "Paid a utility bill in cash",
    "fin32": "Received wage payments",
    "fin33": "Received public sector wage payments",
    "fin34a": "Received wage payments into an account",
    "fin34b": "Received wage payments to a mobile phone",
    "fin34d": "Received wage payments in cash",
    "fin34e": "Received wage payments to a card",
    "fin35": "Received wage payments into an account or to a phone or a card and paid higher t",
    "fin37": "Received a government transfer",
    "fin38": "Received a government pension",
    "fin39a": "Received a government transfer or pension into an account",
    "fin39b": "Received a government transfer or pension to a mobile phone",
    "fin39d": "Received a government transfer or pension in cash",
    "fin39e": "Received a government transfer or pension to a card",
    "fin42": "Received an agricultural payment",
    "fin42a": "Grow own crops or raise livestock",
    "fin43a": "Received an agricultural payment into an account",
    "fin43b": "Received an agricultural payment to a mobile phone",
    "fin43d": "Received an agricultural payment in cash",
    "fin43e": "Received an agricultural payment to a card",
    "fin44a": "Financially worried: old age",
    "fin44b": "Financially worried: medical cost",
    "fin44c": "Financially worried: bills",
    "fin44d": "Financially worried: education",
    "fin45": "Financially most worried",
    "fin45_1": "Financially worried due to COVID-19",
    "fin45_1_China": "Financial worry",
    "saved": "Saved in the past year",
    "borrowed": "Borrowed in the past year",
    "receive_wages": "Received a wage payment",
    "receive_transfers": "Received a government transfer payment",
    "receive_pension": "Received a government pension payment",
    "receive_agriculture": "Received a payment for the sale of agricultural goods",
    "pay_utilities": "Paid a utility bill",
    "remittances": "Made or received a domestic remittance payment",
    "mobileowner": "Owns a mobile phone",
    "internetaccess": "Internet access",
    "anydigpayment": "Made or received a digital payment",
    "merchantpay_dig": "Made a digital merchant payment",
    "year": "Year"
}

FINDEX_DATA_DICT_2014 = {
    "economy": "Economy",
    "economycode": "Economy Code",
    "wpid_random": "Gallup World Poll identifier",
    "wgt": "Weight",
    "female": "Respondent is female",
    "age": "Respondent age",
    "educ": "Respondent education level",
    "inc_q": "Within-economy household income quintile",
    "account": "Has an account",
    "account_fin": "Has an account at a financial institution",
    "account_mob": "Has a mobile money account",
    "q2": "Has a debit card",
    "q3": "If has debit card: card in own name",
    "q4": "If has debit card: used card in past 12 months",
    "q5": "Has a credit card",
    "q6": "If has credit card: used card in past 12 months",
    "q8a": "If does not have account: b/c too far away",
    "q8b": "If does not have account: b/c too expensive",
    "q8c": "If does not have account: b/c lack documentation",
    "q8d": "If does not have account: b/c lack trust",
    "q8e": "If does not have account: b/c religious reasons",
    "q8f": "If does not have account: b/c lack of money",
    "q8g": "If does not have account: b/c family member already has one",
    "q8h": "If does not have account: b/c cannot get one",
    "q8i": "If does not have account: b/c no need for financial services",
    "q9": "If has account: any deposit into account in past 12 months",
    "q10": "If has any deposit into account: number of monthly deposits",
    "q11": "If has account: any withdrawal from account in past 12 months",
    "q12": "If has any withdrawal from account: number of monthly withdrawals",
    "q13": "If has account: most frequent mode of cash withdrawal",
    "q14": "If has account: made a transaction using a mobile phone",
    "q16": "Made payments online using the Internet",
    "q17a": "Saved in past 12 months: for farm/business purposes",
    "q17b": "Saved in past 12 months: for old age",
    "q17c": "Saved in past 12 months: for education or school fees",
    "q18a": "Saved in past 12 months: using an account at a financial institution",
    "q18b": "Saved in past 12 months: using an informal savings club",
    "q20": "Has loan from a financial institution for house, apartment, or land",
    "q21a": "Borrowed in past 12 months: from a financial institution",
    "q21b": "Borrowed in past 12 months: from a store (store credit)",
    "q21c": "Borrowed in past 12 months: from family or friends",
    "q21d": "Borrowed in past 12 months: from another private lender",
    "q22a": "Borrowed in past 12 months: for education or school fees",
    "q22b": "Borrowed in past 12 months: for medical purposes",
    "q22c": "Borrowed in past 12 months: for farm/business purposes",
    "q24": "Possibility of coming up with emergency funds",
    "q25": "If able to come up with emergency funds: main source",
    "q26": "Sent domestic remittances in past 12 months",
    "q27a": "If sent domestic remittances: in cash",
    "q27b": "If sent domestic remittances: through a financial institution",
    "q27c": "If sent domestic remittances: through a mobile phone",
    "q27d": "If sent domestic remittances: through an MTO",
    "q28": "Received domestic remittances in past 12 months",
    "q29a": "If received domestic remittances: in cash",
    "q29b": "If received domestic remittances: through a financial institution",
    "q29c": "If received domestic remittances: through a mobile phone",
    "q29d": "If received domestic remittances: through an MTO",
    "q30": "Paid utility bills in past 12 months",
    "q31a": "If paid utility bills: in cash",
    "q31b": "If paid utility bills: using an account",
    "q31c": "If paid utility bills: through a mobile phone",
    "q32": "Paid school fees in past 12 months",
    "q33a": "If paid school fees: in cash",
    "q33b": "If paid school fees: using an account",
    "q33c": "If paid school fees: through a mobile phone",
    "q34": "Received wage payments in past 12 months",
    "q35": "If received wage payments: work in public sector",
    "q36a": "If received wage payments: in cash",
    "q36bc": "If received wage payments: into an account or to a card",
    "q36d": "If received wage payments: through a mobile phone",
    "q37": "If received cashless wage payments: account use",
    "q38": "If received cashless wage payments: account type",
    "q39": "Received government transfers in past 12 months",
    "q40a": "If received government transfers: in cash",
    "q40bc": "If received government transfers: into an account or to a card",
    "q40d": "If received government transfers: through a mobile phone",
    "q41": "If received cashless government transfers: account use",
    "q42": "If received cashless government transfers: account type",
    "q43": "Received agricultural payments in past 12 months",
    "q44a": "If received agricultural payments: in cash",
    "q44b": "If received agricultural payments: into an account",
    "q44c": "If received agricultural payments: through a mobile phone",
    "saved": "Saved in the past year",
    "borrowed": "Borrowed in the past year"
}

MODIFIED_DATA_DICT = {key: value.lower().replace(" ", "_") for key, value in FINDEX_DATA_DICT.items()}
# columns without null values
COLUMNS_TO_KEEP =  [
    "economy", #duplicate with econoomy code
    "economycode",
    "regionwb",
    "pop_adult", #gonna need to log scale 
    "female", 
    "educ", "inc_q", "account", "account_fin", "fin7", "fin8b", "fin2", "fin14_1", "fin14a", 
    "fin14a1", "fin14b", "fin16", "fin17a", "fin20", "fin22a", "fin22b", 
    "fin24", "fin30", "fin32", "fin37", "fin38", "fin44a", "fin44b", 
    "fin44c", "fin44d", "saved", "borrowed", "receive_wages", "receive_transfers", 
    "receive_pension", "pay_utilities", "mobileowner", "internetaccess", 
    "anydigpayment", "year"  # Include 'year' for filtering
]
