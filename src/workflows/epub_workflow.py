from datetime import timedelta

from temporalio import workflow

from .activities import (convert_activity, download_with_validation_activity,
                         extract_urls_activity)


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
    async def run(self, input_data: dict) -> str:
        """Execute the EPUB generation workflow.

        Args:
            input_data: Dictionary containing:
                - api_url: API endpoint for URL extraction
                - page_from: Starting page number
                - page_to: Ending page number
                - title: Story title
                - author: Story author
                - concurrency: Download concurrency level
                - max_retries: Max download retry attempts
                - cover_path: Optional cover image path
                - urls_file: Output file for URLs
                - output_dir: Directory for HTML files
                - output_file: Output EPUB file path

        Returns:
            Path to the generated EPUB file
        """
        retry_policy = workflow.RetryPolicy(
            initial_interval=timedelta(seconds=2),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(seconds=60),
            maximum_attempts=3,
        )

        urls_file = await workflow.execute_activity(
            extract_urls_activity,
            input_data["api_url"],
            input_data["page_from"],
            input_data["page_to"],
            input_data["urls_file"],
            retry_policy=retry_policy,
        )

        output_dir = await workflow.execute_activity(
            download_with_validation_activity,
            urls_file,
            input_data["output_dir"],
            input_data["concurrency"],
            input_data["max_retries"],
            retry_policy=retry_policy,
        )

        epub_path = await workflow.execute_activity(
            convert_activity,
            output_dir,
            input_data["output_file"],
            input_data["title"],
            input_data["author"],
            input_data.get("cover_path"),
            retry_policy=retry_policy,
        )

        return epub_path
