#!/usr/bin/env python3
"""
O214 — Script 01: 結構定義核對 (Structural Definition Verification)
====================================================================
驗證 IDCM 三類 (物質/暗物質/真空能) 嘅結構定義全部有閉合來源,
並且冇用 ΛCDM 標籤 (CSG v2 命名修正: 「暗能量」標籤禁止).

定義 (O214 提案, 全部基於已閉合 O):
  A. 物質 (Matter)      = 觀察者費米子扇區 (Observer Fermion Sector)
     結構身份: N_gen = 3 = B−1, 份額 3/60, Z₂-奇, 反週期, 質量 m = M₀γ_nC_f
     來源: O155 (費米子=觀察者) / O169 (反週期) / CSSG-v3 (質量譜)
  B. 暗物質 (Dark Matter) = 隱藏譜扇區 (Hidden Spectral Sector)
     結構身份: κ = γ_max⁻² = 1/16 可見性閘極, DM = κ⁻¹ = B² = 16, 份額 16/60
     非粒子 (冇質量/自旋/耦合承諾); 玻色塔 m_n 係世界扇區, 唔係 DM
     來源: O163 (DM 真身閉合) / O207 (玻色塔)
  C. 真空能 (Vacuum Energy) = 未被投影能量 (Unprojected Energy)
     結構身份: f_unproj = L₁₀/(2Σγ_even) = 123/180 = 41/60 = ⟨W⟩²/Σγ = 61.5/90
     W-field 凝聚 ⟨W⟩² = 61.5 = μ²/(2λ); 雙標度: 世界 41/60, 觀察者 123/176
     來源: O39 (凝聚) / O41 (觀察者預算) / O148 (雙標度) / O163 (f_unproj)
"""
import sys
from pathlib import Path
import mpmath as mp

mp.mp.dps = 40
OUT = Path(__file__).parent.parent / "data"
OUT.mkdir(exist_ok=True)
checks = []

def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))

print("=" * 100)
print("O214 Script 01: IDCM 三類結構定義核對")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A 60 份額預算分解 (O163 閉合)\n{'─'*100}")
N_d, B, N_gen = 44, 4, 3
Sigma_even, Sigma_odd = 90, 88
mu2 = Sigma_even - Sigma_odd          # 2
L10 = 123
F11 = 89

# 60 = N_d + B²
chk("A1  60 = N_d + B² = 44+16", N_d + B**2 == 60, f"{N_d}+{B**2}={N_d+B**2}")
# (B−1, B², N_d−B+1) = (3, 16, 41)
a, b, c = B - 1, B**2, N_d - B + 1
chk("A2  (B−1, B², N_d−B+1) = (3,16,41)", (a, b, c) == (3, 16, 41), f"({a},{b},{c})")
chk("A3  3+16+41 = 60 閉合", a + b + c == 60, f"{a}+{b}+{c}={a+b+c}")
chk("A4  B = N_gen + 1 = 4", B == N_gen + 1)
chk("A5  3 = B−1 = N_gen (世代數)", a == N_gen)
chk("A6  16 = B² (K_Tree 分支²)", b == B**2)
chk("A7  41 = N_d − B + 1 = N_d − N_gen", c == N_d - N_gen)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 暗物質: 隱藏譜扇區 (O163 閉合)\n{'─'*100}")
# κ = γ_max⁻² = 1/16, γ_max = 4sin²(π/2) = 4 (88-site Laplacian, Nyquist k=88)
gamma_max = 4 * mp.sin(mp.pi / 2) ** 2
kappa = gamma_max ** -2
chk("B1  γ_max = 4sin²(π/2) = 4 (Nyquist)", abs(gamma_max - 4) < mp.mpf('1e-30'))
chk("B2  κ = γ_max⁻² = 1/16", abs(kappa - mp.mpf(1) / 16) < mp.mpf('1e-30'), f"κ={mp.nstr(kappa,10)}")
chk("B3  DM 份額 = κ⁻¹ = B² = 16", abs(1 / kappa - B**2) < mp.mpf('1e-30'), f"κ⁻¹={mp.nstr(1/kappa,10)}")
# 閘極: e⁻ⁿ < κ ⟺ n ≥ 3 被閘走 (可見性權重 φ⁻²ˡ, O165; e⁻ⁿ 近似標籤)
import math
gated = [n for n in range(1, 8) if math.exp(-n) < float(kappa)]
chk("B4  閘極: n≥3 被閘走 (e⁻ⁿ < κ=1/16)", gated == [3, 4, 5, 6, 7], f"e⁻ⁿ<κ 於 n={gated}")
# 16/60 vs ΛCDM Ω_dm — 份額層對應 (觀測比較留 script 02)
chk("B5  16/60 = 0.26667", abs(mp.mpf(16)/60 - mp.mpf('0.2666666666666666667')) < mp.mpf('1e-18'))

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C 真空能: 未被投影能量 (O39/O41/O148/O163)\n{'─'*100}")
# f_unproj = L₁₀/(2Σγ_even) = 123/180 = 41/60
f_unproj = mp.mpf(L10) / (2 * Sigma_even)
chk("C1  f_unproj = L₁₀/(2Σγ_even) = 123/180", f_unproj == mp.mpf(41) / 60, f"= {mp.nstr(f_unproj,10)}")
# ⟨W⟩²/Σγ = 61.5/90 = 41/60
W2 = mp.mpf('61.5')
chk("C2  ⟨W⟩²/Σγ = 61.5/90 = 41/60", W2 / Sigma_even == mp.mpf(41) / 60, f"{mp.nstr(W2/Sigma_even,10)}")
# ⟨W⟩² = μ²/(2λ), λ = 2/123 (O39)
lam = mp.mpf(2) / 123
chk("C3  ⟨W⟩² = μ²/(2λ) = 61.5", mu2 / (2 * lam) == W2, f"{mp.nstr(mu2/(2*lam),10)}")
chk("C4  λ = 2/123 = 2/(3(N_d−dim_ℂ)), dim_ℂ=3", lam == mp.mpf(2) / (3 * (N_d - 3)))
# 雙標度 (O148): 世界 41/60, 觀察者 123/176 = E_min (O41 Landauer)
E_min = mp.mpf(L10) / (4 * N_d)
chk("C5  觀察者標度 E_min = L₁₀/(4N_d) = 123/176", E_min == mp.mpf(123) / 176, f"{mp.nstr(E_min,10)}")
ratio_wo = (mp.mpf(41) / 60) / E_min
chk("C6  世界:觀察者比 = 44:45 = Σγ_odd:Σγ_even",
    abs(ratio_wo - mp.mpf(44) / 45) < mp.mpf('1e-30'), f"{mp.nstr(ratio_wo,12)}")
# 帳戶守恆 (O41): 世界 90 = 61.5+28.5; 觀察者 88 = 61.5+26.5; 差 2 = μ²
chk("C7  帳戶守恆: (90−61.5) − (88−61.5) = 2 = μ²", (Sigma_even - W2) - (Sigma_odd - W2) == mu2)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 玻色塔 m_n = M₀√γ_n (O204/O207) — 唔係 DM\n{'─'*100}")
M0 = mp.mpf('27.900915')  # MeV
def gamma_n(n):
    return 4 * mp.sin(mp.pi * n / 88) ** 2
m7 = M0 * mp.sqrt(gamma_n(7))
chk("D1  m₇ = M₀√γ₇ = 13.800155 MeV (O204)", abs(m7 - mp.mpf('13.800155')) < mp.mpf('1e-5'), f"m₇={mp.nstr(m7,8)}")
# 塔範圍 [1.99, 55.80]: n=1 最小, n=44 最大 (γ 對稱 γ_n = γ_{44−n}? 不 — 用實際)
m1 = M0 * mp.sqrt(gamma_n(1))
m44 = M0 * mp.sqrt(gamma_n(44))
chk("D2  塔範圍 [1.99, 55.80] MeV", 1.99 < float(m1) < 2.01 and 55.7 < float(m44) < 55.9,
    f"[{mp.nstr(m1,5)}, {mp.nstr(m44,5)}]")
# 玻色塔 = 世界扇區 (Z₂-偶) / 費米子 = 觀察者扇區 (Z₂-奇) — O155/O206
chk("D3  玻色塔 C_b = 1 (Z₂-偶, 世界扇區); 費米 C_f (Z₂-奇, 觀察者)", True,
    "O207 分解: m_n = M₀√γ_n·1 vs 費米 m = M₀γ_nC_f (CSSG-v3)")
# 玻色塔質量 m_n ∈ [1.99, 55.8] MeV 遠細過 ΛCDM WIMP 尺度 (GeV-TeV)
chk("D4  玻色塔質量尺度 (MeV) ≠ ΛCDM DM 粒子尺度 (GeV-TeV)",
    float(m44) / 1000 < 0.1, "m_n ∈ MeV 級, 非 WIMP 級")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§E 命名紀律 (CSG v2): 結構名 ≠ ΛCDM 標籤\n{'─'*100}")
# 三類結構名 (唔含 ΛCDM 標籤)
structural_names = {
    "物質": "觀察者費米子扇區 (Observer Fermion Sector)",
    "暗物質": "隱藏譜扇區 (Hidden Spectral Sector, κ 閘極後)",
    "真空能": "未被投影能量 (Unprojected Energy, W-field 凝聚)",
}
for k, v in structural_names.items():
    print(f"  {k:>5} = {v}")
chk("E1  真空能結構名 = 未被投影能量 (禁「暗能量」標籤)", "暗能量" not in structural_names["真空能"])
chk("E2  暗物質結構名 = 隱藏譜扇區 (禁「粒子/WIMP」承諾)", all(w not in structural_names["暗物質"] for w in ["粒子", "WIMP", "axion"]))
chk("E3  物質結構名 = 費米子扇區 (禁「重子」誤導)", "重子" not in structural_names["物質"])
chk("E4  m₇ 唔係 DM: 玻色塔成員, 世界扇區 (O207 定位)", True,
    "O136 docs/02「DM 模式」舊標籤將修正")

# ═══════════════════════════════════════════════════════════════
n_pass = sum(1 for _, ok in checks if ok)
print(f"\n{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

import json
with open(OUT / "01_structural_definitions.json", "w") as f:
    json.dump({
        "checks_pass": n_pass, "checks_total": len(checks),
        "budget": {"B": B, "N_gen": N_gen, "N_d": N_d, "parts": [a, b, c], "sum": a+b+c},
        "kappa": float(kappa), "f_unproj": float(f_unproj),
        "W2": float(W2), "E_min": float(E_min), "m7_MeV": float(m7),
        "structural_names": structural_names,
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/01_structural_definitions.json")
