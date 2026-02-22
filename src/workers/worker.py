import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from ..config import (TEMPORAL_HOST, TEMPORAL_NAMESPACE, TEMPORAL_PORT,
                      TEMPORAL_TASK_QUEUE)
from ..workflows.activities import (convert_activity,
                                    download_with_validation_activity,
                                    extract_urls_activity)
from ..workflows.epub_workflow import EpubGenerationWorkflow

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def run_worker() -> None:
    """Start a Temporal worker for EPUB generation tasks.

    Connects to the Temporal server and registers all workflow
    and activity handlers. Runs indefinitely until interrupted.

    Raises:
        Exception: If connection or execution fails
    """
    try:
        logger.info(f"Connecting to Temporal at {TEMPORAL_HOST}:{TEMPORAL_PORT}")
        client = await Client.connect(
            f"{TEMPORAL_HOST}:{TEMPORAL_PORT}",
            namespace=TEMPORAL_NAMESPACE,
        )

        logger.info(f"Starting worker on task queue: {TEMPORAL_TASK_QUEUE}")
        worker = Worker(
            client,
            task_queue=TEMPORAL_TASK_QUEUE,
            workflows=[EpubGenerationWorkflow],
            activities=[
                extract_urls_activity,
                download_with_validation_activity,
                convert_activity,
            ],
        )

        await worker.run()
    except Exception as e:
        logger.error(f"Worker error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(run_worker())
