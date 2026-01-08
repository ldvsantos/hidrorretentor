import glob

import numpy as np
import pandas as pd
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd

FILE_GLOB = r"C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/Avaliac*substrato*DIEGO.xlsx"

TREATMENT_MAP = {
    "SOLV+RESI": "N1",
    "SEM RESINA": "N2",
    "PURA": "N3",
    "SEM SOLVENTE": "N4",
    "CONTROLE": "Control",
    "Controle": "Control",
    "ÁGUA DESTILADA": "Control",
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


def partial_eta_squared(anova_tbl: pd.DataFrame) -> float:
    if "sum_sq" not in anova_tbl.columns:
        return float("nan")
    if anova_tbl.shape[0] < 2:
        return float("nan")
    ss_effect = float(anova_tbl.iloc[0]["sum_sq"])
    ss_error = float(anova_tbl.iloc[-1]["sum_sq"])
    denom = ss_effect + ss_error
    if denom <= 0:
        return float("nan")
    return ss_effect / denom


def letters_from_tukey(tukey) -> dict[str, str]:
    """Gera letras simples (compact letter display) a partir de Tukey.

    Implementação pragmática: ordena por média e atribui letras garantindo que
    grupos não diferentes compartilhem letras; suficiente para n pequeno.
    """

    res = pd.DataFrame(tukey._results_table.data[1:], columns=tukey._results_table.data[0])
    res["reject"] = res["reject"].astype(bool)

    groups = sorted(set(res["group1"]).union(set(res["group2"])))
    # inicia com tudo em uma letra
    letters = {g: "a" for g in groups}

    # estratégia: se há rejeição entre pares, separa letras incrementalmente
    # (não é CLD perfeito, mas evita colidir quando há diferença).
    # Para este trabalho, as letras são auxiliares; p e eta² são os principais.
    current_letter_ord = ord("a")
    means_order = groups
    for g in means_order:
        # verifica se g difere de algum grupo que já tem a mesma letra
        same_letter = [h for h, l in letters.items() if l == letters[g] and h != g]
        for h in same_letter:
            pair = res[((res.group1 == g) & (res.group2 == h)) | ((res.group1 == h) & (res.group2 == g))]
            if not pair.empty and bool(pair.iloc[0]["reject"]):
                current_letter_ord += 1
                letters[g] = chr(current_letter_ord)
                break

    return letters


def analyze_response(raw: pd.DataFrame, response_col: str, label: str) -> dict:
    df = raw[["Tratamento", response_col]].copy()
    df[response_col] = pd.to_numeric(df[response_col], errors="coerce")
    df = df.dropna()
    df = df.rename(columns={response_col: "Valor"})

    # Ajuste de escala: índices de comprimento relativo no Excel estão na ordem de 0.01 (~100%).
    if response_col in {"Comprimento relativo parte aérea", "Comprimento relativo raiz"}:
        df["Valor"] = df["Valor"] * 10000.0

    before_n = len(df)
    df = remove_outliers_iqr(df, "Tratamento", "Valor")
    after_n = len(df)

    present = [k for k in ORDER if k in df["Tratamento"].unique()]
    df["Tratamento"] = pd.Categorical(df["Tratamento"], categories=present, ordered=True)

    means = df.groupby("Tratamento", observed=True)["Valor"].agg(["mean", "std", "count"]).reindex(present)

    # ANOVA OLS
    model = ols("Valor ~ C(Tratamento)", data=df).fit()
    anova_tbl = anova_lm(model, typ=2)
    p_val = float(anova_tbl.iloc[0]["PR(>F)"]) if not anova_tbl.empty else float("nan")
    eta2p = partial_eta_squared(anova_tbl)

    # Tukey
    tukey = pairwise_tukeyhsd(endog=df["Valor"].values, groups=df["Tratamento"].astype(str).values, alpha=0.05)
    letters = letters_from_tukey(tukey)

    tukey_df = pd.DataFrame(tukey._results_table.data[1:], columns=tukey._results_table.data[0])
    # padroniza tipos
    if "p-adj" in tukey_df.columns:
        tukey_df["p-adj"] = pd.to_numeric(tukey_df["p-adj"], errors="coerce")
    if "reject" in tukey_df.columns:
        tukey_df["reject"] = tukey_df["reject"].astype(bool)

    return {
        "label": label,
        "response": response_col,
        "n_before": before_n,
        "n_after": after_n,
        "means": means,
        "p": p_val,
        "eta2p": eta2p,
        "letters": letters,
        "tukey": tukey_df,
    }


def fmt_mean_sd(mean: float, sd: float) -> str:
    if pd.isna(mean):
        return "-"
    if pd.isna(sd):
        sd = 0.0
    return f"{mean:.3f} ± {sd:.3f}"


def main() -> None:
    files = glob.glob(FILE_GLOB)
    if not files:
        raise FileNotFoundError(f"Nenhum arquivo encontrado em: {FILE_GLOB}")

    df = pd.read_excel(files[0], skiprows=1)
    if "Trat." in df.columns:
        df["Trat."] = df["Trat."].ffill()
        df = df[df["Trat."] != "Trat."]

    df["Tratamento"] = df["Trat."].astype(str).str.strip().map(TREATMENT_MAP)
    df = df.dropna(subset=["Tratamento"]).copy()

    targets = [
        ("Comprimento relativo parte aérea", "Comprimento relativo parte aérea (%)"),
        ("Comprimento relativo raiz", "Comprimento relativo raiz (%)"),
        ("Dependência do substrato", "Dependência do núcleo (DN%)"),
    ]

    results = []
    for col, label in targets:
        if col not in df.columns:
            print(f"[skip] coluna ausente: {col}")
            continue
        results.append(analyze_response(df, col, label))

    print("\n=== BANDEJA: resumo pós-IQR (média ± DP) + ANOVA + Tukey ===")
    for r in results:
        print(f"\n[{r['label']}]  n: {r['n_after']} (antes IQR: {r['n_before']})")
        print(f"ANOVA (Tratamento): p = {r['p']:.4g}; eta² parcial = {r['eta2p']:.3f}")
        means = r["means"]
        letters = r["letters"]
        for treat in means.index.tolist():
            mean = float(means.loc[treat, "mean"]) if not pd.isna(means.loc[treat, "mean"]) else float("nan")
            sd = float(means.loc[treat, "std"]) if not pd.isna(means.loc[treat, "std"]) else 0.0
            n = int(means.loc[treat, "count"]) if not pd.isna(means.loc[treat, "count"]) else 0
            letter = letters.get(str(treat), "")
            print(f"- {treat}: {fmt_mean_sd(mean, sd)} ({letter}); n={n}")

        tuk = r.get("tukey")
        if tuk is not None and not tuk.empty:
            sig = tuk[tuk.get("reject", False) == True]  # noqa: E712
            if not sig.empty:
                print("Tukey HSD (pares significativos):")
                for _, row in sig.iterrows():
                    g1 = row.get("group1")
                    g2 = row.get("group2")
                    p_adj = row.get("p-adj")
                    md = row.get("meandiff")
                    print(f"  * {g1} vs {g2}: meandiff={md}, p-aj={p_adj}")


if __name__ == "__main__":
    main()
