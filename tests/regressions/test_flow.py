"""Test rnotes (flow)"""
import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, ".")
from rnotes.rnotes import generate_release_notes
from rnotes.utils import init_log

has_github_token = pytest.mark.skipif(
    "GITHUB_TOKEN" not in os.environ,
    reason="GITHUB_TOKEN environment variables is not defined",
)


@has_github_token
class TestFlow:
    """Test the full rnotes flow"""

    def test_flow_1(self, tmp_path):
        "Test the rnotes flow"
        input_dir = Path("./tests/collaterals")
        file_name = "test_flow.md"
        output_dir = tmp_path
        # Run flow:
        generate_release_notes(
            repository_name="dyeheske/dummy_tool",
            from_tag="v0.1",
            to_tag="v0.2",
            output_dir=output_dir,
            file_name=file_name,
            grammar_path=input_dir / "grammar.py",
            release_notes_path=input_dir / "release_notes.j2",
            additional_content_path=input_dir / "additional_content.py",
        )
        # Check results:
        result_path = output_dir / file_name
        assert result_path.is_file()
        golden_path = Path("./tests/golden") / "expected_release_notes_1.md"
        if "UPDATE_GOLDEN" in os.environ:
            golden_path.write_text(result_path.read_text())
            return
        assert result_path.read_text() == golden_path.read_text()
