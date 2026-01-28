import pandas as pd
import numpy as np

df = pd.read_excel('C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE/CONTAGEM RÚCULA BOD.xlsx')
df.columns = [c.strip() for c in df.columns]
treat_col = 'CONTAGEM DE PLANTULAS NA B.O.D'

df_clean = df.dropna(subset=['IVG', 'TMG', 'G%']).copy()

# Strip extra spaces from treatment names
df_clean[treat_col] = df_clean[treat_col].str.strip()

mapping = {
    'SOLV+RESI': 'N1',
    'PURA': 'N2', 
    'FOLHA': 'N3',
    'SEM SOLVENTE': 'N4',
    'ÁGUA DESTILADA': 'Control'
}

df_clean['Tratamento'] = df_clean[treat_col].map(mapping)

print('=== ESTATÍSTICAS POR TRATAMENTO ===')
for trat in ['N1', 'N2', 'N3', 'N4', 'Control']:
    subset = df_clean[df_clean['Tratamento'] == trat]
    if len(subset) > 0:
        ivg_mean = subset['IVG'].mean()
        ivg_std = subset['IVG'].std()
        tmg_mean = subset['TMG'].mean()
        tmg_std = subset['TMG'].std()
        g_mean = subset['G%'].mean()
        g_std = subset['G%'].std()
        print(f'{trat}: G%={g_mean:.2f}±{g_std:.3f} | IVG={ivg_mean:.3f}±{ivg_std:.3f} | TMG={tmg_mean:.3f}±{tmg_std:.3f}')

print('\n=== COMPARAÇÕES COM CONTROLE ===')
control_ivg = df_clean[df_clean['Tratamento'] == 'Control']['IVG'].mean()
control_tmg = df_clean[df_clean['Tratamento'] == 'Control']['TMG'].mean()
control_g = df_clean[df_clean['Tratamento'] == 'Control']['G%'].mean()

n1_ivg = df_clean[df_clean['Tratamento'] == 'N1']['IVG'].mean()
n1_tmg = df_clean[df_clean['Tratamento'] == 'N1']['TMG'].mean()
n1_g = df_clean[df_clean['Tratamento'] == 'N1']['G%'].mean()

print(f'G%: N1 vs Control = {n1_g:.2f} vs {control_g:.2f} | Δ% = {((n1_g-control_g)/control_g*100):.2f}%')
print(f'IVG: N1 vs Control = {n1_ivg:.3f} vs {control_ivg:.3f} | Δ% = {((n1_ivg-control_ivg)/control_ivg*100):.2f}%')
print(f'TMG: N1 vs Control = {n1_tmg:.3f} vs {control_tmg:.3f} | Δ% = {((n1_tmg-control_tmg)/control_tmg*100):.2f}%')

print('\n=== COHEN D (N1 vs Control) ===')
# Cohen's d = (mean1 - mean2) / pooled_std
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (group1.mean() - group2.mean()) / pooled_std

n1_data = df_clean[df_clean['Tratamento'] == 'N1']
control_data = df_clean[df_clean['Tratamento'] == 'Control']

d_g = cohens_d(n1_data['G%'], control_data['G%'])
d_ivg = cohens_d(n1_data['IVG'], control_data['IVG'])
d_tmg = cohens_d(n1_data['TMG'], control_data['TMG'])

print(f"Cohen's d (G%): {d_g:.3f}")
print(f"Cohen's d (IVG): {d_ivg:.3f}")
print(f"Cohen's d (TMG): {d_tmg:.3f}")
