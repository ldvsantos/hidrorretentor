import pandas as pd
import os
import sys

def read_excel_safe(path):
    print(f"--- Reading {os.path.basename(path)} ---")
    try:
        # Load the spreadsheet to see sheet names
        xl = pd.ExcelFile(path)
        print(f"Sheets: {xl.sheet_names}")
        
        # Read first sheet/relevant sheets
        for sheet in xl.sheet_names:
            print(f"\nSheet: {sheet}")
            df = xl.parse(sheet)
            print(df.head(10).to_string())
            print(df.describe().to_string())
    except Exception as e:
        print(f"Error reading {path}: {e}")

base_path = r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2 - HIDRORRETENTOR\2 - DADOS"
file1 = os.path.join(base_path, "Avaliação substrato 1 incompleto-DIEGO.xlsx")
file2 = os.path.join(base_path, "PLANTULAS UMIDAS E SECAS PESAGEM GOURD FLOWER 21 E 22 FEVEREIRO .xlsx")

read_excel_safe(file1)
read_excel_safe(file2)
