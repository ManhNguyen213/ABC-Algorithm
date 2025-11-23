import random

# --- Hàm mục tiêu phức tạp 2 biến ---
def objective_function(x):
    # x[0] = x, x[1] = y
    return (x[0]**4 - 16*x[0]**2 + 5*x[0]) + (x[1]**4 - 16*x[1]**2 + 5*x[1])

# --- Lớp đại diện nguồn thức ăn ---
class FoodSource:
    def __init__(self, position):
        self.position = position
        self.fitness = objective_function(position)
        self.trial = 0  # số lần không cải thiện

# --- Lớp ABC ---
class ABC:
    def __init__(self, func, bounds, pop_size=20, max_iter=300, limit=20):
        self.func = func
        self.bounds = bounds
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.limit = limit
        # Khởi tạo quần thể
        self.population = [FoodSource([random.uniform(b[0], b[1]) for b in bounds]) for _ in range(pop_size)]
        # Lưu nghiệm tốt nhất
        self.best_solution = min(self.population, key=lambda f: f.fitness)
    
    # --- Tạo nghiệm mới lân cận ---
    def get_neighbor(self, idx):
        solution = self.population[idx]
        neighbor_pos = solution.position[:]
        # Chọn cá thể j khác i
        j = random.choice([k for k in range(self.pop_size) if k != idx])
        phi = random.uniform(-1, 1)
        # Chọn 1 chiều ngẫu nhiên để thay đổi
        dim = random.randint(0, len(self.bounds) - 1)
        neighbor_pos[dim] = solution.position[dim] + phi * (solution.position[dim] - self.population[j].position[dim])
        # Giới hạn theo bounds
        neighbor_pos[dim] = max(min(neighbor_pos[dim], self.bounds[dim][1]), self.bounds[dim][0])
        return neighbor_pos

    # --- Tính xác suất cho Onlooker bees ---
    def calculate_probabilities(self):
        inv_fitness = [1/(f.fitness + 1e-10) for f in self.population]  # Dùng 1e-10 tránh chia 0
        total = sum(inv_fitness)
        return [f/total for f in inv_fitness]

    # --- Chạy thuật toán ---
    def run(self):
        for t in range(self.max_iter):
            # --- Employed Bees Phase ---
            for i in range(self.pop_size):
                neighbor_pos = self.get_neighbor(i)
                neighbor_fit = self.func(neighbor_pos)
                if neighbor_fit < self.population[i].fitness:
                    self.population[i].position = neighbor_pos
                    self.population[i].fitness = neighbor_fit
                    self.population[i].trial = 0
                else:
                    self.population[i].trial += 1

            # --- Onlooker Bees Phase ---
            probs = self.calculate_probabilities()
            i = 0
            count = 0
            while count < self.pop_size:
                if random.random() < probs[i]:
                    neighbor_pos = self.get_neighbor(i)
                    neighbor_fit = self.func(neighbor_pos)
                    if neighbor_fit < self.population[i].fitness:
                        self.population[i].position = neighbor_pos
                        self.population[i].fitness = neighbor_fit
                        self.population[i].trial = 0
                    else:
                        self.population[i].trial += 1
                    count += 1
                i = (i + 1) % self.pop_size

            # --- Scout Bees Phase ---
            for i in range(self.pop_size):
                if self.population[i].trial > self.limit:
                    self.population[i] = FoodSource([random.uniform(b[0], b[1]) for b in self.bounds])

            # --- Cập nhật nghiệm tốt nhất ---
            current_best = min(self.population, key=lambda f: f.fitness)
            if current_best.fitness < self.best_solution.fitness:
                self.best_solution = current_best

            # --- In tiến trình mỗi 50 vòng ---
            if t % 50 == 0 or t == self.max_iter-1:
                print(f"Iteration {t}: Best Fitness = {self.best_solution.fitness:.6f}")

        return self.best_solution.position, self.best_solution.fitness

# --- Chạy thử ---
if __name__ == "__main__":
    bounds = [(-5,5), (-5,5)]  # Giới hạn cho x và y
    abc = ABC(objective_function, bounds, pop_size=20, max_iter=300, limit=20)
    best_pos, best_val = abc.run()
    print("\nBest solution found:", best_pos)
    print("Best objective value:", best_val)
