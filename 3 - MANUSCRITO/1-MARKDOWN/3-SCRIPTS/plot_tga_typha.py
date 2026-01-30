import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Settings
HERE = Path(__file__).resolve().parent
IMG_DIR = HERE.parent / "2-IMG"
IMG_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = str(HERE / "data" / "tga_typha.csv")
OUTPUT_FILE = str(IMG_DIR / "Fig_TGA_Typha.png")
COLOR_TGA = '#2E86AB'
COLOR_DTG = '#D9534F'

def main():
    if not os.path.exists(DATA_FILE):
        print(f"File {DATA_FILE} not found. Please create it with columns: temp, mass, dtg (optional)")
        return

    # Load data (expecting CSV with 'temp', 'mass' %)
    try:
        df = pd.read_csv(DATA_FILE, sep=';', decimal=',')
        if df.shape[1] < 2:
            df = pd.read_csv(DATA_FILE, sep=',', decimal='.')
    except:
        df = pd.read_csv(DATA_FILE)
    
    # Rename columns if needed to standardized names
    if len(df.columns) >= 2:
        # Pega as duas primeiras colunas sempre
        df = df.iloc[:, :3] # Pega até 3 colunas
        cols = ['temp', 'mass']
        if df.shape[1] > 2:
            cols.append('dtg')
        df.columns = cols
    
    # Clean numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Plot TGA
    ax1.plot(df['temp'], df['mass'], color=COLOR_TGA, linewidth=2, label='TGA')
    ax1.set_xlabel('Temperature (°C)')
    ax1.set_ylabel('Mass Loss (%)', color=COLOR_TGA)
    ax1.tick_params(axis='y', labelcolor=COLOR_TGA)
    ax1.set_ylim(0, 110)
    
    # Plot DTG if available
    if 'dtg' in df.columns:
        ax2 = ax1.twinx()
        ax2.plot(df['temp'], df['dtg'], color=COLOR_DTG, linestyle='--', linewidth=1.5, label='DTG')
        ax2.set_ylabel('Mass Loss Derivative (%/°C)', color=COLOR_DTG)
        ax2.tick_params(axis='y', labelcolor=COLOR_DTG)
    
    # Annotate Thermal Stability (e.g., 285 C)
    target_temp = 285
    # Find closest temp
    if not df.empty:
        idx = (df['temp'] - target_temp).abs().idxmin()
        y_val = df.loc[idx, 'mass']
        
        ax1.annotate('Stability ~285°C', xy=(target_temp, y_val), xytext=(target_temp+50, y_val+10),
                    arrowprops=dict(facecolor='black', arrowstyle='->'))

    plt.title('Thermal Stability (TGA) - Typha Fibers')
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300)
    print(f"Figure saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
