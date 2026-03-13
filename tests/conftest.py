"""共通fixture"""
import pytest

from synapse.sandbox import Sandbox


@pytest.fixture
def sandbox(tmp_path):
    sb = Sandbox()
    yield sb
    sb.cleanup()
