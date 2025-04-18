import pandas as pd
import numpy as np
from datetime import datetime

# This functions return DataFrame after adding new columns
def add_coln(temp_df):
    temp_df['Month'] = temp_df['Date'].dt.month_name()  # Extract full month name from Date
    temp_df['Year'] = temp_df['Date'].dt.year  # Extract year from Date
    temp_df['Monthly_year'] = temp_df['Month'] + '-' + temp_df['Year'].astype(str)  # Combine month and year
    return temp_df

# This functions returns DataFrame after filtering data which only have 'EMI' Transactions.
def emi_analysis(temp_df):
    temp_df1 = add_coln(temp_df)  # Add necessary columns
    temp_df1 = temp_df[['Monthly_year','Date','Narration','Payment Mode','Credit','Debit','Balance']]  # Select only required columns for analysis
    temp_df1 = temp_df1[temp_df1['Payment Mode']=="EMI"]   # Filter rows where Payment Mode is EMI
    return temp_df1

# This functions returns DataFrame after filtering data which only have 'Salary' Transactions.
def salary_analysis(temp_df):
    temp_df2 = add_coln(temp_df)   # Add necessary columns
    temp_df2 = temp_df[['Monthly_year','Date','Narration','Payment Mode','Credit','Debit','Balance']]  # Select only required columns for analysis
    temp_df2 = temp_df2[temp_df2['Payment Mode']=='Salary']  # Filter rows where Payment Mode is Salary
    return temp_df2
