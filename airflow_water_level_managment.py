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
amount_of_checks = 3
pH_upper_limit = 27
pH_lower_limit = 21
pH_middle_value = 24

args = {
    'owner': 'airflow',
}

def measure_water_level():
    r = requests.get(address + 'water_level')
    if r.text == "ok":
        return True
    return False

def add_water():
    r = requests.get(address + 'add_water')
    #TODO check velocity of adding water xd
    water_shortage = True
    while(water_shortage):
        if measure_water_level():
            water_shortage = False
            sleep(10)#how much additional water we want to add
    r = requests.get(address + 'stop_adding_water')


def check_water_level():
    if measure_water_level():
        return 'water_is_ok'
    return 'add_water'
	
with DAG(
    dag_id='airflow_water_level_managment',
    default_args=args,
    catchup=False,
    schedule_interval='0 */12 * * *', #At minute 0 past every 8th hour.
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    check_water_level = BranchPythonOperator(
        task_id='check_water_level',
        python_callable=check_water_level
    )

    add_water = PythonOperator(
        task_id='add_water',
        python_callable=add_water
    )

    water_is_ok = DummyOperator(
        task_id='water_is_ok',
    )


if __name__ == "__main__":
    dag.cli()