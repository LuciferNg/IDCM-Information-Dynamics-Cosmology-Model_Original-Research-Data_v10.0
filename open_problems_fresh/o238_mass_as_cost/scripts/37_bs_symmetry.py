#!/usr/bin/python3
"""O238 — Script 37: b/s 對稱離群檢定 — 跨 scheme 穩健性 + MC null

R21 發現: rank-parity 過後 b −0.805 / s +0.798, b+s=−0.007≈0 EXACT。
構造意義: m_s·m_b (乘積) 被模型預測 <1% 誤差, 但各自 ±120%。

本 script:
P1 三 scheme (S1/S2/S3) 下 rank 修正後 b/s 對稱是否保持
P2 b+s 精確度 (每 scheme)
P3 乘積守恆: (m_s·m_b)_obs/(m_s·m_b)_pred — 誤差%
P4 MC null: 隨機 9 點殘差 (固定 RMS) 出現 |b+s|<0.05 機率
P5 判決: b/s 對稱係咪結構 (唔係單 scheme 偽影 / 唔係隨機)
"""
import numpy as np, math, json

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

N = 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, N + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
D = E[:, None] - E[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2

# 三 scheme (scripts/08 原版)
SETS = {
    "S1_v11": {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
               "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
               "c": 93.4*11.652, "b": 93.4*11.652*3.291, "t": 172690.0},
    "S2_v2_3GeV": {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
                   "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
                   "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0},
    "S3_v2_RGI": {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
                  "u": 2.97, "d": 6.53, "s": 130.0, "c": 1484.2, "b": 6938.0, "t": 172690.0},
}

logd = np.log([admn[n-1] for n in SEL9])
rank = np.arange(1, 10)
even_mask = (rank % 2 == 0).astype(float)

def rank_resid(mset):
    logm = np.log([mset[p] for p in names9])
    A = np.vstack([np.ones(9), logd, even_mask]).T
    c, *_ = np.linalg.lstsq(A, logm, rcond=None)
    res = logm - A @ c
    return c, res

results = {}
print("═══ P1. 三 scheme rank 修正後 b/s 對稱 ═══")
for nm, m in SETS.items():
    c, res = rank_resid(m)
    rb, rs = res[names9.index("b")], res[names9.index("s")]
    ssum = rb + rs
    # 乘積守恆
    ms_obs, mb_obs = m["s"], m["b"]
    ms_pred = math.exp(c[0] + c[1]*logd[names9.index("s")] + c[2]*even_mask[names9.index("s")])
    mb_pred = math.exp(c[0] + c[1]*logd[names9.index("b")] + c[2]*even_mask[names9.index("b")])
    prod_err = (ms_obs*mb_obs)/(ms_pred*mb_pred) - 1
    results[nm] = {"res_b": float(rb), "res_s": float(rs), "sum": float(ssum),
                   "alpha": float(c[1]), "delta": float(c[2]),
                   "prod_err_pct": float(prod_err*100),
                   "ms_obs": ms_obs, "mb_obs": mb_obs,
                   "ms_pred": float(ms_pred), "mb_pred": float(mb_pred)}
    print(f"  {nm:12s}: b={rb:+.4f} s={rs:+.4f} b+s={ssum:+.4f} | 乘積誤差={prod_err*100:+.3f}%")

chk("P1.1 三 scheme b+s 都近零 (<0.05)",
    all(abs(results[nm]["sum"]) < 0.05 for nm in SETS),
    " vs ".join(f"{nm}:{results[nm]['sum']:+.4f}" for nm in SETS))
chk("P1.2 三 scheme 乘積誤差都 <3%",
    all(abs(results[nm]["prod_err_pct"]) < 3.0 for nm in SETS),
    " vs ".join(f"{nm}:{results[nm]['prod_err_pct']:+.3f}%" for nm in SETS))

print("\n═══ P2. b+s 精確度 ═══")
for nm in SETS:
    print(f"  {nm}: b+s = {results[nm]['sum']:+.6f}  乘積誤差 = {results[nm]['prod_err_pct']:+.4f}%")

print("\n═══ P3. α/δ 三 scheme ═══")
for nm in SETS:
    print(f"  {nm}: α={results[nm]['alpha']:.4f} (dev φ² {(results[nm]['alpha']-PHI2)/PHI2*100:+.2f}%)"
          f"  δ={results[nm]['delta']:+.4f}")
chk("P3.1 α 三 scheme 一致 (max dev <5%)",
    max(abs((results[nm]["alpha"]-PHI2)/PHI2) for nm in SETS) < 0.05,
    " vs ".join(f"{nm}:{results[nm]['alpha']:.4f}" for nm in SETS))

print("\n═══ P4. MC null: 隨機殘差出現 |b+s|<0.05 機率 ═══")
rng = np.random.default_rng(237001)
NMC = 100000
rms_ref = math.sqrt(np.mean([rank_resid(SETS["S2_v2_3GeV"])[1]**2]))
count = 0
for _ in range(NMC):
    # 隨機 9 殘差 (高斯, RMS = ref), 抽 b/s 兩點
    r = rng.normal(0, rms_ref, 9)
    if abs(r[names9.index("b")] + r[names9.index("s")]) < 0.05:
        count += 1
p_null = count / NMC
print(f"  參考 RMS = {rms_ref:.4f}")
print(f"  MC: |b+s|<0.05 出現 {count}/{NMC} = {p_null*100:.4f}%")
chk("P4.1 MC null 機率 < 5% (唔係隨機)",
    p_null < 0.05, f"p={p_null*100:.4f}%")
# 更嚴: 要求 s 大正 b 大負 (|r_s|>0.5 且 |r_b|>0.5 且 sum<0.05)
count2 = 0
for _ in range(NMC):
    r = rng.normal(0, rms_ref, 9)
    rb, rs = r[names9.index("b")], r[names9.index("s")]
    if abs(rb) > 0.5 and abs(rs) > 0.5 and abs(rb+rs) < 0.05:
        count2 += 1
p2 = count2 / NMC
print(f"  MC: |b|,|s|>0.5 且 |b+s|<0.05 = {count2}/{NMC} = {p2*100:.6f}%")
chk("P4.2 嚴格條件 (大離群+和零) p < 0.1%",
    p2 < 0.001, f"p={p2*100:.6f}%")

print("\n═══ P5. 判決 ═══")
print(f"  ★三 scheme b+s ≈ 0 保持 (max {max(abs(results[nm]['sum']) for nm in SETS):.4f})")
print(f"  ★乘積守恆 {max(abs(results[nm]['prod_err_pct']) for nm in SETS):+.3f}% (worst)")
print(f"  ★MC null: |b+s|<0.05 = {p_null*100:.4f}%; 嚴格 = {p2*100:.6f}%")
if p2 < 0.001 and max(abs(results[nm]["sum"]) for nm in SETS) < 0.05:
    print("  ⟹ b/s 對稱 = 結構信號 (跨 scheme 穩健 + 非隨機)")
else:
    print("  ⟹ b/s 對稱未能過檢定 (降級為候選)")
chk("P5.1 b/s 對稱 = 結構信號",
    p2 < 0.001 and max(abs(results[nm]["sum"]) for nm in SETS) < 0.05,
    f"p2={p2*100:.6f}%, maxsum={max(abs(results[nm]['sum']) for nm in SETS):.4f}")

out = {"results": results, "rms_ref": float(rms_ref),
       "p_null_loose": float(p_null), "p_null_strict": float(p2),
       "n_mc": NMC}
with open("data/37_bs_symmetry.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")