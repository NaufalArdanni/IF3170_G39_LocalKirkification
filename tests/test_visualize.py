"""Tests for the plotting helpers."""

from pathlib import Path

import pytest

from mejiro_express import visualize


def test_moving_average_uses_a_trailing_window() -> None:
    assert visualize._moving_average([1, 1, 0, 0], 2) == [1.0, 1.0, 0.5, 0.0]


def test_curve_and_probability_plots_are_written(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(visualize, "PLOTS", tmp_path)
    sa = {"history": [-100, 0, 50, 60], "exp_history": [1.0, 0.2, 1.0]}
    ga = {"hist_max": [-50, 10, 20], "hist_avg": [-500, -5, 15]}
    visualize.plot_curves(sa, "sa")
    visualize.plot_probability(sa, "sa")
    visualize.plot_curves(ga, "ga")
    for expected in ("sa_objective.png", "sa_exp.png", "ga_objective.png"):
        assert (tmp_path / expected).is_file()
