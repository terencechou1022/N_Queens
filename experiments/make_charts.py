"""讀取 results/benchmark.csv 產出 README 用的三張圖，存至 docs/images/。

1. success_rate.png：各演算法成功率隨 N 的變化
2. time_vs_n.png：成功案例的中位數求解時間隨 N 的變化（對數刻度）
3. convergence.png：三演算法在 n=20、seed=0 的收斂曲線

收斂曲線不走 CSV，以固定 seed 直接呼叫求解器重現。
執行方式（於專案根目錄）：python experiments/make_charts.py
"""
import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, NullFormatter, ScalarFormatter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nqueens import genetic_algorithm, hill_climbing, simulated_annealing

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "results" / "benchmark.csv"
IMG_DIR = ROOT / "docs" / "images"

# 演算法固定用色（經 CVD 驗證的類別色前三格），所有圖表一致
ALGOS = ["hill_climbing", "simulated_annealing", "genetic_algorithm"]
COLORS = {
    "hill_climbing": "#2a78d6",
    "simulated_annealing": "#eb6834",
    "genetic_algorithm": "#1baf7a",
}
LABELS = {
    "hill_climbing": "爬山演算法",
    "simulated_annealing": "模擬退火",
    "genetic_algorithm": "基因演算法",
}

# 圖表用色：墨色、格線、座標軸（淺色模式）
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft JhengHei", "Segoe UI", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "text.color": INK,
    "axes.labelcolor": INK_2,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": AXIS,
    "font.size": 11,
})


def style_axes(ax):
    """收斂視覺噪音：只留左下兩條軸線，格線退到資料後面。"""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def load_rows():
    with CSV_PATH.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def aggregate(rows):
    """回傳 {algo: {n: (成功率, 成功案例中位時間或 None)}}。"""
    cells = defaultdict(list)
    for row in rows:
        cells[(row["algorithm"], int(row["n"]))].append(row)
    stats = defaultdict(dict)
    for (algo, n), runs in cells.items():
        solved_times = [float(r["elapsed"]) for r in runs if r["solved"] == "1"]
        rate = len(solved_times) / len(runs) * 100
        median_time = statistics.median(solved_times) if solved_times else None
        stats[algo][n] = (rate, median_time)
    return stats


def log_xaxis(ax, all_ns):
    ax.set_xscale("log")
    ax.set_xticks(all_ns)
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.tick_params(axis="x", which="minor", bottom=False)


def chart_success_rate(stats, all_ns):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for algo in ALGOS:
        ns = sorted(stats[algo])
        rates = [stats[algo][n][0] for n in ns]
        ax.plot(ns, rates, color=COLORS[algo], linewidth=1.8,
                marker="o", markersize=6, label=LABELS[algo])
    log_xaxis(ax, all_ns)
    ax.set_ylim(-4, 104)
    ax.set_xlabel("N（棋盤大小，對數刻度）")
    ax.set_ylabel("成功率（%）")
    ax.set_title("60 秒預算內的成功率（每格 20 次重複）", color=INK)
    ax.legend(frameon=False, labelcolor=INK_2)
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "success_rate.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_time_vs_n(stats, all_ns):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for algo in ALGOS:
        pairs = [(n, stats[algo][n][1]) for n in sorted(stats[algo])
                 if stats[algo][n][1] is not None]
        ax.plot([p[0] for p in pairs], [p[1] for p in pairs],
                color=COLORS[algo], linewidth=1.8,
                marker="o", markersize=6, label=LABELS[algo])
    ax.axhline(60, color=MUTED, linewidth=1, linestyle="--")
    ax.text(all_ns[-1], 60, " 逾時上限 60 秒", color=MUTED,
            fontsize=9, va="bottom", ha="right")
    log_xaxis(ax, all_ns)
    ax.set_yscale("log")
    # 用純小數標示刻度，避免科學記號的負號在中文字型缺字
    ax.set_yticks([0.01, 0.1, 1, 10, 60])
    ax.yaxis.set_major_formatter(FormatStrFormatter("%g"))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("N（棋盤大小，對數刻度）")
    ax.set_ylabel("中位數求解時間（秒，對數刻度）")
    ax.set_title("成功案例的中位數求解時間（全數失敗的格子無資料點）", color=INK)
    ax.legend(frameon=False, labelcolor=INK_2)
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "time_vs_n.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def chart_convergence(n=20, seed=0):
    runs = [
        ("hill_climbing", "移動步數",
         hill_climbing.solve(n, seed=seed, time_limit=120)),
        ("simulated_annealing", "降溫步數",
         simulated_annealing.solve(n, seed=seed, time_limit=120)),
        ("genetic_algorithm", "世代數",
         genetic_algorithm.solve(n, seed=seed, time_limit=120)),
    ]
    y_max = max(max(r.history) for _, _, r in runs) * 1.06
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
    for ax, (algo, x_label, result) in zip(axes, runs):
        # 爬山的軌跡近兩千步且重啟頻繁，用細線才看得出結構
        line_width = 0.7 if algo == "hill_climbing" else 1.4
        ax.plot(range(len(result.history)), result.history,
                color=COLORS[algo], linewidth=line_width)
        outcome = "成功" if result.solved else f"未解（剩 {result.conflicts} 衝突）"
        ax.set_title(f"{LABELS[algo]}（{outcome}）", color=INK, fontsize=11)
        ax.set_xlabel(x_label)
        ax.set_ylim(0, y_max)
        style_axes(ax)
    axes[0].set_ylabel("衝突數")
    fig.suptitle(f"收斂曲線：n={n}、seed={seed}（爬山曲線的高值跳點為隨機重啟）",
                 color=INK, fontsize=12)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "convergence.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def print_summary_table(stats):
    """輸出 README 數據表用的 Markdown。"""
    print("| 演算法 | N | 成功率 | 中位數求解時間（秒） |")
    print("|---|---|---|---|")
    for algo in ALGOS:
        for n in sorted(stats[algo]):
            rate, median_time = stats[algo][n]
            time_str = f"{median_time:.2f}" if median_time is not None else "－"
            print(f"| {LABELS[algo]} | {n} | {rate:.0f}% | {time_str} |")


def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    stats = aggregate(rows)
    all_ns = sorted({int(r["n"]) for r in rows})
    chart_success_rate(stats, all_ns)
    chart_time_vs_n(stats, all_ns)
    chart_convergence()
    print(f"三張圖已輸出至 {IMG_DIR}\n")
    print_summary_table(stats)


if __name__ == "__main__":
    main()
