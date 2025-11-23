import random

# --- Hàm mục tiêu (bạn có thể thay đổi) ---
def objective_function(x):
    return (x[0]**4 - 16*x[0]**2 + 5*x[0]) + (x[1]**4 - 16*x[1]**2 + 5*x[1])


# --- Lớp đại diện cho một nguồn thức ăn ---
class FoodSource:
    def __init__(self, position):
        self.position = position
        self.fitness = objective_function(position)
        self.trial = 0


# --- Lớp thuật toán ABC ---
class ABC:
    def __init__(self, func, bounds, pop_size=20, max_iter=500, limit=50):
        self.func = func
        self.bounds = bounds
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.limit = limit

        # Khởi tạo quần thể
        self.population = [
            FoodSource([random.uniform(b[0], b[1]) for b in bounds])
            for _ in range(pop_size)
        ]

        # Lưu nghiệm tốt nhất
        self.best_solution = min(self.population, key=lambda f: f.fitness)

    # Tạo nghiệm lân cận
    def get_neighbor(self, idx):
        solution = self.population[idx]
        neighbor_pos = solution.position[:]

        # Chọn cá thể khác
        j = random.choice([k for k in range(self.pop_size) if k != idx])
        phi = random.uniform(-1, 1)

        # Chọn ngẫu nhiên 1 chiều
        dim = random.randint(0, len(self.bounds) - 1)

        # Công thức cập nhật
        neighbor_pos[dim] = solution.position[dim] + \
                            phi * (solution.position[dim] - self.population[j].position[dim])

        # Ràng buộc biên
        neighbor_pos[dim] = max(min(neighbor_pos[dim], self.bounds[dim][1]),
                                self.bounds[dim][0])
        return neighbor_pos

    # Tính xác suất chọn nguồn thức ăn
    def calculate_probabilities(self):
        inv_fit = [1/(f.fitness + 1e-10) for f in self.population]
        total = sum(inv_fit)
        return [x / total for x in inv_fit]

    # Chạy thuật toán
    def run(self):
        for _ in range(self.max_iter):

            # --- Employed Bees ---
            for i in range(self.pop_size):
                neighbor_pos = self.get_neighbor(i)
                neighbor_fit = self.func(neighbor_pos)

                if neighbor_fit < self.population[i].fitness:
                    self.population[i].position = neighbor_pos
                    self.population[i].fitness = neighbor_fit
                    self.population[i].trial = 0
                else:
                    self.population[i].trial += 1

            # --- Onlooker Bees ---
            probs = self.calculate_probabilities()
            count = 0
            i = 0

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

            # --- Scout Bees ---
            for i in range(self.pop_size):
                if self.population[i].trial > self.limit:
                    self.population[i] = FoodSource([random.uniform(b[0], b[1]) for b in self.bounds])

            # --- Cập nhật nghiệm tốt nhất ---
            current_best = min(self.population, key=lambda f: f.fitness)
            if current_best.fitness < self.best_solution.fitness:
                self.best_solution = current_best

        return self.best_solution.position, self.best_solution.fitness


# --- Chạy thuật toán ---
if __name__ == "__main__":
    bounds = [(-5, 5), (-5, 5)]
    abc = ABC(objective_function, bounds, pop_size=20, max_iter=500, limit=50)
    best_pos, best_val = abc.run()

    print("Best solution found:", best_pos)
    print("Best objective value:", best_val)
