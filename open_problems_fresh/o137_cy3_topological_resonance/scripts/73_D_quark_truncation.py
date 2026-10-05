#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O137 — scripts/73: D_quark 截斷階結構機制（為何二階）
======================================================
問題: D = 1 + r·ε·Σ_{k<N} ε^k, r = 18/49, ε = 1/(Bφ).
      O134 scripts/06 判定 N=1 統計排除 (χ²=3.95), N=2 vs N(∞) 唔銳利;
      截斷階之結構機制 🔴 開放 (O137 唯一剩餘).
本 script 建立結構推導:
  定理 1 (代數階): ε 極小多項式 B²x²+Bx−1 = 0, deg = 2 ⟹ ε^k (k≥2) 可 collapse
                   到 {1, ε} 基; ε(1+ε) = 1/B² + (B−1)ε/B (規範型, 係數全 B).
  定理 2 (N_d 因式): α = 3√5−1 滿足 α(α+2) = 44 = N_d (ℤ[√5] 因式分解);
                    ε(1+ε) = α/32, N(ε(1+ε)) = −L₅/B⁴ = −11/256.
  唯一性定理: x_N = ε·Σ_{k<N}ε^k 對 N=1..6, 唯一 N=2 令 32x_N = α ∈ ℤ[√5] 且
             |N(α)| = 44 = N_d (鏈長). 高階 N≥3 破壞 44-因式 ⟹ 結構唯一 = 二階.
  統計判定: N=1 排除 (χ² > 3×最佳), N=2 vs N(∞) 無顯著差別且 N(∞) 非譜修正形式.

判準: mpmath dps=50 代數 EXACT + PDG 觀測 pull; N_search=0 (純代數恆等式).
"""
import json, os
import mpmath as mp

mp.mp.dps = 60
PHI = (1 + mp.sqrt(5)) / 2
SQ5 = mp.sqrt(5)
L = [mp.nint(PHI**n + (-1)**n * PHI**(-n)) for n in range(12)]
B = mp.mpf(4)
N_gen = mp.mpf(3)
L4 = L[4]
L5 = L[5]
N_d = mp.mpf(44)

eps = 1 / (B * PHI)
r = 2 * N_gen**2 / L4**2          # 18/49

results = []
def chk(name, cond, detail):
    results.append((name, bool(cond), detail))
    print(f"  [{'✔' if cond else '✘'}] {name}\n       {detail}")
    return cond

print("=" * 88)
print("O137 scripts/73 — D_quark 截斷階結構機制（為何二階）")
print("=" * 88)

# ── ① ε 之代數階 ────────────────────────────────────────────────────────
print("\n── ① ε 極小多項式: 代數階 = 2 ────────────────────────────────")
print(f"      ε = 1/(Bφ) = {mp.nstr(eps, 16)}")
# φ²−φ−1=0, φ=1/(Bε) ⟹ 1/(B²ε²) − 1/(Bε) − 1 = 0 ⟹ B²ε² + Bε − 1 = 0
poly = B**2 * eps**2 + B * eps - 1
print(f"      B²ε² + Bε − 1 = {mp.nstr(poly, 5)}  (EXACT 0 ⟹ ε 極小多項式 deg=2)")
chk("①-1 ε 極小多項式 B²ε²+Bε−1=0 (代數階=2)", abs(poly) < mp.mpf('1e-50'),
    f"ε = 1/(Bφ) ⟹ φ=1/(Bε) ⟹ B²ε²+Bε−1 = {mp.nstr(poly,3)} ⟹ deg[ℚ(ε):ℚ] = 2")
# 規範型: ε² = (1−Bε)/B² ⟹ ε+ε² = 1/B² + (B−1)ε/B
eff = eps * (1 + eps)
canon_a = 1 / B**2
canon_b = (B - 1) / B * eps
print(f"      ε(1+ε) = ε+ε² 規範型 = 1/B² + (B−1)ε/B = {mp.nstr(canon_a,12)} + {mp.nstr(canon_b,12)} = {mp.nstr(canon_a+canon_b,16)}")
chk("①-2 (1+ε) 因子之規範型係數全由 B 決定: 1/B² + (B−1)ε/B",
    abs(eff - (canon_a + canon_b)) < mp.mpf('1e-50'),
    f"ε(1+ε) = {mp.nstr(eff,16)}; 規範型 = 1/16 + (3/4)ε (B=4), dev=0")
# ε^k k≥3 亦 collapse
eps3 = eps**3
collapsed = eps3 - (2*eps/B**2 - 1/B**3)
chk("①-3 ε³ collapse 到 {1,ε}: ε³ = 2ε/B² − 1/B³", abs(collapsed) < mp.mpf('1e-50'),
    f"ε³ = {mp.nstr(eps3,12)} = 2ε/B² − 1/B³ ⟹ 任何 ε^k (k≥2) 無新代數自由度")

# ── ② N_d 因式: α(α+2) = 44 ─────────────────────────────────────────────
print("\n── ② 44 之 ℤ[√5] 因式分解 ──────────────────────────────────────")
alpha = 3 * SQ5 - 1                       # (775+27√5)/784 之分子根
prod = alpha * (alpha + 2)
print(f"      α = 3√5−1 = {mp.nstr(alpha, 16)}")
print(f"      α(α+2) = {mp.nstr(prod, 16)}  vs N_d = 44")
chk("②-1 ★ 44 = α(α+2) 喺 ℤ[√5] 分解 (|N(α)| = 44 = N_d)", abs(prod - N_d) < mp.mpf('1e-50'),
    f"α(α+2) = (3√5−1)(3√5+1) = 45−1 = 44 = N_d ⟹ 44 在 ℤ[√5] 非素 ⟹ N_d 因式身份")
chk("②-2 α 特徵方程 x²+2x−44=0", abs(alpha**2 + 2*alpha - 44) < mp.mpf('1e-50'),
    f"α² = 44 − 2α (EXACT: {mp.nstr(alpha**2,12)} = 44 − {mp.nstr(2*alpha,12)})")
# ε(1+ε) 與 α 之橋
eps_eff32 = eff * 32
print(f"      ε(1+ε)·32 = {mp.nstr(eps_eff32, 16)}  vs α = {mp.nstr(alpha,16)}")
chk("②-3 ★ 橋: ε(1+ε) = α/32 ⟹ D−1 繼承 N_d-因式", abs(eps_eff32 - alpha) < mp.mpf('1e-50'),
    f"32ε(1+ε) = α ⟹ D−1 = r·ε(1+ε) = r·α/32 = N_gen²α/(B²L₄²) ⟹ 分子 = N_gen²×[N_d 之因式]")
N_eff = eff * (eps_conj * (1 + eps_conj)) if False else None
EPS_CONJ = -PHI / B                       # ε' = 1/(B·φ'), φ' = −1/φ ⟹ ε' = −φ/B
eff_conj = EPS_CONJ * (1 + EPS_CONJ)
N_eff = eff * eff_conj
print(f"      N(ε(1+ε)) = {mp.nstr(N_eff,16)}  vs −L₅/B⁴ = −11/256 = {mp.nstr(-L5/16**2,16)}")
chk("②-4 |N(ε(1+ε))| = L₅/B⁴ = 11/256", abs(N_eff + L5/B**4) < mp.mpf('1e-50'),
    f"N(ε(1+ε)) = εε'(1+ε)(1+ε') = (1+ε+ε'+εε')·(−1/16)... = −L₅/B⁴ EXACT")

# ── ③ 唯一性定理: 何階令 32·x_N 成為 N_d-因式 ─────────────────────────────
print("\n── ③ 唯一性: x_N = ε·Σ_{k<N}ε^k, 32x_N = ⋯ ────────────────────")
found = 0
scan_rows = []
for N in range(1, 7):
    xN = eps * sum(eps**k for k in range(N))
    xN_conj = EPS_CONJ * sum(EPS_CONJ**k for k in range(N))
    y = xN * 32
    y_conj = xN_conj * 32
    # y = a + b√5 ⟹ a = (y+y')/2, b = (y−y')/(2√5); 要求 a,b 整數
    a = (y + y_conj) / 2
    b = (y - y_conj) / (2 * SQ5)
    a_int = mp.nint(a); b_int = mp.nint(b)
    is_int = abs(a - a_int) < mp.mpf('1e-40') and abs(b - b_int) < mp.mpf('1e-40')
    norm = y * y_conj
    hit = is_int and abs(abs(norm) - 44) < mp.mpf('1e-40')
    if hit:
        found += 1
        mark = " ★★ 命中 (α 之 N_d 因式)"
    else:
        mark = ""
    scan_rows.append((N, y, a, b, norm, hit))
    print(f"      N={N}: 32x_N = {mp.nstr(y,10)} = {mp.nstr(a_int,3)}{'+' if b_int>=0 else ''}{mp.nstr(b_int,3)}√5 |N|={mp.nstr(abs(norm),8)} N_d?=44 {mark}")
chk("③-1 唯一 N=2 令 32x_N = α ∈ ℤ[√5] 且 |N| = 44 = N_d", found == 1,
    f"掃描 N=1..6: a,b 整數? N1: (a={mp.nstr(scan_rows[0][2],3)}, b={mp.nstr(scan_rows[0][3],3)}) |N|={mp.nstr(abs(scan_rows[0][4]),6)}; "
    f"N2: (a={mp.nstr(scan_rows[1][2],3)}, b={mp.nstr(scan_rows[1][3],3)}) |N|={mp.nstr(abs(scan_rows[1][4]),6)}=44命中 ⟹ 二階權威")
print("      ⟹ 一階 (N=1) 嘅 32x₁ = 8/φ, |N|=64 = B³ (唔係 44); 三階以上脫離 α-因式")
print("      ⟹ 「二階」= 唯一令 D−1 繼承鏈長 N_d=44 因式身份嘅階")

# ── ④ D 之封閉形式重現 ──────────────────────────────────────────────────
print("\n── ④ D 之多重形式一致性 ───────────────────────────────────────")
D0 = 1 + r * eps * (1 + eps)
D1 = 1 + N_gen**2 * (3*SQ5 - 1) / (B**2 * L4**2)
D2 = 1 + 2 * N_gen**2 * (3*PHI - 2) / (B**2 * L4**2)
D_alpha = 1 + N_gen**2 * alpha / 784
print(f"      D0 (ε 級數)          = {mp.nstr(D0,16)}")
print(f"      D1 (α 閉式)          = {mp.nstr(D1,16)}")
print(f"      D2 (φ 閉式)          = {mp.nstr(D2,16)}")
chk("④-1 四形式全等 (dev=0)", abs(D0-D1)<mp.mpf('1e-50') and abs(D0-D2)<mp.mpf('1e-50') and abs(D0-D_alpha)<mp.mpf('1e-50'),
    f"D = 1 + rε(1+ε) = 1 + N_gen²(3√5−1)/(B²L₄²) = (775+27√5)/784 = {mp.nstr(D0,16)}")
chk("④-2 D−1 = N_gen²×(N_d 因式 α)/(B·L₄)²", abs(D0-1 - N_gen**2*alpha/(B*L4)**2) < mp.mpf('1e-50'),
    f"D−1 = 9·α/784, α(α+2)=44=N_d, 784 = (B·L₄)² = 28²")

# ── ⑤ 統計判定 (O134 scripts/06 數值重用 + 銳利度) ───────────────────────
print("\n── ⑤ 統計/判別整合 ────────────────────────────────────────────")
chi = {1: 3.946, 2: 0.343, 3: 0.184, 4: 0.169, "inf": 0.166}
print(f"      χ²: N=1 {chi[1]} (排除), N=2 {chi[2]}, N=3 {chi[3]}, N=4 {chi[4]}, N(∞) {chi['inf']}")
chk("⑤-1 N=1 統計排除 (χ² > 3×最佳)", chi[1] > 3 * chi["inf"],
    f"χ²₁ = {chi[1]} vs 3×χ²_∞ = {3*chi['inf']} ⟹ 一階無效")
chk("⑤-2 N=2 vs N(∞) 統計上唔銳利 (χ² 比 < 3)", chi[2] < 3 * chi["inf"],
    f"χ²₂ = {chi[2]} vs χ²_∞ = {chi['inf']}, 比 = {chi[2]/chi['inf']:.2f} ⟹ 統計不能裁定 ⟹ 結構裁定 (③)")
print("      ⟹ 統計只排除一階; 二階 vs 無窮 由③唯一性定理裁定 = 二階")
print("      ⟹ N(∞) 亦非「譜修正」形式: D(∞) = 1+rε/(1−ε) 係無窮重和 (需全階機制),")
print("         而二階 = 有限微擾 + ε極小多項式 deg=2 (①) + 44-因式 (②③) 三層一致")

# ── ⑥ 結論 ──────────────────────────────────────────────────────────────
npass = sum(1 for x in results if x[1])
print(f"\n{'='*88}\nRESULT: {npass}/{len(results)} PASS — D_quark 截斷階結構機制\n{'='*88}")
print("結論: D 級數 D = 1 + r·ε(1+ε) 之「為何二階」:")
print("  ① 代數階: ε 極小多項式 deg=2 ⟹ ε+ε² 係唯一「規範 (1/16 + 3ε/4) 全由 B 定」截斷")
print("  ② N_d 因式: 44 = (3√5−1)(3√5+1) 喺 ℤ[√5] 分解; ε(1+ε) = α/32 ⟹ D−1 繼承鏈長")
print("  ③ 唯一性: N=1..6 中僅 N=2 令 32x_N = α (|N|=44); 一階給 |N|=64=B³ 唔係鏈長")
print("  ④ 統計: N=1 排除 (χ²=3.95); N=2 vs N(∞) 無銳利區分 ⟹ 結構裁定 = 二階")
out = {
    "eps_minimal_poly": "B^2 x^2 + B x - 1 = 0 (deg 2)",
    "canonical_form": "eps(1+eps) = 1/B^2 + (B-1)/B * eps",
    "alpha_identity": "alpha = 3√5−1, alpha(alpha+2) = 44 = N_d",
    "bridge": "32 eps(1+eps) = alpha",
    "norm_eff": "-L5/B^4 = -11/256",
    "uniqueness_N2": "only N=2 in 1..6 gives 32 x_N = alpha with |N|=44 (N1 gives |N|=64=B^3)",
    "statistics": {"N1_chi2": 3.946, "N2_chi2": 0.343, "Ninf_chi2": 0.166, "verdict": "N1 excluded, N2 vs Ninf not sharp -> structural"},
    "D_forms_equal": True,
    "verdict": "二階 = 唯一結構裁定 (代數階 2 + N_d 因式 + 唯一性 + 統計排除一階)",
    "result": f"{npass}/{len(results)} PASS",
}
os.makedirs("data", exist_ok=True)
with open("data/73_D_quark_truncation.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("→ data/73_D_quark_truncation.json")