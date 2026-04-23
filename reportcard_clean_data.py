import pandas as pd
from pathlib import Path
import os

# config
INPUT_FOLDER = "data/report_card"
OUTPUT_FOLDER = "data/cleaned_data/report_card"

# exact name of the district as it appears in the CSV
TARGET_DISTRICT = "Walla Walla Public Schools" 

def process_modern_ospi_data():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    input_path = Path(INPUT_FOLDER)
    
    csv_files = list(input_path.glob("*.csv")) + list(input_path.glob("*.CSV"))
    
    # The essential columns for longitudinal district demographic analysis
    columns_to_keep = [
        'SchoolYear', 
        'DistrictName', 
        'StudentGroupType',    # e.g., 'Gender', 'ELL', 'All'
        'StudentGroup',        # e.g., 'Female', 'English Language Learners', 'All Students'
        'GradeLevel', 
        'TestAdministration',  # SBAC vs AIM (Alternative)
        'TestSubject',         # ELA, Math
        'DAT',
        'Count of Students Expected to Test', # Your N-Size for weighted averages
        'Count of Students Expected to Test (included previously passed)',
        'Count Consistent Grade Level Knowledge And Above',
        'Percent Consistent Grade Level Knowledge And Above', # Proficiency Rate
        'PercentLevel1', 
        'PercentLevel2', 
        'PercentLevel3', 
        'PercentLevel4',
        'Percent Consistent Tested Only',
        'PercentNoScore',
        'PercentParticipation',
    ]

    for file_path in csv_files:
        print(f"Cleaning: {file_path.name}...")
        
        try:
            # Read the CSV (low_memory=False prevents mixed-type guessing errors)
            df = pd.read_csv(file_path, low_memory=False)
            
            # 1. Filter down to just District-level data (drops State and School rows)
            df = df[df['OrganizationLevel'] == 'District']
            
            # 2. Filter for your specific district
            # Using str.contains or exact match. Exact match is safer if you know the string.
            df = df[df['DistrictName'] == TARGET_DISTRICT]
            
            # 3. Filter for only ELA and Math (Drops Science, WIDA, etc.)
            if 'TestSubject' in df.columns:
                df = df[df['TestSubject'].isin(['ELA', 'Math'])]
                
            # 4. Keep only the columns we actually need
            # We do a list comprehension to avoid KeyErrors if a file is missing a column
            available_cols = [col for col in columns_to_keep if col in df.columns]
            df = df[available_cols]
            
            # 5. Clean up the Proficiency column (optional, but makes analysis easier)
            # Sometimes OSPI exports this as a string like "45.5%" or "< 5%". 
            # Leaving it as-is for now, but you will need to handle "< 5%" strings in your analytics model.

            # Save to output
            output_file = Path(OUTPUT_FOLDER) / f"{TARGET_DISTRICT.replace(' ', '_')}_CLEANED_{file_path.name}"
            df.to_csv(output_file, index=False)
            
            print(f"Success. Kept {len(df)} rows and {len(df.columns)} columns.\n")
            
        except Exception as e:
            print(f"error processing {file_path.name}: {e}\n")

if __name__ == "__main__":
    process_modern_ospi_data()