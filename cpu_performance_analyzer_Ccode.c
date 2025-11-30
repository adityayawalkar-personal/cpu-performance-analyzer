//C code
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <pthread.h>
#include <unistd.h>
#include <gmp.h>

#ifdef _WIN32
    #include <windows.h>
#else
    #include <sys/sysinfo.h>
#endif

#define MAX_THREADS 256

// Global configuration
typedef struct {
    int decimal_places;
    int total_calculations;
    int num_cores;
} BenchmarkConfig;

// Thread work structure
typedef struct {
    int thread_id;
    int calculations_per_thread;
    int decimal_places;
    double* times;
    int start_index;
} ThreadWork;

// Results structure
typedef struct {
    double total_time;
    double avg_per_calc;
    double throughput;
    long long operations;
    double ops_per_sec;
} BenchmarkResults;

// Get number of CPU cores
int get_cpu_cores() {
#ifdef _WIN32
    SYSTEM_INFO sysinfo;
    GetSystemInfo(&sysinfo);
    return sysinfo.dwNumberOfProcessors;
#else
    return sysconf(_SC_NPROCESSORS_ONLN);
#endif
}

// Get CPU time in seconds
double get_cpu_time() {
    return (double)clock() / CLOCKS_PER_SEC;
}

// Get wall clock time in seconds
double get_wall_time() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

// Compute pi using Chudnovsky algorithm with GMP
void compute_pi_chudnovsky(mpf_t result, int n) {
    mpf_set_default_prec((n + 10) * 3.33);  // bits = digits * 3.33

    mpf_t C, K, M, X, L, S, temp1, temp2, temp3;
    mpf_t sqrt_10005, K_cubed, term;

    mpf_init(C);
    mpf_init(K);
    mpf_init(M);
    mpf_init(X);
    mpf_init(L);
    mpf_init(S);
    mpf_init(temp1);
    mpf_init(temp2);
    mpf_init(temp3);
    mpf_init(sqrt_10005);
    mpf_init(K_cubed);
    mpf_init(term);

    // C = 426880 * sqrt(10005)
    mpf_set_ui(sqrt_10005, 10005);
    mpf_sqrt(sqrt_10005, sqrt_10005);
    mpf_set_ui(C, 426880);
    mpf_mul(C, C, sqrt_10005);

    // Initialize values
    mpf_set_ui(K, 6);
    mpf_set_ui(M, 1);
    mpf_set_ui(X, 1);
    mpf_set_ui(L, 13591409);
    mpf_set(S, L);

    int iterations = n / 14 + 1;

    for (int i = 1; i < iterations; i++) {
        // M = M * (K^3 - 16*K) / i^3
        mpf_pow_ui(K_cubed, K, 3);
        mpf_set_ui(temp1, 16);
        mpf_mul(temp1, temp1, K);
        mpf_sub(temp2, K_cubed, temp1);
        mpf_mul(M, M, temp2);
        mpf_set_ui(temp3, i * i * i);
        mpf_div(M, M, temp3);

        // K += 12
        mpf_add_ui(K, K, 12);

        // L += 545140134
        mpf_add_ui(L, L, 545140134);

        // X *= -262537412640768000
        mpf_set_si(temp1, -262537412640768000LL);
        mpf_mul(X, X, temp1);

        // S += (M * L) / X
        mpf_mul(term, M, L);
        mpf_div(term, term, X);
        mpf_add(S, S, term);
    }

    // result = C / S
    mpf_div(result, C, S);

    // Cleanup
    mpf_clear(C);
    mpf_clear(K);
    mpf_clear(M);
    mpf_clear(X);
    mpf_clear(L);
    mpf_clear(S);
    mpf_clear(temp1);
    mpf_clear(temp2);
    mpf_clear(temp3);
    mpf_clear(sqrt_10005);
    mpf_clear(K_cubed);
    mpf_clear(term);
}

// Worker function for multi-threaded computation
void* worker_thread(void* arg) {
    ThreadWork* work = (ThreadWork*)arg;
    mpf_t pi_result;
    mpf_init(pi_result);

    for (int i = 0; i < work->calculations_per_thread; i++) {
        double start = get_wall_time();
        compute_pi_chudnovsky(pi_result, work->decimal_places);
        double elapsed = get_wall_time() - start;
        work->times[work->start_index + i] = elapsed;
    }

    mpf_clear(pi_result);
    return NULL;
}

// Single-core benchmark
BenchmarkResults benchmark_single_core(int n, int total_calculations) {
    printf("\n============================================================\n");
    printf("SINGLE-CORE BENCHMARK (%d calculations)\n", total_calculations);
    printf("============================================================\n");

    // Warmup
    printf("\n[WARMUP] Running 2 warmup iterations...\n");
    mpf_t pi_warmup;
    mpf_init(pi_warmup);
    for (int i = 0; i < 2; i++) {
        compute_pi_chudnovsky(pi_warmup, n < 100 ? n : 100);
    }
    mpf_clear(pi_warmup);

    // Benchmark
    printf("\n[BENCHMARK] Computing %d pi calculations sequentially...\n", total_calculations);

    double* times = malloc(total_calculations * sizeof(double));
    mpf_t pi_result;
    mpf_init(pi_result);

    double start_total = get_wall_time();

    for (int i = 0; i < total_calculations; i++) {
        double start = get_wall_time();
        compute_pi_chudnovsky(pi_result, n);
        times[i] = get_wall_time() - start;

        if ((i + 1) % (total_calculations / 5 > 0 ? total_calculations / 5 : 1) == 0) {
            printf("  Progress: %d/%d calculations (%.4f s)\n", i+1, total_calculations, times[i]);
        }
    }

    double total_time = get_wall_time() - start_total;

    // Calculate statistics
    double sum = 0.0;
    for (int i = 0; i < total_calculations; i++) {
        sum += times[i];
    }
    double avg_per_calc = sum / total_calculations;

    long long operations = (long long)(n / 14 + 1) * total_calculations;

    printf("\n[RESULTS]\n");
    printf("  Total Calculations   : %d\n", total_calculations);
    printf("  Total Time           : %.6f seconds\n", total_time);
    printf("  Avg Time per Calc    : %.6f seconds\n", avg_per_calc);
    printf("  Throughput           : %.2f calculations/second\n", total_calculations / total_time);
    printf("  Operations/Second    : %.0f\n", operations / total_time);
    printf("  Digits/Second        : %.0f\n", (double)n * total_calculations / total_time);

    // Print pi value
    char* pi_str = malloc(n + 10);
    gmp_sprintf(pi_str, "%.*Ff", n < 98 ? n : 98, pi_result);

    BenchmarkResults results;
    results.total_time = total_time;
    results.avg_per_calc = avg_per_calc;
    results.throughput = total_calculations / total_time;
    results.operations = operations;
    results.ops_per_sec = operations / total_time;

    free(times);
    free(pi_str);
    mpf_clear(pi_result);

    return results;
}

// Multi-core benchmark
BenchmarkResults benchmark_multi_core(int n, int total_calculations, int num_cores) {
    printf("\n============================================================\n");
    printf("MULTI-CORE BENCHMARK (%d calculations on %d cores)\n", total_calculations, num_cores);
    printf("============================================================\n");

    // Warmup
    printf("\n[WARMUP] Running warmup on all cores...\n");
    pthread_t warmup_threads[num_cores];
    ThreadWork warmup_work[num_cores];
    double warmup_times[num_cores * 2];

    for (int i = 0; i < num_cores; i++) {
        warmup_work[i].thread_id = i;
        warmup_work[i].calculations_per_thread = 2;
        warmup_work[i].decimal_places = n < 100 ? n : 100;
        warmup_work[i].times = warmup_times;
        warmup_work[i].start_index = i * 2;
        pthread_create(&warmup_threads[i], NULL, worker_thread, &warmup_work[i]);
    }

    for (int i = 0; i < num_cores; i++) {
        pthread_join(warmup_threads[i], NULL);
    }

    // Benchmark
    printf("\n[BENCHMARK] Distributing %d calculations across %d cores...\n", total_calculations, num_cores);

    pthread_t threads[num_cores];
    ThreadWork work[num_cores];
    double* times = malloc(total_calculations * sizeof(double));

    int calcs_per_thread = total_calculations / num_cores;
    int remaining = total_calculations % num_cores;

    double start_total = get_wall_time();

    int current_index = 0;
    for (int i = 0; i < num_cores; i++) {
        work[i].thread_id = i;
        work[i].calculations_per_thread = calcs_per_thread + (i < remaining ? 1 : 0);
        work[i].decimal_places = n;
        work[i].times = times;
        work[i].start_index = current_index;
        current_index += work[i].calculations_per_thread;

        pthread_create(&threads[i], NULL, worker_thread, &work[i]);
    }

    // Wait for all threads
    for (int i = 0; i < num_cores; i++) {
        pthread_join(threads[i], NULL);
    }

    double total_time = get_wall_time() - start_total;

    // Calculate statistics
    double sum = 0.0;
    for (int i = 0; i < total_calculations; i++) {
        sum += times[i];
    }
    double avg_per_calc = sum / total_calculations;

    long long operations = (long long)(n / 14 + 1) * total_calculations;

    printf("\n[RESULTS]\n");
    printf("  Total Calculations   : %d\n", total_calculations);
    printf("  Total Time           : %.6f seconds\n", total_time);
    printf("  Avg Time per Calc    : %.6f seconds (per core)\n", avg_per_calc);
    printf("  Throughput           : %.2f calculations/second\n", total_calculations / total_time);
    printf("  Operations/Second    : %.0f\n", operations / total_time);
    printf("  Digits/Second        : %.0f\n", (double)n * total_calculations / total_time);

    BenchmarkResults results;
    results.total_time = total_time;
    results.avg_per_calc = avg_per_calc;
    results.throughput = total_calculations / total_time;
    results.operations = operations;
    results.ops_per_sec = operations / total_time;

    free(times);

    return results;
}

// Compare performance
void compare_performance(BenchmarkResults single, BenchmarkResults multi, int num_cores, int total_calculations) {
    printf("\n============================================================\n");
    printf("PERFORMANCE COMPARISON - SAME TOTAL WORK\n");
    printf("============================================================\n");

    double real_speedup = single.total_time / multi.total_time;
    double parallel_efficiency = (real_speedup / num_cores) * 100.0;

    printf("\n[WORKLOAD]\n");
    printf("  Total Calculations   : %d\n", total_calculations);

    printf("\n[TIME TO COMPLETE SAME WORK]\n");
    printf("  Single-Core Time     : %.6f seconds\n", single.total_time);
    printf("  Multi-Core Time      : %.6f seconds\n", multi.total_time);
    printf("  Time Saved           : %.6f seconds\n", single.total_time - multi.total_time);
    printf("  *** REAL SPEEDUP     : %.2fx faster ***\n", real_speedup);

    printf("\n[IDEAL vs ACTUAL]\n");
    printf("  Number of Cores      : %d\n", num_cores);
    printf("  Ideal Speedup        : %.2fx (perfect scaling)\n", (double)num_cores);
    printf("  Actual Speedup       : %.2fx\n", real_speedup);
    printf("  Parallel Efficiency  : %.1f%%\n", parallel_efficiency);
    printf("  Efficiency Loss      : %.1f%%\n", 100.0 - parallel_efficiency);

    printf("\n[THROUGHPUT COMPARISON]\n");
    printf("  Single-Core          : %.2f calculations/sec\n", single.throughput);
    printf("  Multi-Core           : %.2f calculations/sec\n", multi.throughput);
    printf("  Throughput Gain      : %.2fx\n", multi.throughput / single.throughput);

    printf("\n[OPERATIONS COMPARISON]\n");
    printf("  Single-Core          : %.0f ops/sec\n", single.ops_per_sec);
    printf("  Multi-Core           : %.0f ops/sec\n", multi.ops_per_sec);
    printf("  Operations Gain      : %.2fx\n", multi.ops_per_sec / single.ops_per_sec);

    printf("\n[SCALING ASSESSMENT]\n");
    const char* rating;
    const char* comment;

    if (parallel_efficiency >= 90) {
        rating = "Excellent";
        comment = "Near-perfect scaling! Minimal overhead.";
    } else if (parallel_efficiency >= 75) {
        rating = "Very Good";
        comment = "Strong scaling with acceptable overhead.";
    } else if (parallel_efficiency >= 60) {
        rating = "Good";
        comment = "Decent scaling, some overhead present.";
    } else if (parallel_efficiency >= 40) {
        rating = "Fair";
        comment = "Significant overhead from parallelization.";
    } else {
        rating = "Poor";
        comment = "High overhead - may not be worth parallelizing.";
    }

    printf("  Scaling Efficiency   : %s (%.1f%%)\n", rating, parallel_efficiency);
    printf("  Assessment           : %s\n", comment);

    if (parallel_efficiency < 70) {
        printf("\n  Efficiency losses likely due to:\n");
        printf("    • Thread creation/management overhead\n");
        printf("    • Memory bandwidth saturation\n");
        printf("    • Cache contention between cores\n");
        printf("    • Potential thermal throttling\n");
    }

    printf("\n[REAL-WORLD INTERPRETATION]\n");
    double hours_saved = ((single.total_time - multi.total_time) * 1000.0) / 3600.0;
    printf("  For 1000 such tasks:\n");
    printf("    Single-Core: %.1f hours\n", (single.total_time * 1000.0) / 3600.0);
    printf("    Multi-Core:  %.1f hours\n", (multi.total_time * 1000.0) / 3600.0);
    printf("    Time Saved:  %.1f hours (%.2fx faster)\n", hours_saved, real_speedup);
}

// Main function
int main() {
    printf("\n*** CPU Performance Analyzer - Real Speedup Measurement (C) ***\n\n");

    int num_cores = get_cpu_cores();
    printf("System has %d CPU cores detected.\n\n", num_cores);

    int n, total_calculations;

    printf("Enter number of decimal places for pi (recommended: 1000-5000): ");
    scanf("%d", &n);

    if (n < 100) {
        printf("Warning: Too few digits. Using 1000.\n");
        n = 1000;
    } else if (n > 50000) {
        printf("Warning: Very large computation may take several minutes.\n");
    }

    int default_calcs = num_cores * 3;
    printf("\nYour system has %d cores.\n", num_cores);
    printf("Recommended: %d total calculations (%d per core)\n", default_calcs, 3);
    printf("Enter total number of calculations (or 0 for default): ");
    scanf("%d", &total_calculations);

    if (total_calculations == 0) {
        total_calculations = default_calcs;
    }

    if (total_calculations < num_cores) {
        printf("Warning: Too few calculations. Using %d (1 per core).\n", num_cores);
        total_calculations = num_cores;
    }

    printf("\n============================================================\n");
    printf("CPU PERFORMANCE ANALYZER - COMPREHENSIVE BENCHMARK\n");
    printf("============================================================\n");

    printf("\n[SYSTEM INFORMATION]\n");
    printf("  CPU Cores            : %d\n", num_cores);

    printf("\n[TEST CONFIGURATION]\n");
    printf("  Decimal Places       : %d\n", n);
    printf("  Total Calculations   : %d\n", total_calculations);
    printf("  Algorithm Iterations : %d (per calculation)\n", n / 14 + 1);
    printf("\n  NOTE: Both benchmarks will compute the SAME total work\n");
    printf("        to measure real speedup from parallelization.\n");

    // Run benchmarks
    BenchmarkResults single = benchmark_single_core(n, total_calculations);
    BenchmarkResults multi = benchmark_multi_core(n, total_calculations, num_cores);

    // Compare
    compare_performance(single, multi, num_cores, total_calculations);

    printf("\n============================================================\n");
    printf("BENCHMARK COMPLETE\n");
    printf("============================================================\n\n");

    return 0;
}