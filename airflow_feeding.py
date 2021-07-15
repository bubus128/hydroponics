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
pH_upper_limit = 27
pH_lower_limit = 21
pH_middle_value = 24

args = {
    'owner': 'airflow',
}

def check_phase(ti):
    r = requests.get(address + 'add_pH_minus')
    ti.xcom_push(key='tds_value', value=int(r.text))
    phase = Variable.get("WHAT_PHASE_IT_IT")
    if phase == "flowering":
        return 'flowering_phase'
    return 'growth_phase'

def growth_phase(ti):
    tds_value = ti.xcom_pull(key='tds_value', task_ids=['check_phase'])


def flowering_phase(ti):
    tds_value = ti.xcom_pull(key='tds_value', task_ids=['check_phase'])


with DAG(
    dag_id='airflow_feeding',
    default_args=args,
    catchup=False,
    schedule_interval='0 */8 * * *', #At minute 0 past every 8th hour.
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:


    check_phase = BranchPythonOperator(
        task_id='check_phase',
        python_callable=check_phase
    )

    flowering_phase = PythonOperator(
        task_id='flowering_phase',
        python_callable=flowering_phase
    )
    growth_phase = PythonOperator(
        task_id='growth_phase',
        python_callable=growth_phase
    )

if __name__ == "__main__":
    dag.cli()