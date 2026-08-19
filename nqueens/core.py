"""N 皇后問題的共用核心：棋盤表示、衝突計算、求解結果結構。

棋盤表示：queens[i] 代表第 i 直行 (column) 的皇后所在的橫列 (row)，
一個長度為 n 的 list 即代表一個 n 皇后的棋盤狀態。
這個表示法保證每行恰有一個皇后，因此不可能發生同行衝突。
"""
import random
from dataclasses import dataclass, field


def count_conflicts(queens: list[int]) -> int:
    """計算互相攻擊的皇后對數（衝突數），0 代表合法解。

    衝突條件：同列（row 相同）或同斜線（列差等於行差）。
    時間複雜度 O(n^2)，逐對檢查。
    """
    n = len(queens)
    conflicts = 0
    for i in range(n):
        for j in range(i + 1, n):
            if queens[i] == queens[j] or abs(queens[i] - queens[j]) == abs(i - j):
                conflicts += 1
    return conflicts


def random_board(n: int, rng: random.Random) -> list[int]:
    """產生隨機初始棋盤：0 到 n-1 的隨機排列，初始狀態即無同列衝突。"""
    return rng.sample(range(n), n)


@dataclass
class SolveResult:
    """單次求解的完整結果，三種演算法共用同一介面。"""

    solution: list[int]        # 最終棋盤狀態
    conflicts: int             # 最終衝突數，0 代表成功
    iterations: int            # 迭代次數（HC: 移動步數、SA: 降溫步數、GA: 世代數）
    elapsed: float             # 求解耗時（秒）
    history: list[int] = field(default_factory=list)  # 衝突數軌跡，供收斂曲線使用
    timed_out: bool = False    # 是否因超過 time_limit 而中止

    @property
    def solved(self) -> bool:
        return self.conflicts == 0
