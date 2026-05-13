import pytest
import os
import sqlite3
import time
import json
import subprocess
import sys
import pandas as pd # Import pandas for read_sql_query
import re # Import re for regex matching

# Adjust path to import populate_db.py from v2/src
sys.path.insert(0, os.path.abspath('v2/src'))
import populate_db
sys.path.pop(0)

# Define paths
V2_DIR = "v2"
NOTEBOOK_PATH = os.path.join(V2_DIR, "src", "exercices_SQL.ipynb")
TEST_DB_PATH = os.path.join(V2_DIR, "explo.db")

@pytest.fixture(scope='session')
def setup_notebook_performance_db():
    """Fixture to set up the database for notebook performance tests."""
    # Ensure a clean database before any test runs
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # Run populate_db.py to set up the database
    print("\nEnsuring fresh database state by running populate_db.py for notebook performance test...")
    try:
        subprocess.run([sys.executable, populate_db.__file__], check=True, cwd='v2', capture_output=True, text=True)
        print("populate_db.py executed successfully for performance test.")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Error running populate_db.py during setup for performance test: {e.stderr}")

    yield # This is where the tests run

@pytest.fixture(scope='function')
def notebook_db_connection(setup_notebook_performance_db):
    """Fixture to provide a database connection for each test function."""
    conn = sqlite3.connect(TEST_DB_PATH)
    yield conn
    conn.close()

def test_notebook_sql_execution_performance(notebook_db_connection):
    """
    Measures the total execution time of SQL queries extracted from the Jupyter notebook.
    """
    total_execution_time = 0
    executed_queries_count = 0

    if not os.path.exists(NOTEBOOK_PATH):
        pytest.fail(f"Error: Notebook not found at {NOTEBOOK_PATH}")

    with open(NOTEBOOK_PATH, 'r') as f:
        notebook_content = json.load(f)

    conn = notebook_db_connection # Use the fixture provided connection
    cursor = conn.cursor()

    print(f"\nMeasuring performance of notebook SQL queries from: {NOTEBOOK_PATH}")

    for cell in notebook_content['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            
            # Skip %pip install, %load_ext, %config, !python commands
            if source.strip().startswith(('%pip', '%load_ext', '%config', '!python')):
                continue

            # Handle %%sql magic
            if source.strip().startswith('%%sql'):
                sql_query = source.replace('%%sql', '', 1).strip()
                # Remove comments
                sql_query = '\n'.join([line for line in sql_query.split('\n') if not line.strip().startswith('--')])
                
                if sql_query:
                    start_time = time.time()
                    try:
                        cursor.execute(sql_query)
                        conn.commit()
                        # If it's a SELECT, fetch results (but don't print to avoid clutter)
                        if sql_query.strip().upper().startswith('SELECT'):
                            cursor.fetchall()
                        print(f"  Executed SQL (%%sql): {sql_query.splitlines()[0]}... Time: {(time.time() - start_time):.4f}s")
                        executed_queries_count += 1
                    except sqlite3.Error as e:
                        pytest.fail(f"  Error executing SQL (%%sql): {sql_query.splitlines()[0]}... Error: {e}")
                    total_execution_time += (time.time() - start_time)

            # Handle pandas.read_sql_query
            elif 'pd.read_sql_query' in source:
                # This is a simplified extraction. A robust solution would parse Python code.
                # For this specific notebook, we know the pattern.
                # Extract the query string from the source code
                query_match = re.search(r'query\s*=\s*"""(.*?)"""|query\s*=\s*"(.*?)"|query\s*=\s*\'(.*?)\'', source, re.DOTALL)
                if query_match:
                    sql_query = query_match.group(1) or query_match.group(2) or query_match.group(3)
                    if sql_query:
                        start_time = time.time()
                        try:
                            # Execute the query using pandas directly
                            pd.read_sql_query(sql_query, conn)
                            print(f"  Executed SQL (pandas): {sql_query.splitlines()[0]}... Time: {(time.time() - start_time):.4f}s")
                            executed_queries_count += 1
                        except Exception as e:
                            pytest.fail(f"  Error executing SQL (pandas): {sql_query.splitlines()[0]}... Error: {e}")
                        total_execution_time += (time.time() - start_time)

    print(f"\n======================================================================")
    print(f"SUMMARY: {executed_queries_count} SQL queries extracted and executed from notebook.")
    print(f"TOTAL SQL EXECUTION TIME FROM NOTEBOOK: {total_execution_time:.4f} seconds")
    print(f"======================================================================")
    assert executed_queries_count > 0, "No SQL queries were extracted and executed from the notebook."