import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os
from pathlib import Path

# Path to the saved model and its components
BASE_DIR = Path(__file__).parent.parent  # Goes up one level from app/
MODEL_PATH = BASE_DIR / 'artifacts' / 'model_data.joblib'

# Debugging output
print(f"Model path: {MODEL_PATH}")
print(f"Path exists: {os.path.exists(MODEL_PATH)}")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")

# Load the model and its components
try:
    model_data = joblib.load(MODEL_PATH)
    model = model_data['model']
    scaler = model_data['scaler']
    features = model_data['features']
    cols_to_scale = model_data['cols_to_scale']
except Exception as e:
    raise ValueError(f"Error loading model: {str(e)}")

def prepare_input(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
                delinquency_ratio, credit_utilization_ratio, num_open_accounts, 
                residence_type, loan_purpose, loan_type):
    # [Rest of your prepare_input function]
    input_data = {
        'age': age,
        'loan_tenure_months': loan_tenure_months,
        'number_of_open_accounts': num_open_accounts,
        'credit_utilization_ratio': credit_utilization_ratio,
        'loan_to_income': loan_amount / income if income > 0 else 0,
        'delinquency_ratio': delinquency_ratio,
        'avg_dpd_per_delinquency': avg_dpd_per_delinquency,
        'residence_type_Owned': 1 if residence_type == 'Owned' else 0,
        'residence_type_Rented': 1 if residence_type == 'Rented' else 0,
        'loan_purpose_Education': 1 if loan_purpose == 'Education' else 0,
        'loan_purpose_Home': 1 if loan_purpose == 'Home' else 0,
        'loan_purpose_Personal': 1 if loan_purpose == 'Personal' else 0,
        'loan_type_Unsecured': 1 if loan_type == 'Unsecured' else 0,
        'number_of_dependants': 1,
        'years_at_current_address': 1,
        'zipcode': 1,
        'sanction_amount': 1,
        'processing_fee': 1,
        'gst': 1,
        'net_disbursement': 1,
        'principal_outstanding': 1,
        'bank_balance_at_application': 1,
        'number_of_closed_accounts': 1,
        'enquiry_count': 1
    }

    df = pd.DataFrame([input_data])
    df[cols_to_scale] = scaler.transform(df[cols_to_scale])
    return df[features]

def calculate_credit_score(input_df, base_score=300, scale_length=600):
    x = np.dot(input_df.values, model.coef_.T) + model.intercept_
    default_probability = 1 / (1 + np.exp(-x))
    non_default_probability = 1 - default_probability
    credit_score = base_score + non_default_probability.flatten() * scale_length
    
    def get_rating(score):
        if 300 <= score < 500: return 'Poor'
        elif 500 <= score < 650: return 'Average'
        elif 650 <= score < 750: return 'Good'
        elif 750 <= score <= 900: return 'Excellent'
        return 'Undefined'
    
    return default_probability.flatten()[0], int(credit_score[0]), get_rating(credit_score[0])

def predict(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
           delinquency_ratio, credit_utilization_ratio, num_open_accounts,
           residence_type, loan_purpose, loan_type):
    input_df = prepare_input(age, income, loan_amount, loan_tenure_months,
                           avg_dpd_per_delinquency, delinquency_ratio,
                           credit_utilization_ratio, num_open_accounts,
                           residence_type, loan_purpose, loan_type)
    return calculate_credit_score(input_df)
