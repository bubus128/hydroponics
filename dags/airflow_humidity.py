from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import BranchPythonOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
from airflow.providers.postgres.operators.postgres import PostgresOperator
import requests
from time import sleep
import glob
import json

address = Variable.get("RPI_IP", deserialize_json=False)
variables = Variable.get("indication_limits", deserialize_json=True)
ideal_humidity = variables[Variable.get("phase")]["humidity"]["standard"]
hysteresis = variables[Variable.get("phase")]["humidity"]["hysteresis"]


args = {
    'owner': 'airflow',
}

def measure_humidity():
    r = requests.get(address + '/humidity')
    return float(r.text)

def check_humidity():
    humidity = measure_humidity()
    if humidity > ideal_humidity + hysteresis:
        return 'decrease_humidity'
    elif humidity < ideal_humidity - hysteresis:
        return 'increase_humidity'
    return 'ok_humidity'

def decrease_humidity():
    r = requests.post(address + '/manage/humidity/decrease')
    return

def increase_humidity():
    r = requests.post(address + '/manage/humidity/increase')
    return

def ok_humidity():
    r = requests.post(address + '/manage/humidity/remain')
    return


with DAG(
    dag_id='airflow_humidity',
    default_args=args,
    catchup=False,
    schedule_interval='*/1 * * * *',
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    check_humidity = BranchPythonOperator(
        task_id='check_humidity',
        python_callable=check_humidity
    )

    decrease_humidity = PythonOperator(
        task_id='decrease_humidity',
        python_callable=decrease_humidity
    )

    increase_humidity = PythonOperator(
        task_id='increase_humidity',
        python_callable=increase_humidity
    )

    ok_humidity = PythonOperator(
        task_id='ok_humidity',
        python_callable=ok_humidity
    )


check_humidity >> decrease_humidity
check_humidity >> increase_humidity
check_humidity >> ok_humidity

if __name__ == "__main__":
    dag.cli()