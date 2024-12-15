import datetime
import json
from typing import Dict, Optional

import urllib.parse
from google.cloud import tasks_v2
from google.protobuf import duration_pb2, timestamp_pb2

from src.config import settings


def create_http_task(
    http_method: tasks_v2.HttpMethod,
    path: str,
    body: Dict,
    query: Dict,
    project: str = settings.GC_PROJECT_ID,
    location: str = settings.GC_LOCATION,
    queue: str = settings.GC_QUEUE,
    url: str = settings.GC_BACKEND_URI,
    scheduled_seconds_from_now: Optional[int] = None,
    task_id: Optional[str] = None,
    deadline_in_seconds: Optional[int] = None,
) -> tasks_v2.Task:
    """Create an HTTP POST task with a JSON payload.
    Args:
        project: The project ID where the queue is located.
        location: The location where the queue is located.
        queue: The ID of the queue to add the task to.
        url: The target URL of the task.
        json_payload: The JSON payload to send.
        scheduled_seconds_from_now: Seconds from now to schedule the task for.
        task_id: ID to use for the newly created task.
        deadline_in_seconds: The deadline in seconds for task.
    Returns:
        The newly created task.
    """

    # Create a client.
    client = tasks_v2.CloudTasksClient()

    # Construct the task.
    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=http_method,
            url=f"{url}{path}?{urllib.parse.urlencode(query)}",
            headers={
                "Content-type": "application/json",
                "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            },
            body=json.dumps(body).encode(),
        ),
        name=(
            client.task_path(project, location, queue, task_id)
            if task_id is not None
            else None
        ),
    )

    # Convert "seconds from now" to an absolute Protobuf Timestamp
    if scheduled_seconds_from_now is not None:
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(seconds=scheduled_seconds_from_now)
        )
        task.schedule_time = timestamp

    # Convert "deadline in seconds" to a Protobuf Duration
    if deadline_in_seconds is not None:
        duration = duration_pb2.Duration()
        duration.FromSeconds(deadline_in_seconds)
        task.dispatch_deadline = duration

    # Use the client to send a CreateTaskRequest.
    return client.create_task(
        tasks_v2.CreateTaskRequest(
            # The queue to add the task to
            parent=client.queue_path(project, location, queue),
            # The task itself
            task=task,
        )
    )
