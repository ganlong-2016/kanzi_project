from __future__ import annotations

from pathlib import Path

from confluence_upload.config import UploadConfig


def scan_documents(config: UploadConfig) -> list[Path]:
    if not config.docs_directory.is_dir():
        raise FileNotFoundError(f"Docs directory does not exist: {config.docs_directory}")

    documents: list[Path] = []
    _scan_recursive(config.docs_directory, config, documents)
    return sorted(
        (
            path
            for path in documents
            if path.name.lower() not in config.excluded_file_names
        ),
        key=lambda path: str(path.relative_to(config.docs_directory)),
    )


def _scan_recursive(directory: Path, config: UploadConfig, documents: list[Path]) -> None:
    if directory.name in config.excluded_directory_names:
        return
    for child in directory.iterdir():
        if child.is_dir():
            _scan_recursive(child, config, documents)
        elif child.is_file() and any(child.name.lower().endswith(ext) for ext in config.included_extensions):
            documents.append(child)
