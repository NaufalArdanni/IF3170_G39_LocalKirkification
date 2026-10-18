"""Tests for constraints, objective and State helpers."""

import random

from mejiro_express.constraints import is_valid, violations
from mejiro_express.model import Package, State, Truck
from mejiro_express.objective import score

ZERO = {
    "out_of_bounds": 0,
    "overlap": 0,
    "floating": 0,
    "fragile_support": 0,
    "overweight": 0,
}


def test_all_outside_is_valid_and_scores_zero(
    packages: list[Package], truck: Truck
) -> None:
    s = State(packages, truck)
    assert violations(s) == ZERO
    assert is_valid(s)
    assert score(s) == 0


def test_valid_stack(packages: list[Package], truck: Truck) -> None:
    s = State(packages, truck)
    s.pos[0], s.pos[1], s.pos[2] = (0, 0, 0), (0, 0, 1), (5, 5, 0)
    assert violations(s) == ZERO
    assert is_valid(s)
    assert score(s) == 130


def test_fragile_cannot_support(packages: list[Package], truck: Truck) -> None:
    s = State(packages, truck)
    s.pos[0], s.pos[1], s.pos[2] = (0, 0, 0), (0, 0, 1), (0, 0, 3)
    assert violations(s) == ZERO | {"fragile_support": 1}
    assert not is_valid(s)
    assert score(s) == 60 + 40 + 30 - 1000


def test_floating(packages: list[Package], truck: Truck) -> None:
    s = State(packages, truck)
    s.pos[0], s.pos[1], s.pos[2] = (0, 0, 0), (0, 0, 1), (5, 5, 2)
    assert violations(s) == ZERO | {"floating": 1}


def test_partial_support_is_not_floating(packages: list[Package], truck: Truck) -> None:
    s = State(packages, truck)
    s.pos[0], s.pos[2] = (0, 0, 0), (2, 0, 1)
    assert violations(s) == ZERO


def test_out_of_bounds(packages: list[Package], truck: Truck) -> None:
    s = State(packages, truck)
    s.pos[0] = (9, 0, 0)
    assert violations(s) == ZERO | {"out_of_bounds": 1}


def test_overlap(packages: list[Package], truck: Truck) -> None:
    s = State(packages, truck)
    s.pos[0], s.pos[2] = (0, 0, 0), (1, 1, 0)
    assert violations(s) == ZERO | {"overlap": 1}


def test_overweight(packages: list[Package]) -> None:
    small = Truck(dims=(10, 20, 5), maxCapacity=10)
    s = State(packages, small)
    s.pos[0], s.pos[1] = (0, 0, 0), (5, 5, 0)
    assert violations(s) == ZERO | {"overweight": 1}


def test_rotate_and_copy_are_independent(packages: list[Package], truck: Truck) -> None:
    s = State(packages, truck)
    s.pos[0] = (0, 0, 0)
    s.rotate(0, 2)
    assert s.packages[0].orient == (1, 0, 2)
    assert s.size(0) == (4, 3, 1)
    t = s.copy()
    t.rotate(0, 0)
    t.pos[0] = (1, 1, 0)
    assert s.size(0) == (4, 3, 1)
    assert s.pos[0] == (0, 0, 0)
    assert t.size(0) != s.size(0)


def test_random_init_is_reproducible(packages: list[Package], truck: Truck) -> None:
    random.seed(42)
    a = State.random_init(packages, truck)
    random.seed(42)
    b = State.random_init(packages, truck)
    assert a.pos == b.pos
    assert [p.orient for p in a.packages] == [p.orient for p in b.packages]


def test_to_dict_marks_outside_packages_with_none(
    packages: list[Package], truck: Truck
) -> None:
    s = State(packages, truck)
    s.pos[0] = (0, 0, 0)
    d = s.to_dict()
    assert d["truck"]["dims"] == [10, 20, 5]
    assert d["packages"][0]["pos"] == [0, 0, 0]
    assert d["packages"][0]["size"] == [3, 4, 1]
    assert d["packages"][1]["pos"] is None
