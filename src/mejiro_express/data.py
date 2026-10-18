import json
import random
from pathlib import Path

from mejiro_express.model import Package, Truck

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "packages.json"


def generate(path=DATA_PATH, n=30, seed=2026):
    rng = random.Random(seed)  # tidak mengganggu random.seed di algoritma
    truck = {"dims": [10, 20, 5], "maxCapacity": 200}
    pkgs = [
        {
            "id": f"P{i:02d}",
            "dims": [
                rng.randint(2, 5) for _ in range(3)
            ],  # min 2, max 5: selalu muat di tinggi truk (5) lewat rotasi
            "value": rng.randint(10, 100),
            "weight": rng.randint(5, 20),
            "isFragile": rng.random() < 0.2,  # sekitar 20% pecah-belah
            "eta": rng.randint(1, 7),
        }
        for i in range(n)
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"truck": truck, "packages": pkgs}, indent=2))
    return path


def load(path=DATA_PATH):
    d = json.loads(Path(path).read_text())
    truck = Truck(dims=tuple(d["truck"]["dims"]), maxCapacity=d["truck"]["maxCapacity"])
    packages = [
        Package(
            id=p["id"],
            dims=tuple(p["dims"]),
            value=p["value"],
            weight=p["weight"],
            isFragile=p["isFragile"],
            eta=p["eta"],
        )
        for p in d["packages"]
    ]  # orient default (0,1,2)
    return packages, truck


if __name__ == "__main__":
    print("ditulis ke", generate())
