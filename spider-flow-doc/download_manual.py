#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download spider-flow v0.5.0 manual from bookstack.cn and convert to Markdown."""

import os
import re
import time
import urllib.request
from bs4 import BeautifulSoup

BASE_URL = "https://www.bookstack.cn/read/spiderflow-0.5.0/{}.md"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# All pages organized by category
PAGES = [
    # 使用教程
    ("01-使用教程", "01-简介", "98bc712c0831b890"),
    ("01-使用教程", "02-安装部署", "cbd8de47d4474b91"),
    ("01-使用教程", "03-快速入门", "0618b5296afcb0ec"),
    ("01-使用教程", "04-表达式语法", "620e86c3c5a46c8b"),
    ("01-使用教程", "05-内置变量", "a84ba53bcaa8876c"),
    ("01-使用教程", "06-高级应用", "b41274ae955f4627"),
    ("01-使用教程", "07-插件开发", "012ed125c6ef4d2c"),
    ("01-使用教程", "08-常见问题", "b21643963c940cb5"),
    # 函数说明
    ("02-函数说明", "01-抽取函数", "6b51214d941f8b38"),
    ("02-函数说明", "02-base64", "6c11a826a7fb67f5"),
    ("02-函数说明", "03-date", "0257ebe9a5c40dc8"),
    ("02-函数说明", "04-file", "0cf27f119d785511"),
    ("02-函数说明", "05-json", "736dd7675d55820b"),
    ("02-函数说明", "06-list", "04c4eb5f448efd9b"),
    ("02-函数说明", "07-random", "9268522df1b866d7"),
    ("02-函数说明", "08-string", "0c8f87f78abc4879"),
    ("02-函数说明", "09-url", "5475fed325f0ca47"),
    # 类型扩展
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
    # 插件
    ("04-插件", "01-selenium", "f29ef61ee185953e"),
    ("04-插件", "02-redis", "c6a0ff50924497e3"),
    ("04-插件", "03-mongodb", "f84295ba325f4603"),
    ("04-插件", "04-oss", "fa1cf76cf5f45e8a"),
    ("04-插件", "05-ocr", "31febf38b20913ac"),
    ("04-插件", "06-IP代理池插件", "88082c85c82b79ca"),
]


def fetch_html(url):
    """Fetch HTML from URL."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def html_table_to_md(table):
    """Convert HTML table to markdown table."""
    rows = table.find_all("tr")
    if not rows:
        return ""
    result = []
    for i, row in enumerate(rows):
        cells = row.find_all(["th", "td"])
        cell_texts = [cell.get_text(strip=True).replace("|", "\\|") for cell in cells]
        line = "| " + " | ".join(cell_texts) + " |"
        result.append(line)
        if i == 0:
            result.append("| " + " | ".join(["---"] * len(cell_texts)) + " |")
    return "\n".join(result)


def code_block_to_md(pre):
    """Convert HTML pre/code block to markdown code block."""
    code_lines = []
    for li in pre.find_all("li", class_=re.compile(r"^L\d")):
        code_lines.append(li.get_text())
    if not code_lines:
        code_lines = [pre.get_text()]
    return "```\n" + "\n".join(code_lines) + "\n```"


def extract_article_to_md(html_content):
    """Extract article content from HTML and convert to markdown."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Get title
    title_el = soup.find("h1", id="article-title")
    title = title_el.get_text(strip=True) if title_el else "Untitled"

    # Get article body
    article = soup.find("article", id="page-content")
    if not article:
        return f"# {title}\n\n(Content not found)"

    lines = [f"# {title}", ""]

    # Process child elements
    for el in article.children:
        if not hasattr(el, "name"):
            continue
        if el.name is None:
            continue

        # Skip TOC
        if el.get("class") and "markdown-toc" in el.get("class", []):
            continue

        # Headers
        if el.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(el.name[1])
            text = el.get_text(strip=True)
            if text == title and level == 1:
                continue  # Skip duplicate title
            lines.append("")
            lines.append("#" * level + " " + text)
            lines.append("")
            continue

        # Tables
        if el.name == "table":
            lines.append("")
            lines.append(html_table_to_md(el))
            lines.append("")
            continue

        # Code blocks
        if el.name == "pre":
            lines.append("")
            lines.append(code_block_to_md(el))
            lines.append("")
            continue

        # Lists
        if el.name in ("ul", "ol"):
            for li in el.find_all("li", recursive=False):
                text = ""
                for child in li.children:
                    if hasattr(child, "name") and child.name == "pre":
                        text += "\n" + code_block_to_md(child) + "\n"
                    elif hasattr(child, "name") and child.name == "p":
                        text += child.get_text(strip=True)
                    elif hasattr(child, "name") and child.name == "a":
                        href = child.get("href", "")
                        link_text = child.get_text(strip=True)
                        text += f"[{link_text}]({href})"
                    elif hasattr(child, "name") and child.name == "code":
                        text += f"`{child.get_text(strip=True)}`"
                    elif hasattr(child, "name") and child.name == "img":
                        alt = child.get("data-original", child.get("alt", ""))
                        src = child.get("data-original", child.get("src", ""))
                        if src and "loading.gif" not in src:
                            text += f"![{alt}]({src})"
                    else:
                        t = child.get_text(strip=True) if hasattr(child, "get_text") else str(child)
                        if t:
                            text += t
                text = text.strip()
                if text:
                    lines.append(f"- {text}")
            lines.append("")
            continue

        # Paragraphs
        if el.name == "p":
            text = el.get_text(strip=True)
            if text == "TIP":
                continue  # Skip standalone TIP labels
            # Check for images
            imgs = el.find_all("img")
            for img in imgs:
                src = img.get("data-original", img.get("src", ""))
                alt = img.get("alt", "")
                if src and "loading.gif" not in src:
                    lines.append(f"![{alt}]({src})")
            # Clean text
            if text:
                lines.append(text)
                lines.append("")
            continue

    return "\n".join(lines)


def main():
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Total pages to download: {len(PAGES)}")
    print("=" * 60)

    for i, (category, name, page_id) in enumerate(PAGES, 1):
        url = BASE_URL.format(page_id)
        out_dir = os.path.join(OUTPUT_DIR, category)
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"{name}.md")

        # Skip if already exists and has content
        if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
            print(f"[{i:02d}/{len(PAGES)}] SKIP (exists): {category}/{name}.md")
            continue

        print(f"[{i:02d}/{len(PAGES)}] Downloading: {category}/{name}.md ...", end=" ")
        try:
            html = fetch_html(url)
            md = extract_article_to_md(html)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"OK ({len(md)} chars)")
        except Exception as e:
            print(f"ERROR: {e}")

        # Be polite - small delay between requests
        time.sleep(0.5)

    print("=" * 60)
    print("Done! All pages downloaded.")


if __name__ == "__main__":
    main()
