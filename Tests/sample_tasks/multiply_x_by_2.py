import json
from typing import Any, Dict
from background_workflows.tasks.process_single_queue import ProcessSingleQueue
from background_workflows.utils.decorators import register_activity
from background_workflows.utils.task_logger import logger


@register_activity( "MULTIPLY_X_BY_2" )
class MultiplyXBy2( ProcessSingleQueue ):
    """
    Example task that processes a single message by reading input parameters,
    performing a calculation (multiplying 'x' by 2), and generating an output message.

    The final result is returned as a JSON string, which is stored in the task's OutputPayload.
    """

    def do_work_on_single(self, payload: Dict[ str, Any ]) -> str:
        """
        Processes the input payload by multiplying 'x' by 2 and preparing an output message.

        :param payload: A dictionary containing input parameters (e.g., {"x": value, "y": message}).
        :return: A JSON string representing the output, e.g., {"answer": <x*2>, "details": "Hello: <y>"}.
        """
        logger.info( f"[MultiplyXBy2] Processing payload: {payload}" )
        input_data: Dict[ str, Any ] = payload

        # Extract values with defaults.
        x: Any = input_data.get( "x", 0 )
        y: Any = input_data.get( "y", "no message" )

        # Perform computation: multiply x by 2.
        answer: Any = x * 2
        details: str = f"Hello: {y}"

        result_data: Dict[ str, Any ] = {"answer": answer, "details": details}
        return json.dumps( result_data )
