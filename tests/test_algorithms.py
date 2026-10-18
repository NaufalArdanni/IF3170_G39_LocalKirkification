"""Smoke tests: each algorithm runs and returns self-consistent records."""

import random

from mejiro_express.genetic_algorithm import genetic_algorithm
from mejiro_express.hill_climbing import steepest_ascent
from mejiro_express.model import Package, State, Truck
from mejiro_express.objective import score
from mejiro_express.simulated_annealing import simulated_annealing


def _init(packages: list[Package], truck: Truck) -> State:
    random.seed(0)
    state: State = State.random_init(packages, truck)
    return state


def test_steepest_ascent(packages: list[Package], truck: Truck) -> None:
    init = _init(packages, truck)
    res = steepest_ascent(init, max_iter=20, k_move=20)
    assert res["final_score"] >= score(init)
    assert res["final_score"] == score(res["final_state"])
    assert len(res["history"]) == res["iterations"] + 1


def test_simulated_annealing(packages: list[Package], truck: Truck) -> None:
    init = _init(packages, truck)
    res = simulated_annealing(init, t0=100.0, max_iter=200)
    assert len(res["history"]) == 201
    assert len(res["exp_history"]) == 200
    assert all(0.0 <= p <= 1.0 for p in res["exp_history"])
    assert res["final_score"] >= score(init)
    assert res["final_score"] == score(res["final_state"])


def test_genetic_algorithm(packages: list[Package], truck: Truck) -> None:
    random.seed(0)
    res = genetic_algorithm(packages, truck, pop_size=6, generations=5)
    assert res["pop_size"] == 6
    assert res["generations"] == 5
    assert len(res["hist_max"]) == len(res["hist_avg"])
    assert res["final_score"] >= res["hist_max"][0]
    assert res["final_score"] == score(res["final_state"])
