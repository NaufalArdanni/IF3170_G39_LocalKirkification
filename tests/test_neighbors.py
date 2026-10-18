"""Tests for the neighbor generators."""

import random

from mejiro_express.model import Package, State, Truck
from mejiro_express.neighbors import all_neighbors, random_neighbor


def test_all_neighbors_count(packages: list[Package], truck: Truck) -> None:
    random.seed(0)
    s = State.random_init(packages, truck)
    assert len(all_neighbors(s, k_move=5)) == 3 + 9 + 5


def test_neighbors_do_not_mutate_original(
    packages: list[Package], truck: Truck
) -> None:
    random.seed(0)
    s = State.random_init(packages, truck)
    pos_before = list(s.pos)
    orient_before = [p.orient for p in s.packages]
    all_neighbors(s, k_move=20)
    for _ in range(50):
        random_neighbor(s)
    assert s.pos == pos_before
    assert [p.orient for p in s.packages] == orient_before
