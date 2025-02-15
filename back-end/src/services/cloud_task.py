import datetime
import json

import urllib.parse
from google.cloud import tasks_v2
from google.protobuf import duration_pb2, timestamp_pb2

from src.config import settings


class CloudTask:
    def __init__(
        self,
        project: str = settings.GC_PROJECT_ID,
        location: str = settings.GC_LOCATION,
        queue: str = settings.GC_QUEUE,
        url: str = settings.GC_BACKEND_URI,
    ):
        self.project = project
        self.location = location
        self.queue = queue
        self.url = url

    def create_task(
        self,
        path: str,
        body: dict,
        query: dict | None,
        http_method: tasks_v2.HttpMethod = tasks_v2.HttpMethod.POST,
        scheduled_seconds_from_now: int | None = None,
        task_id: str | None = None,
        deadline_in_seconds: int | None = None,
    ) -> tasks_v2.Task:
        """Create an HTTP POST task with a JSON payload."""

        # Create a client.
        client = tasks_v2.CloudTasksClient()

        # Construct the task.
        task = tasks_v2.Task(
            http_request=tasks_v2.HttpRequest(
                http_method=http_method,
                url=f"{self.url}{path}{'?' + urllib.parse.urlencode(query) if query else ''}",
                headers={
                    "Content-type": "application/json",
                    "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                },
                body=json.dumps(body).encode() if body else None,
            ),
            name=(
                client.task_path(self.project, self.location, self.queue, task_id)
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
                parent=client.queue_path(self.project, self.location, self.queue),
                task=task,
            )
        )
