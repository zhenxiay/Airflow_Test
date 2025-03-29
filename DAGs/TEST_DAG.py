from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import io
import psycopg2
from psycopg2 import extras
from sqlalchemy import create_engine

def extract_data_from_url(**kwargs):
    url = 'https://www.basketball-reference.com/leagues/NBA_2025_per_game.html'
    df = pd.html(url)[0]
    return df

def insert_data_to_postgres(**kwargs):
    engine = create_engine('postgresql://root:root@localhost:5432/postgres')
    engine.connect()

    df = extract_data_from_url()

    df.to_sql('per_game',
                con=engine,
                if_exists="replace", 
                schema='public')

with DAG(
    dag_id='ingest_data_to_postgres',
    schedule_interval=None,  # Or a cron schedule, e.g., '0 0 * * *'
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['postgres', 'ingestion', 'sql', 'python'],
) as dag:

    extract_data = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data_from_url,
        op_kwargs={'url': 'your_data_url.csv'}, #Replace with your data url
        provide_context=True,
    )

    insert_data = PythonOperator(
        task_id='insert_data',
        python_callable=insert_data_to_postgres,
        provide_context=True,
    )

    extract_data >> insert_data