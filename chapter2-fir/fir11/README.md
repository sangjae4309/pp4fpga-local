# Project 1 – FIR Filter (11-tap)

11-tap FIR filter implemented in Vitis HLS.  
Several implementations are provided to compare HLS coding styles and directives.

Reference: [Parallel Programming for FPGAs, Ch. 2 – FIR Filters](https://kastner.ucsd.edu/hlsbook/)

---

## Implementations

| `IMPL` | File | Description |
|--------|------|-------------|
| `fir` (default) | [src/fir.cpp](src/fir.cpp) | Baseline – `if (i == 0)` branch lives **inside** the loop body |
| `fir_code_hoist` | [src/fir_code_hoist.cpp](src/fir_code_hoist.cpp) | Optimized – the `i == 0` special case is **hoisted out** of the loop |
| `fir_loop_fission` | [src/fir_loop_fission.cpp](src/fir_loop_fission.cpp) | Shift-register update and MAC split into separate loops |
| `fir_loop_unrolling` | [src/fir_loop_unrolling.cpp](src/fir_loop_unrolling.cpp) | Manual factor-2 loop unrolling |
| `fir_loop_unrolling_directive` | [src/fir_loop_unrolling_directive.cpp](src/fir_loop_unrolling_directive.cpp) | Factor-2 unrolling with HLS pragmas |
| `fir_pipeline_directive` | [src/fir_pipeline_directive.cpp](src/fir_pipeline_directive.cpp) | Loop pipelining with HLS pragmas |
| `fir_pipeline_directive_bit_opt` | [src/fir_pipeline_directive_bit_opt.cpp](src/fir_pipeline_directive_bit_opt.cpp) | Pipeline version using `ap_int` coefficient type |

Removing the branch gives the HLS scheduler a cleaner loop body, which can improve pipeline initiation interval (II) and resource usage.

---

## Directory Structure

```
fir11/
├── src/
│   ├── fir.h               shared header (types, N=11, function prototype)
│   ├── fir_bit_opt.h       bit-optimized shared header using ap_int
│   ├── fir.cpp             baseline implementation
│   ├── fir_code_hoist.cpp  code-hoisted implementation
│   ├── fir_loop_fission.cpp
│   ├── fir_loop_unrolling.cpp
│   ├── fir_loop_unrolling_directive.cpp
│   ├── fir_pipeline_directive.cpp
│   ├── fir_pipeline_directive_bit_opt.cpp
│   └── fir_test.cpp        shared C-sim testbench
├── script/syn.tcl          Vitis HLS synthesis Tcl template
├── plot_metrics.py         report parser and CSV/PNG table generator
├── run.py                  full C-test, HLS, and report pipeline
├── input.dat               chirp input samples (600 samples)
├── out.gold.dat            golden reference output
└── Makefile
```

---

## Quick Start

```bash
# C-test + HLS synthesis + metrics CSV/PNG summary for all implementations
python3 run.py

# C-test only
python3 run.py test

# HLS synthesis + metrics only
python3 run.py syn

# Metrics only from existing *.comp directories
python3 plot_metrics.py

# Individual C-test
make IMPL=fir test
make IMPL=fir_code_hoist test

# Individual HLS synthesis
make IMPL=fir hls
make IMPL=fir_code_hoist hls

# Individual C-test + HLS synthesis
make IMPL=fir
make IMPL=fir_code_hoist

# Remove all build artifacts
make clean
```

---

## Build Outputs

| File / Directory | Created by | Description |
|-----------------|------------|-------------|
| `$(IMPL).bin` | `make test` | Compiled C-sim binary |
| `$(IMPL)_csim.log` | `make test` | C-sim stdout (PASS/FAIL) |
| `logs/*_csim.log` | `python3 run.py` | Per-implementation C-test logs |
| `logs/*_syn.log` | `python3 run.py` | Per-implementation HLS logs |
| `$(IMPL).comp/` | `make hls` | HLS component directory (synthesis output) |
| `reports/run_results.tsv` | `python3 run.py` | C-test/HLS status table |
| `reports/metrics.csv` | `python3 plot_metrics.py` | Parsed latency/resource metrics from existing `*.comp` directories |
| `reports/summary_table.png` | `python3 plot_metrics.py` | Summary table image for latency, II, timing, and resources |

The active HLS target settings live in [script/syn.tcl](script/syn.tcl).
Change `set_part` and `create_clock` there to match your target board.

---

## Current HLS Results

The table below is parsed from the current `*.comp/hls/syn/report/*csynth.xml`
files using:

```bash
python3 plot_metrics.py
```

| Implementation | Latency | II | Clock (ns) | DSP | FF | LUT | BRAM |
|----------------|--------:|---:|-----------:|----:|---:|----:|-----:|
| Baseline | 19 | 20 | 6.91 | 2 | 573 | 407 | 0 |
| Code Hoist | 17 | 18 | 6.91 | 2 | 572 | 390 | 0 |
| Loop Fission | 33 | 34 | 6.91 | 2 | 487 | 351 | 0 |
| Manual Unroll | 36 | 37 | 6.91 | 4 | 1358 | 1190 | 0 |
| Pragma Unroll | 37 | 38 | 6.91 | 4 | 1390 | 1097 | 0 |
| Pipeline | 33 | 34 | 6.91 | 2 | 486 | 364 | 0 |
| Pipeline Bit Opt | 33 | 34 | 6.91 | 2 | 442 | 360 | 0 |

`Latency` is the number of cycles from starting one `fir()` call to receiving
its output. `II` is the initiation interval: how many cycles must pass before
the next `fir()` call can start. For repeated sample processing, lower II means
higher throughput.

