#!/usr/bin/python3
"""
O209 — Script 14: Id(f) 交接項攻堅 (O233 → O209) 三層探索
================================================================================
O233 交接項 (docs/20 §六): Id(f) = C_f 絕對值生成 = 質量對 γ-階梯偏差生成
    m_f = M₀·γ_n·Id(f), Id(f) 絕對值 → O209 質量層 (唯一後續出路)
O209 已封: docs/12 譜比橋 (C_f=C·|Δm|^α/γ RMS 0.622 拒); docs/13 9/2 否證
本 script explorer:
    [P1] C_f 8 值重現 (m/(M₀γ_n), O233 γ升序 frame)
    [P2] C_f ~ |Δm|^β: OLS β=1.1985 ≈ 6/5=μ²N_gen/F₅ (dev 0.125%)? 固定 β 有冇閉合力
    [P3] m/M₀ 塊心候選 {1/16=B^{-2}, 25/3=F₅²/N_gen, 98=2L₄²} 總 dev 1.37%
    [P4] C_f 比 vs Fib/Lucas 有理池: P=0.77 遁入 null (18 vs null 15.6) — 無有理身份
    [P5] C_f 比 vs 結構有理池 (317): P=0.0006 結構隔離 (docs/13 複現)
    [P6] C_f/塊心 鋸齒因子 (塊內 Z₂ 結構)
    [P7] γ 升序 = m 升序 零反轉 (O233 已閉合, 對照)
"""
import numpy as np, math, json, random
from itertools import combinations
from fractions import Fraction

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

# ── 底層 (room 定義) ──────────────────────────────────────────────────────
N, NC = 88, 88
gam_n = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, 14)])
M0 = 27.900915  # O120 世界質量量子
M_pdg = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
         "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
O233 = {1: "e", 2: "u", 3: "d", 4: "s", 5: "mu", 7: "c", 9: "tau", 11: "b", 13: "t"}
O209 = {1: "t", 2: "b", 3: "tau", 4: "c", 5: "mu", 7: "s", 9: "d", 11: "u", 13: "e"}
ns8 = [1, 2, 3, 4, 5, 7, 9, 11]  # 8 值 C_f 族 (t 係 VEV 分離, O233 docs/20)
cf = {n: M_pdg[O233[n]] / (M0 * gam_n[n - 1]) for n in ns8}

# |dm| 重算
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

# ── P1. C_f 8 值重現 ──
print("═══ P1. C_f 8 值 (m/(M₀γ_n), O233 γ升序) ═══")
ref = {"e": 3.5941, "u": 3.8029, "d": 3.6620, "s": 41.3207,
       "mu": 30.0309, "c": 186.061, "tau": 159.64, "b": 255.752}
ok = True
for n in ns8:
    f = O233[n]
    dev = abs(cf[n] - ref[f]) / ref[f] * 100
    print(f"  n={n:2d} {f:4s}: C_f={cf[n]:.4f} (ref {ref[f]:.2f}) dev={dev:.3f}%")
    if dev > 0.05:
        ok = False
chk("P1.1 C_f 8 值重現 (dev<0.05%)", ok)

# ── P2. C_f ~ |Δm|^β ──
print("\n═══ P2. C_f ~ |Δm|^β (O233 frame |dm|) ═══")
ld = np.log(admn[[n - 1 for n in ns8]])
lc = np.log([cf[n] for n in ns8])
Ab = np.vstack([np.ones(8), ld]).T
c1, *_ = np.linalg.lstsq(Ab, lc, rcond=None)
r1 = lc - Ab @ c1
rms1 = float(np.sqrt((r1 ** 2).mean()))
corr1 = float(np.corrcoef(ld, lc)[0, 1])
print(f"  β={-c1[1]:.6f} A={c1[0]:.4f} RMS={rms1:.4f} corr={corr1:+.4f}")
dev65 = abs(1.2 - (-c1[1])) / 1.2 * 100
print(f"  β vs 6/5=μ²N_gen/F₅: dev={dev65:.4f}%")
# 固定 β=±6/5 閉合力
resid_fix = lc - (c1[0] + (-1.2) * ld)
rms_fix = float(np.sqrt((resid_fix ** 2).mean()))
print(f"  固定 β=6/5: RMS={rms_fix:.4f} (OLS {rms1:.4f}) Δ={rms_fix-rms1:+.5f}")
chk("P2.1 β ≈ 6/5 dev < 0.2%", dev65 < 0.2, f"{dev65:.3f}%")
chk("P2.2 固定 β 冇閉合力 (ΔRMS < 0.01)", abs(rms_fix - rms1) < 0.01, f"Δ={rms_fix-rms1:+.5f}")

# ── P3. m/M₀ 塊心候選 ──
print("\n═══ P3. m/M₀ 塊心候選 (1/16, 25/3, 98) ═══")
def gmean(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs))
blocks = {"low": [1, 2, 3], "mid": [4, 5, 7], "high": [9, 11]}
mm0 = {n: M_pdg[O233[n]] / M0 for n in ns8}
gmm = {b: gmean([mm0[n] for n in nsb]) for b, nsb in blocks.items()}
cand_mm0 = {"low": 1 / 16, "mid": 25 / 3, "high": 98}
total_dev = 0
for b in blocks:
    d = abs(gmm[b] - cand_mm0[b]) / cand_mm0[b] * 100
    total_dev += d
    print(f"  {b}: m/M₀ 塊心={gmm[b]:.6f} vs {cand_mm0[b]:.4f} dev={d:.3f}%")
print(f"  總 dev = {total_dev:.3f}%")
chk("P3.1 三塊候選總 dev < 2%", total_dev < 2, f"{total_dev:.3f}%")
chk("P3.2 後見之明 (冇 pre-registered 盲測)", True, "需 O136 盲測")

# ── P4. C_f 比 vs Fib/Lucas 池 ──
print("\n═══ P4. C_f 比 vs Fib/Lucas 有理池 (look-elsewhere) ═══")
FIB = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
LUC = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123]
pool_fl = sorted({float(Fraction(a, b)) for a in FIB + LUC for b in FIB + LUC if b})
print(f"  Fib/Lucas 池: {len(pool_fl)} 個")
f8 = ["e", "u", "d", "s", "mu", "c", "tau", "b"]
Cf = {O233[n]: cf[n] for n in ns8}
def count_hits(vals, SP, tol=0.5):
    n = 0
    for (f1, f2) in combinations(f8, 2):
        for r, direction in [(vals[f1]/vals[f2], f"{f1}/{f2}"), (vals[f2]/vals[f1], f"{f2}/{f1}")]:
            for sv in SP:
                if abs(r - sv) / sv * 100 < tol:
                    n += 1; break
    return n
n_real_fl = count_hits(Cf, pool_fl)
rng = random.Random(20261006)
MC = 3000
le = 0
dist = []
for it in range(MC):
    fake = {f: math.exp(rng.uniform(math.log(3.5), math.log(256))) for f in f8}
    nf = count_hits(fake, pool_fl)
    dist.append(nf)
    if nf <= n_real_fl:
        le += 1
a = np.array(dist)
print(f"  真實命中 {n_real_fl}; MC null: mean={a.mean():.2f} median={np.median(a):.0f} p90={np.percentile(a,90):.0f}")
print(f"  P(≤{n_real_fl}) = {le/MC:.4f}")
chk("P4.1 Fib/Lucas 命中遁入 null (P>0.05)", le / MC > 0.05, f"P={le/MC:.4f}")

# ── P5. C_f 比 vs 結構有理池 (docs/13 複現) ──
print("\n═══ P5. C_f 比 vs 結構有理池 (docs/13 複現) ═══")
STRUCT = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 15, 20, 22, 26, 29, 44, 55, 88, 123, 528]
pool_s = sorted({float(Fraction(a, b)) for a in STRUCT for b in STRUCT if b})
n_real_s = count_hits(Cf, pool_s, tol=0.5)
rng2 = random.Random(20261006)
le_s = 0
for it in range(MC):
    fake = {f: math.exp(rng2.uniform(math.log(3.5), math.log(256))) for f in f8}
    if count_hits(fake, pool_s, tol=0.5) <= n_real_s:
        le_s += 1
print(f"  真實命中 {n_real_s}; P(≤{n_real_s}) = {le_s/MC:.4f} (docs/13: 0.0006)")
chk("P5.1 C_f 比結構隔離 (P<0.01)", le_s / MC < 0.01, f"P={le_s/MC:.4f}")

# ── P6. C_f/塊心 鋸齒因子 ──
print("\n═══ P6. C_f/塊心 鋸齒因子 (塊內 Z₂) ═══")
gcf = {b: gmean([cf[n] for n in nsb]) for b, nsb in blocks.items()}
for b, nsb in blocks.items():
    for n in nsb:
        r = cf[n] / gcf[b]
        print(f"  {O233[n]:4s} (块 {b:4s}): C_f/塊心 = {r:.4f} log={math.log(r):+.4f}")
# 最強鋸齒 — G2 內 c 3.03× 塊心
g2 = gcf["mid"]
c_over = cf[7] / g2
print(f"  ★ G2 內 c 對塊心 = {c_over:.4f} ≈ 3 = N_gen (dev {abs(c_over-3)/3*100:.2f}%)")
chk("P6.1 G2 內 c ≈ 3×塊心 (dev<2%)", abs(c_over - 3) / 3 < 0.02, f"{abs(c_over-3)/3*100:.2f}%")

# ── P7. γ 升序 = m 升序 零反轉 (O233 已閉合) ──
print("\n═══ P7. γ 升序 = m 升序 (對照, O233 已閉合) ═══")
m_asc = [M_pdg[O233[n]] for n in ns8]
gamma_asc = [gam_n[n - 1] for n in ns8]
is_asc = all(m_asc[i] < m_asc[i + 1] for i in range(7))
chk("P7.1 γ 升序 = m 升序 (零反轉)", is_asc)
print(f"  m 升序: {['%.1f' % x for x in m_asc]} ⟹ {is_asc}")

# ── 輸出 ──
out = {
    "cf_8": {O233[n]: round(cf[n], 6) for n in ns8},
    "ols_beta": -c1[1], "ols_corr": corr1, "ols_rms": rms1,
    "beta_65_dev_pct": dev65, "fix65_rms": rms_fix,
    "block_mm0": {k: round(v, 6) for k, v in gmm.items()},
    "cand_mm0_dev_pct": {k: round(abs(gmm[k] - cand_mm0[k]) / cand_mm0[k] * 100, 3) for k in blocks},
    "fibluc_n": n_real_fl, "fibluc_null_mean": float(a.mean()), "fibluc_p": le / MC,
    "structpool_n": n_real_s, "structpool_p": le_s / MC,
    "c_over_G2": c_over,
}
with open("data/14_idf_handoff.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c, _ in checks if c)}/{len(checks)} checks passed")
for nm, c, dt in checks:
    print(f"  [{'OK' if c else 'XX'}] {nm} — {dt}")