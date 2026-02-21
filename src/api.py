import logging
import os
import uuid

from fastapi import FastAPI, File, Form, UploadFile

from .api_helpers import (StatusResponse, WorkflowResponse,
                          build_workflow_input, get_temporal_client,
                          save_cover_image)
from .config import (COVER_UPLOAD_DIR, DEFAULT_CONCURRENCY,
                     DEFAULT_DOWNLOAD_DIR, DEFAULT_EPUB_DIR,
                     DOWNLOAD_MAX_RETRIES, TEMPORAL_TASK_QUEUE,
                     WORKFLOW_ID_HEX_LENGTH)
from .utils import ensure_directory_exists
from .validation import validate_make_request
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
    concurrency: int = Form(DEFAULT_CONCURRENCY),
    max_retries: int = Form(DOWNLOAD_MAX_RETRIES),
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

    try:
        validate_make_request(api_url, page_from, page_to, concurrency, max_retries)
    except ValueError as e:
        logger.error(f"Invalid request parameters: {str(e)}")
        raise

    try:
        ensure_directory_exists(COVER_UPLOAD_DIR)
        ensure_directory_exists(DEFAULT_DOWNLOAD_DIR)
        ensure_directory_exists(DEFAULT_EPUB_DIR)
    except OSError as e:
        logger.error(f"Failed to create required directories: {str(e)}")
        raise

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

    try:
        client = await get_temporal_client()
        workflow_id = f"epub-{uuid.uuid4().hex[:WORKFLOW_ID_HEX_LENGTH]}"
        logger.info(f"Starting workflow {workflow_id} on queue {TEMPORAL_TASK_QUEUE}")

        try:
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
        finally:
            await client.close()
    except Exception as e:
        logger.error(f"Error submitting workflow: {str(e)}", exc_info=True)
        if cover_path and os.path.exists(cover_path):
            try:
                os.remove(cover_path)
                logger.info(f"Cleaned up cover image: {cover_path}")
            except OSError as cleanup_error:
                logger.warning(f"Failed to clean up cover image: {cleanup_error}")
        raise


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

    try:
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
                    logger.error(
                        f"Failed to retrieve result for {workflow_id}: {error}"
                    )
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
        finally:
            await client.close()
    except Exception as e:
        logger.warning(f"Workflow {workflow_id} not found: {str(e)}")
        return StatusResponse(
            workflow_id=workflow_id,
            status="NOT_FOUND",
            current_step="error",
            result=None,
            error=f"Workflow not found: {str(e)}",
        )
