import requests
import time
import os
import boto3
from botocore.client import Config

# Configuration
API_URL = "http://localhost:8080"
QUEUES = ['shell', 'git', 'llm', 'qa', 'tests', 'repo']
s3_config = {
    'endpoint_url': os.environ.get('S3_ENDPOINT', 'http://localhost:9000'),
    'aws_access_key_id': os.environ.get('S3_ACCESS_KEY', 'minioadmin'),
    'aws_secret_access_key': os.environ.get('S3_SECRET_KEY', 'minioadmin'),
    'bucket_name': os.environ.get('S3_BUCKET', 'artifacts'),
    'config': Config(signature_version='s3v4')
}

def get_s3_client():
    """Initializes and returns a boto3 S3 client."""
    return boto3.client(
        's3',
        endpoint_url=s3_config['endpoint_url'],
        aws_access_key_id=s3_config['aws_access_key_id'],
        aws_secret_access_key=s3_config['aws_secret_access_key'],
        config=s3_config['config']
    )

def main():
    """Main function to run the verification."""
    run_ids = {}

    # 1. Enqueue a job in each queue
    print("--- Enqueuing jobs ---")
    for queue in QUEUES:
        command = f'echo "This is a test for the {queue} queue." && touch test_artifact_{queue}.txt'
        payload = {
            "command": command,
            "queue": queue
        }
        try:
            response = requests.post(f"{API_URL}/api/execute", json=payload)
            response.raise_for_status()
            run = response.json()
            run_ids[queue] = run['id']
            print(f"Successfully enqueued job for queue '{queue}' with run ID {run['id']}")
        except requests.exceptions.RequestException as e:
            print(f"Error enqueuing job for queue '{queue}': {e}")
            return # Exit if we can't even enqueue jobs

    # 2. Poll for job completion
    print("\n--- Waiting for jobs to complete ---")
    completed_runs = {}
    for queue, run_id in run_ids.items():
        while run_id not in completed_runs:
            try:
                response = requests.get(f"{API_URL}/runs/{run_id}")
                response.raise_for_status()
                run = response.json()
                if run['status'] in ['succeeded', 'failed']:
                    completed_runs[run_id] = run
                    print(f"Job for queue '{queue}' (Run ID {run_id}) finished with status: {run['status']}")
                else:
                    print(f"Job for queue '{queue}' (Run ID {run_id}) is still {run['status']}...")
                    time.sleep(2)
            except requests.exceptions.RequestException as e:
                print(f"Error polling for run {run_id}: {e}")
                time.sleep(2)

    # 3. Check metrics
    print("\n--- Verifying metrics ---")
    try:
        response = requests.get(f"{API_URL}/api/metrics")
        response.raise_for_status()
        metrics = response.json()
        print("Metrics received:", metrics)
        for queue in QUEUES:
            assert metrics.get(queue, {}).get('submitted', 0) >= 1
            assert metrics.get(queue, {}).get('processed', 0) >= 1
            assert metrics.get(queue, {}).get('succeeded', 0) >= 1
        print("Metrics verification successful!")
    except (requests.exceptions.RequestException, AssertionError) as e:
        print(f"Metrics verification failed: {e}")

    # 4. Verify artifacts in MinIO
    print("\n--- Verifying artifacts in MinIO ---")
    s3 = get_s3_client()
    all_artifacts_verified = True
    for queue, run_id in run_ids.items():
        artifact_name = f"test_artifact_{queue}.txt"
        s3_key = f"{run_id}/{artifact_name}"
        try:
            s3.head_object(Bucket=s3_config['bucket_name'], Key=s3_key)
            print(f"Successfully verified artifact '{s3_key}' for queue '{queue}'")
        except Exception as e:
            print(f"Failed to verify artifact '{s3_key}' for queue '{queue}': {e}")
            all_artifacts_verified = False

    if all_artifacts_verified:
        print("All artifacts verified successfully!")
    else:
        print("Some artifacts were not found.")

if __name__ == "__main__":
    main()
