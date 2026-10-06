#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O234 scripts/02 -- 反推引擎: (n,C) 約束解集 + 枚舉密度 null + s/mud 池掃描 + P2 循環證明

License: IDCM O234. Deterministic, stdlib-only.
PASS/FAIL 只數「可檢驗」層; 池掃描 = 診斷性 (nominal, look-elsewhere 未校正).
"""
import itertools, json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FROZEN = json.load(open(os.path.join(DATA, "01_frozen_observations.json"), encoding="utf-8"))

MODES = [1,2,3,4,5,7,9,11,13]
A_GAMMA = {"e":1, "u":2, "d":3, "s":4, "mu":5, "c":7, "tau":9, "b":11, "t":13}
def gamma(n): return 4.0*math.sin(n*math.pi/88.0)**2
g = {n: gamma(n) for n in MODES}

md_mu11, e_md_mu11 = FROZEN["Nf=2+1+1"]["md_mu_derived"]
ms_mud11, e_ms_mud11 = FROZEN["Nf=2+1+1"]["ms_mud_ratio"]

p = s = 0
def chk(name, ok, detail):
    global p, s
    print(("  PASS " if ok else "  FAIL ") + f"[{name}] {detail}")
    if ok: p += 1
    else:  s += 1

# ---------------------------------------------------------------- §1 反推 (n,C) 約束
print("[1] 反推: 觀測比 R -> 所需 C_i/C_j = R / (gamma_i/gamma_j)  (A_gamma)")
needed = {}
obs = {
    "d/u": (md_mu11, e_md_mu11, 3, 2),        # (obs, err, num_mode, den_mode)
    "c/s": (11.85, 0.16, 7, 4),
    "b/c": (4.18/1.27, (4.18/1.27)*math.hypot(0.03/4.18,0.02/1.27), 11, 7),
    "t/b": (172.57/4.18, (172.57/4.18)*math.hypot(0.29/172.57,0.03/4.18), 13, 11),
}
for name, (r, er, i, j) in obs.items():
    pred = g[i]/g[j]
    cneed = r/pred
    needed[name] = cneed
    print(f"  {name:4s}: obs {r:8.4f} / gamma({i})/gamma({j}) = {pred:.4f} -> 所需 C_i/C_j = {cneed:.4f}")

# 所需 C 比 vs 結構池 ratio (池 = {3.6,13,15.5,33,37,44}; 任何命中 = nominal)
POOL = [3.6, 13.0, 15.5, 33.0, 37.0, 44.0]
pool_ratios = set()
for a, b in itertools.product(POOL, repeat=2):
    if a != b:
        pool_ratios.add(round(a/b, 6))
hits = {name: [r for r in pool_ratios if abs(r-cneed)/cneed < 0.05] for name, cneed in needed.items()}
for name, hh in hits.items():
    print(f"     {name}: 所需 C 比 {needed[name]:.4f}; 結構池 5% 內命中 = {hh if hh else '無'}")
chk("S1a 所需 C 比冇結構池命中 (所有比)", all(len(v) == 0 for v in hits.values()),
    "c/s 所需 3.92 池無命中 (15.5/3.6=4.31 dev 10%); b/c 所需 1.375 近命中 44/33=1.3333 dev 3.0% (nominal, 池成員 44/33 涉 look-elsewhere)")

# ---------------------------------------------------------------- §2 枚舉密度 null (u/d)
band_lo, band_hi = md_mu11 - e_md_mu11, md_mu11 + e_md_mu11
hits72 = []
for i, j in itertools.permutations(MODES, 2):
    r = g[i]/g[j]
    if band_lo <= r <= band_hi:
        hits72.append((i, j, r))
print(f"[2] u/d FLAG 1σ 帶 [{band_lo:.4f}, {band_hi:.4f}]: 72 個有序模式對命中 {hits72}")
pn = len(hits72)/72.0
chk("S2a 命中密度 <= 2/72 (單目標 nominal)", pn <= 2/72,
    f"{len(hits72)}/72 = {pn*100:.1f}%")
ack = any(i == 3 and j == 2 for (i, j, _) in hits72)
chk("S2b A_gamma (3,2) 係命中對之一", ack, "-> 純 γ 鏈譜確實供給 u/d（0.85σ, CHK5）; 但 assignment 選擇本身含 look-elsewhere")

# ---------------------------------------------------------------- §3 s/mud 池掃描 (診斷性)
print("[3] s/mud 池掃描 (診斷性, nominal): FLAG s/mud = 27.227(81) @0.3%")
w = e_ms_mud11/ms_mud11
mall = [27.5, 27.4, 27.4179, 55/2, 54.8358/2, 0.0, 0.0, 0.0]
def poolgen():
    base = [1,2,3,4,5,7,8,11,13,18,21,29,34,44,47,55,76,88,90,123]
    for a, b in itertools.product(base, repeat=2):
        if b == 0: continue
        v = a/b
        if 20 < v < 35:
            yield v
pool_hits = [v for v in poolgen() if abs(v-ms_mud11)/ms_mud11 <= w]
print(f"  候選 {len(set(round(v,4) for v in poolgen()))} 個 (a/b, a,b in 結構集, 20<v<35) 中 1σ 命中: {sorted(set(round(v, 4) for v in pool_hits))}")
cand = [("27.5 = F10/2", 27.5), ("27.4179 = (O233 R20 G3/G1)/2", 27.4179), ("27.4", 27.4)]
for nm, v in cand:
    zz = (v-ms_mud11)/e_ms_mud11
    flag = "命中" if abs(zz) <= 1 else ("邊緣" if abs(zz) <= 3 else "未命中")
    print(f"    {nm:28s} vs 27.227(81): z={zz:+.2f} -> {flag}")
chk("S3a F10/2 未命中 (|z|>3)", abs((27.5-ms_mud11)/e_ms_mud11) > 3,
    f"F10/2 = 27.5 偏 +1.0% = 3.4σ -> FLAG 0.3% 精度下池無明顯命中（方法有牙）")

# ---------------------------------------------------------------- §4 P2 循環證明
print("[4] P2 循環性: C_f = m/(M0*gamma_n) 定義下 gamma*C 恆等還原 m")
m_u, m_d = 2.16, 4.67
Cu = m_u/(27.900915*g[2])
Cd = m_d/(27.900915*g[3])
recon = (g[3]*Cd)/(g[2]*Cu)
circ = abs(recon - m_d/m_u)
chk("S4a gamma*C 還原 = 恆等式 (循環證明)", circ < 1e-12,
    f"(gamma3*C_d)/(gamma2*C_u) - m_d/m_u = {circ:.3e} -> O233 P2 'EXACT' = 定義恆等, 0 檢驗力")
print(f"    C_u = {Cu:.4f}, C_d = {Cd:.4f} (O120 商定義 -> 同 O233 docs/15 3.80/3.66 一致)")

print(f"\n=== {p} PASS / {s} FAIL ===")