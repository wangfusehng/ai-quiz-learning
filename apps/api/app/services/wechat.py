from typing import Protocol

import httpx

from app.config import get_settings
from app.errors import UpstreamError


class WeChatAuthClient(Protocol):
    def exchange_code(self, code: str) -> str:
        """用 wx.login 的 code 换 openid。不保存 session_key。"""


class HttpWeChatAuthClient:
    def exchange_code(self, code: str) -> str:
        settings = get_settings()
        if not settings.wechat_app_id or not settings.wechat_app_secret:
            raise UpstreamError("wechat")
        try:
            response = httpx.get(
                "https://api.weixin.qq.com/sns/jscode2session",
                params={
                    "appid": settings.wechat_app_id,
                    "secret": settings.wechat_app_secret,
                    "js_code": code,
                    "grant_type": "authorization_code",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise UpstreamError("wechat") from exc
        if data.get("errcode"):
            raise UpstreamError("wechat")
        openid = data.get("openid")
        if not isinstance(openid, str) or not openid:
            raise UpstreamError("wechat")
        return openid
