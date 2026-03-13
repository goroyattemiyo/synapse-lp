"""image_pipeline.py のテスト"""

from synapse.image_pipeline import (
    HAS_PILLOW,
    HAS_PLAYWRIGHT,
    extract_sections,
    extract_text_from_html,
    generate_manual_screenshot_guide,
)


class TestExtractSections:
    def test_single_section(self):
        html = '<section data-section="hero">Hello</section>'
        result = extract_sections(html)
        assert len(result) == 1
        assert result[0]["name"] == "hero"
        assert "Hello" in result[0]["content"]

    def test_multiple_sections(self):
        html = (
            '<div data-section="hero">Hero</div>'
            '<div data-section="problem">Problem</div>'
            '<section data-section="cta">CTA</section>'
        )
        result = extract_sections(html)
        assert len(result) == 3
        assert result[0]["name"] == "hero"
        assert result[2]["name"] == "cta"

    def test_no_sections(self):
        html = "<div>No data-section here</div>"
        result = extract_sections(html)
        assert len(result) == 0

    def test_nested_content(self):
        html = '<section data-section="features"><h2>Features</h2><p>Details</p></section>'
        result = extract_sections(html)
        assert len(result) == 1
        assert "Features" in result[0]["content"]


class TestExtractText:
    def test_strip_tags(self):
        html = "<h1>Title</h1><p>Body text</p>"
        text = extract_text_from_html(html)
        assert "Title" in text
        assert "Body text" in text
        assert "<" not in text

    def test_strip_style_script(self):
        html = "<style>body{color:red}</style><script>alert(1)</script><p>Clean</p>"
        text = extract_text_from_html(html)
        assert "Clean" in text
        assert "color" not in text
        assert "alert" not in text

    def test_empty_html(self):
        assert extract_text_from_html("") == ""


class TestManualGuide:
    def test_guide_with_sections(self):
        sections = [{"name": "hero", "content": ""}, {"name": "cta", "content": ""}]
        guide = generate_manual_screenshot_guide("lp.html", sections)
        assert "lp.html" in guide
        assert "hero" in guide
        assert "cta" in guide
        assert "800" in guide

    def test_guide_without_sections(self):
        guide = generate_manual_screenshot_guide("lp.html", [])
        assert "full_page.png" in guide

    def test_guide_is_markdown(self):
        guide = generate_manual_screenshot_guide("lp.html", [])
        assert guide.startswith("#")


class TestFlags:
    def test_has_playwright_is_bool(self):
        assert isinstance(HAS_PLAYWRIGHT, bool)

    def test_has_pillow_is_bool(self):
        assert isinstance(HAS_PILLOW, bool)
