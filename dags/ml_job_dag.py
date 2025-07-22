from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.utils import timezone
from datetime import timedelta
from airflow.models import Variable

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
}

with DAG(
    dag_id="ml_job_dag",
    default_args=default_args,
    start_date=timezone.utcnow() - timedelta(days=1),
    schedule="@daily",
    catchup=False,
    tags=["example"],
) as dag:

    mlflow_uri = Variable.get("MLFLOW_TRACKING_URI")
    mlflow_username = Variable.get("MLFLOW_TRACKING_USERNAME")
    mlflow_password = Variable.get("MLFLOW_TRACKING_PASSWORD")

    print(mlflow_uri)
    print(mlflow_username)
    print(mlflow_password)

    k8s_task = KubernetesPodOperator(
        namespace="airflow",  # 실행할 namespace
        image="doohee323/ml_job_dag:latest",  # 사용할 컨테이너 이미지
        image_pull_policy="Always",
        labels={"foo": "bar"},
        name="ml_task",
        task_id="run_ml_task",
        is_delete_operator_pod=True,  # 작업 완료 후 Pod 삭제
        get_logs=True,                # 로그 출력
        env_vars={
            "MLFLOW_TRACKING_URI": mlflow_uri,
            "MLFLOW_TRACKING_USERNAME": mlflow_username,
            "MLFLOW_TRACKING_PASSWORD": mlflow_password
        }
    )
