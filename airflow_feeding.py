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

address = ('https://3d2e88aee6d7.ngrok.io/')
amount_of_checks = 3
growth_min_value = 600
growth_max_value = 950
growth_avg_value = 800
flowering_min_value = 850
flowering_max_value = 1250
flowering_avg_value = 1100
tds_per_ml = 12.5

args = {
    'owner': 'airflow',
}

def measure_tds():
    sum=0
    for i in range(amount_of_checks):
        r = requests.get(address + 'measure_tds')
        sum+=int(r.text)
        sleep(5)
    sum/=amount_of_checks
    return sum


def growth_phase():
    tds_value = measure_tds()
    if tds_value < growth_min_value:
        return 'deficiency_of_minerals'
    if tds_value > flowering_max_value:
        return 'excess_of_minerals'
    return 'normal_value'
    

def check_tds():
    if Variable.get("WHAT_PHASE_IT_IT") == "flowering":
        min_value = flowering_min_value
        max_value = flowering_max_value
    else:
        min_value = growth_min_value
        max_value = growth_max_value
    tds_value = measure_tds()
    if tds_value < min_value:
        return 'deficiency_of_minerals'
    if tds_value > max_value:
        return 'excess_of_minerals'
    return 'normal_val'

def deficiency_of_minerals():
    if Variable.get("WHAT_PHASE_IT_IT") == "flowering":
        min_value = flowering_min_value
    else:
        min_value = growth_min_value
    for i in range(amount_of_checks):
        sleep(600)
        if measure_tds() > min_value:
            return 'normal_value'
    return 'dose_fertilizer'
    
def excess_of_minerals():
    if Variable.get("WHAT_PHASE_IT_IT") == "flowering":
        max_value = flowering_max_value
    else:
        max_value = growth_max_value
    for i in range(amount_of_checks):
        sleep(600)
        if measure_tds() > max_value:
            return 'alarm_system'
    return 'normal_value'

def alarm_system():
    print("ERROR")

def dose_fertilizer():
    if Variable.get("WHAT_PHASE_IT_IT") == "flowering":
        avg_value = flowering_avg_value
    else:
        avg_value = growth_avg_value
    tds_value = measure_tds()
    amt_of_dose = (avg_value-tds_value)/tds_per_ml
    #TODO ogarnac jak sie dozuje to gowno
    #for i in range(amt_of_dose):
    #    r = requests.get(address + 'add_fertilizer')

with DAG(
    dag_id='airflow_feeding',
    default_args=args,
    catchup=False,
    schedule_interval='0 */12 * * *', #At minute 0 past every 24th hour.
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    check_tds = BranchPythonOperator(
        task_id='check_tds',
        python_callable=check_tds
    )

    deficiency_of_minerals = BranchPythonOperator(
        task_id='deficiency_of_minerals',
        python_callable=deficiency_of_minerals
    )

    alarm_system = PythonOperator(
        task_id='alarm_system',
        python_callable=alarm_system
    )

    dose_fertilizer = PythonOperator(
        task_id='dose_fertilizer',
        python_callable=dose_fertilizer
    )

    excess_of_minerals = BranchPythonOperator(
        task_id='excess_of_minerals',
        python_callable=excess_of_minerals
    )

    normal_value = DummyOperator(
        task_id='normal_value'
    )
    normal_val = DummyOperator(
        task_id='normal_val'
    )

    first_measure_error = DummyOperator(
        task_id='first_measure_error'
    )

check_tds >> excess_of_minerals >> alarm_system
check_tds >> excess_of_minerals >> first_measure_error
check_tds >> deficiency_of_minerals >> dose_fertilizer
check_tds >> deficiency_of_minerals >> normal_value
check_tds >> normal_val


if __name__ == "__main__":
    dag.cli()