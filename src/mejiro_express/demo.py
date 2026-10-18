import json
import random
from pathlib import Path

from mejiro_express.constraints import is_valid
from mejiro_express.data import load
from mejiro_express.genetic_algorithm import genetic_algorithm
from mejiro_express.hill_climbing import steepest_ascent
from mejiro_express.model import State
from mejiro_express.simulated_annealing import simulated_annealing

OUT = Path(__file__).resolve().parents[2] / "output"  # root repo/output


def save(name, res):
    # State diubah pakai to_dict()
    out = {k: v for k, v in res.items() if k not in ("initial_state", "final_state")}
    for k in ("initial_state", "final_state"):
        st = res[k]
        out[k] = st.to_dict()
        out[k]["valid"] = is_valid(st)
        out[k]["inside_value"] = sum(
            p.value
            for p, pos in zip(st.packages, st.pos, strict=True)
            if pos is not None
        )

    big = (
        "history",
        "hist_max",
        "hist_avg",
        "exp_history",
    )  # list panjang: satu baris per key
    small = ", ".join(f'"{k}": {json.dumps(v)}' for k, v in out.items() if k not in big)
    rest = [f'"{k}": {json.dumps(v)}' for k, v in out.items() if k in big]
    OUT.mkdir(exist_ok=True)
    (OUT / f"{name}.json").write_text("{\n" + ",\n".join([small, *rest]) + "\n}")

    it = res.get("iterations", res.get("generations", "-"))
    print(
        f"{name}: score={res['final_score']} valid={out['final_state']['valid']} "
        f"iter={it} t={res['duration']:.2f}s"
    )


def main():
    packages, truck = load()

    # Non-GA: 3 run. HC dan SA memakai state awal yang sama per run.
    for r in range(1, 4):
        random.seed(r)
        init = State.random_init(packages, truck)
        save(f"hc_run{r}", steepest_ascent(init))
        random.seed(100 + r)  # seed SA terpisah dari HC, agar acak
        save(f"sa_run{r}", simulated_annealing(init, t0=1000.0))

    # GA: kontrol populasi (variasi iterasi) lalu kontrol iterasi (variasi populasi), masing-masing 3 run
    groups = {
        "ctrlpop": [(50, g) for g in (50, 100, 200)],
        "ctrliter": [(p, 100) for p in (20, 50, 100)],
    }
    for grp, cfgs in groups.items():
        for pop, gen in cfgs:
            for r in range(1, 4):
                random.seed(r)
                save(
                    f"ga_{grp}_pop{pop}_gen{gen}_run{r}",
                    genetic_algorithm(packages, truck, pop, gen),
                )


if __name__ == "__main__":
    main()
