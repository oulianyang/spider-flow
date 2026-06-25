#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download spider-flow v0.5.0 manual as browsable HTML files with sidebar navigation."""

import os
import time
import urllib.request
from bs4 import BeautifulSoup

BASE_URL = "https://www.bookstack.cn/read/spiderflow-0.5.0/{}.md"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(OUTPUT_DIR, "html")

PAGES = [
    ("01-使用教程", "01-简介", "98bc712c0831b890"),
    ("01-使用教程", "02-安装部署", "cbd8de47d4474b91"),
    ("01-使用教程", "03-快速入门", "0618b5296afcb0ec"),
    ("01-使用教程", "04-表达式语法", "620e86c3c5a46c8b"),
    ("01-使用教程", "05-内置变量", "a84ba53bcaa8876c"),
    ("01-使用教程", "06-高级应用", "b41274ae955f4627"),
    ("01-使用教程", "07-插件开发", "012ed125c6ef4d2c"),
    ("01-使用教程", "08-常见问题", "b21643963c940cb5"),
    ("02-函数说明", "01-抽取函数", "6b51214d941f8b38"),
    ("02-函数说明", "02-base64", "6c11a826a7fb67f5"),
    ("02-函数说明", "03-date", "0257ebe9a5c40dc8"),
    ("02-函数说明", "04-file", "0cf27f119d785511"),
    ("02-函数说明", "05-json", "736dd7675d55820b"),
    ("02-函数说明", "06-list", "04c4eb5f448efd9b"),
    ("02-函数说明", "07-random", "9268522df1b866d7"),
    ("02-函数说明", "08-string", "0c8f87f78abc4879"),
    ("02-函数说明", "09-url", "5475fed325f0ca47"),
    ("03-类型扩展", "01-说明", "db12d839b285b452"),
    ("03-类型扩展", "02-SpiderResponse", "cd5de098cc77a7c2"),
    ("03-类型扩展", "03-String", "3b9afee52169a1b8"),
    ("03-类型扩展", "04-Date", "0cf88f8893d5b208"),
    ("03-类型扩展", "05-Object", "e62136367240b933"),
    ("03-类型扩展", "06-List", "24462b07eba0709d"),
    ("03-类型扩展", "07-Map", "c1b64145d3c2abaa"),
    ("03-类型扩展", "08-Element", "08255145cc328955"),
    ("03-类型扩展", "09-Elements", "8c170717c4b91a77"),
    ("03-类型扩展", "10-数组", "bb62c1cf56345655"),
    ("04-插件", "01-selenium", "f29ef61ee185953e"),
    ("04-插件", "02-redis", "c6a0ff50924497e3"),
    ("04-插件", "03-mongodb", "f84295ba325f4603"),
    ("04-插件", "04-oss", "fa1cf76cf5f45e8a"),
    ("04-插件", "05-ocr", "31febf38b20913ac"),
    ("04-插件", "06-IP代理池插件", "88082c85c82b79ca"),
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - spider-flow v0.5.0 使用手册</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; color: #333; line-height: 1.8; background: #f5f6f8; }}
.layout {{ display: flex; min-height: 100vh; }}
.sidebar {{ width: 280px; background: #1e1e2e; color: #cdd6f4; padding: 20px 0; position: fixed; top: 0; left: 0; bottom: 0; overflow-y: auto; flex-shrink: 0; }}
.sidebar h2 {{ padding: 0 20px 15px; font-size: 16px; color: #89b4fa; border-bottom: 1px solid #313244; margin-bottom: 10px; }}
.sidebar .cat {{ padding: 8px 20px 4px; font-size: 13px; color: #a6adc8; font-weight: 600; margin-top: 8px; }}
.sidebar a {{ display: block; padding: 5px 20px 5px 30px; color: #bac2de; text-decoration: none; font-size: 14px; transition: all .15s; }}
.sidebar a:hover {{ background: #313244; color: #89b4fa; }}
.sidebar a.active {{ background: #313244; color: #89b4fa; border-left: 3px solid #89b4fa; padding-left: 27px; }}
.main {{ margin-left: 280px; flex: 1; padding: 30px 40px; max-width: 960px; }}
.main h1 {{ font-size: 28px; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid #89b4fa; }}
.main h2 {{ font-size: 22px; margin-top: 35px; margin-bottom: 15px; color: #1e1e2e; }}
.main h3 {{ font-size: 18px; margin-top: 25px; margin-bottom: 10px; color: #45475a; }}
.main p {{ margin-bottom: 14px; }}
.main ul, .main ol {{ margin: 10px 0 14px 24px; }}
.main li {{ margin-bottom: 6px; }}
.main table {{ border-collapse: collapse; width: 100%; margin: 14px 0; }}
.main th, .main td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
.main th {{ background: #e8e9ed; font-weight: 600; }}
.main tr:nth-child(even) {{ background: #f9f9fb; }}
.main pre {{ background: #1e1e2e; color: #cdd6f4; padding: 16px; border-radius: 6px; overflow-x: auto; margin: 12px 0; font-size: 14px; line-height: 1.5; }}
.main code {{ background: #e8e9ed; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
.main pre code {{ background: none; padding: 0; }}
.main img {{ max-width: 100%; border-radius: 4px; margin: 8px 0; }}
.main blockquote {{ border-left: 4px solid #89b4fa; padding: 10px 16px; margin: 12px 0; background: #eff1f5; color: #4c4f69; }}
.main a {{ color: #1e66f5; text-decoration: none; }}
.main a:hover {{ text-decoration: underline; }}
.nav-bar {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; display: flex; justify-content: space-between; }}
.nav-bar a {{ color: #1e66f5; text-decoration: none; font-size: 15px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 4px; }}
.nav-bar a:hover {{ background: #eff1f5; }}
</style>
</head>
<body>
<div class="layout">
<nav class="sidebar">
<h2>spider-flow v0.5.0</h2>
{sidebar}
</nav>
<main class="main">
{content}
<div class="nav-bar">
{prev_link}
{next_link}
</div>
</main>
</div>
</body>
</html>"""


def fetch_html(url):
    """Fetch HTML page from bookstack.cn."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def extract_article(html):
    """Extract article content from HTML, fix images/links, return (content_html, title)."""
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article", id="page-content")
    if not article:
        return "<p>Content not found</p>", "Untitled"

    # Remove table of contents
    toc = article.find("div", class_="markdown-toc")
    if toc:
        toc.decompose()

    # Fix image lazy loading (data-original -> src)
    for img in article.find_all("img"):
        data_orig = img.get("data-original")
        if data_orig:
            img["src"] = data_orig
        src = img.get("src", "")
        if src.startswith("/"):
            img["src"] = "https://www.bookstack.cn" + src

    # Fix links - make internal bookstack links absolute
    for a in article.find_all("a"):
        href = a.get("href", "")
        if href.startswith("/static/") or href.startswith("/read/"):
            a["href"] = "https://www.bookstack.cn" + href
            a["target"] = "_blank"

    # Convert prettyprint code blocks (ol/li -> plain code text)
    # NOTE: must use soup.new_tag(), NOT article.new_tag() (article may be detached)
    for pre in article.find_all("pre"):
        lis = pre.find_all("li")
        if lis:
            code_text = "\n".join(li.get_text() for li in lis)
            pre.clear()
            code_tag = soup.new_tag("code")
            code_tag.string = code_text
            pre.append(code_tag)

    title_el = soup.find("h1", id="article-title")
    title = title_el.get_text(strip=True) if title_el else "Untitled"
    content_html = f"<h1>{title}</h1>\n{article.decode_contents()}"
    return content_html, title


def build_sidebar(active_id):
    """Build sidebar navigation HTML, highlighting the current page."""
    lines = []
    current_cat = ""
    for cat, name, pid in PAGES:
        if cat != current_cat:
            current_cat = cat
            lines.append(f'<div class="cat">{cat[3:]}</div>')
        cls = ' class="active"' if pid == active_id else ""
        lines.append(f'<a href="{pid}.html"{cls}>{name[3:]}</a>')
    return "\n".join(lines)


def main():
    os.makedirs(HTML_DIR, exist_ok=True)
    print(f"Output: {HTML_DIR}")
    print(f"Total: {len(PAGES)} pages")
    print("=" * 60)

    results = []  # (cat, name, page_id, success)

    for i, (cat, name, pid) in enumerate(PAGES, 1):
        url = BASE_URL.format(pid)
        out_file = os.path.join(HTML_DIR, f"{pid}.html")

        # Skip if already exists and has content
        if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
            print(f"[{i:02d}/{len(PAGES)}] SKIP (exists): {cat}/{name}")
            results.append((cat, name, pid, True))
            continue

        print(f"[{i:02d}/{len(PAGES)}] {cat}/{name} ...", end=" ")

        try:
            html = fetch_html(url)
            content, title = extract_article(html)
            sidebar = build_sidebar(pid)

            # Build prev/next navigation links
            prev_link = ""
            next_link = ""
            if i > 1:
                p_cat, p_name, p_pid = PAGES[i - 2]
                prev_link = f'<a href="{p_pid}.html">&larr; {p_name[3:]}</a>'
            else:
                prev_link = '<span></span>'
            if i < len(PAGES):
                n_cat, n_name, n_pid = PAGES[i]
                next_link = f'<a href="{n_pid}.html">{n_name[3:]} &rarr;</a>'

            final_html = HTML_TEMPLATE.format(
                title=title,
                sidebar=sidebar,
                content=content,
                prev_link=prev_link,
                next_link=next_link,
            )
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(final_html)
            print(f"OK ({len(final_html)} bytes)")
            results.append((cat, name, pid, True))
        except Exception as e:
            print(f"ERROR: {e}")
            results.append((cat, name, pid, False))

        # Be polite - small delay between requests
        time.sleep(0.5)

    # Generate index.html (table of contents page)
    print("\nGenerating index.html ...")
    index_lines = ["<h1>spider-flow v0.5.0 使用手册</h1>", "<h2>目录</h2>"]
    current_cat = ""
    for cat, name, pid, ok in results:
        if cat != current_cat:
            if current_cat:
                index_lines.append("</ul>")
            current_cat = cat
            index_lines.append(f"<h3>{cat[3:]}</h3><ul>")
        if ok:
            index_lines.append(f'<li><a href="{pid}.html">{name[3:]}</a></li>')
        else:
            index_lines.append(f'<li style="color:#999">{name[3:]} (不可用)</li>')
    index_lines.append("</ul>")
    index_content = "\n".join(index_lines)

    first_ok = next((r for r in results if r[3]), None)
    index_html = HTML_TEMPLATE.format(
        title="spider-flow v0.5.0 使用手册",
        sidebar=build_sidebar(""),
        content=index_content,
        prev_link='<span></span>',
        next_link=f'<a href="{first_ok[2]}.html">{first_ok[1][3:]} &rarr;</a>' if first_ok else "",
    )
    with open(os.path.join(HTML_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    ok_count = sum(1 for _, _, _, ok in results if ok)
    print(f"Done!")
    print(f"\n{'='*60}")
    print(f"Success: {ok_count}/{len(PAGES)}")
    print(f"Open: {os.path.join(HTML_DIR, 'index.html')}")


if __name__ == "__main__":
    main()
