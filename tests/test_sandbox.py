"""sandbox.py のテスト"""

import platform

import pytest


def test_write_and_read_file(sandbox):
    result = sandbox.write_file("hello.txt", "Hello World")
    assert "Written" in result
    content = sandbox.read_file("hello.txt")
    assert content == "Hello World"


def test_write_nested_path(sandbox):
    result = sandbox.write_file("src/main.py", "print('hi')")
    assert "Written" in result
    content = sandbox.read_file("src/main.py")
    assert "print" in content


def test_read_nonexistent_file(sandbox):
    result = sandbox.read_file("nofile.txt")
    assert "Error" in result


def test_read_truncation(sandbox):
    big_content = "x" * 200_000
    sandbox.write_file("big.txt", big_content)
    result = sandbox.read_file("big.txt")
    assert "truncated" in result


def test_run_command_success(sandbox):
    sandbox.write_file("test.txt", "hello")
    if platform.system() == "Windows":
        result = sandbox.run_command("type test.txt")
    else:
        result = sandbox.run_command("cat test.txt")
    assert "hello" in result


@pytest.mark.skipif(platform.system() == "Windows", reason="timeout test unreliable on Windows")
def test_run_command_timeout(sandbox):
    result = sandbox.run_command("sleep 999")
    assert "timed out" in result or "Error" in result


def test_list_files(sandbox):
    sandbox.write_file("a.txt", "aaa")
    sandbox.write_file("b.txt", "bbb")
    files = sandbox.list_files()
    assert len(files) == 2


def test_cleanup(sandbox):
    workspace = sandbox.workspace
    sandbox.write_file("tmp.txt", "data")
    assert workspace.exists()
    sandbox.cleanup()
    assert not workspace.exists()
