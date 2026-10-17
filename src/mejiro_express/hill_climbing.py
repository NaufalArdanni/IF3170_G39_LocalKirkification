import time
from neighbors import all_neighbors
from objective import score

def steepest_ascent(init, max_iter=1000, k_move=100):
    t0 = time.time()
    cur, cur_sc = init.copy(), score(init)
    hist = [cur_sc]
    it = 0
    for it in range(1, max_iter + 1):
        best, best_sc = None, cur_sc
        for n in all_neighbors(cur, k_move):
            sc = score(n)
            if sc > best_sc:                 # harus lebih baik
                best, best_sc = n, sc
        if best is None:                     # tidak ada neighbor lebih baik: berhenti
            it -= 1
            break
        cur, cur_sc = best, best_sc
        hist.append(cur_sc)
    return dict(initial_state=init, final_state=cur, final_score=cur_sc,
                history=hist, duration=time.time() - t0, iterations=it)