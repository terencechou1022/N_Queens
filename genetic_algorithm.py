import random
import time
from count_conflicts import count_conflicts

def fitness(conflicts: int):
    """
    衝突數越少，適應度越高。
    """
    return 1.0 / (conflicts + 1)

def selection(population: list[tuple[list[int], int]], fit_weights: list[float]):
    """
    Stochastic selection: select each individual in proportion to its relative fitness to the population.
    """
    # 根據適應度權重挑選出一對父母
    parents = random.choices(population, weights=fit_weights, k=2)
    parent_x, parent_y = parents[0][0], parents[1][0]
    return parent_x, parent_y

def reproduction(parent_x: list[int], parent_y: list[int]):
    """
    Single-point crossover: choose the split point randomly, take the first half of one parent, and the second half of another parent.
    """
    n = len(parent_x)
    c = random.randint(0, n - 1) # 隨機決定切點
    child = parent_x[:c] + parent_y[c:] # 產生子代
    return child

def mutation(child: list[int]):
    """
    1. Who to mutate: random.
    2. How to mutate: totally arbitrarily.
    """
    n = len(child)
    col = random.randint(0, n - 1) # 第幾行的皇后要移動
    row = random.randint(0, n - 1) # 移動到第幾列的位置
    # 如果挑選到原本的位置
    while row == child[col]:
        row = random.randint(0, n - 1) # 重新 random 一次
    # 產生變體
    mutant_child = child.copy() # 複製一份目前的棋盤
    mutant_child[col] = row # 移動皇后
    return mutant_child

def genetic_algorithm(n):
    pop_size = 1000 # 族群大小
    max_gen = 10000 # 最大世代數
    min_conflicts = float('inf') # 最小衝突數
    
    # 初始化
    population = []
    while len(population) < pop_size:
        individual = random.sample(range(n), n)
        conflicts = count_conflicts(individual)
        population.append((individual, conflicts))
    
    # 遺傳過程
    for i in range(max_gen):
        # 取得當前最佳個體
        best_item = min(population, key=lambda x: x[1])
        # 如果找到全域最佳解
        if best_item[1] == 0:
            print(f"\n在第 {i+1} 代找到全域最佳解！")
            return best_item[0] # 提早結束
        # 動態調整突變率
        if best_item[1] < min_conflicts:
            min_conflicts = best_item[1]
            stagnation = 0
            mutation_rate = 0.2
        else:
            stagnation += 1
        if stagnation > 100 and stagnation % 50 == 0:
            mutation_rate = min(mutation_rate + 0.05, 0.4)
        # 顯示進度
        if i % 100 == 0:
            print(f"第 {i+1} 代 -> 突變率: {mutation_rate:.2f}，最小衝突數: {best_item[1]}")
        # 計算適應度權重
        fit_weights = [fitness(item[1]) for item in population]
        
        # 產生下一代
        new_population = []
        while len(new_population) < pop_size:
            parent_x, parent_y = selection(population, fit_weights)
            child = reproduction(parent_x, parent_y)
            if random.random() < mutation_rate:
                child = mutation(child)
            child_conflicts = count_conflicts(child)
            # 如果小孩就是全域最佳解
            if child_conflicts == 0:
                print(f"\n在第 {i+1} 代找到全域最佳解！")
                return child # 提早結束
            new_population.append((child, child_conflicts))
        
        # 更新族群
        population = new_population
    
    final_item = min(population, key=lambda x: x[1])
    print(f"\n未找到全域最佳解 -> 最終衝突數: {final_item[1]}")
    return final_item[0]

if __name__ == "__main__":
    n = 30
    print(f"--- 使用基因演算法解 {n} 皇后問題 ---")
    start_time = time.time()
    solution = genetic_algorithm(n)
    end_time = time.time()
    if count_conflicts(solution) == 0:
        execution_time = end_time - start_time
        print(f"執行時間: {execution_time:.3f} 秒")
        for queen in solution:
            print(f"{queen}", end=' ')