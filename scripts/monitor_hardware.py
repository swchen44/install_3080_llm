#!/usr/bin/env python3
"""Print GPU and CPU utilization, memory, power, and clock speeds periodically.

GPU readings use ``nvidia-smi`` (NVIDIA driver required). CPU and system memory
readings come from Linux's /proc and /sys interfaces.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path


INTERVAL_SECONDS = 10
NVIDIA_QUERY = (
    "index,name,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu,"
    "clocks.current.graphics,clocks.current.memory"
)


def read_cpu_times() -> tuple[int, int]:
    """Return total and idle CPU jiffies across all cores."""
    with open("/proc/stat", encoding="ascii") as stat_file:
        fields = stat_file.readline().split()[1:]
    values = [int(value) for value in fields]
    idle = values[3] + (values[4] if len(values) > 4 else 0)
    return sum(values), idle


def cpu_usage(previous: tuple[int, int], current: tuple[int, int]) -> float:
    total_delta = current[0] - previous[0]
    idle_delta = current[1] - previous[1]
    if total_delta <= 0:
        return 0.0
    return max(0.0, min(100.0, 100.0 * (total_delta - idle_delta) / total_delta))


def memory_usage() -> tuple[int, int, float]:
    values: dict[str, int] = {}
    with open("/proc/meminfo", encoding="ascii") as mem_file:
        for line in mem_file:
            key, raw, *_ = line.replace(":", "").split()
            values[key] = int(raw)  # Linux reports these values in kB.
    total = values["MemTotal"]
    available = values.get("MemAvailable", total - values.get("MemFree", 0))
    used = total - available
    return used, total, 100.0 * used / total if total else 0.0


def cpu_frequency() -> str:
    frequencies: list[float] = []
    for path in Path("/sys/devices/system/cpu").glob("cpu[0-9]*/cpufreq/scaling_cur_freq"):
        try:
            frequencies.append(int(path.read_text().strip()) / 1000.0)
        except (OSError, ValueError):
            continue
    if frequencies:
        return f"{min(frequencies):.0f}-{max(frequencies):.0f} MHz (cores)"

    # Fallback for systems without cpufreq sysfs entries.
    try:
        mhz = [float(line.split(":", 1)[1]) for line in Path("/proc/cpuinfo").read_text().splitlines()
               if line.startswith("cpu MHz")]
    except (OSError, ValueError, IndexError):
        mhz = []
    return f"{min(mhz):.0f}-{max(mhz):.0f} MHz (cores)" if mhz else "unavailable"


def cpu_temperature() -> str:
    readings: list[float] = []
    for path in Path("/sys/class/thermal").glob("thermal_zone*/temp"):
        try:
            value = int(path.read_text().strip())
        except (OSError, ValueError):
            continue
        # Linux thermal zones commonly report millidegrees Celsius; some report
        # whole degrees. Ignore implausible values and unavailable zones.
        celsius = value / 1000.0 if value > 1000 else float(value)
        if 0 < celsius < 150:
            readings.append(celsius)
    if not readings:
        return "unavailable"
    return f"{min(readings):.1f}-{max(readings):.1f} °C (thermal zones)"


def rapl_energy_counters() -> dict[Path, tuple[int, int]]:
    """Read package-level RAPL energy counters and their wraparound limits."""
    counters: dict[Path, tuple[int, int]] = {}
    for energy_path in Path("/sys/class/powercap").glob("*/energy_uj"):
        # Keep package counters only; summing package and child domains would
        # count some CPU energy twice.
        if energy_path.parent.name.count(":") > 1:
            continue
        try:
            energy = int(energy_path.read_text().strip())
            max_path = energy_path.parent / "max_energy_range_uj"
            maximum = int(max_path.read_text().strip())
        except (OSError, ValueError):
            continue
        counters[energy_path] = (energy, maximum)
    return counters


def cpu_power_watts(previous: dict[Path, tuple[int, int]], elapsed: float) -> str:
    current = rapl_energy_counters()
    deltas = []
    for path, (old_energy, old_maximum) in previous.items():
        if path not in current:
            continue
        new_energy, new_maximum = current[path]
        maximum = new_maximum or old_maximum
        delta = new_energy - old_energy
        if delta < 0 and maximum > 0:  # Counter wrapped around.
            delta += maximum
        if delta >= 0:
            deltas.append(delta)
    if not deltas or elapsed <= 0:
        return "unavailable (RAPL not exposed)"
    return f"{sum(deltas) / 1_000_000 / elapsed:.1f} W avg"


def gpu_readings() -> list[str]:
    if not shutil.which("nvidia-smi"):
        return ["GPU: nvidia-smi not found; NVIDIA GPU metrics unavailable"]
    result = subprocess.run(
        ["nvidia-smi", f"--query-gpu={NVIDIA_QUERY}", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    if result.returncode:
        detail = result.stderr.strip() or "unknown nvidia-smi error"
        return [f"GPU: unable to read metrics ({detail})"]

    lines = []
    for row in result.stdout.splitlines():
        columns = [column.strip() for column in row.split(",")]
        if len(columns) != 9:
            lines.append(f"GPU: unrecognized nvidia-smi output: {row}")
            continue
        index, name, utilization, mem_used, mem_total, power, temperature, graphics_clock, memory_clock = columns
        lines.append(
            f"GPU {index} ({name}): load {utilization}% | VRAM {mem_used}/{mem_total} MiB "
            f"| temp {temperature} °C | power {power} W "
            f"| clocks core {graphics_clock} MHz, memory {memory_clock} MHz"
        )
    return lines or ["GPU: no NVIDIA GPUs reported"]


def main() -> None:
    previous_cpu = read_cpu_times()
    print(f"Hardware monitor started; sampling every {INTERVAL_SECONDS} seconds. Ctrl+C to stop.", flush=True)
    while True:
        previous_energy = rapl_energy_counters()
        sample_start = time.monotonic()
        time.sleep(INTERVAL_SECONDS)
        elapsed = time.monotonic() - sample_start
        current_cpu = read_cpu_times()
        cpu_percent = cpu_usage(previous_cpu, current_cpu)
        previous_cpu = current_cpu
        power = cpu_power_watts(previous_energy, elapsed)
        used, total, percent = memory_usage()
        print(f"\n[{datetime.now().astimezone().isoformat(timespec='seconds')}]")
        print(f"CPU: load {cpu_percent:.1f}% | RAM {used / 1024:.0f}/{total / 1024:.0f} MiB ({percent:.1f}%) "
              f"| power {power} | temp {cpu_temperature()} | frequency {cpu_frequency()}")
        for line in gpu_readings():
            print(line)
        print(flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nHardware monitor stopped.")
