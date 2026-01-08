import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# --- CONFIGURAÇÃO DE ESTILO ---
# Paleta A (Pastel) - Para gráficos (a) / Parte Aérea
CORES_A = {
    "N1": "#B4E7CE", "N2": "#A8D8EA", "N3": "#FFCDB2", "N4": "#D4A5A5", "CONTROLE": "#FFF4A3", "Controle": "#FFF4A3"
}

# Paleta B (Saturada/Vibrante) - Para gráficos (b) / Raiz ou Comparativo
CORES_B = {
    "N1": "#52B788", "N2": "#5FA8D3", "N3": "#F4A261", "N4": "#E76F51", "CONTROLE": "#E9C46A", "Controle": "#E9C46A"
}

HATCHES = {
    "N1": "///", "N2": "+++", "N3": "OO", "N4": "...", "CONTROLE": "", "Controle": ""
}

LEGENDA_DESCRICOES = {
    "N1": "N1 (formulação completa)",
    "N2": "N2 (sem resina)",
    "N3": "N3 (resíduos vegetais)",
    "N4": "N4 (resíduos e fibras)",
    "CONTROLE": "Controle",
    "Controle": "Controle"
}

ORDER = ["N1", "N2", "N3", "N4", "Controle"]

plt.rcParams.update({
    "font.size": 14,
    "font.family": "sans-serif",
    "font.sans-serif": ["Poppins", "Arial", "DejaVu Sans"],
    'axes.edgecolor': 'black',
    'axes.linewidth': 0.8,
    'axes.grid': False,
    'grid.color': '#E5E5E5',
    'grid.linewidth': 0.3, 
    'axes.grid.axis': 'y',
    'legend.frameon': True,
    'legend.edgecolor': 'black',
    'legend.fancybox': False,
    'xtick.color': 'black',
    'ytick.color': 'black'
})

def adicionar_legenda(ax, present_keys: list, palette: dict):
    patches = []
    labels = []
    # Force specific order
    
    # Normalize keys for searching in descriptions
    # The sheet data columns are uppercase or Capitalized. 
    # Let's trust ORDER list which is standard. 
    
    for key in ORDER:
        # Check if this key corresponds to any of the present columns
        # Treat 'CONTROLE' and 'Controle' as same
        found = False
        if key in present_keys: found = True
        if key == "Controle" and "CONTROLE" in present_keys: found = True
        
        if not found:
            continue
            
        # Get color/hatch using the key that exists in palette map
        # Palette has both 'Controle' and 'CONTROLE'
        color = palette.get(key, "#cccccc")
        hatch = HATCHES.get(key, "")
        
        patches.append(
            mpatches.Patch(
                facecolor=color,
                edgecolor="black",
                hatch=hatch,
            )
        )
        labels.append(LEGENDA_DESCRICOES.get(key, key))

    if patches:
        ax.legend(
            patches,
            labels,
            loc="upper right",
            frameon=True,
            framealpha=1.0,
            facecolor="white",
            edgecolor="black",
            labelspacing=0.35,
            handlelength=1.0,
            handletextpad=0.5,
            borderpad=0.6,
            fontsize=11,
        )

def plot_sheet(sheet_name, y_label, output_file, df_curr, palette=CORES_A, tag=None):
    # Calculate Mean and Std
    # Columns expected: N1, N2, N3, N4, CONTROLE (or similar)
    cols = [c for c in ["CONTROLE", "Controle", "N1", "N2", "N3", "N4"] if c in df_curr.columns]
    
    # Sort cols
    # Ensure standard order: Controle, N1, N2, N3, N4 -- actually user wants N1..N4, Controle usually?
    # plot_bandeja uses ORDER = ["N1", "N2", "N3", "N4", "Control"]
    # Let's stick to ORDER defined above for rendering x-axis too or just reuse logic
    
    # Define display order
    order_display = ["N1", "N2", "N3", "N4", "Controle", "CONTROLE"]
    final_cols = [c for c in order_display if c in cols]
    
    means = df_curr[final_cols].mean()
    stds = df_curr[final_cols].std()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    for i, col in enumerate(final_cols):
        val_mean = means[col]
        val_std = stds[col]
        
        # Determine Color/Hatch key
        key = col
        if col.upper() == "CONTROLE": key = "Controle"
        
        color = palette.get(key, "#cccccc")
        hatch = HATCHES.get(key, "")
        
        ax.bar(
            i, val_mean,
            yerr=val_std,
            color=color,
            edgecolor="black",
            hatch=hatch,
            width=0.6,
            capsize=5,
            linewidth=1.0,
            error_kw={'ecolor': 'black', 'elinewidth': 1.0}
        )
        
    ax.set_xticks(range(len(final_cols)))
    labels = [c.replace("CONTROLE", "Controle") for c in final_cols]
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylabel(y_label, color="black", weight='bold')
    
    ax.grid(axis='y', linestyle='-', color='gray', alpha=0.3)
    ax.set_axisbelow(True)

    if tag:
        ax.text(
            0.02, 0.95, tag,
            transform=ax.transAxes,
            fontsize=16,
            fontweight='bold',
            va='top', ha='left'
        )
    
    adicionar_legenda(ax, final_cols, palette)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Salvou {output_file}")

def remove_outliers_iqr_series(vals):
    if len(vals) < 4: return vals
    Q1 = np.percentile(vals, 25)
    Q3 = np.percentile(vals, 75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return vals[(vals >= lower) & (vals <= upper)]

def plot_raincloud(sheet_name, y_label, output_file, df_curr, palette=CORES_A, tag=None):
    # Columns expected: N1, N2, N3, N4, CONTROLE
    cols = [c for c in ["CONTROLE", "Controle", "N1", "N2", "N3", "N4"] if c in df_curr.columns]
    
    # Define display order
    order_display = ["N1", "N2", "N3", "N4", "Controle", "CONTROLE"]
    final_cols = [c for c in order_display if c in cols]
    
    # Normalize keys for plotting loop
    unique_keys = [] 
    for c in final_cols:
        key = "Controle" if c.upper() == "CONTROLE" else c
        if key not in unique_keys: unique_keys.append(key)
    
    # Prepare data dict: key -> values (filtered)
    # Using specific key "Controle" for both "CONTROLE" and "Controle" columns if both exist (rare)
    data_map = {}
    for col in final_cols:
        key = "Controle" if col.upper() == "CONTROLE" else col
        vals = df_curr[col].dropna().values
        vals = remove_outliers_iqr_series(vals)
        data_map[key] = vals

    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Indices for x axis
    indices = range(len(unique_keys))
    
    # Draw Raincloud elements
    # 1. Violin (Right half)
    for i, key in enumerate(unique_keys):
        vals = data_map[key]
        if len(vals) < 2 or np.var(vals) == 0:
            continue
            
        parts = ax.violinplot(
            [vals], positions=[i], vert=True, 
            showmeans=False, showmedians=False, showextrema=False, widths=0.5
        )
        for pc in parts['bodies']:
            pc.set_facecolor(palette.get(key, "#cccccc"))
            pc.set_edgecolor("black")
            pc.set_alpha(0.6)
            # Clip to right half
            path = pc.get_paths()[0]
            verts = path.vertices
            m = np.mean(verts[:, 0])
            verts[:, 0] = np.clip(verts[:, 0], m, np.inf)

    # 2. Boxplot (Left shifted)
    for i, key in enumerate(unique_keys):
        vals = data_map[key]
        if len(vals) == 0: continue
        
        bp = ax.boxplot(
            [vals], positions=[i - 0.15], widths=0.2, 
            patch_artist=True, showfliers=False
        )
        
        color = palette.get(key, "#cccccc")
        hatch = HATCHES.get(key, "")
        
        for patch in bp['boxes']:
            patch.set_facecolor(color)
            patch.set_hatch(hatch)
            patch.set_edgecolor("black")
            
        for element in ['whiskers', 'fliers', 'medians', 'caps']:
            plt.setp(bp[element], color='black', linewidth=1)

    # 3. Jitter Points (Right shifted)
    for i, key in enumerate(unique_keys):
        vals = data_map[key]
        if len(vals) == 0: continue
        
        # Jitter x
        x_jit = np.random.normal(i + 0.1, 0.04, size=len(vals))
        ax.scatter(x_jit, vals, s=20, alpha=0.7, color="black", edgecolor="none", zorder=3)

    ax.set_xticks(indices)
    ax.set_xticklabels([k for k in unique_keys], rotation=45, ha='right')
    ax.set_ylabel(y_label, color="black", weight='bold')
    
    ax.grid(axis='y', linestyle='-', color='gray', alpha=0.3)
    ax.set_axisbelow(True)

    if tag:
        ax.text(
            0.02, 0.95, tag,
            transform=ax.transAxes,
            fontsize=16,
            fontweight='bold',
            va='top', ha='left'
        )
    
    adicionar_legenda(ax, unique_keys, palette)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Salvou {output_file}")

# --- PROCESSAMENTO ---
root_dados = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE/Ensaio_fitotoxidade_1_(25112024).xlsx"
output_dir = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/3 - MANUSCRITO/1-MARKDOWN/2-IMG"

try:
    xl = pd.ExcelFile(root_dados)
    
    # Fig 7a / Fig_006: Hipocótilo (Paleta A - Pastel)
    if "COMPRIMENTO AEREO" in xl.sheet_names:
        df = pd.read_excel(root_dados, sheet_name="COMPRIMENTO AEREO")
        plot_sheet("COMPRIMENTO AEREO", "Comprimento do hipocótilo (mm)", f"{output_dir}/Fig_006.png", df, palette=CORES_A, tag="(a)")

    # Fig 7b / Fig_007: Radícula (Paleta B - Saturada)
    if "COMPRIMENTO RAIZ" in xl.sheet_names:
        df = pd.read_excel(root_dados, sheet_name="COMPRIMENTO RAIZ")
        plot_sheet("COMPRIMENTO RAIZ", "Comprimento da radícula (mm)", f"{output_dir}/Fig_007.png", df, palette=CORES_B, tag="(b)")
        
    # Fig 8a / Fig_008: Inibição Hipocótilo (Paleta A - Pastel) -> RAINCLOUD
    if "INIBIÇÃO AEREA" in xl.sheet_names:
        df = pd.read_excel(root_dados, sheet_name="INIBIÇÃO AEREA")
        plot_raincloud("INIBIÇÃO AEREA", "Inibição do hipocótilo (%)", f"{output_dir}/Fig_008.png", df, palette=CORES_A, tag="(a)")

    # Fig 8b / Fig_009: Inibição Radícula (Paleta B - Saturada) -> RAINCLOUD
    if "INIBICAO RAIZ" in xl.sheet_names:
        df = pd.read_excel(root_dados, sheet_name="INIBICAO RAIZ")
        plot_raincloud("INIBICAO RAIZ", "Inibição da radícula (%)", f"{output_dir}/Fig_009.png", df, palette=CORES_B, tag="(b)")

except Exception as e:
    print(f"Erro: {e}")
