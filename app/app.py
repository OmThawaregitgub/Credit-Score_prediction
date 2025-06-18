from flask import Flask, render_template, request, jsonify
from prediction_helper import predict
from pathlib import Path
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Get all form inputs exactly matching Streamlit version
            age = int(request.form.get('age', 28))
            income = int(request.form.get('income', 1200000))
            loan_amount = int(request.form.get('loan_amount', 2560000))
            loan_tenure_months = int(request.form.get('loan_tenure_months', 36))
            avg_dpd_per_delinquency = int(request.form.get('avg_dpd_per_delinquency', 20))
            delinquency_ratio = int(request.form.get('delinquency_ratio', 30))
            credit_utilization_ratio = int(request.form.get('credit_utilization_ratio', 30))
            num_open_accounts = int(request.form.get('num_open_accounts', 2))
            residence_type = request.form.get('residence_type', 'Owned')
            loan_purpose = request.form.get('loan_purpose', 'Education')
            loan_type = request.form.get('loan_type', 'Unsecured')

            # Calculate loan to income ratio (matches Streamlit calculation)
            loan_to_income_ratio = loan_amount / income if income > 0 else 0

            # Call predict function with exact same parameters as Streamlit version
            probability, credit_score, rating = predict(
                age, income, loan_amount, loan_tenure_months, 
                avg_dpd_per_delinquency, delinquency_ratio,
                credit_utilization_ratio, num_open_accounts,
                residence_type, loan_purpose, loan_type
            )

            return jsonify({
                'probability': f"{probability:.2%}",
                'credit_score': credit_score,
                'rating': rating,
                'loan_to_income_ratio': f"{loan_to_income_ratio:.2f}"
            })

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return jsonify({'error': str(e)}), 400

    # Render template with default values matching Streamlit
    return render_template('index.html', 
                          default_age=28,
                          default_income=1200000,
                          default_loan_amount=2560000,
                          default_loan_tenure_months=36,
                          default_avg_dpd_per_delinquency=20,
                          default_delinquency_ratio=30,
                          default_credit_utilization_ratio=30,
                          default_num_open_accounts=2)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)