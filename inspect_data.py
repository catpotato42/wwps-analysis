import pandas as pd
from pathlib import Path

# --- Configuration ---
# Replace this with the actual path to your folder containing the 2016-2025 CSVs
DATA_FOLDER = "data" 
# ---------------------

def inspect_csv_files(folder_path):
    folder = Path(folder_path)
    
    # Check if the folder exists
    if not folder.exists() or not folder.is_dir():
        print(f"Error: The directory '{folder_path}' does not exist.")
        return

    # Find all CSV files in the folder (case-insensitive)
    csv_files = list(folder.glob("*.csv")) + list(folder.glob("*.CSV"))
    
    if not csv_files:
        print(f"No CSV files found in '{folder_path}'.")
        return

    print(f"Found {len(csv_files)} CSV files. Inspecting...\n")
    print("=" * 60)

    for file_path in csv_files:
        print(f"\n FILE: {file_path.name}")
        
        try:
            df = pd.read_csv(file_path, nrows=5)
            
            print("\nCOLUMNS:")
            print(df.columns.tolist())
            
            print("\nDATA PREVIEW:")
            print(df.head().to_string(index=False)) 
            
        except Exception as e:
            print(f"\error reading {file_path.name}: {e}")
            
        print("\n" + "=" * 60)

if __name__ == "__main__":
    inspect_csv_files(DATA_FOLDER)