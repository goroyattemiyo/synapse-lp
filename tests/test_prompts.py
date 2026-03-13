"""prompts.py のテスト"""

from synapse.prompts import (
    CODER_SYSTEM,
    ENV_CONTEXT,
    ORCHESTRATOR_SYSTEM,
    REVIEWER_SYSTEM,
)


def test_orchestrator_system_not_empty():
    assert len(ORCHESTRATOR_SYSTEM) > 100


def test_coder_system_contains_env_context():
    assert "Python" in CODER_SYSTEM
    assert "write_file" in CODER_SYSTEM


def test_reviewer_system_contains_approved_keyword():
    assert "APPROVED" in REVIEWER_SYSTEM


def test_env_context_not_empty():
    assert len(ENV_CONTEXT) > 10


def test_all_prompts_contain_env():
    for prompt in [ORCHESTRATOR_SYSTEM, CODER_SYSTEM, REVIEWER_SYSTEM]:
        assert "実行環境" in prompt
