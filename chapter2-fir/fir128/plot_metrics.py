#!/usr/bin/env python3
"""
Parse Vitis HLS csynth XML reports and generate a summary table PNG.

This script intentionally uses only the Python standard library so the full
pipeline works on lab machines without installing matplotlib.
"""

import argparse
import csv
import struct
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path


IMPL_ORDER = [
    "fir",
    "fir_code_hoist",
    "fir_loop_fission",
    "fir_loop_unrolling",
    "fir_loop_unrolling_directive",
    "fir_pipeline_directive",
    "fir_pipeline_directive_bit_opt",
]

DISPLAY_NAMES = {
    "fir": "Baseline",
    "fir_code_hoist": "Code Hoist",
    "fir_loop_fission": "Loop Fission",
    "fir_loop_unrolling": "Manual Unroll",
    "fir_loop_unrolling_directive": "Pragma Unroll",
    "fir_pipeline_directive": "Pipeline",
    "fir_pipeline_directive_bit_opt": "Pipeline Bit Opt",
}

FIELDS = [
    "impl",
    "latency_min",
    "latency_max",
    "interval_min",
    "interval_max",
    "estimated_clock_ns",
    "estimated_freq_mhz",
    "DSP",
    "FF",
    "LUT",
    "BRAM_18K",
]

TABLE_COLUMNS = [
    ("impl", "Implementation", 310),
    ("latency_max", "Latency", 75),
    ("interval_max", "II", 55),
    ("estimated_clock_ns", "Clk(ns)", 75),
    ("DSP", "DSP", 55),
    ("FF", "FF", 70),
    ("LUT", "LUT", 70),
    ("BRAM_18K", "BRAM", 60),
]


def text(root, path, default=""):
    if root is None:
        return default
    node = root.find(path)
    if node is None or node.text is None:
        return default
    return node.text.strip()


def to_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def choose_report(comp_dir):
    report_dir = comp_dir / "hls" / "syn" / "report"
    preferred = report_dir / "fir_csynth.xml"
    if preferred.exists():
        return preferred
    generic = report_dir / "csynth.xml"
    if generic.exists():
        return generic
    xmls = sorted(report_dir.glob("*_csynth.xml"))
    return xmls[0] if xmls else None


def parse_report(impl, xml_path):
    row = {field: "" for field in FIELDS}
    row["impl"] = impl

    if xml_path is None:
        return row

    root = ET.parse(xml_path).getroot()
    perf = root.find("PerformanceEstimates")
    area = root.find("AreaEstimates")
    resources = area.find("Resources") if area is not None else None

    est_clk = to_float(text(perf, "SummaryOfTimingAnalysis/EstimatedClockPeriod"))
    row.update(
        {
            "latency_min": to_int(text(perf, "SummaryOfOverallLatency/Best-caseLatency")),
            "latency_max": to_int(text(perf, "SummaryOfOverallLatency/Worst-caseLatency")),
            "interval_min": to_int(text(perf, "SummaryOfOverallLatency/Interval-min")),
            "interval_max": to_int(text(perf, "SummaryOfOverallLatency/Interval-max")),
            "estimated_clock_ns": est_clk,
            "estimated_freq_mhz": (1000.0 / est_clk) if est_clk else 0.0,
            "DSP": to_int(text(resources, "DSP")),
            "FF": to_int(text(resources, "FF")),
            "LUT": to_int(text(resources, "LUT")),
            "BRAM_18K": to_int(text(resources, "BRAM_18K")),
        }
    )
    return row


def collect(root_dir):
    rows = []
    impls = [impl for impl in IMPL_ORDER if (root_dir / f"{impl}.comp").exists()]

    extra_comp_dirs = sorted(root_dir.glob("*.comp"))
    for comp_dir in extra_comp_dirs:
        impl = comp_dir.name.removesuffix(".comp")
        if impl not in impls:
            impls.append(impl)

    for impl in impls:
        xml_path = choose_report(root_dir / f"{impl}.comp")
        if xml_path is not None:
            rows.append(parse_report(impl, xml_path))
    return rows


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def format_cell(row, field):
    value = row.get(field, "")
    if value == "":
        return "-"
    if field == "impl":
        return DISPLAY_NAMES.get(value, str(value))
    if field in {"estimated_clock_ns", "estimated_freq_mhz"}:
        return f"{float(value):.2f}"
    return str(value)


def print_table(rows):
    columns = [
        ("impl", "Implementation", 32),
        ("latency_max", "Latency", 8),
        ("interval_max", "II", 5),
        ("estimated_clock_ns", "Clk(ns)", 8),
        ("DSP", "DSP", 5),
        ("FF", "FF", 7),
        ("LUT", "LUT", 7),
        ("BRAM_18K", "BRAM", 5),
    ]
    header = " ".join(
        label.rjust(width) if field != "impl" else label.ljust(width)
        for field, label, width in columns
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            " ".join(
                format_cell(row, field).rjust(width)
                if field != "impl"
                else format_cell(row, field).ljust(width)
                for field, _label, width in columns
            )
        )


FONT = {
    " ": ["000", "000", "000", "000", "000", "000", "000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ".": ["0", "0", "0", "0", "0", "0", "1"],
    "(": ["01", "10", "10", "10", "10", "10", "01"],
    ")": ["10", "01", "01", "01", "01", "01", "10"],
    "/": ["00001", "00010", "00100", "01000", "10000", "00000", "00000"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["111", "010", "010", "010", "010", "010", "111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
}


def put_pixel(img, width, height, x, y, color):
    if 0 <= x < width and 0 <= y < height:
        img[y][x] = color


def fill_rect(img, width, height, x, y, w, h, color):
    for yy in range(max(0, y), min(height, y + h)):
        row = img[yy]
        for xx in range(max(0, x), min(width, x + w)):
            row[xx] = color


def draw_text(img, width, height, x, y, text_value, color=(30, 30, 30), scale=2):
    cursor = x
    for char in str(text_value).upper():
        pattern = FONT.get(char, FONT[" "])
        for row_idx, bits in enumerate(pattern):
            for col_idx, bit in enumerate(bits):
                if bit == "1":
                    fill_rect(
                        img,
                        width,
                        height,
                        cursor + col_idx * scale,
                        y + row_idx * scale,
                        scale,
                        scale,
                        color,
                    )
        cursor += (len(pattern[0]) + 1) * scale


def png_chunk(kind, payload):
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_png(path, img, width, height):
    raw = bytearray()
    for row in img:
        raw.append(0)
        for red, green, blue in row:
            raw.extend((red, green, blue))

    data = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            png_chunk(b"IDAT", zlib.compress(bytes(raw), level=9)),
            png_chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(data)


def write_table_png(rows, path):
    margin = 20
    title_h = 34
    row_h = 30
    header_h = 34
    width = margin * 2 + sum(col[2] for col in TABLE_COLUMNS)
    height = margin * 2 + title_h + header_h + row_h * len(rows)
    img = [[(255, 255, 255) for _ in range(width)] for _ in range(height)]

    fill_rect(img, width, height, 0, 0, width, height, (255, 255, 255))
    draw_text(img, width, height, margin, 14, "FIR HLS SUMMARY", (20, 20, 20), scale=3)

    y = margin + title_h
    x = margin
    fill_rect(img, width, height, margin, y, width - 2 * margin, header_h, (40, 49, 59))
    for field, label, col_w in TABLE_COLUMNS:
        draw_text(img, width, height, x + 8, y + 10, label, (255, 255, 255), scale=2)
        x += col_w

    y += header_h
    for row_idx, row in enumerate(rows):
        bg = (248, 250, 252) if row_idx % 2 == 0 else (255, 255, 255)
        fill_rect(img, width, height, margin, y, width - 2 * margin, row_h, bg)
        x = margin
        for field, _label, col_w in TABLE_COLUMNS:
            draw_text(img, width, height, x + 8, y + 9, format_cell(row, field), (30, 41, 59), scale=2)
            x += col_w
            fill_rect(img, width, height, x, y, 1, row_h, (226, 232, 240))
        fill_rect(img, width, height, margin, y + row_h - 1, width - 2 * margin, 1, (226, 232, 240))
        y += row_h

    path.parent.mkdir(parents=True, exist_ok=True)
    write_png(path, img, width, height)


def main():
    parser = argparse.ArgumentParser(description="Summarize Vitis HLS FIR metrics")
    parser.add_argument("--root", default=Path(__file__).resolve().parent, type=Path)
    parser.add_argument("--outdir", default="reports")
    args = parser.parse_args()

    root_dir = args.root.resolve()
    outdir = root_dir / args.outdir
    rows = collect(root_dir)

    if not rows:
        print("No HLS csynth XML reports found under *.comp directories.", file=sys.stderr)
        return 1

    csv_path = outdir / "metrics.csv"
    png_path = outdir / "summary_table.png"
    write_csv(rows, csv_path)
    write_table_png(rows, png_path)
    print_table(rows)
    print()
    print(f"CSV: {csv_path}")
    print(f"PNG: {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
