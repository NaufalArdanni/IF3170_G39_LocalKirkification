"""Tests for the command-line interface."""

from pathlib import Path

import pytest

from mejiro_express import data
from mejiro_express.__main__ import main


def test_help_lists_every_command(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert all(cmd in out for cmd in ("generate", "run", "visualize"))


def test_missing_command_is_an_error() -> None:
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_generate_writes_a_loadable_instance(tmp_path: Path) -> None:
    target = tmp_path / "instance.json"
    assert main(["generate", "--n", "5", "--seed", "1", "--output", str(target)]) == 0
    packages, truck = data.load(target)
    assert len(packages) == 5
    assert truck.dims == (10, 20, 5)
    assert all(2 <= d <= 5 for p in packages for d in p.dims)
