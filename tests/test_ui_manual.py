"""ui.py / lp_ui_manual.py のテスト"""


class TestUiImport:
    """UIモジュールがインポートできるか検証。"""

    def test_ui_importable(self):
        from synapse.ui import main

        assert callable(main)

    def test_manual_mode_importable(self):
        from synapse.lp_ui_manual import render_manual_mode

        assert callable(render_manual_mode)


class TestBuildChatPrompt:
    """プロンプト生成関数の検証。"""

    def test_prompt_contains_product_name(self):
        from synapse.lp_ui_manual import _build_chat_prompt

        data = {
            "name": "TestProduct",
            "target": "初心者",
            "price": "1000円",
            "contents": "ツール本体",
            "diff": "AI搭載",
            "extra": "",
        }
        prompt = _build_chat_prompt(data)
        assert "TestProduct" in prompt
        assert "初心者" in prompt
        assert "1000円" in prompt

    def test_prompt_contains_html_rules(self):
        from synapse.lp_ui_manual import _build_chat_prompt

        prompt = _build_chat_prompt({"name": "X", "target": "Y", "price": "Z"})
        assert "data-section" in prompt
        assert "hero" in prompt
        assert "プレースホルダー" in prompt

    def test_prompt_contains_12_sections(self):
        from synapse.lp_ui_manual import _build_chat_prompt

        prompt = _build_chat_prompt({"name": "X"})
        assert "ファーストビュー" in prompt
        assert "最終CTA" in prompt

    def test_prompt_extra_included(self):
        from synapse.lp_ui_manual import _build_chat_prompt

        data = {"name": "X", "extra": "返金保証あり"}
        prompt = _build_chat_prompt(data)
        assert "返金保証あり" in prompt


class TestConvertHtml:
    """HTML変換関数の検証。"""

    def test_convert_returns_all_keys(self):
        from synapse.lp_ui_manual import _convert_html

        html = """<html><body>
        <section data-section="hero"><h1>Test</h1></section>
        <section data-section="problem"><p>Problem</p></section>
        </body></html>"""
        result = _convert_html(html)
        assert "lp.html" in result
        assert "brain_draft.md" in result
        assert "note_draft.md" in result
        assert "posting_guide.md" in result
        assert "image_files" in result

    def test_convert_brain_contains_sections(self):
        from synapse.lp_ui_manual import _convert_html

        html = """<html><body>
        <section data-section="hero"><h1>Hello</h1></section>
        </body></html>"""
        result = _convert_html(html)
        assert "ファーストビュー" in result["brain_draft.md"]

    def test_convert_preserves_original_html(self):
        from synapse.lp_ui_manual import _convert_html

        html = "<html><body><h1>Original</h1></body></html>"
        result = _convert_html(html)
        assert result["lp.html"] == html


class TestManualZip:
    """ZIP生成関数の検証。"""

    def test_zip_contains_all_files(self):
        import io
        import zipfile

        from synapse.lp_ui_manual import _create_manual_zip

        result = {
            "lp.html": "<h1>Test</h1>",
            "brain_draft.md": "# Brain",
            "note_draft.md": "# Note",
            "posting_guide.md": "# Guide",
            "image_files": [],
        }
        zdata = _create_manual_zip(result)
        zf = zipfile.ZipFile(io.BytesIO(zdata))
        names = zf.namelist()
        assert "lp.html" in names
        assert "brain_draft.md" in names
        assert "note_draft.md" in names
        assert "posting_guide.md" in names
