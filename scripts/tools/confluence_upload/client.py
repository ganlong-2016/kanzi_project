from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExistingPage:
    page_id: str
    version: int


class ConfluenceClient:
    def __init__(
        self,
        confluence_url: str,
        api_token: str,
        *,
        dry_run: bool = False,
        timeout_seconds: int = 300,
    ) -> None:
        self._base_url = confluence_url.rstrip("/")
        self._api_token = api_token
        self._dry_run = dry_run
        self._timeout = timeout_seconds
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            }
        )

    def get_space_key(self, page_id: str) -> str:
        if self._dry_run:
            logger.info("[dryRun] resolve space key for parent page %s", page_id)
            return "DRYRUN"
        data = self._request_json("GET", f"/rest/api/content/{page_id}?expand=space")
        space = data.get("space") or {}
        key = space.get("key")
        if not key:
            raise RuntimeError(f"Space key missing in Confluence response for page {page_id}")
        return str(key)

    def create_or_update_child_page(
        self,
        parent_id: str,
        space_key: str,
        title: str,
        storage_html: str,
    ) -> str:
        if self._dry_run:
            logger.info("[dryRun] upsert page '%s' under parent %s", title, parent_id)
            return "dry-run-page-id"

        existing = self._find_child_page(parent_id, title, space_key)
        payload = self._build_page_payload(parent_id, space_key, title, storage_html, existing)
        if existing:
            url = f"/rest/api/content/{existing.page_id}"
            data = self._request_json("PUT", url, json_body=payload)
        else:
            data = self._request_json("POST", "/rest/api/content", json_body=payload)
        return str(data["id"])

    def upload_attachment(self, page_id: str, file_path: Path) -> None:
        if self._dry_run:
            logger.info("[dryRun] upload attachment %s to page %s", file_path.name, page_id)
            return

        attachment_id = self._find_attachment_id(page_id, file_path.name)
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "X-Atlassian-Token": "no-check",
        }
        with file_path.open("rb") as handle:
            files = {"file": (file_path.name, handle, _guess_image_media_type(file_path))}
            if attachment_id:
                logger.info("Updating existing attachment %s on page %s", file_path.name, page_id)
                url = f"{self._base_url}/rest/api/content/{page_id}/child/attachment/{attachment_id}/data"
            else:
                logger.info("Creating attachment %s on page %s", file_path.name, page_id)
                url = f"{self._base_url}/rest/api/content/{page_id}/child/attachment"
            self._execute_with_retry(
                f"{'update' if attachment_id else 'create'} attachment {file_path.name}",
                lambda: self._raise_for_status(
                    requests.post(url, headers=headers, files=files, timeout=self._timeout)
                ),
            )

    def _build_page_payload(
        self,
        parent_id: str,
        space_key: str,
        title: str,
        storage_html: str,
        existing: ExistingPage | None,
    ) -> dict:
        payload: dict = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": storage_html,
                    "representation": "storage",
                }
            },
        }
        if existing:
            payload["id"] = existing.page_id
            payload["version"] = {"number": existing.version + 1}
        else:
            payload["ancestors"] = [{"id": parent_id}]
        return payload

    def _find_child_page(self, parent_id: str, title: str, space_key: str) -> ExistingPage | None:
        encoded_title = quote(title, safe="")
        url = (
            f"/rest/api/content?title={encoded_title}&spaceKey={space_key}"
            f"&expand=version,ancestors"
        )
        try:
            data = self._request_json("GET", url)
        except Exception:
            return None
        for page in data.get("results", []):
            if page.get("title") != title:
                continue
            ancestors = page.get("ancestors") or []
            if any(str(ancestor.get("id")) == parent_id for ancestor in ancestors):
                version = int((page.get("version") or {}).get("number", 1))
                return ExistingPage(page_id=str(page["id"]), version=version)
        return None

    def _find_attachment_id(self, page_id: str, filename: str) -> str | None:
        encoded = quote(filename, safe="")
        url = f"/rest/api/content/{page_id}/child/attachment?filename={encoded}&expand=version"
        try:
            data = self._request_json("GET", url)
        except Exception:
            return None
        for attachment in data.get("results", []):
            if attachment.get("title") == filename:
                return str(attachment["id"])
        return None

    def _request_json(self, method: str, path: str, *, json_body: dict | None = None) -> dict:
        def call() -> dict:
            response = self._session.request(
                method,
                f"{self._base_url}{path}",
                json=json_body,
                timeout=self._timeout,
            )
            self._raise_for_status(response)
            return response.json()

        return self._execute_with_retry(f"{method} {path}", call)

    def _execute_with_retry(self, label: str, action: Callable[[], object], max_attempts: int = 3) -> object:
        last_error: Exception | None = None
        for attempt in range(max_attempts):
            try:
                return action()
            except (requests.Timeout, requests.ConnectionError) as error:
                last_error = error
                if attempt >= max_attempts - 1:
                    raise
                wait_seconds = (attempt + 1) * 2
                logger.warning(
                    "Confluence %s failed (%s); retrying in %ss (%s/%s)",
                    label,
                    error,
                    wait_seconds,
                    attempt + 2,
                    max_attempts,
                )
                time.sleep(wait_seconds)
        raise last_error or RuntimeError(f"Confluence {label} failed")

    @staticmethod
    def _raise_for_status(response: requests.Response) -> requests.Response:
        if response.ok:
            return response
        raise RuntimeError(f"Confluence request failed: {response.status_code} {response.text}")


def _guess_image_media_type(file_path: Path) -> str:
    lower_name = file_path.name.lower()
    if lower_name.endswith(".png"):
        return "image/png"
    if lower_name.endswith(".jpg") or lower_name.endswith(".jpeg"):
        return "image/jpeg"
    if lower_name.endswith(".gif"):
        return "image/gif"
    if lower_name.endswith(".svg"):
        return "image/svg+xml"
    return "application/octet-stream"
