import pandas as pd
import statsmodels.formula.api as smf
from pathlib import Path
import glob

# --- Configuration ---
INPUT_FOLDER = "data/cleaned_data/report_card"
# ---------------------

def run_longitudinal_regression():
    # 1. Load all cleaned CSVs into one master DataFrame
    all_files = glob.glob(f"{INPUT_FOLDER}/WWPS_*.csv")
    if not all_files:
        print("No CSV files found.")
        return
        
    df = pd.concat([pd.read_csv(f, low_memory=False) for f in all_files], ignore_index=True)

    # 2. Data Type Cleaning
    # Extract the starting year to use as our continuous 'Time' variable (e.g., '2015-16' -> 2015)
    df['Year'] = df['SchoolYear'].str[:4].astype(float)
    
    # Strip any potential '%' signs and force the column to numeric. 
    # errors='coerce' turns 'N<10', 'No Students', and '<5%' into standard NaNs.
    if df['PercentMetStandard'].dtype == object:
        df['PercentMetStandard'] = df['PercentMetStandard'].str.replace('%', '', regex=False)
    
    df['PercentMetStandard'] = pd.to_numeric(df['PercentMetStandard'], errors='coerce')

    # 3. Filter for our "Apples-to-Apples" Model Data
    # We only want the general student population taking the standard test.
    model_data = df[
        (df['StudentGroup'] == 'All Students') & 
        (df['TestAdministration'] == 'SBAC')   # Ignore AIM/WA-AIM to prevent skew
    ].copy()

    # Drop rows where we don't have a proficiency score (the suppressed N<10 rows)
    model_data = model_data.dropna(subset=['PercentMetStandard', 'Year']) #TODO: ERROR IT'S SUPPOSED TO BE PercentMetTestedOnly

    if model_data.empty:
        print("Error: No data left after filtering for SBAC and All Students.")
        return

    # 4. The Regression Model
    # We are modeling Proficiency as a function of Year, controlling for Subject and GradeLevel.
    # C() tells statsmodels to treat Subject and GradeLevel as categorical variables.
    formula = "PercentMetStandard ~ Year + C(TestSubject) + C(GradeLevel)"
    
    print("Fitting OLS Regression Model...")
    print(f"Formula: {formula}")
    print(f"N = {len(model_data)} observations\n")
    
    model = smf.ols(formula, data=model_data).fit()
    
    # Print the academic summary
    print(model.summary())

if __name__ == "__main__":
    run_longitudinal_regression()