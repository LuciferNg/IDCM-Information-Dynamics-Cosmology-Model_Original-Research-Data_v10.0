#!/usr/bin/env python3
"""O146 L2: 物理存在 — 質量比 δ_min 盲測 (拍頻對質量比空間有冇吸引力)
====================================================================
🚨 陷阱意識: 946 個拍頻密佈 [0,1.93], 平均間距 ~0.002 → 任意質量比
都近某個拍頻 (單一匹配 p≈0.5)。所以正確檢驗唔係「搵到匹配」,
而係「質量比集合嘅 δ_min 分佈 vs 隨機比集合嘅 δ_min 分佈」—
整體比較, 唔指定任何 (d,s), 測拍頻集合有冇統計吸引力。
"""
import math, json, os
import numpy as np
from scipy import stats

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "02_physical_mapping.json")
N = 44

# ---------- 拍頻集合 B (946 值) ----------
B = []
for n in range(1, N+1):
    for m in range(n+1, N+1):
        B.append(abs(2*math.sin(m*math.pi/88) - 2*math.sin(n*math.pi/88)))
B = np.array(sorted(B))
print(f"拍頻集合: {len(B)} 值, 範圍 [{B.min():.4f}, {B.max():.4f}]")
print(f"拍頻平均間距: {(B.max()-B.min())/len(B):.5f}")

# ---------- PDG 2024 粒子質量 (MeV, 觀測值, 無 IDCM 假設) ----------
MASS = {
    "e":  0.51099895,   # 電子
    "mu": 105.6583755,  # μ
    "tau":1776.86,      # τ
    "u":  2.16,         # up
    "d":  4.67,         # down
    "s":  93.4,         # strange
    "c":  1270.0,       # charm
    "b":  4180.0,       # bottom
    "t":  172690.0,     # top
    "W":  80369.0,      # W boson
    "Z":  91187.6,      # Z boson
    "H":  125250.0,     # Higgs
}
names = list(MASS.keys())

# 質量比集合: 全部 i<j, 取 min/max <1 (無量綱, 對稱)
ratios_real = []
ratio_pairs = []
for i in range(len(names)):
    for j in range(i+1, len(names)):
        r = min(MASS[names[i]], MASS[names[j]]) / max(MASS[names[i]], MASS[names[j]])
        ratios_real.append(r)
        ratio_pairs.append((names[i], names[j]))
ratios_real = np.array(ratios_real)
print(f"\n獨立質量比: {len(ratios_real)} 個 (全部 <1)")
print(f"範圍: [{ratios_real.min():.2e}, {ratios_real.max():.4f}]")

# ---------- δ_min 分佈 ----------
def delta_min(xs, Bset):
    """每個 x 到最近拍頻嘅距離"""
    idx = np.searchsorted(Bset, xs)
    idx = np.clip(idx, 1, len(Bset)-1)
    d = np.minimum(np.abs(Bset[idx]-xs), np.abs(Bset[idx-1]-xs))
    return d

d_real = delta_min(ratios_real, B)
print(f"\n真實質量比 δ_min: 中位數 = {np.median(d_real):.5f}, 均值 = {np.mean(d_real):.5f}")

# ---------- 對照 1: 均勻隨機比 × 10000 (同數量) ----------
rng = np.random.default_rng(20260904)
lo, hi = ratios_real.min(), ratios_real.max()
n_rat = len(ratios_real)
med_uniform = []
mean_uniform = []
for _ in range(10000):
    xs = rng.uniform(lo, hi, n_rat)
    d = delta_min(xs, B)
    med_uniform.append(np.median(d))
    mean_uniform.append(np.mean(d))
med_uniform = np.array(med_uniform)

# ---------- 對照 2: 對數均勻隨機比 (質量比天然 log 分佈) ----------
med_log = []
for _ in range(10000):
    xs = np.exp(rng.uniform(np.log(lo), np.log(hi), n_rat))
    d = delta_min(xs, B)
    med_log.append(np.median(d))
med_log = np.array(med_log)

# ---------- 統計 ----------
p_uniform = (med_uniform <= np.median(d_real)).mean()
p_log = (med_log <= np.median(d_real)).mean()
z_uniform = (np.median(d_real) - med_uniform.mean()) / med_uniform.std()
z_log = (np.median(d_real) - med_log.mean()) / med_log.std()

print(f"\n=== 對照 (10000 次, 每次 {n_rat} 個隨機比) ===")
print(f"均勻隨機 δ_min 中位數分佈: {med_uniform.mean():.5f} ± {med_uniform.std():.5f}")
print(f"對數隨機 δ_min 中位數分佈: {med_log.mean():.5f} ± {med_log.std():.5f}")
print(f"真實 δ_min 中位數:          {np.median(d_real):.5f}")
print(f"\n均勻對照: p(真實≤隨機) = {p_uniform:.4f}, z = {z_uniform:+.2f}σ")
print(f"對數對照: p(真實≤隨機) = {p_log:.4f}, z = {z_log:+.2f}σ")

# ---------- KS 檢驗: 真實 δ_min 分佈 vs 單次大樣本對照 ----------
xs_big = rng.uniform(lo, hi, 100000)
d_big = delta_min(xs_big, B)
ks = stats.ks_2samp(d_real, d_big)

print(f"\nKS 檢驗 (真實 vs 10⁵ 均勻比): D = {ks.statistic:.4f}, p = {ks.pvalue:.4f}")

# ---------- 判決 ----------
# 盲測判據: 如果質量比真係由拍頻產生, δ_min 中位數應顯著細過隨機 (p<0.01)
# 但 946 拍頻密佈 → 預期就算無物理, p 都可能細 (密度效應)
# 所以真正判據: p 對照 log 分佈 (質量比物理分佈) 先準
verdict_uniform = "✅ 質量比傾向近拍頻" if p_uniform < 0.01 else "🟡 無顯著吸引力"
verdict_log = "✅ 質量比傾向近拍頻" if p_log < 0.01 else "🟡 無顯著吸引力"

print(f"\n判決 (均勻對照): {verdict_uniform}")
print(f"判決 (對數對照): {verdict_log}")

# 附加: 最接近嘅匹配表 (報告, 但唔作證據)
print(f"\n=== 最接近拍頻匹配 (僅報告, 非證據) ===")
order = np.argsort(d_real)
for k in order[:10]:
    i = np.searchsorted(B, ratios_real[k])
    nearest = B[i] if abs(B[i]-ratios_real[k]) < abs(B[i-1]-ratios_real[k]) else B[i-1]
    print(f"  {ratio_pairs[k][0]}/{ratio_pairs[k][1]} = {ratios_real[k]:.6f}  → 拍頻 {nearest:.6f}  δ={d_real[k]:.2e}")

res = {
    "n_ratios": int(n_rat),
    "beat_range": [float(B.min()), float(B.max())],
    "real_median_dmin": float(np.median(d_real)),
    "uniform_null": {"mean": float(med_uniform.mean()), "std": float(med_uniform.std()),
                     "p": float(p_uniform), "z": float(z_uniform)},
    "log_null": {"mean": float(med_log.mean()), "std": float(med_log.std()),
                 "p": float(p_log), "z": float(z_log)},
    "ks": {"D": float(ks.statistic), "p": float(ks.pvalue)},
    "verdict_uniform": verdict_uniform,
    "verdict_log": verdict_log,
}
# ============================================================
# ★ L2b: γ-ratio 盲測 — 混合角觀測值 vs γ_a/(γ_a+γ_b) 集合
# IDCM 聲稱 (O65): 混合角 sin²θ = γ-ratio (rank-1 Yukawa 結構推出,
# 先驗鎖定公式, 唔係後驗搜索). 測試: 混合角觀測值係咪傾向近 γ-ratio?
# ============================================================
G = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, N+1)])  # γ_n
g_ratios = []
for a in range(N):
    for b in range(N):
        if a != b:
            g_ratios.append(G[a]/(G[a]+G[b]))
g_ratios = np.array(sorted(g_ratios))
print(f"\nγ-ratio 集合: {len(g_ratios)} 值, 範圍 [{g_ratios.min():.4f}, {g_ratios.max():.4f}]")

# O65 先驗鎖定嘅混合角預言 (由 rank-1 Yukawa + Z₂ 投影推出, 唔係搜索)
MIXING = [
    ("sin²θ₁₂ (PMNS)", 0.303,  "γ₂/(γ₂+γ₃)",  G[1]/(G[1]+G[2])),
    ("sin²θ₂₃ (PMNS)", 0.572,  "γ₇/(γ₇+γ₆)",  G[6]/(G[6]+G[5])),
    ("sin²θ₁₃ (PMNS)", 0.02203,"γ₆/2³",       G[5]/8),
    ("λ (CKM)",        0.225,  "(γ₆/16)^(1/3)", (G[5]/16)**(1/3)),
]
print("\n=== O65 先驗鎖定混合角預言 (結構推出, 非搜索) ===")
ok_priori = 0
for name, obs, formula, pred in MIXING:
    dev = abs(pred-obs)/obs*100
    ok = dev < 5.0
    ok_priori += ok
    print(f"  {name:16s} 預言={pred:.5f} 觀測={obs:.5f} 偏差={dev:.2f}%  {'✅' if ok else '🔴'}")

# γ-ratio 盲測: 4 個混合角觀測值 vs γ-ratio 集合 δ_min
d_mix = delta_min(np.array([m[1] for m in MIXING]), g_ratios)
med_mix = np.median(d_mix)
med_mix_null = []
for _ in range(10000):
    xs = rng.uniform(0, 1, len(MIXING))
    med_mix_null.append(np.median(delta_min(xs, g_ratios)))
med_mix_null = np.array(med_mix_null)
p_mix = (med_mix_null <= med_mix).mean()
z_mix = (med_mix - med_mix_null.mean())/med_mix_null.std()
print(f"\nγ-ratio 盲測: 真實混合角 δ_min 中位數 = {med_mix:.5f}")
print(f"  隨機對照: {med_mix_null.mean():.5f} ± {med_mix_null.std():.5f}")
print(f"  p(真實≤隨機) = {p_mix:.4f}, z = {z_mix:+.2f}σ")

res.update({
    "gamma_ratio_blind": {
        "n": len(g_ratios),
        "real_median_dmin": float(med_mix),
        "null": {"mean": float(med_mix_null.mean()), "std": float(med_mix_null.std()),
                 "p": float(p_mix), "z": float(z_mix)},
        "verdict": "✅ 顯著吸引力" if p_mix < 0.05 else "🟡 無顯著",
    },
    "o65_priori_locked": {
        "n_pass": ok_priori, "n_total": len(MIXING),
        "pass": ok_priori == len(MIXING),
    },
})
print(f"\nO65 先驗鎖定: {ok_priori}/{len(MIXING)} 閉合 (<5%)")
print(f"γ-ratio 盲測判決: {'✅ 混合角顯著傾向 γ-ratio' if p_mix<0.05 else '🟡 樣本太少 (4 點), 無法判定'}")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
def _default(o):
    if hasattr(o, "item"):
        try: return o.item()
        except Exception: pass
    if isinstance(o, (np.bool_, np.integer)): return bool(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.ndarray): return o.tolist()
    raise TypeError(type(o))
with open(OUT, "w") as f:
    json.dump(res, f, indent=2, default=_default)
print(f"\n結果: {OUT}")
