"""
Synapse - Streamlit メインUI
"""

import os

import streamlit as st

st.set_page_config(
    page_title="シナプス LP ジェネレーター",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# カスタムCSS
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
    .mode-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px; padding: 24px; color: white;
        margin-bottom: 16px;
    }
    .mode-card h3 { margin: 0 0 8px; font-size: 1.1rem; }
    .mode-card p { margin: 0; font-size: 0.85rem; opacity: 0.9; }
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
    # サイドバー
    st.sidebar.markdown('<div class="sidebar-header">🧠 シナプス LP</div>', unsafe_allow_html=True)
    mode = st.sidebar.radio(
        "モードを選択",
        ["✨ 手動LP変換", "⚡ LP自動生成（API）", "🔧 通常モード"],
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

    # メインエリア
    st.markdown(
        '<div class="main-title">🧠 シナプス LP ジェネレーター</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="main-sub">Brain・Note向けの売れるLPコンテンツを自動生成</div>',
        unsafe_allow_html=True,
    )

    if "手動" in mode:
        from synapse.lp_ui_manual import render_manual_mode

        render_manual_mode()
    elif "API" in mode:
        from synapse.lp_ui import render_lp_mode

        render_lp_mode()
    else:
        _render_normal_mode()


def _render_normal_mode():
    """通常モード。"""
    st.markdown("### 🔧 通常モード")
    st.info("目標を入力すると、3エージェントがコードを自動生成します。")
    goal = st.text_area(
        "達成したい目標", height=120, placeholder="例: Pythonで売上データを分析するスクリプト"
    )
    if st.button("🚀 生成開始", type="primary", use_container_width=True):
        if not goal:
            st.warning("目標を入力してください。")
            return
        with st.status("生成中...", expanded=True) as status:
            try:
                from synapse.engine import run_synapse

                result = run_synapse(goal)
                files = result.get("files", {})
                approved = result.get("approved", False)
                status.update(
                    label="✅ 完了!" if approved else "⚠️ 完了（未承認）", state="complete"
                )
                for name, c in files.items():
                    with st.expander(f"📄 {name}", expanded=True):
                        st.code(c, language="python" if name.endswith(".py") else "text")
            except Exception as e:
                status.update(label=f"❌ エラー: {e}", state="error")


if __name__ == "__main__":
    main()
