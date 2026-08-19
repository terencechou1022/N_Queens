"""三種求解器的行為測試：解的合法性、可重現性、失敗與逾時路徑。"""
import pytest

from nqueens import genetic_algorithm, hill_climbing, simulated_annealing
from nqueens.core import count_conflicts

# GA 測試用較小的族群與世代數即可在 N=8 穩定找到解，避免測試過慢
SOLVERS = {
    "hill_climbing": lambda n, seed: hill_climbing.solve(n, seed=seed),
    "simulated_annealing": lambda n, seed: simulated_annealing.solve(n, seed=seed),
    "genetic_algorithm": lambda n, seed: genetic_algorithm.solve(
        n, seed=seed, pop_size=200, max_gen=500),
}


@pytest.mark.parametrize("name", SOLVERS)
def test_solver_finds_valid_solution_at_n8(name):
    result = SOLVERS[name](8, 42)
    assert result.solved
    assert result.conflicts == 0
    assert len(result.solution) == 8
    assert all(0 <= row < 8 for row in result.solution)
    assert count_conflicts(result.solution) == 0
    assert result.history[-1] == 0
    assert result.elapsed >= 0
    assert not result.timed_out


@pytest.mark.parametrize("name", SOLVERS)
def test_solver_reproducible_with_same_seed(name):
    first = SOLVERS[name](8, 7)
    second = SOLVERS[name](8, 7)
    assert first.solution == second.solution
    assert first.iterations == second.iterations
    assert first.history == second.history


def test_unsolved_result_reports_failure():
    # t_min 設得比初始溫度高，一步都不會跑，必然以初始棋盤失敗收場
    result = simulated_annealing.solve(30, seed=1, t_min=200.0)
    assert not result.solved
    assert result.conflicts > 0
    assert result.iterations == 0
    assert result.history == [result.conflicts]


def test_time_limit_stops_solver():
    # N=50 的 GA 不可能在 0.05 秒內完成，應觸發逾時中止
    result = genetic_algorithm.solve(50, seed=1, pop_size=500,
                                     max_gen=10000, time_limit=0.05)
    assert result.timed_out
    assert not result.solved
