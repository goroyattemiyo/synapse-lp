"""
Synapse - Streamlit メインUI
"""

import os

import streamlit as st

st.set_page_config(
    page_title="PostCraft ジェネレーター",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap');
    .stApp { font-family: 'Noto Sans JP', sans-serif; }
    .main-title {
        text-align: center; padding: 20px 0 10px;
        font-size: 2.2rem; font-weight: 900; color: #1a1a2e;
    }
    .main-sub {
        text-align: center; color: #666; font-size: 1rem;
        margin-bottom: 30px;
    }
    .sidebar-header {
        font-size: 0.85rem; font-weight: 700; color: #1a1a2e;
        margin-bottom: 8px; padding-bottom: 8px;
        border-bottom: 2px solid #667eea;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    """メインエントリポイント。"""
    st.sidebar.markdown('<div class="sidebar-header">🧠 PostCraft</div>', unsafe_allow_html=True)
    mode = st.sidebar.radio(
        "モードを選択",
        ["✨ 手動LP変換（おすすめ）", "⚡ LP自動生成（API）"],
        index=0,
        help="手動LP変換: APIキー不要で誰でも使えます",
    )

    if "API" in mode:
        st.sidebar.divider()
        st.sidebar.markdown("**🔑 APIキー設定**")
        api_key = st.sidebar.text_input(
            "Anthropic API Key",
            type="password",
            value=os.environ.get("ANTHROPIC_API_KEY", ""),
            label_visibility="collapsed",
        )
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        else:
            st.sidebar.caption("⚠️ APIキーが未設定です")

    st.sidebar.divider()
    st.sidebar.caption("v0.3.0 | 108テスト合格")

    st.markdown('<div class="main-title">🧠 PostCraft ジェネレーター</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-sub">Brain・Note向けの売れるLPコンテンツを自動生成</div>',
        unsafe_allow_html=True,
    )

    if "手動" in mode:
        from synapse.lp_ui_manual import render_manual_mode

        render_manual_mode()
    else:
        from synapse.lp_ui import render_lp_mode

        render_lp_mode()


if __name__ == "__main__":
    main()
