#!/usr/bin/env python3
"""
O136 — Script 2: 用 v10.0 M₀×γ_n×F_proj 框架搜尋夸克質量公式
================================================================
核心: 每個夸克質量 = M₀ × γ_n × F_proj
    其中 γ_n = 4sin²(nπ/88)  (K_Chain 譜)
         F_proj = 結構投影因子 (來自 CY₃, Lucas, Fibonacci 等)

方法:
  1. 對每個夸克, 搜尋所有 n=1..44 使 F_proj = m/(M₀×γ_n) 為結構數
  2. 結構數候選: Lucas 數, CY₃, Nd, F_proj 組合 (如 O54 輕子模式)
  3. 交叉比對: 夸克 vs 輕子的 F_proj 模式

O54 輕子參考:
  e⁻: n=1,  γ₁=0.005096,  F_proj=3.6   = L₆/F₅
  μ⁻: n=7,  γ₇=0.244642,  F_proj=15.5  = Nd−E_proj
  τ⁻: n=20, γ₂₀=1.715370, F_proj=37    = Nd−L₄
"""
import json, math, sys
from pathlib import Path

# ─── 常數 ───────────────────────────────────────────────
φ = (1 + math.sqrt(5)) / 2
φ_inv = 1 / φ
L = [round(φ**n + (-1)**n * φ**(-n)) for n in range(15)]
# L₀=2, L₁=1, L₂=3, L₃=4, L₄=7, L₅=11, L₆=18, L₇=29, L₈=47
F = [0, 1]
for n in range(2, 12): F.append(F[n-1] + F[n-2])
# F₅=5, F₆=8, F₇=13, F₈=21, F₉=34
h11, h21 = 36, 98
CY3 = 134
B = 4
Nd = 44
M0 = 27.900915  # MeV
EPS = φ_inv / 4
D_quark = 1 + (h11/h21) * EPS * (1 + EPS)  # 1.065528

# K_Chain 譜
γ = lambda n: 4 * math.sin(n * math.pi / 88)**2
ω = lambda n: 2 * math.sin(n * math.pi / 88)  # √γ_n

# PDG 質量 (MeV)
PDG_MeV = {
    "top": 172760, "charm": 1270, "up": 2.16,
    "bottom": 4180, "strange": 93.0, "down": 4.67,
    "tau": 1776.86, "muon": 105.66, "electron": 0.510999,
}

# ─── 結構 F_proj 候選庫 ────────────────────────────────
# O54 輕子模式: L₆/F₅=3.6, Nd−E_proj=15.5, Nd−L₄=37
# 擴展: 所有合理的 Lucas/Fibonacci/CY₃ 組合
struct_F_proj = {
    "L₆/F₅": L[6]/F[5],       # 18/5 = 3.6
    "L₅": L[5],                 # 11
    "Nd−L₆": Nd - L[6],        # 44-18 = 26
    "Nd−L₅": Nd - L[5],        # 44-11 = 33
    "Nd−L₄": Nd - L[4],        # 44-7 = 37
    "Nd": Nd,                   # 44
    "L₇": L[7],                 # 29
    "L₈": L[8],                 # 47
    "CY₃/4": CY3/4,            # 33.5
    "CY₃/3": CY3/3,            # 44.67
    "CY₃−L₇": CY3 - L[7],     # 134-29 = 105
    "CY₃−L₆": CY3 - L[6],     # 134-18 = 116
    "CY₃−L₄": CY3 - L[4],     # 134-7 = 127
    "CY₃−Nd": CY3 - Nd,       # 134-44 = 90
    "h²¹": h21,                 # 98
    "h¹¹": h11,                 # 36
    "B×L₅": B*L[5],            # 44
    "B×L₆": B*L[6],            # 72
    "B×L₇": B*L[7],            # 116
    "L₅×L₄": L[5]*L[4],       # 77
    "L₅×L₃": L[5]*L[3],       # 44
    "L₆×L₄": L[6]*L[4],       # 126
    "F₇": F[7],                 # 13
    "F₈": F[8],                 # 21
    "F₉": F[9],                 # 34
    "F₁₀": F[10],              # 55
    "Nd−E_proj": 44 - 28.5,     # 15.5
    "Nd−L₄−D_q": (Nd - L[4]) * D_quark,  # 37 × 1.0655 = 39.42
}

# ─── 搜尋每個夸克的最佳 n 和 F_proj ─────────────────────
print("=" * 78)
print("O136 Script 2: 夸克質量公式搜尋 — M₀×γ_n×F_proj 框架")
print("=" * 78)

results = {}
for particle, m_obs in PDG_MeV.items():
    print(f"\n─── {particle} (m_obs = {m_obs:.4f} MeV) ───")
    best_hits = []
    
    # 試所有 n=1..44
    for n in range(1, 45):
        γ_n = γ(n)
        F_needed = m_obs / (M0 * γ_n)
        
        # 檢查 F_needed 是否接近結構候選
        for name, F_candidate in struct_F_proj.items():
            err = abs(F_needed / F_candidate - 1) * 100
            if err < 3.0:  # 3% 以內
                m_pred = M0 * γ_n * F_candidate
                dev = (m_pred - m_obs) / m_obs * 100
                best_hits.append((err, n, name, F_candidate, m_pred, dev))
    
    # 排序: 誤差最小在前
    best_hits.sort(key=lambda x: x[0])
    
    if best_hits:
        print(f"  {'n':>3} {'F_proj':>20} {'F_val':>10} {'m_pred':>10} {'Δ%':>8}")
        print(f"  {'-'*3} {'-'*20} {'-'*10} {'-'*10} {'-'*8}")
        for err, n, fname, fval, mpred, dev in best_hits[:5]:
            print(f"  {n:>3} {fname:>20} {fval:>10.4f} {mpred:>10.2f} {dev:>8.3f}%")
        results[particle] = [(n, fname, float(fval), float(mpred), float(dev)) 
                            for err, n, fname, fval, mpred, dev in best_hits[:3]]
    else:
        print("  ❌ 無匹配 (3% 閾值內)")
        results[particle] = []

# ─── 擴展搜尋: 含 D_quark 修正 ─────────────────────────
print(f"\n{'='*78}")
print("擴展搜尋: 含 D_quark 色荷修正 (m = M₀ × γ_n × F_proj × D_quark)")
print("=" * 78)

for particle, m_obs in PDG_MeV.items():
    if particle in ["electron", "muon", "tau"]:
        continue  # 輕子無色荷
    print(f"\n─── {particle} (含 D_quark = {D_quark:.6f}) ───")
    best_hits = []
    
    for n in range(1, 45):
        γ_n = γ(n)
        F_needed = m_obs / (M0 * γ_n * D_quark)
        
        for name, F_candidate in struct_F_proj.items():
            err = abs(F_needed / F_candidate - 1) * 100
            if err < 3.0:
                m_pred = M0 * γ_n * F_candidate * D_quark
                dev = (m_pred - m_obs) / m_obs * 100
                best_hits.append((err, n, name, F_candidate, m_pred, dev))
    
    best_hits.sort(key=lambda x: x[0])
    if best_hits:
        print(f"  {'n':>3} {'F_proj':>20} {'F_val':>10} {'m_pred':>10} {'Δ%':>8}")
        print(f"  {'-'*3} {'-'*20} {'-'*10} {'-'*10} {'-'*8}")
        for err, n, fname, fval, mpred, dev in best_hits[:5]:
            print(f"  {n:>3} {fname:>20} {fval:>10.4f} {mpred:>10.2f} {dev:>8.3f}%")
        results[f"{particle}_Dq"] = [(n, fname, float(fval), float(mpred), float(dev))
                                     for err, n, fname, fval, mpred, dev in best_hits[:3]]
    else:
        print(f"  ❌ 無匹配 (3% 閾值內)")
        results[f"{particle}_Dq"] = []

# ─── 模式分析: 輕子 vs 夸克的 n 和 F_proj 規律 ────────
print(f"\n{'='*78}")
print("模式分析: 輕子 vs 夸克")
print("=" * 78)

print(f"\nO54 輕子已閉合公式:")
print(f"  e⁻: n=1,  γ₁=0.005096, F_proj= L₆/F₅ = 3.6        → 0.511 MeV (0.16%)")
print(f"  μ⁻: n=7,  γ₇=0.244642, F_proj= Nd−E_proj = 15.5   → 105.7 MeV (0.13%)")
print(f"  τ⁻: n=20, γ₂₀=1.715370, F_proj= Nd−L₄ = 37        → 1770.9 MeV (0.34%)")
print(f"  模式跳躍: 1 → 7 → 20 (間隔: 6=F₅+1, 13=F₇)")
print(f"  F_proj 增長: 3.6 → 15.5 → 37")

print(f"\n最佳匹配摘要:")
print(f"{'粒子':>10} | {'n':>3} | {'γ_n':>10} | {'F_proj':>20} | {'F_val':>8} | {'m_pred':>10} | {'Δ%':>8}")
print("-" * 78)
for particle, hits in results.items():
    if hits:
        n, fname, fval, mpred, dev = hits[0]
        print(f"{particle:>10} | {n:>3} | {γ(n):>10.6f} | {fname:>20} | {fval:>8.4f} | {mpred:>10.2f} | {dev:>8.3f}%")
    else:
        print(f"{particle:>10} | {'—':>3} | {'—':>10} | {'—':>20} | {'—':>8} | {'—':>10} | {'—':>8}")

# ─── 保存 ───────────────────────────────────────────────
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "02_quark_mode_search.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/02_quark_mode_search.json")