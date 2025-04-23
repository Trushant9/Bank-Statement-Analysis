# Bank-Statement-Analysis

## Description
Developed a Bank Statement Analyzer using Python to extract, clean and analyze transaction data from pdf files of bank statements.

## Features
- Extracts text and transaction tables from bank statement PDFs  
- Categorizes transactions based on payment mode using narration details  
- Provides insightful and easy-to-understand analysis  
- Helps assess a user’s capability to get a personal loan based on various factors  

---

## Technologies Used
- **Python**  
- **Libraries**: `pandas`, `numpy`, `pdfplumber`  
- **Machine Learning** (used for categorization and prediction logic, if applicable)

---

## Folder Structure
- **Table Extraction**:  
  Contains scripts that process bank PDFs and extract relevant tables based on the bank name.
  
- **Analysis**:  
  Includes scripts that generate analysis reports such as EMI summary, salary credits, account summary, and daily balance trend after categorizing the data.

---

## How It Works

**What it does:**  
This project analyzes PDF bank statements to evaluate if a user qualifies for a personal loan. It is useful for both financial institutions and individual users.

**How it works:**
1. Upload or drag & drop your bank statement PDF into the system.  
2. Based on the bank name, the system uses a custom extraction script to retrieve the transaction table using `pdfplumber`.  
3. It checks for any calculation mismatches or inconsistencies.  
4. Then, it categorizes transactions by payment mode using narration descriptions.  
5. The user is prompted to select the type of analysis they want to view:  
   - Summary of Account  
   - EMI Detection  
   - Salary Credits  
   - Daily Balance Overview  
6. After reviewing the analysis tables, users or bank staff can decide whether the account shows eligibility for a personal loan.
   
---

## Note:

- **Supported Banks** (currently):
  - HDFC Bank
  - AU Small Finance Bank
  - Canara Bank
  - Bank of Maharashtra
  - Axis Bank

- **To Run the App**:
  Open your VS Code terminal and run:
  ```cmd
  streamlit run main.py

---

## Why I Built This
I created this project to simplify the loan eligibility process.  
It empowers not only **bank employees** but also **individual users** to easily check if someone qualifies for a personal loan based on real-time data extracted and analyzed from their bank statements.

---

## Author
**Trushant Jagdish**
