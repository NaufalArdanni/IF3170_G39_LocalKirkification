import math

from mejiro_express.data import load
from mejiro_express.model import Package, Truck


def _fractional(items: list[tuple[float, float]], capacity: float) -> float:
    total = 0.0
    for value, cost in sorted(items, key=lambda it: it[0] / it[1], reverse=True):
        if capacity <= 0:
            break
        take = min(1.0, capacity / cost)
        total += value * take
        capacity -= cost * take
    return total


def upper_bound(packages: list[Package], truck: Truck) -> tuple[float, float, float]:
    by_weight = _fractional([(p.value, p.weight) for p in packages], truck.maxCapacity)
    by_volume = _fractional(
        [(p.value, math.prod(p.dims)) for p in packages], math.prod(truck.dims)
    )
    return by_weight, by_volume, min(by_weight, by_volume)


def main() -> None:
    packages, truck = load()
    by_weight, by_volume, bound = upper_bound(packages, truck)
    print(f"weight bound = {by_weight:.1f}")
    print(f"volume bound = {by_volume:.1f}")
    print(f"upper bound  = {bound:.1f}")


if __name__ == "__main__":
    main()
