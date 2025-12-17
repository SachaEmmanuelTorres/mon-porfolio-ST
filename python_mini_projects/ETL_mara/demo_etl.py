import mara_pipelines.pipelines as pipelines
from mara_pipelines.commands.python import PythonCommand
from mara_pipelines.commands.sql import ExecuteSQL

import pandas as pd
import psycopg2


# 1. create extract + transform function
def extract_transform():
    """
    Extract data from CSV, filter and save to new CSV.
    """
    df = pd.read_csv("users.csv")
    df = df[df["age"].apply(lambda x: str(x).isdigit() and int(x) > 24)]  # filter
    df[["name", "city"]].to_csv("filtered_users.csv", index=False)
    print("Extract & Transform finished. Saved to filtered_users.csv")


# 2. Define load SQL
load_sql = """
COPY users(name, city)
FROM PROGRAM 'cat filtered_users.csv'
DELIMITER ',' CSV HEADER;
"""

# 3. Create Mara pipeline
pipeline = pipelines.Pipeline("demo_etl")
pipeline.add(PythonCommand("extract-transform", extract_transform))
pipeline.add(ExecuteSQL("load-to-postgres", load_sql, database="postgres"))
