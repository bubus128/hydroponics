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
temp_upper_limit = 27
temp_lower_limit = 21
temp_middle_value = 24

args = {
    'owner': 'airflow',
}

def measure_temp():
    sum=0
    for i in range(amount_of_checks):
        r = requests.get(address + 'temperature')
        sum += int(r.text)
        sleep(1)
    sum /= amount_of_checks
    return sum

def check_temp():
    temperature = measure_temp()
    print(temperature)
    if temperature >= temp_upper_limit:
        return 'lower_temperature'
    elif temperature <= temp_lower_limit:
        return 'raise_temperature'
    return 'everything_is_ok'
	
def raise_the_temperature():
    r = requests.get(address + 'turn_on_heater')
    raise_temperature = True
    while(raise_temperature):
        if(measure_temp() >= temp_middle_value):
            raise_temperature = False
        sleep(30)
    r = requests.get(address + 'turn_off_heater')

def lower_the_temperature():
    r = requests.get(address + 'turn_on_cooling')
    lower_temperature = True
    while(lower_temperature):
        if(measure_temp() <= temp_middle_value):
            lower_temperature = False
        sleep(30)
    r = requests.get(address + 'turn_off_cooling')
	
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
	
    everything_is_ok = DummyOperator(
        task_id='everything_is_ok'
    )
	
check_temp >> lower_temperature
check_temp >> raise_temperature
check_temp >> everything_is_ok

if __name__ == "__main__":
    dag.cli()