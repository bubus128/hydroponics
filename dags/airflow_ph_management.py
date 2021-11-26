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
ideal_ph = variables[Variable.get("phase")]['ph']["standard"]
hysteresis = variables[Variable.get("phase")]['ph']["hysteresis"]


args = {
    'owner': 'airflow',
}

def measure_ph():
    r = requests.get(address + '/ph')
    return float(r.text)

def check_ph():
    ph = measure_ph()
    if ph > ideal_ph + hysteresis:
        return 'lower_ph'
    elif ph < ideal_ph - hysteresis:
        return 'raise_ph'
    return 'everything_is_ok'
	
def raise_the_ph():
    r = requests.post(address + '/dose', data ='ph+')
    return

def lower_the_ph():
    r = requests.post(address + '/dose', data='ph-')
    return

def ok_ph():
    return
	
with DAG(
    dag_id='airflow_ph_management',
    default_args=args,
    catchup=False,
    schedule_interval='*/1 * * * *',
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    check_ph = BranchPythonOperator(
        task_id='check_ph',
        python_callable=check_ph
    )

    lower_ph = PythonOperator(
        task_id='lower_ph',
        python_callable=lower_the_ph
    )
    raise_ph = PythonOperator(
        task_id='raise_ph',
        python_callable=raise_the_ph
    )
	
    everything_is_ok = PythonOperator(
        task_id='everything_is_ok',
        python_callable=ok_ph
    )
	
check_ph >> lower_ph
check_ph >> raise_ph
check_ph >> everything_is_ok

if __name__ == "__main__":
    dag.cli()