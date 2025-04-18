import pdfplumber
import pandas as pd
import numpy as np
from Table_Extraction.bom import convert_numeric  # Reusing a common function to convert columns to numeric

def extract_table_canara_bank(file,password=None):
  pdf = pdfplumber.open(file)
  extraction_table_list_can = []

  for page in pdf.pages:
    # A try-except block is used to handle any errors during table extraction.
    try:
      # Table is extracted with custom settings using vertical and horizontal strategies.
      table_form = page.extract_table(table_settings={'vertical_strategy':'explicit',
                                                      'horizontal_strategy':'text',
                                                      'explicit_vertical_lines':[25,95,295,400,500,584]})
      extraction_table_list_can.extend(table_form)
    except:
      pass  # Ignores any extraction errors silently.

  df = pd.DataFrame(extraction_table_list_can)
  return df

# This function processes and merges narration entries split across rows. 
def complete_narration(df):
  df['Narration'] = df['Narration'].fillna("") # Fill missing narration with empty string because nan values data types is float.
  new_narrations = []
  narr = ""

  for index,row in df.iterrows():
    # Check if the row doesn't start with 'Chq:', then append narration text
    if not row['Narration'].startswith('Chq:'):
      narr += row['Narration']
    else:
      # if the row start with 'Chq:',still append narration text because i need complete text.
      narr +=" "+ row['Narration']
      new_narrations.append(narr)
      narr = ""  # Reset for the next narration

  return new_narrations

# This function processes the raw table to create a clean and readable DataFrame.
def table_processing_can_bank(df):
  df.columns = ['Date','Narration','Credit','Debit','Balance']  # Assign proper column names

  df = df.loc[df[df['Date'] == 'Date'].index[0]+1:] # Skip the header row and keep only the actual transaction rows

  df.replace('',np.nan,inplace=True)  # Replace empty strings with NaN
  df.dropna(axis=0,how='all')  # Drop rows where all values are NaN

  df=df[df['Date'] != 'Date'].reset_index(drop=True)  # Remove any leftover header rows

  df['Date'] = pd.to_datetime(df['Date'],format="%d-%m-%Y", errors = 'coerce') # Convert date

  # Merge narrations spread across multiple rows
  complete_narr = complete_narration(df)

  df=df.dropna(subset=['Date']).reset_index(drop=True)  # Drop rows with invalid dates
  df['Narration']=complete_narr  # Replace with clean narrations

  # Remove commas to prepare for numeric conversion
  df['Balance'] = df['Balance'].apply(lambda x: str(x).replace(',',''))
  df['Debit'] = df['Debit'].apply(lambda x: str(x).replace(',',''))
  df['Credit'] = df['Credit'].apply(lambda x: str(x).replace(',',''))

  df = convert_numeric(df)

  return df

# This function returns the final DataFrame after extracting, processing, and cleaning the table.
# You need to provide the file and password (if required), and the function will handle the rest.
def extract_can_table(file,password=None):
    df = extract_table_canara_bank(file,password=password)
    df = table_processing_can_bank(df)
    
    return df

