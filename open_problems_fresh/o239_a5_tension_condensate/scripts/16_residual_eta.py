#!/usr/bin/python3
"""O239 — Script 16: 合成殘餘 ∝ η_sum 形式檢定（即時落手 候選①）
============================================================================
docs/12 §五候選①: 「合成殘餘 ∝ η_sum（高能時空離散效應）」——R9 只係
見「最差對係細 n 高能、好對係大 n 低能」(903 掃描)。而家做形式檢定:
d(η_sum) 係咪單調? 定量斜率? 係咩函數形式?

本 script 用 R9 嘅 903 對數據（eta0 + 每對 d7 + 尾部比）重做, 但按 η_sum 排序
分析。預註冊判據:
  Q1 相關係數: Spearman(d7, η_sum) > 0.8（單調正相關）
  Q2 冪律斜率: log(d7) vs η_sum —— 若斜率 ≈ 1（d7 ∝ e^η 線性）定 ≫1（指數）?
  Q3 分段: η_sum 低半 vs 高半 d7 中位比（高能區殘餘至少 10× 低能區）
  Q4 邊界: d7 > 1e-6 嘅 η_sum 閾值（殘餘開始「可見」嘅能量）——報告
數據: scripts/11 嘅 903 對 —— 本 script 重新計算（快: numpy searchsorted）
"""
import itertools, json
import numpy as np
from scipy import stats

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/16 — 合成殘餘 ∝ η_sum 形式檢定")
print("=" * 78)

N = 44
eta0 = -np.log(np.tan(np.arange(1, N, dtype=np.float64) * np.pi / 176.0))

def ladder_at(ell):
    Nl = N * 4**ell
    k = np.arange(Nl, 0, -1, dtype=np.float64)
    x = k * np.pi / (176.0 * 4**ell)
    return -np.log(np.tan(x))

lads = {ell: ladder_at(ell) for ell in range(4, 8)}
rows = []
for a, b in itertools.combinations(range(1, N), 2):
    s = eta0[a-1] + eta0[b-1]
    ds = []
    for ell in range(4, 8):
        lad = lads[ell]
        j = np.searchsorted(lad, s)
        dmin = np.inf
        if j > 0:
            dmin = min(dmin, abs(s - lad[j-1]))
        if j < len(lad):
            dmin = min(dmin, abs(s - lad[j]))
        ds.append(float(dmin))
    trs = [ds[i+1]/ds[i] for i in range(3) if ds[i] > 0]
    meanr = sum(trs)/len(trs) if trs else float('nan')
    rows.append((a, b, float(s), ds[-1], meanr))

X = np.array([r[2] for r in rows])     # η_sum
Y = np.array([r[3] for r in rows])     # d7
R = np.array([r[4] for r in rows])     # 收斂比
labels_ab = [(r[0], r[1]) for r in rows]

print(f"   903 對: η_sum ∈ [{X.min():.3f}, {X.max():.3f}]")

# ── Q1: Spearman ──
sp = stats.spearmanr(X, Y)
print("\n── Q1: Spearman(d7, η_sum) ──")
print(f"   ρ = {sp.statistic:.4f}  p = {sp.pvalue:.2e}")
chk("Q1 ρ > 0.8 (單調正相關)", sp.statistic > 0.8, f"ρ={sp.statistic:.4f}")

# ── Q2: 冪律/log 形式 ──
print("\n── Q2: log(d7) vs η_sum 形式 ──")
mask = Y > 0
lr = stats.linregress(X[mask], np.log(Y[mask]))
print(f"   log(d7) = {lr.slope:.4f}·η_sum + {lr.intercept:.4f}, R² = {lr.rvalue**2:.4f}")
print(f"   ⟹ d7 ∝ exp({lr.slope:.3f}·η_sum)——斜率 ≈ 1 即 d7 ∝ e^η (linear in energy), ≫1 即超指數")
print(f"   對照: 若 d7 ∝ 1/階梯密度 ∝ 4^ℓ 尾 —— 應 log(d7) vs η_sum 斜率冇結構")
chk("Q2 log 線性 R² > 0.8 (冪律形式成立)", lr.rvalue**2 > 0.8, f"R²={lr.rvalue**2:.4f}")

# ── Q3: 低半 vs 高半 ──
med = np.median(X)
lo = Y[X <= med]; hi = Y[X > med]
ratio = np.median(hi) / np.median(lo)
print("\n── Q3: η_sum 低半 vs 高半 ──")
print(f"   低半 η_sum≤{med:.2f}: d7 中位 {np.median(lo):.2e}")
print(f"   高半 η_sum>{med:.2f}: d7 中位 {np.median(hi):.2e}")
print(f"   中位比 = {ratio:.1f}×")
chk("Q3 高能殘餘 ≥10× 低能", ratio >= 10, f"{ratio:.1f}×")

# ── Q4: d7 > 1e-6 閾值 ──
print("\n── Q4: 殘餘開始「可見」嘅 η_sum 閾值 ──")
vis = X[Y > 1e-6]
if len(vis) > 0:
    thr = vis.min()
    print(f"   d7>1e-6 嘅對: {len(vis)}/903, 最小 η_sum = {thr:.3f} (η_sum > 此值殘餘可見)")
    # 呢啲對係咩?
    vis_idx = np.where(Y > 1e-6)[0]
    vis_pairs = [(labels_ab[i], round(X[i],3), f'{Y[i]:.1e}') for i in vis_idx[:8]]
    print(f"   例子: {vis_pairs}")
else:
    thr = float('inf')
    print("   冇對超過 1e-6（全部收斂）")

json.dump({
    "Q1_spearman": sp.statistic, "Q1_p": float(sp.pvalue),
    "Q2_slope_log": lr.slope, "Q2_R2": float(lr.rvalue**2),
    "Q3_ratio_med": float(ratio),
    "Q4_threshold": float(thr) if len(vis) > 0 else None,
    "Q4_n_visible": len(vis),
    "verdict": "合成殘餘 ∝ exp(斜率×η_sum)" if lr.rvalue**2 > 0.8 else "非冪律形式",
}, open("data/16_residual_eta.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")