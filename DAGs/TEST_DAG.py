from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.sqlserver.operators.sqlserver import MsSqlOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import io
import requests

def extract_html_to_dataframe(**kwargs):
    url = kwargs['url']
    response = requests.get(url)
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    dfs = pd.read_html(io.StringIO(response.text)) # pandas reads all tables in the html
    if dfs:
        return dfs[0].to_json(orient='records') #Return the first table as json
    else:
        raise ValueError(f"No tables found at {url}")

def insert_dataframe_to_sql(**kwargs):
    import json
    import pyodbc
    ti = kwargs['ti']
    data_json = ti.xcom_pull(task_ids='extract_html_data', key='return_value')
    data = json.loads(data_json)
    df = pd.DataFrame(data)

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
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:
    http_sensor = HttpSensor(
        task_id='http_sensor_task',
        http_conn_id='http_default', #Ensure this connection is set in Airflow UI
        endpoint='your_html_page.html', #e.g. /data.html or index.html
        response_check=lambda response: "<table>" in response.text, #checks for table tag
        poke_interval=5,
        timeout=20,
    )

    extract_html_data = PythonOperator(
        task_id='extract_html_data',
        python_callable=extract_html_to_dataframe,
        op_kwargs={'url': 'http://your_website/your_html_page.html'}, #full URL
        provide_context=True,
    )

    insert_to_sql_server = PythonOperator(
        task_id='insert_to_sql_server',
        python_callable=insert_dataframe_to_sql,
        provide_context=True,
    )

    http_sensor >> extract_html_data >> insert_to_sql_server