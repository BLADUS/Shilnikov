import numpy as np

def solve_heat_equation(a, b, f_func, T, h, left_bc, right_bc, initial_cond):
    # Параметры сетки
    x_points = np.linspace(0, 1, int(1 / h) + 1)
    Nx = len(x_points) - 1

    # Увеличиваем шаг по времени для заметного изменения
    tau = h  # Используем h вместо h² / (4a) для ускорения
    Nt = int(T / tau) + 1

    # Инициализация сетки
    u = np.zeros((Nt, Nx + 1))
    
    # Начальное условие
    for i in range(Nx + 1):
        u[0, i] = initial_cond(x_points[i])
    
    # Коэффициенты
    alpha = a * tau / h**2
    beta = b * tau

    # Матрица коэффициентов (трехдиагональная)
    size = Nx - 1
    A = np.zeros((size, size))
    for i in range(size):
        A[i, i] = 1 + 2 * alpha + beta
        if i > 0:
            A[i, i - 1] = -alpha
        if i < size - 1:
            A[i, i + 1] = -alpha

    # Временные слои
    for n in range(Nt - 1):
        t = n * tau

        # Правая часть (учитываем f(x, t))
        F = np.zeros(size)
        for i in range(1, Nx):
            x = x_points[i]
            F[i - 1] = u[n, i] + tau * f_func(x, t)

        # Граничные условия
        F[0] += alpha * left_bc(t + tau)
        F[-1] += alpha * right_bc(t + tau)

        # Решение системы
        u[n + 1, 1:Nx] = np.linalg.solve(A, F)

        # Явно задаем границы (важно!)
        u[n + 1, 0] = left_bc(t + tau)
        u[n + 1, -1] = right_bc(t + tau)

    return x_points, np.linspace(0, T, Nt), u

def read_problem_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    params = {}
    for line in lines:
        if '=' in line:
            key, value = line.split('=')
            key = key.strip()
            value = value.strip()
            params[key] = value
    
    # Парсинг параметров
    a = float(params['a'])
    b = float(params['b'])
    T = float(params['T'])
    h = float(params.get('h', '0.01'))
    
    # Парсинг функций
    f_expr = params['f']
    left_bc_expr = params['u (0,t)']
    right_bc_expr = params['u (1,t)']
    initial_cond_expr = params['u (x,0)']
    
    # Создание функций
    def f(x, t):
        return eval(f_expr, {'x': x, 't': t, 'np': np})
    
    def left_bc(t):
        return eval(left_bc_expr, {'t': t, 'np': np})
    
    def right_bc(t):
        return eval(right_bc_expr, {'t': t, 'np': np})
    
    def initial_cond(x):
        return eval(initial_cond_expr, {'x': x, 'np': np})
    
    return a, b, f, T, h, left_bc, right_bc, initial_cond

def write_solution(filename, x_points, t_points, u):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=== НАЧАЛО РАСЧЕТА ===\n")
        f.write(f"Параметры сетки: h = {x_points[1] - x_points[0]:.6f}, tau = {t_points[1] - t_points[0]:.6f}\n")
        f.write(f"Количество точек по пространству: {len(x_points)}\n")
        f.write(f"Количество временных слоев: {len(t_points)}\n\n")
        
        step = max(1, len(t_points) // 100)
        for n in range(0, len(t_points), step):
            t = t_points[n]
            f.write(f"=== Временной слой t = {t:.6f} ===\n")
            for i in range(0, len(x_points), 10):
                x = x_points[i]
                f.write(f"u({x:.6f}, {t:.6f}) = {u[n, i]:.12f}\n")
            f.write("\n")
        
        f.write("=== КОНЕЦ РАСЧЕТА ===\n")

def main():
    input_file = "THIRD_PROBLEM/problem.txt"
    output_file = "THIRD_PROBLEM/answer.txt"
    
    try:
        a, b, f, T, h, left_bc, right_bc, initial_cond = read_problem_file(input_file)
        
        print("Параметры задачи:")
        print(f"a = {a}, b = {b}, T = {T}, h = {h}")
        
        x_points, t_points, u = solve_heat_equation(a, b, f, T, h, left_bc, right_bc, initial_cond)
        
        write_solution(output_file, x_points, t_points, u)
        print(f"Результаты записаны в {output_file}")
    
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    main()