from constraints import violations

def score(s, penalty=1000): # semakin besar penalty, landscape jadi datar dan hill-climbing sulit keluar dari state valid; semakin kecil penalty, solusi akhir bisa tidak valid.
    inside_value = sum(p.value for p, pos in zip(s.packages, s.pos) if pos is not None)
    return inside_value - penalty * sum(violations(s).values())