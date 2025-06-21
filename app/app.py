import streamlit as st
from prediction_helper import predict

def main():
    st.set_page_config(page_title="Credit Scoring System", layout="wide")
    
    # Custom CSS for styling
    st.markdown("""
        <style>
            .main {
                padding: 2rem;
            }
            .stNumberInput, .stSelectbox {
                margin-bottom: 1rem;
            }
            .result-box {
                padding: 2rem;
                border-radius: 10px;
                background-color: #1e1e1e;
                margin-top: 2rem;
                color: white;
            }
            .metric-box {
                display: flex;
                justify-content: space-between;
                margin-bottom: 1.5rem;
            }
            .metric {
                text-align: center;
                padding: 1.5rem 1rem;
                border-radius: 8px;
                background-color: #2d2d2d;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                flex: 1;
                margin: 0 0.5rem;
            }
            .metric-label {
                font-size: 1rem;
                margin-bottom: 0.75rem;
                color: #a0a0a0;
                font-weight: 500;
            }
            .metric-value {
                font-size: 1.75rem;
                font-weight: bold;
                margin-top: 0.5rem;
            }
            .interpretation-guide {
                padding: 1.5rem;
                border-radius: 8px;
                background-color: #2d2d2d;
                margin-top: 1.5rem;
            }
            .interpretation-guide h3 {
                color: #ffffff;
                margin-bottom: 1rem;
            }
            .interpretation-guide ul {
                color: #d0d0d0;
                padding-left: 1.5rem;
            }
            @media (max-width: 768px) {
                .metric-box {
                    flex-direction: column;
                }
                .metric {
                    margin: 0.75rem 0;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("Credit Scoring System")
    st.markdown("Enter the applicant details to calculate credit score and default probability")

    with st.form("credit_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Personal Information")
            age = st.number_input("Age", min_value=18, max_value=100, value=28, step=1)
            income = st.number_input("Annual Income (₹)", min_value=0, value=1200000, step=10000)
            residence_type = st.selectbox("Residence Type", ["Owned", "Rented"], index=0)
            
        with col2:
            st.subheader("Loan Information")
            loan_amount = st.number_input("Loan Amount (₹)", min_value=0, value=2560000, step=10000)
            loan_tenure_months = st.number_input("Loan Tenure (Months)", min_value=1, value=36, step=1)
            loan_purpose = st.selectbox("Loan Purpose", ["Education", "Home", "Personal"], index=0)
            loan_type = st.selectbox("Loan Type", ["Unsecured", "Secured"], index=0)
        
        st.subheader("Credit History")
        col3, col4 = st.columns(2)
        
        with col3:
            avg_dpd_per_delinquency = st.number_input("Average Days Past Due per Delinquency", min_value=0, value=20, step=1)
            delinquency_ratio = st.number_input("Delinquency Ratio (%)", min_value=0, max_value=100, value=30, step=1)
            
        with col4:
            credit_utilization_ratio = st.number_input("Credit Utilization Ratio (%)", min_value=0, max_value=100, value=30, step=1)
            num_open_accounts = st.number_input("Number of Open Accounts", min_value=0, value=2, step=1)
        
        submitted = st.form_submit_button("Calculate Credit Score", use_container_width=True)

    if submitted:
        try:
            # Calculate loan to income ratio
            loan_to_income_ratio = loan_amount / income if income > 0 else 0
            
            # Call predict function
            probability, credit_score, rating = predict(
                age, income, loan_amount, loan_tenure_months, 
                avg_dpd_per_delinquency, delinquency_ratio,
                credit_utilization_ratio, num_open_accounts,
                residence_type, loan_purpose, loan_type
            )
            
            # Display results
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.subheader("Results")
            
            # Rating color mapping
            rating_colors = {
                'Poor': '#ff4b4b',
                'Average': '#ffa700',
                'Good': '#00b0f0',
                'Excellent': '#00d154'
            }
            
            # Create metrics
            st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class='metric'>
                    <div class='metric-label'>CREDIT SCORE</div>
                    <div class='metric-value' style='color: {rating_colors.get(rating, 'white')};'>{credit_score}</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class='metric'>
                    <div class='metric-label'>RATING</div>
                    <div class='metric-value' style='color: {rating_colors.get(rating, 'white')};'>{rating}</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class='metric'>
                    <div class='metric-label'>DEFAULT PROBABILITY</div>
                    <div class='metric-value' style='color: #ff4b4b;'>{probability:.2%}</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class='metric'>
                    <div class='metric-label'>LOAN-TO-INCOME RATIO</div>
                    <div class='metric-value'>{loan_to_income_ratio:.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Interpretation Guide
            st.markdown("""
            <div class='interpretation-guide'>
                <h3>Interpretation Guide</h3>
                <ul>
                    <li><strong>Credit Score Range</strong>: 300-900</li>
                    <li><strong>Default Probability</strong>: The predicted likelihood the applicant will default on the loan</li>
                    <li><strong>Loan-to-Income Ratio</strong>: Loan amount divided by annual income (lower is better)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()