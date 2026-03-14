"""
Synapse - Streamlit メインUI
3モード切替のエントリポイント。
"""

import os

import streamlit as st

st.set_page_config(
    page_title="Synapse LP Generator",
    page_icon="🧠",
    layout="centered",
)


def main():
    """メインエントリポイント。"""
    st.title("🧠 Synapse LP Generator")

    # サイドバー: モード選択
    mode = st.sidebar.radio(
        "モード選択",
        ["手動LP変換", "LP自動生成（API）", "通常モード"],
        index=0,
    )

    # サイドバー: APIキー（API使用モード向け）
    if mode == "LP自動生成（API）":
        api_key = st.sidebar.text_input(
            "Anthropic API Key",
            type="password",
            value=os.environ.get("ANTHROPIC_API_KEY", ""),
        )
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        if not api_key:
            st.sidebar.warning("APIキーを入力してください")

    # モード描画
    if mode == "手動LP変換":
        from synapse.lp_ui_manual import render_manual_mode

        render_manual_mode()
    elif mode == "LP自動生成（API）":
        from synapse.lp_ui import render_lp_mode

        render_lp_mode()
    else:
        _render_normal_mode()


def _render_normal_mode():
    """通常モード: 自由記述の目標からコード生成。"""
    st.header("通常モード")
    st.markdown("目標を入力すると、3エージェントがコードを生成します。")

    goal = st.text_area(
        "達成したい目標を入力",
        height=150,
        placeholder="例: Pythonでフィボナッチ数列を計算する関数を作成",
    )

    if st.button("生成開始", type="primary", use_container_width=True):
        if not goal:
            st.warning("目標を入力してください。")
            return
        status = st.status("生成中...", expanded=True)
        try:
            from synapse.engine import run_synapse

            result = run_synapse(goal)
            files = result.get("files", {})
            approved = result.get("approved", False)
            status.update(
                label="完了!" if approved else "完了（未承認）",
                state="complete",
            )
            for name, content in files.items():
                with st.expander(name, expanded=True):
                    st.code(content, language="python" if name.endswith(".py") else "text")
            st.caption(f"ラウンド: {result.get('rounds', 0)} | 承認: {approved}")
        except Exception as e:
            status.update(label=f"エラー: {e}", state="error")


if __name__ == "__main__":
    main()
