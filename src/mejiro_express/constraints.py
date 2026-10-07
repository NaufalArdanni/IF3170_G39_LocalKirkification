from itertools import combinations

def _box(s, i): # helper: mengembalikan koordinat kotak paket i dalam bentuk (x1, y1, z1, x2, y2, z2)
    x, y, z = s.pos[i]
    w, l, h = s.size(i)
    return x, y, z, x + w, y + l, z + h

def violations(s):
    """Mengembalikan jumlah pelanggaran per jenis. Semua nol = state valid."""
    W, L, H = s.truck.dims
    ins = [i for i in range(len(s.pos)) if s.pos[i] is not None]
    boxes = {i: _box(s, i) for i in ins}
    v = dict(out_of_bounds=0, overlap=0, floating=0, fragile_support=0, overweight=0)

    for i in ins:
        x1, y1, z1, x2, y2, z2 = boxes[i]
        if x1 < 0 or y1 < 0 or z1 < 0 or x2 > W or y2 > L or z2 > H:
            v['out_of_bounds'] += 1          # menembus dinding

    for i, j in combinations(ins, 2):
        a, b = boxes[i], boxes[j]
        if all(a[k] < b[k + 3] and b[k] < a[k + 3] for k in range(3)):
            v['overlap'] += 1

    for i in ins:
        x1, y1, z1, x2, y2, _ = boxes[i]
        if z1 == 0:
            continue                          # di alas truk, otomatis punya support
        # support = paket j yang sisi atasnya tepat di z1
        sup = [j for j in ins if j != i and boxes[j][5] == z1
               and x1 < boxes[j][3] and boxes[j][0] < x2
               and y1 < boxes[j][4] and boxes[j][1] < y2]
        if not sup:
            v['floating'] += 1                # tidak ada satu pun titik alas yang punya support
        v['fragile_support'] += sum(s.packages[j].isFragile for j in sup)

    if sum(s.packages[i].weight for i in ins) > s.truck.maxCapacity:
        v['overweight'] = 1
    return v

def is_valid(s):
    return not any(violations(s).values())