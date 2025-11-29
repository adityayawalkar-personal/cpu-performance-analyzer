import time
import math
from decimal import Decimal, getcontext

def compute_pi_chudnovsky(n):
    """Compute pi using Chudnovsky algorithm with precision."""
    getcontext().prec = n + 5  # extra digits for rounding accuracy

    C = 426880 * Decimal(10005).sqrt()
    M = Decimal(1)
    L = Decimal(13591409)
    X = Decimal(1)
    K = Decimal(6)
    S = L

    for i in range(1, n // 14 + 1):
        M = (M * (K ** 3 - 16 * K)) / (i ** 3)
        L += 545140134
        X *= -262537412640768000
        S += (M * L) / X
        K += 12

    pi_val = C / S
    return pi_val

n = int(input("Enter number of decimal places for pi: "))
iterations = 5  # number of runs to average performance

# Warmup_phase
compute_pi_chudnovsky(100)

start_time = time.process_time()
for _ in range(iterations):
    pi_val = compute_pi_chudnovsky(n)
end_time = time.process_time()

avg_time = (end_time - start_time) / iterations
pi_str = str(pi_val)[:n + 2]

#Output/Result
print(f"\nValue of pi up to {n} decimal places:")
print(pi_str)
print(f"\nAverage CPU time per run: {avg_time:.6f} seconds")
print(f"Estimated CPU performance: {1/avg_time:.2f} runs/second")