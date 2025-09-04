# sheets_async.py
import asyncio
import time
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

import httpx
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request as GAuthRequest

_DEFAULT_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
_TOKEN_REFRESH_MARGIN = 60  # seconds
_RETRYABLE = {429, 500, 502, 503, 504}


class _SAAuth:
    """Handles OAuth tokens for a service account in an async-friendly way."""
    def __init__(self, sa_json_path: str, scopes: Optional[Sequence[str]] = None):
        self.creds = Credentials.from_service_account_file(
            sa_json_path, scopes=scopes or _DEFAULT_SCOPES
        )
        self._lock = asyncio.Lock()

    async def _ensure_valid(self):
        async with self._lock:
            now = time.time()
            if self.creds.valid and self.creds.expiry and now < self.creds.expiry.timestamp() - _TOKEN_REFRESH_MARGIN:
                return
            # refresh in a thread to avoid blocking the loop
            await asyncio.to_thread(self.creds.refresh, GAuthRequest())

    async def headers(self) -> Dict[str, str]:
        await self._ensure_valid()
        return {"Authorization": f"Bearer {self.creds.token}"}


class SheetsAsync:
    """Async Google Sheets (Values + batchUpdate)."""
    def __init__(
        self,
        spreadsheet_id: str,
        sa_json_path: str,
        *,
        scopes: Optional[Sequence[str]] = None,
        timeout: float = 30.0,
        client: Optional[httpx.AsyncClient] = None,
        retries: int = 5,
        backoff_base: float = 0.5,
    ):
        self.base = "https://sheets.googleapis.com/v4/spreadsheets"
        self.spreadsheet_id = spreadsheet_id
        self.auth = _SAAuth(sa_json_path, scopes or _DEFAULT_SCOPES)
        self._own_client = client is None
        self.client = client or httpx.AsyncClient(timeout=timeout)
        self.retries = retries
        self.backoff_base = backoff_base

    async def close(self):
        if self._own_client:
            await self.client.aclose()

    # ---- internal request with retries ----
    async def _request(self, method: str, url: str, **kwargs) -> Any:
        headers = kwargs.pop("headers", {})
        headers.update(await self.auth.headers())

        for attempt in range(self.retries):
            resp = await self.client.request(method, url, headers=headers, **kwargs)
            if resp.status_code < 400:
                # Sheets returns JSON on success
                if resp.headers.get("content-type", "").startswith("application/json"):
                    return resp.json()
                return resp.text

            if resp.status_code in _RETRYABLE:
                await asyncio.sleep((2 ** attempt) * self.backoff_base)
                continue

            # raise with body for debugging
            raise httpx.HTTPStatusError(
                f"{resp.status_code} {resp.text}",
                request=resp.request,
                response=resp,
            )
        raise RuntimeError("Exceeded retry attempts for Sheets API")

    # ---- VALUES API ----
    async def read(self, a1_range: str) -> Dict[str, Any]:
        url = f"{self.base}/{self.spreadsheet_id}/values/{a1_range}"
        return await self._request("GET", url)

    async def batch_get(self, ranges: Iterable[str]) -> Dict[str, Any]:
        url = f"{self.base}/{self.spreadsheet_id}/values:batchGet"
        # multiple 'ranges' query params; httpx accepts list values
        params = [("ranges", r) for r in ranges]
        return await self._request("GET", url, params=params)

    async def update(
        self,
        a1_range: str,
        values: List[List[Union[str, int, float, None]]],
        *,
        value_input_option: str = "USER_ENTERED",
    ) -> Dict[str, Any]:
        url = f"{self.base}/{self.spreadsheet_id}/values/{a1_range}"
        params = {"valueInputOption": value_input_option}
        body = {"values": values}
        return await self._request("PUT", url, params=params, json=body)

    async def append(
        self,
        a1_range: str,
        values: List[List[Union[str, int, float, None]]],
        *,
        value_input_option: str = "USER_ENTERED",
        insert_data_option: str = "INSERT_ROWS",
    ) -> Dict[str, Any]:
        url = f"{self.base}/{self.spreadsheet_id}/values/{a1_range}:append"
        params = {
            "valueInputOption": value_input_option,
            "insertDataOption": insert_data_option,
        }
        body = {"values": values}
        return await self._request("POST", url, params=params, json=body)

    # ---- SPREADSHEETS batchUpdate (formatting, add sheets, etc.) ----
    async def batch_update(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        url = f"{self.base}/{self.spreadsheet_id}:batchUpdate"
        body = {"requests": requests}
        return await self._request("POST", url, json=body)

    # ---- Convenience helpers ----
    async def get_spreadsheet(self, *, include_grid_data: bool = False) -> Dict[str, Any]:
        url = f"{self.base}/{self.spreadsheet_id}"
        params = {"includeGridData": str(include_grid_data).lower()}
        return await self._request("GET", url, params=params)

    async def get_sheet_id_by_title(self, title: str) -> Optional[int]:
        meta = await self.get_spreadsheet()
        for s in meta.get("sheets", []):
            if s["properties"]["title"] == title:
                return s["properties"]["sheetId"]
        return None

    async def ensure_sheet(self, title: str) -> int:
        """Create the tab if missing; return sheetId."""
        sid = await self.get_sheet_id_by_title(title)
        if sid is not None:
            return sid
        reqs = [{
            "addSheet": {"properties": {"title": title}}
        }]
        res = await self.batch_update(reqs)
        return res["replies"][0]["addSheet"]["properties"]["sheetId"]
