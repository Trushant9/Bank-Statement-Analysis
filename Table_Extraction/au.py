import pandas as pd
import numpy as np
import pdfplumber

# This function returns a Dataframe after extracting tables from a pdf file.
# You need to provide the file and password (if required) as input.
def extract_table_au_bank(file,password=None):
  pdf = pdfplumber.open(file)
  table_extraction_list_au = []
  
  for page in pdf.pages:
    # A try-except block is used to handle any errors during table extraction.
    try:
      table_form = page.extract_table()  # Each page’s table is extracted using the extract_table() function.
      table_extraction_list_au.extend(table_form)
    except:
      pass  # pass is used to ignore errors silently.
  
  df = pd.DataFrame(table_extraction_list_au)
  return df

# This function processes the data to create a clean and readable DataFrame for analysis.
def table_processing_au_bank(df):
  df = df[[0,1,4,5,6]]  # Selecting only the required columns.
  df.columns = ['Date','Narration','Debit','Credit','Balance']
   
  df = df.loc[df[df['Date']=='Date'].index[0]+1:]  # Find the index after the header row where actual data starts.
  df = df[df['Date']!='Date'].reset_index(drop=True)   # Remove any remaining rows where the 'Date' column still contains the word 'Date'.
  
  df[['Debit','Credit','Balance']] = df[['Debit','Credit','Balance']].replace('-',np.nan) # replace the '-' with nan values for changing their data types

  df['Date'] = pd.to_datetime(df['Date'],format="%d %b %Y")
  df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce")
  df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce")
  df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce")

  return df

# This function returns the final DataFrame after extracting, processing, and cleaning the table.
# You need to provide the file and password (if required), and the function will handle the rest.
def extract_au_bank_table(file, password=None):
    df = extract_table_au_bank(file,password=password)
    df = table_processing_au_bank(df)
    
    return df

