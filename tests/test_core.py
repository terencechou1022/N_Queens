"""衝突計算與隨機棋盤的單元測試。"""
import random

from nqueens.core import count_conflicts, random_board


def test_known_valid_solutions_have_zero_conflicts():
    # 已知的 4 皇后與 8 皇后合法解
    assert count_conflicts([1, 3, 0, 2]) == 0
    assert count_conflicts([0, 4, 7, 5, 2, 6, 1, 3]) == 0


def test_same_row_conflict():
    assert count_conflicts([0, 0]) == 1


def test_diagonal_conflict():
    assert count_conflicts([0, 1]) == 1


def test_non_attacking_pair():
    # 差兩列、差一行，彼此攻擊不到
    assert count_conflicts([0, 2]) == 0


def test_all_queens_on_same_diagonal():
    # 三個皇后全在同一條斜線上，兩兩衝突共 3 對
    assert count_conflicts([0, 1, 2]) == 3


def test_example_board_conflicts():
    # 範例棋盤 "7 5 1 3 2 4 0 6"
    assert count_conflicts([7, 5, 1, 3, 2, 4, 0, 6]) == 9


def test_random_board_is_permutation():
    board = random_board(20, random.Random(123))
    assert sorted(board) == list(range(20))


def test_random_board_reproducible_with_same_seed():
    assert random_board(15, random.Random(7)) == random_board(15, random.Random(7))
