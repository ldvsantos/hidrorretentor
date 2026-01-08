from pathlib import Path
import pandas as pd

fp = Path(r"C:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2 - HIDRORRETENTOR\2 - DADOS\TERMICO")
print("Exists:", fp.exists(), "Is file:", fp.is_file())
try:
    xls = pd.ExcelFile(fp)
    print("Sheets:", xls.sheet_names)
except Exception as exc:
    print("Failed to open as Excel:", exc)
    data = fp.read_bytes()[:128]
    print("First 128 bytes:", data)
