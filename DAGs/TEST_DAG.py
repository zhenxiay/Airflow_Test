from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import requests
import io
import psycopg2
from psycopg2 import extras

def extract_data_from_url(**kwargs):
    url = kwargs['url']
    response = requests.get(url)
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    df = pd.read_csv(io.StringIO(response.text))
    return df.to_json(orient='records')

def insert_data_to_postgres(**kwargs):
    import json
    ti = kwargs['ti']
    data_json = ti.xcom_pull(task_ids='extract_data')
    data = json.loads(data_json)
    df = pd.DataFrame(data)

    conn_string = "host=your_host dbname=your_dbname user=your_user password=your_password" #replace with your credentials
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    tuples = [tuple(x) for x in df.to_numpy()]
    cols = ','.join(list(df.columns))

    query = "INSERT INTO %s(%s) VALUES %%s" % ('your_table', cols) #replace with your table name
    extras.execute_values(cursor, query, tuples)

    conn.commit()
    cursor.close()
    conn.close()

with DAG(
    dag_id='ingest_data_to_postgres',
    schedule_interval=None,  # Or a cron schedule, e.g., '0 0 * * *'
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['postgres', 'ingestion'],
) as dag:

    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default', #Ensure this connection is set in Airflow UI
        sql="""
            CREATE TABLE IF NOT EXISTS your_table (
                col1 VARCHAR,
                col2 INTEGER,
                col3 DATE
                -- Add more columns as needed
            );
        """,
    )

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

    create_table >> extract_data >> insert_data