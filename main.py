import pandas as pd
import numpy as np

# Import custom modules for IFSC extraction and bank name detection
from detect_bank import extract_ifsc, get_bank_name

# Import bank-specific table extraction modules
from Table_Extraction.au import extract_au_bank_table
from Table_Extraction.axis import extract_ax_table
from Table_Extraction.bom import extract_bom_table
from Table_Extraction.canara import extract_can_table
from Table_Extraction.hdfc import extract_hdfc_table

# Import error checking and category classification
from check_err import check_error
from category_prediction import get_payment_category

# Import analysis functions
from Analysis.Summary_of_acc import gen_analysis
from Analysis.emi_salary_analysis import emi_analysis, salary_analysis
from Analysis.daily_balances_analysis import daily_balance
import streamlit as st
import os

# Function to Extract Table Based on Bank
def extract_table(file, bank_name):
    # Choose the appropriate function to extract table based on the bank name
    if bank_name == "Axis Bank":
        df = extract_ax_table(file)
    elif bank_name == "AU Small Finance Bank":
        df = extract_au_bank_table(file)
    elif bank_name == "Bank of Maharashtra":
        df = extract_bom_table(file)
    elif bank_name == "Canara Bank":
        df = extract_can_table(file)
    else:
        df = extract_hdfc_table(file)

    # If extraction is successful and not empty, verify table structure
    if not df.empty:
        response = check_error(df)  # Checks for common format errors
        if response['Status'] == "Proper Extraction":  
            return df
        else:
            return "Wrong Table Extraction"   # Return error message if structure is wrong

# Streamlit App UI Begins
st.title("Bank Statement PDF Analyzer")   # App title

# Initialize session state
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "df_result" not in st.session_state:
    st.session_state.df_result = None

# File uploader
uploaded_file = st.file_uploader("Upload your bank statement (PDF)", type=["pdf"])  # Only accepts PDFs

# Submit button
if st.button("Submit") and uploaded_file is not None:
    with st.spinner("Processing..."):   # Show a loading spinner while processing
        if uploaded_file is None:
            st.error("Please upload a file")
        try:
            # Save PDF
            temp_path = os.path.join("Uploaded_file", "temp.pdf")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            # Step 1: Extract IFSC from PDF and detect bank and show details to user
            ifsc = extract_ifsc(temp_path)
            bank_name = get_bank_name(ifsc)
            st.write(f"Bank Name: {bank_name}")
            st.write(f"Detected IFSC Code: {ifsc}")

            # Step 2: Extract transaction table
            df_extracted = extract_table(temp_path, bank_name)

            # Step 3: Predict and label transaction categories
            df_result = get_payment_category(df_extracted)

            # Step 4: Filter and rename necessary columns
            df_result = df_result[['Date', 'Narration', 'Result', 'Credit', 'Debit', 'Balance']]
            df_result = df_result.rename(columns={'Result': "Payment Mode"})

            # Store results in session state
            st.session_state.df_result = df_result
            st.session_state.submitted = True

            # Show extracted data
            st.success("Processing complete. Here's the categorized data:")
            st.dataframe(df_result)

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
            st.session_state.submitted = False

# User-Selectable Analysis
if st.session_state.submitted and st.session_state.df_result is not None:
    try:
        # Dropdown to select type of analysis
        analysis_type = st.selectbox(
            "What type of analysis would you like to see?",
            ("Summary of Account", "EMI", "Salary", "Daily Balances")
        )

        # Based on user selection, run and display appropriate analysis
        if analysis_type == "Summary of Account":
            st.subheader("Here is Summary of Account")
            result = gen_analysis(st.session_state.df_result)
            st.dataframe(result)
        elif analysis_type == "EMI":
            st.subheader("Here are EMI Transactions")
            result = emi_analysis(st.session_state.df_result)
            st.dataframe(result)
        elif analysis_type == "Salary":
            st.subheader("Here are Monthly Salary Transactions")
            result = salary_analysis(st.session_state.df_result)
            st.dataframe(result)
        elif analysis_type == "Daily Balances":
            st.subheader("Here is Closing Balances Transactions")
            result = daily_balance(st.session_state.df_result)
            st.dataframe(result)

    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")

                