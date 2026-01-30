import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Settings
HERE = Path(__file__).resolve().parent
IMG_DIR = HERE.parent / "2-IMG"
IMG_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = str(HERE / "data" / "ftir_typha.csv")
OUTPUT_FILE = str(IMG_DIR / "Fig_FTIR_Typha.png")
COLOR = '#1B998B'

def main():
    if not os.path.exists(DATA_FILE):
        print(f"File {DATA_FILE} not found. Please create it with columns: wavenumber, transmittance. (CSV sep=; or ,)")
        return

    # Load data (expecting CSV with 'wavenumber' and 'transmittance')
    # Try different separators if needed
    try:
        # Padrão comum em instrumentos: sep=; decimal=, ou sep=, decimal=.
        # Tentativa 1: Ponto e vírgula
        df = pd.read_csv(DATA_FILE, sep=';', decimal=',')
        if df.shape[1] < 2:
             df = pd.read_csv(DATA_FILE, sep=',', decimal='.')
    except:
        df = pd.read_csv(DATA_FILE)
    
    # Check columns
    # Se não tiver cabeçalho, assume col 0 = wavenumber, col 1 = trasmittance
    if 'wavenumber' not in df.columns or 'transmittance' not in df.columns:
        df.columns = ['wavenumber', 'transmittance'] + list(df.columns[2:])

    # Force numeric
    df['wavenumber'] = pd.to_numeric(df['wavenumber'], errors='coerce')
    df['transmittance'] = pd.to_numeric(df['transmittance'], errors='coerce')
    df = df.dropna()

    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(df['wavenumber'], df['transmittance'], color=COLOR, linewidth=1.5)
    
    # Annotations based on manuscript
    annotations = [
        (3300, '3300\nO-H'),
        (2920, '2920\nC-H'),
        (1735, '1735\nC=O'),
        (1600, '1600\nAr'),
    ]
    
    for wave, label in annotations:
        # Find closest point
        closest_idx = (df['wavenumber'] - wave).abs().idxmin()
        y_val = df.loc[closest_idx, 'transmittance']
        
        ax.annotate(label, xy=(wave, y_val), xytext=(wave, y_val + 5),
                    arrowprops=dict(facecolor='black', arrowstyle='->'),
                    ha='center')

    ax.set_xlim(4000, 400)
    ax.set_xlabel('Wavenumber ($cm^{-1}$)')
    ax.set_ylabel('Transmittance (%)')
    ax.set_title('FTIR - Typha domingensis Fibers')
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300)
    print(f"Figure saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
