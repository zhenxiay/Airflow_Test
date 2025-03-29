from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.sqlserver.operators.sqlserver import MsSqlOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import io
import requests

def insert_dataframe_to_sql(**kwargs):
    import json
    import pyodbc

    df = pd.read_html('https://www.basketball-reference.com/leagues/NBA_2025.html_per_game')[0]

    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server;DATABASE=your_database;UID=your_user;PWD=your_password' #replace with your credentials
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    for index, row in df.iterrows():
        columns = ', '.join(f'[{col}]' for col in df.columns)
        placeholders = ', '.join('?' for _ in df.columns)
        values = tuple(row.values)
        sql = f"INSERT INTO your_table ({columns}) VALUES ({placeholders})" # Replace with your table name
        cursor.execute(sql, values)

    conn.commit()
    conn.close()


with DAG(
    dag_id='html_to_sql_server',
    schedule_interval=None,  # Or a cron schedule, e.g., '0 0 * * *'
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:

    insert_to_sql_server = PythonOperator(
        task_id='insert_to_sql_server',
        python_callable=insert_dataframe_to_sql,
        provide_context=True,
    )

    insert_to_sql_server