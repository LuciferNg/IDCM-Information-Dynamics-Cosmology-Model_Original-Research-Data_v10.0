#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""O247 CLOSEOUT 審計 — 獨立重驗 (T1, by first principles, 零 import 原 scripts) v2

審計對象: O247 全部記錄 (01_problem_record.md / SESSION_START.md / docs/01-07 /
         scripts/01-10 / logs/01-10) 嘅計算數字及結論。

原則 (idcm-closeout §6.4):
  - 唔 import / 唔 call 任何原推導 script (冇共享函數 = 冇共享 bug)
  - 由原始輸入 (PDG 2024 + CODATA + IDCM 結構定義) 重算所有 headline 數字
  - 高精度; 逐項對 docs 記錄判斷 [PASS]/[FAIL]

v2 更正 (首跑 4 FAIL 分辨):
  - γ₁ 用正確值 4sin²(π/88)=0.005095771 (scripts/08 docstring 0.005096319 係錯 — 記 finding F1)
  - m_uud obs 用 PDG 電流夸克質量約定 2×2.16+4.67=8.99 (scripts/02/docs 用此)
  - scripts/05 MC null 按原文: N=20000, 7×log-uniform[1,400], 5% 窗
  - S2 檢查改為斷言「sign bug 造成假 PASS」

輸出: RESULT + findings 摘要
"""
import math
import numpy as np

PASS, FAIL = 0, 0
results = []

def chk(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
    results.append((name, bool(cond), detail))
    print("  [%s] %-52s %s" % ("PASS" if cond else "FAIL", name, detail))

# ================= 基礎常數 (原始輸入) =================
MP = 938.27208816
MN = 939.5654205
ME = 0.51099895000
M0 = 27.900915
HBC = 197.3269804
ALPHA_INV = 137.035999084
RYD_INF = 10973731.568160
A0_CODATA = 0.529177210903
AMU = 931.49410242
M_H_ION = 13.5984345
RYD_EV = 13.605693122994
MPL = 1.220890e22
MU_F2, MD_F2 = 93.4/42.890, 93.4/42.890*2.1505   # O238 freeze v2
MU_PDG, MD_PDG = 2.16, 4.67                        # PDG 電流夸克質量 (scripts/02 用)
PHI = (1 + math.sqrt(5)) / 2
G1 = 4 * math.sin(math.pi / 88) ** 2
N_D = 88

print("=" * 78)
print("§0 常數自洽 (raw inputs sanity)")
print("=" * 78)
chk("γ₁ = 4sin²(π/88) = 0.00509577 (正確值)", abs(G1 - 0.005095771) < 1e-8, "γ₁=%.9f" % G1)
chk("★F1 scripts/08 docstring γ₁=0.005096319 係誤值", abs(0.005096319 - G1) > 1e-7,
    "正確 %.9f vs docstring %.9f (差 %.2e; 計算未受影響 — 用計算式)" % (G1, 0.005096319, 0.005096319 - G1))
chk("u/d freeze v2 (2.1776/4.6827)", abs(MU_F2 - 2.1776) < 1e-3 and abs(MD_F2 - 4.6827) < 1e-3,
    "mu=%.4f md=%.4f" % (MU_F2, MD_F2))

# ================= §1 scripts/01 (docs/02 §一) =================
print()
print("=" * 78)
print("§1 scripts/01 快閘 — 5 個核子單量 r 值 + 池密度")
print("=" * 78)
r1, r2 = MP / M0, MN / M0
r3, r4 = (MN - MP) / ME, (MN - MP) / M0
r5 = MN / MP
chk("r1 m_p/M₀ = 33.6287", abs(r1 - 33.6287) < 1e-4, "r1=%.7f" % r1)
chk("r2 m_n/M₀ = 33.6751", abs(r2 - 33.6751) < 1e-4, "r2=%.7f" % r2)
chk("r3 (m_n−m_p)/m_e = 2.53099", abs(r3 - 2.53099) < 1e-5, "r3=%.7f" % r3)
chk("r4 (m_n−m_p)/M₀ = 0.04635", abs(r4 - 0.04635) < 1e-5, "r4=%.7f" % r4)
chk("r5 m_n/m_p = 1.00138", abs(r5 - 1.00138) < 1e-5, "r5=%.8f" % r5)
P_int = set(range(1, 21)) | {22, 29, 30, 33, 34, 37, 42, 44, 45, 47, 55, 60, 61, 62,
                             64, 68, 70, 71, 76, 79, 85, 86, 88, 89, 90, 123, 137,
                             178, 199, 233, 264, 322, 377, 521, 528, 610, 843,
                             1364, 1547, 1554}
pool = set(P_int) | {PHI ** k for k in range(-5, 11) if PHI ** k > 0}
pool |= {2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521, 843, 1364}
pool |= {1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987}
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
chk("scripts/01 池規模 = 1936", len(pool) == 1936, "pool=%d" % len(pool))
rng = np.random.default_rng(20261012)
null_r = np.exp(rng.uniform(math.log(0.5), math.log(50.0), size=10000))
p_arr = np.array(sorted(pool))
hits_arr = np.array([int(np.sum(np.abs(p_arr / r - 1.0) < 0.01)) for r in null_r])
chk("MC null mean=5.24, std=3.42", abs(hits_arr.mean() - 5.24) < 0.05
    and abs(hits_arr.std() - 3.42) < 0.05,
    "mean=%.2f std=%.2f" % (hits_arr.mean(), hits_arr.std()))
for nm, rv, hx in [("r1", r1, 0), ("r2", r2, 1), ("r3", r3, 6), ("r4", r4, 1), ("r5", r5, 3)]:
    h = int(np.sum(np.abs(p_arr / rv - 1.0) < 0.01))
    z = (h - hits_arr.mean()) / hits_arr.std()
    chk("§1 %s 命中=%d z=%.2f (doc: %d)" % (nm, h, z, hx), h == hx and (z < 3), "z=%.2f" % z)

# ================= §2 scripts/02 (docs/02 §二) =================
print()
print("=" * 78)
print("§2 scripts/02 P2 — 節點 / 束縛能 / 雙項式 / glueball")
print("=" * 78)
m_uud_obs = 2 * MU_PDG + MD_PDG           # 8.99 (PDG 約定, scripts/02 用)
m_uud_pred = M0 * G1 * 64
dev_node = abs(m_uud_pred - m_uud_obs) / m_uud_obs
chk("G1 m_uud = M₀γ₁×64 = 9.099 dev 1.22% (obs 8.99)",
    abs(m_uud_pred - 9.099) < 0.002 and abs(dev_node - 0.0122) < 0.001,
    "pred=%.4f obs=%.4f dev=%.4f%%" % (m_uud_pred, m_uud_obs, dev_node * 100))
Eb_p, Eb_n = MP - m_uud_obs, MN - m_uud_obs
chk("G2 E_bind_p/M₀ = 33.307", abs(Eb_p / M0 - 33.307) < 0.01, "r=%.4f z<0 否決" % (Eb_p / M0))
chk("G2 E_bind_n/M₀ = 33.353", abs(Eb_n / M0 - 33.353) < 0.01, "r=%.4f" % (Eb_n / M0))
binom = M0 * (34 - 64 * G1)
devB = abs(binom - MN) / MN
chk("G3 雙項式 (34,64) dev ~0.0034%", abs(devB - 3.4e-5) < 1e-5,
    "M₀(34−64γ₁)=%.4f dev=%.5f%% (doc 0.0036%%, z=3.40 線索非證據)" % (binom, devB * 100))
chk("G4 glueball 84.94 → 85 dev 0.067%", abs(2370.0 / M0 - 84.94) < 0.01,
    "r=%.4f (z=−1.24 否決)" % (2370.0 / M0))

# ================= §3 scripts/03 (docs/02 §三) =================
print()
print("=" * 78)
print("§3 scripts/03 — R∞ = α_str²·m_e/2 + m_1H 恆等式 (正確單位 ✓)")
print("=" * 78)
alpha = 1.0 / 137.036
R_idcm = alpha * alpha * ME * 1e6 / 2.0
devR = abs(R_idcm / RYD_EV - 1.0)
chk("C1 R∞_IDCM = 13.605693 eV dev <1e-6", devR < 1e-6,
    "R=%11.6f eV dev=%.3e (doc: dev 1e-8)" % (R_idcm, devR))
mH_id = MP + ME - M_H_ION * 1e-6
mH_obs = 1.00782503223 * AMU
devH = abs(mH_id / mH_obs - 1.0)
chk("C2 m_1H 恆等式自洽 (13.598 eV ×1e-6 ✓)", devH < 1e-6,
    "pred=%.6f obs=%.6f dev=%.2e" % (mH_id, mH_obs, devH))

# ================= §4 scripts/04 (docs/03 §二) =================
print()
print("=" * 78)
print("§4 scripts/04 — K_Tree 池 (λ_k=4sin²(kπ/68), k=1..33)")
print("=" * 78)
lam = [4 * math.sin(k * math.pi / 68) ** 2 for k in range(1, 34)]
psums = []
sacc = 0.0
for v in lam:
    sacc += v
    psums.append(sacc)
pool4 = set(lam) | set(psums)
pool4 |= {66, 68, 176, 134, 42, 88, 55, 34, 17, 33, 22, 4, 16, 90, 61.5, 5940 / 90}
pool4 |= {291.5 - m for m in range(34)}
pool4 |= {4 ** p for p in range(-5, 6)}
pool4 |= {PHI ** q for q in range(-10, 11)}
for k in range(33):
    for j in range(33):
        if j != k:
            pool4.add(lam[k] / lam[j])
pool4.discard(0.0)
pa4 = np.array(sorted(pool4))
chk("scripts/04 池規模 = 1187", len(pool4) == 1187, "pool=%d" % len(pool4))
rng4 = np.random.default_rng(20261012)
nr4 = np.exp(rng4.uniform(math.log(0.1), math.log(400.0), size=10000))
nh4 = np.array([int(np.sum(np.abs(pa4 / r - 1.0) < 0.03)) for r in nr4])
chk("MC null mean=7.51 std=6.03", abs(nh4.mean() - 7.509) < 0.05 and abs(nh4.std() - 6.027) < 0.05,
    "mean=%.3f std=%.3f" % (nh4.mean(), nh4.std()))
mH4 = 938.7830745
mHe4 = 3727.3794066
EbHe4 = 2 * MP + 2 * MN - mHe4
chk("E_bind(He4) = 2p+2n−m_He4 = 28.2957", abs(EbHe4 - 28.2957) < 0.001, "=%.4f" % EbHe4)
obs4 = [("m_p/M0", MP / M0, 3, -0.75), ("m_n/M0", MN / M0, 3, -0.75),
        ("m_H/M0", mH4 / M0, 3, -0.75), ("amu/M0", AMU / M0, 4, -0.58),
        ("m_He4/M0", mHe4 / M0, 2, -0.91), ("E_bind(He4)/M0", EbHe4 / M0, 18, 1.74),
        ("E_bind(Fe56)/A/M0", 8.7903 / M0, 10, 0.41), ("E_bind(D2)/A/M0", 1.1123 / M0, 3, -0.75)]
for nm, rv, hx, zx in obs4:
    h = int(np.sum(np.abs(pa4 / rv - 1.0) < 0.03))
    z = (h - nh4.mean()) / nh4.std()
    chk("§4 %-20s 命中=%d z=%.2f" % (nm, h, z), h == hx and abs(z - zx) < 0.3,
        "r=%.4f (doc h=%d z=%.2f → 否決)" % (rv, hx, zx))
chk("G4 Σλ(2)/M₀=1.188 dev 6.82%", abs(psums[1] * M0 - 1.188) < 0.01
    and abs(abs(psums[1] * M0 / 1.1123 - 1) * 100 - 6.82) < 0.2, "Σλ2=%.5f" % psums[1])
chk("G4 Σλ(4)/M₀=7.087 dev 0.18%", abs(psums[3] * M0 - 7.087) < 0.01, "Σλ4=%.5f" % psums[3])
chk("G4 Σλ(12)/M₀=144.9 dev 1786%", abs(psums[11] * M0 - 144.866) < 0.1, "Σλ12=%.5f" % psums[11])
chk("G4 Σλ(16)/M₀=317.2 dev 3877%", abs(psums[15] * M0 - 317.243) < 0.1, "Σλ16=%.5f" % psums[15])

# ================= §5 scripts/05 (docs/03 §三) =================
print()
print("=" * 78)
print("§5 scripts/05 — 核幻數池密度 + λ(x) 連續化")
print("=" * 78)
pool5 = set()
pool5 |= {33, 66, 68, 88, 90, 176, 134, 42, 55, 34, 17, 22, 4, 16, 36, 32, 44, 61.5, 123}
pool5 |= {2, 1, 3, 7, 11, 18, 29, 47, 76, 199, 322, 521, 843, 1364}
pool5 |= {1, 5, 8, 13, 21, 89, 144, 233, 377, 610, 987}
pool5 |= {4 ** p for p in range(-3, 6)}
pool5 |= {PHI ** q for q in range(-8, 12)}
pool5 |= set(lam)
s = 0.0
for v in lam:
    s += v
    pool5.add(s)
pool5 |= {ki / 88 for ki in range(1, 89)}
pool5.discard(0.0)
pa5 = np.array(sorted(pool5))
chk("scripts/05 池 = 218", len(pool5) == 218, "pool=%d" % len(pool5))
magic = [2, 8, 20, 28, 50, 82, 126]
hits5 = sum(1 for m in magic if np.min(np.abs(pa5 / m - 1.0)) < 0.05)
chk("G1 幻數命中 6/7 (82 ✗)", hits5 == 6, "hits=%d/7" % hits5)
# MC null 按 scripts/05 原文: N=20000, 每組 7×log-uniform[1,400], 5% 窗
rng5 = np.random.default_rng(20261012)
null_hits5 = np.zeros(20000)
for i in range(20000):
    r7 = np.exp(rng5.uniform(math.log(1.0), math.log(400.0), size=7))
    c = 0
    for rv in r7:
        if np.min(np.abs(pa5 / rv - 1.0)) < 0.05:
            c += 1
    null_hits5[i] = c
z5 = (hits5 - null_hits5.mean()) / null_hits5.std()
chk("G1 MC null mean=5.66 std=1.04 z=0.32", abs(null_hits5.mean() - 5.66) < 0.05
    and abs(null_hits5.std() - 1.04) < 0.05 and abs(z5 - 0.32) < 0.2,
    "mean=%.2f std=%.2f z=%.2f" % (null_hits5.mean(), null_hits5.std(), z5))
lx = lambda A: 4 * math.sin(math.pi * A / 68) ** 2
chk("G2 λ(2)·M₀=0.950 dev 14.58%", abs(lx(2) * M0 - 0.950) < 0.01
    and abs(abs(lx(2) * M0 / 1.1123 - 1) * 100 - 14.58) < 0.3)
chk("G2 λ(4)·M₀=3.768 dev 46.73%", abs(lx(4) * M0 - 3.768) < 0.01)
chk("G2 λ(12)·M₀=30.93 dev 302.7%", abs(lx(12) * M0 - 30.929) < 0.01)
chk("G2 λ(16)·M₀=50.65 dev 535.1%", abs(lx(16) * M0 - 50.653) < 0.01)

# ================= §6 scripts/06 (docs/03 §四) =================
print()
print("=" * 78)
print("§6 scripts/06 — μ-ladder k = log_φ(x/M₀) vs 半整數")
print("=" * 78)
def k_of(x):
    return math.log(x / M0) / math.log(PHI)
obs6 = [("m_p", MP, 7.30527, 0.195), ("m_n", MN, 7.30813, 0.192),
        ("m_H", mH4, 7.30640, 0.194), ("amu", AMU, 7.29020, 0.210),
        ("m_He4", mHe4, 10.17182, 0.172), ("E_bind(He4)", EbHe4, 0.02920, 0.029),
        ("E_bind(Fe56)/A", 8.7903, -2.40021, 0.100), ("E_bind(D2)/A", 1.1123, -6.69607, 0.196)]
for nm, xv, kx, offx in obs6:
    k = k_of(xv)
    r_ = round(2 * k) / 2.0
    chk("§6 %-16s k=%.5f 偏離=%.3f" % (nm, k, abs(k - r_)),
        abs(k - kx) < 0.002 and abs(abs(k - r_) - offx) < 0.002, "最近半整數=%.4f" % r_)
n_hit6 = sum(1 for _, xv, _, _ in obs6 if abs(k_of(xv) - round(2 * k_of(xv)) / 2.0) < 0.05)
z6 = (n_hit6 / 8 - 0.1989) / math.sqrt(0.1989 * 0.8011 / 8)
chk("§6 命中 1/8, z=−0.52", n_hit6 == 1 and abs(z6 + 0.52) < 0.1, "hit=%d/8 z=%.2f" % (n_hit6, z6))

# ================= §7 scripts/07 (docs/04) =================
print()
print("=" * 78)
print("§7 scripts/07 — A₅ 出處 (質因數和/τ/譜投影子/計數)")
print("=" * 78)
A5 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
def pf(n):
    fs, d, m = [], 2, n
    while d * d <= m:
        if m % d == 0:
            fs.append(d)
            while m % d == 0:
                m //= d
        d += 1
    if m > 1:
        fs.append(m)
    return fs
chk("C1 88 質因數 {2,11} 和 = 13", pf(88) == [2, 11])
def tau(n):
    ans, d, m = 1, 2, n
    while d * d <= m:
        if m % d == 0:
            e = 0
            while m % d == 0:
                m //= d
                e += 1
            ans *= (e + 1)
        d += 1
    if m > 1:
        ans *= 2
    return 1 if n == 1 else ans
chk("C2 τ(n)≤3 = A₅ EXACT", sorted([k for k in range(1, 14) if tau(k) <= 3]) == A5)
def isp(k):
    if k < 2: return False
    for d in range(2, int(math.sqrt(k)) + 1):
        if k % d == 0: return False
    return True
def issq(k):
    r = int(round(math.sqrt(k)))
    return r * r == k
def psq(ub):
    return sorted([k for k in range(1, ub + 1) if isp(k) or issq(k)])
chk("C4 psq(13)=psq(14)=psq(15)=A₅, psq(16)≠A₅",
    psq(13) == A5 and psq(14) == A5 and psq(15) == A5 and psq(16) != A5)
# C1 MC null 重現
rng7 = np.random.default_rng(20261012)
sizes = np.array([len(psq(sum(pf(int(rng7.integers(50, 151)))))) for _ in range(10000)])
p9 = float(np.mean(sizes == 9))
chk("C1 MC: 集=9 概率 6.73% (唔夠 5% 閘)", abs(p9 * 100 - 6.73) < 0.3, "p9=%.2f%%" % (p9 * 100))
N = 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, N + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
PA5 = np.zeros((N, N))
for n in A5:
    v = psii[n - 1]
    PA5 += np.outer(v, v)
tr = np.trace(PA5)
ok_idem = np.allclose(PA5 @ PA5, PA5, atol=1e-12)
Lc = np.zeros((N, N))
for i in range(N):
    Lc[i, i] = 2.0
    Lc[i, (i + 1) % N] = -1.0
    Lc[i, (i - 1) % N] = -1.0
comm = np.linalg.norm(Lc @ PA5 - PA5 @ Lc)
chk("C3 Tr(P_A₅)=9, P²=P, ‖[L,P]‖=2.23e-1",
    abs(tr - 9) < 1e-6 and ok_idem and abs(comm - 0.2227) < 0.01,
    "Tr=%.6f P²=%s ‖[L,P]‖=%.3e" % (tr, ok_idem, comm))

# ================= §8 scripts/08 (docs/05) =================
print()
print("=" * 78)
print("§8 scripts/08 — m₄₄ / uud-udd 節點 / n−p 差")
print("=" * 78)
m44 = MPL * math.exp(-44)
chk("G1 m₄₄ = M_Pl·e^(−44) = 949.991 MeV", abs(m44 - 949.991) < 0.05, "m₄₄=%.4f" % m44)
chk("G1 m_p/m₄₄ dev −1.2335%", abs((MP / m44 - 1) * 100 + 1.2335) < 0.01,
    "dev=%.4f%%" % ((MP / m44 - 1) * 100))
chk("G1 m_n/m₄₄ dev −1.0974%", abs((MN / m44 - 1) * 100 + 1.0974) < 0.01,
    "dev=%.4f%%" % ((MN / m44 - 1) * 100))
g11, g9 = 4 * math.sin(11 * math.pi / 88) ** 2, 4 * math.sin(9 * math.pi / 88) ** 2
chk("γ₁₁=0.585786 γ₉=0.398918", abs(g11 - 0.585786) < 1e-5 and abs(g9 - 0.398918) < 1e-5,
    "γ11=%.6f γ9=%.6f" % (g11, g9))
g_uud, g_udd = 2 * g11 + g9, g11 + 2 * g9
chk("G2 M₀·γ_uud=43.8181 (dev 95%)", abs(M0 * g_uud - 43.8181) < 0.01, "=%.4f" % (M0 * g_uud))
chk("G2 M₀·γ_udd=38.6043 (dev 96%)", abs(M0 * g_udd - 38.6043) < 0.01, "=%.4f" % (M0 * g_udd))
chk("G2 m₄₄−M₀·γ_uud=906.17 (dev 3.42%)", abs(m44 - M0 * g_uud - 906.1725) < 0.1,
    "=%.4f" % (m44 - M0 * g_uud))
chk("G2 m₄₄−M₀·γ_udd=911.39 (dev 2.87%)", abs(m44 - M0 * g_udd - 911.3863) < 0.1,
    "=%.4f (最近但唔過 1.5%% 閘)" % (m44 - M0 * g_udd))
dmnp = MN - MP
chk("G3 m_n−m_p=1.293332, M₀γ₁=0.142177, ratio=9.0967, dev 1.06%",
    abs(dmnp - 1.293332) < 1e-5 and abs(M0 * G1 - 0.142177) < 1e-5
    and abs(dmnp / (M0 * G1) - 9.0967) < 1e-3
    and abs((dmnp - 9 * M0 * G1) / dmnp * 100 - 1.06) < 0.05,
    "ratio=%.4f dev=%.2f%%" % (dmnp / (M0 * G1), (dmnp - 9 * M0 * G1) / dmnp * 100))
# ★F2: G2.1 chk sign bug 重現
v = m44 - M0 * g_uud
clause1 = abs(v) / MP - 1          # scripts/08 原式: abs(v)/mp - 1
clause2 = min(abs(v) / MP - 1, abs(v) / MN - 1,
              abs(m44 - M0 * g_udd) / MP - 1, abs(m44 - M0 * g_udd) / MN - 1)
c2_src = (clause1 < 0.015) or (clause2 < 0.015)
true_min_dev = min(abs(v / MP - 1), abs(v / MN - 1),
                   abs((m44 - M0 * g_udd) / MP - 1), abs((m44 - M0 * g_udd) / MN - 1)) * 100
chk("★F2 G2.1 sign bug → 假 PASS (真 dev %.2f%% >1.5%%)" % true_min_dev,
    bool(c2_src) and true_min_dev > 1.5,
    "原式 abs(v)/mp−1 = %.4f <0.015 → True (sign 錯); 真最近 dev=%.2f%% ⟹ 名義 PASS 係假" % (clause1, true_min_dev))

# ================= §9 scripts/09 (docs/06) ★S1 單位 =================
print()
print("=" * 78)
print("§9 scripts/09 — a₀ (C1/C2) + m_H (★S1 單位核查)")
print("=" * 78)
a0_1 = 1e10 / (4 * math.pi * RYD_INF * ALPHA_INV)
dev1 = abs(a0_1 / A0_CODATA - 1) * 100
chk("C1 a₀ = 1/(4πR∞α⁻¹) = 0.529177211 Å dev 1.3e-10%", abs(dev1 - 1.3e-10) < 1e-9,
    "a0=%.9f Å dev=%.4e%%" % (a0_1, dev1))
a0_2_A = (HBC * ALPHA_INV) / ME * 1e-5
dev2 = abs(a0_2_A / A0_CODATA - 1) * 100
chk("C2 a₀ = ħc·α⁻¹/m_e = 0.529177211 Å dev 3.0e-8%",
    abs(a0_2_A - 0.529177211) < 1e-6 and abs(dev2 - 3.0e-8) < 1e-7,
    "a0=%.9f Å dev=%.4e%%" % (a0_2_A, dev2))
mH_wrong = MP + ME - 13.605693e-3
mH_right = MP + ME - RYD_EV * 1e-6
mH_pdg = 938.7830745
dev_wrong = abs(mH_wrong / mH_pdg - 1) * 100
dev_right = abs(mH_right / mH_pdg - 1) * 100
print("   scripts/09 C5 : m_H = %.6f (用 13.605693e-3 MeV = 13.6 keV ⚠️)" % mH_wrong)
print("   正確單位      : m_H = %.6f (R∞ = 1.3605693e-5 MeV)" % mH_right)
print("   dev(記錄) = %.4e%%   dev(正確) = %.4e%%" % (dev_wrong, dev_right))
chk("★S1 m_H 單位 1000× 錯: 記錄 938.7695/dev 1.448e-3% 係 bug; 正確 dev ~1e-7%",
    abs(mH_wrong - 938.7695) < 1e-4 and abs(dev_wrong - 1.448e-3) < 1e-6 and dev_right < 1e-6,
    "記錄值重現 ✓; 正確 m_H=%.7f dev=%.2e%% (結論不變且更強)" % (mH_right, dev_right))

# ================= §10 scripts/10 (docs/07) =================
print()
print("=" * 78)
print("§10 scripts/10 — P1/P2/P3")
print("=" * 78)
N_NUC, N_STAB = 3300, 254
chk("P1 3300 核素 >> 88 mode", N_NUC / 88 > 30 and N_STAB / 88 > 2, "ratio=%.1f" % (N_NUC / 88))
chk("P2 A∈[1,250]: 250/88 = 2.84 A/mode", abs(250 / 88 - 2.84) < 0.01,
    "(docs/07 寫「5.4 mode/A」— 屬表述, 見 finding F3)")
mH_pred10 = MP + ME - 13.605693e-3
dev10 = abs(mH_pred10 / mH_pdg - 1) * 100
chk("P3 同 S1: 記錄 938.7695 dev 1.448e-3% = 單位 bug", abs(dev10 - 1.448e-3) < 1e-6,
    "重現記錄值 ✓; 正確 m_H=%.7f dev=%.2e%%" % (mH_right, dev_right))
chk("P3 結論(複合投影形式)不受影響 — 正確值更吻合",
    abs(mH_right / mH_pdg - 1) < 1e-6, "dev(right)=%.2e%%" % dev_right)

# ================= §11 跨-O 引用 =================
print()
print("=" * 78)
print("§11 跨-O 引用數字 (O140 BBN γ₇/γ₂₀)")
print("=" * 78)
g7 = 4 * math.sin(7 * math.pi / 88) ** 2
g20 = 4 * math.sin(20 * math.pi / 88) ** 2
chk("O140 γ₇/γ₂₀ = 0.14261761", abs(g7 / g20 - 0.14261761) < 1e-7, "ratio=%.8f" % (g7 / g20))

print()
print("=" * 78)
print("RESULT: %d/%d PASS (FAIL=%d)" % (PASS, PASS + FAIL, FAIL))
print("=" * 78)
print("FINDINGS:")
print("  F1 scripts/08 docstring γ₁ = 0.005096319 誤值 (正確 0.005095771) — 註解級, 計算無影響")
print("  F2 scripts/08 G2.1 chk sign bug (abs(v)/mp−1 缺外層 abs) → 假 PASS;")
print("     log/08「PASS: 1/3」含此假 PASS; docs/05 判決表正確報 G2 全滅 → 結論不受影響")
print("  F3 docs/07 P2「5.4 mode/A」表述 — 數值 250/88=2.84 (單位方向); 不影響 no-go 結論")
print("  ★S1 scripts/09 C5 + scripts/10 P3: m_H 用 R∞=13.605693e-3 MeV (13.6 keV, 1000×錯)")
print("     正確 R∞=1.3605693e-5 MeV → m_H=938.7830735 dev 1.06e-7%")
print("     影響: docs/06「dev 1.4e-3%」、docs/07 P3「938.7695/dev 1.448e-3%」、")
print("     SESSION_START S6#4/S7 數字需 append-only 修正; 結論(複合投影)不變且更強")
for nm, c_, dt in results:
    if not c_:
        print("  FAIL: %s — %s" % (nm, dt))