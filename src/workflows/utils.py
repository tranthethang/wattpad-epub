class ValidationError(ValueError):
    """Raised when input validation fails."""

    pass


class DownloadValidationError(Exception):
    """Raised when download validation fails after retries."""

    pass
