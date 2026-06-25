import json
import os

import boto3
import streamlit as st
from botocore.exceptions import ClientError, NoCredentialsError


ENDPOINT_NAME = os.environ.get("ENDPOINT_NAME", "credit-score-endpoint")
REGION = os.environ.get("AWS_REGION", "us-east-1")


@st.cache_resource
def get_runtime_client():
    return boto3.client("sagemaker-runtime", region_name=REGION)


def invoke_endpoint(features: list) -> dict:
    runtime = get_runtime_client()
    payload = {"instances": [features]}
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Accept="application/json",
        Body=json.dumps(payload),
    )
    return json.loads(response["Body"].read().decode("utf-8"))


def main():
    st.set_page_config(page_title="Credit Score Predictor", layout="wide")
    st.title("Credit Score Prediction")
    st.write("Stevanus Gerald Marconus — 2802392500")

    with st.sidebar:
        st.header("Input Guide")
        st.write("Isi data nasabah di form, lalu klik **Predict** untuk melihat hasil prediksi Credit Score.")
        st.info("Model akan memprediksi apakah Credit Score nasabah termasuk **Good**, **Standard**, atau **Poor**.")

    st.subheader("Data Nasabah")

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Informasi Pribadi**")
            age = st.number_input("Age", min_value=18, max_value=100, step=1, value=30)
            occupation = st.selectbox("Occupation", [
                "Unknown", "Accountant", "Architect", "Developer", "Doctor",
                "Engineer", "Entrepreneur", "Journalist", "Lawyer",
                "Manager", "Media_Manager", "Mechanic", "Musician",
                "Scientist", "Teacher", "Writer"
            ])
            annual_income = st.number_input("Annual Income", min_value=0.0, step=100.0, value=50000.0)
            monthly_inhand_salary  = st.number_input("Monthly Inhand Salary", min_value=0.0, step=100.0, value=4000.0)
            num_bank_accounts = st.number_input("Num Bank Accounts", min_value=0, max_value=20, step=1, value=3)
            num_credit_card = st.number_input("Num Credit Card", min_value=0, max_value=20, step=1, value=2)
            interest_rate = st.number_input("Interest Rate (%)", min_value=0, max_value=50, step=1, value=10)
            num_of_loan = st.number_input("Num of Loan", min_value=0, max_value=20, step=1, value=2)

        with col2:
            st.markdown("**Riwayat Kredit**")
            delay_from_due_date = st.number_input("Delay from Due Date (days)", min_value=0, max_value=100, step=1, value=5)
            num_delayed_payment = st.number_input("Num of Delayed Payment", min_value=0, max_value=50, step=1, value=3)
            changed_credit_limit = st.number_input("Changed Credit Limit", min_value=0.0, step=0.1, value=5.0)
            num_credit_inquiries = st.number_input("Num Credit Inquiries", min_value=0, max_value=30, step=1, value=3)
            credit_mix = st.selectbox("Credit Mix", ["Standard", "Good", "Bad"])
            outstanding_debt = st.number_input("Outstanding Debt", min_value=0.0, step=10.0, value=500.0)
            credit_utilization_ratio = st.number_input("Credit Utilization Ratio (%)", min_value=0.0, max_value=100.0, step=0.1, value=25.0)
            payment_of_min_amount = st.selectbox("Payment of Min Amount", ["Yes", "No", "NM"])
            total_emi_per_month = st.number_input("Total EMI per Month", min_value=0.0, step=10.0, value=50.0)
            amount_invested_monthly  = st.number_input("Amount Invested Monthly", min_value=0.0, step=10.0, value=100.0)
            payment_behaviour = st.selectbox("Payment Behaviour", [
                "Low_spent_Small_value_payments",
                "Low_spent_Medium_value_payments",
                "Low_spent_Large_value_payments",
                "High_spent_Small_value_payments",
                "High_spent_Medium_value_payments",
                "High_spent_Large_value_payments",
            ])
            monthly_balance = st.number_input("Monthly Balance", min_value=0.0, step=10.0, value=300.0)

        submitted = st.form_submit_button("Predict", use_container_width=True)

    if submitted:
        features = [
            age, annual_income, monthly_inhand_salary,
            num_bank_accounts, num_credit_card, interest_rate,
            num_of_loan, delay_from_due_date, num_delayed_payment,
            changed_credit_limit, num_credit_inquiries, credit_mix,
            outstanding_debt, credit_utilization_ratio, payment_of_min_amount,
            total_emi_per_month, amount_invested_monthly, monthly_balance,
            payment_behaviour, occupation, credit_mix
        ]

        try:
            result = invoke_endpoint(features)
        except NoCredentialsError:
            st.error(
                "No AWS credentials found. "
                "If running on EC2, attach LabInstanceProfile. "
                "If running locally, configure ~/.aws/credentials."
            )
        except ClientError as e:
            st.error(f"AWS error: {e.response['Error'].get('Message', str(e))}")
        else:
            label = result["labels"][0]

            st.divider()
            st.subheader("Hasil Prediksi")

            if label == "Good":
                st.success("Credit Score: **Good**")
                st.write("Nasabah memiliki riwayat kredit yang baik dan dianggap layak untuk mendapatkan kredit dengan bunga rendah.")
            elif label == "Standard":
                st.warning("Credit Score: **Standard**")
                st.write("Nasabah memiliki riwayat kredit yang cukup. Perlu evaluasi lebih lanjut sebelum pemberian kredit.")
            else:
                st.error("Credit Score: **Poor**")
                st.write("Nasabah memiliki riwayat kredit yang buruk. Berisiko tinggi untuk pemberian kredit.")


if __name__ == "__main__":
    main()