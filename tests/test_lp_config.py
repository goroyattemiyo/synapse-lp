"""LP用config のテスト"""

from synapse.config import (
    LP_CODER_MODEL,
    LP_MAX_ROUNDS,
    LP_MAX_TOKENS,
    LP_ORCHESTRATOR_MODEL,
    LP_REVIEWER_MODEL,
)


def test_lp_max_tokens_sufficient():
    assert LP_MAX_TOKENS >= 8192


def test_lp_max_rounds_positive():
    assert isinstance(LP_MAX_ROUNDS, int)
    assert LP_MAX_ROUNDS > 0


def test_lp_models_valid():
    for model in [LP_ORCHESTRATOR_MODEL, LP_CODER_MODEL, LP_REVIEWER_MODEL]:
        assert isinstance(model, str)
        assert "claude" in model
