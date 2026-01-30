import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.patches as mpatches

# --- CONFIGURAÇÃO DE ESTILO ---
CORES_PASTEL_N = {
    "N1": "#B4E7CE",
    "N2": "#A8D8EA",
    "N3": "#FFCDB2",
    "N4": "#D4A5A5",
    "Control": "#FFF4A3",
}

HATCHES_N = {
    "N1": "///",
    "N2": "+++",
    "N3": "OO",
    "N4": "...",
    "Control": "",
}

# Cores e hachuras por rótulo bruto (dos arquivos) e por rótulo canônico (N1..N4/Control)
CORES_PASTEL = {
    **CORES_PASTEL_N,
    "SOLV+RESI": CORES_PASTEL_N["N1"],
    "SEM RESINA": CORES_PASTEL_N["N2"],
    "PURA": CORES_PASTEL_N["N3"],
    "FOLHA": CORES_PASTEL_N["N3"],
    "SEM SOLVENTE": CORES_PASTEL_N["N4"],
    "CONTROLE": CORES_PASTEL_N["Control"],
    "Controle": CORES_PASTEL_N["Control"],
    "AGUA DESTILADA": CORES_PASTEL_N["Control"],
    "ÁGUA DESTILADA": CORES_PASTEL_N["Control"],
}

HATCHES = {
    **HATCHES_N,
    "SOLV+RESI": HATCHES_N["N1"],
    "SEM RESINA": HATCHES_N["N2"],
    "PURA": HATCHES_N["N3"],
    "FOLHA": HATCHES_N["N3"],
    "SEM SOLVENTE": HATCHES_N["N4"],
    "CONTROLE": HATCHES_N["Control"],
    "Controle": HATCHES_N["Control"],
    "AGUA DESTILADA": HATCHES_N["Control"],
    "ÁGUA DESTILADA": HATCHES_N["Control"],
}

plt.rcParams.update({
    'font.size': 14,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Poppins', 'Arial', 'DejaVu Sans'],
    'axes.edgecolor': 'black',
    'axes.linewidth': 1.0, # Slightly thicker for "Origin" look
    'axes.grid': False,
    'legend.frameon': True,
    'legend.edgecolor': 'black',
    'xtick.color': 'black',
    'ytick.color': 'black'
})

DISPLAY_MAP = {
    "N1": "N1",
    "N2": "N2",
    "N3": "N3",
    "N4": "N4",
    "SOLV+RESI": "N1",
    "SEM RESINA": "N2",
    "PURA": "N3",
    "FOLHA": "N3",
    "SEM SOLVENTE": "N4",
    "CONTROLE": "Control",
    "Controle": "Control",
    "AGUA DESTILADA": "Control",
    "ÁGUA DESTILADA": "Control",
    "ÁGUA DESTILADA ": "Control",
    "FOLHA": "N3",
    "FOLHA ": "N3"
}

LEGENDA_DESCRICOES = {
    "N1": "N1 (Full formulation)",
    "N2": "N2 (No resin)",
    "N3": "N3 (Plant residues)",
    "N4": "N4 (Residues and fibers)",
    "Control": "Control"
}

ORDER_PRIORITY = {"N1": 0, "N2": 1, "N3": 2, "N4": 3, "Control": 4}

def adicionar_legenda(ax, ordem):
    patches = []
    labels = []
    vistos = set()
    for item in ordem:
        key = DISPLAY_MAP.get(item, item)
        if key in vistos:
            continue
        color = CORES_PASTEL.get(key, "#cccccc")
        hatch = HATCHES.get(key, "")
        patch = mpatches.Patch(facecolor=color, edgecolor="black", hatch=hatch)
        patches.append(patch)
        labels.append(LEGENDA_DESCRICOES.get(key, key))
        vistos.add(key)
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

def remove_outliers_iqr(df, col_group, col_val):
    """
    Remove outliers based on 1.5 * IQR rule per group.
    """
    df_clean = df.copy()
    indices_to_drop = []
    
    groups = df_clean[col_group].unique()
    for g in groups:
        subset = df_clean[df_clean[col_group] == g]
        vals = subset[col_val].dropna()
        if len(vals) < 4: continue
        
        Q1 = vals.quantile(0.25)
        Q3 = vals.quantile(0.75)
        IQR = Q3 - Q1
        
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        
        outliers = subset[(subset[col_val] < lower) | (subset[col_val] > upper)].index
        indices_to_drop.extend(outliers)
        
    if indices_to_drop:
        print(f"Removed {len(indices_to_drop)} outliers from {col_val}")
        df_clean = df_clean.drop(indices_to_drop)
        
    return df_clean

def custom_raincloud(ax, data, x, y, order, colors, hatches):
    """
    Desenha um Raincloud Plot: Half-Violin (Left) + Boxplot (Center) + Strip (Right)
    Para o layout "OriginPro": Box (Left) + Points (Right) + Curve (Right of points)
    O user pediu 'boxplot com residuos por fora' igual a imagem.
    Imagem: Box (Left), Points (Right), Curve (Far Right).
    Vamos tentar: Box @ x-0.1, Points @ x+0.1, Violin @ x+0.2 (Half Right)
    """
    
    # 1. Violin (Density) - Iterativo Seguro
    for i, t in enumerate(order):
        vals = data[data[x] == t][y].dropna().values
        # Violin precisa de >1 ponto e variância > 0
        if len(vals) < 2 or np.var(vals) == 0:
            continue
            
        parts = ax.violinplot(
            [vals],
            positions=[i],
            vert=True, showmeans=False, showmedians=False, showextrema=False,
            widths=0.5
        )
        for pc in parts['bodies']:
            # Clip to right half
            path = pc.get_paths()[0]
            verts = path.vertices
            m = np.mean(verts[:, 0])
            verts[:, 0] = np.clip(verts[:, 0], m, np.inf)
            
            pc.set_facecolor(colors.get(t, "gray"))
            pc.set_edgecolor("black")
            pc.set_alpha(0.6)

    # 2. Boxplot
    for i, t in enumerate(order):
        vals = data[data[x] == t][y].dropna().values
        if len(vals) == 0: continue
        
        # Shift slightly left (-0.15)
        bp = ax.boxplot(
            [vals],
            positions=[i - 0.15],
            widths=0.2,
            patch_artist=True,
            showfliers=False,
        )
        for patch in bp['boxes']:
            patch.set_facecolor(colors.get(t, "white"))
            patch.set_hatch(hatches.get(t, ""))
            patch.set_edgecolor("black")
        for element in ['whiskers', 'fliers', 'medians', 'caps']:
            plt.setp(bp[element], color='black', linewidth=1)

    # 3. Jitter Points
    for i, t in enumerate(order):
        vals = data[data[x] == t][y].dropna().values
        if len(vals) == 0: continue
        # Shift right (+0.1)
        x_jit = np.random.normal(i + 0.1, 0.04, size=len(vals))
        ax.scatter(x_jit, vals, s=20, alpha=0.7, color="black", edgecolor="none", zorder=3)

def process_file_growth():
    file_path = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE/Ensaio_fitotoxidade_1_(25112024).xlsx"
    output_dir = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/3 - MANUSCRITO/1-MARKDOWN/2-IMG"
    
    # Sheets to process
    configs = [
        {"sheet": "COMPRIMENTO AEREO", "ylabel": "Hypocotyl length (mm)", "out": "Fig_006.png"},
        {"sheet": "COMPRIMENTO RAIZ", "ylabel": "Radicle length (mm)", "out": "Fig_007.png"},
        {"sheet": "INIBIÇÃO AEREA", "ylabel": "Hypocotyl inhibition (%)", "out": "Fig_008.png"},
        {"sheet": "INIBICAO RAIZ", "ylabel": "Radicle inhibition (%)", "out": "Fig_009.png"}
    ]
    
    try:
        xl = pd.ExcelFile(file_path)
        for cfg in configs:
            if cfg["sheet"] not in xl.sheet_names: continue
            
            df = pd.read_excel(file_path, sheet_name=cfg["sheet"])
            
            # Melt dataframe: Columns N1, N2.. to Variable/Value
            # Expected cols: N1, N2, N3, N4, CONTROLE
            valid_cols = [c for c in ["CONTROLE", "Controle", "N1", "N2", "N3", "N4"] if c in df.columns]
            
            # Map column names to cleaner labels if needed
            # Or keep them as is and map colors
            
            melted = df.melt(value_vars=valid_cols, var_name="Tratamento", value_name="Valor")
            
            # Normalize names
            melted["Tratamento"] = melted["Tratamento"].replace({"CONTROLE": "Control", "Controle": "Control"})
            
            # REMOVE OUTLIERS
            melted = remove_outliers_iqr(melted, "Tratamento", "Valor")

            # Order
            order = ["N1", "N2", "N3", "N4", "Control"]
            final_order = [o for o in order if o in melted["Tratamento"].unique()]
            final_order = sorted(final_order, key=lambda item: ORDER_PRIORITY.get(DISPLAY_MAP.get(item, item), 99))
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            custom_raincloud(ax, melted, "Tratamento", "Valor", final_order, CORES_PASTEL, HATCHES)
            
            ax.set_xticks(range(len(final_order)))
            axis_labels = [DISPLAY_MAP.get(lbl, lbl) for lbl in final_order]
            ax.set_xticklabels(axis_labels, rotation=0)
            ax.set_ylabel(cfg["ylabel"], weight="bold")
            # ax.set_xlabel("Tratamentos")

            legend_order = [lbl for lbl in ["N1", "N2", "N3", "N4", "Control"] if lbl in [DISPLAY_MAP.get(x, x) for x in final_order]]
            adicionar_legenda(ax, legend_order)
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/{cfg['out']}", dpi=300)
            plt.close()
            print(f"Gerado {cfg['out']}")
            
    except Exception as e:
        print(f"Erro em growth: {e}")

def process_file_ivg():
    file_path = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS/1 - TESTE FITOTOXIDADE/CONTAGEM RÚCULA BOD.xlsx"
    output_dir = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/3 - MANUSCRITO/1-MARKDOWN/2-IMG"
    
    try:
        df = pd.read_excel(file_path)
        # Check cols: 'CONTAGEM DE PLANTULAS NA B.O.D ' (Tratamento), 'IVG'
        # Need to strip whitespace from col name
        df.columns = [c.strip() for c in df.columns]
        
        col_treat = 'CONTAGEM DE PLANTULAS NA B.O.D' 
        valid = df.dropna(subset=['IVG'])
        
        # REMOVE OUTLIERS IQR
        valid = remove_outliers_iqr(valid, col_treat, 'IVG')

        # Order? We will find unique and sort
        valid[col_treat] = valid[col_treat].astype(str).str.strip()
        mapped = valid[col_treat].map(lambda v: DISPLAY_MAP.get(v, v))
        valid = valid.assign(Tratamento=mapped)

        treats = valid["Tratamento"].unique()
        treats = sorted(treats, key=lambda t: ORDER_PRIORITY.get(DISPLAY_MAP.get(t, t), 99))
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Use simpler logic or reuse raincloud
        # Raincloud needs order
        
        # Assuming treats match keys in CORES_PASTEL loosely?
        # If treat is "PURA", we mapped PURA -> N2 color.
        
        custom_raincloud(ax, valid, "Tratamento", 'IVG', treats, CORES_PASTEL, HATCHES)
        
        ax.set_xticks(range(len(treats)))
        axis_labels = [DISPLAY_MAP.get(lbl, lbl) for lbl in treats]
        ax.set_xticklabels(axis_labels, rotation=0)
        ax.set_ylabel("Germination Speed Index (GSI)", weight="bold")
        legend_order = [lbl for lbl in ["N1", "N2", "N3", "N4", "Control"] if lbl in [DISPLAY_MAP.get(x, x) for x in treats]]
        adicionar_legenda(ax, legend_order)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/Fig_005.png", dpi=300)
        plt.close()
        print("Gerado Fig_005.png (IVG)")
        
    except Exception as e:
        print(f"Erro em IVG: {e}")

if __name__ == "__main__":
    process_file_growth()
    process_file_ivg()
