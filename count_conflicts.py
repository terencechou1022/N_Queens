def parse_board(input_str):
    """
    將輸入的字串轉換成棋盤列表
    例如："5 1 6 0 3 7 4 2" -> [5, 1, 6, 0, 3, 7, 4, 2]
    """
    queens = [int(x) for x in input_str.split()]
    return queens

def count_conflicts(queens):
    """
    queens[i] 代表第 i 直行 (column) 的皇后所在的橫列 (row)
    衝突條件：同列 (row 相同)、同斜線 (列差等於行差)
    """
    n = len(queens)
    conflicts = 0

    # 目前正在檢查的皇后
    for i in range(n):
        # 要比較的另一個皇后
        for j in range(i + 1, n):
            # 判斷兩個皇后是否衝突
            if queens[i] == queens[j] or abs(queens[i] - queens[j]) == abs(i - j):
                conflicts += 1
                # print(f"第 {i+1} 個皇后和第 {j+1} 個皇后衝突")
    
    return conflicts

if __name__ == "__main__":
    input_str = "7 5 1 3 2 4 0 6"
    queens = parse_board(input_str)
    conflicts = count_conflicts(queens)
    print(f"衝突數: {conflicts}")