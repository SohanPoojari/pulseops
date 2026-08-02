import sys
import time
import requests

# We will pass this URL in via our CI/CD pipeline
BASE_URL = "http://localhost:8000"

def run_test():
    print(f"Starting smoke test against {BASE_URL}...")

    # 1. Check if API is ready
    try:
        ready_resp = requests.get(f"{BASE_URL}/health/ready", timeout=5)
        ready_resp.raise_for_status()
        print(" API is ready.")
    except Exception as e:
        print(f" API Readiness check failed: {e}")
        sys.exit(1) # Exiting with 1 tells the pipeline the test failed

    #  Submit a job
    try:
        job_payload = {"input_text": "hello platform"}
        post_resp = requests.post(f"{BASE_URL}/jobs", json=job_payload, timeout=5)
        post_resp.raise_for_status()
        job_id = post_resp.json().get("job_id")
        print(f" Job submitted successfully. Job ID: {job_id}")
    except Exception as e:
        print(f" Failed to submit job: {e}")
        sys.exit(1)

    #  Poll for completion (Bounded timeout)
    max_retries = 10
    for attempt in range(max_retries):
        print(f"Polling job status (Attempt {attempt + 1}/{max_retries})...")
        try:
            get_resp = requests.get(f"{BASE_URL}/jobs/{job_id}", timeout=5)
            status = get_resp.json().get("status")
            result = get_resp.json().get("result")
            
            if status == "COMPLETED":
                if result == "HELLO PLATFORM":
                    print(f" Job processed correctly! Result: {result}")
                    sys.exit(0) # Exiting with 0 means SUCCESS!
                else:
                    print(f" Job completed but result is wrong. Expected 'HELLO PLATFORM', got '{result}'")
                    sys.exit(1)
        except Exception as e:
            print(f" Error checking status: {e}")
        
        time.sleep(2) # Wait 2 seconds before checking again

    print(" Timeout reached. Job did not complete in time.")
    sys.exit(1)

if __name__ == "__main__":
    run_test()