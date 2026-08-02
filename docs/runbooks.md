# PulseOps Runbooks

## Deployment & Rollback Runbook
* **To deploy:** Merge the code into the main branch and GitHub Actions will build the image, tag it with the Git SHA, and deploy it.
* **To Verify:** The system automatically executes the script named 'scripts/smoke_test.py' and, if the script returns an exit status of 0, then the release is considered healthy.
* **To roll back (Kubernetes):** Use either `kubectl rollout undo deployment pulseops-api` or `kubectl rollout undo deployment pulseops-worker`.

## Incident Response Runbook

### Incident 1: API Unavailable (Readiness Probe Failing)
The symptom is that Kubernetes flags the API pod as unready and the frontend returns 503 errors.
* **Action:** Check the pod logs by using `kubectl logs -l app=pulseops-api` and make sure the Redis and Database connection strings are correct.
* **Recovery:** If the problem is due to a bad config map rollout, rollback the config and then restart the deployment.

### Incident 2: Worker Not Processing Jobs (Queue Backlog Increasing)
* **Symptom:** Alerts are triggered due to the depth of the Redis queue and the jobs remain in the `QUEUED` state.
* Act by increasing the number of workers (`kubectl scale deployment pulseops-worker --replicas=5`). 
* **Recovery:** Look in the worker logs for any crash loops or database locking problems.

### Incident 3: Controlled Failure Demonstration
* **What went wrong:** I deliberately included a faulty `REDIS_URL` in the API environment variables.
* **Detection:** The CI/CD pipeline failed right away in the `smoke_test.py` stage since the API returned a 503 response when the readiness check was performed.
* **Recovery:** The pull request has been reverted. The guardrail (smoke test) managed to stop faulty code from getting into production.