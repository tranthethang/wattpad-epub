"""Helper functions and models for API endpoints."""

import logging
import os
from pathlib import Path

from fastapi import UploadFile
from pydantic import BaseModel
from temporalio.client import Client

from .config import (COVER_UPLOAD_DIR, DEFAULT_DOWNLOAD_DIR, DEFAULT_EPUB_DIR,
                     TEMPORAL_HOST, TEMPORAL_NAMESPACE, TEMPORAL_PORT)
from .utils import ensure_directory_exists, slugify
from .workflows.models import WorkflowInput

logger = logging.getLogger(__name__)


class WorkflowResponse(BaseModel):
    """Response model for workflow submission."""

    workflow_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    """Response model for workflow status query."""

    workflow_id: str
    status: str
    current_step: str | None
    result: str | None
    error: str | None


async def get_temporal_client() -> Client:
    """Create and return a Temporal client.

    Returns:
        Connected Temporal client

    Raises:
        Exception: If connection fails

    Note:
        Connection timeout is 10 seconds
    """
    return await Client.connect(
        f"{TEMPORAL_HOST}:{TEMPORAL_PORT}",
        namespace=TEMPORAL_NAMESPACE,
    )


async def save_cover_image(cover_image: UploadFile | None) -> str | None:
    """Save uploaded cover image with sanitized filename.

    Args:
        cover_image: Uploaded cover image file

    Returns:
        Path to saved cover image, or None
    """
    if not cover_image:
        return None

    try:
        ensure_directory_exists(COVER_UPLOAD_DIR)
    except OSError as e:
        logger.error(f"Failed to create cover directory: {str(e)}")
        return None

    if not cover_image.filename:
        logger.error("Cover image has no filename")
        return None

    safe_filename = (
        slugify(Path(cover_image.filename).stem) + Path(cover_image.filename).suffix
    )
    cover_path = os.path.join(COVER_UPLOAD_DIR, safe_filename)
    logger.info(f"Saving cover image to {cover_path}")

    try:
        with open(cover_path, "wb") as f:
            content = await cover_image.read()
            f.write(content)
    except OSError as e:
        logger.error(f"Failed to save cover image: {str(e)}")
        return None

    return cover_path


def build_workflow_input(
    api_url: str,
    page_from: int,
    page_to: int,
    title: str,
    author: str,
    concurrency: int,
    max_retries: int,
    cover_path: str | None,
) -> WorkflowInput:
    """Build workflow input data instance.

    Args:
        api_url: API endpoint
        page_from: Starting page
        page_to: Ending page
        title: Story title
        author: Story author
        concurrency: Download concurrency
        max_retries: Max retry attempts
        cover_path: Cover image path

    Returns:
        WorkflowInput dataclass instance
    """
    from .utils import clean_filename

    safe_title = clean_filename(title)
    safe_author = clean_filename(author)

    return WorkflowInput(
        api_url=api_url,
        page_from=page_from,
        page_to=page_to,
        title=title,
        author=author,
        concurrency=concurrency,
        max_retries=max_retries,
        cover_path=cover_path,
        urls_file=os.path.join(DEFAULT_DOWNLOAD_DIR, "urls.txt"),
        output_dir=DEFAULT_DOWNLOAD_DIR,
        output_file=os.path.join(DEFAULT_EPUB_DIR, f"{safe_author}_{safe_title}.epub"),
    )
