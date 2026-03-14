"""
Synapse - LP生成UI（Streamlit）
"""

import io
import os
import zipfile

import streamlit as st


def render_lp_mode():
    """LP生成モードのUIを描画する。"""
    st.header("LP Generator Mode")
    st.markdown("商品情報を入力すると、LP用HTML・Brain/Noteドラフト・投稿ガイドを自動生成します。")

    product_info = st.text_area(
        "商品・サービス情報を入力",
        height=200,
        placeholder="例: AIを使った副業ノウハウ教材。ターゲットは副業初心者。価格4,980円。",
    )

    col1, col2 = st.columns(2)
    run_clicked = col1.button("LP生成開始", type="primary", use_container_width=True)
    clear_clicked = col2.button("クリア", use_container_width=True)

    if clear_clicked:
        st.session_state.pop("lp_result", None)
        st.rerun()

    if run_clicked and product_info:
        _run_lp_generation(product_info)

    if "lp_result" in st.session_state:
        _render_results(st.session_state["lp_result"])


def _run_lp_generation(product_info: str):
    """LP生成を実行する。"""
    status = st.status("LP生成中...", expanded=True)
    messages: list[str] = []

    def callback(role: str, msg: str):
        messages.append(f"[{role}] {msg[:100]}")
        status.write(f"**{role}**: {msg[:100]}")

    try:
        from synapse.lp_engine import run_postcraft

        result = run_postcraft(product_info, callback=callback)
        st.session_state["lp_result"] = result
        if result.get("approved"):
            status.update(label="LP生成完了!", state="complete")
        else:
            status.update(label="LP生成完了（未承認）", state="complete")
    except Exception as e:
        status.update(label=f"エラー: {e}", state="error")


def _render_results(result: dict):
    """生成結果を表示する。"""
    st.divider()
    st.subheader("生成結果")

    files = result.get("files", {})
    if not files:
        st.warning("ファイルが生成されませんでした。")
        return

    tab_names = list(files.keys())
    tabs = st.tabs(tab_names)

    for tab, name in zip(tabs, tab_names):
        with tab:
            content = files[name]
            if name.endswith(".html"):
                st.components.v1.html(content, height=600, scrolling=True)
                st.code(content, language="html")
            elif name.endswith(".md"):
                st.markdown(content)
                with st.expander("ソース表示"):
                    st.code(content, language="markdown")
            else:
                st.code(content)

    # 画像プレビュー
    image_files = result.get("image_files", [])
    if image_files:
        st.divider()
        st.subheader("セクション画像")
        for img_path in image_files:
            if os.path.exists(img_path):
                st.image(img_path, caption=os.path.basename(img_path))

    st.divider()
    zip_buffer = _create_zip(files, image_files)
    st.download_button(
        label="全ファイルをZIPダウンロード",
        data=zip_buffer,
        file_name="postcraft_output.zip",
        mime="application/zip",
        use_container_width=True,
    )

    rounds = result.get("rounds", 0)
    approved = result.get("approved", False)
    log_path = result.get("log_path", "")
    st.caption(f"ラウンド数: {rounds} | 承認: {approved} | ログ: {log_path}")


def _create_zip(
    files: dict[str, str],
    image_files: list[str] | None = None,
) -> bytes:
    """ファイル辞書と画像ファイルからZIPバイトを生成する。"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
        if image_files:
            for img_path in image_files:
                if os.path.exists(img_path):
                    arcname = "sections/" + os.path.basename(img_path)
                    zf.write(img_path, arcname)
    return buffer.getvalue()


def render_mode_selector():
    """通常モードとLPモードを切り替えるセレクタを描画する。"""
    mode = st.sidebar.radio(
        "モード選択",
        ["通常モード", "LP生成モード"],
        index=0,
    )
    return mode
