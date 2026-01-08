import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd

PATH = r"C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE/Ensaio_fitotoxidade_1_(25112024).xlsx"

SHEETS = {
    "Comp. hipocótilo (mm)": "COMPRIMENTO AEREO",
    "Comprimento radícula (mm)": "COMPRIMENTO RAIZ",
    "% Inibição parte aérea": "INIBIÇÃO AEREA",
    "% Inibição radícula": "INIBICAO RAIZ",
}

ORDER = ["N1", "N2", "N3", "N4", "Control"]


def remove_outliers_iqr(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    df_clean = df.copy()
    drop_idx: list[int] = []

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
        drop_idx.extend(outliers.tolist())

    if drop_idx:
        df_clean = df_clean.drop(drop_idx)

    return df_clean


def compact_letters_from_tukey(means: pd.Series, tukey) -> dict[str, str]:
    # Heurística determinística, suficiente para tabela com poucos grupos.
    groups = [g for g in means.index.tolist()]
    groups_sorted = sorted(groups, key=lambda g: (-means[g], g))

    # matriz de significância
    sig = {(a, b): False for a in groups for b in groups}
    if tukey is not None:
        for a, b, _meandiff, _p, _low, _high, reject in tukey._results_table.data[1:]:
            sig[(a, b)] = bool(reject)
            sig[(b, a)] = bool(reject)

    letters: dict[str, str] = {g: "" for g in groups_sorted}
    current_letter_ord = ord("a")

    for g in groups_sorted:
        placed = False
        for letter in sorted({l for v in letters.values() for l in v}):
            # pode compartilhar letra se NÃO for diferente de todos que já têm essa letra
            ok = True
            for other in groups_sorted:
                if other == g:
                    continue
                if letter in letters[other] and sig.get((g, other), False):
                    ok = False
                    break
            if ok:
                letters[g] += letter
                placed = True
                break

        if not placed:
            new_letter = chr(current_letter_ord)
            letters[g] += new_letter
            current_letter_ord += 1

    # manter uma única letra por grupo, como no manuscrito
    letters_single = {g: letters[g][0] if letters[g] else "" for g in letters}
    return letters_single


def analyze_sheet(sheet: str) -> tuple[pd.DataFrame, float | None, float | None, dict[str, str]]:
    df = pd.read_excel(PATH, sheet_name=sheet)
    cols = [c for c in ["N1", "N2", "N3", "N4", "CONTROLE", "Controle"] if c in df.columns]
    melted = df.melt(value_vars=cols, var_name="Tratamento", value_name="Valor").dropna()
    melted["Tratamento"] = melted["Tratamento"].replace({"CONTROLE": "Control", "Controle": "Control"})

    cleaned = remove_outliers_iqr(melted, "Tratamento", "Valor")

    stats = cleaned.groupby("Tratamento")["Valor"].agg(["mean", "std"]).reindex(
        [o for o in ORDER if o in cleaned["Tratamento"].unique()]
    )

    p_value = None
    eta2 = None
    letters = {t: "" for t in stats.index.tolist()}

    if cleaned["Tratamento"].nunique() >= 2:
        model = ols("Valor ~ C(Tratamento)", data=cleaned).fit()
        anova = sm.stats.anova_lm(model, typ=2)
        ss_between = float(anova.loc["C(Tratamento)", "sum_sq"])
        ss_within = float(anova.loc["Residual", "sum_sq"])
        eta2 = ss_between / (ss_between + ss_within) if (ss_between + ss_within) > 0 else None
        p_value = float(anova.loc["C(Tratamento)", "PR(>F)"])

        # letras por Tukey
        try:
            tukey = pairwise_tukeyhsd(endog=cleaned["Valor"], groups=cleaned["Tratamento"], alpha=0.05)
        except Exception:
            tukey = None
        letters = compact_letters_from_tukey(stats["mean"], tukey)

    # garantir que todos do índice existem
    letters = {t: letters.get(t, "") for t in stats.index.tolist()}

    return stats, p_value, eta2, letters


if __name__ == "__main__":
    for label, sheet in SHEETS.items():
        stats, p_value, eta2, letters = analyze_sheet(sheet)
        print(f"\n== {label} ==")
        for t in stats.index.tolist():
            m = stats.loc[t, "mean"]
            s = stats.loc[t, "std"]
            print(f"{t}\t{m:.3f} ± {s:.3f}\t{letters.get(t, '')}")
        print(f"eta2_partial\t{eta2 if eta2 is not None else 'NA'}")
        print(f"p\t{p_value if p_value is not None else 'NA'}")
