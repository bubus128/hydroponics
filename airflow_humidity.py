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
from airflow.models import Variable

address = ('https://1027f0e835e5.ngrok.io/')
amount_of_checks = 3
growth_min_value = 55
growth_max_value = 80
growth_avg_value = 70
flowering_min_value = 35 
flowering_max_value = 47
flowering_avg_value = 60


args = {
    'owner': 'airflow',
}

def measure_humidity():
    sum=0
    for i in range(amount_of_checks):
        r = requests.get(address + 'measure_humidity')
        sum+=int(r.text)
        sleep(5)
    sum/=amount_of_checks
    return sum

def check_humidity():
    if Variable.get("WHAT_PHASE_IT_IT") == "flowering":
        min_value = flowering_min_value
        max_value = flowering_max_value
    else:
        min_value = growth_min_value
        max_value = growth_max_value
    hum_value = measure_humidity()
    if hum_value < min_value:
        return 'low_humidity'
    if hum_value > max_value:
        return 'high_humidity'
    return 'normal_val'

def low_humidity():
    if Variable.get("WHAT_PHASE_IT_IT") == "flowering":
        avg_value = flowering_avg_value
    else:
        avg_value = growth_avg_value
    humidity_too_low = True
    while(humidity_too_low):
        r = requests.get(address + 'turn_on_atomizer')
        sleep(60)
        hum = measure_humidity()
        if hum >= avg_value:
            humidity_too_low = False

def high_humidity():
    if Variable.get("WHAT_PHASE_IT_IT") == "flowering":
        avg_value = flowering_avg_value
    else:
        avg_value = growth_avg_value
    humidity_too_high = True
    while(humidity_too_high):
        r = requests.get(address + 'turn_on_fan')
        sleep(60)
        hum = measure_humidity()
        if hum <= avg_value:
            humidity_too_high = False


with DAG(
    dag_id='airflow_humidity',
    default_args=args,
    catchup=False,
    schedule_interval='*/3 * * * *', #At every 3rd minute.
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    check_humidity = BranchPythonOperator(
        task_id='check_humidity',
        python_callable=check_humidity
    )

    low_humidity = PythonOperator(
        task_id='low_humidity',
        python_callable=low_humidity
    )

    high_humidity = PythonOperator(
        task_id='high_humidity',
        python_callable=high_humidity
    )

    normal_val = DummyOperator(
        task_id='normal_val'
    )

    humidity_increased = DummyOperator(
        task_id='humidity_increased'
    )

    humidity_decreased = DummyOperator(
        task_id='humidity_decreased'
    )


check_humidity >> low_humidity >> humidity_increased
check_humidity >> high_humidity >> humidity_decreased
check_humidity >> normal_val

if __name__ == "__main__":
    dag.cli()