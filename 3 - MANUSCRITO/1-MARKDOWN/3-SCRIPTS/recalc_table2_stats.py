import pandas as pd

PATH = r"C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE/Ensaio_fitotoxidade_1_(25112024).xlsx"
SHEETS = {
    "hipocotilo": "COMPRIMENTO AEREO",
    "radicula": "COMPRIMENTO RAIZ",
    "inibicao_aerea": "INIBIÇÃO AEREA",
    "inibicao_raiz": "INIBICAO RAIZ",
}

ORDER = ["N1", "N2", "N3", "N4", "Control"]


def remove_outliers_iqr(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    df_clean = df.copy()
    indices = []

    for group in df_clean[group_col].dropna().unique():
        subset = df_clean[df_clean[group_col] == group]
        vals = subset[value_col].dropna()
        if len(vals) < 4:
            continue

        q1 = vals.quantile(0.25)
        q3 = vals.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = subset[(subset[value_col] < lower) | (subset[value_col] > upper)].index
        indices.extend(outliers.tolist())

    if indices:
        df_clean = df_clean.drop(indices)

    return df_clean


def summarize_sheet(sheet_name: str) -> pd.DataFrame:
    df = pd.read_excel(PATH, sheet_name=sheet_name)
    cols = [c for c in ["N1", "N2", "N3", "N4", "CONTROLE", "Controle"] if c in df.columns]
    melted = df.melt(value_vars=cols, var_name="Tratamento", value_name="Valor").dropna()
    melted["Tratamento"] = melted["Tratamento"].replace({"CONTROLE": "Control", "Controle": "Control"})

    cleaned = remove_outliers_iqr(melted, "Tratamento", "Valor")

    stats = cleaned.groupby("Tratamento")["Valor"].agg(["mean", "std"]).reindex(
        [o for o in ORDER if o in cleaned["Tratamento"].unique()]
    )
    return stats


if __name__ == "__main__":
    for key, sheet in SHEETS.items():
        stats = summarize_sheet(sheet)
        print(f"\n== {key} ==")
        for treatment, row in stats.iterrows():
            print(f"{treatment}\t{row['mean']:.3f} ± {row['std']:.3f}")
