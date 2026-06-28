"""Unit tests for headroom.gate_config — loading ~/.config/headroom/env."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from headroom.gate_config import load_gate_config


class TestLoadGateConfig:
    """Unit tests for ``load_gate_config()``."""

    @pytest.fixture(autouse=True)
    def _clean_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Remove gate vars so each test starts from a clean slate."""
        for var in (
            "HEADROOM_API_KEY",
            "HEADROOM_ENCRYPTION_KEY",
            "HEADROOM_PROXY_URL",
            "NEO4J_URI",
            "NEO4J_USER",
            "NEO4J_PASSWORD",
            "QDRANT_URL",
        ):
            monkeypatch.delenv(var, raising=False)

    def _write_env_file(self, tmp_path: Path, content: str) -> Path:
        """Create a .config/headroom/env file and return its parent path."""
        env_dir = tmp_path / ".config" / "headroom"
        env_dir.mkdir(parents=True)
        env_file = env_dir / "env"
        env_file.write_text(content)
        return tmp_path

    # --- file exists scenarios ------------------------------------------

    def test_loads_all_standard_vars(self, monkeypatch, tmp_path):
        """All standard gate vars are loaded from the env file."""
        base = self._write_env_file(
            tmp_path,
            """HEADROOM_API_KEY="hr_test_key_123"
HEADROOM_ENCRYPTION_KEY="test_encryption_key_base64_test_="
HEADROOM_PROXY_URL="http://localhost:8787"
NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="testpassword"
QDRANT_URL="http://localhost:6333"
""",
        )
        home = base
        with patch.object(Path, "home", return_value=home):
            load_gate_config()

        assert os.environ["HEADROOM_API_KEY"] == "hr_test_key_123"
        assert os.environ["HEADROOM_ENCRYPTION_KEY"] == "test_encryption_key_base64_test_="
        assert os.environ["HEADROOM_PROXY_URL"] == "http://localhost:8787"
        assert os.environ["NEO4J_URI"] == "bolt://localhost:7687"
        assert os.environ["NEO4J_USER"] == "neo4j"
        assert os.environ["NEO4J_PASSWORD"] == "testpassword"
        assert os.environ["QDRANT_URL"] == "http://localhost:6333"

    def test_strips_single_quotes(self, monkeypatch, tmp_path):
        """Single-quoted values are loaded without the quotes."""
        base = self._write_env_file(
            tmp_path,
            "NEO4J_PASSWORD='devpassword'",
        )
        home = base
        with patch.object(Path, "home", return_value=home):
            load_gate_config()

        assert os.environ["NEO4J_PASSWORD"] == "devpassword"

    def test_strips_double_quotes(self, monkeypatch, tmp_path):
        """Double-quoted values are loaded without the quotes."""
        base = self._write_env_file(
            tmp_path,
            'HEADROOM_API_KEY="hr_abc123"',
        )
        home = base
        with patch.object(Path, "home", return_value=home):
            load_gate_config()

        assert os.environ["HEADROOM_API_KEY"] == "hr_abc123"

    def test_unquoted_values(self, monkeypatch, tmp_path):
        """Values without quotes are loaded as-is."""
        base = self._write_env_file(
            tmp_path,
            "NEO4J_PASSWORD=devpassword",
        )
        home = base
        with patch.object(Path, "home", return_value=home):
            load_gate_config()

        assert os.environ["NEO4J_PASSWORD"] == "devpassword"

    def test_respects_existing_env_vars(self, monkeypatch, tmp_path):
        """Shell-exported values are NOT overwritten by the file."""
        monkeypatch.setenv("NEO4J_PASSWORD", "shell_password")

        base = self._write_env_file(
            tmp_path,
            'NEO4J_PASSWORD="file_password"',
        )
        home = base
        with patch.object(Path, "home", return_value=home):
            load_gate_config()

        # Shell value wins
        assert os.environ["NEO4J_PASSWORD"] == "shell_password"

    def test_ignores_comments_and_blank_lines(self, monkeypatch, tmp_path):
        """Comments and blank lines are skipped."""
        base = self._write_env_file(
            tmp_path,
            """
# This is a comment

NEO4J_USER="neo4j"

# Another comment

NEO4J_PASSWORD="secret123"
# More comments

""",
        )
        home = base
        with patch.object(Path, "home", return_value=home):
            load_gate_config()

        assert os.environ["NEO4J_USER"] == "neo4j"
        assert os.environ["NEO4J_PASSWORD"] == "secret123"

    def test_malformed_lines_ignored(self, monkeypatch, tmp_path):
        """Lines without '=' sign are silently ignored."""
        base = self._write_env_file(
            tmp_path,
            """SOMETHING_WEIRD
NEO4J_USER="neo4j"
=empty_key
""",
        )
        home = base
        with patch.object(Path, "home", return_value=home):
            load_gate_config()

        assert os.environ["NEO4J_USER"] == "neo4j"
        assert "SOMETHING_WEIRD" not in os.environ

    # --- file missing scenarios -----------------------------------------

    def test_noop_when_file_missing(self, monkeypatch, tmp_path):
        """No exception when ~/.config/headroom/env doesn't exist."""
        with patch.object(Path, "home", return_value=tmp_path):
            load_gate_config()  # must not raise

        assert "NEO4J_PASSWORD" not in os.environ

    def test_env_already_set_when_file_missing(self, monkeypatch, tmp_path):
        """Pre-existing env vars survive when file is missing."""
        monkeypatch.setenv("NEO4J_PASSWORD", "already_set")

        with patch.object(Path, "home", return_value=tmp_path):
            load_gate_config()

        assert os.environ["NEO4J_PASSWORD"] == "already_set"

    # --- edge cases ----------------------------------------------------

    def test_value_with_equals_sign(self, monkeypatch, tmp_path):
        """Values containing '=' are preserved (only first '=' splits)."""
        base = self._write_env_file(
            tmp_path,
            'HEADROOM_ENCRYPTION_KEY="key_with_=_inside="',
        )
        home = base
        with patch.object(Path, "home", return_value=home):
            load_gate_config()

        assert os.environ["HEADROOM_ENCRYPTION_KEY"] == "key_with_=_inside="

    def test_value_with_spaces(self, monkeypatch, tmp_path):
        """Quoted values with spaces are preserved."""
        base = self._write_env_file(
            tmp_path,
            'HEADROOM_PROXY_URL="http://localhost:8787"',
        )
        home = base
        with patch.object(Path, "home", return_value=home):
            load_gate_config()

        assert os.environ["HEADROOM_PROXY_URL"] == "http://localhost:8787"
