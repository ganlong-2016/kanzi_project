from __future__ import annotations

import os
import platform
import re
from dataclasses import dataclass
from pathlib import Path

from confluence_upload.paths import EXPORT_DIR_NAME, PLANTUML_TMP_DIR_NAME


@dataclass(frozen=True)
class UploadConfig:
    confluence_url: str
    parent_page_id: str
    api_token: str
    docs_directory: Path
    export_directory: Path
    page_title_prefix: str
    drawio_executable: str
    plantuml_font_name: str
    dry_run: bool
    upload_delay_seconds: float
    http_timeout_seconds: int
    skip_drawio_when_unavailable: bool
    excluded_directory_names: frozenset[str]
    excluded_file_names: frozenset[str]
    included_extensions: frozenset[str]

    @staticmethod
    def load(
        project_root: Path,
        *,
        docs_directory: Path | None = None,
        export_directory: Path | None = None,
        page_title_prefix: str | None = None,
        dry_run: bool = False,
    ) -> UploadConfig:
        props = _load_properties(project_root / "local.properties")
        props.update(_load_properties(project_root / "gradle.properties"))

        def resolve(key: str, env_name: str, default: str = "") -> str:
            for source in (os.environ.get(env_name), props.get(key)):
                if source and source.strip():
                    return source.strip()
            return default

        token = resolve("confluence.apiToken", "CONFLUENCE_API_TOKEN")
        if not token:
            raise ValueError(
                "Confluence API token is not configured. Set confluence.apiToken in "
                "gradle.properties/local.properties or env CONFLUENCE_API_TOKEN."
            )

        docs = docs_directory or (project_root / "docs" / "architecture")
        export = export_directory or (project_root / "docs" / EXPORT_DIR_NAME)

        return UploadConfig(
            confluence_url=resolve(
                "confluence.url", "CONFLUENCE_URL", "https://confluence.scania.com.cn"
            ).rstrip("/"),
            parent_page_id=resolve("confluence.parentPageId", "CONFLUENCE_PARENT_PAGE_ID", "93520482"),
            api_token=token,
            docs_directory=docs.resolve(),
            export_directory=export.resolve(),
            page_title_prefix=page_title_prefix or project_root.name,
            drawio_executable=resolve("confluence.drawioExecutable", "DRAWIO_EXECUTABLE", "drawio"),
            plantuml_font_name=resolve(
                "confluence.plantumlFontName",
                "CONFLUENCE_PLANTUML_FONT",
                _default_plantuml_font(),
            ),
            dry_run=dry_run,
            upload_delay_seconds=float(
                resolve("confluence.uploadDelayMillis", "CONFLUENCE_UPLOAD_DELAY_MS", "1000")
            )
            / 1000.0,
            http_timeout_seconds=int(
                resolve("confluence.httpReadTimeoutSeconds", "CONFLUENCE_HTTP_TIMEOUT", "300")
            ),
            skip_drawio_when_unavailable=_parse_bool(
                resolve("confluence.skipDrawIoWhenUnavailable", "CONFLUENCE_SKIP_DRAWIO", "true"),
                default=True,
            ),
            excluded_directory_names=frozenset(
                {
                    ".git",
                    ".gradle",
                    ".idea",
                    "build",
                    ".kotlin",
                    EXPORT_DIR_NAME,
                    PLANTUML_TMP_DIR_NAME,
                    ".fonts",
                }
            ),
            excluded_file_names=frozenset({"readme.md"}),
            included_extensions=frozenset({".md", ".doc", ".docx", ".puml", ".drawio"}),
        )


def _default_plantuml_font() -> str:
    system = platform.system().lower()
    if system == "windows":
        return "Microsoft YaHei"
    if system == "darwin":
        return "PingFang SC"
    return "Noto Sans CJK SC"


def _parse_bool(value: str, *, default: bool) -> bool:
    if not value:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _load_properties(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def page_title(prefix: str, document: Path) -> str:
    base = re.sub(r"\.(md|doc|docx|puml|drawio)$", "", document.name, flags=re.IGNORECASE)
    base = re.sub(r"[_-]", " ", base)
    if base:
        base = base[0].upper() + base[1:]
    return f"{prefix}-{base}"
