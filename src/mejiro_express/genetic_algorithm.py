import random
import time

from mejiro_express.model import State
from mejiro_express.neighbors import random_neighbor
from mejiro_express.objective import score


def _crossover(a, b):
    c = a.copy()
    for i in range(len(c.pos)):
        if random.random() < 0.5:  # uniform: ambil pos dan orient paket i dari b
            c.packages[i], c.pos[i] = b.packages[i], b.pos[i]
    return c


def genetic_algorithm(
    packages, truck, pop_size=50, generations=100, p_mut=0.3, k_tour=3
):
    t0 = time.time()
    pop = [State.random_init(packages, truck) for _ in range(pop_size)]
    scores = [score(s) for s in pop]
    init_best = pop[max(range(pop_size), key=scores.__getitem__)].copy()
    best, best_sc = init_best, max(scores)
    hist_max, hist_avg = [], []
    for _ in range(generations):
        hist_max.append(max(scores))
        hist_avg.append(sum(scores) / pop_size)
        elite = pop[max(range(pop_size), key=scores.__getitem__)]
        new = [elite.copy()]  # elitisme: individu terbaik selalu lolos
        while len(new) < pop_size:
            pa, pb = (
                pop[max(random.sample(range(pop_size), k_tour), key=scores.__getitem__)]
                for _ in range(2)
            )
            child = _crossover(pa, pb)
            if random.random() < p_mut:
                child = random_neighbor(child)
            new.append(child)
        pop, scores = new, [score(s) for s in new]
        if max(scores) > best_sc:
            best_sc = max(scores)
            best = pop[scores.index(best_sc)].copy()
    hist_max.append(max(scores))
    hist_avg.append(sum(scores) / pop_size)
    return {
        "initial_state": init_best,
        "final_state": best,
        "final_score": best_sc,
        "hist_max": hist_max,
        "hist_avg": hist_avg,
        "pop_size": pop_size,
        "generations": generations,
        "duration": time.time() - t0,
    }
