"""
IDCM v10.0 — PMNS 946 拍頻比值全面搜尋 (修正版)
================================================
修正: beat function 同 loop variable 嘅 indexing bug
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2
N_d = 44

# 44 個 K_Chain mode 嘅 ω_n (1-indexed)
ω = np.array([2 * abs(math.sin(math.pi * n / 88)) for n in range(1, N_d + 1)])

def beat(i, j):
    """1-indexed: beat between mode i and mode j"""
    return abs(ω[i-1] - ω[j-1])

print("=" * 80)
print("IDCM v10.0 — PMNS 946 拍頻比值搜尋 (修正版) 🎯")
print("=" * 80)

# PMNS 目標
pmns_targets = {
    "tan(θ₁₂=33.41°)": math.tan(math.radians(33.41)),
    "sin(θ₁₂=33.41°)": math.sin(math.radians(33.41)),
    "tan(θ₂₃=42.2°)": math.tan(math.radians(42.2)),
    "tan(θ₂₃=49.0°)": math.tan(math.radians(49.0)),
    "sin(θ₂₃=42.2°)": math.sin(math.radians(42.2)),
    "sin(θ₂₃=49.0°)": math.sin(math.radians(49.0)),
    "tan(θ₁₃=8.54°)": math.tan(math.radians(8.54)),
    "sin(θ₁₃=8.54°)": math.sin(math.radians(8.54)),
}

# ══════════════════════════════════════════════════════════════
# 1. beat/beat 搜尋 (直接用 ω[i] 避免 off-by-one)
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("1. beat/beat 搜尋 (修正版)")
print("─" * 80)

print(f"  {'目標':>20} | {'beat(i,j)':>20} | {'beat(k,l)':>20} | {'ratio':>15} | {'誤差':>12}")
print("-" * 90)

for name, target in pmns_targets.items():
    best_err = float('inf')
    best = None
    for i in range(1, 45):  # 1-indexed loop
        for j in range(i+1, 45):
            bij = abs(ω[i-1] - ω[j-1])
            if bij < 1e-12: continue
            for k in range(1, 45):
                for l in range(k+1, 45):
                    bkl = abs(ω[k-1] - ω[l-1])
                    if bkl < 1e-12: continue
                    ratio = bij / bkl
                    err = abs(ratio - target)
                    if err < best_err:
                        best_err = err
                        best = (i, j, k, l, ratio, bij, bkl)
    
    if best:
        i, j, k, l, ratio, bij, bkl = best
        print(f"  {name:>20} | ({i:2d},{j:2d})={bij:>10.6f} | ({k:2d},{l:2d})={bkl:>10.6f} | {ratio:>15.10f} | {best_err:>12.2e}")

# ══════════════════════════════════════════════════════════════
# 2. beat/ω₆ 搜尋 (p6 模式投影)
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("2. beat/ω₆ 搜尋 (p6 模式投影)")
print("─" * 80)

ω6 = ω[5]  # n=6, 0-indexed = 5
print(f"  ω₆ = {ω6:.10f}\n")

print(f"  {'目標':>20} | {'beat(i,j)':>20} | {'beat/ω₆':>15} | {'誤差':>12} | {'Z₃':>8} | {'Z₅':>8}")
print("-" * 90)

for name, target in pmns_targets.items():
    best_err = float('inf')
    best = None
    for i in range(1, 45):
        for j in range(i+1, 45):
            b = abs(ω[i-1] - ω[j-1])
            if b < 1e-12: continue
            ratio = b / ω6
            err = abs(ratio - target)
            if err < best_err:
                best_err = err
                best = (i, j, ratio, b)
    
    if best:
        i, j, ratio, b = best
        z3_i, z5_i = i % 3, i % 5
        z3_j, z5_j = j % 3, j % 5
        print(f"  {name:>20} | ({i:2d},{j:2d})={b:>10.6f} | {ratio:>15.10f} | {best_err:>12.2e} | ({z3_i},{z3_j}) | ({z5_i},{z5_j})")

# ══════════════════════════════════════════════════════════════
# 3. 結果總結
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. 結果總結")
print("─" * 80)

# CKM 結果 (已知正確)
print(f"\n  CKM beat 公式 (已確認 ✅):")
ckm = [
    ("tan(θ₁₂=13.04°)", beat(5,6)/beat(19,25)),
    ("tan(θ₂₃=2.38°)", beat(33,35)/beat(3,22)),
    ("sin(θ₁₃=0.201°)", beat(42,43)/beat(10,31)),
    ("V_us=0.225", beat(25,35)/beat(6,37)),
    ("V_cb=0.04182", beat(13,14)/beat(6,37)),
    ("V_ub=0.00369", beat(41,42)/beat(3,37)),
    ("A=0.830", beat(16,35)/beat(10,28)),
]
for name, val in ckm:
    print(f"    {name:>25}: {val:.10f}")

# PMNS 結果 (修正版)
print(f"\n  PMNS beat 公式 (修正版):")
for name, target in pmns_targets.items():
    best_err = float('inf')
    best = None
    for i in range(1, 45):
        for j in range(i+1, 45):
            bij = abs(ω[i-1] - ω[j-1])
            if bij < 1e-12: continue
            for k in range(1, 45):
                for l in range(k+1, 45):
                    bkl = abs(ω[k-1] - ω[l-1])
                    if bkl < 1e-12: continue
                    ratio = bij / bkl
                    err = abs(ratio - target)
                    if err < best_err:
                        best_err = err
                        best = (i, j, k, l, ratio, bij, bkl)
    if best and best_err < 1e-5:
        i, j, k, l, ratio, bij, bkl = best
        print(f"    {name:>25}: beat({i},{j})/beat({k},{l}) = {ratio:.10f} (err={best_err:.2e}) ✅")

# ══════════════════════════════════════════════════════════════
# 4. 儲存結果
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. 儲存結果")
print("─" * 80)

lines = []
lines.append("IDCM v10.0 — PMNS 946 拍頻比值搜尋 (修正版)")
lines.append("=" * 60)
lines.append("")
lines.append("CKM Beat 公式 (已確認):")
for name, val in ckm:
    lines.append(f"  {name}: {val:.10f}")
lines.append("")
lines.append("PMNS Beat 公式 (修正版):")
for name, target in pmns_targets.items():
    best_err = float('inf')
    best = None
    for i in range(1, 45):
        for j in range(i+1, 45):
            bij = abs(ω[i-1] - ω[j-1])
            if bij < 1e-12: continue
            for k in range(1, 45):
                for l in range(k+1, 45):
                    bkl = abs(ω[k-1] - ω[l-1])
                    if bkl < 1e-12: continue
                    ratio = bij / bkl
                    err = abs(ratio - target)
                    if err < best_err:
                        best_err = err
                        best = (i, j, k, l, ratio)
    if best and best_err < 1e-5:
        i, j, k, l, ratio = best
        lines.append(f"  {name}: beat({i},{j})/beat({k},{l}) = {ratio:.10f} (err={best_err:.2e})")

with open("open_problems_fresh/ckm_reconstruction/pmns_beat_search_corrected.txt", "w") as f:
    f.write("\n".join(lines))

print("已儲存結果 ✅")