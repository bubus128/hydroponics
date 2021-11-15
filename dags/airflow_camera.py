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

def take_photo():
    r = requests.get(address + 'take_photo')


def recognize_phase():
    if Variable.get("WHAT_PHASE_IT_IT") == "growth":
        #TODO recognizing phase
        if(True):
            Variable.set("WHAT_PHASE_IT_IT", "flowering")

def send_photo():
    print("SEND_PHOTO")

def recognize_disease():
    #TODO recognize disease
    if(False):
        return 'plague'
    elif(False):
        return 'lack_of_minerals'
    elif(False):
        return 'sick'
    return 'all_is_ok'

def sick():
    print("PLANTS SICK!")

def lack_of_minerals():
    print("PLANTS LACKING MINERALS!")

def plague():
    print("THERES PLAGUE!")




with DAG(
    dag_id='airflow_camera',
    default_args=args,
    catchup=False,
    schedule_interval='0 */8 * * *', #TODO CHANGE TO TRIGGER WHEN TAKS IN 'LIGHT' SCRIPT DONE
	max_active_runs=1,
    start_date=days_ago(2),
    dagrun_timeout=timedelta(hours=10),
    params={"example_key": "example_value"},
) as dag:

    take_photo = PythonOperator(
        task_id='take_photo',
        python_callable=take_photo
    )

    recognize_phase = PythonOperator(
        task_id='recognize_phase',
        python_callable=recognize_phase
    )

    send_photo = PythonOperator(
        task_id='send_photo',
        python_callable=send_photo
    )

    recognize_disease = BranchPythonOperator(
        task_id='recognize_disease',
        python_callable=recognize_disease
    )

    all_is_ok = DummyOperator(
        task_id='all_is_ok'
    )

    plague = PythonOperator(
        task_id='plague',
        python_callable=plague
    )

    lack_of_minerals = PythonOperator(
        task_id='lack_of_minerals',
        python_callable=lack_of_minerals
    )

    sick = PythonOperator(
        task_id='sick',
        python_callable=sick
    )

take_photo >> recognize_phase >> send_photo >> recognize_disease >> all_is_ok
take_photo >> recognize_phase >> send_photo >> recognize_disease >> plague
take_photo >> recognize_phase >> send_photo >> recognize_disease >> lack_of_minerals
take_photo >> recognize_phase >> send_photo >> recognize_disease >> sick

if __name__ == "__main__":
    dag.cli()