import pandas as pd
from pathlib import Path

root = Path(r"C:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2 - HIDRORRETENTOR\2 - DADOS")
file_path = root / "PLANTULAS UMIDAS E SECAS PESAGEM GOURD FLOWER 21 E 22 FEVEREIRO .xlsx"

df = pd.read_excel(file_path)
pivot = (
    df.pivot_table(index=["VARIAVEL", "REP"], columns="ESTADO", values="QUANT.")
    .reset_index()
)
pivot["water_gain_g"] = pivot["UMIDA"] - pivot["SECAS"]
pivot["water_gain_ratio"] = pivot["water_gain_g"] / pivot["SECAS"] * 100

summary = pivot.groupby("VARIAVEL").agg(
    n=("water_gain_g", "count"),
    mean_gain=("water_gain_g", "mean"),
    std_gain=("water_gain_g", "std"),
    mean_ratio=("water_gain_ratio", "mean"),
    std_ratio=("water_gain_ratio", "std"),
).reset_index()

print(pivot.round(6))
print("\nSummary:\n", summary.round(3))
