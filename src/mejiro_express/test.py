import random
from model import Package, Truck, State
from constraints import violations, is_valid
from objective import score

truck = Truck(dims=(10, 20, 5), maxCapacity=500)
packages = [
    Package(id="A", dims=(3, 4, 1), orient=(0, 1, 2), value=60, weight=5, isFragile=False, eta=3),
    Package(id="B", dims=(2, 2, 2), orient=(0, 1, 2), value=40, weight=8, isFragile=True,  eta=1),
    Package(id="C", dims=(2, 2, 1), orient=(0, 1, 2), value=30, weight=2, isFragile=False, eta=2),
]

# State manual: semua paket awalnya di luar (pos = None)
s = State(packages, truck)
s.pos[0] = (0, 0, 0)   # A di alas truk
s.pos[1] = (0, 0, 1)   # B di atas A (A tidak fragile -> boleh)
s.pos[2] = (0, 0, 3)   # C di atas B (B fragile -> melanggar)
print(violations(s))   # fragile_support = 1, sisanya 0
print(is_valid(s))     # False
print(score(s))        # 60 + 40 + 30 - 1000 = -870

# Perbaiki: pindahkan C ke alas truk
s.pos[2] = (5, 5, 0)
print(violations(s), is_valid(s), score(s))   # semua 0, True, 130

# Melayang: C di z=2 melayang
s.pos[2] = (5, 5, 2)
print(violations(s)["floating"])   # 1

# Rotasi: axis 0=x, 1=y, 2=z
s.rotate(0, 2)                     # rotasi paket A terhadap sumbu z
print(s.packages[0].orient, s.size(0))   # (1, 0, 2) (4, 3, 1)

# copy() harus independen
t = s.copy()
t.rotate(0, 0)
print(s.size(0), t.size(0))        # ukuran s tidak berubah, t berubah

# State awal random (pakai seed)
random.seed(42)
r = State.random_init(packages, truck)
print(r.pos, [p.orient for p in r.packages])
print(violations(r), score(r))