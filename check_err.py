import pandas as pd
import numpy as np

# This function checks if the running balance is consistent throughout the statement.
def check_error(df):
  balance = None
  extraction_status = []

  pd.set_option('future.no_silent_downcasting', True)   # Enable future behavior for automatic type inference.

  df = df.fillna(0).infer_objects(copy=False)  # Replace NaN with 0 and infer object types

  for index,row in df.iterrows():
    if index==0:
      balance = row['Balance']  # Initialize balance with the first row's balance
    else:
      balance = round(balance-row['Debit']+row['Credit'],2)  # Update balance based on Debit and Credit values

      # Compare with actual balance
    if balance == row['Balance']:
      extraction_status.append(True)
    else:
      extraction_status.append(False)

# Return status based on whether any error was found
  if False in extraction_status:
    return {"Status": "Wrong Table Extraction",
                "Count of errors": extraction_status.count(False),
                "Error row" : extraction_status.index(False),
                "Table":df.replace(0,np.nan)}
  else:
      return {"Status": "Proper Extraction",
              "Count of errors": extraction_status.count(False),
              "Error row" : 0,
              "Table":df.replace(0,np.nan)}