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
