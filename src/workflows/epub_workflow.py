from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from .activities import (convert_activity, download_with_validation_activity,
                         extract_urls_activity)
from .models import WorkflowInput


@workflow.defn
class EpubGenerationWorkflow:
    """Orchestrates the complete EPUB generation workflow.

    Workflow steps:
    1. Extract chapter URLs from API
    2. Download chapters with validation and retry logic
    3. Convert downloaded HTML to EPUB format

    All activities have automatic retry with exponential backoff.
    """

    @workflow.run
    async def run(self, workflow_input: WorkflowInput) -> str:
        """Execute the EPUB generation workflow.

        Args:
            workflow_input: Complete workflow input parameters

        Returns:
            Path to the generated EPUB file
        """
        retry_policy: RetryPolicy = RetryPolicy(
            initial_interval=timedelta(seconds=2),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(seconds=60),
            maximum_attempts=3,
        )

        urls_file: str = await workflow.execute_activity(
            extract_urls_activity,
            args=workflow_input.to_extraction_input().as_args(),
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(minutes=5),
        )

        output_dir: str = await workflow.execute_activity(
            download_with_validation_activity,
            args=workflow_input.to_download_input().as_args(),
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(minutes=30),
        )

        epub_path: str = await workflow.execute_activity(
            convert_activity,
            args=workflow_input.to_conversion_input().as_args(),
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(minutes=10),
        )

        return epub_path
