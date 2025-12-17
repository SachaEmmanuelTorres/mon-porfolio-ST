
import sqlite3
from constants import DB_NAME


def execute_sql_commands(queries: list[str]):
    """_summary_

    Args:
        queries (list[str]): queries list
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        for command in queries:
            print(f"Executing: {command.strip()}")
            cursor.execute(command)
        conn.commit()
        print("All commands executed successfully.")
        print(f"Database populated and saved to {DB_NAME}.")
        print("You can now run sql queries in notebook  to test your queries.")  
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    sql_commands = [
        """
        DROP TABLE IF EXISTS employees;
        """,
        """
        DROP TABLE IF EXISTS customers;
        """,
        """
        DROP TABLE IF EXISTS orders;
        """,
        """
        DROP TABLE IF EXISTS people;
        """,
        """
        DROP TABLE IF EXISTS products;
        """,
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
        """,
        """
        INSERT INTO employees (name, department) VALUES ('Albert', 'HR'), ('Bob', 'Engineering'), ('Charlie', 'Sales');
        """,
        """
        INSERT INTO employees (name, department) VALUES ('David', 'HR'), ('Eve', 'Finances'), ('Frank', 'Sales');
        """,
        """
        INSERT INTO employees (name, department) VALUES ('Grace', 'HR'), ('Heidi', 'Finances'), ('Ivan', 'Sales');
        """,
        """
        UPDATE employees
        SET name = 'Sacha'
        WHERE name = 'Albert' AND department = 'HR';
        """,
        """
        DELETE FROM employees
        WHERE name = 'Sacha';
        """,
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """,
        """
        INSERT INTO customers (id, name) VALUES
        (10, 'Customer A'),
        (11, 'Customer B'),
        (12, 'Customer C'),
        (13, 'Customer D'),
        (14, 'Customer E'),
        (15, 'Customer F'),
        (16, 'Customer G'),
        (17, 'Customer H'),
        (18, 'Customer I');
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
        """,
        """
        INSERT INTO orders (order_id, customer_id) VALUES
        (1, 10),
        (2, 10),
        (3, 14),
        (4, 14),
        (5, 14),
        (6, 16),
        (7, 16),
        (8, 18),
        (9, 18);
        """,
        """
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            fatherId INTEGER,
            motherId INTEGER,
            age INTEGER
        );
        """,
        """
        INSERT INTO people (id, name, fatherId, motherId, age) VALUES
        (1, 'John', NULL, NULL, 40),
        (2, 'Jane', NULL, NULL, 38),
        (3, 'Alice', 1, 2, 10),
        (4, 'Bob', 1, 2, 12),
        (5, 'Michael', NULL, NULL, 45),
        (6, 'Sarah', NULL, NULL, 42),
        (7, 'Emma', 5, 6, 8),
        (8, 'Liam', 5, 6, 6);
        """,
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL CHECK(price > 0)
        );
        """,
        """
        INSERT INTO products (name, price) VALUES ('Laptop', 1200.00);
        """,
        """
        INSERT INTO products (name, price) VALUES ('Mouse', 25.50);
        """,
        """
        INSERT INTO products (name, price) VALUES ('Monitor', 300.00);
        """,
        """
        INSERT INTO products (name, price) VALUES ('Webcam', 50.00);
        """,
        """
        INSERT INTO products (name, price) VALUES ('Headphones', 75.00);
        """,
        """
        INSERT INTO products (name, price) VALUES ('Microphone', 100.00);
        """
    ]
    execute_sql_commands(sql_commands)
