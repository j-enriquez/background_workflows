import json
from typing import Any, Dict
from background_workflows.tasks.process_single_queue import ProcessSingleQueue
from background_workflows.utils.decorators import register_activity
from background_workflows.utils.task_logger import logger

@register_activity("SAMPLE_TASK")
class SampleTask(ProcessSingleQueue):
    def do_work_on_single(self, payload: Dict[str, Any]) -> str:
        """
        For demonstration: Multiply the input 'x' by 2 and echo the value of 'y'.

        :param payload: A dictionary containing the input parameters, e.g., {"x": <number>, "y": <string>}.
        :return: A JSON string representing the output payload, e.g., {"answer": <result>, "echo": <y>}.
        """
        x: Any = payload.get("x", 0)
        y: Any = payload.get("y", "")
        logger.info(f"[SampleTask] Received x={x}, y={y}")

        container_name: Any = payload.get( "container_name", "" )
        blob_name: Any = payload.get( "blob_name", "" )

        result_data: Dict[str, Any] = {"answer": x * 2, "echo": y, "ContainerName": container_name, "BlobName": blob_name }
        return json.dumps(result_data)
