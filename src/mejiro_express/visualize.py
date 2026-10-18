import json
import textwrap
from collections import defaultdict
from itertools import accumulate
from pathlib import Path
from typing import Any

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
    )
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
        )
    fig.suptitle(
        "Biru = paket biasa, merah = pecah-belah (fragile)", fontsize=9, y=1.02
    )
    fig.savefig(PLOTS / f"{name}_states.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_curves(res, name):
    if "hist_max" in res:  # GA: maksimum dan rata-rata populasi
        series = [("maksimum", res["hist_max"]), ("rata-rata", res["hist_avg"])]
        xlabel = "Generasi"
    else:
        series = [("objective function", res["history"])]
        xlabel = "Iterasi"
    fig, (full, zoom) = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax in (full, zoom):
        for label, values in series:
            ax.plot(values, label=label)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Nilai objective function")
        ax.legend()
    full.set_title(f"{name}: seluruh rentang")
    zoom.set_title(f"{name}: diperbesar (nilai >= 0)")
    top = max(max(values) for _, values in series)
    if top > 0:
        zoom.set_ylim(0, top * 1.05)
    fig.tight_layout()
    fig.savefig(PLOTS / f"{name}_objective.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def _moving_average(values, window):
    csum = [0.0, *accumulate(values)]
    out = []
    for i in range(len(values)):
        lo = max(0, i + 1 - window)
        out.append((csum[i + 1] - csum[lo]) / (i + 1 - lo))
    return out


def plot_probability(res, name):
    probs = res["exp_history"]
    fig, (raw, avg) = plt.subplots(1, 2, figsize=(12, 4.5))
    raw.scatter(range(len(probs)), probs, s=1, alpha=0.3)
    raw.set_title(f"{name}: e^(ΔE/T) per iterasi")
    avg.plot(_moving_average(probs, 200))
    avg.set_title(f"{name}: rata-rata bergerak (jendela 200)")
    for ax in (raw, avg):
        ax.set_xlabel("Iterasi")
        ax.set_ylabel("e^(ΔE/T)")
    fig.tight_layout()
    fig.savefig(PLOTS / f"{name}_exp.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_summary(groups):
    labels = list(groups)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.boxplot(
        [[r["final_score"] for r in rs] for rs in groups.values()], tick_labels=labels
    )
    ax1.set_title("Nilai akhir per konfigurasi (3 run)")
    ax1.set_ylabel("Nilai objective function akhir")
    ax2.bar(
        labels, [sum(r["duration"] for r in rs) / len(rs) for rs in groups.values()]
    )
    ax2.set_yscale("log")
    ax2.set_title("Durasi rata-rata per konfigurasi")
    ax2.set_ylabel("Durasi (detik, skala log)")
    for ax in (ax1, ax2):
        ax.tick_params(axis="x", labelrotation=60)
    fig.tight_layout()
    fig.savefig(PLOTS / "summary.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def main():
    PLOTS.mkdir(parents=True, exist_ok=True)
    groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for f in sorted(OUT.glob("*.json")):
        res = json.loads(f.read_text())
        plot_states(res, f.stem)
        plot_curves(res, f.stem)
        if "exp_history" in res:
            plot_probability(res, f.stem)
        groups[f.stem.rsplit("_run", 1)[0]].append(res)
    plot_summary(groups)
    print(
        f"{'konfigurasi':32} {'min':>8} {'mean':>8} {'max':>8} "
        f"{'durasi(s)':>10} {'valid':>6} {'stuck':>6}"
    )
    for cfg, rs in groups.items():
        sc = [r["final_score"] for r in rs]
        stuck = [r["stuck_count"] for r in rs if "stuck_count" in r]
        stuck_txt = f"{sum(stuck) / len(stuck):.1f}" if stuck else "-"
        n_valid = sum(r["final_state"]["valid"] for r in rs)
        mean_duration = sum(r["duration"] for r in rs) / len(rs)
        print(
            f"{cfg:32} {min(sc):8.1f} {sum(sc) / len(sc):8.1f} {max(sc):8.1f} "
            f"{mean_duration:10.2f} {f'{n_valid}/{len(rs)}':>6} {stuck_txt:>6}"
        )


if __name__ == "__main__":
    main()
