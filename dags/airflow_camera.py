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

address = Variable.get("RPI_IP", deserialize_json=False)

args = {
    'owner': 'airflow',
}

def take_photo():
    r = requests.post(address + '/takePhoto')
    return

with DAG(
    dag_id='airflow_camera',
    default_args=args,
    catchup=False,
    schedule_interval= '0 */1 * * *',
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    take_photo = PythonOperator(
        task_id='take_photo',
        python_callable=take_photo
    )

if __name__ == "__main__":
    dag.cli()