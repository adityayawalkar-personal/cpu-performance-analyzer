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
        'RAM': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
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

    K_step = Decimal(12)
    L_step = Decimal(545140134)
    X_mult = Decimal(-262537412640768000)

    iterations = n // 14 + 1
    for i in range(1, iterations):
        M = M * (K**3 - 16*K) / (i**3)
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

def benchmark_single_core(n, total_calculations):
    """Run single-core benchmark computing SAME total work as multi-core."""
    print("\n" + "=" * 60)
    print(f"SINGLE-CORE BENCHMARK ({total_calculations} calculations)")
    print("=" * 60)

    #Warmup
    print(f"\n[WARMUP] Running 2 warmup iterations...")
    for i in range(2):
        compute_pi_chudnovsky(min(100, n))

    #Benchmark
    print(f"\n[BENCHMARK] Computing {total_calculations} pi calculations sequentially...")
    times = []
    individual_times = []

    cpu_before = psutil.cpu_percent(interval=0.1, percpu=False)
    start_total = time.perf_counter()

    for i in range(total_calculations):
        start = time.perf_counter()
        pi_val = compute_pi_chudnovsky(n)
        elapsed = time.perf_counter() - start
        individual_times.append(elapsed)

        if (i + 1) % max(1, total_calculations // 5) == 0:
            print(f"  Progress: {i+1}/{total_calculations} calculations ({elapsed:.4f}s)")

    total_time = time.perf_counter() - start_total
    cpu_after = psutil.cpu_percent(interval=0.1, percpu=False)

    avg_per_calc = statistics.mean(individual_times)
    std_dev = statistics.stdev(individual_times) if len(individual_times) > 1 else 0

    operations = (n // 14 + 1) * total_calculations
    ops_per_sec = operations / total_time
    digits_per_sec = (n * total_calculations) / total_time

    print(f"\n[RESULTS]")
    print(f"  Total Calculations   : {total_calculations}")
    print(f"  Total Time           : {total_time:.6f} seconds")
    print(f"  Avg Time per Calc    : {avg_per_calc:.6f} seconds")
    print(f"  Std Deviation        : {std_dev:.6f} seconds")
    print(f"  Throughput           : {total_calculations/total_time:.2f} calculations/second")
    print(f"  Operations/Second    : {ops_per_sec:,.0f}")
    print(f"  Digits/Second        : {digits_per_sec:,.0f}")
    print(f"  Avg CPU Usage        : {(cpu_before + cpu_after)/2:.1f}%")

    return {
        'total_time': total_time,
        'total_calculations': total_calculations,
        'avg_per_calc': avg_per_calc,
        'throughput': total_calculations/total_time,
        'ops_per_sec': ops_per_sec,
        'digits_per_sec': digits_per_sec,
        'cpu_usage': (cpu_before + cpu_after)/2,
        'pi_value': str(pi_val)[:min(n + 2, 100)]
    }

def benchmark_multi_core(n, total_calculations):
    """Run multi-core benchmark computing SAME total work as single-core."""
    num_cores = mp.cpu_count()

    print("\n" + "=" * 60)
    print(f"MULTI-CORE BENCHMARK ({total_calculations} calculations on {num_cores} cores)")
    print("=" * 60)

    #Warmup
    print(f"\n[WARMUP] Running warmup on all cores...")
    with mp.Pool(processes=num_cores) as pool:
        warmup_tasks = [(i, min(100, n)) for i in range(num_cores * 2)]
        pool.map(worker_task, warmup_tasks)

    #Benchmark
    print(f"\n[BENCHMARK] Distributing {total_calculations} calculations across {num_cores} cores...")
    tasks = [(i, n) for i in range(total_calculations)]

    cpu_before = psutil.cpu_percent(interval=0.1, percpu=False)

    start_total = time.perf_counter()
    with mp.Pool(processes=num_cores) as pool:
        results = pool.map(worker_task, tasks)
    total_time = time.perf_counter() - start_total

    cpu_after = psutil.cpu_percent(interval=0.1, percpu=False)

    #Analyze individual task times
    individual_times = [r[1] for r in results]
    avg_per_calc = statistics.mean(individual_times)
    std_dev = statistics.stdev(individual_times) if len(individual_times) > 1 else 0

    operations = (n // 14 + 1) * total_calculations
    ops_per_sec = operations / total_time
    digits_per_sec = (n * total_calculations) / total_time

    print(f"\n[RESULTS]")
    print(f"  Total Calculations   : {total_calculations}")
    print(f"  Total Time           : {total_time:.6f} seconds")
    print(f"  Avg Time per Calc    : {avg_per_calc:.6f} seconds (per core)")
    print(f"  Std Deviation        : {std_dev:.6f} seconds")
    print(f"  Throughput           : {total_calculations/total_time:.2f} calculations/second")
    print(f"  Operations/Second    : {ops_per_sec:,.0f}")
    print(f"  Digits/Second        : {digits_per_sec:,.0f}")
    print(f"  Avg CPU Usage        : {(cpu_before + cpu_after)/2:.1f}%")

    return {
        'total_time': total_time,
        'total_calculations': total_calculations,
        'avg_per_calc': avg_per_calc,
        'throughput': total_calculations/total_time,
        'ops_per_sec': ops_per_sec,
        'digits_per_sec': digits_per_sec,
        'cpu_usage': (cpu_before + cpu_after)/2,
        'num_cores': num_cores
    }

def compare_performance(single, multi):
    """Generate detailed comparison between single and multi-core."""
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON - SAME TOTAL WORK")
    print("=" * 60)

    #Real_speedup: how much faster we completed the SAME work
    real_speedup = single['total_time'] / multi['total_time']
    parallel_efficiency = (real_speedup / multi['num_cores']) * 100

    #Throughput_comparison
    throughput_gain = multi['throughput'] / single['throughput']

    print(f"\n[WORKLOAD]")
    print(f"  Total Calculations   : {single['total_calculations']}")
    print(f"  Decimal Places       : (per calculation)")

    print(f"\n[TIME TO COMPLETE SAME WORK]")
    print(f"  Single-Core Time     : {single['total_time']:.6f} seconds")
    print(f"  Multi-Core Time      : {multi['total_time']:.6f} seconds")
    print(f"  Time Saved           : {single['total_time'] - multi['total_time']:.6f} seconds")
    print(f"  *** REAL SPEEDUP     : {real_speedup:.2f}x faster ***")

    print(f"\n[IDEAL vs ACTUAL]")
    print(f"  Number of Cores      : {multi['num_cores']}")
    print(f"  Ideal Speedup        : {multi['num_cores']:.2f}x (perfect scaling)")
    print(f"  Actual Speedup       : {real_speedup:.2f}x")
    print(f"  Parallel Efficiency  : {parallel_efficiency:.1f}%")
    print(f"  Efficiency Loss      : {100 - parallel_efficiency:.1f}%")

    print(f"\n[THROUGHPUT COMPARISON]")
    print(f"  Single-Core          : {single['throughput']:.2f} calculations/sec")
    print(f"  Multi-Core           : {multi['throughput']:.2f} calculations/sec")
    print(f"  Throughput Gain      : {throughput_gain:.2f}x")

    print(f"\n[OPERATIONS COMPARISON]")
    print(f"  Single-Core          : {single['ops_per_sec']:,.0f} ops/sec")
    print(f"  Multi-Core           : {multi['ops_per_sec']:,.0f} ops/sec")
    print(f"  Operations Gain      : {multi['ops_per_sec']/single['ops_per_sec']:.2f}x")

    print(f"\n[DIGITS THROUGHPUT]")
    print(f"  Single-Core          : {single['digits_per_sec']:,.0f} digits/sec")
    print(f"  Multi-Core           : {multi['digits_per_sec']:,.0f} digits/sec")
    print(f"  Digits Gain          : {multi['digits_per_sec']/single['digits_per_sec']:.2f}x")

    print(f"\n[CPU UTILIZATION]")
    print(f"  Single-Core Usage    : {single['cpu_usage']:.1f}%")
    print(f"  Multi-Core Usage     : {multi['cpu_usage']:.1f}%")

    print(f"\n[PER-CALCULATION TIME]")
    print(f"  Single-Core Avg      : {single['avg_per_calc']:.6f} sec/calculation")
    print(f"  Multi-Core Avg       : {multi['avg_per_calc']:.6f} sec/calculation")

    print(f"\n[SCALING ASSESSMENT]")
    if parallel_efficiency >= 90:
        rating = "Excellent"
        comment = "Near-perfect scaling! Minimal overhead."
    elif parallel_efficiency >= 75:
        rating = "Very Good"
        comment = "Strong scaling with acceptable overhead."
    elif parallel_efficiency >= 60:
        rating = "Good"
        comment = "Decent scaling, some overhead present."
    elif parallel_efficiency >= 40:
        rating = "Fair"
        comment = "Significant overhead from parallelization."
    else:
        rating = "Poor"
        comment = "High overhead - may not be worth parallelizing."

    print(f"  Scaling Efficiency   : {rating} ({parallel_efficiency:.1f}%)")
    print(f"  Assessment           : {comment}")

    if parallel_efficiency < 70:
        print(f"\n  Efficiency losses likely due to:")
        print(f"    • Process creation/management overhead")
        print(f"    • Memory bandwidth saturation")
        print(f"    • Cache contention between cores")
        print(f"    • Potential thermal throttling")

    #Real-world interpretation
    print(f"\n[REAL-WORLD INTERPRETATION]")
    hours_saved_per_1000 = ((single['total_time'] - multi['total_time']) * 1000) / 3600
    print(f"  For 1000 such tasks:")
    print(f"    Single-Core: {(single['total_time'] * 1000)/3600:.1f} hours")
    print(f"    Multi-Core:  {(multi['total_time'] * 1000)/3600:.1f} hours")
    print(f"    Time Saved:  {hours_saved_per_1000:.1f} hours ({real_speedup:.2f}x faster)")

    return {
        'real_speedup': real_speedup,
        'efficiency': parallel_efficiency,
        'rating': rating
    }

def run_full_benchmark(n, total_calculations):
    """Run complete single and multi-core benchmark suite."""
    print("=" * 60)
    print("CPU PERFORMANCE ANALYZER - COMPREHENSIVE BENCHMARK")
    print("=" * 60)

    #System_info
    cpu_info = get_cpu_info()
    print("\n[SYSTEM INFORMATION]")
    for key, value in cpu_info.items():
        print(f"  {key:20s}: {value}")

    print(f"\n[TEST CONFIGURATION]")
    print(f"  Decimal Places       : {n}")
    print(f"  Total Calculations   : {total_calculations}")
    print(f"  Algorithm Iterations : {n // 14 + 1} (per calculation)")
    print(f"\n  NOTE: Both benchmarks will compute the SAME total work")
    print(f"        to measure real speedup from parallelization.")

    #Run benchmarks with SAME total work
    single_results = benchmark_single_core(n, total_calculations)
    multi_results = benchmark_multi_core(n, total_calculations)

    #Compare
    comparison = compare_performance(single_results, multi_results)

    # Show pi value
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
        print("\n*** CPU Performance Analyzer - Real Speedup Measurement ***\n")

        n = int(input("Enter number of decimal places for pi (recommended: 1000-5000): "))
        if n < 100:
            print("Warning: Too few digits. Using 1000.")
            n = 1000
        elif n > 50000:
            print("Warning: Very large computation may take several minutes.")

        num_cores = mp.cpu_count()
        default_calcs = num_cores * 3  # 3 calculations per core

        print(f"\nYour system has {num_cores} cores.")
        print(f"Recommended: {default_calcs} total calculations ({default_calcs//num_cores} per core)")

        total_calcs = int(input(f"Enter total number of calculations (default: {default_calcs}): ") or str(default_calcs))

        if total_calcs < num_cores:
            print(f"Warning: Too few calculations. Using {num_cores} (1 per core).")
            total_calcs = num_cores

        #Run full benchmark suite
        single, multi, comparison = run_full_benchmark(n, total_calcs)

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
