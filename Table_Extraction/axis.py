import pdfplumber 
import pandas as pd
import numpy as np

# This function returns a Dataframe after extracting tables from a pdf file.
# You need to provide the file and password (if required) as input.
def table_extraction_axis_bank(file,password=None):
  pdf = pdfplumber.open(file)
  extraction_table_list_ax = []

  for page in pdf.pages:
    # A try-except block is used to handle any errors during table extraction.
    try:
      table_form = page.extract_table()   # Each page’s table is extracted using the extract_table() function.
      extraction_table_list_ax.extend(table_form)
    except:
      pass  # pass is used to ignore errors silently.

  df = pd.DataFrame(extraction_table_list_ax)
  return df

# This function processes the data to create a clean and readable DataFrame for analysis.
def table_processing_ax_bank(df):
  df = df[[0,2,3,4,5]]  # Selecting only the required columns.
  df.columns = ['Date','Narration','Debit','Credit','Balance']

  df = df.loc[df[df['Narration'].str.contains('OPENING BALANCE')].index[0]+1:]   # Find the index after the header row where actual data starts.
  df['Date'] = pd.to_datetime(df['Date'],format = "%d-%m-%Y", errors = 'coerce')
  df = df.dropna(subset=['Date']).reset_index(drop=True)  # Remove rows where 'Date' is NaT and reset the index.

  # Convert 'Debit', 'Credit', and 'Balance' columns to numeric types, forcing invalid values to NaN
  df['Debit'] = pd.to_numeric(df['Debit'],errors='coerce')
  df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce")
  df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce")

  return df

# This function returns the final DataFrame after extracting, processing, and cleaning the table.
# You need to provide the file and password (if required), and the function will handle the rest.
def extract_ax_table(file,password=None):
    df = table_extraction_axis_bank(file,password=password)
    df = table_processing_ax_bank(df)
    
    return df
  