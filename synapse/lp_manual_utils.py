"""
Synapse - 手動LP変換ユーティリティ
プロンプト生成・HTML変換・ZIP生成のロジック。
"""

import io
import os
import zipfile

from synapse.draft_generator import (
    generate_brain_draft,
    generate_note_draft,
    generate_posting_guide,
)
from synapse.image_pipeline import (
    HAS_PLAYWRIGHT,
    extract_sections,
    generate_manual_screenshot_guide,
)


def build_chat_prompt(data: dict) -> str:
    """AIチャット用プロンプトを生成する。"""
    lines = [
        "あなたはLP制作の専門家です。以下の商品情報をもとに、",
        "売れるLPのHTMLを1ファイルで生成してください。",
        "",
        "# 商品情報",
        f"- 商品名: {data.get('name', '')}",
        f"- ターゲット: {data.get('target', '')}",
        f"- 価格: {data.get('price', '')}",
        f"- 商品内容: {data.get('contents', '')}",
        f"- 差別化ポイント: {data.get('diff', '')}",
    ]
    if data.get("extra"):
        lines.append(f"- 補足: {data['extra']}")
    lines.extend(
        [
            "",
            "# HTML生成ルール",
            "- 単一HTMLファイル、CSSインライン、レスポンシブ（max-width:800px）",
            "- Google Font Noto Sans JP使用",
            "- 各セクションに data-section 属性を付与",
            "  必須値: hero, problem, empathy, solution, features,",
            "  proof, testimonials, comparison, details, offer, faq, cta",
            "- CTAボタン: オレンジ系(#FF6B35)、heroとctaの最低2ヶ所",
            "- 画像は class='img-placeholder' data-image='説明' のdivで表現",
            "- 実績数値は [利用者数を入力] 形式のプレースホルダーにする",
            "- お客様の声は [お客様の名前・属性] [コメント] 形式にする",
            "- FAQ は details/summary タグでアコーディオン実装（3〜5個）",
            "",
            "# 12セクション構成",
            "1. ファーストビュー 2. 問題提起 3. 共感・あおり 4. 解決策",
            "5. 特徴・メリット(3〜5個) 6. 実績・証拠 7. お客様の声(2〜3件)",
            "8. 比較表 9. 商品詳細 10. 価格・オファー 11. FAQ 12. 最終CTA",
            "",
            "HTMLコードのみ出力してください。説明は不要です。",
        ]
    )
    return chr(10).join(lines)


def convert_html(html: str) -> dict:
    """HTMLからBrain/Note素材を生成する。"""
    sections = extract_sections(html)
    brain = generate_brain_draft(html, sections)
    note = generate_note_draft(html, sections)
    guide = generate_posting_guide(sections, brain, note)

    if not HAS_PLAYWRIGHT:
        manual = generate_manual_screenshot_guide("lp.html", sections)
        guide = guide + chr(10) * 2 + manual

    return {
        "lp.html": html,
        "brain_draft.md": brain,
        "note_draft.md": note,
        "posting_guide.md": guide,
        "image_files": [],
    }


def create_manual_zip(result: dict) -> bytes:
    """ZIPを生成する。"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for key in ["lp.html", "brain_draft.md", "note_draft.md", "posting_guide.md"]:
            if key in result:
                zf.writestr(key, result[key])
        for img in result.get("image_files", []):
            if os.path.exists(img):
                zf.write(img, "sections/" + os.path.basename(img))
    return buffer.getvalue()
