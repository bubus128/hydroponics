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
ideal_temperatere = variables[Variable.get("phase")]["temperature"][Variable.get("time_of_day")]["standard"]
hysteresis = variables[Variable.get("phase")]["temperature"][Variable.get("time_of_day")]["hysteresis"]


args = {
    'owner': 'airflow',
}

def measure_temp():
    r = requests.get(address + '/temperature')
    return float(r.text)

def check_temp():
    temperature = measure_temp()
    if temperature > ideal_temperatere + hysteresis:
        return 'lower_temperature'
    elif temperature < ideal_temperatere:
        return 'raise_temperature'
    return 'everything_is_ok'
	
def raise_the_temperature():
    r = requests.post(address + '/temperature', data = 'increase')
    return

def lower_the_temperature():
    r = requests.post(address + '/temperature', data = 'decrease')
    return

def ok_temperature():
    r = requests.post(address + '/temperature', data = 'remain')
    return
	
with DAG(
    dag_id='airflow_temperature',
    default_args=args,
    catchup=False,
    schedule_interval='*/1 * * * *',
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    check_temp = BranchPythonOperator(
        task_id='check_temp',
        python_callable=check_temp
    )

	
    lower_temperature = PythonOperator(
        task_id='lower_temperature',
        python_callable=lower_the_temperature
    )
    raise_temperature = PythonOperator(
        task_id='raise_temperature',
        python_callable=raise_the_temperature
    )
	
    everything_is_ok = PythonOperator(
        task_id='everything_is_ok',
        python_callable=ok_temperature
    )
	
check_temp >> lower_temperature
check_temp >> raise_temperature
check_temp >> everything_is_ok

if __name__ == "__main__":
    dag.cli()