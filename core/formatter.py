LINK_STATUS_ICON = {
    "ok": "✅",
    "bad": "❌",
    "locked": "⚠️",
    "unsupported": "⚠️",
    "uncertain": "⚠️",
}

LINK_STATUS_LABEL = {
    "ok": "",
    "bad": " [已失效]",
    "locked": " [已锁定]",
    "unsupported": " [不支持检测]",
    "uncertain": " [无法确定]",
}

CLOUD_TYPE_LABELS = {
    "baidu": "百度", "aliyun": "阿里", "quark": "夸克",
    "tianyi": "天翼", "115": "115", "xunlei": "迅雷",
    "uc": "UC", "123": "123云盘", "pikpak": "PikPak",
    "mobile": "移动", "magnet": "磁力", "ed2k": "电驴",
    "guangya": "光鸭",
}

DISK_TYPE_ALIASES = {
    "baidu": "baidu", "bd": "baidu", "百度": "baidu",
    "aliyun": "aliyun", "ali": "aliyun", "阿里": "aliyun",
    "quark": "quark", "kk": "quark", "夸克": "quark",
    "tianyi": "tianyi", "ty": "tianyi", "天翼": "tianyi",
    "115": "115",
    "xunlei": "xunlei", "xl": "xunlei", "迅雷": "xunlei",
    "uc": "uc",
    "123": "123", "123pan": "123",
    "pikpak": "pikpak", "pk": "pikpak",
    "mobile": "mobile", "yd": "mobile", "移动": "mobile", "139": "mobile",
    "magnet": "magnet", "cl": "magnet", "磁力": "magnet",
    "ed2k": "ed2k", "dl": "ed2k", "电驴": "ed2k",
    "guangya": "guangya", "gy": "guangya", "光鸭": "guangya",
}


def _label(disk_type: str) -> str:
    return CLOUD_TYPE_LABELS.get(disk_type, disk_type)


def _link_line(link: dict, status: str = None) -> str:
    dt = _label(link.get("type", ""))
    url = link.get("url", "")
    pwd = link.get("password", "")
    pwd_part = f"  密码：{pwd}" if pwd else ""
    if status:
        icon = LINK_STATUS_ICON.get(status, "⚪")
        label = LINK_STATUS_LABEL.get(status, "")
        return f"   {icon} {dt}: {url}{pwd_part}{label}"
    return f"   📎 {dt}: {url}{pwd_part}"


def format_result_list(
    results: list[dict],
    page: int,
    total_pages: int,
    keyword: str,
    per_page: int = 5,
    check_map: dict[str, str] = None,
) -> str:
    check_map = check_map or {}
    lines = [f"🔍 {keyword} — 第 {page}/{total_pages} 页\n"]
    start = (page - 1) * per_page
    display = []
    for r in results[start:start + per_page]:
        all_links = r.get("links", [])
        if not all_links:
            continue

        # 过滤掉已确认失效的链接
        display_links = [
            l for l in all_links
            if not check_map.get(l.get("url", "")) or check_map.get(l.get("url", "")) != "bad"
        ]

        # 所有链接均已检测且全部失效 → 隐藏整条
        total = len(all_links)
        checked = sum(1 for l in all_links if check_map.get(l.get("url", "")))
        bad = sum(1 for l in all_links if check_map.get(l.get("url", "")) == "bad")
        if checked == total and bad == total:
            continue

        display.append((r, display_links))

    for i, (r, links) in enumerate(display, 1):
        title = r.get("title", "无标题")
        channel = r.get("channel", "")
        channel_part = f" {channel} |" if channel else ""
        lines.append(f"【{i}】{channel_part} {title}")
        for link in links[:5]:
            url = link.get("url", "")
            status = check_map.get(url) if check_map else None
            lines.append(_link_line(link, status))
        extra = len(links) - 5
        if extra > 0:
            lines.append(f"   ... 还有 {extra} 条链接")
        tags = r.get("tags", [])
        if tags:
            lines.append(f"   🏷 {' · '.join(tags)}")
        dt = r.get("datetime", "")
        if dt and not dt.startswith("0001-01-01"):
            lines.append(f"   📅 {dt[:10]}")
        lines.append("")
    lines.append("💡 `/ps <编号>` 看详情 | `/ps n` 下一页 | `/ps p` 上一页 | `/ps help` 帮助")
    return "\n".join(lines)


def format_detail(
    result: dict,
    check_map: dict[str, str] = None,
    hide_bad: bool = True,
) -> str:
    check_map = check_map or {}
    lines = [
        f"📌 {result.get('title', '无标题')}",
        "━" * 25,
    ]
    dt = result.get("datetime", "")
    if dt and not dt.startswith("0001-01-01"):
        dt = dt.replace("T", " ").replace("+08:00", "").replace("Z", "").strip()
        lines.append(f"📅 {dt}")
    tags = result.get("tags", [])
    if tags:
        lines.append(f"🏷 {' · '.join(tags)}")
    content = result.get("content", "")
    title = result.get("title", "")
    if content and content != title:
        lines.append(f"📝 {content[:200]}")
    lines.append("")
    links = result.get("links", [])
    if links:
        lines.append("🔗 链接")
        for link in links:
            url = link.get("url", "")
            status = check_map.get(url) if check_map else None
            if hide_bad and status == "bad":
                continue
            lines.append(_link_line(link, status))
    return "\n".join(lines)
