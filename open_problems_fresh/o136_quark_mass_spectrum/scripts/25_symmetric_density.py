#!/usr/bin/env python3
"""
O136 — Script 25: 對稱檢驗 — O136 P_f 框架的密度測試
================================================================
公平原則: 唔可以只證偽 O34/O35 而唔測自己。
用同一方法測試 O136/O54 的 γ比×P_f 框架。

γ_n = 4sin²(nπ/88)  →  γ比 = (sin比)²  → 密度不同
P_f 字典: {3.6, 15.5, 37, 15.5, 33, 3.6, 13, 44, ...}
"""
import math, json, random
from pathlib import Path

Nd, B_, dimC = 44, 4, 3
def sinm(n): return math.sin(n*math.pi/88)
def gam(n): return 4*sinm(n)**2

print("=" * 92)
print("O136 Script 25: 對稱密度檢驗 — O136 P_f 框架")
print("=" * 92)

# ═══ 1. γ 比空間密度 ════════════════════════════════
print(f"\n{'─'*92}")
print("1. γ 比空間: γ_n/γ_m = (sin n/sin m)²")
print(f"{'─'*92}")

gratios = sorted(gam(n)/gam(m) for n in range(1,45) for m in range(1,45) if n != m)
print(f"\nγ 比值數: {len(gratios)}")
print(f"範圍: [{gratios[0]:.6f}, {gratios[-1]:.2f}]")

import bisect
def best_dev_g(t):
    i = bisect.bisect_left(gratios, t)
    cands = []
    for j in range(max(0,i-3), min(len(gratios), i+4)):
        cands.append(abs(gratios[j]/t - 1))
    return min(cands)*100

random.seed(777)
N = 20000
null_g = []
for _ in range(N):
    t = math.exp(random.uniform(math.log(0.0013), math.log(800)))
    null_g.append(best_dev_g(t))
null_g.sort()

print(f"\n隨機目標的最佳 γ 匹配偏差:")
for q in [1,5,10,25,50,75,90,95]:
    print(f"  {q:>3}% 分位: {null_g[int(N*q/100)]:.4f}%")
print(f"  平均: {sum(null_g)/N:.4f}%")

# ═══ 2. O136 P_f 框架的觀測 ═════════════════════════
print(f"\n{'─'*92}")
print("2. O136 P_f 框架的觀測偏差")
print(f"{'─'*92}")

# O136 公式 (從 docs/06)
o136_claims = [
    ("m_b/m_c", 3.291339, (gam(33)*44)/(gam(34)*13), "γ₃₃×44/(γ₃₄×13)"),
    ("m_μ/m_e", 206.768311, (gam(7)*15.5)/(gam(1)*3.6), "γ₇×15.5/(γ₁×3.6)"),
    ("m_c/m_s", 13.597430, (gam(34)*13)/(gam(14)*3.6), "γ₃₄×13/(γ₁₄×3.6)"),
    ("m_τ/m_μ", 16.817031, (gam(20)*37)/(gam(7)*15.5), "γ₂₀×37/(γ₇×15.5)"),
    ("m_d/m_u", 2.162037, (gam(1)*33)/(gam(1)*15.5), "γ₁×33/(γ₁×15.5)"),
    ("m_s/m_d", 20.000000, (gam(14)*3.6)/(gam(1)*33), "γ₁₄×3.6/(γ₁×33)"),
]

print(f"\n{'配對':>10} {'目標':>14} {'公式':>22} {'計算':>14} {'偏差%':>10} {'隨機分位':>10}")
print("-" * 84)
for label, target, calc, form in o136_claims:
    dev = abs(calc/target - 1)*100
    pct = sum(1 for v in null_g if v > dev)/N*100
    print(f"{label:>10} {target:>14.4f} {form:>22} {calc:>14.4f} {dev:>+10.4f} {pct:>9.1f}%")

# ═══ 3. P_f 字典爆炸檢驗 ════════════════════════════
print(f"\n{'─'*92}")
print("3. ★ P_f 字典爆炸: 有多少結構數可作 P_f?")
print(f"{'─'*92}")

L = [2,1,3,4,7,11,18,29,47]
F = [1,1,2,3,5,8,13,21,34]
lib = set()
for v in L + F: lib.add(v)
lib |= {Nd, B_, dimC, 33, 44, 22, 11, 6, 15.5, 3.6, 37, 40/11, 18/5, 123, 90, 61.5, 28.5, 88}
lib = sorted(x for x in lib if x > 0)
print(f"\nP_f 候選庫大小: {len(lib)}")
print(f"候選: {[f'{x:.4g}' for x in lib]}")

# P_f 比值空間
pf_ratios = sorted(a/b for a in lib for b in lib if a != b)
print(f"\nP_f 比值數: {len(pf_ratios)}")

# 組合空間: γ比 × P_f比
print(f"\n組合空間大小: {len(gratios)} × {len(pf_ratios)} = {len(gratios)*len(pf_ratios):,}")

# 密度: 對隨機目標, 組合空間的最佳偏差
def best_dev_combined(t):
    best = 1e9
    for g in gratios:
        # 需要 P_f 比 = t/g, 檢查是否在 pf_ratios 中
        need = t/g
        i = bisect.bisect_left(pf_ratios, need)
        for j in range(max(0,i-2), min(len(pf_ratios), i+3)):
            d = abs(pf_ratios[j]/need - 1)
            if d < best: best = d
    return best*100

random.seed(555)
N2 = 500
null_c = []
for _ in range(N2):
    t = math.exp(random.uniform(math.log(0.01), math.log(100)))
    null_c.append(best_dev_combined(t))
null_c.sort()

print(f"\n隨機目標的最佳組合匹配偏差 ({N2} 樣本):")
for q in [1,5,10,25,50,75]:
    print(f"  {q:>3}% 分位: {null_c[int(N2*q/100)]:.6f}%")
print(f"  平均: {sum(null_c)/N2:.6f}%")
print(f"  最小: {null_c[0]:.6f}%")

# ═══ 4. 對稱判決 ════════════════════════════════════
print(f"\n{'─'*92}")
print("4. 對稱判決")
print(f"{'─'*92}")

print(f"""
{'框架':>16} {'空間大小':>12} {'隨機最佳偏差中位數':>20} {'觀測中位數':>12} {'判定':>10}
{'-'*74}
{'O34/O35 (sin比)':>16} {'1936':>12} {'0.176%':>20} {'0.146%':>12} {'🔴 巧合':>10}
{'O136 (γ比×P_f)':>16} {f'{len(gratios)*len(pf_ratios):,}':>12} {f'{null_c[N2//2]:.6f}%':>20} {'—':>12} {'🔴 更差':>10}

★ O136 的組合空間比 O34/O35 大 {len(gratios)*len(pf_ratios)/1936:.0f} 倍
★ 隨機最佳偏差中位數 {null_c[N2//2]:.6f}% << O34/O35 的 0.176%
★ → O136 P_f 框架的擬合能力更強 = 更容易湊數 = 更唔可信

★ 誠實結論: 兩個框架都係密度效應主導。
   P_f 框架因為符號庫大, 問題更嚴重。
""")

# ═══ 5. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "25_symmetric_density.json", "w") as f:
    json.dump({
        "gamma_ratio_space": len(gratios),
        "null_gamma_median_pct": null_g[int(N//2)],
        "null_gamma_mean_pct": sum(null_g)/N,
        "pf_library_size": len(lib),
        "pf_ratio_space": len(pf_ratios),
        "combined_space": len(gratios)*len(pf_ratios),
        "null_combined_median_pct": null_c[N2//2],
        "null_combined_mean_pct": sum(null_c)/N2,
        "o136_claims": [{"pair": l, "target": t, "calc": round(c,6), "form": fo,
                         "dev_pct": round(abs(c/t-1)*100, 6)} for l,t,c,fo in o136_claims],
        "verdict": "兩框架都係密度效應; O136 組合空間更大 → 更嚴重",
    }, f, indent=2, ensure_ascii=False)
print(f"✅ 結果已寫入 data/25_symmetric_density.json")