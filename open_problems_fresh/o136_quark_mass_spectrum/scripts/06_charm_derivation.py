#!/usr/bin/env python3
"""
O136 — Script 6: Charm 夸克正確 n 值推導
================================================================
從雙重 Lucas 條件推導 charm 的正確 n 值。

已知:
  - 2nd gen 下型夸克 s: n=14 = 2×L₄
  - 2nd gen 上型夸克 c: 候選 n=34 = F₉
  - 模式偏移: s→c 偏移 +20 = B×F₅

要驗證:
  1. n=34 是否滿足雙重條件 (Lucas/Fibonacci n + γ 比匹配)
  2. 偏移 +20 的結構意義
  3. 公式 m_c = M₀ × γ₃₄ × P_f 的閉合
"""
import math, json, sys
from pathlib import Path

phi = (1 + math.sqrt(5))/2
L = [int(round(phi**n + (-1)**n * phi**(-n))) for n in range(15)]
F = [0, 1]
for n in range(2, 12): F.append(F[n-1] + F[n-2])
Nd, B, M = 44, 4, 33
h11, h21, CY3 = 36, 98, 134
M0 = 27.900915
gamma = lambda n: 4 * math.sin(n * math.pi / 88)**2

print("=" * 78)
print("O136 Script 6: Charm 夸克正確 n 值推導")
print("=" * 78)

g1 = gamma(1)

# ─── 1. 檢查 n=34 的雙重條件 ──────────────────────────
print(f"\n─── 1. n=34 (F₉=34) 的雙重條件檢查 ───")

# 條件 1: n 是 Lucas 或 Fibonacci 數？
n = 34
is_lucas = n in L
is_fib = n in F
print(f"n={n}: Lucas? {is_lucas}, Fibonacci? {is_fib} (F₉={F[9]})")

# 條件 2: γ_n/γ₁ 接近結構組合？
ratio = gamma(n) / g1
print(f"γ₃₄/γ₁ = {ratio:.6f}")

# 擴展的結構組合搜尋
candidates = {}

# CY₃ × F + L
for fi, fv in enumerate(F):
    if fv > 0:
        for li, lv in enumerate(L):
            val = CY3 * fv + lv
            if val > 0:
                dev = abs(ratio - val) / val * 100
                candidates[f"CY3×F{fi}+L{li}={val}"] = dev

# CY₃ × F - L
for fi, fv in enumerate(F):
    if fv > 0:
        for li, lv in enumerate(L):
            val = CY3 * fv - lv
            if val > 0:
                dev = abs(ratio - val) / val * 100
                candidates[f"CY3×F{fi}-L{li}={val}"] = dev

# L × F
for fi, fv in enumerate(F):
    if fv > 0:
        for li, lv in enumerate(L):
            val = li * fv
            if val > 0:
                dev = abs(ratio - val) / val * 100
                candidates[f"L{li}×F{fi}={val}"] = dev

# 排序
sorted_candidates = sorted(candidates.items(), key=lambda x: x[1])
print(f"前 5 最佳匹配:")
for name, dev in sorted_candidates[:5]:
    print(f"  {name:>30} → 偏差 {dev:.4f}%")

# ─── 2. 模式偏移: s→c ──────────────────────────────────
print(f"\n─── 2. 模式偏移: s(n=14) → c(n=34) ───")
print(f"偏移: 34 - 14 = {34-14} = B×F₅ = {B}×{F[5]} = {B*F[5]}")
print(f"偏移量 = B×F₅ = {B*F[5]} ✅ 結構數")

# 偏移的結構意義
print(f"   B = {B} = MERA 分支因子")
print(f"   F₅ = {F[5]} = Fibonacci 5")
print(f"   B×F₅ = {B*F[5]} = 20")

# ─── 3. γ 比結構分析 ──────────────────────────────────
print(f"\n─── 3. γ 比結構分析 ───")

# 對每個夸克，找到最佳結構匹配
quarks = {
    "up": (1, 15.5, False),
    "down": (1, 33.0, False),
    "strange": (14, 3.6, False),
    "charm": (34, 13.0, False),
    "bottom": (33, 44.0, False),
    "top": (0, 0, True),
}

# 擴展結構組合
def find_best_match(ratio, max_dev=2.0):
    best = (float('inf'), "")
    # 現有組合
    for li, lv in enumerate(L):
        if lv > 0:
            dev = abs(ratio - lv) / lv * 100
            if dev < best[0]: best = (dev, f"L{li}={lv}")
    # Nd ± L
    for li, lv in enumerate(L):
        for op, name in [("+", Nd+lv), ("-", Nd-lv)]:
            if name > 0:
                dev = abs(ratio - name) / name * 100
                if dev < best[0] and dev < max_dev: best = (dev, f"Nd{op}L{li}={name}")
    # L × (Nd+L)
    for li, lv in enumerate(L):
        for lj, lv2 in enumerate(L):
            for lk, lv3 in enumerate(L):
                val = lv * (Nd + lv3)
                if val > 0:
                    dev = abs(ratio - val) / val * 100
                    if dev < best[0] and dev < max_dev: best = (dev, f"L{li}x(Nd+L{lk})={val}")
    # CY3 × F + L
    for fi, fv in enumerate(F):
        if fv > 0:
            for li, lv in enumerate(L):
                for op, name in [("+", CY3*fv+lv), ("-", CY3*fv-lv)]:
                    if name > 0:
                        dev = abs(ratio - name) / name * 100
                        if dev < best[0] and dev < max_dev: best = (dev, f"CY3×F{fi}{op}L{li}={name}")
    # L × F (新)
    for fi, fv in enumerate(F):
        if fv > 0:
            for li, lv in enumerate(L):
                val = lv * fv
                if val > 0:
                    dev = abs(ratio - val) / val * 100
                    if dev < best[0] and dev < max_dev: best = (dev, f"L{li}×F{fi}={val}")
    return best

print(f"{'夸克':>8} {'n':>3} {'γ_n/γ₁':>12} {'最佳匹配':>30} {'偏差%':>10}")
print("-" * 65)
for q_name, (n, pf, is_higgs) in quarks.items():
    if is_higgs:
        print(f"{q_name:>8} {'H':>3} {'—':>12} {'Higgs VEV':>30} {'—':>10}")
        continue
    ratio = gamma(n) / g1
    dev, label = find_best_match(ratio)
    print(f"{q_name:>8} {n:>3} {ratio:>12.6f} {label:>30} {dev:>9.4f}%")

# ─── 4. Charm 完整公式 ─────────────────────────────────
print(f"\n─── 4. Charm 完整公式驗證 ───")

n_c = 34
P_f_c = F[7]  # F₇ = 13
m_c_pred = M0 * gamma(n_c) * P_f_c
m_c_obs = 1270.0  # MeV
dev_c = (m_c_pred - m_c_obs) / m_c_obs * 100

print(f"m_c = M₀ × γ₃₄ × F₇")
print(f"    = {M0} × {gamma(n_c):.6f} × {P_f_c}")
print(f"    = {m_c_pred:.4f} MeV")
print(f"PDG charm = {m_c_obs} MeV")
print(f"偏差 = {dev_c:.4f}%")

# γ 比結構
ratio_c = gamma(n_c) / g1
print(f"\nγ₃₄/γ₁ = {ratio_c:.6f}")
print(f"結構: CY₃ × F₅ + L₆ = {CY3}×{F[5]} + {L[6]} = {CY3*F[5]} + {L[6]} = {CY3*F[5]+L[6]}")
print(f"偏差 = {abs(ratio_c - (CY3*F[5]+L[6]))/(CY3*F[5]+L[6])*100:.4f}%")

# ─── 5. 所有夸克 γ 比結構 ─────────────────────────────
print(f"\n─── 5. 所有夸克 γ 比結構總結 ───")

print(f"\n{'夸克':>8} {'n':>3} {'γ_n/γ₁':>12} {'結構公式':>40} {'偏差%':>10}")
print("-" * 75)
for q_name, (n, pf, is_higgs) in quarks.items():
    if is_higgs: continue
    ratio = gamma(n) / g1
    dev, label = find_best_match(ratio)
    print(f"{q_name:>8} {n:>3} {ratio:>12.6f} {label:>40} {dev:>9.4f}%")

# 模式總結
print(f"\n─── 模式總結 ───")
print(f"""輕子 (n, γ比結構):
  e⁻: n=1,  γ比 = L₁ = 1
  μ⁻: n=7,  γ比 = Nd + L₃ = 48
  τ⁻: n=20, γ比 = L₄ × (Nd + L₃) = 336

夸克 (n, γ比結構, 色荷修正):
  u:  n=1,  γ比 = L₁ = 1
  d:  n=1,  γ比 = L₁ = 1
  s:  n=14, γ比 = L₃ × (Nd + L₁) = 180
  c:  n=34, γ比 = CY₃ × F₅ + L₆ = 688
  b:  n=33, γ比 = L₃ × (Nd + L₁₀) = 668

模式:
  1st gen: 所有粒子 n=1, 由 P_f 區分
  2nd gen: 輕子 n=7, s n=14, c n=34
  3rd gen: 輕子 n=20, b n=33, t Higgs VEV

  偏移: s→c = +20 = B×F₅
  偏移: 7→14 = +7 = L₄
  偏移: 20→33 = +13 = F₇
""")

# 保存
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "06_charm_derivation.json", "w") as f:
    json.dump({
        "charm": {"n": n_c, "P_f": float(P_f_c), "m_pred": float(m_c_pred), "dev_pct": float(dev_c)},
        "gamma_ratio_structure": "CY3×F5+L6=688",
        "mode_shift": "s(14)→c(34): +20=B×F5",
    }, f, indent=2)
print("✅ 結果已寫入 data/06_charm_derivation.json")