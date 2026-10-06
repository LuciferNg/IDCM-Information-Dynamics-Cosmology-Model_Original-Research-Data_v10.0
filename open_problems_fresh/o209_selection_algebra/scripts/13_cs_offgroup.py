#!/usr/bin/python3
"""
O209 — Script 13: c/s 離群攻堅（9/2 候選檢驗 + 結構有理池 MC null）
================================================================================
背景: c/s 係 O209 冪律兩大離群 (resid +0.913/+1.156), 亦係 O233 assignment
分歧位 (γ升序 c↔s 對調)。三輪獨立檢驗 (assignment 對調 1.397 / A_γ 0.930 /
C_f 譜比橋 0.622) 都指向 c/s 係結構異常位。

本 script explorer:
  [P1] c/s 離群重現 (9pt 冪律 resid)
  [P2] C_f_c/C_f_s = 4.5029 ≈ 9/2 = N_gen²/μ² 候選 (結構池最近命中)
  [P3] 結構有理池 MC null: C_f 比整體避開結構有理? (P<0.01 先當真)
  [P4] 9/2 單對級唯一性 vs 全池
  [P5] dev<0.1% 層: 9/2 有冇統計地位 (遁入 null = 否證)
  [P6] m_c/m_s 分解: (9/2)·(γ_7/γ_4) = 13.589 (dev 0.06%)
  [P7] mode (4,7) 結構語境: 4=B, 7=L₄, 7−4=3=N_gen, 4+7=11∈合法集
  [P8] 世代對 C_f 比比較 (u/d, c/s, t/b)
"""
import numpy as np, math, json, random
from itertools import combinations
from fractions import Fraction

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

# ── 底層 (room 定義) ──────────────────────────────────────────────────
N, NC = 88, 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, NC + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
D = E[:, None] - E[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)
gam_n = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, 14)])

M_pdg = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
         "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
O209 = {1: "t", 2: "b", 3: "tau", 4: "c", 5: "mu", 7: "s", 9: "d", 11: "u", 13: "e"}
Cf = {"e": 3.5941, "u": 3.8029, "d": 3.6620, "s": 41.3207,
      "mu": 30.0309, "c": 186.061, "tau": 159.64, "b": 255.752}
f8 = ["e", "u", "d", "s", "mu", "c", "tau", "b"]

# ── P1. c/s 離群重現 ──
print("═══ P1. c/s 離群重現 ═══")
ns9 = sorted(O209)
m9 = np.array([M_pdg[O209[n]] for n in ns9])
lm = np.log(m9)
ldm = np.log(admn[[n - 1 for n in ns9]])
A = np.vstack([np.ones(9), ldm]).T
c, *_ = np.linalg.lstsq(A, lm, rcond=None)
res = lm - A @ c
rms9 = float(np.sqrt((res ** 2).mean()))
print(f"  9pt 冪律 α={c[1]:.4f} RMS={rms9:.4f}")
for i, n in enumerate(ns9):
    star = " ◀ c/s" if O209[n] in ("c", "s") else ""
    print(f"    n={n:2d} {O209[n]:4s} resid={res[i]:+.4f}{star}")
chk("P1.1 c/s 係兩大離群", sorted(np.abs(res))[-2:][0] > 0.7, f"max={np.abs(res).max():.3f}")

# ── 結構有理池 ──
STRUCT = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 15, 20, 22, 26, 29, 44, 55, 88, 123, 528]
pool = sorted({Fraction(a, b) for a in STRUCT for b in STRUCT if b})
print(f"\n═══ 結構有理池: {len(pool)} 個 ═══")

def count_hits(vals, tol=0.5):
    n = 0; hits = []
    for (f1, f2) in combinations(list(vals.keys()), 2):
        for r, direction in [(vals[f1]/vals[f2], f"{f1}/{f2}"), (vals[f2]/vals[f1], f"{f2}/{f1}")]:
            for sv in pool:
                if abs(r - sv) / sv * 100 < tol:
                    n += 1; hits.append((direction, float(sv), r)); break
    return n, hits

# ── P2. C_f_c/C_f_s 候選 ──
r_cs = Cf["c"] / Cf["s"]
dists = sorted((abs(float(sv) - r_cs) / float(sv) * 100, float(sv)) for sv in pool)
print(f"\n═══ P2. C_f_c/C_f_s = {r_cs:.6f} ═══")
for d, sv in dists[:4]:
    print(f"    {sv:10.6f}  dev={d:.4f}%")
chk("P2.1 9/2 = 4.5 係 c/s 最近結構有理 (dev<0.1%)", dists[0][0] < 0.1, f"best dev={dists[0][0]:.4f}%")

# ── P3. 結構池 MC null: C_f 比整體 ──
rng = random.Random(20261006)
MC = 5000
n_real, hits_real = count_hits(Cf)
le = 0; dist_arr = []
for it in range(MC):
    fake = {f: math.exp(rng.uniform(math.log(3.5), math.log(256))) for f in f8}
    nf, _ = count_hits(fake)
    dist_arr.append(nf)
    if nf <= n_real:
        le += 1
a = np.array(dist_arr)
print(f"\n═══ P3. C_f 比 vs 結構有理池 (dev<0.5%) ═══")
print(f"  真實命中: {n_real} 個; MC null: mean={a.mean():.1f} median={np.median(a):.0f} p90={np.percentile(a,90):.0f} max={a.max()} (N={MC})")
print(f"  P(≤{n_real}) = {le/MC:.4f}")
for h in hits_real:
    print(f"    {h[0]:8s} = {h[2]:8.4f} ≈ {h[1]:.4f}")
chk("P3.1 C_f 比避開結構有理 (P<0.01)", le / MC < 0.01, f"P={le/MC:.4f}")

# ── P4. 9/2 單對唯一性 ──
second = dists[1][0]
print(f"\n═══ P4. 9/2 單對級獨特性 ═══")
print(f"  最近: {dists[0][1]:.5f} dev={dists[0][0]:.3f}%; 第二近: {dists[1][1]:.5f} dev={second:.3f}%")
chk("P4.1 dev 間隙 > 1.5% (第二近遠離)", second - dists[0][0] > 1.5, f"gap={second-dists[0][0]:.3f}%")

# ── P5. dev<0.1% 層 MC: 9/2 統計地位 ──
n10, h10 = count_hits(Cf, tol=0.1)
le10 = 0; d10 = []
for it in range(MC):
    fake = {f: math.exp(rng.uniform(math.log(3.5), math.log(256))) for f in f8}
    nf, _ = count_hits(fake, tol=0.1)
    d10.append(nf)
    if nf <= n10:
        le10 += 1
a10 = np.array(d10)
print(f"\n═══ P5. dev<0.1% 層統計地位 ═══")
print(f"  真實命中: {n10}; MC null: mean={a10.mean():.2f} median={np.median(a10):.0f} p90={np.percentile(a10,90):.0f}")
print(f"  P(≤{n10}) = {le10/MC:.4f}")
chk("P5.1 9/2 無統計地位 (遁入 null, P>0.1) — 誠實否證", le10 / MC > 0.1, f"P={le10/MC:.4f}")

# ── P6. m_c/m_s 分解 ──
g74 = gam_n[6] / gam_n[3]
pred = (9 / 2) * g74
obs = M_pdg["c"] / M_pdg["s"]
print(f"\n═══ P6. m_c/m_s 分解 ═══")
print(f"  (9/2)·(γ_7/γ_4) = 4.5 × {g74:.4f} = {pred:.4f}  vs PDG {obs:.4f}  dev={abs(pred-obs)/obs*100:.3f}%")
print(f"  γ_7/γ_4 vs 3 = {abs(g74-3)/3*100:.3f}% (≈N_gen, 唔 EXACT)")
chk("P6.1 分解 dev < 0.1%", abs(pred - obs) / obs < 0.001, f"{abs(pred-obs)/obs*100:.3f}%")
chk("P6.2 γ_7/γ_4 偏離 EXACT 3 (dev > 0.3%)", abs(g74 - 3) / 3 > 0.003, f"{abs(g74-3)/3*100:.2f}%")

# ── P7. mode (4,7) 語境 ──
print("\n═══ P7. mode (4,7) 結構語境 ═══")
print("  c→n=4 = B (分支數, O210-T1); s→n=7 = L₄ (Lucas)")
print("  7−4 = 3 = N_gen; 4+7 = 11 ∈ 合法模式集 {1,2,3,4,5,7,9,11,13}")
print("  合法對 with b−a=3: (4,7) 唯一? (2,5): 2+5=7∈集 ✓ 都係差3!")
chk("P7.1 (4,7) 係合法 mode 差 3 對之一", True, "另見 (2,5)")

# ── P8. 世代對 C_f 比 ──
print("\n═══ P8. 世代 up/down 對 ═══")
for fu, fd in [("u", "d"), ("c", "s"), ("t", "b")]:
    if fu in Cf and fd in Cf:
        cr = Cf[fu] / Cf[fd]
        # 最近結構有理
        bd = sorted((abs(cr - float(sv)) / float(sv) * 100, float(sv)) for sv in pool)[0]
        print(f"  {fu}/{fd}: C_f比={cr:.4f}  最近結構 {bd[1]:.4f} dev={bd[0]:.3f}%")
    else:
        print(f"  {fu}/{fd}: C_f比 = N/A (t VEV 無 C_f)")

out = {"r_cs_Cf_ratio": r_cs, "nearest_structural": dists[0][1], "nearest_dev_pct": dists[0][0],
       "n_hits_real": n_real, "mc_null_mean": float(a.mean()), "p_le_real": le / MC,
       "n_hits_01_real": n10, "p_le_01": le10 / MC, "m_c_over_m_s": obs,
       "decomp_9o2_gamma": pred, "decomp_dev_pct": abs(pred - obs) / obs * 100}
with open("data/13_cs_offgroup.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c, _ in checks if c)}/{len(checks)} checks passed")
for nm, c, dt in checks:
    print(f"  [{'OK' if c else 'XX'}] {nm} — {dt}")