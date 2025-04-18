import pandas as pd
import numpy as np
from datetime import datetime 

# This function performs monthly financial transaction analysis from a bank statement-like dataset (temp_df). 
# It calculates various summary statistics for each month, such as total credits, debits, net credits/debits, 
# cash movements, EMI payments, and cheque bounces.
def gen_analysis(temp_df):
  # Add Month, Year, and Monthly_year columns for grouping
  temp_df['Month'] = temp_df['Date'].dt.month_name()
  temp_df['Year'] = temp_df['Date'].dt.year
  temp_df['Monthly_year'] = temp_df['Month'] + '-' + temp_df['Year'].astype(str)

  # Initialize empty lists for metrics
  group1 = []
  no_of_credit = []
  amount_credit = []
  no_of_debit = []
  amount_debit = []
  no_of_net_credit = []
  amount_net_credit = []
  no_of_net_debit = []
  net_debit_amount = []
  no_of_cash = []
  cash_amount = []
  no_atm_cash = []
  atm_cash_a = []
  cash_depo = []
  cash_depo_a = []
  payment_b_c = []
  payment_b_c_a = []
  tech_cheque_b = []
  tech_cheque_b_a = []
  non_tech_b = []
  non_tech_a = []
  no_of_EMI = []
  EMI_amount = []

  # Group by month-year and calculate metrics
  for group,data in temp_df.groupby('Monthly_year'):
    group1.append(group)
    no_of_credit.append(data['Credit'].count())
    amount_credit.append(data['Credit'].sum())
    no_of_debit.append(data['Debit'].count())
    amount_debit.append(data['Debit'].sum())

    # Exclude "Loan Disbursal" and "Interest Received" for net credit/debit
    no_of_net_credit.append(data[~data['Payment Mode'].isin(['Loan Disbursal','Interest Received'])]['Credit'].count())
    amount_net_credit.append(data[~data['Payment Mode'].isin(['Loan Disbursal','Interest Received'])]['Credit'].sum())
    no_of_net_debit.append(data[~data['Payment Mode'].isin(['Loan Disbursal','Interest Received'])]['Debit'].count())
    net_debit_amount.append(data[~data['Payment Mode'].isin(['Loan Disbursal','Interest Received'])]['Debit'].sum())

    # Cash withdrawal (Fund Transfer out)
    no_of_cash.append(data[data['Payment Mode'].isin(['Fund Transfer out'])]['Debit'].count())
    cash_amount.append(data[data['Payment Mode'].isin(['Fund Transfer out'])]['Debit'].sum())

    # ATM withdrawal (Card Settlement)
    no_atm_cash.append(data[data['Payment Mode'].isin(['Card Settlement'])]['Debit'].count())
    atm_cash_a.append(data[data['Payment Mode'].isin(['Card Settlement'])]['Debit'].sum())

    # Cash deposits (Fund Transfer in)
    cash_depo.append(data[data['Payment Mode'].isin(['Fund Transfer in'])]['Credit'].count())
    cash_depo_a.append(data[data['Payment Mode'].isin(['Fund Transfer in'])]['Credit'].sum())

    # Bounce payment charges
    payment_b_c.append(data[data['Payment Mode'].isin(['Bounce Payment Charges'])]['Debit'].count())
    payment_b_c_a.append(data[data['Payment Mode'].isin(['Bounce Payment Charges'])]['Debit'].sum())

    # Technical cheque bounce = Bounce Payment Charges + narration ending with 'GST'
    tech_cheque_b.append(data[(data['Payment Mode'].isin(['Bounce Payment Charges']))  & (data['Narration'].apply(lambda x : x.endswith('GST')))]['Debit'].count())
    tech_cheque_b_a.append(data[(data['Payment Mode'].isin(['Bounce Payment Charges']))  & (data['Narration'].apply(lambda x : x.endswith('GST')))]['Debit'].sum())

    # Non-technical cheque bounce = narration ending with 'GST' but not 'Bounce Payment Charges'
    non_tech_b.append(data[~(data['Payment Mode'].isin(['Bounce Payment Charges']))  & (data['Narration'].apply(lambda x : x.endswith('GST')))]['Debit'].count())
    non_tech_a.append(data[~(data['Payment Mode'].isin(['Bounce Payment Charges']))  & (data['Narration'].apply(lambda x : x.endswith('GST')))]['Debit'].sum())

    # EMI payments
    no_of_EMI.append(data[data['Payment Mode'].isin(['EMI'])]['Debit'].count())
    EMI_amount.append(data[data['Payment Mode'].isin(['EMI'])]['Debit'].sum())

  # Create a DataFrame for the analysis
  Analysis = pd.DataFrame({
    'Month':group1,
    'Total No. of Credit Transactions':no_of_credit,
    'Total of Credit Transactions Amount':amount_credit,
    'Total No. of Debit Transactions': no_of_debit,
    'Total of Debit Transactions Amount':amount_debit,
    'Total No. of Net Credit Transactions':no_of_net_credit,
    'Total of Net Credit Transactions Amount':amount_net_credit,
    'Total No. of Net Debit Transactions':no_of_net_debit,
    'Total of Net Debit Transactions Amount':net_debit_amount,
    'Total No. of Cash Withdrawals':no_of_cash,
    'Total of Cash Withdrawals Amount':cash_amount,
    'Total No. of ATM Cash Withdrawals':no_atm_cash,
    'Total of ATM Cash Withdrawals Amount':atm_cash_a,
    'Total No. of Cash Deposits':cash_depo,
    'Total of Cash Deposits Amount':cash_depo_a,
    'Total No. of Payment Bounce Charges':payment_b_c,
    'Total of Payment Bounce Charges Amount':payment_b_c_a,
    'Total No. of Technical Cheque Bounce':tech_cheque_b,
    'Total of Techical Cheque Bounce Amount':tech_cheque_b_a,
    'Total No. of Non Technical Cheque Bounce':non_tech_b,
    'Total of Non Technical Cheque Bounce Amount':non_tech_a,
    'Total No. of EMI Transactions':no_of_EMI,
    'Total of EMI Transactions Amount':EMI_amount
})

  Analysis.set_index('Month',inplace=True)  # Set month as index
  Analysis = Analysis.T   # Transpose to show months as columns
  sorted_month_year = sorted(group1, key=lambda x: datetime.strptime(x, "%B-%Y"))  # Sort columns chronologically
  Analysis = Analysis[sorted_month_year]
  Analysis['Grand_Total'] = Analysis.sum(axis=1)  # Add total column
  return Analysis