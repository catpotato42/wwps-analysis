import pandas as pd
import glob
import re
from pathlib import Path

DATA_DIR = Path("data")

def extract_year(fname):
    m = re.search(r'(\d{4})-(\d{2})', fname)
    if not m:
        return None
    start = int(m.group(1))
    end = int(m.group(2))
    if end < 100:
        end += 2000
    return start, end

def load_all():
    files = glob.glob(str(DATA_DIR / "*.csv"))
    dfs = []

    for f in files:
        yr = extract_year(f)
        if not yr or yr[0] < 2015:
            continue

        df = pd.read_csv(
            f,
            na_values=["NULL"],
            low_memory=False  # removes DtypeWarning
        )

        df["YearStart"] = yr[0]
        df["YearEnd"] = yr[1]
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)

def clean_percent(col):
    return pd.to_numeric(
        col.astype(str)
        .str.replace('%', '', regex=False)
        .str.replace('<', '', regex=False)
        .str.replace(r'[^0-9.\-]', '', regex=True),  # removes things like 'N10'
        errors="coerce"  # invalid → NaN instead of crash
    )

df = load_all()

df = df[
    (df["TestSubject"] == "Math") &
    (df["TestAdministration"] == "SBAC")
]

percent_cols = [
    "PercentMetStandard",
    "PercentLevel1",
    "PercentLevel2",
    "PercentLevel3",
    "PercentLevel4",
    "PercentParticipation"
]

for c in percent_cols:
    if c in df.columns:
        df[c] = clean_percent(df[c])

result = (
    df.groupby("YearStart")["PercentMetStandard"]
    .mean()
    .sort_index()
)

print(result)