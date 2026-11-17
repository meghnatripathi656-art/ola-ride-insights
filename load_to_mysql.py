"""Loads ola_clean.csv into MySQL table ola.ola_rides.
Keep this file and ola_clean.csv in the SAME folder, then run:  python load_to_mysql.py
"""
from getpass import getpass
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text

csv_path = Path(__file__).parent / "ola_clean.csv"
if not csv_path.exists():
    raise SystemExit(f"ola_clean.csv not found next to this script: {csv_path}")

password = getpass("MySQL root password (typing stays hidden): ")
engine = create_engine(f"mysql+pymysql://root:{quote_plus(password)}@localhost:3306/ola")

df = pd.read_csv(csv_path, parse_dates=["Date"])
print("Read", len(df), "rows from CSV")

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE ola_rides"))   # safe to re-run

df.to_sql("ola_rides", engine, if_exists="append", index=False, chunksize=5000)
print("Loaded", len(df), "rows into ola.ola_rides")
