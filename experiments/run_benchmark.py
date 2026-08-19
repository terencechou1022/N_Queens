"""跑完整的 benchmark 實驗網格，輸出 results/benchmark.csv。

網格設計（依校準試跑結果定案）：
- hill_climbing / genetic_algorithm：N ∈ {8, 16, 20, 24, 32}，
  兩者在 n=32 已接近 60 秒預算的極限，保留該點以呈現可行性邊界
- simulated_annealing：N ∈ {8, 16, 20, 24, 32, 50, 64, 100}，
  單步成本低，多測大 N 以觀察固定迭代預算下成功率的衰減
- 每個組合重複 REPS 次，seed = 重複編號（0 到 REPS-1），結果可完全重現
- 單次求解超過 TIME_LIMIT 秒即中止並記為失敗（timed_out = 1）

執行方式（於專案根目錄）：python experiments/run_benchmark.py
"""
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nqueens import genetic_algorithm, hill_climbing, simulated_annealing

REPS = 20
TIME_LIMIT = 60.0
GRID = [
    ("hill_climbing", hill_climbing.solve, [8, 16, 20, 24, 32]),
    ("simulated_annealing", simulated_annealing.solve,
     [8, 16, 20, 24, 32, 50, 64, 100]),
    ("genetic_algorithm", genetic_algorithm.solve, [8, 16, 20, 24, 32]),
]
OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "benchmark.csv"


def main():
    OUT_PATH.parent.mkdir(exist_ok=True)
    total = sum(len(n_values) for _, _, n_values in GRID) * REPS
    done = 0
    start = time.perf_counter()

    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm", "n", "seed", "solved", "conflicts",
                         "iterations", "elapsed", "timed_out"])
        for name, solve, n_values in GRID:
            for n in n_values:
                for seed in range(REPS):
                    result = solve(n, seed=seed, time_limit=TIME_LIMIT)
                    writer.writerow([name, n, seed, int(result.solved),
                                     result.conflicts, result.iterations,
                                     f"{result.elapsed:.4f}",
                                     int(result.timed_out)])
                    f.flush()  # 逐列寫入，中斷時保留已完成的部分
                    done += 1
                    status = "成功" if result.solved else "失敗"
                    print(f"[{done}/{total}] {name} n={n} seed={seed} "
                          f"{status} {result.elapsed:.2f}s", flush=True)

    print(f"總耗時 {time.perf_counter() - start:.0f} 秒，結果已寫入 {OUT_PATH}")


if __name__ == "__main__":
    main()
