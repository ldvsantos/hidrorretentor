import pandas as pd
import numpy as np

# === MORFOLOGIA ===
path_morph = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE/Ensaio_fitotoxidade_1_(25112024).xlsx"

df_hipo = pd.read_excel(path_morph, sheet_name="COMPRIMENTO AEREO")
df_rad = pd.read_excel(path_morph, sheet_name="COMPRIMENTO RAIZ")

# === BIOMASSA ===
path_biomassa = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE/PESAGEM RAIZES^LJ FOLHAS E PLANTULAS 2.xlsx"
df_biomassa = pd.read_excel(path_biomassa)

def cohens_d(group1, group2):
    """Calcula Cohen's d"""
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    d = (group1.mean() - group2.mean()) / pooled_std
    return d

print("=== COHEN'S D - MORFOLOGIA (HIPOCÓTILO E RADÍCULA) ===\n")

# Hipocótilo
cols_hipo = ['N1', 'N2', 'N3', 'N4', 'CONTROLE']
if 'Controle' in df_hipo.columns:
    cols_hipo = ['N1', 'N2', 'N3', 'N4', 'Controle']

for col in cols_hipo:
    if col in df_hipo.columns and col != 'CONTROLE' and col != 'Controle':
        control_col = 'CONTROLE' if 'CONTROLE' in df_hipo.columns else 'Controle'
        if control_col in df_hipo.columns:
            treat = df_hipo[col].dropna()
            control = df_hipo[control_col].dropna()
            if len(treat) > 1 and len(control) > 1:
                d = cohens_d(treat, control)
                print(f"Hipocótilo - {col} vs Control: Cohen's d = {d:.3f}")

# Radícula
cols_rad = ['N1', 'N2', 'N3', 'N4', 'CONTROLE']
if 'Controle' in df_rad.columns:
    cols_rad = ['N1', 'N2', 'N3', 'N4', 'Controle']

for col in cols_rad:
    if col in df_rad.columns and col != 'CONTROLE' and col != 'Controle':
        control_col = 'CONTROLE' if 'CONTROLE' in df_rad.columns else 'Controle'
        if control_col in df_rad.columns:
            treat = df_rad[col].dropna()
            control = df_rad[control_col].dropna()
            if len(treat) > 1 and len(control) > 1:
                d = cohens_d(treat, control)
                print(f"Radícula - {col} vs Control: Cohen's d = {d:.3f}")

print("\n=== COHEN'S D - BIOMASSA ===\n")

# Carregar dados corretos de biomassa
path_biomassa_correct = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/PLANTULAS UMIDAS E SECAS PESAGEM GOURD FLOWER 21 E 22 FEVEREIRO .xlsx"
df_bio = pd.read_excel(path_biomassa_correct)

# Mapear tratamentos (com strip para remover espaços)
df_bio['VARIAVEL'] = df_bio['VARIAVEL'].str.strip()

mapping_bio = {
    'SOLV+RESI': 'N1',
    'PURA': 'N2',
    'FOLHA': 'N3',
    'SEM SOLVENTE': 'N4',
    'AGUA DESTILADA': 'Control'
}

df_bio['Tratamento'] = df_bio['VARIAVEL'].map(mapping_bio)

# Calcular Cohen's d para massa UMIDA e SECA
for estado in ['UMIDA', 'SECAS']:
    subset = df_bio[df_bio['ESTADO'] == estado].copy()
    control_data = subset[subset['Tratamento'] == 'Control']['QUANT.'].dropna()
    
    print(f"\n--- Massa {estado} ---")
    for trat in ['N1', 'N2', 'N3', 'N4']:
        treat_data = subset[subset['Tratamento'] == trat]['QUANT.'].dropna()
        if len(treat_data) > 1 and len(control_data) > 1:
            d = cohens_d(treat_data, control_data)
            treat_mean = treat_data.mean()
            treat_std = treat_data.std()
            control_mean = control_data.mean()
            control_std = control_data.std()
            print(f"{trat}: {treat_mean:.3f}±{treat_std:.3f} vs Control: {control_mean:.3f}±{control_std:.3f} | Cohen's d = {d:.3f}")

