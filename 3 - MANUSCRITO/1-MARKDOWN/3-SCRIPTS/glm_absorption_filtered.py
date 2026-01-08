import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

def main():
    root = r"C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS"
    df = pd.read_excel(root + "/PLANTULAS UMIDAS E SECAS PESAGEM GOURD FLOWER 21 E 22 FEVEREIRO .xlsx")
    pivot = df.pivot_table(index=["VARIAVEL", "REP"], columns="ESTADO", values="QUANT.").reset_index()
    pivot["water_gain_g"] = pivot["UMIDA"] - pivot["SECAS"]
    pivot["water_gain_ratio"] = pivot["water_gain_g"] / pivot["SECAS"] * 100
    filtered = pivot[pivot["water_gain_ratio"] > 0]
    model = smf.glm(
        formula="water_gain_ratio ~ C(VARIAVEL)",
        data=filtered,
        family=sm.families.Gamma(sm.families.links.log()),
    ).fit()
    print(model.summary())
    print("\nEstimated marginal means:")
    means = filtered.groupby("VARIAVEL")["water_gain_ratio"].mean()
    print(means)

if __name__ == "__main__":
    main()
