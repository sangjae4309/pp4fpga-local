#!/usr/bin/env python3
"""Run C-tests, HLS synthesis, and FIR metric report generation."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


IMPLS = [
    "fir",
    "fir_code_hoist",
    "fir_loop_fission",
    "fir_loop_unrolling",
    "fir_loop_unrolling_directive",
    "fir_pipeline_directive",
    "fir_pipeline_directive_bit_opt",
]

def run_make(root, impl, target, log_path):
    cmd = ["make", "--no-print-directory", f"IMPL={impl}", target]
    with log_path.open("w") as log:
        proc = subprocess.run(cmd, cwd=root, stdout=log, stderr=subprocess.STDOUT)
    return proc.returncode


def log_contains(path, needle):
    try:
        return needle in path.read_text(errors="replace")
    except FileNotFoundError:
        return False


def run_csim(root, log_dir, impl):
    log = log_dir / f"{impl}_csim.log"
    print(f"  [csim] {impl} ...")
    rc = run_make(root, impl, "test", log)
    if rc != 0:
        return f"FAIL(exit {rc})"
    if log_contains(log, "PASS"):
        return "PASS"
    return "FAIL(no PASS string)"


def has_csynth_report(root, impl, log):
    comp_dir = root / f"{impl}.comp"
    if not comp_dir.exists():
        return False

    log_mtime = log.stat().st_mtime if log.exists() else 0
    reports = list(comp_dir.rglob("*csynth.rpt"))
    if not reports:
        return False
    return any(report.stat().st_mtime >= log_mtime for report in reports) or bool(reports)


def run_synth(root, log_dir, impl):
    log = log_dir / f"{impl}_syn.log"
    print(f"  [syn]  {impl} ...")
    if shutil.which("vitis-run") is None:
        log.write_text(
            f"Skipped HLS synthesis for {impl}\n"
            "Reason: vitis-run was not found.\n"
            "Source Xilinx/Vitis settings before running synthesis.\n"
        )
        return "SKIP(no vitis-run)"

    rc = run_make(root, impl, "hls", log)
    if rc != 0:
        return "FAIL(exit)"
    if has_csynth_report(root, impl, log):
        return "PASS"
    return "FAIL(no rpt)"


def write_results(path, impls, test_results, synth_results):
    with path.open("w") as fp:
        for impl in impls:
            fp.write(f"{impl}\t{test_results.get(impl, 'SKIP')}\t{synth_results.get(impl, 'SKIP')}\n")


def print_status_table(impls, test_results, synth_results):
    print()
    print("==================================================================")
    print(f" {'Implementation':<35}  {'C-Sim Test':<12}  {'HLS Synth':<12}")
    print("------------------------------------------------------------------")

    failed = False
    for impl in impls:
        test = test_results.get(impl, "SKIP")
        synth = synth_results.get(impl, "SKIP")
        failed = failed or test.startswith("FAIL") or synth.startswith("FAIL")
        print(f" {impl:<35}  {test:<22}  {synth:<22}")

    print("==================================================================")
    print()
    if failed:
        print("Some checks failed - see logs/ for details.")
    else:
        print("All checks passed.")
    print()
    return failed


def run_metrics(root, report_dir):
    print("==================================================================")
    print(" FIR Metrics Summary")
    print("==================================================================")
    cmd = [
        sys.executable,
        str(root / "plot_metrics.py"),
        "--outdir",
        str(report_dir),
    ]
    return subprocess.run(cmd, cwd=root).returncode


def parse_args():
    parser = argparse.ArgumentParser(description="Run FIR C-tests, HLS synthesis, and reports")
    parser.add_argument("mode", nargs="?", default="all", choices=["all", "test", "syn"])
    return parser.parse_args()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    args = parse_args()
    root = Path(__file__).resolve().parent
    log_dir = root / "logs"
    report_dir = root / "reports"
    results_tsv = report_dir / "run_results.tsv"
    log_dir.mkdir(exist_ok=True)
    report_dir.mkdir(exist_ok=True)

    test_results = {}
    synth_results = {}

    print()
    print("==================================================================")
    print(" FIR Design Suite - run.py")
    print(f" Mode: {args.mode}")
    print("==================================================================")
    print()

    for impl in IMPLS:
        if args.mode in {"all", "test"}:
            test_results[impl] = run_csim(root, log_dir, impl)
        else:
            test_results[impl] = "SKIP"

        if args.mode in {"all", "syn"}:
            synth_results[impl] = run_synth(root, log_dir, impl)
        else:
            synth_results[impl] = "SKIP"

    write_results(results_tsv, IMPLS, test_results, synth_results)
    failed = print_status_table(IMPLS, test_results, synth_results)
    metrics_rc = 0
    if args.mode in {"all", "syn"}:
        metrics_rc = run_metrics(root, report_dir)
    print()

    return 1 if failed or metrics_rc != 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
