import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os
from pathlib import Path

# Get the absolute path to the directory containing this script
current_dir = Path(__file__).parent

# Path to the saved model and its components
MODEL_PATH = current_dir / 'artifacts' / 'model_data.joblib'

def load_model():
    try:
        # Check if model file exists
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
            
        # Load the model and its components
        model_data = joblib.load(MODEL_PATH)
        return model_data
    except Exception as e:
        raise RuntimeError(f"Error loading model: {str(e)}")

# Load model at module level
try:
    model_data = load_model()
    model = model_data['model']
    scaler = model_data['scaler']
    features = model_data['features']
    cols_to_scale = model_data['cols_to_scale']
except Exception as e:
    raise RuntimeError(f"Failed to initialize model: {str(e)}")

def prepare_input(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
                delinquency_ratio, credit_utilization_ratio, num_open_accounts, residence_type,
                loan_purpose, loan_type):
    try:
        # Create a dictionary with input values
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
            # additional dummy fields for scaling
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

        # Create DataFrame
        df = pd.DataFrame([input_data])

        # Scale the required columns
        df[cols_to_scale] = scaler.transform(df[cols_to_scale])

        # Ensure the DataFrame contains only the features expected by the model
        df = df[features]

        return df
    except Exception as e:
        raise RuntimeError(f"Error preparing input: {str(e)}")

def predict(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
            delinquency_ratio, credit_utilization_ratio, num_open_accounts,
            residence_type, loan_purpose, loan_type):
    try:
        # Prepare input data
        input_df = prepare_input(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
                               delinquency_ratio, credit_utilization_ratio, num_open_accounts, residence_type,
                               loan_purpose, loan_type)

        probability, credit_score, rating = calculate_credit_score(input_df)

        return probability, credit_score, rating
    except Exception as e:
        raise RuntimeError(f"Prediction error: {str(e)}")

def calculate_credit_score(input_df, base_score=300, scale_length=600):
    try:
        x = np.dot(input_df.values, model.coef_.T) + model.intercept_

        # Apply the logistic function to calculate the probability
        default_probability = 1 / (1 + np.exp(-x))
        non_default_probability = 1 - default_probability

        # Convert the probability to a credit score
        credit_score = base_score + non_default_probability.flatten() * scale_length

        # Determine the rating category
        def get_rating(score):
            if 300 <= score < 500:
                return 'Poor'
            elif 500 <= score < 650:
                return 'Average'
            elif 650 <= score < 750:
                return 'Good'
            elif 750 <= score <= 900:
                return 'Excellent'
            else:
                return 'Undefined'

        rating = get_rating(credit_score[0])

        return default_probability.flatten()[0], int(credit_score[0]), rating
    except Exception as e:
        raise RuntimeError(f"Credit score calculation error: {str(e)}")
