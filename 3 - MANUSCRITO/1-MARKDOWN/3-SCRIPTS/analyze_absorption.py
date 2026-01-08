import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

root = r"C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS"
file_path = root + "/PLANTULAS UMIDAS E SECAS PESAGEM GOURD FLOWER 21 E 22 FEVEREIRO .xlsx"

df = pd.read_excel(file_path)
pivot = (
    df.pivot_table(index=["VARIAVEL", "REP"], columns="ESTADO", values="QUANT.")
    .reset_index()
)
pivot["water_gain_g"] = pivot["UMIDA"] - pivot["SECAS"]
pivot["water_gain_ratio"] = pivot["water_gain_g"] / pivot["SECAS"] * 100

anova_gain = ols("water_gain_g ~ C(VARIAVEL)", data=pivot).fit()
table_gain = sm.stats.anova_lm(anova_gain, typ=2)

anova_ratio = ols("water_gain_ratio ~ C(VARIAVEL)", data=pivot).fit()
table_ratio = sm.stats.anova_lm(anova_ratio, typ=2)

print("gain means:")
print(pivot.groupby("VARIAVEL")["water_gain_g"].agg(['mean','std']))
print("\nratio means:")
print(pivot.groupby("VARIAVEL")["water_gain_ratio"].agg(['mean','std']))
print("\nANOVA gain:")
print(table_gain)
print("\nANOVA ratio:")
print(table_ratio)
