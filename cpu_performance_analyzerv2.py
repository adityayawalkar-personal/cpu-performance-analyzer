import time
import math
import platform
import psutil
import statistics
import multiprocessing as mp
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
    """Compute pi using Chudnovsky algorithm ."""
    getcontext().prec = n + 10

    C = 426880 * Decimal(10005).sqrt()
    K = Decimal(6)
    M = Decimal(1)
    X = Decimal(1)
    L = Decimal(13591409)
    S = L

    K_step = Decimal(12)
    L_step = Decimal(545140134)
    X_mult = Decimal(-262537412640768000)

    iterations = n // 14 + 1
    for i in range(1, iterations):
        M = M * (K ** 3 - 16 * K) / (i ** 3)
        K += K_step
        L += L_step
        X *= X_mult
        S += (M * L) / X

    return C / S


def worker_task(args):
    """Worker function for multiprocessing."""
    task_id, n = args
    start = time.process_time()
    result = compute_pi_chudnovsky(n)
    elapsed = time.process_time() - start
    return task_id, elapsed, str(result)[:50]


def benchmark_single_core(n, runs=5, warmup=2):
    """Run single-core benchmark."""
    print("\n" + "=" * 60)
    print("SINGLE-CORE BENCHMARK")
    print("=" * 60)

    #Warmup
    print(f"\n[WARMUP] Running {warmup} warmup iterations...")
    for i in range(warmup):
        compute_pi_chudnovsky(min(100, n))

    #Benchmark
    print(f"\n[BENCHMARK] Running {runs} iterations with {n} decimal places...")
    times = []
    cpu_percentages = []

    for i in range(runs):
        cpu_before = psutil.cpu_percent(interval=0.1, percpu=False)

        start = time.perf_counter()
        start_cpu = time.process_time()
        pi_val = compute_pi_chudnovsky(n)
        elapsed = time.perf_counter() - start
        elapsed_cpu = time.process_time() - start_cpu

        cpu_after = psutil.cpu_percent(interval=0.1, percpu=False)

        times.append(elapsed)
        cpu_percentages.append((cpu_before + cpu_after) / 2)

        print(f"  Run {i + 1}/{runs}: {elapsed:.4f}s (CPU time: {elapsed_cpu:.4f}s, Usage: {cpu_percentages[-1]:.1f}%)")

    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0

    operations = n // 14 + 1
    ops_per_sec = operations / avg_time
    digits_per_sec = n / avg_time

    print(f"\n[RESULTS]")
    print(f"  Average Time         : {avg_time:.6f} seconds")
    print(f"  Std Deviation        : {std_dev:.6f} seconds")
    print(f"  Consistency          : {(1 - std_dev / avg_time) * 100:.2f}%")
    print(f"  Throughput           : {1 / avg_time:.2f} runs/second")
    print(f"  Operations/Second    : {ops_per_sec:,.0f}")
    print(f"  Digits/Second        : {digits_per_sec:,.0f}")
    print(f"  Avg CPU Usage        : {statistics.mean(cpu_percentages):.1f}%")

    return {
        'avg_time': avg_time,
        'throughput': 1 / avg_time,
        'ops_per_sec': ops_per_sec,
        'digits_per_sec': digits_per_sec,
        'cpu_usage': statistics.mean(cpu_percentages),
        'consistency': (1 - std_dev / avg_time) * 100,
        'pi_value': str(pi_val)[:min(n + 2, 100)]
    }


def benchmark_multi_core(n, runs=5, warmup=2):
    """Run multi-core benchmark."""
    num_cores = mp.cpu_count()

    print("\n" + "=" * 60)
    print(f"MULTI-CORE BENCHMARK (Using {num_cores} cores)")
    print("=" * 60)

    #Warmup
    print(f"\n[WARMUP] Running warmup on all cores...")
    with mp.Pool(processes=num_cores) as pool:
        warmup_tasks = [(i, min(100, n)) for i in range(warmup * num_cores)]
        pool.map(worker_task, warmup_tasks)

    #Benchmark
    print(f"\n[BENCHMARK] Running {runs} parallel batches ({num_cores} tasks per batch)...")
    times = []
    cpu_percentages = []

    for i in range(runs):
        tasks = [(j, n) for j in range(num_cores)]

        cpu_before = psutil.cpu_percent(interval=0.1, percpu=False)

        start = time.perf_counter()
        with mp.Pool(processes=num_cores) as pool:
            results = pool.map(worker_task, tasks)
        elapsed = time.perf_counter() - start

        cpu_after = psutil.cpu_percent(interval=0.1, percpu=False)

        times.append(elapsed)
        cpu_percentages.append((cpu_before + cpu_after) / 2)

        total_cpu_time = sum(r[1] for r in results)
        print(
            f"  Batch {i + 1}/{runs}: {elapsed:.4f}s (Total CPU: {total_cpu_time:.2f}s, Usage: {cpu_percentages[-1]:.1f}%)")

    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0

    # Per-batch metrics
    operations = (n // 14 + 1) * num_cores
    ops_per_sec = operations / avg_time
    total_digits = n * num_cores
    digits_per_sec = total_digits / avg_time

    print(f"\n[RESULTS]")
    print(f"  Average Time         : {avg_time:.6f} seconds")
    print(f"  Std Deviation        : {std_dev:.6f} seconds")
    print(f"  Consistency          : {(1 - std_dev / avg_time) * 100:.2f}%")
    print(f"  Tasks per Batch      : {num_cores}")
    print(f"  Throughput           : {num_cores / avg_time:.2f} runs/second")
    print(f"  Operations/Second    : {ops_per_sec:,.0f}")
    print(f"  Digits/Second        : {digits_per_sec:,.0f}")
    print(f"  Avg CPU Usage        : {statistics.mean(cpu_percentages):.1f}%")

    return {
        'avg_time': avg_time,
        'throughput': num_cores / avg_time,
        'ops_per_sec': ops_per_sec,
        'digits_per_sec': digits_per_sec,
        'cpu_usage': statistics.mean(cpu_percentages),
        'consistency': (1 - std_dev / avg_time) * 100,
        'num_cores': num_cores
    }


def compare_performance(single, multi):
    """Generating detailed comparison between single and multi-core."""
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)

    speedup = single['avg_time'] / multi['avg_time']
    parallel_efficiency = (speedup / multi['num_cores']) * 100
    throughput_gain = (multi['throughput'] / single['throughput'])

    print(f"\n[SPEEDUP ANALYSIS]")
    print(f"  Single-Core Time     : {single['avg_time']:.6f} seconds")
    print(f"  Multi-Core Time      : {multi['avg_time']:.6f} seconds")
    print(f"  Speedup Factor       : {speedup:.2f}x")
    print(f"  Ideal Speedup        : {multi['num_cores']:.0f}x ({multi['num_cores']} cores)")
    print(f"  Parallel Efficiency  : {parallel_efficiency:.1f}%")

    print(f"\n[THROUGHPUT COMPARISON]")
    print(f"  Single-Core          : {single['throughput']:.2f} runs/sec")
    print(f"  Multi-Core           : {multi['throughput']:.2f} runs/sec")
    print(f"  Throughput Gain      : {throughput_gain:.2f}x")

    print(f"\n[OPERATIONS COMPARISON]")
    print(f"  Single-Core          : {single['ops_per_sec']:,.0f} ops/sec")
    print(f"  Multi-Core           : {multi['ops_per_sec']:,.0f} ops/sec")
    print(f"  Operations Gain      : {multi['ops_per_sec'] / single['ops_per_sec']:.2f}x")

    print(f"\n[DIGITS THROUGHPUT]")
    print(f"  Single-Core          : {single['digits_per_sec']:,.0f} digits/sec")
    print(f"  Multi-Core           : {multi['digits_per_sec']:,.0f} digits/sec")
    print(f"  Digits Gain          : {multi['digits_per_sec'] / single['digits_per_sec']:.2f}x")

    print(f"\n[CPU UTILIZATION]")
    print(f"  Single-Core Usage    : {single['cpu_usage']:.1f}%")
    print(f"  Multi-Core Usage     : {multi['cpu_usage']:.1f}%")

    print(f"\n[SCALING ASSESSMENT]")
    if parallel_efficiency >= 90:
        rating = "Excellent"
    elif parallel_efficiency >= 75:
        rating = "Very Good"
    elif parallel_efficiency >= 60:
        rating = "Good"
    elif parallel_efficiency >= 40:
        rating = "Fair"
    else:
        rating = "Poor"

    print(f"  Scaling Efficiency   : {rating} ({parallel_efficiency:.1f}%)")
    print(f"  Overhead Loss        : {100 - parallel_efficiency:.1f}%")

    if parallel_efficiency < 70:
        print(f"\n  Note: Efficiency below 70% suggests overhead from process")
        print(f"        creation, memory copying, or synchronization.")

    return {
        'speedup': speedup,
        'efficiency': parallel_efficiency,
        'rating': rating
    }


def run_full_benchmark(n, runs=5):
    """Run complete single and multi-core benchmark suite."""
    print("=" * 60)
    print("CPU PERFORMANCE ANALYZER - COMPREHENSIVE BENCHMARK")
    print("=" * 60)

    # System info
    cpu_info = get_cpu_info()
    print("\n[SYSTEM INFORMATION]")
    for key, value in cpu_info.items():
        print(f"  {key:20s}: {value}")

    print(f"\n[TEST CONFIGURATION]")
    print(f"  Decimal Places       : {n}")
    print(f"  Benchmark Runs       : {runs}")
    print(f"  Algorithm Iterations : {n // 14 + 1}")

    #Run_benchmarks
    single_results = benchmark_single_core(n, runs)
    multi_results = benchmark_multi_core(n, runs)

    # Compare
    comparison = compare_performance(single_results, multi_results)

    #Show_pivalue
    print(f"\n[PI VALUE (first {min(n, 98)} decimal places)]")
    print(f"  {single_results['pi_value']}")
    if n > 98:
        print(f"  ... (truncated)")

    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)

    return single_results, multi_results, comparison


if __name__ == "__main__":
    try:
        print("\n*** CPU Performance Analyzer ***\n")

        n = int(input("Enter number of decimal places for pi (recommended: 1000-5000): "))
        if n < 100:
            print("Warning: Too few digits for meaningful benchmark. Using 1000.")
            n = 1000
        elif n > 50000:
            print("Warning: Very large computation. This may take several minutes.")

        runs = int(input("Enter number of benchmark runs (recommended: 3-5): ") or "5")

        single, multi, comparison = run_full_benchmark(n, runs)

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
