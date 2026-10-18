import time

from mejiro_express.neighbors import all_neighbors
from mejiro_express.objective import score


def steepest_ascent(init, max_iter=1000, k_move=100):
    t0 = time.perf_counter()
    cur, cur_sc = init.copy(), score(init)
    hist = [cur_sc]
    iterations = 0
    for _ in range(max_iter):
        best, best_sc = None, cur_sc
        for n in all_neighbors(cur, k_move):
            sc = score(n)
            if sc > best_sc:  # harus lebih baik
                best, best_sc = n, sc
        if best is None:  # tidak ada neighbor lebih baik: berhenti
            break
        cur, cur_sc = best, best_sc
        hist.append(cur_sc)
        iterations += 1
    return {
        "initial_state": init,
        "final_state": cur,
        "final_score": cur_sc,
        "history": hist,
        "duration": time.perf_counter() - t0,
        "iterations": iterations,
    }
