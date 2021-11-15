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
pH_upper_limit = 6.5
pH_lower_limit = 4.9
pH_middle_value = 5.7

args = {
    'owner': 'airflow',
}

def measure_pH():
    sum = 0
    for i in range(amount_of_checks):
        r = requests.get(address + 'pH_level')
        if(int(r.text)>100):
            exit(1)
        sum += int(r.text)
        sleep(300)
    sum /= amount_of_checks
    return sum

def check_pH():
    ph = measure_pH()
    if ph >= pH_upper_limit:
        return 'pH_too_high'
    elif ph <= pH_lower_limit:
        return 'pH_too_low'
    return 'pH_is_good'

def lower_the_pH():
    pH_is_too_high = True
    while(pH_is_too_high):
        r = requests.get(address + 'add_pH_minus')
        sleep(600)
        if(measure_pH()<=pH_middle_value):
            pH_is_too_high = False


def raise_the_pH():
    pH_is_too_low = True
    while(pH_is_too_low):
        r = requests.get(address + 'add_pH_plus')
        sleep(600)
        if(measure_pH()>=pH_middle_value):
            pH_is_too_low = False

	
with DAG(
    dag_id='airflow_ph_managment',
    default_args=args,
    catchup=False,
    schedule_interval='0 */8 * * *', #At minute 0 past every 8th hour.
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    check_pH = BranchPythonOperator(
        task_id='check_pH',
        python_callable=check_pH
    )

    pH_too_high = PythonOperator(
        task_id='pH_too_high',
        python_callable=lower_the_pH
    )
    pH_too_low = PythonOperator(
        task_id='pH_too_low',
        python_callable=raise_the_pH
    )

    pH_is_good = DummyOperator(
        task_id='pH_is_good'
    )

check_pH >> pH_too_high
check_pH >> pH_too_low
check_pH >> pH_is_good

if __name__ == "__main__":
    dag.cli()