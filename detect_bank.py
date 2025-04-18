import requests
import pdfplumber
import re

# This function calls Razorpay's IFSC API to fetch bank details.
def get_bank_details(ifsc_code):
    url = f"https://ifsc.razorpay.com/{ifsc_code}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Invalid IFSC Code or API Error: {response.status_code}"

# This regular expression pattern matches IFSC codes.
ifsc_pattern = r'[a-z]{4}\d{7}' 

# This function extracts the bank name using the IFSC code.
def extract_ifsc(file):
    pdf = pdfplumber.open(file)
    text = pdf.pages[0].extract_text()
    match = re.search(ifsc_pattern, text.lower())

    if match:
        ifsc = match.group()
    else:
        ifsc = None

    return ifsc

# This functions return the name of bank after calling get_bank_details function
def get_bank_name(ifsc):
    bank_details = get_bank_details(ifsc)

    bank = bank_details['BANK']

    return bank
