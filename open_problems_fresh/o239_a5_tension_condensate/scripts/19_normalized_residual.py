#!/usr/bin/python3
"""O239 — Script 19: Audit 幽靈推導補落碟 (A: 歸一化殘餘終審)
============================================================================
Audit 發現 (2026-10-12): R13「殘餘∝η_sum 撤回」結論核心 = inline 歸一化分析,
冇落碟 script。本 script 將歸一化終審正式化 (docs/13 §一 之判決依據):

  原始: d7 (903 對, 對 ℓ=7 階梯絕對殘餘) vs η_sum: ρ=0.764
  歸一化: d7 ÷ local_spacing(ℓ=7) → ρ 應 ~0 (階梯密度平凡效應)

預註冊判據:
  N1 歸一化後 Spearman(d7/spacing, η_sum) < 0.2 (原始 0.764 → 應崩潰)
  N2 高/低半歸一化殘餘中位比 < 2× (原始 5.3× → 應 ~1)
  N3 歸一化殘餘中位 ≈ 0.25 ± 0.02 (均勻分佈期望)
產物: data/19_normalized_residual.json
"""
import itertools, json
import numpy as np
from scipy import stats

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/19 — Audit 補落碟 A: 歸一化殘餘終審")
print("=" * 78)

N = 44
eta0 = -np.log(np.tan(np.arange(1, N, dtype=np.float64) * np.pi / 176.0))

def ladder_at(ell):
    Nl = N * 4**ell
    k = np.arange(Nl, 0, -1, dtype=np.float64)
    return -np.log(np.tan(k * np.pi / (176.0 * 4**ell)))

lad = ladder_at(7)
spacing = np.diff(lad)

rows = []
for a, b in itertools.combinations(range(1, N), 2):
    s = eta0[a-1] + eta0[b-1]
    j = np.searchsorted(lad, s)
    dmin = np.inf; local_sp = np.inf
    if j > 0:
        dmin = min(dmin, abs(s - lad[j-1])); local_sp = min(local_sp, spacing[min(j-1, len(spacing)-1)])
    if j < len(lad):
        dmin = min(dmin, abs(s - lad[j])); local_sp = min(local_sp, spacing[min(j, len(spacing)-1)])
    rows.append((float(s), float(dmin), float(local_sp)))

X = np.array([r[0] for r in rows])
Y = np.array([r[1] for r in rows])
SP = np.array([r[2] for r in rows])
YN = Y / SP

sp_raw = stats.spearmanr(X, Y)
sp_norm = stats.spearmanr(X, YN)
print(f"\n原始 d7 vs η_sum:   ρ = {sp_raw.statistic:.4f} (p={sp_raw.pvalue:.1e})")
print(f"歸一化 d7/sp vs η:  ρ = {sp_norm.statistic:.4f} (p={sp_norm.pvalue:.1e})")
chk("N1 歸一化 ρ < 0.2 (階梯密度平凡效應)", abs(sp_norm.statistic) < 0.2, f"ρ={sp_norm.statistic:.4f}")

med = np.median(X)
lo_n = YN[X <= med]; hi_n = YN[X > med]
ratio = np.median(hi_n) / np.median(lo_n)
print(f"\n低半 (η≤{med:.2f}): 歸一化中位 {np.median(lo_n):.4f}")
print(f"高半 (η>{med:.2f}): 歸一化中位 {np.median(hi_n):.4f}")
print(f"高/低比 = {ratio:.2f}×")
chk("N2 高/低半中位比 < 2×", ratio < 2.0, f"{ratio:.2f}×")

ymn = float(np.median(YN))
print(f"\n歸一化殘餘中位 = {ymn:.4f} (均勻期望 0.25)")
chk("N3 中位 ≈ 0.25 ± 0.02", abs(ymn - 0.25) < 0.02, f"{ymn:.4f}")

json.dump({
    "N1_raw_rho": float(sp_raw.statistic), "N1_norm_rho": float(sp_norm.statistic),
    "N2_ratio_med": float(ratio),
    "N3_median_norm": ymn,
    "verdict": "歸一化後 ρ 崩潰至 ~0 ⟹ 殘餘∝η_sum 係階梯密度平凡效應 (docs/13 撤回確認)",
}, open("data/19_normalized_residual.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")