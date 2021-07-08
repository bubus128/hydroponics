from datetime import timedelta
import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.dates import days_ago
from airflow.providers.postgres.operators.postgres import PostgresOperator
import requests
from time import sleep


date = datetime.datetime.now()
current_day = date.strftime("%d")
address = ('https://1027f0e835e5.ngrok.io/')

args = {
    'owner': 'airflow',
}

def is_filtering_done():
    r = requests.get(address + 'is_filtering_done')
    if r.text == "yes":
        return True
    return False

def start_filtering():
    #TODO SUSPEND DAGS: PH, TDS, WATER MEASURING
    r = requests.get(address + 'start_filtering')
    water_is_filtering = True
    while(water_is_filtering):
        sleep(300)
        if(is_filtering_done):
            water_is_filtering = False
    #TODO UNSUSPEND UPPER DAGS



with DAG(
    dag_id='airflow_filtering',
    default_args=args,
    catchup=False,
    schedule_interval='0 0 ' + str(current_day) + ' */1 *', #At 00:00 on day-of-month (current-day-1) in every month.
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    start_filtering = PythonOperator(
        task_id='start_filtering',
        python_callable=start_filtering
    )

    filtering_done = DummyOperator(
        task_id='filtering_done',
    )

start_filtering >> filtering_done

if __name__ == "__main__":
    dag.cli()