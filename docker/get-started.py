import os
import mlflow

def main():
    print("Hello from converted notebook")

    print(os.getenv("MLFLOW_TRACKING_URI"))
    print(os.getenv("MLFLOW_TRACKING_USERNAME"))
    print(os.getenv("MLFLOW_TRACKING_PASSWORD"))

    # MLflow server configuration
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

    # Set experiment name (be careful as deleted names will cause errors)
    mlflow.set_experiment("Check localhost connection2")

    # First run
    with mlflow.start_run():
        mlflow.log_metric("test", 1)
        mlflow.log_metric("Krish", 2)

    # Second run
    with mlflow.start_run():
        mlflow.log_metric("test1", 1)
        mlflow.log_metric("Krish1", 2)

    # Third run
    with mlflow.start_run():
        mlflow.log_metric("test2", 1)
        mlflow.log_metric("Krish2", 2)

if __name__ == "__main__":
    main()
