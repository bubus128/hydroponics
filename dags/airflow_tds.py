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
ideal_tds = variables[Variable.get("phase")]['tds']["standard"]
hysteresis = variables[Variable.get("phase")]['tds']["hysteresis"]
fertilizer_dosing = False


args = {
    'owner': 'airflow',
}

def measure_tds():
    r = requests.get(address + '/tds')
    return float(r.text)

def check_tds():
    tds = measure_tds()
    tds_limit = ideal_tds if fertilizer_dosing else ideal_tds - hysteresis
    if tds > ideal_tds + hysteresis:
        return 'lower_tds'
    elif tds < tds_limit:
        return 'raise_tds'
    return 'everything_is_ok'
	
def raise_the_tds():
    r = requests.post(address + '/dose', data = "fertilizer")
    fertilizer_dosing = True
    return

def lower_the_tds():
    return

def ok_tds():
    fertilizer_dosing = False
    return
	
with DAG(
    dag_id='airflow_tds',
    default_args=args,
    catchup=False,
    schedule_interval='*/1 * * * *',
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    check_tds = BranchPythonOperator(
        task_id='check_tds',
        python_callable=check_tds
    )

    lower_tds = PythonOperator(
        task_id='lower_tds',
        python_callable=lower_the_tds
    )
    raise_tds = PythonOperator(
        task_id='raise_tds',
        python_callable=raise_the_tds
    )
	
    everything_is_ok = PythonOperator(
        task_id='everything_is_ok',
        python_callable=ok_tds
    )
	
check_tds >> lower_tds
check_tds >> raise_tds
check_tds >> everything_is_ok

if __name__ == "__main__":
    dag.cli()