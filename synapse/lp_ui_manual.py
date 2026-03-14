"""
Synapse - 手動LP変換モード（APIキー不要）
ステップUI: 商品情報入力 -> プロンプト生成 -> HTML貼付 -> 素材完成
"""

import os

import streamlit as st

from synapse.lp_manual_utils import build_chat_prompt, convert_html, create_manual_zip

STEP_LABELS = ["① 商品情報", "② プロンプト生成", "③ HTML貼付", "④ 素材完成"]


def render_manual_mode():
    """手動LP変換モードのUI。"""
    step = st.session_state.get("manual_step", 1)

    cols = st.columns(4)
    for i, (col, label) in enumerate(zip(cols, STEP_LABELS)):
        if i + 1 < step:
            col.markdown(
                f'<div style="text-align:center;padding:8px;background:#27ae60;color:white;border-radius:8px;font-size:0.8rem;font-weight:700">✅ {label}</div>',
                unsafe_allow_html=True,
            )
        elif i + 1 == step:
            col.markdown(
                f'<div style="text-align:center;padding:8px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-radius:8px;font-size:0.8rem;font-weight:700">{label}</div>',
                unsafe_allow_html=True,
            )
        else:
            col.markdown(
                f'<div style="text-align:center;padding:8px;background:#e9ecef;color:#999;border-radius:8px;font-size:0.8rem">{label}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("")

    if step == 1:
        _step1_form()
    elif step == 2:
        _step2_prompt()
    elif step == 3:
        _step3_paste()
    elif step == 4:
        _step4_results()


def _step1_form():
    """Step 1: 商品情報入力。"""
    st.markdown("### ✨ 商品情報を教えてください")
    st.caption("入力内容をもとに、AIチャット用の最適なプロンプトを自動生成します。")

    with st.form("product_form"):
        name = st.text_input("🏷️ 商品名 *", placeholder="例: Insightmaster")
        target = st.text_input(
            "🎯 ターゲット *", placeholder="例: Threads運用者、SNS発信を伸ばしたい20〜30代"
        )
        price = st.text_input("💰 価格 *", placeholder="例: 3,980円")
        contents = st.text_area(
            "📦 商品内容（含まれるもの）",
            height=80,
            placeholder="例: 分析ツール本体、AI分析機能、投稿出力機能、分析マニュアル(PDF)",
        )
        diff = st.text_area(
            "⚡ 差別化ポイント",
            height=60,
            placeholder="例: Threads特化の唯一のツール、AI要因分析、テンプレート自動生成",
        )
        extra = st.text_area(
            "📝 補足情報（任意）", height=50, placeholder="例: 返金保証あり、買い切り型"
        )
        submitted = st.form_submit_button(
            "🚀 プロンプトを生成する", type="primary", use_container_width=True
        )

    if submitted:
        if not name or not target or not price:
            st.error("商品名・ターゲット・価格は必須です。")
        else:
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


def _step2_prompt():
    """Step 2: プロンプト表示。"""
    st.markdown("### 📋 プロンプトが完成しました")
    data = st.session_state.get("product_data", {})
    prompt = build_chat_prompt(data)

    st.success("以下のプロンプトをコピーして、**Claude** や **ChatGPT** に貼り付けてください。")
    st.code(prompt, language="text")
    st.caption("💡 AIがHTMLコードを出力したら、次のステップで貼り付けます。")

    col1, col2 = st.columns(2)
    if col1.button("▶️ Step 3へ進む", type="primary", use_container_width=True):
        st.session_state["manual_step"] = 3
        st.rerun()
    if col2.button("◀️ 戻る", use_container_width=True):
        st.session_state["manual_step"] = 1
        st.rerun()


def _step3_paste():
    """Step 3: HTML貼り付け。"""
    st.markdown("### 📥 AIが生成したHTMLを貼り付け")
    st.info("AIチャットが出力した **HTMLコード全体** をコピーして、下に貼り付けてください。")

    html_input = st.text_area(
        "HTMLコード",
        height=250,
        placeholder="<!DOCTYPE html>...",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns(2)
    if col1.button("🔄 Brain/Note素材に変換", type="primary", use_container_width=True):
        if not html_input or "<html" not in html_input.lower():
            st.error("有効なHTMLを貼り付けてください。")
        else:
            with st.spinner("変換中..."):
                result = convert_html(html_input)
            st.session_state["manual_result"] = result
            st.session_state["manual_step"] = 4
            st.rerun()
    if col2.button("◀️ 戻る", use_container_width=True):
        st.session_state["manual_step"] = 2
        st.rerun()


def _step4_results():
    """Step 4: 結果表示。"""
    st.markdown("### 🎉 Brain/Note素材が完成しました！")
    result = st.session_state.get("manual_result", {})

    with st.expander("🖥️ LPプレビュー", expanded=True):
        html = result.get("lp.html", "")
        if html:
            st.components.v1.html(html, height=500, scrolling=True)

    st.markdown("### 📝 プラットフォーム別ドラフト")
    tab_b, tab_n, tab_g = st.tabs(["🧠 Brain用", "📒 Note用", "📖 投稿ガイド"])
    with tab_b:
        brain = result.get("brain_draft.md", "")
        st.markdown(brain)
        st.download_button("Brain用ドラフトをDL", brain, "brain_draft.md", use_container_width=True)
    with tab_n:
        note = result.get("note_draft.md", "")
        st.markdown(note)
        st.download_button("Note用ドラフトをDL", note, "note_draft.md", use_container_width=True)
    with tab_g:
        guide = result.get("posting_guide.md", "")
        st.markdown(guide)

    images = result.get("image_files", [])
    if images:
        st.markdown("### 🖼️ セクション画像")
        for img in images:
            if os.path.exists(img):
                st.image(img, caption=os.path.basename(img))

    st.divider()
    zip_bytes = create_manual_zip(result)
    st.download_button(
        "📦 全素材をZIPでダウンロード",
        zip_bytes,
        "synapse_lp_output.zip",
        "application/zip",
        use_container_width=True,
        type="primary",
    )

    st.markdown("")
    if st.button("🔄 最初からやり直す", use_container_width=True):
        for key in ["manual_step", "product_data", "manual_result"]:
            st.session_state.pop(key, None)
        st.rerun()
