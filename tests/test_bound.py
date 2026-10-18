"""Tests for the upper bound."""

import pytest

from mejiro_express.bound import _fractional, upper_bound
from mejiro_express.model import Package, Truck


def test_fractional_knapsack_classic_example() -> None:
    items = [(60.0, 10.0), (100.0, 20.0), (120.0, 30.0)]
    assert _fractional(items, 50.0) == pytest.approx(240.0)


def test_fractional_with_zero_capacity() -> None:
    assert _fractional([(60.0, 10.0)], 0.0) == 0.0


def test_everything_fits_gives_total_value(
    packages: list[Package], truck: Truck
) -> None:
    assert upper_bound(packages, truck) == pytest.approx((130.0, 130.0, 130.0))


def test_weight_limit_binds(packages: list[Package]) -> None:
    tight = Truck(dims=(10, 20, 5), maxCapacity=5)
    by_weight, _, bound = upper_bound(packages, tight)
    assert by_weight == pytest.approx(66.0)
    assert bound == pytest.approx(66.0)
