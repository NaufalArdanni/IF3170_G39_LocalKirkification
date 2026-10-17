import random
from dataclasses import dataclass, replace
ORIENTS = [(0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0)]

@dataclass(frozen=True)
class Package:
    id: str
    dims: tuple      # (w, l, h) asli sebelum rotasi (orient)
    value: int
    weight: int
    isFragile: bool
    eta: int
    orient: tuple = (0, 1, 2)   # indeks (x, y, z) dari dims

@dataclass(frozen=True)
class Truck:
    dims: tuple      # (W, L, H)
    maxCapacity: int

class State:
    def __init__(self, packages, truck):
        self.packages = list(packages)
        self.truck = truck
        self.pos = [None] * len(packages)   # pos[i] = (x, y, z) atau None kalau paket i di luar

    @staticmethod
    def random_init(packages, truck, p_inside=0.5):
        s = State(packages, truck)
        W, L, H = truck.dims
        for i in range(len(s.packages)):
            s.packages[i] = replace(s.packages[i], orient=random.choice(ORIENTS))
            w, l, h = s.size(i)
            # package bisa melayang/overlap, akan dihukum penalti
            if random.random() < p_inside and w <= W and l <= L and h <= H:
                s.pos[i] = (random.randint(0, W - w), random.randint(0, L - l),
                            random.randint(0, H - h))
        return s

    def size(self, i):
        p = self.packages[i]
        return tuple(p.dims[k] for k in p.orient)

    def rotate(self, i, axis):
        a, b = [(1, 2), (0, 2), (0, 1)][axis]
        o = list(self.packages[i].orient)
        o[a], o[b] = o[b], o[a]
        self.packages[i] = replace(self.packages[i], orient=tuple(o))

    def copy(self):
        s = State(self.packages, self.truck)
        s.pos = list(self.pos)
        return s
        
    def to_dict(self):  # pos None -> null di JSON, berarti paket di luar truk
        return {
            "truck": {"dims": list(self.truck.dims), "maxCapacity": self.truck.maxCapacity},
            "packages": [
                {"id": p.id, "dims": list(p.dims), "orient": list(p.orient),
                 "size": list(self.size(i)),   # ukuran setelah orientasi, memudahkan visualisasi
                 "pos": list(self.pos[i]) if self.pos[i] is not None else None,
                 "value": p.value, "weight": p.weight, "isFragile": p.isFragile, "eta": p.eta}
                for i, p in enumerate(self.packages)
            ],
        }