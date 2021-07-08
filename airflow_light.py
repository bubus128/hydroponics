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

	
with DAG(
    dag_id='airflow_light',
    default_args=args,
    catchup=False,
    schedule_interval='0 */8 * * *', #At minute 0 past every 8th hour.
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:


if __name__ == "__main__":
    dag.cli()