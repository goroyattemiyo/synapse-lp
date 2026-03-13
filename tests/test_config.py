"""config.py のテスト"""
from synapse.config import (
    CODER_MODEL,
    COMMAND_TIMEOUT,
    MAX_FILE_READ_SIZE,
    MAX_ROUNDS,
    MAX_TOKENS,
    MAX_TOOL_ITERATIONS,
    ORCHESTRATOR_MODEL,
    REVIEWER_MODEL,
    STDERR_LIMIT,
    STDOUT_LIMIT,
)


def test_max_rounds_positive_int():
    assert isinstance(MAX_ROUNDS, int)
    assert MAX_ROUNDS > 0


def test_max_tool_iterations_positive_int():
    assert isinstance(MAX_TOOL_ITERATIONS, int)
    assert MAX_TOOL_ITERATIONS > 0


def test_max_tokens_minimum():
    assert isinstance(MAX_TOKENS, int)
    assert MAX_TOKENS >= 1024


def test_command_timeout_positive():
    assert isinstance(COMMAND_TIMEOUT, int)
    assert COMMAND_TIMEOUT > 0


def test_file_read_size_positive():
    assert isinstance(MAX_FILE_READ_SIZE, int)
    assert MAX_FILE_READ_SIZE > 0


def test_stdout_stderr_limits():
    assert isinstance(STDOUT_LIMIT, int)
    assert isinstance(STDERR_LIMIT, int)
    assert STDOUT_LIMIT > 0
    assert STDERR_LIMIT > 0


def test_model_names_valid_format():
    for model in [ORCHESTRATOR_MODEL, CODER_MODEL, REVIEWER_MODEL]:
        assert isinstance(model, str)
        assert len(model) > 0
        assert "claude" in model
