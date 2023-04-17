import os
import json
import requests
from dotenv import load_dotenv
from github_api import fetch_workflow_run_data
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from convert_to_otlp_json import convert_to_otlp_json

# Load environment variables from .env file
load_dotenv()

# Initialize Tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)


if __name__ == "__main__":
    # Github API documentation: https://docs.github.com/en/rest/reference/actions#get-a-workflow-run
    # This script uses the Github API to retrieve the status of a workflow run

    github_token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    run_id = os.getenv("GITHUB_RUN_ID")

    try:
        result = fetch_workflow_run_data(run_id, owner, repo, github_token)
        print(f"Workflow run data：\n{json.dumps(result, ensure_ascii=False)}")

        trace_data = convert_to_otlp_json(result)
        print(json.dumps(trace_data, indent=2))

        # Send the JSON payload to the OTLP endpoint using HTTP
        headers = {"Content-Type": "application/json"}
        otlp_endpoint = "http://localhost:4318/v1/traces"
        response = requests.post(otlp_endpoint, data=json.dumps(trace_data), headers=headers)
        print("Response status code:", response.status_code)
    except Exception as e:
        print(str(e))