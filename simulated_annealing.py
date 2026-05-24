import random
import math
import time
from count_conflicts import count_conflicts

def get_random_neighbor(current: list[int]):
    """
    隨機產生鄰居。
    """
    n = len(current)
    col = random.randint(0, n - 1) # 第幾行的皇后要移動
    row = random.randint(0, n - 1) # 移動到第幾列的位置
    # 如果挑選到原本的位置
    while row == current[col]:
        row = random.randint(0, n - 1) # 重新 random 一次
    # 產生鄰居
    neighbor = current.copy() # 複製一份目前的棋盤
    neighbor[col] = row # 移動皇后
    return neighbor

def simulated_annealing(n):
    t = 100.0 # 初始溫度
    a = 0.95 # 降溫速率
    
    # 初始化
    current = random.sample(range(n), n)
    current_conflicts = count_conflicts(current)
    print(f"初始衝突數: {current_conflicts}")
    
    # 退火過程
    while t > 0:
        # 如果找到全域最佳解
        if current_conflicts == 0:
            print(f"\n找到全域最佳解！")
            return current # 提早結束
        # 隨機產生鄰居
        next = get_random_neighbor(current)
        next_conflicts = count_conflicts(next)
        # 如果鄰居就是全域最佳解
        if next_conflicts == 0:
            print(f"\n找到全域最佳解！")
            return next # 提早結束
        # 計算能量差
        delta_e = current_conflicts - next_conflicts
        # 好的鄰居 -> 無條件接受
        if delta_e > 0:
            # 移動到好的鄰居
            current = next
            current_conflicts = next_conflicts
            print(f"移動到好的鄰居 -> 新衝突數: {current_conflicts}")
        else:
            # 壞的鄰居 -> 機率性接受
            probability = math.exp(delta_e / t)
            if random.random() < probability:
                # 移動到壞的鄰居
                current = next
                current_conflicts = next_conflicts
                print(f"移動到壞的鄰居 -> 新衝突數: {current_conflicts}")
        
        t *= a # 退火
    
    print(f"\n未找到全域最佳解 -> 最終衝突數: {current_conflicts}")
    return current

if __name__ == "__main__":
    n = 50
    print(f"--- 使用模擬退火演算法解 {n} 皇后問題 ---")
    start_time = time.time()
    solution = simulated_annealing(n)
    end_time = time.time()
    if count_conflicts(solution) == 0:
        execution_time = end_time - start_time
        print(f"執行時間: {execution_time:.3f} 秒")
        for queen in solution:
            print(f"{queen}", end=' ')