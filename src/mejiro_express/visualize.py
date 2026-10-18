import json
import textwrap
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

plt.switch_backend("Agg")  # simpan ke file saja, tanpa GUI

OUT = Path(__file__).resolve().parents[2] / "output"
PLOTS = OUT / "plots"


def _faces(x, y, z, w, l, h):
    # 8 sudut balok -> 6 sisi (indeks sudut per sisi)
    v = [
        (x, y, z),
        (x + w, y, z),
        (x + w, y + l, z),
        (x, y + l, z),
        (x, y, z + h),
        (x + w, y, z + h),
        (x + w, y + l, z + h),
        (x, y + l, z + h),
    ]
    idx = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (2, 3, 7, 6),
        (1, 2, 6, 5),
        (0, 3, 7, 4),
    ]
    return [[v[i] for i in f] for f in idx]


def draw_state(ax, st, title):
    W, L, H = st["truck"]["dims"]
    ax.add_collection3d(
        Poly3DCollection(
            _faces(0, 0, 0, W, L, H),
            facecolors="none",
            edgecolors="black",
            linewidths=1,
        )
    )  # rangka kontainer truck
    outside = []
    for p in st["packages"]:
        if p["pos"] is None:
            outside.append(p["id"])
            continue
        (x, y, z), (w, l, h) = p["pos"], p["size"]
        ax.add_collection3d(
            Poly3DCollection(
                _faces(x, y, z, w, l, h),
                alpha=0.5,
                linewidths=0.4,
                facecolors="tab:red" if p["isFragile"] else "tab:blue",
                edgecolors="k",
            )
        )
    ax.set_xlim(0, W)
    ax.set_ylim(0, L)
    ax.set_zlim(0, H)
    ax.set_box_aspect((W, L, H))
    n_in = len(st["packages"]) - len(outside)
    ax.set_title(
        f"{title}\nvalue={st['inside_value']}  valid={st['valid']}  di dalam={n_in}",
        fontsize=9,
    )
    return outside


def plot_states(res, name):
    fig = plt.figure(figsize=(13, 6))
    for k, (key, t) in enumerate(
        (("initial_state", "State awal"), ("final_state", "State akhir")), 1
    ):
        ax = fig.add_subplot(1, 2, k, projection="3d")
        out = draw_state(ax, res[key], t)
        ax.text2D(
            0,
            -0.1,
            textwrap.fill("Di luar truk: " + (", ".join(out) or "-"), 60),
            transform=ax.transAxes,
            fontsize=7,
            va="top",
        )  # merah = fragile
    fig.savefig(PLOTS / f"{name}_states.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_curves(res, name):
    fig, ax = plt.subplots()
    if "hist_max" in res:  # GA: maksimum dan rata-rata populasi
        ax.plot(res["hist_max"], label="maksimum")
        ax.plot(res["hist_avg"], label="rata-rata")
        ax.set_xlabel("Generasi")
        ax.legend()
    else:
        ax.plot(res["history"])
        ax.set_xlabel("Iterasi")
    ax.set_ylabel("Nilai objective function")
    ax.set_title(name)
    fig.savefig(PLOTS / f"{name}_objective.png", dpi=120)
    plt.close(fig)
    if "exp_history" in res:  # khusus SA: e^(dE/T) per iterasi
        fig, ax = plt.subplots()
        ax.plot(res["exp_history"], linewidth=0.5)
        ax.set_xlabel("Iterasi")
        ax.set_ylabel("e^(ΔE/T)")
        ax.set_title(f"{name}: probabilitas")
        fig.savefig(PLOTS / f"{name}_exp.png", dpi=120)
        plt.close(fig)


def main():
    PLOTS.mkdir(parents=True, exist_ok=True)
    groups = defaultdict(list)
    for f in sorted(OUT.glob("*.json")):
        res = json.loads(f.read_text())
        plot_states(res, f.stem)
        plot_curves(res, f.stem)
        groups[f.stem.rsplit("_run", 1)[0]].append(res)
    # ringkasan per konfigurasi  untuk analisis konsistensi dan perbandingan durasi
    print(
        f"{'konfigurasi':32} {'min':>8} {'mean':>8} {'max':>8} {'durasi(s)':>10} valid"
    )
    for cfg, rs in groups.items():
        sc = [r["final_score"] for r in rs]
        print(
            f"{cfg:32} {min(sc):8.1f} {sum(sc) / len(sc):8.1f} {max(sc):8.1f} "
            f"{sum(r['duration'] for r in rs) / len(rs):10.2f} {sum(r['final_state']['valid'] for r in rs)}/{len(rs)}"
        )


if __name__ == "__main__":
    main()
