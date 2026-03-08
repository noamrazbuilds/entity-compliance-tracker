import os

import requests

API_BASE_URL = os.environ.get("ECT_API_URL", "http://localhost:8000")


class APIClient:
    def __init__(self, base_url: str = API_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get(self, path: str, params: dict | None = None) -> dict | list:
        resp = self.session.get(self._url(path), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, json: dict | None = None) -> dict:
        resp = self.session.post(self._url(path), json=json, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def put(self, path: str, json: dict | None = None) -> dict:
        resp = self.session.put(self._url(path), json=json, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def delete(self, path: str) -> dict | None:
        resp = self.session.delete(self._url(path), timeout=30)
        resp.raise_for_status()
        if resp.content:
            return resp.json()
        return None


client = APIClient()
