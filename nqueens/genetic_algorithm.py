"""基因演算法（genetic algorithm），含自適應突變率。

以衝突數的倒數作為適應度做輪盤式選擇（fitness-proportionate selection），
單點交配產生子代；當族群最佳解停滯超過門檻時逐步調高突變率，
幫助族群跳出局部最佳解，這是標準流程之外自行加入的機制。
"""
import random
import time

from nqueens.core import SolveResult, count_conflicts, random_board


def _fitness(conflicts: int) -> float:
    """衝突數越少，適應度越高。"""
    return 1.0 / (conflicts + 1)


def _reproduce(parent_x: list[int], parent_y: list[int],
               rng: random.Random) -> list[int]:
    """單點交配：隨機決定切點，前段取一方、後段取另一方。"""
    c = rng.randint(0, len(parent_x) - 1)
    return parent_x[:c] + parent_y[c:]


def _mutate(child: list[int], rng: random.Random) -> list[int]:
    """隨機挑一行的皇后，移動到該行任意其他位置。"""
    n = len(child)
    col = rng.randint(0, n - 1)
    row = rng.randint(0, n - 1)
    while row == child[col]:
        row = rng.randint(0, n - 1)
    mutant = child.copy()
    mutant[col] = row
    return mutant


def solve(n: int, seed: int | None = None, pop_size: int = 1000,
          max_gen: int = 10000, time_limit: float | None = None) -> SolveResult:
    """以基因演算法求解 n 皇后。

    自適應突變率：基礎值 0.2，族群最佳衝突數有進步就重設；
    停滯超過 100 代後，每 50 代調高 0.05，上限 0.4。

    iterations 定義為實際演化的世代數。history 記錄每一代開始時的
    族群最佳衝突數。
    """
    rng = random.Random(seed)
    start = time.perf_counter()

    # 初始化族群，個體為 (棋盤, 衝突數)
    population = []
    for _ in range(pop_size):
        individual = random_board(n, rng)
        population.append((individual, count_conflicts(individual)))

    min_conflicts = float("inf")
    stagnation = 0
    mutation_rate = 0.2
    history: list[int] = []

    # 遺傳過程
    for gen in range(max_gen):
        best_board, best_conflicts = min(population, key=lambda item: item[1])
        history.append(best_conflicts)
        if best_conflicts == 0:
            return SolveResult(best_board, 0, gen,
                               time.perf_counter() - start, history)
        if time_limit is not None and time.perf_counter() - start > time_limit:
            return SolveResult(best_board, best_conflicts, gen,
                               time.perf_counter() - start, history,
                               timed_out=True)

        # 自適應突變率：有進步就重設，停滯過久就逐步調高
        if best_conflicts < min_conflicts:
            min_conflicts = best_conflicts
            stagnation = 0
            mutation_rate = 0.2
        else:
            stagnation += 1
        if stagnation > 100 and stagnation % 50 == 0:
            mutation_rate = min(mutation_rate + 0.05, 0.4)

        # 依適應度權重選擇父母，產生下一代
        fit_weights = [_fitness(conflicts) for _, conflicts in population]
        new_population = []
        while len(new_population) < pop_size:
            (board_x, _), (board_y, _) = rng.choices(
                population, weights=fit_weights, k=2)
            child = _reproduce(board_x, board_y, rng)
            if rng.random() < mutation_rate:
                child = _mutate(child, rng)
            child_conflicts = count_conflicts(child)
            if child_conflicts == 0:
                history.append(0)
                return SolveResult(child, 0, gen + 1,
                                   time.perf_counter() - start, history)
            new_population.append((child, child_conflicts))
        population = new_population

    best_board, best_conflicts = min(population, key=lambda item: item[1])
    history.append(best_conflicts)
    return SolveResult(best_board, best_conflicts, max_gen,
                       time.perf_counter() - start, history)
