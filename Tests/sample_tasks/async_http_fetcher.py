# Tests/sample_tasks/async_http_fetcher.py

import json
import aiohttp
from typing import Any, Dict

from background_workflows.tasks.process_single_queue import ProcessSingleQueue
from background_workflows.utils.decorators import register_activity
from background_workflows.utils.task_logger import logger

@register_activity("ASYNC_HTTP_FETCH")
class AsyncHttpFetcher(ProcessSingleQueue):
    """
    An async task that fetches data from a given URL.
    The input payload is expected to have: {"url": "..."}.
    The output is JSON containing status_code, content_length, etc.
    """

    def do_work_on_single(self, payload: Dict[str, Any]) -> str:
        pass

    async def do_work_on_single_async(self, payload: Dict[str, Any]) -> str:
        url = payload.get("url", "https://httpbin.org/get")
        logger.info(f"[AsyncHttpFetcher] Fetching URL: {url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                status = resp.status
                text = await resp.text()

        result_data = {
            "status_code": status,
            "content_length": len(text),
            "first_50_chars": text[:50],  # store a snippet
        }
        logger.info(f"[AsyncHttpFetcher] Fetched {url}, status={status}, size={len(text)}")

        return json.dumps(result_data)
