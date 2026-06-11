from astrbot.api import logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from typing import Optional

from .core.pansou_client import PanSouClient
from .core.state_manager import StateManager
from .core.formatter import DISK_TYPE_ALIASES
from .core.search_handler import (
    handle_search, handle_next_page, handle_prev_page,
    handle_filter, handle_detail,
)

SUB_ALIASES = {
    "next": "next", "n": "next", "下一页": "next",
    "prev": "prev", "p": "prev", "上一页": "prev",
    "filter": "filter", "f": "filter", "过滤": "filter",
    "help": "help", "帮助": "help",
}


class Main(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context)
        self.config = config or {}
        self.client: Optional[PanSouClient] = None
        self.state_mgr = StateManager()

    async def initialize(self):
        url = self.config.get("pansou_url", "https://so.252035.xyz/")
        proxy = self.config.get("proxy", "")
        self.client = PanSouClient(url, proxy)
        username = self.config.get("auth_username", "")
        password = self.config.get("auth_password", "")
        if username and password:
            self.client.set_auth(username, password)
            await self.client._login()
        logger.info("[盘搜助手] 插件已初始化")

    async def terminate(self):
        if self.client:
            await self.client.close()

    @filter.command("ps", alias={"盘搜"})
    async def handle(self, event: AstrMessageEvent, keyword: str = ""):
        """处理用户消息，支持搜索、翻页、查看详情等功能。使用 /ps help 了解更多。"""
        if not keyword:
            yield event.plain_result("⚠️ 请指定关键词，如 /ps 速度与激情")
            return

        parts = keyword.split(maxsplit=1)
        sub = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        cmd = SUB_ALIASES.get(sub, sub)

        if cmd == "next":
            auto_check = self.config.get("auto_check_links", False)
            async for r in handle_next_page(event, self.state_mgr, self.client, auto_check):
                yield r
            return
        if cmd == "prev":
            auto_check = self.config.get("auto_check_links", False)
            async for r in handle_prev_page(event, self.state_mgr, self.client, auto_check):
                yield r
            return
        if cmd == "help":
            yield event.plain_result(self._help_text())
            return
        if cmd == "filter":
            async for r in handle_filter(event, self.state_mgr, rest):
                yield r
            return

        if sub.isdigit():
            auto_check = self.config.get("auto_check_links", False)
            async for r in handle_detail(event, self.state_mgr, self.client, int(sub), auto_check):
                yield r
            return

        per_page = self.config.get("results_per_page", 5)
        source = self.config.get("default_source", "all")
        cloud_types = self.config.get("default_cloud_types", None) or None
        exclude = self.config.get("default_exclude_keywords", None) or None
        auto_check = self.config.get("auto_check_links", False)
        async for r in handle_search(
            event, self.client, self.state_mgr,
            keyword, source, cloud_types, exclude,
            auto_check, per_page=per_page,
        ):
            yield r

    def _help_text(self) -> str:
        return (
            "📖 盘搜助手 使用帮助\n"
            "━━━━━━━━━━━━━━━\n"
            "/ps <关键词>    搜索网盘资源\n"
            "/ps <编号>      查看详情\n"
            "/ps n         下一页\n"
            "/ps p         上一页\n"
            "/ps f <类型> 按盘类型过滤\n"
            "/ps help         此帮助\n"
            "━━━━━━━━━━━━━━━\n"
            "盘类型: baidu(bd/百度), quark(kk/夸克), aliyun(ali/阿里), 115, xunlei(xl/迅雷), uc, tianyi(ty/天翼), mobile(yd/移动), pikpak(pk), 123, magnet(cl/磁力), ed2k(dl/电驴), guangya(gy/光鸭)"
        )
