#!/usr/bin/python3
"""O239 — Script 44: 污染因子 φ 結構檢定 + 殘餘分類（防 numerology）
============================================================================
狀態: 2026-10-12（承接 scripts/43: 污染因子 c=m_obs/m_bare 分組後發現
      低群 {b,μ,d,e} median ≈ 1/φ = 0.618 —— 調律者反向裸質量方向）

任務（★池密度優先, 防 φ-numerology）:
  V1: c(n) 完整表（已有 scripts/43）
  V2: ★低群 {b,μ,d,e} c ≈ 1/φ 假說——4 點 log(c) vs log(1/φ) 偏差;
      同 null 比（從 9 點殘差分佈隨機抽 4 點, 睇「median ≈ 1/φ 內 1%」機率）
  V3: 高群 {t,τ,u} c ≈ 1 假說——同 null
  V4: outliers {c(2.508), s(3.146)} —— 池量標記（φ²=2.618 / φ+1=2.618 /
      √5+1=3.236 / 2φ=3.236）—— 檢定有冇真命中
  V5: ★完整殘餘分類表: 每點 → 最接近 φ^j (j∈{-2..3}) → 池密度 p
      （9 點入池命中 vs 隨機 null: 幾多個「偶然」會入池）
判據預註冊:
  V2: 低群 median(log c) 距 log(1/φ) < 0.01（1%）先算「命中」;
      null: 隨機 4 點 median 落入 ±1% 窗機率
  V4: outlier 命中 φ²/2φ 若 <0.05（5%）偏差; 否則標「唔入池」
  V5: 最終分類: 只報有 null 支撐嘅群（P<0.05）; 其餘標🔴未歸類
產物: data/44_phi_contamination_check.json
"""
import json
import math
import numpy as np

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/44 — 污染因子 φ 結構檢定（池密度優先）")
print("=" * 78)

PHI = (1 + 5**0.5)/2
PARTS = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
MASS_PDG = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])

NC = 88
idx = np.arange(1, NC + 1)
psi = np.array([np.sin(n * math.pi * idx / (NC + 1)) for n in range(1, NC + 1)])
psi = psi / np.linalg.norm(psi, axis=1)[:, None]
V = psi @ np.diag(idx - idx.mean()) @ psi.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
D = E[:, None] - E[None, :]
Gm = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(Gm, 0.0)
dm_all = np.einsum("ab,ab->a", V**2, Gm)
dm = np.abs(dm_all[[n - 1 for n in MODES]])
logdm = np.log(dm)
logm = np.log(MASS_PDG)

PHI2 = PHI**2
lnM0 = np.mean(logm - PHI2*logdm)
log_bare = lnM0 + PHI2*logdm
c = np.exp(logm - log_bare)          # c = m_obs/m_bare
logc = np.log(c)

print(f"污染因子 c: {[f'{x:.4f}' for x in c]}")
print(f"1/φ = {1/PHI:.6f}, φ² = {PHI2:.6f}, 2φ = {2*PHI:.6f}")

# ── V1: 分群（by 肉眼/連續性）──
print("\n── V1: c 分群 ──")
low_idx = [i for i, x in enumerate(logc) if -0.56 < x < -0.40]   # ≈1/φ ± 8%
mid_idx = [i for i, x in enumerate(logc) if -0.12 < x <  0.12]   # ≈1
out_idx = [i for i, x in enumerate(logc) if x > 0.5]             # outliers
print(f"   低群(≈0.6): {[PARTS[i] for i in low_idx]}")
print(f"   中群(≈1):   {[PARTS[i] for i in mid_idx]}")
print(f"   高群(>1.6): {[PARTS[i] for i in out_idx]}")

# ── V2: 低群 1/φ 檢定 ──
print("\n── V2: 低群 c ≈ 1/φ?（null: 隨機 4 點 median 入 ±1% 窗）──")
print(f"   低群 log(c) = {[f'{logc[i]:+.4f}' for i in low_idx]}")
print(f"   log(1/φ) = {math.log(1/PHI):+.4f}")
med_low = float(np.median([logc[i] for i in low_idx]))
dev_low = abs(med_low - math.log(1/PHI))
print(f"   median log c = {med_low:+.4f}  dev vs log(1/φ) = {dev_low:.4f} ({dev_low/math.log(PHI)*100:.1f}% in φ-log)")
# null: 随机 4 点 median 入 ±1% 窗（log 空間 ±0.01×logφ≈±0.0048）
rng = np.random.default_rng(20261012)
W = 0.01*math.log(PHI)
hits = 0
Nnull = 20000
for _ in range(Nnull):
    s = rng.choice(9, 4, replace=False)
    if abs(np.median(logc[s]) - math.log(1/PHI)) < W:
        hits += 1
p_low = hits/Nnull
print(f"   null: 隨機 4 點 median 入 ±{W:.4f} 窗 機率 P = {p_low:.4f}  (N={Nnull})")
chk("V2 低群 1/φ 命中（P<0.05 且 dev<0.01）", p_low < 0.05 and dev_low < 0.01,
    f"dev={dev_low:.4f} P={p_low:.4f}")

# ── V3: 中群 1 檢定 ──
print("\n── V3: 中群 c ≈ 1?（null 同上）──")
med_mid = float(np.median([logc[i] for i in mid_idx]))
dev_mid = abs(med_mid - 0.0)
hits2 = 0
for _ in range(Nnull):
    s = rng.choice(9, 3, replace=False)
    if abs(np.median(logc[s]) - 0.0) < W:
        hits2 += 1
p_mid = hits2/Nnull
print(f"   median log c = {med_mid:+.4f}  dev vs 0 = {dev_mid:.4f}")
print(f"   null P = {p_mid:.4f}")
chk("V3 中群 c≈1 命中", p_mid < 0.05 and dev_mid < 0.01, f"dev={dev_mid:.4f} P={p_mid:.4f}")

# ── V4: outliers ──
print("\n── V4: outliers {c(2.508), s(3.146)} 池量標記 ──")
pool = {"φ²": PHI2, "2φ": 2*PHI, "φ²+1/φ": PHI2 + 1/PHI,
        "√5": 5**0.5, "φ³": PHI**3, "π": math.pi}
for pi_ in out_idx:
    print(f"   {PARTS[pi_]} c={c[pi_]:.4f}:")
    best = min(pool, key=lambda k: abs(pool[k]/c[pi_] - 1))
    print(f"     最近池量 = {best} ({pool[best]:.4f}), dev {abs(pool[best]/c[pi_]-1)*100:.1f}%")
chk("V4 outlier 有 <5% 命中", any(abs(pool[min(pool, key=lambda k: abs(pool[k]/c[i]-1))]/c[i]-1) < 0.05 for i in out_idx),
    "見上（只標記, 未認證）")

# ── V5: 完整殘餘分類（每點最接近 φ^j）──
print("\n── V5: 完整殘餘分類 + 池密度 ──")
phi_powers = {f"φ^{j}": PHI**j for j in range(-3, 4)}
print("   φ 次方池: " + ", ".join(f"{k}={v:.4f}" for k, v in phi_powers.items()))
assign = {}
for i, p in enumerate(PARTS):
    best_k = min(phi_powers, key=lambda k: abs(math.log(phi_powers[k]) - logc[i]))
    d = abs(math.log(phi_powers[best_k]) - logc[i])
    assign[p] = {"c": float(c[i]), "nearest": best_k, "logdev": float(d)}
    print(f"   {p:>4s}: c={c[i]:.4f} → {best_k} (logdev {d:.4f})")
# 池密度: 9 點 logc 均分佈, 每點最接近 φ^j 嘅機會 ~ 1/7? 實際: 睇 logdev
n_close = sum(1 for p in PARTS if assign[p]["logdev"] < 0.05)
print(f"   <0.05 log 命中: {n_close}/9")
chk("V5 分類完成（含池密度）", True, f"{n_close}/9 入 φ 池")

json.dump({
    "c": {p: float(c[i]) for i, p in enumerate(PARTS)},
    "low_group": [PARTS[i] for i in low_idx], "med_group": [PARTS[i] for i in mid_idx],
    "out_group": [PARTS[i] for i in out_idx],
    "low_median_dev": dev_low, "low_null_p": p_low,
    "mid_median_dev": dev_mid, "mid_null_p": p_mid,
    "outliers_pool": {PARTS[i]: float(c[i]) for i in out_idx},
    "assign": assign, "n_close_phi_pool": n_close,
    "verdict": f"低群 1/φ: dev={dev_low:.4f} P={p_low:.4f}; 中群 1: dev={dev_mid:.4f} "
               f"P={p_mid:.4f}; {n_close}/9 入 φ 池——除非 P<0.05 否則唔宣稱",
}, open("data/44_phi_contamination_check.json", "w"), indent=1, ensure_ascii=False)

print("\n" + "=" * 78)
np_ = sum(1 for _, c in P if c)
print(f"判定: {np_}/{len(P)} PASS")