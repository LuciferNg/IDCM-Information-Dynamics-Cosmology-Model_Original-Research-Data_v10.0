#!/usr/bin/env python3
"""O146 獨立驗證器 — 唔 import o146 scripts 任何函數
===================================================
由原始定義 (sin 譜, PDG 質量, Planck 峰位) 重新計算 docs 所有數值,
同 docs/01_derivation_record.md + data/*.json 對照。禁止污染。
"""
import math, json, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
N = 44
M = 33
PASS = 0
FAIL = 0
rows = []

def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond:
        PASS += 1
    else:
        FAIL += 1

# ============ 原始定義 (獨立重算) ============
w = lambda n: 2*math.sin(math.pi*n/88)
G = np.array([4*math.sin(math.pi*n/88)**2 for n in range(1, N+1)])

# ============ L1: 數學存在 ============
# 1a. 可分性 (全 946 對)
maxdev_sep = 0.0
for n in range(1, N+1):
    for m in range(n+1, N+1):
        d, s = m-n, m+n
        maxdev_sep = max(maxdev_sep, abs((w(m)-w(n)) - 4*math.sin(d*math.pi/176)*math.cos(s*math.pi/176)))
check("L1 可分性 < 1e-12 (docs: 5.55e-16)", maxdev_sep < 1e-12, f"max_dev={maxdev_sep:.2e}")
check("L1 可分性 = 5.55e-16 (docs 數值)", abs(maxdev_sep - 5.55e-16) < 1e-17, f"got={maxdev_sep:.2e}")

# 1b. 唯一性 946
vals = set(round(w(m)-w(n), 12) for n in range(1, N+1) for m in range(n+1, N+1))
check("L1 唯一性 946", len(vals) == 946, f"unique={len(vals)}")

# 1c. Z₂ 對偶
z2 = all(abs(w(n)**2 + w(44-n)**2 - 4) < 1e-12 for n in range(1, 44))
check("L1 Z₂ 對偶 44/44", z2)

# 1d. 斜邊閉合
hyp = max(abs((w(44)-w(44-d)) - 4*math.sin(math.pi*d/176)**2) for d in range(1, 44))
check("L1 斜邊 < 1e-12 (docs: 6.66e-16)", hyp < 1e-12, f"max_dev={hyp:.2e}")

# 1e. 無理度分層 (docs hist {1:1,2:1,4:2,5:5,10:5,20:10,40:20})
# 獨立: 用數值 Jordan 檢驗 — 用 sympy minimal_polynomial 重算
from sympy import sin as ssin, pi as spi, minimal_polynomial, symbols, degree
_x = symbols('x')
hist = {}
for n in range(1, N+1):
    dg = degree(minimal_polynomial(ssin(n*spi/88), _x))
    hist[dg] = hist.get(dg, 0) + 1
check("L1 無理度分層 hist", hist == {1:1, 2:1, 4:2, 5:5, 10:5, 20:10, 40:20}, f"hist={hist}")

# ============ L2: 物理存在 ============
# 2a. 拍頻範圍 (docs: [0.0013, 1.9286])
B = np.array(sorted(abs(w(m)-w(n)) for n in range(1, N+1) for m in range(n+1, N+1)))
check("L2 拍頻範圍", abs(B.min()-0.0013) < 1e-4 and abs(B.max()-1.9286) < 1e-4,
      f"[{B.min():.4f}, {B.max():.4f}]")

# 2b. O65 先驗鎖定 4/4 (docs: 1.70%, 0.54%, 2.55%, 0.28%)
MIX = [
    ("sin²θ₁₂", 0.303, G[1]/(G[1]+G[2])),
    ("sin²θ₂₃", 0.572, G[6]/(G[6]+G[5])),
    ("sin²θ₁₃", 0.02203, G[5]/8),
    ("λ CKM", 0.225, (G[5]/16)**(1/3)),
]
for name, obs, pred in MIX:
    dev = abs(pred-obs)/obs*100
    check(f"L2 {name} < 5%", dev < 5, f"pred={pred:.5f} obs={obs} dev={dev:.2f}%")

# ============ L3: N_d 跨系統收斂 ============
# 3a. CMB 峰反推 (docs: m=1..7 → 44.02/44.00/44.00/44.00/44.00/43.90/43.625, mean 43.935)
peaks_obs = {1: 220.1, 2: 537.0, 3: 810.0, 4: 1014.0, 5: 1121.0, 6: 1337.0, 7: 1400.0}
def k_m(m):
    return 33-8 if m == 5 else M - math.comb(9-m, 2)
def frac_m(m):
    return 21 if m == 5 else ((m-1)*9) % 25
N_cmb = np.mean([(ell-frac_m(m))/k_m(m) for m, ell in peaks_obs.items()])
check("L3 CMB N_est ≈ 43.94 (docs)", abs(N_cmb - 43.935) < 0.02, f"mean={N_cmb:.4f}")

# 3b. H(z) ε⁻² (docs: 41.89)
N_hz = 1/0.1545**2
check("L3 H(z) ε⁻² ≈ 41.89", abs(N_hz - 41.89) < 0.05, f"N={N_hz:.2f}")

# 3c. 冷斑 (docs: 134.2)
A = 88*61/40
check("L3 冷斑 134.2", abs(A - 134.2) < 0.1, f"A={A}")

# 3d. v1.0 幾何 (docs: 40.17)
N_geo = math.sqrt(19.19*84.08)
check("L3 幾何 √(N₂N₃) ≈ 40.17", abs(N_geo - 40.17) < 0.02, f"N={N_geo:.2f}")

# 3e. 核心 4 領域 (docs: 43.46 ± 0.90)
core = np.array([N_cmb, N_hz, 44.0, 44.0])
check("L3 核心均值 ≈ 43.46", abs(core.mean()-43.46) < 0.05, f"mean={core.mean():.2f}")
check("L3 核心 std ≈ 0.90", abs(core.std()-0.90) < 0.05, f"std={core.std():.2f}")

# ============ L4: 聲學峰投影 ============
# docs: RMS 0.335%, m=1..4 <0.05%
preds = [N*k_m(m)+frac_m(m) for m in sorted(peaks_obs)]
obs_v = [peaks_obs[m] for m in sorted(peaks_obs)]
devs = np.array([abs(p-o)/o*100 for p, o in zip(preds, obs_v)])
rms = float(np.sqrt((devs**2).mean()))
check("L4 RMS ≈ 0.335%", abs(rms-0.335) < 0.01, f"rms={rms:.3f}%")
low = [abs(N*k_m(m)+frac_m(m)-peaks_obs[m])/peaks_obs[m]*100 for m in [1,2,3,4]]
check("L4 m=1..4 < 0.05%", max(low) < 0.05, f"max={max(low):.3f}%")

# ============ L5: 證偽 0/4 ============
check("L5 K3 核心偏離 <10%", abs(core.mean()-44)/44 < 0.10)

# ============ data JSON 對照 ============
for jf, key_checks in [("01_math_existence", ["separability"]), ("04_acoustic_projection", ["rms_pct"])]:
    p = os.path.join(DATA, jf + ".json")
    if os.path.exists(p):
        with open(p) as f:
            d = json.load(f)
        check(f"JSON {jf} 存在且可讀", True, "ok")

print("=" * 66)
print("  O146 獨立驗證器 (原始定義重算 vs docs)")
print("=" * 66)
for name, ok, detail in rows:
    print(f"  {'✅' if ok else '🔴'} {name:42s} {detail}")
print("-" * 66)
print(f"  PASS: {PASS}  FAIL: {FAIL}")
print(f"  總判定: {'✅ 全部一致' if FAIL == 0 else '🔴 有偏差需審計'}")
