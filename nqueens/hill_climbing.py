"""最陡爬升爬山演算法（steepest-ascent hill climbing）搭配隨機重啟。

每一步掃描整個鄰域（n 行 × (n-1) 個新位置），移動到衝突數最少的鄰居；
卡在局部最佳解或高原時隨機重啟。單步需評估 O(n^2) 個鄰居、每個鄰居的
衝突計算為 O(n^2)，因此單步成本為 O(n^4)，是三種演算法中對 N 最敏感的。
"""
import random
import time

from nqueens.core import SolveResult, count_conflicts, random_board


def _best_neighbor(current: list[int], current_conflicts: int):
    """掃描全鄰域，回傳衝突數最少的鄰居；發現 0 衝突的鄰居時提早回傳。

    若沒有任何鄰居嚴格優於目前狀態，回傳 (None, current_conflicts)。
    """
    n = len(current)
    best = None
    min_conflicts = current_conflicts

    for col in range(n):        # 第幾行的皇后要移動
        for row in range(n):    # 移動到第幾列的位置
            if row == current[col]:
                continue        # 跳過原本的位置
            neighbor = current.copy()
            neighbor[col] = row
            conflicts = count_conflicts(neighbor)
            if conflicts == 0:
                return neighbor, conflicts  # 全域最佳解，直接回傳
            if conflicts < min_conflicts:
                min_conflicts = conflicts
                best = neighbor

    return best, min_conflicts


def solve(n: int, seed: int | None = None, max_restarts: int = 1000,
          time_limit: float | None = None) -> SolveResult:
    """以隨機重啟爬山法求解 n 皇后。

    iterations 定義為累計的移動步數（不含重啟）。
    history 記錄每次狀態更新後的目前衝突數，重啟時會跳回高值，
    因此可以從收斂曲線上直接看出重啟行為。
    """
    rng = random.Random(seed)
    start = time.perf_counter()
    iterations = 0
    history: list[int] = []
    current: list[int] = []
    current_conflicts = 0

    for _ in range(max_restarts):
        # 隨機重啟：產生新的初始棋盤
        current = random_board(n, rng)
        current_conflicts = count_conflicts(current)
        history.append(current_conflicts)

        # 爬山過程
        while True:
            if current_conflicts == 0:
                return SolveResult(current, 0, iterations,
                                   time.perf_counter() - start, history)
            if time_limit is not None and time.perf_counter() - start > time_limit:
                return SolveResult(current, current_conflicts, iterations,
                                   time.perf_counter() - start, history,
                                   timed_out=True)
            neighbor, neighbor_conflicts = _best_neighbor(current, current_conflicts)
            if neighbor is not None and neighbor_conflicts == 0:
                iterations += 1
                history.append(0)
                return SolveResult(neighbor, 0, iterations,
                                   time.perf_counter() - start, history)
            # 沒有嚴格更好的鄰居：卡在局部最佳解，跳出進行重啟
            if neighbor is None or neighbor_conflicts >= current_conflicts:
                break
            current = neighbor
            current_conflicts = neighbor_conflicts
            iterations += 1
            history.append(current_conflicts)

    return SolveResult(current, current_conflicts, iterations,
                       time.perf_counter() - start, history)
