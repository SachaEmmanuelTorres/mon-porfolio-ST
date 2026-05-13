import pytest
import os
import sqlite3
import subprocess
import time
import sys

# Adjust path to import populate_db.py from v2/src
sys.path.insert(0, os.path.abspath('v2/src'))
import populate_db
sys.path.pop(0)

# Define the database path relative to the test script
TEST_DB_PATH = os.path.join('v2', 'explo.db')

@pytest.fixture(scope='session')
def setup_database():
    """Fixture to set up and tear down the database for all tests in the session."""
    # Ensure a clean database before any test runs
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    print(f"\n[DEBUG] Running populate_db.py from cwd: {os.getcwd()}/v2")
    print(f"[DEBUG] populate_db.py script path: {os.path.join('src', 'populate_db.py')}")
    print(f"[DEBUG] Expected DB path for tests: {TEST_DB_PATH}")

    try:
        result = subprocess.run([sys.executable, os.path.join("src", "populate_db.py")], check=True, cwd='v2', capture_output=True, text=True)
        print(f"[DEBUG] populate_db.py stdout:\n{result.stdout}")
        if result.stderr:
            print(f"[DEBUG] populate_db.py stderr:\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Error running populate_db.py during setup: {e.stderr}")
    
    if not os.path.exists(TEST_DB_PATH):
        pytest.fail(f"[DEBUG] Database file not found after populate_db.py execution: {TEST_DB_PATH}")
    else:
        print(f"[DEBUG] Database file found at: {TEST_DB_PATH}")

    yield # This is where the tests run

    # Teardown: Optionally remove the database after all tests
    # if os.path.exists(TEST_DB_PATH):
    #     os.remove(TEST_DB_PATH)

@pytest.fixture(scope='function')
def db_connection(setup_database):
    """Fixture to provide a database connection for each test function."""
    conn = sqlite3.connect(TEST_DB_PATH)
    yield conn
    conn.close()

@pytest.fixture(scope='function')
def db_cursor(db_connection):
    """Fixture to provide a database cursor for each test function."""
    cursor = db_connection.cursor()
    yield cursor
    cursor.close()

def test_db_connection(db_connection):
    """Test that the database connection can be established."""
    assert db_connection is not None, "Database connection should not be None."
    assert isinstance(db_connection, sqlite3.Connection), "Connection should be an sqlite3.Connection object."

def test_table_creation(db_cursor):
    """Test that all expected tables are created."""
    expected_tables = ['employees', 'customers', 'orders', 'people', 'products']
    db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in db_cursor.fetchall()]
    for table in expected_tables:
        assert table in tables, f"Table '{table}' should be created."

def test_data_population(db_cursor):
    """Test that tables are populated with data."""
    # Test employees table
    db_cursor.execute("SELECT COUNT(*) FROM employees;")
    assert db_cursor.fetchone()[0] > 0, "Employees table should have data."
    # Test customers table
    db_cursor.execute("SELECT COUNT(*) FROM customers;")
    assert db_cursor.fetchone()[0] > 0, "Customers table should have data."
    # Test orders table
    db_cursor.execute("SELECT COUNT(*) FROM orders;")
    assert db_cursor.fetchone()[0] > 0, "Orders table should have data."
    # Test people table
    db_cursor.execute("SELECT COUNT(*) FROM people;")
    assert db_cursor.fetchone()[0] > 0, "People table should have data."
    # Test products table
    db_cursor.execute("SELECT COUNT(*) FROM products;")
    assert db_cursor.fetchone()[0] == 6, "Products table should have 6 rows of data."

def test_check_constraint_products(db_connection, db_cursor):
    """Test that the CHECK(price > 0) constraint is enforced on products table."""
    # Attempt to insert a product with invalid price (should fail)
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        db_cursor.execute("INSERT INTO products (name, price) VALUES ('Invalid Product', 0.00);")
        db_connection.commit() # Commit to trigger the constraint check
    assert "CHECK constraint failed: price > 0" in str(excinfo.value)

    # Ensure the invalid product was not inserted
    db_cursor.execute("SELECT COUNT(*) FROM products WHERE name = 'Invalid Product';")
    assert db_cursor.fetchone()[0] == 0, "Invalid product should not be inserted."

class TestPerformance:

    def test_populate_db_performance(self):
        """Measure the execution time of populate_db.py."""
        # Ensure a clean database before running populate_db.py for performance measurement
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

        start_time = time.time()
        try:
            subprocess.run([sys.executable, populate_db.__file__], check=True, cwd='v2', capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            pytest.fail(f"populate_db.py failed during performance test: {e.stderr}")
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\npopulate_db.py execution time: {execution_time:.4f} seconds")
        # You can set a threshold here if needed, e.g., assert execution_time < 1.0