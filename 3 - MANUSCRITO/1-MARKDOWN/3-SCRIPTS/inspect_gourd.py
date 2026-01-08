import pandas as pd
from pathlib import Path

root = Path(r"C:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2 - HIDRORRETENTOR\2 - DADOS")
file_path = root / "PLANTULAS UMIDAS E SECAS PESAGEM GOURD FLOWER 21 E 22 FEVEREIRO .xlsx"

if not file_path.exists():
    raise FileNotFoundError(file_path)

xls = pd.ExcelFile(file_path)
print("Sheets:", xls.sheet_names)
for name in xls.sheet_names:
    df = xls.parse(name)
    print("===", name, "===")
    print(df.head())
    print(df.describe(include='all'))
    if {"VARIAVEL", "ESTADO", "QUANT."}.issubset(df.columns):
        grouped = (
            df.groupby(["VARIAVEL", "ESTADO"], dropna=False)["QUANT."]
            .agg(["count", "mean", "std", "min", "max"])
            .reset_index()
        )
        print("Grouped QUANT. stats:\n", grouped)
    if "Dependencia" in df.columns:
        dep = df.dropna(subset=["Dependencia"])
        if not dep.empty:
            dep_grouped = (
                dep.groupby("VARIAVEL")["Dependencia"]
                .agg(["count", "mean", "std", "min", "max"])
                .reset_index()
            )
            print("Dependencia stats:\n", dep_grouped)
