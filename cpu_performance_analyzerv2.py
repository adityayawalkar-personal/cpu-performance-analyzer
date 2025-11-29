import time
import math
import platform
import psutil
import statistics
from decimal import Decimal, getcontext


def get_cpu_info():
    """Gathering CPU and system information."""
    info = {
        'CPU': platform.processor() or psutil.cpu_freq().current,
        'Cores (Physical)': psutil.cpu_count(logical=False),
        'Threads (Logical)': psutil.cpu_count(logical=True),
        'Base Frequency': f"{psutil.cpu_freq().current:.2f} MHz",
        'RAM': f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
        'Python Version': platform.python_version(),
        'System': f"{platform.system()} {platform.release()}"
    }
    return info


def compute_pi_chudnovsky(n):
    """Computing pi using Chudnovsky algorithm."""
    getcontext().prec = n + 10

    C = 426880 * Decimal(10005).sqrt()
    K = Decimal(6)
    M = Decimal(1)
    X = Decimal(1)
    L = Decimal(13591409)
    S = L

    #Pre-calculated_constants
    K_step = Decimal(12)
    L_step = Decimal(545140134)
    X_mult = Decimal(-262537412640768000)

    iterations = n // 14 + 1
    for i in range(1, iterations):
        # Optimized calculation order
        M = M * (K ** 3 - 16 * K) / (i ** 3)
        K += K_step
        L += L_step
        X *= X_mult
        S += (M * L) / X

    return C / S


def benchmark_cpu(n, runs=5, warmup=2):
    """Running comprehensive CPU benchmark."""
    print("=" * 60)
    print("CPU PERFORMANCE ANALYZER - Pi Calculation Benchmark")
    print("=" * 60)

    # Display system info
    cpu_info = get_cpu_info()
    print("\n[SYSTEM INFORMATION]")
    for key, value in cpu_info.items():
        print(f"  {key:20s}: {value}")

    #Warmup_phase
    print(f"\n[WARMUP] Running {warmup} warmup iterations...")
    for i in range(warmup):
        compute_pi_chudnovsky(min(100, n))
        print(f"  Warmup {i + 1}/{warmup} complete")

    #Benchmark_phase
    print(f"\n[BENCHMARK] Running {runs} iterations with {n} decimal places...")
    times = []
    cpu_percentages = []
    memory_usage = []

    for i in range(runs):
        #Measuring CPU and memory before execution
        cpu_before = psutil.cpu_percent(interval=0.1)
        mem_before = psutil.virtual_memory().used / (1024 ** 3)

        #Timing the computation
        start = time.process_time()
        pi_val = compute_pi_chudnovsky(n)
        elapsed = time.process_time() - start

        #Measure after computation
        cpu_after = psutil.cpu_percent(interval=0.1)
        mem_after = psutil.virtual_memory().used / (1024 ** 3)

        times.append(elapsed)
        cpu_percentages.append((cpu_before + cpu_after) / 2)
        memory_usage.append(mem_after - mem_before)

        print(f"  Run {i + 1}/{runs}: {elapsed:.4f}s (CPU: {cpu_percentages[-1]:.1f}%, Mem: {memory_usage[-1]:.3f}GB)")

    #Statistical_analysis
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    min_time = min(times)
    max_time = max(times)

    #Calculating_performance_metrics
    operations = n // 14 + 1  #number of looped iterations
    ops_per_sec = operations / avg_time
    digits_per_sec = n / avg_time

    #Result
    print("\n" + "=" * 60)
    print("[PERFORMANCE RESULTS]")
    print("=" * 60)
    print(f"\n  Decimal Places       : {n}")
    print(f"  Algorithm Iterations : {operations}")
    print(f"\n  Average Time         : {avg_time:.6f} seconds")
    print(f"  Std Deviation        : {std_dev:.6f} seconds ({(std_dev / avg_time) * 100:.2f}%)")
    print(f"  Min Time             : {min_time:.6f} seconds")
    print(f"  Max Time             : {max_time:.6f} seconds")
    print(f"  Consistency Score    : {(1 - std_dev / avg_time) * 100:.2f}%")

    print(f"\n  Throughput           : {1 / avg_time:.2f} runs/second")
    print(f"  Operations/Second    : {ops_per_sec:,.0f}")
    print(f"  Digits/Second        : {digits_per_sec:,.0f}")

    print(f"\n  Avg CPU Usage        : {statistics.mean(cpu_percentages):.1f}%")
    print(f"  Avg Memory Delta     : {statistics.mean(memory_usage):.3f} GB")

    #Performance_rating
    rating = get_performance_rating(digits_per_sec, n)
    print(f"\n  Performance Rating   : {rating}")

    #Show_pivalue(truncated)
    pi_str = str(pi_val)[:min(n + 2, 100)]
    if n > 100:
        pi_str += "..."
    print(f"\n[PI VALUE (first {min(n, 100)} places)]")
    print(f"  {pi_str}")

    print("\n" + "=" * 60)

    return {
        'avg_time': avg_time,
        'throughput': 1 / avg_time,
        'ops_per_sec': ops_per_sec,
        'digits_per_sec': digits_per_sec,
        'consistency': (1 - std_dev / avg_time) * 100
    }


def get_performance_rating(digits_per_sec, n):
    """Providing qualitative performance rating."""
    if n < 1000:
        thresholds = [(100000, "Excellent"), (50000, "Very Good"), (20000, "Good"),
                      (10000, "Average"), (0, "Below Average")]
    elif n < 10000:
        thresholds = [(50000, "Excellent"), (20000, "Very Good"), (10000, "Good"),
                      (5000, "Average"), (0, "Below Average")]
    else:
        thresholds = [(10000, "Excellent"), (5000, "Very Good"), (2000, "Good"),
                      (1000, "Average"), (0, "Below Average")]

    for threshold, rating in thresholds:
        if digits_per_sec >= threshold:
            return f"{rating} ({digits_per_sec:,.0f} digits/sec)"
    return f"Below Average ({digits_per_sec:,.0f} digits/sec)"


if __name__ == "__main__":
    try:
        n = int(input("Enter number of decimal places for pi (recommended: 1000-10000): "))
        if n < 10:
            print("Warning: Too few digits for meaningful benchmark. Using 1000.")
            n = 1000
        elif n > 100000:
            print("Warning: Very large computation. This may take several minutes.")

        runs = int(input("Enter number of benchmark runs (recommended: 5-10): ") or "5")

        results = benchmark_cpu(n, runs=runs)

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")