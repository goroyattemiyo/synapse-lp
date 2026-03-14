"""lp_prompts.py のテスト"""

from synapse.lp_prompts import (
    LP_CODER_SYSTEM,
    LP_ORCHESTRATOR_SYSTEM,
    LP_REVIEWER_SYSTEM,
    LP_SECTION_TEMPLATE,
)


def test_lp_orchestrator_not_empty():
    assert len(LP_ORCHESTRATOR_SYSTEM) > 100


def test_lp_orchestrator_contains_target():
    assert "ターゲット" in LP_ORCHESTRATOR_SYSTEM


def test_lp_coder_contains_html_rules():
    assert "data-section" in LP_CODER_SYSTEM
    assert "lp.html" in LP_CODER_SYSTEM
    assert "brain_draft.md" in LP_CODER_SYSTEM
    assert "note_draft.md" in LP_CODER_SYSTEM


def test_lp_coder_contains_responsive():
    assert "レスポンシブ" in LP_CODER_SYSTEM


def test_lp_reviewer_contains_approved():
    assert "APPROVED" in LP_REVIEWER_SYSTEM


def test_lp_reviewer_checks_platform_constraints():
    assert "Brain" in LP_REVIEWER_SYSTEM
    assert "Note" in LP_REVIEWER_SYSTEM


def test_lp_section_template_has_firstview():
    assert "ファーストビュー" in LP_SECTION_TEMPLATE


def test_lp_section_template_has_cta():
    assert "CTA" in LP_SECTION_TEMPLATE


# === 新規テスト: プロンプトチューニング検証 ===


class TestCoderPlaceholderRules:
    """Coderプロンプトにプレースホルダールールが含まれるか検証。"""

    def test_placeholder_section_exists(self):
        assert "プレースホルダールール" in LP_CODER_SYSTEM

    def test_placeholder_format_example(self):
        assert "[利用者数を入力]" in LP_CODER_SYSTEM

    def test_testimonial_placeholder(self):
        assert "[お客様の名前" in LP_CODER_SYSTEM

    def test_price_placeholder(self):
        assert "[通常価格を入力]" in LP_CODER_SYSTEM

    def test_user_data_passthrough(self):
        assert "ユーザーが提供した情報はそのまま使用可" in LP_CODER_SYSTEM


class TestCoderImagePlaceholder:
    """Coderプロンプトに画像プレースホルダー仕様が含まれるか検証。"""

    def test_img_placeholder_class(self):
        assert "img-placeholder" in LP_CODER_SYSTEM

    def test_data_image_attribute(self):
        assert "data-image" in LP_CODER_SYSTEM


class TestCoderDataSectionValues:
    """data-section属性の必須値が明示されているか検証。"""

    def test_required_section_values(self):
        for val in [
            "hero",
            "problem",
            "empathy",
            "solution",
            "features",
            "proof",
            "testimonials",
            "comparison",
            "details",
            "offer",
            "faq",
            "cta",
        ]:
            assert val in LP_CODER_SYSTEM


class TestCoderCtaPlacement:
    """CTAボタン配置ルールが明示されているか検証。"""

    def test_cta_minimum_two(self):
        assert "hero と cta の最低2ヶ所" in LP_CODER_SYSTEM


class TestReviewerNewChecks:
    """Reviewerプロンプトの新規検証項目。"""

    def test_reviewer_checks_placeholder(self):
        assert "プレースホルダー" in LP_REVIEWER_SYSTEM

    def test_reviewer_checks_fake_numbers(self):
        assert "架空" in LP_REVIEWER_SYSTEM

    def test_reviewer_checks_img_placeholder(self):
        assert "img-placeholder" in LP_REVIEWER_SYSTEM

    def test_reviewer_cta_two_places(self):
        assert "hero と cta の最低2ヶ所" in LP_REVIEWER_SYSTEM
