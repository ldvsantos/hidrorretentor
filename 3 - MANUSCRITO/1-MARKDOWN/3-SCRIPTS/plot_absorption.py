import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.patches as mpatches

# --- CONFIGURAÇÃO DE ESTILO (BASEADO EM GRAFICOS_ARTIGO_FINAL_ENGLISH.R) ---

DISPLAY_LABELS = {
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
    "FOLHA ": "N3"
}

LEGEND_DESCRIPTIONS = {
    "N1": "N1 (formulação completa)",
    "N2": "N2 (sem resina)",
    "N3": "N3 (resíduos vegetais)",
    "N4": "N4 (resíduos e fibras)",
    "Control": "Control"
}

# Configuração de Fonte e Eixos (Tema Clássico)
plt.rcParams.update({
    'font.size': 14,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Poppins', 'Arial', 'DejaVu Sans'],
    'axes.edgecolor': 'black',
    'axes.linewidth': 0.8,
    'axes.grid': False,
    'grid.color': '#E5E5E5',
    'grid.linewidth': 0.3, # Aparecerá apenas se grid() for chamado
    'axes.grid.axis': 'y',
    'legend.frameon': True,
    'legend.edgecolor': 'black',
    'legend.fancybox': False,
    'xtick.color': 'black',
    'ytick.color': 'black'
})

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

# --- PROCESSAMENTO DE DADOS ---
root = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/2 - DADOS"
file_path = root + "/PLANTULAS UMIDAS E SECAS PESAGEM GOURD FLOWER 21 E 22 FEVEREIRO .xlsx"

try:
    df = pd.read_excel(file_path)
    
    # Pivotagem
    pivot = (
        df.pivot_table(index=["VARIAVEL", "REP"], columns="ESTADO", values="QUANT.")
        .reset_index()
    )
    pivot["water_gain_g"] = pivot["UMIDA"] - pivot["SECAS"]
    
    # Filtragem (Remover valores negativos espúrios)
    filtered = pivot[pivot["water_gain_g"] > 0].copy()
    
    # Normaliza tratamentos (evita duplicata do controle e garante cores/hachuras únicas)
    filtered["Tratamento"] = filtered["VARIAVEL"].astype(str).str.strip().map(lambda v: DISPLAY_LABELS.get(v, v))
    filtered["Tratamento"] = filtered["Tratamento"].replace({"CONTROLE": "Control", "Controle": "Control"})

    # Summary stats por rótulo canônico
    summary = filtered.groupby("Tratamento", as_index=False)[["water_gain_g"]].agg(["mean", "std"])
    summary.columns = ["Tratamento", "mean", "std"]

    # --- PLOTAGEM ---
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Ordem desejada (somente canônicos)
    desired_order = ["N1", "N2", "N3", "N4", "Control"]
    plot_order = [t for t in desired_order if t in summary["Tratamento"].unique()]
    
    legend_labels = []
    legend_entries = []
    legend_labels = []
    tick_labels = []

    for i, treat in enumerate(plot_order):
        row = summary[summary["Tratamento"] == treat]
        if row.empty: continue
        
        val_mean = row["mean"].values[0]
        val_std = row["std"].values[0]
        
        color = CORES_PASTEL_N.get(treat, "#cccccc")
        hatch = HATCHES_N.get(treat, "")
        
        # Plot Bar
        bar = ax.bar(
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
        tick_labels.append(treat)
        legend_entries.append((bar.patches[0], treat, color, hatch))

    # Eixos e Legenda
    ax.set_xticks(range(len(plot_order)))
    ax.set_xticklabels(tick_labels, rotation=0)
    ax.set_ylabel("Ganho de massa hídrica (g)", color="black", weight='bold')
    ax.set_xlabel("", color="black") # X axis label redundant with ticks
    
    # Grid apenas horizontal
    ax.grid(axis='y', linestyle='-', color='gray', alpha=0.3)
    ax.set_axisbelow(True) # Grid atrás das barras

    # Legenda com descrições das formulações
    # Legenda estilo quadro
    legend_keys = []
    for _handle, key, _color, _hatch in legend_entries:
        if key not in legend_keys:
            legend_keys.append(key)

    legend_patches = []
    legend_labels = []
    for key in ["N1", "N2", "N3", "N4", "Control"]:
        if key not in legend_keys:
            continue
        legend_patches.append(
            mpatches.Patch(
                facecolor=CORES_PASTEL_N.get(key, "#cccccc"),
                edgecolor="black",
                hatch=HATCHES_N.get(key, ""),
            )
        )
        legend_labels.append(LEGEND_DESCRIPTIONS.get(key, key))

    if legend_patches:
        ax.legend(
            legend_patches,
            legend_labels,
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

    # Ajustes finais
    plt.tight_layout()
    
    output_path = "C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/2 - HIDRORRETENTOR/3 - MANUSCRITO/1-MARKDOWN/2-IMG/Fig_absorcao.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Figura atualizada com novo estilo salva em:", output_path)

except Exception as e:
    print(f"Erro ao processar figura: {e}")
