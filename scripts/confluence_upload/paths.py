from __future__ import annotations

from pathlib import Path

EXPORT_DIR_NAME = ".confluence-export"
WORK_DIR_NAME = ".work"
PLANTUML_TMP_DIR_NAME = ".plantuml-tmp"


def export_file(export_root: Path, docs_root: Path, source_parent: Path, file_name: str) -> Path:
    relative_parent = source_parent.relative_to(docs_root)
    target_dir = export_root if str(relative_parent) == "." else export_root / relative_parent
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / file_name


def work_dir(export_root: Path, kind: str) -> Path:
    directory = export_root / WORK_DIR_NAME / kind
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def clean_export_work_dir(export_root: Path) -> None:
    work = export_root / WORK_DIR_NAME
    if work.exists():
        import shutil

        shutil.rmtree(work)
