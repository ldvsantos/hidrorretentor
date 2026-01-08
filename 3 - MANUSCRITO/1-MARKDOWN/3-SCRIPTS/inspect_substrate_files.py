import pandas as pd
import os

files = [
    "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/Avaliação substrato 1 incompleto-DIEGO.xlsx",
    "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/Avaliação Plantulas b.o.d incompleto.xlsx",
    "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/Modelo para avaliação substrato.xlsx"
]

for f in files:
    if os.path.exists(f):
        print(f"\n=== {os.path.basename(f)} ===")
        try:
            xl = pd.ExcelFile(f)
            print("Sheets:", xl.sheet_names)
            for sheet in xl.sheet_names:
                df = pd.read_excel(f, sheet_name=sheet, nrows=5)
                print(f"--- Sheet: {sheet} ---")
                print(df.columns.tolist())
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Missing: {f}")
