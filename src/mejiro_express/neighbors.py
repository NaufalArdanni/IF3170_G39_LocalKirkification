import random
from itertools import combinations


def _move(s, i):
    # pindahkan paket i keluar/masuk truk
    W, L, H = s.truck.dims
    w, l, h = s.size(i)
    fits = w <= W and l <= L and h <= H
    old = s.pos[i]
    for _ in range(10):  # coba beberapa kali sampai posisinya beda
        if old is not None and (not fits or random.random() < 0.2):
            new = None  # keluarkan dari truk
        elif fits:
            new = (
                random.randint(0, W - w),
                random.randint(0, L - l),
                random.randint(0, H - h),
            )
        else:
            return  # tidak muat dan sudah di luar: tidak ada move
        if new != old:
            s.pos[i] = new
            return


def _swap(s, i, j):
    s.pos[i], s.pos[j] = s.pos[j], s.pos[i]  # orientasi tetap melekat di paket


def random_neighbor(s):
    n = s.copy()
    kind = random.choice(("swap", "move", "rotate"))
    if kind == "swap" and len(n.pos) > 1:
        _swap(n, *random.sample(range(len(n.pos)), 2))
    elif kind == "rotate":
        n.rotate(random.randrange(len(n.pos)), random.randrange(3))
    else:
        _move(n, random.randrange(len(n.pos)))
    return n


def all_neighbors(s, k_move=100):
    # semua swap + semua rotasi + k_move sampel move (ruang koordinat terlalu besar untuk ditelusuri semua)
    out = []
    for i, j in combinations(range(len(s.pos)), 2):
        n = s.copy()
        _swap(n, i, j)
        out.append(n)
    for i in range(len(s.pos)):
        for axis in range(3):
            n = s.copy()
            n.rotate(i, axis)
            out.append(n)
    for _ in range(k_move):
        n = s.copy()
        _move(n, random.randrange(len(n.pos)))
        out.append(n)
    return out
