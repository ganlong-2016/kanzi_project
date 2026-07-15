from __future__ import annotations

import html
from dataclasses import dataclass
from pathlib import Path

import markdown

from confluence_upload.config import UploadConfig
from confluence_upload.renderers import ensure_png_exists, ensure_pngs_exist


@dataclass(frozen=True)
class RenderedDocument:
    storage_html: str
    attachments: tuple[Path, ...] = ()


@dataclass(frozen=True)
class SkippedDocument:
    reason: str


RenderOutcome = RenderedDocument | SkippedDocument


def render_document(config: UploadConfig, document: Path, project_root: Path) -> RenderOutcome:
    lower_name = document.name.lower()
    if lower_name.endswith(".md"):
        return RenderedDocument(_render_markdown(document))
    if lower_name.endswith(".puml"):
        png = ensure_png_exists(config, document, project_root)
        return RenderedDocument(
            storage_html=_build_image_section(
                intro=f"Auto-generated from PlantUML file: {document.name}",
                sections=((None, png),),
            ),
            attachments=(png,),
        )
    if lower_name.endswith(".drawio"):
        exported = ensure_pngs_exist(config, document)
        if exported is None:
            return SkippedDocument(
                reason=f"draw.io export skipped for {document.name}: CLI unavailable and no cached PNG found"
            )
        return RenderedDocument(
            storage_html=_build_image_section(
                intro=f"Auto-generated from draw.io file: {document.name}",
                sections=exported,
            ),
            attachments=tuple(path for _, path in exported),
        )
    if lower_name.endswith((".doc", ".docx")):
        return RenderedDocument(
            storage_html=(
                f"<p>Word document: {html.escape(document.name)} "
                "(upload placeholder; POI parsing not enabled)</p>"
            )
        )
    return RenderedDocument(storage_html=f"<p>Unsupported document: {html.escape(document.name)}</p>")


def _render_markdown(document: Path) -> str:
    body = markdown.markdown(document.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
    return f"<p>Auto-generated from Markdown by Python Confluence uploader.</p><hr/>{body}"


def _build_image_section(
    *,
    intro: str,
    sections: tuple[tuple[str | None, Path], ...],
) -> str:
    parts = [f"<p>{html.escape(intro)}</p>"]
    for heading, png in sections:
        if heading:
            parts.append(f"<h3>{html.escape(heading)}</h3>")
        parts.append(
            f'<ac:image ac:align="center" ac:layout="center">'
            f'<ri:attachment ri:filename="{html.escape(png.name, quote=True)}" />'
            f"</ac:image>"
        )
    return "".join(parts)
