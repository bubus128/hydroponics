from datetime import timedelta, timezone
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
import datetime
address = Variable.get("RPI_IP", deserialize_json=False)
light_cycle_hours = Variable.get("daily_light_cycle", deserialize_json=True)
curr_phase_night_hour = light_cycle_hours[Variable.get("phase")]['OFF']
curr_phase_day_hour = light_cycle_hours[Variable.get("phase")]['ON']


args = {
    'owner': 'airflow',
}

def check_day_time():
    time_of_the_day = Variable.get("time_of_day")
    curr_hour = datetime.datetime.now().hour
    print(curr_hour)
    print(curr_phase_night_hour)
    print(curr_phase_day_hour)
    if time_of_the_day == "night" and curr_hour == int(curr_phase_day_hour):
        Variable.set("time_of_day", "day")
        r = requests.post(address + '/changeDayPhase', data ='day')
        return 'switch_on_lights'
    elif time_of_the_day == "day" and curr_hour == int(curr_phase_night_hour):
        Variable.set("time_of_day", "night")
        r = requests.post(address + '/changeDayPhase', data ='night')
        return 'switch_off_lights'
    return 'everything_is_ok'
	
def switch_off_lights():
    r = requests.post(address + '/light', data='off')
    return

def switch_on_lights():
    r = requests.post(address + '/light', data='on')
    return

	
with DAG(
    dag_id='airflow_light',
    default_args=args,
    catchup=False,
    schedule_interval='*/1 * * * *',
	max_active_runs=1,
    start_date=days_ago(0),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    check_day_time = BranchPythonOperator(
        task_id='check_day_time',
        python_callable=check_day_time
    )

    switch_on_lights = PythonOperator(
        task_id='switch_on_lights',
        python_callable=switch_on_lights
    )
    switch_off_lights = PythonOperator(
        task_id='switch_off_lights',
        python_callable=switch_off_lights
    )
	
    everything_is_ok = DummyOperator(
        task_id='everything_is_ok'
    )
	
check_day_time >> switch_on_lights
check_day_time >> switch_off_lights
check_day_time >> everything_is_ok

if __name__ == "__main__":
    dag.cli()