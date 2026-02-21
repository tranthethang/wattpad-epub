import logging
import os
import uuid

from fastapi import FastAPI, File, Form, UploadFile

from .api_helpers import (StatusResponse, WorkflowResponse,
                          build_workflow_input, get_temporal_client,
                          save_cover_image)
from .config import (COVER_UPLOAD_DIR, DEFAULT_DOWNLOAD_DIR, DEFAULT_EPUB_DIR,
                     TEMPORAL_TASK_QUEUE)
from .workflows.epub_workflow import EpubGenerationWorkflow

logger = logging.getLogger(__name__)

app = FastAPI(title="wattpad-epub API")


@app.post("/make", response_model=WorkflowResponse)
async def make(
    api_url: str = Form(...),
    page_from: int = Form(...),
    page_to: int = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    concurrency: int = Form(4),
    max_retries: int = Form(10),
    cover_image: UploadFile | None = File(None),
) -> WorkflowResponse:
    """Submit a new EPUB generation workflow.

    Args:
        api_url: API endpoint to extract chapter URLs from
        page_from: Starting page number
        page_to: Ending page number
        title: Story title
        author: Story author
        concurrency: Number of concurrent downloads (default: 4)
        max_retries: Maximum download retry attempts (default: 10)
        cover_image: Optional cover image file

    Returns:
        WorkflowResponse with workflow_id and status

    Raises:
        Exception: If workflow submission fails
    """
    logger.info(
        f"POST /make - title={title}, author={author}, pages={page_from}-{page_to}"
    )

    if not api_url or not isinstance(api_url, str):
        logger.error("Invalid api_url: must be non-empty string")
        raise ValueError("api_url must be a non-empty string")
    if page_from < 1 or page_to < page_from:
        logger.error(f"Invalid page range: from={page_from}, to={page_to}")
        raise ValueError("page_from must be >= 1 and page_from <= page_to")
    if concurrency < 1:
        logger.error(f"Invalid concurrency: {concurrency}")
        raise ValueError("concurrency must be >= 1")
    if max_retries < 1:
        logger.error(f"Invalid max_retries: {max_retries}")
        raise ValueError("max_retries must be >= 1")

    os.makedirs(COVER_UPLOAD_DIR, exist_ok=True)
    os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(DEFAULT_EPUB_DIR, exist_ok=True)

    cover_path = await save_cover_image(cover_image)
    input_data = build_workflow_input(
        api_url,
        page_from,
        page_to,
        title,
        author,
        concurrency,
        max_retries,
        cover_path,
    )
    client = await get_temporal_client()

    try:
        workflow_id = f"epub-{uuid.uuid4().hex[:12]}"
        logger.info(f"Starting workflow {workflow_id} on queue {TEMPORAL_TASK_QUEUE}")
        await client.start_workflow(
            EpubGenerationWorkflow.run,
            input_data,
            id=workflow_id,
            task_queue=TEMPORAL_TASK_QUEUE,
        )

        logger.info(f"Workflow {workflow_id} submitted successfully")
        return WorkflowResponse(
            workflow_id=workflow_id,
            status="submitted",
            message=f"Workflow {workflow_id} submitted successfully",
        )
    except Exception as e:
        logger.error(f"Error submitting workflow: {str(e)}", exc_info=True)
        if cover_path and os.path.exists(cover_path):
            try:
                os.remove(cover_path)
                logger.info(f"Cleaned up cover image: {cover_path}")
            except OSError as cleanup_error:
                logger.warning(f"Failed to clean up cover image: {cleanup_error}")
        raise
    finally:
        await client.close()


@app.get("/status/{workflow_id}", response_model=StatusResponse)
async def status(workflow_id: str) -> StatusResponse:
    """Get the status of an EPUB generation workflow.

    Args:
        workflow_id: The workflow ID to query

    Returns:
        StatusResponse with workflow status and current step

    Note:
        Returns gracefully if workflow not found (status=NOT_FOUND)
    """
    logger.info(f"GET /status/{workflow_id}")

    client = await get_temporal_client()

    try:
        handle = client.get_workflow_handle(workflow_id)
        workflow_status = await handle.describe()
        state = workflow_status.status

        result = None
        error = None
        current_step = state.name.lower()

        logger.info(f"Workflow {workflow_id} status: {state.name}")

        if state.name == "COMPLETED":
            try:
                result = await handle.result()
                current_step = "completed"
                logger.info(f"Workflow {workflow_id} completed: {result}")
            except Exception as e:
                error = f"Failed to retrieve result: {str(e)}"
                current_step = "completed_with_error"
                logger.error(f"Failed to retrieve result for {workflow_id}: {error}")
        elif state.name == "FAILED":
            error = workflow_status.status_message or "Unknown error"
            current_step = "failed"
            logger.error(f"Workflow {workflow_id} failed: {error}")

        return StatusResponse(
            workflow_id=workflow_id,
            status=state.name,
            current_step=current_step,
            result=result,
            error=error,
        )
    except Exception as e:
        logger.warning(f"Workflow {workflow_id} not found: {str(e)}")
        return StatusResponse(
            workflow_id=workflow_id,
            status="NOT_FOUND",
            current_step="error",
            result=None,
            error=f"Workflow not found: {str(e)}",
        )
    finally:
        await client.close()
