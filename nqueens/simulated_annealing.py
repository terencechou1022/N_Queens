"""模擬退火演算法（simulated annealing），幾何降溫。

每一步隨機挑一個鄰居：比目前好就無條件接受，比目前差則以
exp(delta_e / t) 的機率接受；隨溫度下降，接受劣解的機率趨近於 0。
"""
import math
import random
import time

from nqueens.core import SolveResult, count_conflicts, random_board


def _random_neighbor(current: list[int], rng: random.Random) -> list[int]:
    """隨機挑一行的皇后，移動到該行任意其他位置，產生一個鄰居。"""
    n = len(current)
    col = rng.randint(0, n - 1)
    row = rng.randint(0, n - 1)
    while row == current[col]:
        row = rng.randint(0, n - 1)
    neighbor = current.copy()
    neighbor[col] = row
    return neighbor


def solve(n: int, seed: int | None = None, t_start: float = 100.0,
          alpha: float = 0.95, t_min: float = 1e-300,
          time_limit: float | None = None) -> SolveResult:
    """以模擬退火求解 n 皇后。

    終止條件為 t <= t_min。初版寫 while t > 0，實際上是靠浮點數
    下溢到 0 才終止（約 1.46 萬步）；這裡改為顯式參數，預設值對應
    約 1.36 萬步，維持相近的迭代預算。t 降到約 1e-2 以下後（約 180 步起），
    接受劣解的機率已趨近於 0，演算法尾段等同於「只接受更好的隨機鄰居」
    的貪婪搜索。

    iterations 定義為降溫步數。history 記錄每一步結束時的目前衝突數。
    """
    rng = random.Random(seed)
    start = time.perf_counter()
    t = t_start
    iterations = 0

    current = random_board(n, rng)
    current_conflicts = count_conflicts(current)
    history = [current_conflicts]

    # 退火過程
    while t > t_min:
        if current_conflicts == 0:
            break
        if time_limit is not None and time.perf_counter() - start > time_limit:
            return SolveResult(current, current_conflicts, iterations,
                               time.perf_counter() - start, history,
                               timed_out=True)
        neighbor = _random_neighbor(current, rng)
        neighbor_conflicts = count_conflicts(neighbor)
        # delta_e > 0 代表鄰居比較好
        delta_e = current_conflicts - neighbor_conflicts
        # 好的鄰居無條件接受；壞的鄰居以 exp(delta_e / t) 的機率接受
        if delta_e > 0 or rng.random() < math.exp(delta_e / t):
            current = neighbor
            current_conflicts = neighbor_conflicts
        t *= alpha
        iterations += 1
        history.append(current_conflicts)

    return SolveResult(current, current_conflicts, iterations,
                       time.perf_counter() - start, history)
