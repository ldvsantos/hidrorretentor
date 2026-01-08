import pandas as pd
import os

def read_excel_safe(path):
    print(f"--- Reading {os.path.basename(path)} ---")
    try:
        xl = pd.ExcelFile(path)
        print(f"Sheets: {xl.sheet_names}")
        for sheet in xl.sheet_names:
            print(f"\nSheet: {sheet}")
            df = xl.parse(sheet)
            print(df.head(10).to_string())
    except Exception as e:
        print(f"Error reading {path}: {e}")

base_path = r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2 - HIDRORRETENTOR\2 - DADOS"
file3 = os.path.join(base_path, "1 - TESTE FITOTOXIDADE", "Cronograma degradação.xlsx")

read_excel_safe(file3)
