import aiohttp
import json
from astrbot.api import logger
import asyncio


class PanSouClient:
    def __init__(self, base_url: str, proxy: str = ""):
        self.base_url = base_url.rstrip("/")
        self.proxy = proxy.strip() or None
        self._session: aiohttp.ClientSession = None
        self._token: str = ""
        self._auth_username: str = ""
        self._auth_password: str = ""
        self._lock = asyncio.Lock()

    async def ensure_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def set_auth(self, username: str, password: str):
        self._auth_username = username
        self._auth_password = password

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        await self.ensure_session()
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        proxy = kwargs.pop("proxy", self.proxy)

        for attempt in range(2):
            try:
                async with self._session.request(
                    method, url, headers=headers, proxy=proxy, **kwargs
                ) as resp:
                    if resp.status == 401 and self._auth_username and attempt == 0:
                        await self._login()
                        headers["Authorization"] = f"Bearer {self._token}"
                        continue
                    body_bytes = await resp.read()
                    body_text = body_bytes.decode("utf-8", errors="surrogateescape")
                    if resp.status >= 400:
                        raise aiohttp.ClientResponseError(
                            resp.request_info, resp.history,
                            status=resp.status, message=f"{resp.reason}: {body_text[:500]}",
                            headers=resp.headers,
                        )
                    return json.loads(body_text)
            except aiohttp.ClientError as e:
                if attempt == 0 and self._auth_username:
                    await self._login()
                    continue
                raise

    async def _login(self):
        async with self._lock:
            data = {"username": self._auth_username, "password": self._auth_password}
            url = f"{self.base_url}/api/auth/login"
            headers = {}
            proxy = self.proxy
            try:
                async with self._session.post(
                    url, json=data, headers=headers, proxy=proxy
                ) as resp:
                    body = await resp.json()
                    if resp.status >= 400:
                        logger.error(f"[PanSou] 登录失败 ({resp.status}): {body}")
                        return
                    token = (body.get("data") or body).get("token")
                    if token:
                        self._token = token
                        logger.info("[PanSou] 登录成功，已获取 JWT token")
                    else:
                        logger.error("[PanSou] 登录返回中未找到 token")
            except Exception as e:
                logger.error(f"[PanSou] 登录失败: {e}")

    async def search(
        self,
        keyword: str,
        source: str = "all",
        cloud_types: list[str] = None,
        force_refresh: bool = False,
    ) -> dict:
        payload = {
            "kw": keyword,
            "src": source,
            "res": "all",
            "refresh": force_refresh,
        }
        if cloud_types:
            payload["cloud_types"] = cloud_types
        return await self._request("POST", "/api/search", json=payload)

    async def check_links(self, items: list[dict]) -> dict:
        payload = {"items": items}
        return await self._request("POST", "/api/check/links", json=payload)
