#!/usr/bin/env python3
"""
O136 — Script 3: 夸克質量公式候選驗證
================================================================
確認 Script 2 發現的最佳匹配，測試多個假設組合。

假設 A: 所有夸克用 M₀×γ_n×F_proj (無 D_quark)
假設 B: 所有夸克用 M₀×γ_n×F_proj×D_quark (統一色荷修正)
假設 C: 上 sector 無 D_quark, 下 sector 有 D_quark (v9.0 兼容)
假設 D: 所有夸克用 M₀×γ_n×F_proj, 但 F_proj 含色荷 (CY₃ 投影)
假設 E: 頂夸克用 Higgs VEV, 其餘用 M₀×γ_n×F_proj (新框架)
"""
import json, math, sys
from pathlib import Path

# ─── 常數 ───────────────────────────────────────────────
φ = (1 + math.sqrt(5)) / 2
φ_inv = 1 / φ
L = [round(φ**n + (-1)**n * φ**(-n)) for n in range(15)]
F = [0, 1]
for n in range(2, 12): F.append(F[n-1] + F[n-2])
h11, h21, CY3 = 36, 98, 134
B, Nd, M_val = 4, 44, 33
M0 = 27.900915  # MeV
EPS = φ_inv / 4
KAPPA = 1/16
D_quark = 1 + (h11/h21) * EPS * (1 + EPS)  # 1.065528
γ = lambda n: 4 * math.sin(n * math.pi / 88)**2

# Higgs VEV 頂夸克 (v9.0 結構公式)
V_EW = φ**8 * (φ**3 + 1)  # 245.9837 GeV
VEV_nat = math.sqrt(EPS / (2 * KAPPA))  # 1.11179
SCALE = V_EW / VEV_nat  # 221.25 GeV/nat
m_t_higgs = VEV_nat / math.sqrt(2) * SCALE  # 173.937 GeV

# PDG (MeV)
PDG = {"top": 172760, "charm": 1270, "up": 2.16,
       "bottom": 4180, "strange": 93.0, "down": 4.67,
       "tau": 1776.86, "muon": 105.66, "electron": 0.510999}

# ─── 候選公式 ───────────────────────────────────────────
# 每個假設: {粒子: (n, F_proj_name, F_proj_value, 用D_q?, 用Higgs?)}
hypotheses = {
    "A: M₀×γ_n×F_proj (無色荷)": {
        "up":      (1, "Nd−E_proj", 15.5, False, False),
        "down":    (1, "Nd−L₅", 33.0, False, False),
        "strange": (14, "L₆/F₅", L[6]/F[5], False, False),
        "charm":   (34, "F₇", float(F[7]), False, False),
        "bottom":  (33, "Nd", float(Nd), False, False),
        "top":     (0, "Higgs VEV", 0, False, True),
        "electron":(1, "L₆/F₅", L[6]/F[5], False, False),
        "muon":    (7, "Nd−E_proj", 15.5, False, False),
        "tau":     (20, "Nd−L₄", float(Nd-L[4]), False, False),
    },
    "B: M₀×γ_n×F_proj×D_q (統一色荷)": {
        "up":      (2, "L₆/F₅", L[6]/F[5], True, False),
        "down":    (0, "—", 0, True, False),  # no match
        "strange": (7, "F₇", float(F[7]), True, False),
        "charm":   (39, "L₅", float(L[5]), True, False),
        "bottom":  (31, "Nd", float(Nd), True, False),
        "top":     (0, "Higgs VEV", 0, False, True),
        "electron":(1, "L₆/F₅", L[6]/F[5], False, False),
        "muon":    (7, "Nd−E_proj", 15.5, False, False),
        "tau":     (20, "Nd−L₄", float(Nd-L[4]), False, False),
    },
    "C: Up無D_q / Down有D_q (v9.0兼容)": {
        "up":      (1, "Nd−E_proj", 15.5, False, False),
        "down":    (1, "Nd−L₅", 33.0, False, False),  # no D_q (v9.0: m_d no D_q)
        "strange": (7, "F₇", float(F[7]), True, False),
        "charm":   (34, "F₇", float(F[7]), False, False),
        "bottom":  (31, "Nd", float(Nd), True, False),
        "top":     (0, "Higgs VEV", 0, False, True),
        "electron":(1, "L₆/F₅", L[6]/F[5], False, False),
        "muon":    (7, "Nd−E_proj", 15.5, False, False),
        "tau":     (20, "Nd−L₄", float(Nd-L[4]), False, False),
    },
    "E: Higgs VEV 頂 + M₀×γ_n×F_proj 其餘": {
        "up":      (1, "Nd−E_proj", 15.5, False, False),
        "down":    (1, "Nd−L₅", 33.0, False, False),
        "strange": (14, "L₆/F₅", L[6]/F[5], False, False),
        "charm":   (34, "F₇", float(F[7]), False, False),
        "bottom":  (33, "Nd", float(Nd), False, False),
        "top":     (0, "Higgs VEV", 0, False, True),
        "electron":(1, "L₆/F₅", L[6]/F[5], False, False),
        "muon":    (7, "Nd−E_proj", 15.5, False, False),
        "tau":     (20, "Nd−L₄", float(Nd-L[4]), False, False),
    },
}

# ─── 驗證 ───────────────────────────────────────────────
print("=" * 82)
print("O136 Script 3: 夸克質量公式候選驗證 — 5 假設對比")
print("=" * 82)

overall_results = {}

for h_name, h_particles in hypotheses.items():
    print(f"\n{'='*82}")
    print(f"📌 {h_name}")
    print(f"{'='*82}")
    
    passed = 0
    total = 0
    details = []
    
    for p_name, (n, f_name, f_val, use_dq, use_higgs) in sorted(h_particles.items()):
        if p_name not in PDG:
            continue
        m_obs = PDG[p_name]
        total += 1
        
        if use_higgs:
            m_pred = m_t_higgs * 1000  # GeV → MeV
            formula_str = f"V_EW/√2 = {m_t_higgs:.4f} GeV"
        elif n == 0:
            m_pred = 0
            formula_str = "❌ 無匹配"
        else:
            γ_n = γ(n)
            factor = f_val
            if use_dq:
                factor *= D_quark
            m_pred = M0 * γ_n * factor
            formula_str = f"M₀×γ({n})×{f_name}"
            if use_dq:
                formula_str += "×D_q"
        
        if m_pred > 0:
            dev = (m_pred - m_obs) / m_obs * 100
            status = "✅" if abs(dev) < 1 else "🟡" if abs(dev) < 3 else "❌"
            if abs(dev) < 1: passed += 1
        else:
            dev = 0
            status = "❌"
        
        details.append((p_name, m_pred, m_obs, dev, status, formula_str))
    
    # 輸出表格
    print(f"{'粒子':>10} | {'預言(MeV)':>12} | {'PDG(MeV)':>10} | {'Δ%':>8} | {'狀態':>4} | {'公式'}")
    print("-" * 82)
    for p_name, m_pred, m_obs, dev, status, fstr in details:
        if m_pred > 0:
            print(f"{p_name:>10} | {m_pred:>12.4f} | {m_obs:>10.4f} | {dev:>8.3f}% | {status:>4} | {fstr}")
        else:
            print(f"{p_name:>10} | {'—':>12} | {m_obs:>10.4f} | {'—':>8} | {status:>4} | {fstr}")
    
    score = f"{passed}/{total}"
    print(f"\n  得分: {score} ✅  ({passed/total*100:.0f}%)")
    overall_results[h_name] = {"score": score, "passed": passed, "total": total}

# ─── 總結 ───────────────────────────────────────────────
print(f"\n{'='*82}")
print("📊 總結: 假設對比")
print(f"{'='*82}")
print(f"{'假設':>40} | {'得分':>8} | {'通過率':>8}")
print("-" * 62)
for h_name, res in sorted(overall_results.items(), key=lambda x: -x[1]["passed"]):
    print(f"{h_name:>40} | {res['score']:>8} | {res['passed']/res['total']*100:>7.0f}%")

# ─── 模式分析 ───────────────────────────────────────────
print(f"\n{'='*82}")
print("🔍 模式分析: F_proj 結構共享")
print(f"{'='*82}")

# 提取假設 E 的結果 (最乾淨)
print(f"\n假設 E 模式 (Higgs VEV for top, M₀×γ_n×F_proj for rest):")
print(f"  {''}")
print(f"  Generation 1 (n=1):")
print(f"    e⁻: F_proj = L₆/F₅ = 3.6    → 0.511 MeV (0.16% ✅)")
print(f"    u:  F_proj = Nd−E_proj = 15.5 → 2.20 MeV (2.0% 🟡)")
print(f"    d:  F_proj = Nd−L₅ = 33     → 4.69 MeV (0.47% ✅)")
print(f"    F_proj 增長: 3.6 → 15.5 → 33")
print(f"  {''}")
print(f"  Generation 2:")
print(f"    μ⁻: n=7,  F_proj = Nd−E_proj = 15.5 → 105.8 MeV (0.13% ✅)")
print(f"    s:  n=14, F_proj = L₆/F₅ = 3.6     → 92.3 MeV (-0.78% ✅)")
print(f"    c:  n=34, F_proj = F₇ = 13         → 1273.7 MeV (0.29% ✅)")
print(f"  {''}")
print(f"  Generation 3:")
print(f"    τ⁻: n=20, F_proj = Nd−L₄ = 37 → 1770.8 MeV (-0.34% ✅)")
print(f"    b:  n=33, F_proj = Nd = 44    → 4191.4 MeV (0.27% ✅)")
print(f"    t:  Higgs VEV (y_t=1)          → 173.9 GeV (0.7% ✅)")
print(f"  {''}")
print(f"  F_proj 共享模式:")
print(f"    L₆/F₅=3.6:   e⁻(n=1) ↔ s(n=14)")
print(f"    Nd−E_proj=15.5: μ⁻(n=7) ↔ u(n=1)")
print(f"    F₇=13:       c(n=34) [strange w/ D_q: n=7]")
print(f"    Nd−L₅=33:    d(n=1)")
print(f"    Nd−L₄=37:    τ⁻(n=20)")
print(f"    Nd=44:       b(n=33)")

# ─── 結構 n 值分析 ──────────────────────────────────────
print(f"\n{'='*82}")
print("🔢 K_Chain 模式 n 的結構意義")
print(f"{'='*82}")
print(f"  n=1:   fundamental (最低非零模式)")
print(f"  n=7:   DM 模式 (m₇ = 13.8 MeV, O36)")
print(f"  n=14:  2×7 = 2×DM 模式")
print(f"  n=20:  τ 模式 (F_proj=Nd−L₄=37, O54)")
print(f"  n=33:  M = K_tree 深度 (v9.0 O34)")
print(f"  n=34:  F₉ = Fibonacci 9")
print(f"  n=44:  Nyquist (v_g=0, 最大模式)")
print(f"  {''}")
print(f"  模式跳躍 (1→7→14→20→33→34):")
print(f"    +6, +7, +6, +13, +1")
print(f"    6=F₅+1, 7=L₄, 13=F₇")

# ─── 保存結果 ───────────────────────────────────────────
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "03_hypothesis_validation.json", "w") as f:
    json.dump(overall_results, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/03_hypothesis_validation.json")