import math
import random
import time

from mejiro_express.neighbors import random_neighbor
from mejiro_express.objective import score


def simulated_annealing(init, t0=100.0, alpha=0.999, max_iter=20000, stuck_limit=200):
    t_start = time.time()
    cur, cur_sc = init.copy(), score(init)
    best, best_sc = cur, cur_sc
    hist, probs = [cur_sc], []
    T, no_gain, stuck, is_stuck = t0, 0, 0, False
    for _ in range(max_iter):
        n = random_neighbor(cur)
        delta = score(n) - cur_sc
        p = 1.0 if delta > 0 else math.exp(delta / T)  # peluang menerima (maks 1)
        probs.append(
            math.exp(min(delta / T, 50))
        )  # e^(dE/T) mentah untuk plot, dibatasi agar tidak overflow
        if random.random() < p:
            cur, cur_sc = n, cur_sc + delta
            if cur_sc > best_sc:
                best, best_sc = cur, cur_sc
            if delta > 0:
                no_gain, is_stuck = 0, False
            else:
                no_gain += 1  # diterima tapi tidak membaik (delta <= 0)
        else:
            no_gain += 1
        if no_gain >= stuck_limit and not is_stuck:
            stuck += 1  # satu stuck dihitung sekali
            is_stuck = True
        hist.append(cur_sc)
        T = max(T * alpha, 1e-9)  # jadwal geometrik
    return {
        "initial_state": init,
        "final_state": best,
        "final_score": best_sc,
        "history": hist,
        "exp_history": probs,
        "stuck_count": stuck,
        "iterations": max_iter,
        "t0": t0,
        "alpha": alpha,
        "duration": time.time() - t_start,
    }
