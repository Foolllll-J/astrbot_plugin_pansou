import aiohttp
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent
import astrbot.api.message_components as Comp
from .pansou_client import PanSouClient
from .formatter import format_result_list, format_detail, DISK_TYPE_ALIASES, CLOUD_TYPE_LABELS
from .state_manager import StateManager, SearchState


async def handle_search(
    event: AstrMessageEvent,
    client: PanSouClient,
    state_mgr: StateManager,
    keyword: str,
    source: str = "all",
    cloud_types: list[str] = None,
    exclude_keywords: list[str] = None,
    auto_check: bool = False,
    force_refresh: bool = False,
    per_page: int = 5,
):
    user_id = event.get_sender_id()
    logger.info(f"[PanSou] 用户 {user_id} 搜索关键词: {keyword}, 来源: {source}, 类型: {cloud_types}, 排除: {exclude_keywords}, 自动验链: {auto_check}")

    try:
        data = await client.search(keyword, source, cloud_types, force_refresh)
    except Exception as e:
        logger.error(f"[PanSou] 搜索失败: {e}")
        if isinstance(e, aiohttp.ClientResponseError) and e.status == 401:
            yield event.plain_result("❌ 登录认证失败，请检查 auth_username 和 auth_password 配置是否正确")
            return
        yield event.plain_result(f"❌ 搜索失败: {e}")
        return

    results = (data.get("data") or data).get("results", [])
    if not results:
        yield event.plain_result("😴 没有找到相关结果")
        return

    if cloud_types:
        cloud_set = set(cloud_types)
        results = [
            r for r in results
            if any(l.get("type") in cloud_set for l in r.get("links", []))
        ]

    if exclude_keywords:
        results = _apply_exclude(results, exclude_keywords)

    state = SearchState(keyword, results, per_page)
    state_mgr.save(user_id, state)

    if auto_check and results:
        logger.info("🔎 正在验证链接有效性...")
        try:
            page_slice = results[:per_page]
            await _ensure_links_checked(page_slice, client, state.check_map, max_per_entry=per_page)
        except Exception as e:
            logger.warning(f"[PanSou] 自动验链失败，跳过: {e}")

    text = format_result_list(
        state.filtered_results, 1, state.total_pages,
        keyword, per_page, state.check_map,
    )
    yield event.plain_result(text)


CHECKABLE_TYPES = {"baidu", "aliyun", "quark", "tianyi", "uc", "mobile", "115", "xunlei", "123"}


async def _ensure_links_checked(
    entries: list[dict],
    client: PanSouClient,
    check_map: dict,
    max_per_entry: int = 5,
):
    to_check = []
    for r in entries:
        for l in r.get("links", [])[:max_per_entry]:
            if l.get("type", "") not in CHECKABLE_TYPES:
                continue
            url = l.get("url", "")
            if url and url not in check_map:
                to_check.append({
                    "disk_type": l.get("type", ""),
                    "url": url,
                    "password": l.get("password", ""),
                })
    if not to_check:
        return
    try:
        resp = await client.check_links(to_check)
    except Exception as e:
        logger.warning(f"[PanSou] 验链接口不可用，跳过: {e}")
        return
    statuses = (resp.get("data") or resp).get("results", [])
    for s in statuses:
        check_map[s.get("url", "")] = s.get("state", "uncertain")


async def _handle_page_change(event, state_mgr: StateManager, client: PanSouClient, auto_check: bool, direction: int):
    user_id = event.get_sender_id()
    state = state_mgr.get(user_id)
    if not state:
        yield event.plain_result("⚠️ 请先搜索，如 /ps <关键词>")
        return

    new_page = state.page + direction
    if new_page < 1 or new_page > state.total_pages:
        yield event.plain_result("📄 没有更多了")
        return
    state.page = new_page

    if auto_check:
        page_entries = state.filtered_results
        pp = state.per_page
        start = (state.page - 1) * pp
        page_slice = page_entries[start:start + pp]
        await _ensure_links_checked(page_slice, client, state.check_map, max_per_entry=state.per_page)

    text = format_result_list(
        state.filtered_results, state.page, state.total_pages,
        state.keyword, state.per_page, state.check_map,
    )
    yield event.plain_result(text)


async def handle_next_page(event, state_mgr: StateManager, client: PanSouClient, auto_check: bool = False):
    async for r in _handle_page_change(event, state_mgr, client, auto_check, 1):
        yield r


async def handle_prev_page(event, state_mgr: StateManager, client: PanSouClient, auto_check: bool = False):
    async for r in _handle_page_change(event, state_mgr, client, auto_check, -1):
        yield r


async def handle_filter(event, state_mgr: StateManager, cloud_type: str):
    user_id = event.get_sender_id()
    state = state_mgr.get(user_id)
    if not state:
        yield event.plain_result("⚠️ 请先搜索，如 /ps <关键词>")
        return
    resolved = DISK_TYPE_ALIASES.get(cloud_type, cloud_type)
    state.cloud_type = resolved
    state.page = 1

    label = CLOUD_TYPE_LABELS.get(resolved, cloud_type)
    text = format_result_list(
        state.filtered_results, 1, state.total_pages,
        f"{state.keyword} (仅 {label})", state.per_page, state.check_map,
    )
    yield event.plain_result(text)


async def handle_detail(
    event: AstrMessageEvent,
    state_mgr: StateManager,
    client: PanSouClient,
    index: int,
    auto_check: bool = False,
):
    user_id = event.get_sender_id()
    state = state_mgr.get(user_id)
    if not state:
        yield event.plain_result("⚠️ 请先搜索，如 /ps <关键词>")
        return
    results = state.filtered_results
    if index < 1 or index > len(results):
        yield event.plain_result(f"⚠️ 编号 {index} 超出范围 (1-{len(results)})")
        return
    result = results[index - 1]

    await _ensure_links_checked([result], client, state.check_map, max_per_entry=10)

    text = format_detail(result, state.check_map, hide_bad=auto_check)
    chain = [Comp.Plain(text)]
    for img_url in result.get("images", []):
        if img_url:
            chain.append(Comp.Image(file=img_url))
    yield event.chain_result(chain)


def _apply_exclude(results: list[dict], keywords: list[str]) -> list[dict]:
    if not keywords:
        return results
    filtered = []
    for r in results:
        text = f"{r.get('title', '')} {r.get('content', '')}".lower()
        if not any(k.lower() in text for k in keywords):
            filtered.append(r)
    return filtered
