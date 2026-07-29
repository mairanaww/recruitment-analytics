import pytest
import pandas as pd
from sqlalchemy import text
from src.etl import get_engine, upsert_dataframe
import os
import uuid

@pytest.fixture(scope="module")
def engine():
    return get_engine()

def test_idempotency(engine):
    """
    Tests that the upsert logic correctly inserts a new row,
    does not duplicate it on a second run, and correctly updates
    a modified field on a third run.
    """
    table_name = 'candidates'
    pk = ['candidate_id']
    test_id = f"TEST-{str(uuid.uuid4())[:8]}"
    
    initial_data = [{
        'candidate_id': test_id,
        'name': 'John Doe',
        'email': 'john@example.com',
        'source': 'LinkedIn'
    }]
    df = pd.DataFrame(initial_data)
    
    # Run 1: Insert
    upsert_dataframe(df, table_name, engine, pk)
    
    with engine.connect() as conn:
        count1 = conn.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE candidate_id = :id"), {"id": test_id}).scalar()
        name1 = conn.execute(text(f"SELECT name FROM {table_name} WHERE candidate_id = :id"), {"id": test_id}).scalar()
        
    assert count1 == 1
    assert name1 == 'John Doe'
    
    # Run 2: Idempotent run (no changes)
    upsert_dataframe(df, table_name, engine, pk)
    
    with engine.connect() as conn:
        count_specific = conn.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE candidate_id = :id"), {"id": test_id}).scalar()
    
    # Assert it didn't duplicate
    assert count_specific == 1
    
    # Run 3: Modify a field
    modified_data = [{
        'candidate_id': test_id,
        'name': 'Jane Doe', # Changed name
        'email': 'john@example.com',
        'source': 'LinkedIn'
    }]
    df_modified = pd.DataFrame(modified_data)
    
    upsert_dataframe(df_modified, table_name, engine, pk)
    
    with engine.connect() as conn:
        count3 = conn.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE candidate_id = :id"), {"id": test_id}).scalar()
        name3 = conn.execute(text(f"SELECT name FROM {table_name} WHERE candidate_id = :id"), {"id": test_id}).scalar()
        
    assert count3 == 1
    assert name3 == 'Jane Doe'

    # Cleanup
    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM {table_name} WHERE candidate_id = :id"), {"id": test_id})
