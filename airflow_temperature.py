from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.dates import days_ago
from airflow.providers.postgres.operators.postgres import PostgresOperator
import requests
from time import sleep

address = ('https://1027f0e835e5.ngrok.io/')

args = {
    'owner': 'airflow',
}

def measure_temp():
    sum=0
    r = requests.get(address + 'temperature')
    sum += int(r.text)
    sleep(5)
    r = requests.get(address + 'temperature')
    sum += int(r.text)
    sleep(5)
    r = requests.get(address + 'temperature')
    sum += int(r.text)
    if sum/3 > 1339:
        return 'temp_too_high'
    else:
        return 'temp_ok'

with DAG(
    dag_id='airflow_temperature',
    default_args=args,
    catchup=False,
    schedule_interval='*/1 * * * *',
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    tags=['example', 'example2'],
    params={"example_key": "example_value"},
) as dag:

    run_this_last = BranchPythonOperator(
        task_id='python',
        python_callable=measure_temp
    )

	
    temp_too_high = DummyOperator(
        task_id='temp_too_high'
    )
    temp_ok = DummyOperator(
        task_id='temp_ok'
    )
	
run_this_last >> [temp_too_high,temp_ok]

if __name__ == "__main__":
    dag.cli()