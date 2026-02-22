from dataclasses import astuple, dataclass


@dataclass
class UrlExtractionInput:
    """Input parameters for URL extraction activity."""

    api_url: str
    page_from: int
    page_to: int
    urls_file: str

    def as_args(self) -> tuple[str, int, int, str]:
        """Convert to tuple of arguments for activity execution."""
        return astuple(self)


@dataclass
class DownloadInput:
    """Input parameters for download activity."""

    urls_file: str
    output_dir: str
    concurrency: int
    max_retries: int

    def as_args(self) -> tuple[str, str, int, int]:
        """Convert to tuple of arguments for activity execution."""
        return astuple(self)


@dataclass
class ConversionInput:
    """Input parameters for conversion activity."""

    input_dir: str
    output_file: str
    title: str
    author: str
    cover_path: str | None

    def as_args(self) -> tuple[str, str, str, str, str | None]:
        """Convert to tuple of arguments for activity execution."""
        return astuple(self)


@dataclass
class WorkflowInput:
    """Complete input for EPUB generation workflow."""

    api_url: str
    page_from: int
    page_to: int
    title: str
    author: str
    concurrency: int
    max_retries: int
    urls_file: str
    output_dir: str
    output_file: str
    cover_path: str | None = None

    def to_extraction_input(self) -> UrlExtractionInput:
        """Convert to UrlExtractionInput."""
        return UrlExtractionInput(
            api_url=self.api_url,
            page_from=self.page_from,
            page_to=self.page_to,
            urls_file=self.urls_file,
        )

    def to_download_input(self) -> DownloadInput:
        """Convert to DownloadInput."""
        return DownloadInput(
            urls_file=self.urls_file,
            output_dir=self.output_dir,
            concurrency=self.concurrency,
            max_retries=self.max_retries,
        )

    def to_conversion_input(self) -> ConversionInput:
        """Convert to ConversionInput."""
        return ConversionInput(
            input_dir=self.output_dir,
            output_file=self.output_file,
            title=self.title,
            author=self.author,
            cover_path=self.cover_path,
        )
