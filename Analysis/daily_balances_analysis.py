import pandas as pd
import numpy as np
from datetime import datetime
from calendar import monthrange  # Used to get the number of days in a given month and year.
from Analysis.emi_salary_analysis import add_coln

#  Custom function to return number of days in a given "Month-Year" format (e.g., "April-2025").
def get_days_in_month(month_year: str) -> int:
    date_obj = datetime.strptime(month_year, "%B-%Y")
    days_in_month = monthrange(date_obj.year, date_obj.month)[1]
    return days_in_month

def daily_balance(temp_df):
    temp_df = add_coln(temp_df)  # Add required columns like 'Monthly_year' if not already present.
    temp_df['Day'] = temp_df['Date'].dt.day

    # Get the last available balance for each day of each month
    month_end = temp_df.groupby(['Monthly_year','Day'])['Balance'].last()
    month_end = month_end.unstack().unstack().unstack()   # Reshape to have months as columns and days as rows

    # Sort columns (month-year) chronologically
    sorted_month_year = sorted(month_end.columns, key=lambda x: datetime.strptime(x, "%B-%Y"))
    month_end = month_end[sorted_month_year]

    month_end = month_end.fillna(method='ffill')  # Forward fill missing balances within a month

    # Fill missing values of current month with last balance of previous month
    for month_idx in range(1,month_end.shape[1]):
        last_balance = month_end.iloc[-1,month_idx-1]
        month_end.iloc[:,month_idx] = month_end.iloc[:,month_idx].fillna(last_balance)

    initial_balance = None

    # If first entry is not the 1st day, calculate and fill initial balance before first transaction
    if not temp_df["Date"][0].day == 1:
        if  pd.isna(temp_df["Credit"][0]):
            initial_balance = temp_df["Balance"][0] + temp_df["Debit"][0]
        else:
            initial_balance = temp_df["Balance"][0] -temp_df["Credit"][0]
    month_end.iloc[:temp_df["Date"][0].day-1, 0] = initial_balance

    # Set values to NaN for days beyond the actual month length (like 31st in February)
    for i in month_end.columns:
        last_date = get_days_in_month(i)
        month_end.loc[last_date+1:,i] = np.nan
        
    return month_end
