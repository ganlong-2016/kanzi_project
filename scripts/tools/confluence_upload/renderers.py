from __future__ import annotations

import logging
import os
import re
import shutil
from pathlib import Path

from confluence_upload.config import UploadConfig
from confluence_upload.java_runtime import resolve_java
from confluence_upload.paths import PLANTUML_TMP_DIR_NAME, export_file, work_dir
from confluence_upload.process_utils import format_process_output, log_process_output, run_subprocess

logger = logging.getLogger(__name__)

FONT_DIRECTIVES = (
    "skinparam defaultFontName",
    "skinparam classFontName",
    "skinparam packageFontName",
    "skinparam componentFontName",
    "skinparam noteFontName",
    "skinparam titleFontName",
    "skinparam sequenceFontName",
    "skinparam participantFontName",
    "skinparam actorFontName",
    "skinparam rectangleFontName",
    "skinparam messageFontName",
    "skinparam legendFontName",
    "skinparam captionFontName",
    "skinparam stereotypeFontName",
    "skinparam swimlaneTitleFontName",
    "skinparam activityFontName",
)


def ensure_png_exists(config: UploadConfig, puml_file: Path, project_root: Path) -> Path:
    png_file = export_file(
        config.export_directory,
        config.docs_directory,
        puml_file.parent,
        f"{puml_file.stem}.png",
    )
    temp_dir = puml_file.parent / PLANTUML_TMP_DIR_NAME
    temp_png = temp_dir / png_file.name
    temp_dir.mkdir(parents=True, exist_ok=True)
    png_file.parent.mkdir(parents=True, exist_ok=True)
    if png_file.exists():
        png_file.unlink()

    source_copy = temp_dir / puml_file.name
    shutil.copy2(puml_file, source_copy)

    try:
        _render_png(config, source_copy, temp_dir, temp_png, project_root)
        if not temp_png.exists():
            raise RuntimeError(f"PlantUML finished but PNG was not created: {temp_png}")
        shutil.move(str(temp_png), png_file)
        return png_file
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def _render_png(
    config: UploadConfig,
    source_copy: Path,
    temp_dir: Path,
    temp_png: Path,
    project_root: Path,
) -> None:
    plantuml_jar = _find_plantuml_jar(project_root)
    cli_jar = _find_plantuml_cli_jar(project_root)
    java_runtime = resolve_java(min_major=8, project_root=project_root)

    if cli_jar and java_runtime and java_runtime[1] >= 21:
        logger.info("Using Java %s for PlantUmlCliMain: %s", java_runtime[1], java_runtime[0])
        _render_with_java_cli(config, source_copy, temp_dir, cli_jar, plantuml_jar, java_runtime[0])
        return

    if cli_jar and (java_runtime is None or java_runtime[1] < 21):
        found = f"Java {java_runtime[1]} ({java_runtime[0]})" if java_runtime else "no suitable Java"
        logger.warning(
            "PlantUmlCliMain requires Java 21+ but found %s. Falling back to plantuml.jar. "
            "Set CONFLUENCE_JAVA or confluence.javaHome to Android Studio JBR for better CJK rendering.",
            found,
        )

    java_exe = java_runtime[0] if java_runtime else "java"
    if java_runtime:
        logger.info("Using Java %s for plantuml.jar: %s", java_runtime[1], java_exe)
    _render_with_plantuml_jar(config, source_copy, temp_dir, plantuml_jar, java_exe)


def _render_with_plantuml_jar(
    config: UploadConfig,
    source_copy: Path,
    temp_dir: Path,
    plantuml_jar: Path,
    java_exe: str,
) -> None:
    wrapped = _preprocess_puml(source_copy, temp_dir, config.plantuml_font_name)
    command = [
        java_exe,
        "-Dfile.encoding=UTF-8",
        "-Dsun.jnu.encoding=UTF-8",
        "-Djava.awt.headless=true",
        "-jar",
        str(plantuml_jar),
        "-charset",
        "UTF-8",
        "-tpng",
        str(wrapped),
        "-o",
        str(temp_dir),
    ]
    logger.info("PlantUML command: %s", " ".join(command))
    result = run_subprocess(command)
    log_process_output(result)
    if result.returncode != 0:
        raise RuntimeError(
            f"PlantUML exited with code {result.returncode} for {source_copy.name}.\n"
            f"{format_process_output(result)}"
        )


def _render_with_java_cli(
    config: UploadConfig,
    source_copy: Path,
    temp_dir: Path,
    cli_jar: Path,
    plantuml_jar: Path,
    java_exe: str,
) -> None:
    command = [
        java_exe,
        "-Dfile.encoding=UTF-8",
        "-Dsun.jnu.encoding=UTF-8",
        "-Djava.awt.headless=true",
        "-cp",
        f"{cli_jar}{_classpath_separator()}{plantuml_jar}",
        "com.rightware.kanzi.gradle.confluence.PlantUmlCliMain",
        f"--font={config.plantuml_font_name}",
        "-charset",
        "UTF-8",
        "-tpng",
        str(source_copy),
        "-o",
        str(temp_dir),
    ]
    logger.info("PlantUML command: %s", " ".join(command))
    result = run_subprocess(command)
    log_process_output(result)
    if result.returncode != 0:
        raise RuntimeError(
            f"PlantUML CLI exited with code {result.returncode} for {source_copy.name}.\n"
            f"{format_process_output(result)}"
        )


def _preprocess_puml(source: Path, temp_dir: Path, font_name: str) -> Path:
    lines = source.read_text(encoding="utf-8").splitlines()
    sanitized = [line for line in lines if not line.strip().startswith("!theme")]
    start_index = next(
        (index for index, line in enumerate(sanitized) if line.strip().startswith("@startuml")),
        -1,
    )
    if start_index < 0:
        wrapped_lines = sanitized
    else:
        font_lines = _build_font_lines(font_name)
        wrapped_lines = []
        for index, line in enumerate(sanitized):
            wrapped_lines.append(line)
            if index == start_index:
                wrapped_lines.extend(font_lines)

    wrapped = temp_dir / f"wrapped-{source.name}"
    content = "\n".join(wrapped_lines)
    wrapped.write_bytes(b"\xef\xbb\xbf" + content.encode("utf-8"))
    return wrapped


def _build_font_lines(font_name: str) -> list[str]:
    lines = ["!pragma layout smetana"]
    lines.extend(f'{name} "{font_name}"' for name in FONT_DIRECTIVES)
    return lines


def _find_plantuml_cli_jar(project_root: Path) -> Path | None:
    candidates = [
        project_root / "build-logic/confluence-publish/build/libs/confluence-publish-1.0.0.jar",
    ]
    version_file = project_root / "gradle.properties"
    if version_file.is_file():
        for line in version_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("kanzi.confluence.plugin.version="):
                version = line.split("=", 1)[1].strip()
                candidates.insert(
                    0,
                    project_root / f"build-logic/confluence-publish/build/libs/confluence-publish-{version}.jar",
                )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _find_plantuml_jar(project_root: Path) -> Path:
    env = os_environ("PLANTUML_JAR", "")
    if env:
        path = Path(env)
        if path.is_file():
            return path
        raise RuntimeError(f"PLANTUML_JAR does not exist: {path}")

    gradle_cache = Path.home() / ".gradle/caches/modules-2/files-2.1/net.sourceforge.plantuml/plantuml"
    if gradle_cache.is_dir():
        jars = sorted(gradle_cache.glob("*/plantuml-*.jar"), key=lambda item: item.stat().st_mtime, reverse=True)
        if jars:
            return jars[0]

    cached = project_root / "scripts/.cache/plantuml.jar"
    if cached.is_file():
        return cached

    return _download_plantuml_jar(cached)


def _download_plantuml_jar(target: Path) -> Path:
    import urllib.request

    url = (
        "https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml/"
        "1.2023.12/plantuml-1.2023.12.jar"
    )
    logger.info("Downloading PlantUML jar to %s", target)
    target.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, target)
    return target


def os_environ(name: str, default: str = "") -> str:
    import os

    return os.environ.get(name, default)


def _classpath_separator() -> str:
    import os

    return ";" if os.name == "nt" else ":"


DIAGRAM_NAME_PATTERN = re.compile(r'<diagram\s+[^>]*\bname="([^"]*)"', re.IGNORECASE)


def ensure_pngs_exist(config: UploadConfig, drawio_file: Path) -> list[tuple[str | None, Path]] | None:
    pages = _parse_pages(drawio_file)
    existing = _resolve_existing_pngs(config, drawio_file, pages)
    if len(existing) == len(pages):
        logger.info("Reusing cached draw.io PNG export(s) for %s", drawio_file.name)
        return existing

    executable = resolve_drawio_executable(config.drawio_executable)
    if not executable:
        message = (
            "draw.io CLI not found. Install draw.io Desktop or set confluence.drawioExecutable "
            f"in gradle.properties, or place PNG file(s) under {config.export_directory.name}/."
        )
        if config.skip_drawio_when_unavailable:
            logger.warning("Skipped %s: %s", drawio_file.name, message)
            return None
        raise RuntimeError(message)

    export_work = work_dir(config.export_directory, "drawio")
    for page_index, page_name in pages:
        target = _png_output_file(config, drawio_file, page_index, page_name, len(pages))
        if target.is_file() and target.stat().st_size > 0:
            continue
        temp_out = export_work / target.name
        _export_drawio_page(executable, drawio_file, page_index, temp_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.unlink()
        shutil.move(str(temp_out), target)

    exported = _resolve_existing_pngs(config, drawio_file, pages)
    if len(exported) != len(pages):
        message = (
            f"Failed to export all draw.io pages for {drawio_file.name}. "
            f"Expected {len(pages)} page(s), found {len(exported)}."
        )
        if config.skip_drawio_when_unavailable:
            logger.warning("Skipped %s: %s", drawio_file.name, message)
            return None
        raise RuntimeError(message)
    return exported


def resolve_drawio_executable(configured: str) -> str | None:
    import os
    import shutil

    candidates: list[str] = []
    if configured.strip():
        candidates.append(configured.strip())
    candidates.extend(["drawio", "draw.io"])
    for env_name in ("ProgramFiles", "ProgramFiles(x86)"):
        root = os.environ.get(env_name)
        if root:
            candidates.append(str(Path(root) / "draw.io" / "draw.io.exe"))
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(str(Path(local_app_data) / "Programs" / "draw.io" / "draw.io.exe"))

    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
        if shutil.which(candidate):
            return candidate
    return None


def _parse_pages(drawio_file: Path) -> list[tuple[int, str]]:
    content = drawio_file.read_text(encoding="utf-8")
    names = DIAGRAM_NAME_PATTERN.findall(content)
    if not names:
        raise RuntimeError(f"No <diagram> pages found in {drawio_file}")
    return list(enumerate(names))


def _resolve_existing_pngs(
    config: UploadConfig,
    drawio_file: Path,
    pages: list[tuple[int, str]],
) -> list[tuple[str | None, Path]]:
    exported: list[tuple[str | None, Path]] = []
    for page_index, page_name in pages:
        png = _png_output_file(config, drawio_file, page_index, page_name, len(pages))
        if png.is_file() and png.stat().st_size > 0:
            heading = None
            if len(pages) > 1:
                heading = f"Page {page_index + 1}: {page_name}"
            exported.append((heading, png))
    return exported


def _png_output_file(
    config: UploadConfig,
    drawio_file: Path,
    page_index: int,
    page_name: str,
    total_pages: int,
) -> Path:
    base_name = drawio_file.stem
    if total_pages == 1:
        file_name = f"{base_name}.png"
    else:
        safe_name = re.sub(r"[^a-z0-9._-]+", "_", page_name.lower()).strip("_") or "page"
        file_name = f"{base_name}-{page_index + 1}-{safe_name}.png"
    return export_file(config.export_directory, config.docs_directory, drawio_file.parent, file_name)


def _export_drawio_page(executable: str, drawio_file: Path, page_index: int, output_png: Path) -> None:
    command = [
        executable,
        "-x",
        "-f",
        "png",
        "-p",
        str(page_index),
        "-o",
        str(output_png),
        str(drawio_file),
    ]
    logger.info("Exporting draw.io page %s from %s -> %s", page_index + 1, drawio_file.name, output_png.name)
    result = run_subprocess(command)
    if result.returncode != 0 or not output_png.exists():
        raise RuntimeError(
            f"draw.io CLI export failed (exit={result.returncode}) for {drawio_file.name} page {page_index}. "
            f"Output: {format_process_output(result)}"
        )
