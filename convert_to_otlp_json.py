import json
import uuid
from datetime import datetime, timezone

def iso8601_to_otlp_nano(iso8601_str, timezone = timezone.utc):
    dt = datetime.fromisoformat(iso8601_str.rstrip("Z"))
    dt_timezone = dt.astimezone(timezone)
    timestamp_nano = int(dt_timezone.timestamp() * 1e9)
    return timestamp_nano

def convert_to_otlp_json(input_json):
    trace_id = uuid.uuid4().hex

    resource_spans = []
    for job in input_json["jobs"]:
        job_span = {
            "trace_id": trace_id,
            "span_id": f"{job['id']:016x}",
            "name": job["name"],
            "start_time_unix_nano": iso8601_to_otlp_nano(job["started_at"]),
            "end_time_unix_nano": iso8601_to_otlp_nano(job["completed_at"]),
            "attributes": [
                {"key": "component", "value": {"string_value": "GitHub Actions"}}
            ]
        }
        
        span_list = [job_span]
        for step in job["steps"]:
            step_span = {
                "trace_id": trace_id,
                "span_id": f"{step['number']:016x}",
                "parent_span_id": job_span["span_id"],
                "name": step["name"],
                "start_time_unix_nano": iso8601_to_otlp_nano(step["started_at"]),
                "end_time_unix_nano": iso8601_to_otlp_nano(step["completed_at"]),
                "attributes": []
            }
            span_list.append(step_span)
            
        instrumentation_library_spans = {
            "spans": span_list
        }

        resource_spans.append({
            "resource": {
                "attributes": [
                    {"key": "service.name", "value": {"string_value": job["name"]}}
                ]
            },
            "instrumentation_library_spans": [instrumentation_library_spans],
        })

    return {"resource_spans": resource_spans}