"""
Synapse - 手動LP変換モード（APIキー不要）
Step1: 商品情報入力 -> Step2: プロンプト生成 -> Step3: HTML貼付 -> Step4: 変換＆DL
"""

import io
import os
import zipfile

import streamlit as st

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


def render_manual_mode():
    """手動LP変換モードのUIを描画する。"""
    st.header("手動LP変換モード")
    st.markdown(
        "APIキー不要。AIチャットでLPを生成し、ここに貼るだけでBrain/Note用素材を作成します。"
    )

    step = st.session_state.get("manual_step", 1)

    if step == 1:
        _step1_product_form()
    elif step == 2:
        _step2_prompt_display()
    elif step == 3:
        _step3_html_paste()
    elif step == 4:
        _step4_results()


def _step1_product_form():
    """Step 1: 商品情報の構造化入力。"""
    st.subheader("Step 1 / 4: 商品情報を入力")

    with st.form("product_form"):
        name = st.text_input("商品名", placeholder="例: Insightmaster")
        target = st.text_input(
            "ターゲット", placeholder="例: Threads運用者、SNS発信を伸ばしたい20〜30代"
        )
        price = st.text_input("価格", placeholder="例: 3,980円")
        contents = st.text_area(
            "商品内容（含まれるもの）",
            height=100,
            placeholder="例: 分析ツール本体、AI分析機能、投稿出力機能、分析マニュアル(PDF)",
        )
        diff = st.text_area(
            "差別化ポイント（他との違い）",
            height=80,
            placeholder="例: Threads特化、AI要因分析、投稿テンプレート自動生成",
        )
        extra = st.text_area(
            "補足情報（任意）", height=60, placeholder="例: 返金保証あり、買い切り型"
        )
        submitted = st.form_submit_button(
            "プロンプトを生成", type="primary", use_container_width=True
        )

    if submitted and name and target and price:
        st.session_state["product_data"] = {
            "name": name,
            "target": target,
            "price": price,
            "contents": contents,
            "diff": diff,
            "extra": extra,
        }
        st.session_state["manual_step"] = 2
        st.rerun()


def _step2_prompt_display():
    """Step 2: AIチャット用プロンプトの生成・表示。"""
    st.subheader("Step 2 / 4: プロンプトをAIチャットに貼り付け")
    data = st.session_state.get("product_data", {})
    prompt = _build_chat_prompt(data)

    st.info("以下のプロンプトをコピーして、Claude や ChatGPT に貼り付けてください。")
    st.code(prompt, language="text")

    col1, col2 = st.columns(2)
    if col1.button("Step 3へ進む（HTML貼付）", type="primary", use_container_width=True):
        st.session_state["manual_step"] = 3
        st.rerun()
    if col2.button("Step 1に戻る", use_container_width=True):
        st.session_state["manual_step"] = 1
        st.rerun()


def _step3_html_paste():
    """Step 3: AIが生成したHTMLの貼り付け。"""
    st.subheader("Step 3 / 4: 生成されたHTMLを貼り付け")
    st.info("AIチャットが出力したHTMLコードを丸ごと貼り付けてください。")

    html_input = st.text_area("HTMLを貼り付け", height=300, placeholder="<!DOCTYPE html>...")

    col1, col2 = st.columns(2)
    if col1.button("変換してBrain/Note素材を生成", type="primary", use_container_width=True):
        if not html_input or "<html" not in html_input.lower():
            st.error("有効なHTMLを貼り付けてください。")
        else:
            result = _convert_html(html_input)
            st.session_state["manual_result"] = result
            st.session_state["manual_step"] = 4
            st.rerun()
    if col2.button("Step 2に戻る", use_container_width=True):
        st.session_state["manual_step"] = 2
        st.rerun()


def _step4_results():
    """Step 4: 変換結果の表示とダウンロード。"""
    st.subheader("Step 4 / 4: Brain/Note素材が完成しました")
    result = st.session_state.get("manual_result", {})

    # Step 4-1: LPプレビュー
    st.markdown("### LPプレビュー")
    html = result.get("lp.html", "")
    if html:
        st.components.v1.html(html, height=500, scrolling=True)
        st.download_button("lp.html をダウンロード", html, "lp.html", "text/html")

    # Step 4-2: Brain/Note ドラフト
    st.markdown("### Brain/Note ドラフト")
    tab_b, tab_n, tab_g = st.tabs(["Brain用", "Note用", "投稿ガイド"])
    with tab_b:
        st.markdown(result.get("brain_draft.md", ""))
    with tab_n:
        st.markdown(result.get("note_draft.md", ""))
    with tab_g:
        st.markdown(result.get("posting_guide.md", ""))

    # Step 4-3: 画像
    images = result.get("image_files", [])
    if images:
        st.markdown("### セクション画像")
        for img in images:
            if os.path.exists(img):
                st.image(img, caption=os.path.basename(img))

    # ZIP ダウンロード
    st.divider()
    zip_bytes = _create_manual_zip(result)
    st.download_button(
        "全素材をZIPダウンロード",
        zip_bytes,
        "synapse_lp_output.zip",
        "application/zip",
        use_container_width=True,
        type="primary",
    )

    if st.button("最初からやり直す", use_container_width=True):
        for key in ["manual_step", "product_data", "manual_result"]:
            st.session_state.pop(key, None)
        st.rerun()


def _build_chat_prompt(data: dict) -> str:
    """構造化商品データからAIチャット用プロンプトを生成する。"""
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


def _convert_html(html: str) -> dict:
    """貼り付けられたHTMLからBrain/Note素材を生成する。"""
    sections = extract_sections(html)
    brain = generate_brain_draft(html, sections)
    note = generate_note_draft(html, sections)
    guide = generate_posting_guide(sections, brain, note)

    if not HAS_PLAYWRIGHT:
        manual = generate_manual_screenshot_guide("lp.html", sections)
        guide = guide + chr(10) * 2 + manual

    result: dict = {
        "lp.html": html,
        "brain_draft.md": brain,
        "note_draft.md": note,
        "posting_guide.md": guide,
        "image_files": [],
    }
    return result


def _create_manual_zip(result: dict) -> bytes:
    """手動モード結果からZIPを生成する。"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for key in ["lp.html", "brain_draft.md", "note_draft.md", "posting_guide.md"]:
            if key in result:
                zf.writestr(key, result[key])
        for img in result.get("image_files", []):
            if os.path.exists(img):
                zf.write(img, "sections/" + os.path.basename(img))
    return buffer.getvalue()
