#!/usr/bin/env python3
"""
O136 — Script 8: 最終閉合驗證 (方向二)
================================================================
完整驗證所有 SM 費米子的 Lucas 階梯選擇律公式。

公式結構:
  m_f = M₀ × γ_n × P_f × (D_quark 如適用)

模式分配 (從雙重 Lucas 條件推導):
  1st gen (n=1):  e⁻, u, d  — 由 P_f 區分
  2nd gen:        μ⁻(n=7), s(n=14), c(n=34)
  3rd gen:        τ⁻(n=20), b(n=33), t(Higgs VEV)

γ 比結構:
  輕子: L₁, Nd+L₃, L₄×(Nd+L₃)
  夸克: L₁, L₃×(Nd+L₁), CY₃×F₅+L₆, CY₃×F₅
"""
import json, math, sys
from pathlib import Path

# ─── 常數 ───────────────────────────────────────────────
phi = (1 + math.sqrt(5))/2
L = [int(round(phi**n + (-1)**n * phi**(-n))) for n in range(15)]
F = [0, 1]
for n in range(2, 12): F.append(F[n-1] + F[n-2])
h11, h21, CY3 = 36, 98, 134
Nd, B, M_val = 44, 4, 33
M0 = 27.900915  # MeV
EPS = 1/phi/4
D_quark = 1 + (h11/h21) * EPS * (1 + EPS)  # 1.065528

# K_Chain 譜
gamma = lambda n: 4 * math.sin(n * math.pi / 88)**2

# Higgs VEV 頂夸克
V_EW = phi**8 * (phi**3 + 1)
VEV_nat = math.sqrt(EPS / (2 * 1/16))
SCALE = V_EW / VEV_nat
m_t = VEV_nat / math.sqrt(2) * SCALE * 1000  # MeV

# PDG (MeV)
PDG = {"top": 172760, "charm": 1270, "up": 2.16,
       "bottom": 4180, "strange": 93.0, "down": 4.67,
       "tau": 1776.86, "muon": 105.66, "electron": 0.510999}

# ─── 完整公式集 ─────────────────────────────────────────
# (n, P_f, 名稱, 是否用 D_q, 是否 Higgs)
formulas = {
    "electron": (1, L[6]/F[5], "L6/F5", False, False),
    "muon":     (7, Nd - 28.5, "Nd-E_proj", False, False),
    "tau":      (20, Nd - L[4], "Nd-L4", False, False),
    "up":       (1, Nd - 28.5, "Nd-E_proj", False, False),
    "down":     (1, Nd - L[5], "Nd-L5", False, False),
    "strange":  (14, L[6]/F[5], "L6/F5", False, False),
    "charm":    (34, F[7], "F7", False, False),
    "bottom":   (33, Nd, "Nd", False, False),
    "top":      (0, 0, "Higgs VEV", False, True),
}

# ─── 輸出 ───────────────────────────────────────────────
print("=" * 78)
print("O136 Script 8: 最終閉合驗證 (方向二)")
print("=" * 78)

print(f"\n{'粒子':>10} | {'n':>3} | {'γ_n':>12} | {'P_f':>15} | {'預言(MeV)':>12} | {'PDG(MeV)':>10} | {'Δ%':>8} | {'狀態':>4}")
print("-" * 78)

passed = 0
total = len(PDG)
results = {}

for p_name, (n, pf, pf_name, use_dq, is_higgs) in formulas.items():
    m_obs = PDG[p_name]
    
    if is_higgs:
        m_pred = m_t
        formula_str = "Higgs VEV"
    else:
        factor = pf
        if use_dq:
            factor *= D_quark
        m_pred = M0 * gamma(n) * factor
        formula_str = f"M0×γ({n})×{pf_name}"
        if use_dq:
            formula_str += "×Dq"
    
    dev = (m_pred - m_obs) / m_obs * 100
    status = "✅" if abs(dev) < 1 else "🟡" if abs(dev) < 3 else "❌"
    if abs(dev) < 1: passed += 1
    
    gn = gamma(n) if not is_higgs else 0
    print(f"{p_name:>10} | {n:>3} | {gn:>12.6f} | {pf:>15.4f} | {m_pred:>12.4f} | {m_obs:>10.4f} | {dev:>8.4f}% | {status:>4}")
    
    results[p_name] = {
        "n": n, "gamma_n": float(gn), "P_f": float(pf),
        "m_pred": float(m_pred), "m_obs": m_obs,
        "dev_pct": float(dev), "status": status,
        "formula": formula_str,
    }

# ─── 總結 ───────────────────────────────────────────────
print(f"\n{'='*78}")
print(f"閉合: {passed}/{total} ✅  ({passed/total*100:.0f}%)")
print(f"{'='*78}")

# 列出每個粒子的結構公式
print(f"\n─── 結構公式歸納 ───")
print(f"""
輕子 (M₀ × γ_n × P_f):
  e⁻ = M₀ × γ₁ × L₆/F₅      = {results['electron']['m_pred']:.4f} MeV  ({results['electron']['dev_pct']:.2f}%)
  μ⁻ = M₀ × γ₇ × (Nd-E_proj) = {results['muon']['m_pred']:.2f} MeV  ({results['muon']['dev_pct']:.2f}%)
  τ⁻ = M₀ × γ₂₀ × (Nd-L₄)   = {results['tau']['m_pred']:.2f} MeV  ({results['tau']['dev_pct']:.2f}%)

夸克 (M₀ × γ_n × P_f, 頂夸克 Higgs VEV):
  u  = M₀ × γ₁ × (Nd-E_proj) = {results['up']['m_pred']:.4f} MeV  ({results['up']['dev_pct']:.2f}%)
  d  = M₀ × γ₁ × (Nd-L₅)     = {results['down']['m_pred']:.4f} MeV  ({results['down']['dev_pct']:.2f}%)
  s  = M₀ × γ₁₄ × L₆/F₅      = {results['strange']['m_pred']:.4f} MeV  ({results['strange']['dev_pct']:.2f}%)
  c  = M₀ × γ₃₄ × F₇         = {results['charm']['m_pred']:.2f} MeV  ({results['charm']['dev_pct']:.2f}%)
  b  = M₀ × γ₃₃ × Nd         = {results['bottom']['m_pred']:.2f} MeV  ({results['bottom']['dev_pct']:.2f}%)
  t  = Higgs VEV (y_t=1)      = {results['top']['m_pred']:.0f} MeV  ({results['top']['dev_pct']:.2f}%)
""")

# γ 比結構
print(f"─── γ 比結構 ───")
print(f"""
γ₁/γ₁   = 1                  = L₁
γ₇/γ₁   = 48.0088 ≈ 48       = Nd + L₃          (0.018%)
γ₂₀/γ₁  = 336.626 ≈ 336      = L₄ × (Nd+L₃)     (0.186%)
γ₁₄/γ₁  = 180.290 ≈ 180      = L₃ × (Nd+L₁)     (0.161%)
γ₃₄/γ₁  = 689.101 ≈ 688      = CY₃ × F₅ + L₆   (0.160%)
γ₃₃/γ₁  = 670.009 ≈ 670      = CY₃ × F₅         (0.001%)
""")

# Lucas 階梯
print(f"─── Lucas 階梯 ───")
print(f"""
n 值:    1        7        14       20       33       34
      L₁       L₄       2×L₄     L₆+L₀    M        F₉
      |        |        |        |        |        |
γ比:  L₁    Nd+L₃   L₃×(Nd+L₁) L₄×(Nd+L₃) CY₃×F₅  CY₃×F₅+L₆
      |        |        |        |        |        |
粒子: e⁻,u,d  μ⁻       s        τ⁻       b        c
                  ↘       ↗        ↘       ↗
                  (n=7)  (n=14)   (n=20)  (n=33)
                  色荷偏移 +7      色荷偏移 +13
""")

# 保存
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "08_final_closure.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"✅ 結果已寫入 data/08_final_closure.json")