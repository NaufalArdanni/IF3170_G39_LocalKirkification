"""Smoke tests for the package entry point."""

import pytest

from mejiro_express.__main__ import main


def test_main_prints_placeholder(capsys: pytest.CaptureFixture[str]) -> None:
    """The placeholder CLI announces that it is not implemented."""
    main()
    assert "not implemented" in capsys.readouterr().out
