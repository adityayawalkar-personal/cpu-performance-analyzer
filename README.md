<h1>⚡ CPU Performance Analyzer</h1>

<p>A comprehensive benchmarking suite that measures CPU performance through high-precision pi calculations using the Chudnovsky algorithm. Includes single-core, multi-core, and parallel processing benchmarks in both Python and C.</p>

<p>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.7+-blue.svg">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green.svg">
  </a>
</p>

<h2>📋 Table of Contents</h2>
<ul>
  <li><a href="#overview">Overview</a></li>
  <li><a href="#features">Features</a></li>
  <li><a href="#requirements">Requirements</a></li>
  <li><a href="#benchmark-versions">Benchmark Versions</a></li>
  <li><a href="#performance-metrics">Performance Metrics</a></li>
  <li><a href="#understanding-results">Understanding Results</a></li>
  <li><a href="#example-output">Example Output</a></li>
  <li><a href="#project-structure">Project Structure</a></li>
  <li><a href="#contributing">Contributing</a></li>
</ul>

<!-- ==================== OVERVIEW ==================== -->

<h2 id="overview">🎯 Overview</h2>
<p>
This project provides multiple versions of CPU benchmarking tools that calculate pi to arbitrary precision using the Chudnovsky algorithm. It measures real-world CPU performance by comparing single-core vs multi-core execution, calculating speedup factors, and analyzing parallel efficiency.
</p>

<h3>Why Pi Calculation?</h3>
<ul>
  <li><b>CPU-Intensive</b>: Requires heavy arithmetic operations</li>
  <li><b>Memory-Intensive</b>: Tests RAM bandwidth with large precision numbers</li>
  <li><b>Scalable</b>: Adjustable difficulty</li>
  <li><b>Deterministic</b>: Same input → same result</li>
  <li><b>Real-World</b>: Similar to scientific workloads</li>
</ul>

<!-- ==================== FEATURES ==================== -->

<h2 id="features">✨ Features</h2>

<h3>Core Features</h3>
<ul>
  <li>High-precision arithmetic (thousands of digits)</li>
  <li>Single-core and multi-core benchmarking</li>
  <li>Real speedup measurement</li>
  <li>Time, throughput, operations/second, efficiency metrics</li>
  <li>Automatic system information</li>
  <li>Statistical analysis + performance ratings</li>
</ul>

<h3>Advanced Features</h3>
<ul>
  <li>Warmup iterations</li>
  <li>Parallel efficiency calculation</li>
  <li>Real-world time projections</li>
  <li>Multiple implementations (Python & C)</li>
  <li>Progress tracking</li>
</ul>

<!-- ==================== REQUIREMENTS ==================== -->

<h2 id="requirements">💻 Requirements</h2>

<h3>Python Version</h3>

<pre><code>python >= 3.7
psutil >= 5.8.0
</code></pre>

<p><b>Basic Version:</b> no extra libraries</p>

<h3>C Version</h3>
<ul>
  <li>GCC/Clang compiler</li>
  <li>GMP library</li>
  <li>pthread (POSIX threads)</li>
</ul>

<pre><code># Ubuntu
sudo apt-get install build-essential libgmp-dev

# macOS
brew install gmp

# Windows (MinGW)
pacman -S mingw-w64-x86_64-gmp
</code></pre>

<!-- ==================== PERFORMANCE METRICS ==================== -->

<h2 id="performance-metrics">📊 Performance Metrics</h2>

<table border="1" cellpadding="6">
<tr><th>Metric</th><th>Description</th><th>Importance</th></tr>
<tr><td>Total Time</td><td>Wall-clock time</td><td>Speed</td></tr>
<tr><td>Throughput</td><td>Calculations/sec</td><td>Overall performance</td></tr>
<tr><td>Operations/Second</td><td>Algorithm iterations/sec</td><td>Raw compute power</td></tr>
<tr><td>Digits/Second</td><td>Digits computed per sec</td><td>Task performance</td></tr>
<tr><td>Speedup Factor</td><td>Parallel improvement</td><td>Scaling measure</td></tr>
<tr><td>Parallel Efficiency</td><td>Speedup ÷ Cores</td><td>Core utilization</td></tr>
</table>

<!-- ==================== UNDERSTANDING RESULTS ==================== -->

<h2 id="understanding-results">🔍 Understanding Results</h2>
<p>
Real speedup is measured by performing the same amount of work on single-core and multi-core setups. This avoids falsely inflated speedup values.
</p>

<pre><code>Single-Core Time: 10s
Multi-Core Time : 2.5s
Speedup         : 4.0x
Efficiency      : 50%
</code></pre>

<!-- ==================== EXAMPLE OUTPUT ==================== -->

<h2 id="example-output">📈 Example Output</h2>

<p>A long formatted sample output with system info, benchmark results, efficiency, and real-world interpretation.</p>

<!-- ==================== PROJECT STRUCTURE ==================== -->

<h2 id="project-structure">📁 Project Structure</h2>

<pre><code>
cpu-performance-analyzer/
│
├── python_versions/
│   ├── code1_basic.py
│   ├── code2_v1_comprehensive.py
│   ├── code2_v2_multicore.py
│   └── code2_v3_real_speedup.py
│
├── c_version/
│   ├── cpu_benchmark.c
│   ├── Makefile
│   └── README_C.md
│
├── results/
├── docs/
├── requirements.txt
├── LICENSE
└── README.md
</code></pre>

<!-- ==================== CONTRIBUTING ==================== -->

<h2 id="contributing">🤝 Contributing</h2>
<ol>
  <li>Fork the repository</li>
  <li>Create a feature branch</li>
  <li>Submit a Pull Request</li>
</ol>

<!-- ==================== AUTHOR ==================== -->

<h2>👨‍💻 Author</h2>
<p><b>Aditya Yawalkar</b><br>
GitHub: <a href="https://github.com/adityayawalkar-personal">@adityayawalkar-personal</a><br>

<!-- ==================== ACKNOWLEDGMENTS ==================== -->

<h2>🙏 Acknowledgments</h2>
<ul>
  <li>Chudnovsky algorithm creators</li>
  <li>GMP developers</li>
  <li>Python Software Foundation</li>
</ul>

<!-- ==================== FURTHER READING ==================== -->

<h2>📚 Further Reading</h2>
<ul>
  <li><a href="https://en.wikipedia.org/wiki/Chudnovsky_algorithm">Chudnovsky Algorithm</a></li>
  <li><a href="https://en.wikipedia.org/wiki/Amdahl%27s_law">Parallel Efficiency</a></li>
</ul>
