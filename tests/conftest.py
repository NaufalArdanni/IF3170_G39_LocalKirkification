"""Shared fixtures."""

import pytest

from mejiro_express.model import Package, Truck


@pytest.fixture
def truck() -> Truck:
    """Truck from the spec's example (10 x 20 x 5, capacity 500)."""
    return Truck(dims=(10, 20, 5), maxCapacity=500)


@pytest.fixture
def packages() -> list[Package]:
    return [
        Package(id="A", dims=(3, 4, 1), value=60, weight=5, isFragile=False, eta=3),
        Package(id="B", dims=(2, 2, 2), value=40, weight=8, isFragile=True, eta=1),
        Package(id="C", dims=(2, 2, 1), value=30, weight=2, isFragile=False, eta=2),
    ]
