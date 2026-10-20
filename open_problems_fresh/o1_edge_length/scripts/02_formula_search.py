#!/usr/bin/env python3
"""
02_formula_search.py — 26.091346° 精確公式搜索
================================================
候選: φ 冪, atan/asin/acos 組合, π 分數, √ 組合
目標: 偏差 < 0.001° (arcsec 級)
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
target = 26.091346
print("=" * 66)
print(f"新O1: 26.091346° 公式搜索")
print("=" * 66)

# 基本候選
cands = {
    "atan(1/2)": math.degrees(math.atan(0.5)),
    "2*atan(1/2)": 2*math.degrees(math.atan(0.5)),
    "atan(2)": math.degrees(math.atan(2)),
    "atan(1/φ)": math.degrees(math.atan(1/phi)),
    "2*atan(1/φ)": 2*math.degrees(math.atan(1/phi)),
    "atan(1/φ²)": math.degrees(math.atan(1/phi**2)),
    "2*atan(1/φ²)": 2*math.degrees(math.atan(1/phi**2)),
    "atan(φ/2)": math.degrees(math.atan(phi/2)),
    "2*atan(φ/2)": 2*math.degrees(math.atan(phi/2)),
    "atan(φ²/2)": math.degrees(math.atan(phi**2/2)),
    "atan(1/√2)": math.degrees(math.atan(1/math.sqrt(2))),
    "asin(1/φ)": math.degrees(math.asin(1/phi)),
    "asin(1/φ²)": math.degrees(math.asin(1/phi**2)),
    "2*asin(1/φ²)": 2*math.degrees(math.asin(1/phi**2)),
    "asin(1/√5)": math.degrees(math.asin(1/math.sqrt(5))),
    "2*asin(1/√5)": 2*math.degrees(math.asin(1/math.sqrt(5))),
    "asin(1/(2φ))": math.degrees(math.asin(1/(2*phi))),
    "2*asin(1/(2φ))": 2*math.degrees(math.asin(1/(2*phi))),
    "acos(φ/2)": math.degrees(math.acos(phi/2)),
    "2*acos(φ/2)": 2*math.degrees(math.acos(phi/2)),
    "acos(1/√5)": math.degrees(math.acos(1/math.sqrt(5))),
    "acos(1/(2φ))": math.degrees(math.acos(1/(2*phi))),
    "π/7": 180/7,
    "2π/13.8": 360/13.8,
    "360/13.8": 360/13.8,
    "44*φ⁻² rad": math.degrees(44/phi**2),
    "44*φ⁻³ rad": math.degrees(44/phi**3),
    "90*φ⁻³": 90*phi**-3,
    "90*φ⁻⁴": 90*phi**-4,
    "180*φ⁻⁴": 180*phi**-4,
    "360*φ⁻⁵": 360*phi**-5,
    "360*φ⁻⁶": 360*phi**-6,
    "45*φ⁻¹": 45*phi**-1,
    "45*φ⁻²": 45*phi**-2,
    "ε rad": math.degrees(1/(4*phi)),
    "2ε rad": math.degrees(2/(4*phi)),
    "3ε rad": math.degrees(3/(4*phi)),
    "κ rad": math.degrees(1/16),
    "2κ rad": math.degrees(2/16),
    "atan(φ-1)": math.degrees(math.atan(phi-1)),
    "atan(1/φ³)": math.degrees(math.atan(1/phi**3)),
    "atan(φ⁻¹/2)": math.degrees(math.atan(1/(2*phi))),
    "asin(φ⁻¹/2)": math.degrees(math.asin(1/(2*phi))),
}

print(f"\n=== 單一候選 (偏差 < 0.5°) ===")
best = []
for name, val in cands.items():
    diff = abs(val - target)
    if diff < 0.5:
        mark = "✅" if diff < 0.01 else ("🟡" if diff < 0.1 else "")
        print(f"  {mark} {name:20s} = {val:10.6f}°  偏差 {diff:8.4f}°")
    best.append((diff, name, val))

# 特別搜索: asin/atan 分數型
print(f"\n=== 分數型搜索 (p/q 有理數) ===")
for q in range(2, 20):
    for p in range(1, q):
        v1 = math.degrees(math.asin(p/q))
        v2 = math.degrees(math.atan(p/q))
        for name, v in [("asin", v1), ("atan", v2)]:
            for mult, mname in [(1, ""), (2, "2*"), (0.5, "(1/2)*")]:
                diff = abs(mult*v - target)
                if diff < 0.001:
                    print(f"  ✅ {mname}{name}({p}/{q}) = {mult*v:.6f}° 偏差 {diff:.6f}°")

# 特別: 26.091346 嘅 tan/arcsin
print(f"\n=== 逆函數 (26.091346° → 值) ===")
t = math.tan(math.radians(target))
print(f"  tan(26.091°) = {t:.10f}")
print(f"  1/tan = {1/t:.10f}")
print(f"  sin(26.091°) = {math.sin(math.radians(target)):.10f}")
print(f"  cos(26.091°) = {math.cos(math.radians(target)):.10f}")
print(f"  1/cos = {1/math.cos(math.radians(target)):.10f}")
print(f"  φ⁻¹ = {1/phi:.10f}")
print(f"  φ⁻² = {1/phi**2:.10f}")
print(f"  φ⁻³ = {1/phi**3:.10f}")
print(f"  (φ⁻¹)/2 = {1/(2*phi):.10f}")
print(f"  (φ⁻²)/2 = {1/(2*phi**2):.10f}")
print(f"  √(φ-1)/2 = {math.sqrt(phi-1)/2:.10f}")

# 分數×π
print(f"\n=== 分數×π ===")
for num in range(1, 30):
    for den in range(1, 30):
        val = 180*num/den
        diff = abs(val - target)
        if diff < 0.01:
            print(f"  {num}π/{den} = {val:.4f}° 偏差 {diff:.4f}°")
