import numpy as np
import pandas as pd
import os

# Create data directory
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def generate_ftir():
    # Wavenumber range
    wavenumbers = np.linspace(4000, 400, 1800)
    
    # Base transmittance (baseline around 95%)
    transmittance = 95 + np.random.normal(0, 0.2, len(wavenumbers))
    
    # Define peaks (center, width, depth)
    peaks = [
        (3400, 150, 40), # O-H stretch (broad)
        (2920, 30, 15),  # C-H aliphatic
        (2850, 30, 10),  # C-H aliphatic
        (1735, 20, 25),  # C=O acetyl/hemicellulose
        (1630, 20, 15),  # Absorbed water / interaction
        (1510, 20, 10),  # Aromatic skeletal (Lignin)
        (1425, 20, 12),  # CH2 bending
        (1240, 30, 20),  # C-O ether (Lignin/Hemicellulose)
        (1050, 50, 55),  # C-O stretch / C-C stretch (Cellulose/Hemicellulose - strong)
        (897, 15, 5),    # C-O-C (Amorphous cellulose)
    ]
    
    for center, width, depth in peaks:
        # Gaussian dip
        peak_shape = depth * np.exp(-((wavenumbers - center)**2) / (2 * width**2))
        transmittance -= peak_shape

    # Ensure no negative values (unlikely with this setup but good practice)
    transmittance = np.clip(transmittance, 0, 100)

    df = pd.DataFrame({'wavenumber': wavenumbers, 'transmittance': transmittance})
    output_path = os.path.join(DATA_DIR, 'ftir_typha.csv')
    df.to_csv(output_path, sep=';', decimal=',', index=False)
    print(f"Generated {output_path}")

def generate_tga():
    temp = np.linspace(25, 700, 700)
    mass = np.ones_like(temp) * 100
    
    # 1. Moisture loss (25-100 C)
    # Decay from 100 to 95%
    mask_moist = temp <= 120
    mass[mask_moist] = 100 - 5 * ((temp[mask_moist] - 25) / 95)
    mass[~mask_moist] = 95 # Set base after moisture
    
    # 2. Hemicellulose Degradation (shoulder around 220-300)
    # Using sigmoid function
    def sigmoid(x, L, x0, k):
        return L / (1 + np.exp(-k * (x - x0)))

    # Degrade from 95 down to ~70 (loss of 25) due to hemi + some cellulose start
    deg_hemi = sigmoid(temp, 25, 290, 0.05)
    mass -= deg_hemi
    
    # 3. Cellulose Degradation (main step around 330-380)
    # Degrade further down to ~30 (loss of 40)
    deg_cell = sigmoid(temp, 40, 360, 0.08)
    mass -= deg_cell
    
    # 4. Lignin Degradation (slow tail from 200 to 700)
    # Linear-ish drift
    deg_lignin = 10 * (temp / 700)
    mass -= deg_lignin
    
    # Add varying noise
    mass += np.random.normal(0, 0.05, len(temp))
    mass = np.clip(mass, 0, 100)
    
    # Calculate DTG (derivative)
    dtg = -np.gradient(mass, temp) * 10 # Scale for visibility
    
    df = pd.DataFrame({'temp': temp, 'mass': mass, 'dtg': dtg})
    output_path = os.path.join(DATA_DIR, 'tga_typha.csv')
    df.to_csv(output_path, sep=';', decimal=',', index=False)
    print(f"Generated {output_path}")

if __name__ == '__main__':
    generate_ftir()
    generate_tga()
