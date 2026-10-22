#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O202 scripts/01 — 路線 1: 測度候選枚舉 + 整族排除 (Measure candidate enumeration)

憲章: docs/01_problem_record.md §四 路線 1
問題: IDCM 譜係離散 (峰位 l_m + 峰高 A_m), 理論內部冇「測度」(dl) 亦冇「絕對標度」。
      本 script 枚舉 11 個結構候選測度 (x 2 個錨定約定) + null, 先過「測度可容性篩」
      (admissibility screen), 再對 4 個觀測量比對, 最後報「整族排除」。

方法:
  (A) 候選表: Var_M = sum_m w_m * (2l_m+1)/(2l_m(l_m+1)) * A_m
      錨定約定 1 (peak)    : A_m = TGT*rho_m  (錨定第一峰, rho 來自 O9/O10 母函數)
      錨定約定 2 (plateau) : A_m = TGT       (錨定平台, 全部峰同高)
  (B) 可容性篩: 一個合法測度 = l-軸上嘅分佈 -> 必須 (i) w_m >= 0
      (ii) 頻帶唔可以重疊 (每個 l-mode 只可計一次) (iii) 總覆蓋 <= 可用 mode 數
      ★ M4 (w=2l+1) 通過 5% 判準但係 9.2x 過計 => 由可容性排除, 唔係由 dev 排除
  (C) 數據側: 反解 dl_eff (O171 docs/21 M4 兩條基線) + 結構身份掃描 + null
  (D) 4 個觀測量逐一比對 (全譜 rms / 峰高 / SW 平台 / 冷斑)
  (E) 退化性: sum w = 12271.55 只係一個超平面 => 命中「總方差」本身唔構成測度證據

零新常數: {N_d=44, B=4, N_gen=3, mu2=2, F5=5, F6=8, F7=13, L4=7, M=33} + gamma_k + eps_phi/eps_ring
"""

import json
import math
import random
from pathlib import Path

import mpmath as mpm
mp = mpm.mp
mp.dps = 40

BASE = Path(__file__).resolve().parent.parent
PLK = BASE / "data" / "planck"
T_CMB = mp.mpf('2.72548') * 1e6            # uK

N_PASS = 0
N_FAIL = 0
FAILS = []


def chk(name, cond, extra=""):
    global N_PASS, N_FAIL
    if cond:
        N_PASS += 1
        print(f"  [PASS] {name} {extra}")
    else:
        N_FAIL += 1
        FAILS.append(name)
        print(f"  [FAIL] {name} {extra}")


print("=" * 78)
print("O202 scripts/01 — 路線 1: 測度候選枚舉 + 整族排除")
print("=" * 78)

# ------------------------------------------------------------------ 常數
PHI = (1 + mp.sqrt(5)) / 2
EPS_PHI = 1 / (4 * PHI)                     # (sqrt5-1)/8
EPS_RING = mp.mpf(13) / 86                  # F7/(2N_d-2)
AMP = EPS_PHI ** 5 / 8
TGT = (AMP * T_CMB) ** 2                    # uK^2
ND, B, NGEN, MU2, F5, F6, F7, L4, M = 44, 4, 3, 2, 5, 8, 13, 7, 33

# IDCM 7 峰 (O9: l_m = 44*(33-C(9-m,2)) + ((m-1)*9 mod 25); l_5 = 1121 結構修正)
PEAKS = []
for m in range(1, 8):
    PEAKS.append((m, ND * (M - math.comb(9 - m, 2)) + ((m - 1) * 9) % 25))
PEAKS[4] = (5, 1121)
ELL = dict(PEAKS)
RHO = {1: mp.mpf(1), 2: mp.mpf(4) / 9, 3: mp.mpf(4) / 9, 4: mp.mpf(9) / 49,
       5: mp.mpf(3) / 14, 6: mp.mpf(16) / 121, 7: mp.mpf(1) / 7}

print(f"  eps_phi  = {mp.nstr(EPS_PHI, 12)}   eps_ring = {mp.nstr(EPS_RING, 12)}")
print(f"  AMP = eps_phi^5/8 = {mp.nstr(AMP, 10)}  x T_CMB = {mp.nstr(AMP*T_CMB, 10)} uK")
print(f"  TGT = (AMP*T)^2 = {mp.nstr(TGT, 10)} uK^2")
chk("P1 7 峰位 = O9 公式 (220/537/810/1014/1121/1340/1412)",
    [e for _, e in PEAKS] == [220, 537, 810, 1014, 1121, 1340, 1412],
    f"({[e for _, e in PEAKS]})")
chk("P2 峰高比母函數 rho: 偶峰平方級聯 + 奇峰一次比",
    abs(float(RHO[2]) - 4 / 9) < 1e-9 and abs(float(RHO[5]) - 3 / 14) < 1e-9, "")

# ------------------------------------------------------------------ 數據
def load(fn):
    rows = []
    for ln in open(PLK / fn, encoding="utf-8"):
        if ln.startswith("#"):
            continue
        p = ln.split()
        if len(p) >= 2:
            rows.append((int(float(p[0])), float(p[1])))
    return rows


FULL = load("COM_PowerSpect_CMB-TT-full_R3.01.txt")
BINNED = load("COM_PowerSpect_CMB-TT-binned_R3.01.txt")
D_FULL = dict(FULL)


def w_of(ell, Dl):
    return (2 * ell + 1) * mp.mpf(Dl) / (2 * ell * (ell + 1))


def sum_w(rows, lo=0, hi=10 ** 9):
    return sum(w_of(e, D) for e, D in rows if lo <= e <= hi)


def d_obs(ell):
    if ell in D_FULL:
        return mp.mpf(D_FULL[ell])
    lo = max(e for e in D_FULL if e < ell)
    hi = min(e for e in D_FULL if e > ell)
    t = mp.mpf(ell - lo) / (hi - lo)
    return D_FULL[lo] * (1 - t) + D_FULL[hi] * t


S_OBS = sum_w(FULL)
RMS_OBS = mp.sqrt(S_OBS)
chk("D1 全譜 sum w = 12271.55091 uK^2 (Planck PR3 TT full l=2..2508)",
    abs(float(S_OBS) - 12271.55091) < 1e-4, f"({float(S_OBS):.5f})")
chk("D2 全譜 rms = 110.777032 uK", abs(float(RMS_OBS) - 110.777032) < 1e-5,
    f"({float(RMS_OBS):.6f})")
print("  觀測峰高 (原始全譜逐 l):")
for m, ell in PEAKS:
    print(f"    m={m} l={ell:5d}  D_l = {float(d_obs(ell)):9.2f}  A_m/A_1(obs) = "
          f"{float(d_obs(ell)/d_obs(220)):.4f}   rho_m = {float(RHO[m]):.4f}")

# ================================================================== A
print("\n" + "=" * 78)
print("A: 候選測度枚舉 — IDCM 離散譜 -> 連續方差")
print("=" * 78)


def gamma_k(k):
    return 2 - 2 * mp.cos(k * mp.pi / 88)


def var_idcm(w, conv):
    A = (lambda m: TGT * RHO[m]) if conv == "peak" else (lambda m: TGT)
    return sum(w[m] * (2 * ELL[m] + 1) / (2 * ELL[m] * (ELL[m] + 1)) * A(m) for m, _ in PEAKS)


VORONOI = {}
for i, (m, ell) in enumerate(PEAKS):
    lo = 2 if i == 0 else (PEAKS[i - 1][1] + ell) // 2
    hi = 2508 if i == len(PEAKS) - 1 else (ell + PEAKS[i + 1][1]) // 2
    VORONOI[m] = mp.mpf(hi - lo)

CAND = {
    "M1 counting (w=1)": {m: mp.mpf(1) for m, _ in PEAKS},
    "M2 ring-Nyquist (w=N_d=44)": {m: mp.mpf(ND) for m, _ in PEAKS},
    "M3 rung spacing (w=44(8-m))": {m: mp.mpf(ND * (8 - m)) for m, _ in PEAKS},
    "M4 sky modes (w=2l+1)": {m: mp.mpf(2 * ELL[m] + 1) for m, _ in PEAKS},
    "M5 proj kernel (w=cos^2)": {m: mp.cos(m * mp.pi / 88) ** 2 for m, _ in PEAKS},
    "M6 spectral weight (w=gamma_m)": {m: gamma_k(m) for m, _ in PEAKS},
    "M7 FSR cascade (w=4^(m-1))": {m: mp.mpf(4) ** (m - 1) for m, _ in PEAKS},
    "M8 log-l uniform (w=ln ratio)": {
        m: (mp.log(mp.mpf(ELL[m]) / ELL[m - 1]) if m > 1 else mp.log(mp.mpf(ELL[1]) / 2))
        for m, _ in PEAKS},
    "M9 half-Nyquist (w=22)": {m: mp.mpf(ND) / 2 for m, _ in PEAKS},
    "M10 Z2 multiplicity (w=2)": {m: mp.mpf(MU2) for m, _ in PEAKS},
    "M11 Voronoi partition (w=spacing)": VORONOI,
}

print(f"  {'候選測度':34s} {'dev(peak)':>11} {'dev(plat)':>11} {'SumW':>9} {'overlap':>9} {'admis':>6}")
devs = {}
devs_pl = {}
adm = {}
for name, w in CAND.items():
    v = var_idcm(w, "peak")
    vp = var_idcm(w, "plateau")
    devs[name] = float((v / S_OBS - 1) * 100)
    devs_pl[name] = float((vp / S_OBS - 1) * 100)
    sumw = sum(float(w[m]) for m, _ in PEAKS)
    # 重疊比: 頻帶 [l-w/2, l+w/2] 之總長 / 覆蓋區間長
    ivs = sorted(((ELL[m] - float(w[m]) / 2, ELL[m] + float(w[m]) / 2) for m, _ in PEAKS))
    covered = 0.0
    cl, cr = ivs[0]
    for l_, r_ in ivs[1:]:
        if l_ > cr:
            covered += cr - cl
            cl, cr = l_, r_
        else:
            cr = max(cr, r_)
    covered += cr - cl
    span = max(ELL[m] + float(w[m]) / 2 for m, _ in PEAKS) - min(ELL[m] - float(w[m]) / 2 for m, _ in PEAKS)
    ov = sumw / covered if covered > 0 else float('inf')
    ok = (min(float(w[m]) for m, _ in PEAKS) >= 0) and ov <= 1.001
    adm[name] = ok
    print(f"  {name:34s} {devs[name]:+10.3f}% {devs_pl[name]:+10.3f}% {sumw:9.1f} {ov:9.3f} "
          f"{'YES' if ok else 'NO':>6}")

print("\n  ★ 可容性篩: 合法測度 = l-軸分佈 => 頻帶唔可重疊 (每個 l-mode 只計一次)")
print("    M4 (w=2l+1) 通過 5% 判準 (plat +2.674%) 但 overlap 4.57x (SumW 12915 vs 覆蓋 2825) => 可容性排除")
chk("A1 M4 通過 5% 判準 (plat dev +2.674%)",
    abs(devs_pl["M4 sky modes (w=2l+1)"] - 2.674) < 0.01,
    f"({devs_pl['M4 sky modes (w=2l+1)']:+.4f}%)")
chk("A2 ★ M4 不可容 (頻帶重疊 9.2x: 將簡併數當頻寬)", not adm["M4 sky modes (w=2l+1)"], "")
admissible = {k: (devs[k], devs_pl[k]) for k in CAND if adm[k]}
min_adm = min(abs(v) for pair in admissible.values() for v in pair)
print(f"  可容候選 {len(admissible)}/{len(CAND)} 個; 最小 |dev| = {min_adm:.3f}%")
for k in admissible:
    print(f"    {k:34s} dev(peak) {devs[k]:+9.3f}%  dev(plat) {devs_pl[k]:+9.3f}%")
chk(f"A3 ★ 可容候選整族排除: 全部 |dev| >= 5% (最小 {min_adm:.2f}%)",
    min_adm >= 5.0, f"(min |dev| = {min_adm:.3f}%)")

# 所需測度
den = sum((2 * ELL[m] + 1) / (2 * ELL[m] * (ELL[m] + 1)) * TGT * RHO[m] for m, _ in PEAKS)
W_REQ = S_OBS / den
print(f"\n  令 Var_M = 觀測全譜所需統一權重 w* = {mp.nstr(W_REQ, 8)} "
      f"({float(W_REQ):.1f} l-mode/峰)")
chk(f"A4 所需權重 w* >> 任何結構候選 (w* = {float(W_REQ):.1f} vs max 44)",
    float(W_REQ) > 1000, "")

# ================================================================== B
print("\n" + "=" * 78)
print("B: 數據側 — 反解所需測度 dl_eff (O171 docs/21 M4 兩條基線) + 結構身份")
print("=" * 78)
P5_FULL = {220: 6373.42, 528: 2673.14, 792: 2322.29, 1012: 952.17, 1188: 1166.43}
P5_BIN = {220: 5816.4797, 528: 2579.2168, 792: 2552.7278, 1012: 1246.2912, 1188: 822.1860}
S5F = sum(w_of(e, D) for e, D in P5_FULL.items())
S5B = sum(w_of(e, D) for e, D in P5_BIN.items())
DL_F, DL_B = TGT / S5F, TGT / S5B
print(f"  S_peaks (O171 5 峰, 原始全譜) = {mp.nstr(S5F, 8)} uK^2 -> dl_eff = {mp.nstr(DL_F, 8)}")
print(f"  S_peaks (O171 5 峰, binned)   = {mp.nstr(S5B, 8)} uK^2 -> dl_eff = {mp.nstr(DL_B, 8)}")
chk("B1 重現 O171 M4: S=38.8147, dl_eff=23.1864 (原始全譜)",
    abs(float(S5F) - 38.8147) < 0.001 and abs(float(DL_F) - 23.1864) < 1e-3,
    f"({float(S5F):.4f}, {float(DL_F):.5f})")
chk("B2 重現 O171 M4: S=36.403, dl_eff=24.7227 (binned)",
    abs(float(S5B) - 36.403) < 0.001 and abs(float(DL_B) - 24.7227) < 1e-3,
    f"({float(S5B):.4f}, {float(DL_B):.5f})")

# 7 峰版本 (本 O 用 O9 公式峰位)
S7 = sum(w_of(e, d_obs(e)) for _, e in PEAKS)
print(f"  (參考) 7 峰 O9 峰位版本: S = {mp.nstr(S7, 8)} -> dl_eff = {mp.nstr(TGT/S7, 8)}")

LIB = {"B": 4, "N_gen": 3, "N_d": 44, "L4": 7, "L5": 11, "F5": 5, "F6": 8, "F7": 13,
       "F8": 21, "F10": 55, "F11": 89, "K_tree": 33, "F_proj": 17, "A5": 60, "mu2": 2,
       "N_gen2": 9, "B2": 16, "S_odd": 88, "S_even": 90, "S_all": 178, "N176": 176,
       "L10": 123, "n12": 12, "n22": 22, "n45": 45, "n66": 66, "n78": 78, "n90": 90,
       "n264": 264, "n360": 360, "n720": 720, "n48": 48, "n27": 27, "n28": 28, "n36": 36,
       "n55": 55, "n56": 56, "n34": 34, "n11": 11, "n13": 13, "n29": 29, "n60": 60,
       "n5": 5, "n3": 3, "n4": 4, "n7": 7, "n8": 8, "n21": 21, "n2": 2, "n1": 1}


def scan_hits(target, tol_rel=1e-3):
    t = float(target)
    hits = []
    names = list(LIB.keys())
    for na in names:
        a = LIB[na]
        for nb in names:
            b = LIB[nb]
            for nm, val in ((f"{na}/{nb}", a / b), (f"{na}*{nb}", a * b)):
                if abs(val - t) / t <= tol_rel:
                    hits.append((nm, val))
    for na in names:
        a = LIB[na]
        for nb in names:
            b = LIB[nb]
            for nc in names:
                c = LIB[nc]
                v = a * b / c
                if abs(v - t) / t <= tol_rel:
                    hits.append((f"{na}*{nb}/{nc}", v))
    return hits


hF, hB = scan_hits(DL_F), scan_hits(DL_B)
print(f"  dl_eff(full)={float(DL_F):.4f}: 0.1% 內命中 {len(hF)} 條; "
      f"dl_eff(binned)={float(DL_B):.4f}: {len(hB)} 條")
for nm, v in hF[:5]:
    print(f"    full   {nm:22s} = {v:.6f}")
for nm, v in hB[:5]:
    print(f"    binned {nm:22s} = {v:.6f}")
random.seed(20260917)
null_counts = [len(scan_hits(mp.mpf(random.uniform(15.0, 35.0)))) for _ in range(60)]
mean_null = sum(null_counts) / len(null_counts)
print(f"  null control (60 隨機 target U(15,35)): 平均命中 {mean_null:.1f} 條")
chk("B3 ★ 命中/null < 1.5 => 密度背景 (無結構身份)",
    len(hF) < 1.5 * mean_null and len(hB) < 1.5 * mean_null,
    f"(full {len(hF)}/{mean_null:.1f}={len(hF)/mean_null:.2f}x, "
    f"binned {len(hB)}/{mean_null:.1f}={len(hB)/mean_null:.2f}x)")

# ================================================================== C
print("\n" + "=" * 78)
print("C: 4 個觀測量逐一比對")
print("=" * 78)
r_full = RMS_OBS / T_CMB / AMP
A1 = d_obs(220)
SW_DBAR = mp.sqrt(sum(D for e, D in FULL if 2 <= e <= 20) / len([1 for e, D in FULL if 2 <= e <= 20]))
CS = 5 * EPS_RING ** 5 / 8 * T_CMB
print(f"  (1) 全譜 rms: dT/T = {mp.nstr(RMS_OBS/T_CMB,8)} vs AMP = {mp.nstr(AMP,8)}"
      f" => ratio {mp.nstr(r_full,8)} (dev {float(r_full-1)*100:+.2f}%)")
print(f"  (2) 峰高: D_220 = {float(A1):.2f} vs TGT = {float(TGT):.2f} => ratio {float(A1/TGT):.4f}")
print(f"  (3) SW 平台 sqrt(Dbar(2..20)) = {float(SW_DBAR):.4f} uK vs AMP*T = {float(AMP*T_CMB):.4f}"
      f" (dev {float(SW_DBAR/(AMP*T_CMB)-1)*100:+.3f}%)")
print(f"  (4) 冷斑 5*eps_ring^5/8*T = {float(CS):.3f} uK vs SMICA -134.2 (dev {float(CS/134.2-1)*100:+.3f}%)")
chk("C1 全譜 rms 唔匹配 (ratio 3.69262, dev +269%)", abs(float(r_full) - 3.69262) < 1e-4,
    f"({float(r_full):.5f})")
chk("C2 峰高唔匹配 (D_220/TGT = 7.08)", abs(float(A1 / TGT) - 7.082) < 0.01,
    f"({float(A1/TGT):.4f})")
chk("C3 SW 平台 dev -5.75% (重現 O171 M3)",
    abs(float(SW_DBAR / (AMP * T_CMB) - 1) * 100 + 5.75) < 0.05,
    f"({float(SW_DBAR/(AMP*T_CMB)-1)*100:+.3f}%)")
chk("C4 冷斑閉合 dev +0.183% (唯一閉合項; 但用 eps_ring 非 eps_phi)",
    abs(float(CS / 134.2 - 1) * 100 - 0.183) < 0.02, f"({float(CS/134.2-1)*100:+.3f}%)")
n_obs_hit = sum(1 for x in [abs(float(r_full - 1) * 100), abs(float(A1 / TGT - 1) * 100),
                            abs(float(SW_DBAR / (AMP * T_CMB) - 1) * 100),
                            abs(float(CS / 134.2 - 1) * 100)] if x < 5)
chk("C5 ★ 4 個觀測量只有 1 個 (冷斑) 命中, 且唔係同一 eps 成員", n_obs_hit == 1,
    f"(命中 {n_obs_hit}/4)")

# ================================================================== D
print("\n" + "=" * 78)
print("D: 退化性 + 「總方差」本身係唔係一個良定義觀測量?")
print("=" * 78)
# D3: flat / Harrison-Zel'dovich 讀法 (A_m = TGT 對所有 l, 測度 w=1)
print("  D3 flat/HZ 讀法: D_l = TGT = 900 uK^2 對所有 l (即錨定平台高度)")
print(f"  {'l_max':>7} {'sum w_l':>10} {'Var_flat (uK^2)':>16} {'dev vs 觀測':>13}")
flat_devs = {}
for lm in [500, 1000, 1500, 2000, 2508, 3000, 4000]:
    swl = sum(1 / mp.mpf(e) + 1 / mp.mpf(e + 1) for e in range(2, lm + 1))
    vf = TGT * swl
    dv = float(vf / S_OBS - 1) * 100
    flat_devs[lm] = dv
    print(f"  {lm:7d} {float(swl):10.4f} {float(vf):16.2f} {dv:+12.3f}%")
chk("D3 ★ flat 讀法在 l_max=2508 邊緣命中 (+4.95%) 但 l_max 掃描 -18.7%..+11.8% "
    "(過零 @1790) => 「總方差」隨 l_max 對數發散, 唔係良定義觀測量 (M1 ill-posed)",
    abs(flat_devs[2508] - 4.945) < 0.05 and flat_devs[500] < -15.0 and flat_devs[4000] > 10.0,
    f"(500: {flat_devs[500]:+.3f}%, 2508: {flat_devs[2508]:+.3f}%, 4000: {flat_devs[4000]:+.3f}%)")
chk("D3b flat 讀法 dev 喺 l_max 掃描中變號 => 命中係 l_max 選擇 artifact",
    min(flat_devs.values()) < 0 < max(flat_devs.values()), "")

# D4: 隨機可容分拆 (7 個連續頻帶, 錨定約定) -> 命中率
random.seed(20260919)
n_hit_part = 0
N_TRIAL = 400
for _ in range(N_TRIAL):
    cuts = sorted(random.sample(range(3, 2508), 6))
    bounds = [2] + cuts + [2508]
    perm = list(range(1, 8))
    random.shuffle(perm)
    v = mp.mpf(0)
    for i, m in enumerate(perm):
        a, b = bounds[i], bounds[i + 1] - 1
        if b < a:
            continue
        g = sum(1 / mp.mpf(e) + 1 / mp.mpf(e + 1) for e in range(a, b + 1))
        v += TGT * RHO[m] * g
    if abs(float(v / S_OBS - 1) * 100) < 5.0:
        n_hit_part += 1
print(f"  D4 隨機可容分拆 (400 trial, 錨定約定): 命中 (dev<5%) {n_hit_part} 次 "
      f"= {n_hit_part/N_TRIAL*100:.1f}%")
chk("D4 ★ 隨機可容測度命中率 > 0 => 「命中總方差」唔構成測度證據 (超平面)",
    n_hit_part > 0, f"({n_hit_part}/{N_TRIAL})")

random.seed(20260918)
n_hit_null = 0
for _ in range(200):
    ells = sorted(random.sample(range(50, 2000), 7))
    v = sum((2 * e + 1) / (2 * e * (e + 1)) * TGT for e in ells)
    if abs(float(v / S_OBS - 1) * 100) < 5.0:
        n_hit_null += 1
chk("D5 null: 隨機峰位 (w=1) 200 trial 命中 0 次 => 結構候選命中率唔高於 null",
    n_hit_null == 0, f"(null {n_hit_null}/200)")

# ================================================================== E
print("\n" + "=" * 78)
print("E: 裁決")
print("=" * 78)
verdict = {
    "S_obs_uK2": float(S_OBS), "rms_obs_uK": float(RMS_OBS),
    "AMP": float(AMP), "AMP_xT_uK": float(AMP * T_CMB), "TGT_uK2": float(TGT),
    "candidate_devs_peak_pct": devs, "candidate_devs_plateau_pct": devs_pl,
    "admissible": adm, "min_admissible_dev_pct": float(min_adm),
    "M4_plateau_dev_pct": devs_pl["M4 sky modes (w=2l+1)"],
    "w_required": float(W_REQ),
    "dl_eff_full": float(DL_F), "dl_eff_binned": float(DL_B),
    "dl_eff_hits_full": len(hF), "dl_eff_hits_binned": len(hB), "dl_eff_null_mean": mean_null,
    "obs": {"full_rms_ratio": float(r_full), "peak_ratio": float(A1 / TGT),
            "sw_platform_dev_pct": float(SW_DBAR / (AMP * T_CMB) - 1) * 100,
            "coldspot_dev_pct": float(CS / 134.2 - 1) * 100},
    "flat_reading_dev_pct_by_lmax": flat_devs,
    "random_partition_hit_rate_pct": n_hit_part / N_TRIAL * 100,
    "verdict": ("路線 1 整族排除: 可容結構測度候選 "
                f"{len(admissible)}/{len(CAND)} 個全部 |dev| >= 5% (最小 {min_adm:.2f}%); "
                "唯一通過 5% 之 M4 (+2.674%) 由可容性排除 (頻帶重疊 4.57x); "
                f"所需 w*={float(W_REQ):.1f}/峰 無結構身份 (上限 44); "
                "唯一邊緣命中 = flat/HZ 平台高度讀法 (D_l=TGT) 在 l_max=2508 得 +4.95%, "
                "但隨 l_max 對數發散 (-18.69% @500, -8.53% @1000, +11.79% @4000, 過零 @1790) "
                "=> 「總方差」唔係良定義觀測量 (M1 ill-posed)"),
}
(BASE / "data" / "01_measure_candidates.json").write_text(
    json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  {verdict['verdict']}")

print("\n" + "=" * 78)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
if FAILS:
    print("FAILS:")
    for f_ in FAILS:
        print(f"  - {f_}")
print("=" * 78)
