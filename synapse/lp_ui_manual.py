"""
Synapse - 手動LP変換モード（APIキー不要）
全ステップ常時表示: 商品情報入力 -> プロンプト生成 -> HTML貼付 -> 素材完成
"""

import os

import streamlit as st

from synapse.lp_manual_utils import build_chat_prompt, convert_html, create_manual_zip

COLOR_THEMES = {
    "おまかせ（AIに任せる）": "",
    "ダークネイビー × オレンジ": "背景: ダークネイビー(#1a1a2e, #16213e), アクセント: オレンジ(#FF6B35), テキスト: 白/ライトグレー, CTA: オレンジグラデーション",
    "ホワイト × ブルー": "背景: 白(#ffffff), サブ背景: 薄いブルーグレー(#f0f4f8), アクセント: ブルー(#2563eb), テキスト: ダークグレー(#1e293b), CTA: ブルーグラデーション",
    "ブラック × ゴールド": "背景: ブラック(#0a0a0a, #1a1a1a), アクセント: ゴールド(#d4a017, #f4c430), テキスト: 白/ゴールド, CTA: ゴールドグラデーション",
    "ホワイト × グリーン": "背景: 白(#ffffff), サブ背景: ミントグリーン(#f0fdf4), アクセント: グリーン(#16a34a), テキスト: ダークグレー(#1e293b), CTA: グリーングラデーション",
    "ダークパープル × ピンク": "背景: ダークパープル(#1a0533, #2d1b69), アクセント: ピンク(#ec4899, #f472b6), テキスト: 白/ラベンダー, CTA: ピンクグラデーション",
    "ベージュ × ブラウン": "背景: ベージュ(#faf7f2, #f5efe6), アクセント: ブラウン(#92400e, #b45309), テキスト: ダークブラウン(#451a03), CTA: ブラウングラデーション, 上品で落ち着いた雰囲気",
    "カスタム": "custom",
}


def render_manual_mode():
    """手動LP変換モードのUI - 全ステップ常時表示。"""

    # === Step 1: 商品情報 ===
    st.markdown("## 1. 商品情報")
    with st.expander("商品情報を入力", expanded=not bool(st.session_state.get("product_data"))):
        with st.form("product_form"):
            name = st.text_input(
                "商品名 *",
                value=st.session_state.get("_pf_name", ""),
                placeholder="例: AI Money Kit",
            )
            target = st.text_input(
                "ターゲット *",
                value=st.session_state.get("_pf_target", ""),
                placeholder="例: AI副業初心者 25-45歳",
            )
            price = st.text_input(
                "価格 *", value=st.session_state.get("_pf_price", ""), placeholder="例: 3,480円"
            )
            contents = st.text_area(
                "商品内容",
                value=st.session_state.get("_pf_contents", ""),
                height=80,
                placeholder="例: 5つの副業モデル手順書、プロンプト集50個",
            )
            diff = st.text_area(
                "差別化ポイント",
                value=st.session_state.get("_pf_diff", ""),
                height=60,
                placeholder="例: 抽象論ではなく具体的な手順とプロンプト付き",
            )

            theme_key = st.selectbox("配色テーマ", list(COLOR_THEMES.keys()), index=0)
            custom_color = ""
            if theme_key == "カスタム":
                custom_color = st.text_input(
                    "カスタム配色",
                    placeholder="例: 背景: 黒, アクセント: 赤, CTA: 赤グラデーション",
                )

            extra = st.text_area(
                "補足情報（任意）",
                value=st.session_state.get("_pf_extra", ""),
                height=50,
                placeholder="例: 返金保証あり",
            )
            submitted = st.form_submit_button(
                "プロンプトを生成", type="primary", use_container_width=True
            )

        if submitted:
            if not name or not target or not price:
                st.error("商品名・ターゲット・価格は必須です。")
            else:
                color_value = custom_color if theme_key == "カスタム" else COLOR_THEMES[theme_key]
                st.session_state["_pf_name"] = name
                st.session_state["_pf_target"] = target
                st.session_state["_pf_price"] = price
                st.session_state["_pf_contents"] = contents
                st.session_state["_pf_diff"] = diff
                st.session_state["_pf_extra"] = extra
                st.session_state["product_data"] = {
                    "name": name,
                    "target": target,
                    "price": price,
                    "contents": contents,
                    "diff": diff,
                    "extra": extra,
                    "color_theme": color_value,
                }
                st.rerun()

    # === Step 2: プロンプト ===
    st.markdown("---")
    st.markdown("## 2. プロンプト")
    data = st.session_state.get("product_data")
    if data:
        prompt = build_chat_prompt(data)
        st.success("以下をコピーして Claude / ChatGPT に貼り付けてください。")
        st.code(prompt, language="text")
        st.caption("AIがHTMLを出力 → ブラウザで確認・調整 → 納得したらStep 3へ。")
    else:
        st.info("Step 1 で商品情報を入力するとプロンプトが表示されます。")

    # === Step 3: HTML貼付 ===
    st.markdown("---")
    st.markdown("## 3. HTML貼付")
    html_input = st.text_area(
        "最終版HTMLを貼り付け",
        height=200,
        placeholder="<!DOCTYPE html>...",
        key="html_paste_area",
    )
    if st.button("Brain/Note素材に変換", type="primary", use_container_width=True):
        if not html_input or "<html" not in html_input.lower():
            st.error("有効なHTMLを貼り付けてください。")
        else:
            with st.spinner("変換中（画像生成含む）..."):
                result = convert_html(html_input)
            st.session_state["manual_result"] = result
            st.rerun()

    # === Step 4: 素材完成 ===
    st.markdown("---")
    st.markdown("## 4. 素材完成")
    result = st.session_state.get("manual_result")
    if result:
        with st.expander("LPプレビュー", expanded=False):
            html = result.get("lp.html", "")
            if html:
                st.components.v1.html(html, height=500, scrolling=True)

        tab_b, tab_n, tab_g = st.tabs(["Brain用", "Note用", "投稿ガイド"])
        with tab_b:
            brain = result.get("brain_draft.md", "")
            st.markdown(brain)
        with tab_n:
            note = result.get("note_draft.md", "")
            st.markdown(note)
        with tab_g:
            guide = result.get("posting_guide.md", "")
            st.markdown(guide)

        images = result.get("image_files", [])
        if images:
            st.markdown("### セクション画像")
            cols = st.columns(3)
            for i, img in enumerate(images):
                if os.path.exists(img):
                    cols[i % 3].image(img, caption=os.path.basename(img))

        st.divider()
        zip_bytes = create_manual_zip(result)
        st.download_button(
            "全素材をZIPでダウンロード",
            zip_bytes,
            "postcraft_output.zip",
            "application/zip",
            use_container_width=True,
            type="primary",
        )
    else:
        st.info("Step 3 でHTMLを変換すると素材が表示されます。")

    # === リセット ===
    st.markdown("---")
    if st.button("全てリセット", use_container_width=True):
        for key in [
            "product_data",
            "manual_result",
            "_pf_name",
            "_pf_target",
            "_pf_price",
            "_pf_contents",
            "_pf_diff",
            "_pf_extra",
        ]:
            st.session_state.pop(key, None)
        st.rerun()
