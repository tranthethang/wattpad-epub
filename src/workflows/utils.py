class ValidationError(ValueError):
    """Raised when input validation fails."""

    pass


class DownloadValidationError(Exception):
    """Raised when download validation fails after retries."""

    pass


def validate_string(value: str, field_name: str) -> None:
    """Validate that a string value is non-empty.

    Args:
        value: The string to validate
        field_name: Name of the field for error messages

    Raises:
        ValidationError: If value is empty or not a string
    """
    if not value or not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a non-empty string")


def validate_page_range(page_from: int, page_to: int) -> None:
    """Validate page range parameters.

    Args:
        page_from: Starting page number
        page_to: Ending page number

    Raises:
        ValidationError: If range is invalid
    """
    if page_from < 1 or page_to < page_from:
        raise ValidationError(
            "page_from and page_to must be positive and page_from <= page_to"
        )


def validate_concurrency(concurrency: int) -> None:
    """Validate concurrency value.

    Args:
        concurrency: Number of concurrent operations

    Raises:
        ValidationError: If concurrency < 1
    """
    if concurrency < 1:
        raise ValidationError("concurrency must be >= 1")


def validate_retries(max_retries: int) -> None:
    """Validate max_retries value.

    Args:
        max_retries: Maximum number of retry attempts

    Raises:
        ValidationError: If max_retries < 1
    """
    if max_retries < 1:
        raise ValidationError("max_retries must be >= 1")
