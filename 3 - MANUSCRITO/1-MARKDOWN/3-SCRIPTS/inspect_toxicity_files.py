import pandas as pd
import os

root_dados = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE"
files = [
    "CONTAGEM RÚCULA BOD.xlsx",
    "Ensaio_fitotoxidade_1_(25112024).xlsx",
    "PESAGEM RAIZES^LJ FOLHAS E PLANTULAS 2.xlsx"
]

for f in files:
    path = os.path.join(root_dados, f)
    if os.path.exists(path):
        print(f"\n=== INSPECTING: {f} ===")
        try:
            xl = pd.ExcelFile(path)
            print("Sheets:", xl.sheet_names)
            for sheet in xl.sheet_names:
                df = pd.read_excel(path, sheet_name=sheet, nrows=5)
                print(f"--- Sheet: {sheet} ---")
                print(df.columns.tolist())
                print(df.head(2))
        except Exception as e:
            print(f"Error reading {f}: {e}")
    else:
        print(f"File not found: {f}")
