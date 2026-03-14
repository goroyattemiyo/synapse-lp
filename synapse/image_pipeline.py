"""
Synapse - 画像化パイプライン
"""

import os
import re
from pathlib import Path
from typing import Any

try:
    from playwright.sync_api import sync_playwright

    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

MAX_IMAGE_WIDTH = 800
MAX_IMAGE_SIZE_BYTES = 1_000_000


def _section_pattern():
    dq = chr(34)
    sq = chr(39)
    return (
        r"<(?:section|div)[^>]*data-section="
        + f"[{dq}{sq}]([^{dq}{sq}]+)[{dq}{sq}]"
        + r"[^>]*>(.*?)</(?:section|div)>"
    )


SECTION_PATTERN = _section_pattern()


def extract_sections(html_content: str) -> list[dict[str, str]]:
    """HTMLからセクションを抽出する。検出優先順位:
    1. data-section属性
    2. <section>タグ
    3. 見出し(h1-h3)で分割
    4. 空リスト(ページ全体撮影へフォールバック)
    """
    result = _extract_by_data_section(html_content)
    if result:
        return result
    result = _extract_by_section_tag(html_content)
    if result:
        return result
    result = _extract_by_headings(html_content)
    if result:
        return result
    return []


def _extract_by_data_section(html_content: str) -> list[dict[str, str]]:
    matches = re.findall(SECTION_PATTERN, html_content, re.DOTALL)
    return [{"name": n, "content": c.strip()} for n, c in matches]


def _extract_by_section_tag(html_content: str) -> list[dict[str, str]]:
    pattern = r"<section[^>]*>(.*?)</section>"
    matches = re.findall(pattern, html_content, re.DOTALL)
    sections = []
    for i, content in enumerate(matches):
        name = _guess_section_name(content, i)
        sections.append({"name": name, "content": content.strip()})
    return sections


def _extract_by_headings(html_content: str) -> list[dict[str, str]]:
    body_match = re.search(r"<body[^>]*>(.*)</body>", html_content, re.DOTALL)
    body = body_match.group(1) if body_match else html_content
    parts = re.split(r"(?=<h[1-3][^>]*>)", body)
    sections = []
    for i, part in enumerate(parts):
        text = part.strip()
        if not text:
            continue
        name = _guess_section_name(text, i)
        sections.append({"name": name, "content": text})
    return sections if len(sections) >= 2 else []


def _guess_section_name(content: str, index: int) -> str:
    heading = re.search(r"<h[1-3][^>]*>(.*?)</h[1-3]>", content, re.DOTALL)
    if heading:
        text = re.sub(r"<[^>]+>", "", heading.group(1)).strip()
        if text:
            slug = text[:20].replace(" ", "_")
            return f"section_{index + 1:02d}_{slug}"
    return f"section_{index + 1:02d}"


def extract_text_from_html(html_content: str) -> str:
    """HTMLタグを除去しプレーンテキストを抽出する。"""
    text = re.sub(r"<style[^>]*>.*?</style>", "", html_content, flags=re.DOTALL)
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</(?:p|div|section|h[1-6]|li|tr)>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def capture_sections(html_path: str, output_dir: str) -> list[str]:
    """PlaywrightでHTMLの各セクションをPNG画像として保存する。"""
    if not HAS_PLAYWRIGHT:
        return []

    html_path = os.path.abspath(html_path)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    saved_images: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": MAX_IMAGE_WIDTH, "height": 600})
        page.goto(f"file://{html_path}")
        page.wait_for_load_state("networkidle")

        sections = page.query_selector_all("[data-section]")
        if not sections:
            sections = page.query_selector_all("section")
        if not sections:
            headings = page.query_selector_all("h1, h2, h3")
            if len(headings) >= 2:
                sections = _build_heading_elements(page, headings)

        if not sections:
            full_path = str(output_dir_path / "full_page.png")
            page.screenshot(path=full_path, full_page=True)
            saved_images.append(full_path)
        else:
            for i, section in enumerate(sections):
                attr = section.get_attribute("data-section")
                if not attr:
                    attr = section.get_attribute("data-name")
                if not attr:
                    attr = f"section_{i + 1:02d}"
                img_path = str(output_dir_path / f"{i + 1:02d}_{attr}.png")
                section.screenshot(path=img_path)
                saved_images.append(img_path)

        browser.close()

    if HAS_PILLOW:
        saved_images = [_optimize_image(img) for img in saved_images]

    return saved_images


def _build_heading_elements(page, headings):
    """見出し要素から親セクション相当の要素リストを構築する。"""
    parents = []
    for h in headings:
        parent = h.evaluate_handle("el => el.parentElement")
        if parent:
            parents.append(parent.as_element())
    seen = set()
    unique = []
    for p in parents:
        if p and id(p) not in seen:
            seen.add(id(p))
            unique.append(p)
    return unique if len(unique) >= 2 else []


def _optimize_image(image_path: str) -> str:
    """画像をリサイズし圧縮する。"""
    if not HAS_PILLOW:
        return image_path

    img: Any = Image.open(image_path)

    if img.width > MAX_IMAGE_WIDTH:
        ratio = MAX_IMAGE_WIDTH / img.width
        new_height = int(img.height * ratio)
        img = img.resize((MAX_IMAGE_WIDTH, new_height))
        img.save(image_path)

    file_size = os.path.getsize(image_path)
    if file_size > MAX_IMAGE_SIZE_BYTES:
        quality = 85
        while file_size > MAX_IMAGE_SIZE_BYTES and quality > 20:
            img.save(image_path, optimize=True, quality=quality)
            file_size = os.path.getsize(image_path)
            quality -= 10

    return image_path


def generate_manual_screenshot_guide(html_path: str, sections: list[dict[str, str]]) -> str:
    """手動スクリーンショットガイドを生成する。"""
    lines = [
        "# 手動スクリーンショットガイド",
        "",
        f"対象ファイル: {html_path}",
        "",
        "## 手順",
        "",
        "1. ブラウザで lp.html を開く",
        "2. 開発者ツール (F12) を開きデバイスツールバーで幅800pxに設定",
        "3. 以下の各セクションをスクリーンショットで保存:",
        "",
    ]

    if sections:
        for i, sec in enumerate(sections):
            lines.append(f"### {i + 1}. {sec[chr(110) + chr(97) + chr(109) + chr(101)]}")
            lines.append(
                f"- ファイル名: {i + 1:02d}_{sec[chr(110) + chr(97) + chr(109) + chr(101)]}.png"
            )
            lines.append("")
    else:
        lines.append("- セクション情報なし: ページ全体を full_page.png として保存")
        lines.append("")

    lines.extend(
        [
            "## 画像仕様",
            "",
            f"- 幅: {MAX_IMAGE_WIDTH}px以下",
            f"- サイズ: {MAX_IMAGE_SIZE_BYTES // 1000}KB以下",
            "- 形式: PNG",
        ]
    )

    return "\n".join(lines)
