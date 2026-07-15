from __future__ import annotations

import logging
import os
import re
import shutil
from pathlib import Path

from confluence_upload.process_utils import run_subprocess

logger = logging.getLogger(__name__)

_JAVA_VERSION_PATTERN = re.compile(r'version "([^"]+)"')


def resolve_java(*, min_major: int = 8, project_root: Path | None = None) -> tuple[str, int] | None:
    """Return (java_executable, major_version) for the best available Java runtime."""
    candidates = _java_candidates(project_root)
    best: tuple[str, int] | None = None
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.suffix.lower() == ".exe" and not path.is_file():
            continue
        if not path.is_absolute() and shutil.which(candidate) is None:
            continue
        major = _java_major_version(candidate)
        if major <= 0:
            continue
        if major < min_major:
            continue
        if best is None or major > best[1]:
            best = (candidate, major)
    return best


def resolve_java_or_raise(*, min_major: int = 8, project_root: Path | None = None) -> tuple[str, int]:
    resolved = resolve_java(min_major=min_major, project_root=project_root)
    if resolved is None:
        raise RuntimeError(
            f"Java {min_major}+ is required for PlantUML rendering. "
            "Install JDK 21, set JAVA_HOME, or set CONFLUENCE_JAVA to Android Studio JBR "
            '(e.g. "C:\\Program Files\\Android\\Android Studio\\jbr\\bin\\java.exe").'
        )
    return resolved


def _java_candidates(project_root: Path | None) -> list[str]:
    candidates: list[str] = []

    for env_name in ("CONFLUENCE_JAVA", "JAVA_HOME"):
        value = os.environ.get(env_name, "").strip()
        if not value:
            continue
        path = Path(value)
        if path.is_dir():
            candidates.append(str(path / "bin" / _java_binary_name()))
        else:
            candidates.append(str(path))

    if project_root is not None:
        props = _load_properties(project_root / "local.properties")
        props.update(_load_properties(project_root / "gradle.properties"))
        configured = props.get("confluence.javaHome", "").strip()
        if configured:
            path = Path(configured)
            if path.is_dir():
                candidates.append(str(path / "bin" / _java_binary_name()))
            else:
                candidates.append(str(path))

    if os.name == "nt":
        for root in (
            os.environ.get("ProgramFiles"),
            os.environ.get("ProgramFiles(x86)"),
            os.environ.get("LOCALAPPDATA"),
        ):
            if not root:
                continue
            base = Path(root)
            candidates.extend(
                str(path)
                for path in (
                    base / "Android/Android Studio/jbr/bin/java.exe",
                    base / "Programs/Android/Android Studio/jbr/bin/java.exe",
                    base / "Java/jdk-21/bin/java.exe",
                    base / "Java/jdk-17/bin/java.exe",
                )
                if path.is_file()
            )

    which_java = shutil.which("java")
    if which_java:
        candidates.append(which_java)
    candidates.append("java")
    return _dedupe(candidates)


def _java_major_version(java_executable: str) -> int:
    try:
        result = run_subprocess([java_executable, "-version"])
    except OSError:
        return -1
    text = f"{result.stderr}\n{result.stdout}"
    match = _JAVA_VERSION_PATTERN.search(text)
    if not match:
        return -1
    return _parse_java_major(match.group(1))


def _parse_java_major(version: str) -> int:
    parts = version.split(".")
    if parts[0] == "1" and len(parts) > 1:
        return int(parts[1])
    return int(parts[0])


def _java_binary_name() -> str:
    return "java.exe" if os.name == "nt" else "java"


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _load_properties(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result
