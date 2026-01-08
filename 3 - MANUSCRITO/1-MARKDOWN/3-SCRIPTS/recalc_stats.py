import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import glm
import glob

# --- 1. Load Data Functions ---
def load_toxicity_data():
    path = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE/Ensaio_fitotoxidade_1_(25112024).xlsx"
    pathraizes = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE/PESAGEM RAIZES^LJ FOLHAS E PLANTULAS 2.xlsx"
    pathgerm = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE/CONTAGEM RÚCULA BOD.xlsx"
    
    # IVG/Germination
    df_germ = pd.read_excel(pathgerm)
    df_germ.columns = [c.strip() for c in df_germ.columns]
    # Tratamento col: 'CONTAGEM DE PLANTULAS NA B.O.D'
    # Need to normalize treatments!
    
    # Morphology
    df_hypo = pd.read_excel(path, sheet_name="COMPRIMENTO AEREO")
    df_rad = pd.read_excel(path, sheet_name="COMPRIMENTO RAIZ")
    
    # Inhibition
    df_inh_hypo = pd.read_excel(path, sheet_name="INIBIÇÃO AEREA")
    df_inh_rad = pd.read_excel(path, sheet_name="INIBICAO RAIZ")
    
    return df_germ, df_hypo, df_rad, df_inh_hypo, df_inh_rad

def load_bandeja_data():
    f = glob.glob('C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/Avaliac*substrato*DIEGO.xlsx')[0]
    df = pd.read_excel(f, skiprows=1)
    # Forward fill "Trat." missing values if they are merged cells in concept
    # Look at head: row 1 PURA, row 2 NaN (R2). So yes, forward fill Trat.
    df["Trat."] = df["Trat."].fillna(method="ffill")
    return df

# --- 2. Outlier Removal (Consistent with Plots) ---
def remove_outliers_iqr(df, col_group, col_val):
    df_clean = df.copy()
    indices = []
    groups = df_clean[col_group].unique()
    for g in groups:
        subset = df_clean[df_clean[col_group] == g]
        vals = subset[col_val].dropna()
        if len(vals) < 4: continue
        Q1 = vals.quantile(0.25)
        Q3 = vals.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5*IQR
        upper = Q3 + 1.5*IQR
        outliers = subset[(subset[col_val] < lower) | (subset[col_val] > upper)].index
        indices.extend(outliers)
    
    if indices:
        df_clean = df_clean.drop(indices)
    return df_clean

# --- 3. Statistical Analysis (GLM Gamma/Gaussian) ---
def run_glm(df, formula, family=sm.families.Gaussian()):
    # Convert To Factor
    # formula ex: "IVG ~ Tratamento"
    model = glm(formula=formula, data=df, family=family).fit()
    return model

def analyze_dataset():
    results = {}
    
    # --- GERMINATION (Table 1) ---
    df_g, _, _, _, _ = load_toxicity_data()
    col_treat = 'CONTAGEM DE PLANTULAS NA B.O.D'
    df_g = df_g.dropna(subset=['IVG', 'G%', 'TMG'])
    # Normalize treatments names if needed (PURA -> N?, etc)
    # For now assume text match or close enough.
    
    # Clean Outliers
    df_g_clean = remove_outliers_iqr(df_g, col_treat, 'IVG')
    
    # Calc Means/SD
    metrics = ['G%', 'IVG', 'TMG']
    stats_g = df_g_clean.groupby(col_treat)[metrics].agg(['mean', 'std'])
    results['germination'] = stats_g
    
    # Run GLM for p-values (Gaussian for IVG/TMG/G% or Binomial for G%?)
    # Usually G% is binomial, but n=100. Gaussian often used on arcsin. 
    # Let's stick to Gaussian GLM (Identity link) as robust ANOVA replacement.
    
    # --- MORPHOLOGY (Table 2) ---
    # Need to melt first
    _, df_h, df_r, df_ih, df_ir = load_toxicity_data()
    
    def process_morph(df, val_name):
        melted = df.melt(value_vars=[c for c in df.columns if c in ['N1','N2','N3','N4','CONTROLE','Controle']], var_name="Tratamento", value_name="Valor")
        melted = melted.dropna()
        # Clean
        clean = remove_outliers_iqr(melted, "Tratamento", "Valor")
        stats = clean.groupby("Tratamento")["Valor"].agg(['mean', 'std'])
        return stats, clean

    h_stats, h_clean = process_morph(df_h, "Hipocótilo")
    r_stats, r_clean = process_morph(df_r, "Radícula")
    ih_stats, ih_clean = process_morph(df_ih, "Inib_Hipo")
    ir_stats, ir_clean = process_morph(df_ir, "Inib_Rad")
    
    results['morph'] = {
        "hipo": h_stats, "rad": r_stats, "inib_hipo": ih_stats, "inib_rad": ir_stats
    }
    
    # --- BANDEJA (Table/Fig 10/11) ---
    df_b = load_bandeja_data()
    # Tratamentos expected: PURA, COMPLETA, SEM RESINA... map to N1..N4?
    # Inspect treatments
    # Clean outliers
    
    target_cols = ['Dependência do substrato', 'Comprimento relativo raiz', 'Comprimento relativo parte aérea']
    
    bandeja_stats = {}
    for col in target_cols:
        if col not in df_b.columns: continue
        # Drop NaNs and ensure numeric
        subset = df_b[['Trat.', col]].dropna().copy()
        subset.columns = ['Tratamento', 'Valor']
        
        # Force numeric
        subset['Valor'] = pd.to_numeric(subset['Valor'], errors='coerce')
        subset = subset.dropna()
        
        # Clean
        clean = remove_outliers_iqr(subset, 'Tratamento', 'Valor')
        stats = clean.groupby('Tratamento')['Valor'].agg(['mean', 'std'])
        bandeja_stats[col] = stats
        
    results['bandeja'] = bandeja_stats

    return results

if __name__ == "__main__":
    res = analyze_dataset()
    print("ANALYSIS COMPLETE. RESULTS:\n")
    for k, v in res.items():
        print(f"=== {k} ===")
        if isinstance(v, dict):
            for subk, subv in v.items():
                print(f"-- {subk} --")
                print(subv)
        else:
            print(v)
