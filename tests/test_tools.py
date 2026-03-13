"""tools.py のテスト"""

from synapse.tools import CODER_TOOLS, REVIEWER_TOOLS, execute_tool


def test_execute_write_file(sandbox):
    result = execute_tool(sandbox, "write_file", {"path": "f.txt", "content": "data"})
    assert "Written" in result


def test_execute_read_file(sandbox):
    sandbox.write_file("f.txt", "hello")
    result = execute_tool(sandbox, "read_file", {"path": "f.txt"})
    assert result == "hello"


def test_execute_run_command(sandbox):
    result = execute_tool(sandbox, "run_command", {"command": "echo test"})
    assert "test" in result


def test_execute_unknown_tool(sandbox):
    result = execute_tool(sandbox, "delete_file", {"path": "x"})
    assert "Unknown tool" in result


def test_coder_tools_has_write():
    names = [t["name"] for t in CODER_TOOLS]
    assert "write_file" in names
    assert "read_file" in names
    assert "run_command" in names


def test_reviewer_tools_no_write():
    names = [t["name"] for t in REVIEWER_TOOLS]
    assert "write_file" not in names
    assert "read_file" in names
