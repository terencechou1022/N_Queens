import random
import time
from count_conflicts import count_conflicts

def get_best_neighbor(current: list[int], current_conflicts: int):
    """
    尋找最佳鄰居。
    """
    n = len(current)
    best_neighbor = None
    min_conflicts = current_conflicts

    # 第幾行的皇后要移動
    for col in range(n):
        # 移動到第幾列的位置
        for row in range(n):
            # 如果挑選到原本的位置
            if row == current[col]:
                continue # 跳過
            # 產生鄰居
            neighbor = current.copy() # 複製一份目前的棋盤
            neighbor[col] = row # 移動皇后
            conflicts = count_conflicts(neighbor) # 計算鄰居的衝突數
            # 如果鄰居就是全域最佳解
            if conflicts == 0:
                return neighbor, conflicts # 直接回傳
            # 如果鄰居的衝突數比目前的最小衝突數還少
            if conflicts < min_conflicts:
                min_conflicts = conflicts # 更新最小衝突數
                best_neighbor = neighbor # 更新最佳鄰居
    
    return best_neighbor, min_conflicts

def hill_climbing(n):
    max_restarts = 1000 # 重啟次數
    
    # 重啟過程
    for i in range(max_restarts):
        # 初始化
        current = random.sample(range(n), n)
        current_conflicts = count_conflicts(current)
        print(f"初始衝突數: {current_conflicts}")
        
        # 爬山過程
        while True:
            # 如果找到全域最佳解
            if current_conflicts == 0:
                print(f"\n在第 {i+1} 次重啟找到全域最佳解！")
                return current # 提早結束
            # 尋找最佳鄰居
            next, next_conflicts = get_best_neighbor(current, current_conflicts)
            # 如果鄰居就是全域最佳解
            if next_conflicts == 0:
                print(f"\n在第 {i+1} 次重啟找到全域最佳解！")
                return next # 提早結束
            # 如果卡在局部最佳解
            if next is None or next_conflicts >= current_conflicts:
                print("卡在局部最佳解，重啟中...")
                break # 跳出 while 迴圈進行重啟
            # 移動到最佳鄰居
            current = next
            current_conflicts = next_conflicts
            print(f"移動到最佳鄰居 -> 新衝突數: {current_conflicts}")
    
    print(f"\n未找到全域最佳解 -> 最終衝突數: {current_conflicts}")
    return current

if __name__ == "__main__":
    n = 20
    print(f"--- 使用爬山演算法解 {n} 皇后問題 ---")
    start_time = time.time()
    solution = hill_climbing(n)
    end_time = time.time()
    if count_conflicts(solution) == 0:
        execution_time = end_time - start_time
        print(f"執行時間: {execution_time:.3f} 秒")
        for queen in solution:
            print(f"{queen}", end=' ')