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
import datetime

address = Variable.get("RPI_IP", deserialize_json=False)
limits = Variable.get("indication_limits", deserialize_json=True)


args = {
    'owner': 'airflow',
}

    
def check_day():
    day = Variable.get("day")
    day_of_phase = Variable.get("day_of_phase")
    day_of_the_month = Variable.get("day_of_the_month")
    phase = Variable.get("phase")
    if int(day_of_the_month) != datetime.datetime.today().day:
        new_days = int(int(day) + 1)
        Variable.set("day", str(new_days))
        Variable.set("day_of_phase", str(int(day_of_phase) + 1))
        Variable.set("day_of_the_month", str(datetime.datetime.today().day))
        days_limit = limits[phase]["days"]
        if int(day_of_phase) > int(days_limit):
             Variable.set("day_of_phase", str(0))
             if phase == "flowering":
                 print("there are no more steps")
             if phase == "growth":
                 phase = Variable.set("phase", "flowering")
             if phase == "resting":
                 phase = Variable.set("phase", "growth")
             r = requests.post(address + '/logData', data = phase)
    r = requests.post(address + '/logData')
    return
	

	
with DAG(
    dag_id='airflow_time',
    default_args=args,
    catchup=False,
    schedule_interval='*/1 * * * *',
	max_active_runs=1,
    start_date=days_ago(0),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    check_day = PythonOperator(
        task_id='check_day',
        python_callable=check_day
    )
	

if __name__ == "__main__":
    dag.cli()