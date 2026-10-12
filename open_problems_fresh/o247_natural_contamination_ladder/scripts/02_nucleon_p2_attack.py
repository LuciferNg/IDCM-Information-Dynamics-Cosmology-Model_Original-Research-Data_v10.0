#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""O247 Q2 攻堅 02 — P2 路: 節點+束縛能量 池密度 + 雙項式家族 (判據預註冊)

docs/01 §二 Q2 活路 = P2 (節點質量 m_uud + 色磁通束縛能量 E_bind) + glueball 交叉。
快閘 (scripts/01) 已否決 5 個核子單量 (全部池密度 FAIL) ⟹ 本 script 轉向:
  - 節點質量 (單項 M₀γ₁×64, 已知 1.2%)
  - 束縛能量 E_bind_p/n (單量, 池密度重測)
  - ★ 雙項式家族 m = M₀(a − b·γ₁)  (a,b ∈ 結構數池) — 候選: m_n ≈ 34M₀ − m_uud
    (M₀(34 − 64γ₁) = 939.53 vs 939.565, 初測 dev 0.0035%) — 必須過 2-DOF MC null
  - glueball 交叉: X(2370)/M₀ = 84.94 (85=5×17 已撤回 docs/03) — 掃其他候選

判據 (預註冊, 凍結):
  G1 節點: m_uud_pred = M₀γ₁×64 vs m_uud_obs = 2m_u+m_d (PDG) — dev < 2% : PASS
  G2 束縛能: E_bind_p/n/M₀ 對 scripts/01 同池掃 1% 窗 + MC null (N=10000) — z≥5 先候選
  G3 ★ 雙項式家族: 對 m_n/M₀, m_p/M₀ 掃 (a,b) ∈ P_int² (a,b≤200), δ=0.1% 窗;
     MC null = 同家族同窗抽 log-uniform r∈[0.5,50] × 10000 → z≥5 先升候選, 否則否決
  G4 glueball: 2370/M₀ 對同池 1% 窗 + MC null; 85 候選 (已撤回) 必須標禁區
  G5 三點檢定: 只有 z≥5 雙項式先檢查喺第二個核子量 (m_p) 有冇同形式命中

池定義: 同 scripts/01 (P_int ∪ P_lucas ∪ P_fib ∪ P_phi ∪ 有理 ∪ k/88), 池規模 log 記低
γ₁ = 4sin²(π/88)  (O36 正典)
"""
import math
import numpy as np

DELTA = 0.01       # 單量窗 (1%)
DELTA2 = 0.001     # 雙項式窗 (0.1%, 因為 2-DOF 密度高)
MC_N = 10000
Z_GATE = 5.0
Z_LINE = 3.0
logmin, logmax = 0.5, 50.0

# ---- 結構池 (同 scripts/01) ----
P_int = set(range(1, 21)) | {22, 29, 30, 33, 34, 37, 42, 44, 45, 47, 55, 60, 61, 62,
                             64, 68, 70, 71, 76, 79, 85, 86, 88, 89, 90, 123, 137,
                             178, 199, 233, 264, 322, 377, 521, 528, 610, 843,
                             1364, 1547, 1554}
phi = (1 + math.sqrt(5)) / 2
pool = set(P_int) | {phi ** k for k in range(-5, 11)} | {2, 1, 3, 4, 7, 11, 18, 29, 47,
       76, 123, 199, 322, 521, 843, 1364} | {1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144,
       233, 377, 610, 987}
for a in P_int:
    for b in P_int:
        if b == 0:
            continue
        g = math.gcd(a, b)
        aa, bb = a // g, b // g
        if aa <= 200 and bb <= 200:
            pool.add(aa / bb)
pool |= {k / 88 for k in range(1, 89)}
pool.discard(0.0)
pool_arr = np.array(sorted(pool))

# ---- 觀測 ----
M0 = 27.900915
mp = 938.27208816
mn = 939.5654205
mu_pdg, md_pdg = 2.16, 4.67
m_uud_obs = 2 * mu_pdg + md_pdg
g1 = 4 * math.sin(math.pi / 88) ** 2
m_uud_pred = M0 * g1 * 64
E_bind_p = mp - m_uud_obs
E_bind_n = mn - m_uud_obs
glueball = 2370.0

def hits_in_window(r, arr, rel):
    return int(np.sum(np.abs(arr / r - 1.0) < rel))

print("=" * 78)
print("G1  節點質量 (預註冊: dev<2% : PASS)")
print("=" * 78)
print("m_uud_obs (2m_u+m_d, PDG) = %.6f MeV" % m_uud_obs)
print("m_uud_pred = M0*γ1*64      = %.6f MeV   (γ1=%.8f)" % (m_uud_pred, g1))
dev_node = abs(m_uud_pred - m_uud_obs) / m_uud_obs
print("dev = %.4f%%  ⟹ %s" % (dev_node * 100, "PASS" if dev_node < 0.02 else "FAIL"))
print("(⚠️ O144 docs/03: 64 ∈ 規則 R 但『指派俾質子節點』後驗 — 標 🟡, 唔當獨立閉合)")

print()
print("=" * 78)
print("G2  束縛能量 單量池密度 (窗=1%%, N=%d, 池=%d)" % (MC_N, len(pool_arr)))
print("=" * 78)
rng = np.random.default_rng(20261012)
null_r = np.exp(rng.uniform(math.log(logmin), math.log(logmax), size=MC_N))
null_hits = np.array([hits_in_window(r, pool_arr, DELTA) for r in null_r])
print("null: mean=%.3f std=%.3f" % (null_hits.mean(), null_hits.std()))
for name, r in [("E_bind_p/M0", E_bind_p / M0), ("E_bind_n/M0", E_bind_n / M0)]:
    h = hits_in_window(r, pool_arr, DELTA)
    z = (h - null_hits.mean()) / null_hits.std()
    print("%-14s r=%10.6f 命中=%d z=%6.2f ⟹ %s" % (
        name, r, h, z, "升候選" if z >= Z_GATE else ("線索" if z >= Z_LINE else "否決")))

print()
print("=" * 78)
print("G3  ★ 雙項式家族 m = M0(a − b·γ1), (a,b) ∈ P_int² (a,b≤200), 窗=0.1%")
print("=" * 78)
As = np.array(sorted(P_int))
Bs = np.array(sorted(P_int))
C = As[:, None] - Bs[None, :] * g1      # (|A|, |B|) 矩陣
Cflat = C.ravel()
def hits2(r, rel=DELTA2):
    return int(np.sum(np.abs(Cflat / r - 1.0) < rel))

for name, r in [("m_n/M0", mn / M0), ("m_p/M0", mp / M0)]:
    h = hits2(r)
    # MC: same 2-DOF family, random target
    null_r2 = np.exp(rng.uniform(math.log(logmin), math.log(logmax), size=MC_N))
    nh = np.array([hits2(rr) for rr in null_r2])
    z = (h - nh.mean()) / nh.std()
    print("%-10s r=%12.7f 命中=%d (null mean=%.3f std=%.3f) z=%7.2f ⟹ %s" % (
        name, r, h, nh.mean(), nh.std(), z,
        "升候選" if z >= Z_GATE else ("線索" if z >= Z_LINE else "否決")))
    if h > 0:
        # 列出命中 (a,b)
        idx = np.where(np.abs(Cflat / r - 1.0) < DELTA2)[0]
        for j in idx[:10]:
            a, b = int(As[j // len(Bs)]), int(Bs[j % len(Bs)])
            print("      (a,b)=(%d,%d): M0×(%.4f)=%.4f dev=%.5f%%" % (
                a, b, a - b * g1, M0 * (a - b * g1),
                abs(M0 * (a - b * g1) - r * M0) / (r * M0) * 100))

print()
print("=" * 78)
print("G4  glueball 交叉 (X(2370)/M0, 池=同池 1% 窗)")
print("=" * 78)
rg = glueball / M0
h = hits_in_window(rg, pool_arr, DELTA)
z = (h - null_hits.mean()) / null_hits.std()
print("X(2370)/M0 = %.4f  最近候選:" % rg)
devs = np.abs(pool_arr / rg - 1.0)
i = int(np.argmin(devs))
print("  %g dev=%.4f%%%s" % (pool_arr[i], devs[i] * 100, " (✔ 窗口內)" if devs[i] < DELTA else ""))
print("  85 = N_φ8×Σφ8 = 5×17 — O144 docs/03 已撤回 (後驗) ⟹ 禁區")
print("  命中=%d z=%6.2f ⟹ %s" % (h, z, "升候選" if z >= Z_GATE else ("線索" if z >= Z_LINE else "否決")))

print()
print("=" * 78)
print("RESULT")
print("=" * 78)
print("G1 節點: %s" % ("PASS" if dev_node < 0.02 else "FAIL"))
print("G2 束縛能: 池密度測 (詳上)")
print("G3 雙項式: 池密度測 (詳上)")
print("G4 glueball: 池密度測 (詳上; 85 禁區)")