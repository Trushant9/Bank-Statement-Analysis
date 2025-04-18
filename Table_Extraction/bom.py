import pdfplumber
import pandas as pd
import numpy as np

# This function returns a Dataframe after extracting tables from a pdf file.
# You need to provide the file and password (if required) as input.
def extract_table_bom_bank(file,password=None):
  pdf = pdfplumber.open(file)
  extraction_table_list_bom = []

  for page in pdf.pages:
    # A try-except block is used to handle any errors during table extraction.
    try:
      table_form = page.extract_table()  # Each page’s table is extracted using the extract_table() function.
      extraction_table_list_bom.extend(table_form)
    except:
      pass   # pass is used to ignore errors silently.

  df = pd.DataFrame(extraction_table_list_bom)
  return df

# This functions returns the dataframe after changing data types of 'Debit','Credit','Balance' Columns, forcing invalid values to NaN
def convert_numeric(df):
    df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce")
    df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce")
    df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce")
    return df

# This function processes the data to create a clean and readable DataFrame for analysis.
def table_processing_bom_bank(df):
  df = df[[1,2,4,5,6]]  # Selecting only the required columns.
  df.columns = ['Date','Narration','Debit','Credit','Balance']

  df = df.loc[df[df['Date'] == 'Date'].index[0]+1:]   # Find the index after the header row where actual data starts.
  df['Date'] = pd.to_datetime(df['Date'],format="%d/%m/%Y", errors = 'coerce')
  df = df.dropna(subset=['Date']).reset_index(drop=True)  # Remove rows where 'Date' is NaT and reset the index.

  # Remove commas from 'Balance', 'Debit', and 'Credit' columns to prepare for numeric conversion
  df['Balance'] = df['Balance'].apply(lambda x: str(x).replace(',',''))
  df['Debit'] = df['Debit'].apply(lambda x: str(x).replace(',',''))
  df['Credit'] = df['Credit'].apply(lambda x: str(x).replace(',',''))

  df = convert_numeric(df)  
  return df

# This function returns the final DataFrame after extracting, processing, and cleaning the table.
# You need to provide the file and password (if required), and the function will handle the rest.
def extract_bom_table(file, password=None):
    df = extract_table_bom_bank(file,password=password)
    df = table_processing_bom_bank(df)
    
    return df