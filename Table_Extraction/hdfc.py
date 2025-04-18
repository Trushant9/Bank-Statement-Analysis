import pdfplumber
import pandas as pd
import numpy as np
import re

# This function extracts raw table data from the HDFC Bank PDF and return a clean and readable Dataframe.
def extract_table_hdfc_bank(file,password=None):
  pdf = pdfplumber.open(file)
  extraction_table_list = []

  for page in pdf.pages:
    try:
      # Extracting the table using explicit vertical lines customized for HDFC format
      extraction = page.extract_table(table_settings={'vertical_strategy':'explicit',
                                                      'horizontal_strategy':'text',
                                                      'explicit_vertical_lines':[30,68,270,355,395,475,552,628]})
      extraction_table_list.extend(extraction)
    except:
      pass  # Silently skip any extraction errors

  df = pd.DataFrame(extraction_table_list)
  return df

# This function removes commas from numeric values for conversion.
def extract_amount_value(x):
    x = str(x).replace(',', '')
    return x

# This function joins narration text spread across multiple rows.
def get_complete_narration(df):
  complete_narration = []
  narr = ""

  for index, row in df[:-1].iterrows():
        # If the next row has no date, narration continues
        if pd.isna(df.at[index+1, "Date"]):
            narr += row["Narration"]
        else:
            narr += f" {row['Narration']}"
            complete_narration.append(narr)
            narr = ""

  complete_narration.append(narr)  # Add last narration

  return complete_narration

# This function checks if a cell contains a valid date or is empty.
def is_date_or_missing_value(x):
  if re.match('\d{2}/\d{2}/\d{2}',str(x)) or pd.isna(x):
    return pd.to_datetime(x,format='%d/%m/%y')
  else:
    return False

# This function processes and cleans the extracted table data  
def table_processing_hdfc_bank(df):
  df = df[[0,1,4,5,6]]  # Keep only necessary columns based on position
  df.columns = ['Date','Narration','Debit','Credit','Balance']

  df = df.loc[df[df['Date']=='Date'].index[0]+1:]  # Skip the header rows and start with actual transaction data

  df = df.replace('',np.nan)
  df = df.dropna(axis=0,how='all').reset_index(drop=True)

  # Convert valid date strings to datetime, and filter out invalid ones
  df['Date'] = df['Date'].apply(is_date_or_missing_value)
  df = df[df['Date']!=False].reset_index(drop=True)

  df['Narration'] = df['Narration'].fillna("")  # Fill empty narration fields to handle merging because nan values data types is float.

  df = df.loc[:df[df['Narration'].str.contains("STATEMENTSUMMARY")].index[0]-1]  # Remove rows after "STATEMENTSUMMARY" since they're not transactions

  complete_narrations = get_complete_narration(df)  # Merge rows where narration was split.

  df = df.dropna(subset=["Date"]).reset_index(drop=True)  # Drop rows with invalid dates
  df['Date'] = pd.to_datetime(df['Date'],errors="coerce") # Convert 'Date' column data types for no further errors
  df['Narration'] = complete_narrations

  # Clean and convert amount columns
  df["Debit"] = df["Debit"].apply(extract_amount_value)
  df["Credit"] = df["Credit"].apply(extract_amount_value)
  df["Balance"] = df["Balance"].apply(extract_amount_value)

  df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce")
  df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce")
  df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce")
  return df

# This function gives the final cleaned transaction DataFrame for HDFC Bank.
def extract_hdfc_table(file,password=None):
    df = extract_table_hdfc_bank(file,password=None)
    df = table_processing_hdfc_bank(df)
    return df