import os
import mlflow

def main():
    print("Hello from converted notebook")

    print(os.getenv("MLFLOW_TRACKING_URI"))
    print(os.getenv("MLFLOW_TRACKING_USERNAME"))
    print(os.getenv("MLFLOW_TRACKING_PASSWORD"))

    # MLflow 서버 설정
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

    # 실험 이름 설정 (삭제된 이름이면 에러 발생하므로 주의)
    mlflow.set_experiment("Check localhost connection2")

    # 첫 run
    with mlflow.start_run():
        mlflow.log_metric("test", 1)
        mlflow.log_metric("Krish", 2)

    # 두 번째 run
    with mlflow.start_run():
        mlflow.log_metric("test1", 1)
        mlflow.log_metric("Krish1", 2)

    # 세 번째 run
    with mlflow.start_run():
        mlflow.log_metric("test2", 1)
        mlflow.log_metric("Krish2", 2)

if __name__ == "__main__":
    main()
