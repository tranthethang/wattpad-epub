"""Centralized validation functions for API and workflow inputs."""


def validate_api_url(api_url: str) -> None:
    """Validate API URL parameter.

    Args:
        api_url: API endpoint URL

    Raises:
        ValueError: If api_url is empty or not a string
    """
    if not api_url or not isinstance(api_url, str):
        raise ValueError("api_url must be a non-empty string")


def validate_page_range(page_from: int, page_to: int) -> None:
    """Validate page range parameters.

    Args:
        page_from: Starting page number
        page_to: Ending page number

    Raises:
        ValueError: If range is invalid
    """
    if page_from < 1 or page_to < page_from:
        raise ValueError("page_from must be >= 1 and page_from <= page_to")


def validate_concurrency(concurrency: int) -> None:
    """Validate concurrency value.

    Args:
        concurrency: Number of concurrent operations

    Raises:
        ValueError: If concurrency < 1
    """
    if concurrency < 1:
        raise ValueError("concurrency must be >= 1")


def validate_retries(max_retries: int) -> None:
    """Validate max_retries value.

    Args:
        max_retries: Maximum number of retry attempts

    Raises:
        ValueError: If max_retries < 1
    """
    if max_retries < 1:
        raise ValueError("max_retries must be >= 1")


def validate_string(value: str, field_name: str) -> None:
    """Validate that a string value is non-empty.

    Args:
        value: The string to validate
        field_name: Name of the field for error messages

    Raises:
        ValueError: If value is empty or not a string
    """
    if not value or not isinstance(value, str):
        raise ValueError(f"{field_name} must be a non-empty string")


def validate_make_request(
    api_url: str,
    page_from: int,
    page_to: int,
    concurrency: int,
    max_retries: int,
    output_dir: str,
) -> None:
    """Validate all parameters for the /make endpoint.

    Args:
        api_url: API endpoint
        page_from: Starting page
        page_to: Ending page
        concurrency: Concurrent downloads
        max_retries: Max retry attempts
        output_dir: Directory to save downloaded chapters

    Raises:
        ValueError: If any parameter is invalid
    """
    validate_api_url(api_url)
    validate_page_range(page_from, page_to)
    validate_concurrency(concurrency)
    validate_retries(max_retries)
    validate_string(output_dir, "output_dir")
