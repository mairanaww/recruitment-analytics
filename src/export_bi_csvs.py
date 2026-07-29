import pandas as pd
import os
import sys

# Ensure src modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.etl import get_engine

def export_bi_csvs():
    print("Connecting to database...")
    engine = get_engine()
    
    views = [
        'bi_dim_department',
        'bi_dim_stage',
        'bi_dim_source',
        'bi_dim_date',
        'bi_fact_applications',
        'bi_fact_headcount'
    ]
    
    export_dir = 'data/bi_export'
    os.makedirs(export_dir, exist_ok=True)
    
    print("Exporting BI views to CSV...")
    for view in views:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {view}", engine)
            out_path = os.path.join(export_dir, f"{view}.csv")
            df.to_csv(out_path, index=False)
            print(f"Exported {view} to {out_path}")
        except Exception as e:
            print(f"Error reading view {view}: {e}")

if __name__ == '__main__':
    export_bi_csvs()
