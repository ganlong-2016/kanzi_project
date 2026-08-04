from __future__ import annotations

import locale
import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def run_subprocess(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a command and decode stdout/stderr without crashing on Windows console encodings."""
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding=_subprocess_encoding(),
        errors="replace",
        check=False,
    )


def log_process_output(result: subprocess.CompletedProcess[str]) -> None:
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    if stdout:
        logger.info(stdout)
    if stderr:
        logger.info(stderr)


def format_process_output(result: subprocess.CompletedProcess[str]) -> str:
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if stdout and stderr:
        return f"{stdout}\n{stderr}"
    return stdout or stderr


def _subprocess_encoding() -> str:
    if os.name == "nt":
        # Chinese Windows consoles and Java often emit GBK/cp936 logs.
        return locale.getpreferredencoding(False) or "gbk"
    return "utf-8"
