# Benchmark report (TASK-06)

Recorded 2026-09-28T21:33:51.694765+00:00. Command: `C:\Users\junio\Downloads\mango-vision\ALBUS26_major_revision\.worktrees\execution\src\benchmarks\run.py --config configs/benchmark.json --out artifacts/metrics/benchmark_raw.csv --report reports/benchmark_report.md`.

## Protocol

- batch: 1
- precision: fp32
- m1_imgsz: 640
- m2_imgsz: 224
- warmups_per_image: 10
- iterations_per_image: 100
- torch_threads: 1
- torch_interop_threads: 1
- opencv_threads: 1
- processes: 1
- device: cpu
- pool_size: 32
- class_names: ['Enfermo', 'Saludable']
- manifest: data/manifests/model1_clean_manifest.csv
- m2_conf: 0.4
- raspberry_pi_4: BLOCKED_BY_HARDWARE
- m1_conf: 0.35
- summary definitions: benchmark-summary-v1: mean = arithmetic mean; median = middle value, or mean of the two middle values; std = population standard deviation (ddof=0, statistics.pstdev); p95 = linear interpolation between order statistics at 0-based rank (n-1)*0.95 (Hyndman-Fan type 7, NumPy default "linear"); min, max and n over the successful measured repetitions

## Boundaries

TASK-06: verifiable latency of the M1 -> crops -> M2 cascade (SPEC section 8).

Wall boundaries, each timed with its own clock reads (perf_counter_ns), never derived by
summing other walls: read (file bytes), decode, m1 (full M1 call), m2_crops (crops + M2
calls), annotate, encode (JPEG in memory); cascade = m1 + m2_crops without decode;
end_to_end = file read -> annotated JPEG encoded, models already resident. Weight loading and
the first call after it (cold start) are recorded apart. Ultralytics .speed is recorded as
internal time in ms and never added to any wall. Network, SQLite and frontend are not measured.

## Hardware and runtime

- cpu_name: AMD Ryzen 5 7520U with Radeon Graphics
- machine: AMD64
- physical_cores: 4
- logical_cores: 8
- ram_bytes: 16407719936
- os: Windows-11-10.0.26200-SP0
- python: 3.12.14 (main, Aug 25 2026, 14:01:42) [MSC v.1944 64 bit (AMD64)]
- executable: C:\Users\junio\Downloads\mango-vision\ALBUS26_major_revision\.worktrees\execution\.venv\Scripts\python.exe
- torch: 2.12.0+cpu
- ultralytics: 8.4.52
- opencv: 5.0.0
- numpy: 2.4.4
- torch_threads: 1
- torch_interop_threads: 1
- opencv_threads: 1
- cuda_available: False
- device: cpu
- thread_env: {'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': None, 'OPENBLAS_NUM_THREADS': None, 'CUDA_VISIBLE_DEVICES': None}

## Pool

32 validation images, file `artifacts/metrics/benchmark_raw_pool.csv` (sha256 ae41f90e39968aeea2b17e5c6dd4855d892169029013fc4c420bc11ecd8432a0), saved before any timing. With Enfermo: 3; without: 29.

## Cold start (recorded apart, not in any distribution)

- load_m1_ns: 501.973 ms
- load_m2_ns: 81.079 ms
- first_call_after_load_end_to_end_ns: 1375.951 ms

## Distribution over all images and repetitions

Measured repetitions: 3200; failed: 0; warm-up failures: 0. No run is dropped for being slow.

### Wall time (ms)

| stage | n | mean | median | std | p95 | min | max |
|---|---|---|---|---|---|---|---|
| read | 3200 | 0.642 | 0.599 | 0.571 | 0.835 | 0.356 | 24.495 |
| decode | 3200 | 2.790 | 2.700 | 0.789 | 3.616 | 1.571 | 25.640 |
| m1 | 3200 | 292.508 | 203.836 | 378.170 | 681.758 | 124.104 | 6144.309 |
| m2_crops | 3200 | 45.285 | 28.437 | 146.108 | 90.090 | 0.009 | 4092.564 |
| annotate | 3200 | 0.129 | 0.132 | 0.076 | 0.212 | 0.001 | 1.372 |
| encode | 3200 | 2.031 | 1.997 | 0.436 | 2.657 | 1.122 | 9.658 |
| cascade | 3200 | 337.799 | 233.881 | 459.667 | 772.002 | 124.125 | 8598.460 |
| end_to_end | 3200 | 343.424 | 239.409 | 459.854 | 777.739 | 129.447 | 8604.973 |

### Ultralytics internal .speed (ms; internal, never added to wall)

| stage | n | mean | median | std | p95 | min | max |
|---|---|---|---|---|---|---|---|
| m1.preprocess | 3200 | 5.795 | 5.053 | 4.242 | 9.065 | 3.417 | 124.565 |
| m1.inference | 3200 | 285.616 | 197.698 | 376.651 | 674.919 | 118.158 | 6136.775 |
| m1.postprocess | 3200 | 0.527 | 0.475 | 0.307 | 0.840 | 0.216 | 11.068 |
| m2.preprocess | 3200 | 4.295 | 3.004 | 13.521 | 8.816 | 0.000 | 582.026 |
| m2.inference | 3200 | 40.055 | 24.313 | 138.463 | 80.715 | 0.000 | 3981.063 |
| m2.postprocess | 3200 | 0.256 | 0.275 | 0.141 | 0.412 | 0.000 | 3.770 |

## Per image (wall ms)

| run | image_id | Enfermo | fruits | M2 calls | failed | cascade median | cascade p95 | end_to_end median | end_to_end p95 | end_to_end max |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | SRC-009826 | False | 1 | 1 | 0 | 259.777 | 1326.472 | 265.381 | 1335.607 | 4583.824 |
| 2 | SRC-010765 | False | 0 | 0 | 0 | 175.101 | 399.056 | 180.829 | 403.667 | 772.843 |
| 3 | SRC-009700 | True | 1 | 1 | 0 | 213.640 | 734.915 | 219.483 | 740.344 | 7089.345 |
| 4 | SRC-009815 | False | 1 | 1 | 0 | 192.775 | 688.066 | 198.482 | 692.629 | 2679.097 |
| 5 | SRC-009696 | False | 1 | 1 | 0 | 183.742 | 561.903 | 188.793 | 566.853 | 783.815 |
| 6 | SRC-009864 | False | 1 | 1 | 0 | 219.856 | 530.373 | 225.349 | 537.333 | 2420.585 |
| 7 | SRC-009868 | False | 1 | 1 | 0 | 193.859 | 474.994 | 199.134 | 480.379 | 823.359 |
| 8 | SRC-009795 | False | 1 | 1 | 0 | 200.479 | 495.457 | 206.353 | 501.550 | 1399.752 |
| 9 | SRC-010761 | False | 0 | 0 | 0 | 187.830 | 457.896 | 193.381 | 463.399 | 821.331 |
| 10 | SRC-009837 | False | 1 | 1 | 0 | 229.413 | 1145.742 | 234.617 | 1150.287 | 1708.178 |
| 11 | SRC-009877 | False | 1 | 1 | 0 | 230.386 | 578.151 | 235.834 | 582.790 | 1175.054 |
| 12 | SRC-009841 | False | 1 | 1 | 0 | 280.928 | 645.559 | 286.265 | 650.781 | 2232.812 |
| 13 | SRC-009784 | False | 1 | 1 | 0 | 223.470 | 498.544 | 228.936 | 504.744 | 2084.677 |
| 14 | SRC-009895 | False | 1 | 1 | 0 | 299.754 | 851.290 | 304.942 | 856.588 | 2313.869 |
| 15 | SRC-009779 | False | 1 | 1 | 0 | 282.600 | 1112.585 | 287.892 | 1117.120 | 3636.738 |
| 16 | SRC-009840 | False | 1 | 1 | 0 | 258.835 | 659.488 | 264.434 | 664.800 | 1377.281 |
| 17 | SRC-009767 | False | 0 | 0 | 0 | 230.869 | 1203.434 | 237.299 | 1209.614 | 2826.451 |
| 18 | SRC-009689 | False | 1 | 1 | 0 | 270.523 | 990.442 | 276.472 | 996.058 | 1718.686 |
| 19 | SRC-009785 | False | 1 | 1 | 0 | 187.627 | 329.737 | 192.739 | 335.335 | 545.699 |
| 20 | SRC-009773 | False | 2 | 2 | 0 | 222.175 | 387.836 | 228.652 | 394.983 | 2058.108 |
| 21 | SRC-010766 | False | 1 | 1 | 0 | 199.251 | 506.463 | 204.749 | 512.120 | 799.841 |
| 22 | SRC-009870 | False | 1 | 1 | 0 | 203.645 | 890.162 | 208.940 | 895.567 | 3274.665 |
| 23 | SRC-010800 | False | 2 | 2 | 0 | 414.712 | 3650.689 | 421.034 | 3657.330 | 6881.011 |
| 24 | SRC-009790 | False | 1 | 1 | 0 | 363.424 | 2848.786 | 369.400 | 2853.853 | 8604.973 |
| 25 | SRC-009917 | True | 1 | 1 | 0 | 257.983 | 379.804 | 264.902 | 387.122 | 899.657 |
| 26 | SRC-009862 | False | 1 | 1 | 0 | 256.176 | 466.588 | 262.495 | 502.711 | 982.506 |
| 27 | SRC-009852 | False | 1 | 1 | 0 | 306.080 | 1090.764 | 311.660 | 1096.347 | 2684.615 |
| 28 | SRC-009909 | False | 1 | 1 | 0 | 222.637 | 1125.325 | 228.133 | 1131.487 | 3723.740 |
| 29 | SRC-009754 | True | 0 | 0 | 0 | 172.523 | 225.669 | 178.108 | 231.479 | 559.587 |
| 30 | SRC-009856 | False | 1 | 1 | 0 | 263.411 | 661.645 | 268.416 | 666.440 | 2531.848 |
| 31 | SRC-010787 | False | 1 | 1 | 0 | 217.466 | 526.507 | 222.617 | 531.751 | 1590.168 |
| 32 | SRC-009831 | False | 1 | 1 | 0 | 207.417 | 376.201 | 212.355 | 382.215 | 1444.630 |

## Raspberry Pi 4: BLOCKED_BY_HARDWARE

No physical device or measurement environment was available as evidence, so no Pi row exists and the CPU numbers above do not stand in for it. Protocol to run when real access is given: the same command, config and pool on the device, with its hardware, OS and runtime recorded; batch 1, FP32, M1 640 / M2 224, 10 warm-ups and 100 measured repetitions per image, one process, threads 1.

## Not measured

Network, SQLite and frontend are outside every boundary.
