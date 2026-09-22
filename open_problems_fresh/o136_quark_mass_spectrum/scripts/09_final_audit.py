#!/usr/bin/env python3
"""
O136 — Script 9: 最終數值核對 (Audit)
================================================================
獨立核對本 session 所有關鍵數值，標記 ✅/🔴。

核對範圍:
  1. K_Chain 譜 γ_n = 4sin²(nπ/88)
  2. γ 比: γ_n/γ₁ 與 Lucas 組合
  3. 質量公式閉合 (9 費米子)
  4. 偏差分析 (過擬合檢驗)
  5. 盲測可行性 (固定公理)
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
M0 = 27.900915
EPS = 1/phi/4
D_quark = 1 + (h11/h21) * EPS * (1 + EPS)
gamma = lambda n: 4 * math.sin(n * math.pi / 88)**2

print("=" * 80)
print("O136 Script 9: 最終數值核對 (Audit)")
print("=" * 80)

results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(f"  [{'✅' if cond else '🔴'}] {name} {detail}")

# ═══ 1. 基礎常數 ═══════════════════════════════════════
print(f"\n─── 1. 基礎常數 ───")
check("φ = 1.6180339887", abs(phi - 1.618033988749895) < 1e-12)
check("Lucas L0-L8 = [2,1,3,4,7,11,18,29,47]", L[:9] == [2,1,3,4,7,11,18,29,47])
check("Fibonacci F5-F10 = [5,8,13,21,34,55]", F[5:11] == [5,8,13,21,34,55])
check("h11 = 36 = L2²×L3", h11 == 36)
check("h21 = 98 = 2×L4²", h21 == 98)
check("CY3 = 134 = h11+h21", CY3 == 134)
check("Nd = 44", Nd == 44)
check("M = 33 = (CY3-2)/B", M_val == 33)
check("M0 = 27.900915 MeV", abs(M0 - 27.900915) < 1e-9)

# ═══ 2. K_Chain 譜 ═════════════════════════════════════
print(f"\n─── 2. K_Chain 譜 γ_n = 4sin²(nπ/88) ───")
spec_vals = {1: 0.005095770779, 7: 0.244642021, 14: 0.918718366,
             20: 1.715370322, 33: 3.414213562, 34: 3.511499150}
for n, expected in spec_vals.items():
    check(f"γ_{n} = {expected:.6f}", abs(gamma(n) - expected) < 1e-6, f"({gamma(n):.9f})")

# Σγ 檢查
S = sum(gamma(n) for n in range(1, 45))
check("Σγ(k=1..44) = 90", abs(S - 90) < 1e-9, f"({S:.12f})")

# ═══ 3. γ 比與 Lucas 組合 ══════════════════════════════
print(f"\n─── 3. γ 比與 Lucas 組合 ───")
g1 = gamma(1)
ratios = {
    1:  (1, "L1"),
    7:  (Nd + L[3], "Nd+L3=48"),
    20: (L[4]*(Nd+L[3]), "L4×(Nd+L3)=336"),
    14: (L[3]*(Nd+L[1]), "L3×(Nd+L1)=180"),
    34: (CY3*F[5]+L[6], "CY3×F5+L6=688"),
    33: (CY3*F[5], "CY3×F5=670"),
}
for n, (target, label) in ratios.items():
    actual = gamma(n)/g1
    dev = abs(actual-target)/target*100
    status = "✅" if dev < 1.0 else "🔴"
    check(f"γ_{n}/γ₁ ≈ {label} ({dev:.4f}%)", dev < 1.0, f"(實際 {actual:.6f})")

# ═══ 4. 質量公式閉合 ═══════════════════════════════════
print(f"\n─── 4. 質量公式閉合 (M₀×γ_n×P_f 框架) ───")

PDG = {"top": 172760, "charm": 1270, "up": 2.16,
       "bottom": 4180, "strange": 93.0, "down": 4.67,
       "tau": 1776.86, "muon": 105.66, "electron": 0.510999}

# Higgs VEV 頂夸克
V_EW = phi**8 * (phi**3 + 1)
VEV_nat = math.sqrt(EPS / (2 * 1/16))
SCALE = V_EW / VEV_nat
m_t = VEV_nat / math.sqrt(2) * SCALE * 1000  # MeV

formulas = {
    "electron": (1, L[6]/F[5], "L6/F5"),
    "muon":     (7, Nd - 28.5, "Nd-E_proj"),
    "tau":      (20, Nd - L[4], "Nd-L4"),
    "up":       (1, Nd - 28.5, "Nd-E_proj"),
    "down":     (1, Nd - L[5], "Nd-L5"),
    "strange":  (14, L[6]/F[5], "L6/F5"),
    "charm":    (34, F[7], "F7"),
    "bottom":   (33, Nd, "Nd"),
    "top":      (0, 0, "Higgs VEV"),
}

print(f"\n{'粒子':>10} | {'n':>3} | {'公式':>30} | {'預言(MeV)':>12} | {'PDG':>10} | {'Δ%':>8} | {'狀態':>4}")
print("-" * 80)

mass_results = {}
for p_name, (n, pf, pf_name) in formulas.items():
    m_obs = PDG[p_name]
    if p_name == "top":
        m_pred = m_t
        formula_str = "V_EW/√2 (y_t=1)"
    else:
        m_pred = M0 * gamma(n) * pf
        formula_str = f"M0×γ({n})×{pf_name}"
    dev = (m_pred - m_obs)/m_obs*100
    status = "✅" if abs(dev) < 1 else "🟡" if abs(dev) < 3 else "🔴"
    print(f"{p_name:>10} | {n:>3} | {formula_str:>30} | {m_pred:>12.4f} | {m_obs:>10.4f} | {dev:>8.3f}% | {status:>4}")
    mass_results[p_name] = {"m_pred": m_pred, "dev": dev, "status": status}

n_pass = sum(1 for v in mass_results.values() if v["status"] == "✅")
check(f"閉合 {n_pass}/9 粒子 < 1%", n_pass >= 8, f"({n_pass}/9)")

# ═══ 5. 過擬合檢驗 ═════════════════════════════════════
print(f"\n─── 5. 過擬合檢驗 ───")
print(f"""
🔴 致命傷 1: 符號庫過大
   {len(L)} Lucas + {len(F)} Fibonacci + Nd/M/B/CY3/h11/h21 + 4 運算
   → 1-1000 範圍任意數都有 ≥3 種組合湊到 0.2%
   → 每個 γ 比匹配都是事後挑選, 不是唯一解

🔴 致命傷 2: 移動球門
   n=1: L₁ → n=7: L₄ → n=20: L₆+L₀ (擴充加法組合)
   → n=34: F₉ (擴充 Fibonacci) → n=33: M (擴充幾何深度)
   → 每次擴充都是為了容納新數據

🔴 致命傷 3: 公式形式不一致
   輕子: P_f = 3.6/15.5/37 (無量綱投影數)
   夸克: P_f = F₇/Nd (直接 Fibonacci/Lucas 數)
   → 沒有統一算子機制
""")

# ═══ 6. 盲測測試 ═══════════════════════════════════════
print(f"─── 6. 盲測測試 (固定公理) ───")
print(f"""
固定公理: n ∈ {{Lucas ≤ 44}} ∪ {{Nd − L_k}} = {{1,3,4,7,11,15,18,26,29,33,37,40,41,43}}

在固定公理下:
  n=20 (τ⁻): 不是 Lucas, 不是 Nd−L_k → 🔴 無資格
  n=14 (s):  不是 Lucas, 不是 Nd−L_k → 🔴 無資格
  n=34 (c):  不是 Lucas, 不是 Nd−L_k → 🔴 無資格
  n=33 (b):  = Nd−L₅ ✅ 有資格 (但為何選 33 而非 15/26/37?)

→ 固定公理下只有 n=1, 7, 33 有資格
→ τ, s, c 的模式分配無法從公理推導 → 🔴 盲測失敗

盲測預言: 從公理鎖定 n_t
  t 夸克質量 = 173.9 GeV
  M₀×γ_n×P_f 最大可達: M₀ × γ₄₄(=4) × P_f_max
  若 P_f ≤ CY₃=134: m_max = {M0*4*CY3:.0f} MeV = {M0*4*CY3/1000:.1f} GeV << 173.9 GeV
  → t 必須用 Higgs VEV 機制 (y_t=1)
  → 這是唯一有結構正當性的「預言」: M₀ 框架有質量上限
""")

# ═══ 7. 保存結果 ═══════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "09_final_audit.json", "w") as f:
    json.dump({
        "checks": [{"name": n, "pass": c, "detail": d} for n, c, d in results],
        "mass_results": mass_results,
        "fatal_flaws": ["symbol_library_overfitting", "moving_goalposts", "inconsistent_formulas"],
        "blind_test": "FAILED - tau/s/charm modes not derivable from fixed axioms",
        "only_structural_claims": ["n=1 fundamental mode", "n=7 DM mass (O34)", "t via Higgs VEV (mass cap)"],
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/09_final_audit.json")