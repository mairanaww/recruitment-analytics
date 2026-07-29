import os
import logging
import click
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etl.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "recruitment")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")

DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

TABLE_CONFIGS = [
    {'name': 'departments', 'pk': ['department_id']},
    {'name': 'employees', 'pk': ['employee_id']},
    {'name': 'headcount_plan', 'pk': ['department_id', 'fiscal_period']},
    {'name': 'requisitions', 'pk': ['req_id']},
    {'name': 'candidates', 'pk': ['candidate_id']},
    {'name': 'applications', 'pk': ['application_id']},
    {'name': 'stage_events', 'pk': ['event_id']},
    {'name': 'offers', 'pk': ['offer_id']}
]

def get_engine():
    return create_engine(DATABASE_URL)

def upsert_dataframe(df: pd.DataFrame, table_name: str, engine, primary_keys: list):
    """
    Upsert a pandas DataFrame into a PostgreSQL table using ON CONFLICT DO UPDATE.
    """
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    if table_name not in metadata.tables:
        logger.error(f"Table {table_name} does not exist in the database.")
        return
        
    table = metadata.tables[table_name]
    
    # Convert DataFrame to list of dicts
    records = df.to_dict(orient='records')
    if not records:
        logger.info(f"No records to insert for {table_name}.")
        return

    stmt = insert(table).values(records)
    
    # Update all columns except the primary keys on conflict
    update_dict = {
        c.name: c
        for c in stmt.excluded
        if c.name not in primary_keys
    }
    
    if update_dict:
        stmt = stmt.on_conflict_do_update(
            index_elements=primary_keys,
            set_=update_dict
        )
    else:
        # If no other columns to update, just do nothing on conflict
        stmt = stmt.on_conflict_do_nothing(index_elements=primary_keys)
        
    with engine.begin() as conn:
        result = conn.execute(stmt)
        # SQLAlchemy doesn't return exact upsert counts easily, but we know it ran
        logger.info(f"Upserted {len(records)} records into {table_name}.")

@click.command()
@click.option('--data-dir', default='data/raw', help='Directory containing the raw CSV files.')
def run_etl(data_dir):
    """Run the ETL pipeline to load CSV files into PostgreSQL."""
    logger.info("Starting ETL process...")
    engine = get_engine()
    
    for config in TABLE_CONFIGS:
        table_name = config['name']
        pk = config['pk']
        csv_path = os.path.join(data_dir, f"{table_name}.csv")
        
        if not os.path.exists(csv_path):
            logger.warning(f"File {csv_path} not found. Skipping {table_name}.")
            continue
            
        logger.info(f"Processing {table_name}...")
        try:
            df = pd.read_csv(csv_path)
            # Basic validation
            if df.empty:
                logger.warning(f"File {csv_path} is empty.")
                continue
                
            # Date validation/conversion can be done here if needed.
            # Pandas mostly handles standard dates when inserting into sqlalchemy.
            
            upsert_dataframe(df, table_name, engine, pk)
            
        except Exception as e:
            logger.error(f"Error processing {table_name}: {str(e)}")
            
    logger.info("ETL process completed.")

if __name__ == '__main__':
    run_etl()
