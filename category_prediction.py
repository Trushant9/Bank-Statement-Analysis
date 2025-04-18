import re
from transformers import pipeline
import pandas as pd
import numpy as np
import concurrent.futures
import logging
import time
import json
import  pickle
# from model import payment_transaction_classifier, party_name

payment_transaction_classifier = pipeline("sentiment-analysis", model=r"model\Classifier")

model_name = r"model\roberta-base-squad2"
party_name = pipeline('question-answering', model=model_name, tokenizer=model_name)

logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


with open("final tokens.json") as f:
    lst = json.load(f)

def counter_party_roberta(narration):
    QA_input = {
        'question': 'Company name to whom the fund transfer',
        'context': narration
    }
    res = party_name(QA_input)
    return res['answer'].split("Ref")[0]



def extract_company_name(row):
    if row["Result"] == "Salary":
        if (re.search(r'\bsalary', row["Narration"].lower()) or re.search(r'\bsalaries', row["Narration"].lower()) or re.search(r'\bsal\b', row["Narration"].lower().replace("_", " "), re.IGNORECASE)) and not re.search(r'arly\s?salary', row["Narration"].lower()):
            return "Salary"
        
        else:
            context = row["Narration"].lower().replace("rtgs", "").replace("neft" ,"").replace("the", "")
            # Mostly, Narrations contains bank names. So, model extract bank name as a Company name. So, replace bank name
            context = re.sub(r'/\w+\s*bank', "", context, re.IGNORECASE)
            result = party_name(question="Tell me the name of organization", context=context)
            result = re.sub(r"\d", "", result['answer'])
            result = result.replace("by transfer", "")
            result = "".join([i for i in result if i.isalpha() or i.isspace()])
            return result
        
    else:
      return ""


def map_to_base(company_names):
    base_names = {}
    for name in company_names:
        base = name
        for other_name in company_names:
            if name != other_name and other_name.startswith(name.split()[0]):
                base = name.split()[0]
                break
            elif other_name != name and name.startswith(other_name.split()[0]):
                base = other_name.split()[0]
                break
        base_names.update({name:base})

    return base_names


def replace_keys_with_values(text, replacement_dict):
    for key, value in replacement_dict.items():
        text = text.replace(key, value)
    return text

def process_narr(narr):
    narr = re.findall(r'\b(?!\w*\d+\w*\b)(\w+)\b', narr)
    narr = " ".join(narr)
    narr = re.sub(r"\d+", " ", narr)
    narr = re.sub(r"[^a-zA-Z ]", " ",narr)
    return narr


def filtered_tokens(txt):
    txt = txt.replace("@", " ").replace(".", " ").replace("to:", " ").replace("from:", " ")
    txt = re.sub(r"\d", " ", txt)
    txt = re.sub(r"\s+", " ", txt)
    if txt.count("-") >= 2:
        txt = txt.replace(" ", "-")
        tokens = txt.split("-")
    elif txt.count("/") >= 2:
        txt = txt.replace(" ", "/")
        tokens = txt.split("/")
    elif txt.count("\\") >= 2:
        txt = txt.replace(" ", "\\")
        tokens = txt.split("\\")
    else:
        txt = re.sub(r"[^A-Za-z\s]", " ", txt)
        tokens = txt.split()
    filtered_tokens = [token.strip() for token in tokens if re.fullmatch(r'[A-Za-z\s]+', token)]
    return filtered_tokens


def trim_name(tokens):
    token_to_keep = []
    a = 0
    b = 0
    length = 0
    for i in tokens:
        if i in lst:
            a += 1
        else:
            a = 0
            b += 1
            token_to_keep.append(i)
        if  a > 0  and (b >= 1 or length >= 5):
            break
    return " ".join(token_to_keep)


def remove_repeated_name(text):
    words = text.split()
    seen = set(words)
    result = []
    for i in words:
        if i not in result:
            if not any(j in i for j in result if len(j)>2):
                result.append(i)
    return " ".join(result)


def replace_tokens(txt, token_list):
    if "bank ltd" in txt:
        txt = txt.replace("bank ltd", "")
    token = filtered_tokens(txt)
    token = trim_name(token)
    name = remove_repeated_name(token)
    return name.title()

def extract_party_name(df, lst):
    mask = df['Result'].isin(["Fund Transfer To", "Fund Transfer From"])

    df.loc[mask, 'Result'] = df.loc[mask].apply(
        lambda row: row['Result'] + " " + replace_tokens(process_narr(row['Updated Narration']).lower(), lst),
        axis=1
    )

    return df


def transformation(df):

    for index, row in df.iterrows():        
        text = row["Narration"].lower()

        text = re.sub(r'\bpriv\b', 'pvt ltd', text)
        text = re.sub(r'private limited', 'pvt ltd', text)
        text = re.sub(r'chq:\s*\d+', '', text)
        
        d = {"salary now":"now", "health insurance":"health", "finsales":"", "financiers ltd":"ltd", "bajaj finance":"bajaj", "life insurance":"life", "airtel payment":"payment", "small finanace":"small", "finance bank":"bank", "bajajpay":"", "finance ltd":"ltd", "by clg":"by", "atdfinancial":"atfinancial"}
        text = replace_keys_with_values(text, d)

        if row["Credit"] == 1.0 and "imps" in text:
            text = text + "imps rs. 1"
            df.at[index, "Updated Narration"] = text

        elif pd.notna(row["Credit"]):
            if not any(keyword.lower() in text for keyword in ["neft", "imps", "upi", "cms", "ift", "chrg", "JAIPUR", "ach"]) and len(text) < 40:
                text = "NEFT " + text
            text = text + "@credit"
            df.at[index, "Updated Narration"] = text

        elif pd.notna(row["Debit"]):
            text = text + "@debit"
            df.at[index, "Updated Narration"] = text
    
    return df

def return_payment_mode(narr):
    if len(narr) > 200:
        narr = narr[:200]
    cat = payment_transaction_classifier(narr)[0]['label']
    return cat

def apply_parallel(df, func, workers=4):
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(func, df['Updated Narration']))
    return results

def extract_company_name_parallel(df, func, workers=4):
    # Create a ThreadPoolExecutor to process rows in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(func, [row for _, row in df.iterrows()]))
    return results

def prediction(df):
    try:
        df['Result'] = apply_parallel(df, return_payment_mode)

        df.loc[(df["Narration"].str.lower().str.contains("imps")) & (df["Credit"] == 1), "Result"] = "IMPS@1"

        df['PrevBalance'] = df['Balance'].shift(1)
        df.loc[(df["Result"] == "EMI-Reversal") & (df['PrevBalance'] >= df["Debit"]) & (pd.isna(df["Credit"])), "Result"] = "EMI"
        df.loc[(df["Result"] == "EMI") & (df['PrevBalance'] < df["Debit"]) & (pd.isna(df["Credit"])), "Result"] = "EMI-Reversal"

        df['PreCategory'] = df['Result'].shift(1)
        df.loc[(df["Result"] == "Loan Disbursal") & (df["PreCategory"] == "EMI-Reversal") & (pd.isna(df["Debit"])), "Result"] = "EMI Payment Bounce"

        df.loc[(df["Result"] == "Cheque Inward Bounce"), "Result"] = "a"
        df.loc[(df["Result"] == "Cheque Outward Bounce"), "Result"] = "Cheque Inward Bounce"
        df.loc[(df["Result"] == "a"), "Result"] = "Cheque Outward Bounce"

        df.loc[(df["Result"] == "Cheque Inward"), "Result"] = "a"
        df.loc[(df["Result"] == "Cheque Outward"), "Result"] = "Cheque Inward"
        df.loc[(df["Result"] == "a"), "Result"] = "Cheque Outward"
    
        return df
    
    except Exception as e:
        print("Final : ", e)


def get_payment_category(df):
    t1 = time.time()
    df_trans = transformation(df)
    df = prediction(df_trans)
    t2 = time.time()

    df["Company Name"] = extract_company_name_parallel(df, extract_company_name, workers=8)
    df["Company Name"] = df["Company Name"].fillna("")
    companies = df["Company Name"].unique().tolist()

    sal_frm_comp = {}
    for index, row in df.iterrows():
        if row["Result"] == "Salary":
            max_sal = df[df["Company Name"] == row["Company Name"]]["Credit"].max()
            sal_frm_comp.update({row["Company Name"] : max_sal})

    for comp in sal_frm_comp:
        if not sal_frm_comp[comp] > 15000:
            df.loc[df[df["Company Name"] == comp].index, "Result"]  = "Fund Transfer From"
            df["Company Name"].replace({comp:""}, inplace=True)

    companies.remove("")
    companies = [i for i in companies if not i.isspace()]
    base_names = map_to_base(companies)
    df["Company Name"] = df["Company Name"].replace(base_names)

    unique_companies = df["Company Name"].value_counts().to_dict()

    if "" in unique_companies.keys():
        del unique_companies[""]

    if unique_companies:
        comp_name = list(unique_companies.keys())[0]
        
    if "Salary" in unique_companies.keys():
        df.loc[(df["Company Name"] == "Salary") & (df["Result"] == "Salary"), "Result"] = "Salary"
        df.loc[(~df["Company Name"].isin(["", "Salary"])) & (df["Result"] == "Salary"), "Result"] = "Fund Transfer From"

    elif len(unique_companies) == 1:

        if df[df["Company Name"] == comp_name].shape[0] == 1:
            if df[df["Company Name"] == comp_name]["Credit"].iloc[0] < 20000:
                df.loc[df[df["Company Name"] == comp_name].index[0], "Result"] = "Fund Transfer From"
    
    elif len(unique_companies) >= 2:
        comp = max(unique_companies, key=lambda k: unique_companies[k])

        for index, row in df.iterrows():
            if row['Company Name'] not in [comp, ""]:
                df.at[index, 'Result'] = 'Fund Transfer From'

            if "tradofin" in row["Narration"].lower() and pd.isna(row["Debit"]):
                df.at[index, "Result"] = "Loan Disbursal"

            if "tradofin" in row["Narration"].lower() and pd.isna(row["Credit"]):
                df.at[index, "Result"] = "EMI"


    if not np.any(df[df["Result"] == "Salary"]["Credit"] > 15000):
        df.loc[df["Result"] == "Salary", "Result"] = "Fund Transfer From"

  
    for index, row in df.iterrows():
        text = row["Narration"]

        if row["Credit"] <= 10.0 and row["Result"] == "Loan Disbursal":
            df.at[index, "Result"] = "Fund Transfer From"

        if row["Debit"] <= 10.0 and row["Result"] == "EMI":
            df.at[index, "Result"] = "Fund Transfer To"


        if row["Result"] == "Fund Transfer To" and "cashfree" in text.lower():
            df.at[index, "Result"] = "EMI"

        if 'penal charges' in text.lower():
            df.at[index, "Result"] = "Penal Charges"

    fund_transfers = df[df["Result"].str.contains("fund transfer")].shape[0]

    t3 = time.time()
    df = extract_party_name(df, lst)
    t4 = time.time()


    return df

