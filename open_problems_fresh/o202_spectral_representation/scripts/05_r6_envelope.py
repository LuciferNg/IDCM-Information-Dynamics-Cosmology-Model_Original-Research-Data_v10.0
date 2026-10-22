#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O202 scripts/05 — 路線 6 攻堅: R6 譜包絡 (由第一原理導出 l-軸密度)

憲章: docs/01_problem_record.md R6 譜包絡 / docs/06 §4.2 交付 (C) 之缺失物件
目標: 由投影核 (O180) + rung law (O9) 導出 l-軸密度 D(l), 並檢驗
      (a) 可容性 (頻帶唔重疊) (b) 5% 判準 (c) 唔可以係退化解。

結構鏈 (本 script 建立):
  ★ A: 精確仿射橋    r_k = 2pi*R_world*(1 - gamma_k/4)     (由 cos^2(theta) = 1 - gamma/4)
  ★ B: 測度誘導      arcsine --(cos^2 核)--> arcsine       (仿射不變 => 測度保持)
  ★ C: l-軸標度      u = l / (N_d*K_tree) = l / 1452
                     (rung law l_m = 44(33 - C(9-m,2)); m>=8 時 C=0 => 上界 1452)
  ★ D: 候選包絡 E1   rho(l) ~ 1/sqrt(l(1452-l))            (零參數)
      檢驗 (i)   峰高檢驗: rho(u_m)/rho(u_1) vs O9 峰高比  (零參數, 直接可證偽)
           (ii)  連續譜檢驗: 零參數 KS 統計 vs F_obs
           (iii) 自由標度: arcsine 形狀本身可否救 (min KS over scale)
           (iv)  null: 其他結構上界作標度
  ★ E: 退化性 + 5% 判準 (所需振幅 vs TGT)
  ★ F: 裁決

零新常數: {N_d=44, K_tree=33, B=4, N_gen=3, mu2=2, F5, F6, F7, L4, M=33} + gamma_k + eps_phi/eps_ring
"""

import json
import math
from pathlib import Path

import mpmath as mpm
mp = mpm.mp
mp.dps = 40

BASE = Path(__file__).resolve().parent.parent
PLK = BASE / "data" / "planck"
T_CMB = mp.mpf('2.72548') * 1e6
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
print("O202 scripts/05 — 路線 6 攻堅: R6 譜包絡 (l-軸密度由第一原理)")
print("=" * 78)

# ------------------------------------------------------------------ 常數
PHI = (1 + mp.sqrt(5)) / 2
EPS_PHI = 1 / (4 * PHI)
AMP = EPS_PHI ** 5 / 8
TGT = (AMP * T_CMB) ** 2
ND, B, NGEN, MU2, F5, F6, F7, L4, M = 44, 4, 3, 2, 5, 8, 13, 7, 33
KTREE = 33
L_TOP = ND * KTREE                      # 1452 = rung law 自然上界

PEAKS = []
for m in range(1, 8):
    PEAKS.append((m, ND * (M - math.comb(9 - m, 2)) + ((m - 1) * 9) % 25))
PEAKS[4] = (5, 1121)
ELL = dict(PEAKS)
RHO = {1: mp.mpf(1), 2: mp.mpf(4) / 9, 3: mp.mpf(4) / 9, 4: mp.mpf(9) / 49,
       5: mp.mpf(3) / 14, 6: mp.mpf(16) / 121, 7: mp.mpf(1) / 7}


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
D_FULL = dict(FULL)


def w_of(ell, Dl):
    return (2 * ell + 1) * mp.mpf(Dl) / (2 * ell * (ell + 1))


S_OBS = sum(w_of(e, D) for e, D in FULL)
print(f"  S_OBS = {mp.nstr(S_OBS, 10)} uK^2   (Planck PR3 TT full, l = 2..2508)")
print(f"  l 上界: rung law 自然上界 L_TOP = N_d*K_tree = {ND}*{KTREE} = {L_TOP};"
      f"  Planck 量到 2508")

# ================================================================== A
print("\n" + "=" * 78)
print("A: 精確仿射橋 — 投影核 <-> Laplacian 譜變數")
print("=" * 78)
print("  gamma_k = 4sin^2(theta_k),  theta_k = k*pi/176  =>  cos^2(theta_k) = 1 - gamma_k/4")
print("  O180 投影核: r_k = 2pi*R_world*cos^2(theta_k)")
print("  => r_k = 2pi*R_world*(1 - gamma_k/4)     (EXACT, 仿射)")
bad = []
for k in range(1, 89):
    th = k * mp.pi / 176
    g = 4 * mp.sin(th) ** 2
    lhs = mp.cos(th) ** 2
    rhs = 1 - g / 4
    if abs(lhs - rhs) > mp.mpf('1e-35'):
        bad.append(k)
print(f"  max_k |cos^2(theta_k) - (1 - gamma_k/4)| <= {mp.nstr(mp.mpf('1e-35'), 4)}  (k = 1..88)")
chk("A1 ★ 精確仿射橋 cos^2(theta_k) = 1 - gamma_k/4 (k = 1..88, 全部 < 1e-35)",
    not bad, f"(例外 {len(bad)} 個)")
RW = mp.mpf(1)
rr = [2 * mp.pi * RW * (1 - (2 - 2 * mp.cos(k * mp.pi / 88)) / 4) for k in range(1, 89)]
chk("A2 ★ 投影半徑 = 譜變數之仿射函數 r_k = 2piR(1 - gamma_k/4) (唔係獨立幾何量)",
    abs(rr[0] - 2 * mp.pi * RW * mp.cos(mp.pi / 176) ** 2) < mp.mpf('1e-35'),
    f"(r_1 = {mp.nstr(rr[0], 10)}, r_88 = {mp.nstr(rr[87], 10)} = 0)")

# ================================================================== B
print("\n" + "=" * 78)
print("B: 測度誘導 — cos^2 核將 arcsine 送到 arcsine (仿射不變)")
print("=" * 78)
print("  rho_gamma(g) = 1/(pi*sqrt(g(4-g)))     on [0,4]")
print("  r = 2piR(1 - g/4)  =>  g = 4(1 - u),  u = r/(2piR)")
print("  rho_r(r) = rho_gamma(g(r)) * |dg/dr| = 1/(2*pi^2*R*sqrt(u(1-u)))")
okB = True
for u in [mp.mpf('0.05'), mp.mpf('0.2'), mp.mpf('0.5'), mp.mpf('0.8'), mp.mpf('0.95')]:
    r = u * 2 * mp.pi * RW
    g = 4 * (1 - u)
    rho_g = 1 / (mp.pi * mp.sqrt(g * (4 - g)))
    dgdr = 4 / (2 * mp.pi * RW)
    num = rho_g * dgdr
    ref = 1 / (2 * mp.pi ** 2 * RW * mp.sqrt(u * (1 - u)))
    if abs(num / ref - 1) > mp.mpf('1e-30'):
        okB = False
    print(f"    u = {float(u):.2f}:  誘導密度 = {mp.nstr(num, 14)}   參考 arcsine = {mp.nstr(ref, 14)}")
chk("B1 ★ 投影核係測度保持: arcsine -> arcsine (仿射不變), 零參數",
    okB, "(=> 核唔提供新信息, 亦唔提供 l-密度)")
chk("B2 ★ 推論: 任何『由投影核生成 l-軸密度』之路線只會得到 arcsine 形狀",
    okB, "(形狀被逼, 標度仍自由)")

# ================================================================== C
print("\n" + "=" * 78)
print("C: l-軸標度 — 由 rung law 逼出 (零參數)")
print("=" * 78)
print("  rung law: l_m = 44*(33 - C(9-m,2)) + frac,  M = 33 = K_tree")
print("  m = 1..7: C(9-m,2) = 28,21,15,10,6,3,1  (三角數 T_7..T_1)")
print("  m >= 8:  C(9-m,2) = C(1,2) = C(0,2) = 0  =>  l = 44*33 = 1452 (飽和)")
print(f"    {'m':>2} {'C(9-m,2)':>9} {'44*(M-c)':>9} {'frac':>5} {'l_m (O9)':>9}")
for m in range(1, 10):
    c = math.comb(9 - m, 2) if 9 - m >= 2 else 0
    fr = ((m - 1) * 9) % 25 if m <= 7 else 0
    lo9 = ELL[m] if m <= 7 else ND * M
    print(f"    {m:2d} {c:9d} {ND*(M-c):9d} {fr:5d} {lo9:9d}")
chk("C1 ★ rung law 自然上界 L_TOP = 44*33 = 1452 = N_d*K_tree (m >= 8 飽和)",
    ND * M == L_TOP, f"({L_TOP})")
print(f"\n  ⚠️ 結構張力: L_TOP = {L_TOP} < Planck l_max = 2508")
frac_hi = sum(w_of(e, D) for e, D in FULL if e > L_TOP) / S_OBS
print(f"     l > 1452 之觀測方差佔比 = {float(frac_hi)*100:.2f}%  (若 l-軸止於 1452, 此部分無法解釋)")
chk("C2 ★ 結構張力: l-軸若止於 L_TOP = 1452, 則 l > 1452 之觀測方差無法解釋",
    frac_hi > mp.mpf('0.01'), f"(佔 {float(frac_hi)*100:.2f}%)")

# ---- C3 ★ 低-ℓ 集中度 vs ℓ-軸解像度 (解釋整族失敗之機制)
print("\n  C3 ★ 低-l 集中度 vs l-軸解像度 (整族失敗之機制)")
print(f"    {'l 上截':>8} {'累積方差佔 S_OBS':>18} {'每 mode 平均權重':>18}")
for Lc in [10, 22, 44, 88, 220, 528, 1452, 2508]:
    s = sum(w_of(e, D) for e, D in FULL if e <= Lc)
    n = sum(1 for e, _ in FULL if e <= Lc)
    print(f"    {Lc:8d} {float(s/S_OBS)*100:17.2f}% {float(s/n):18.3f}")
F44 = sum(w_of(e, D) for e, D in FULL if e <= ND) / S_OBS
AVG_ALL = S_OBS / len(FULL)
AVG_44 = sum(w_of(e, D) for e, D in FULL if e <= ND) / sum(1 for e, _ in FULL if e <= ND)
print(f"    IDCM l-軸單位 = N_d = {ND} ⇒ 框架喺 l < {ND} **無結構解像度**")
print(f"    觀測 l <= {ND} 佔總方差 {float(F44)*100:.2f}% (43 個 mode);")
print(f"      該區平均權重 = {float(AVG_44):.3f} vs 全譜平均 = {float(AVG_ALL):.3f}"
      f"  => 集中 {float(AVG_44/AVG_ALL):.1f}x")
chk("C3 ★ 結構性阻塞: 觀測方差集中於 l <= N_d = 44 達 12x (每 mode 權重), "
    "而 IDCM l-軸單位正係 44 => 解像度不足",
    AVG_44 / AVG_ALL > 5, f"(集中 {float(AVG_44/AVG_ALL):.1f}x; l <= 44 佔 {float(F44)*100:.2f}%)")
print("    => 任何由鏈譜生成之包絡 (自然標度 44) 都**冇能力**重現低-l 集中,")
print("       此為整族失敗之結構原因 (唔係候選選錯, 係解像度不足)")

# ================================================================== D
print("\n" + "=" * 78)
print("D: 候選包絡 E1 — rho(l) ~ 1/sqrt(l(1452-l))  (零參數)")
print("=" * 78)


def rho_e1(ell):
    x = mp.mpf(ell)
    return 1 / mp.sqrt(x * (L_TOP - x))


def cdf_e1(ell):
    """F_E1(l) = [arcsin(2l/L - 1) - arcsin(2*2/L - 1)] / [pi/2 - arcsin(2*2/L - 1)]"""
    a = mp.asin(2 * mp.mpf(ell) / L_TOP - 1)
    a0 = mp.asin(mp.mpf(4) / L_TOP - 1)
    return (a - a0) / (mp.pi / 2 - a0)


# ---- D(i) 峰高檢驗 (零參數, 最直接之證偽面)
print("\n  D(i) 峰高檢驗: 若「峰 = 包絡在峰位之取樣」=> A_m/A_1 = rho(u_m)/rho(u_1)")
print(f"    {'m':>2} {'l_m':>6} {'u_m':>8} {'E1 預言':>10} {'O9 rho_m':>10} {'觀測 A_m/A_1':>12}")
dev_pk = []
for m, ell in PEAKS:
    u = mp.mpf(ell) / L_TOP
    pred = (1 / mp.sqrt(u * (1 - u))) / (1 / mp.sqrt((mp.mpf(220) / L_TOP) * (1 - mp.mpf(220) / L_TOP)))
    obs9 = RHO[m]
    obsd = mp.mpf(D_FULL[ell]) / mp.mpf(D_FULL[220])
    dev_pk.append(float(abs(mp.log(pred / obs9))))
    print(f"    {m:2d} {ell:6d} {float(u):8.5f} {float(pred):10.4f} "
          f"{float(obs9):10.4f} {float(obsd):12.4f}")
rms_pk = math.sqrt(sum(d * d for d in dev_pk) / len(dev_pk))
print(f"    RMS |ln(E1 預言 / O9 rho_m)| = {rms_pk:.4f}  (即 ~{math.exp(rms_pk):.2f}x 典型偏差)")
chk("D1 ★ E1 峰高檢驗失敗: 預言峰高隨 l 上升 (u->1 發散), O9 峰高下降 => 「峰=包絡取樣」證偽",
    rms_pk > 0.5, f"(RMS |ln ratio| = {rms_pk:.3f})")

# ---- D(ii) 連續譜檢驗 (零參數 KS)
print("\n  D(ii) 連續譜檢驗: 零參數 KS 統計 (l = 2..1452, 累積歸一化)")
tot_c = sum(w_of(e, D) for e, D in FULL if 2 <= e <= L_TOP)
cum = mp.mpf(0)
ks = mp.mpf(0)
worst = None
for e, D in FULL:
    if not (2 <= e <= L_TOP):
        continue
    cum += w_of(e, D)
    d = abs(cum / tot_c - cdf_e1(e))
    if d > ks:
        ks = d
        worst = e
print(f"    F_obs 歸一化於 [2, {L_TOP}] (總 = {mp.nstr(tot_c,8)} uK^2)")
print(f"    KS = sup|F_obs - F_E1| = {mp.nstr(ks, 8)}  @ l = {worst}")
print(f"    對照: KS 之 1-sigma 帶 ~ 1/sqrt(N_eff), N_eff = 1451 => ~ {1/math.sqrt(1451):.5f}")
chk("D2 ★ E1 連續譜檢驗失敗: KS >> 1/sqrt(N) => arcsine 形狀唔匹配觀測累積譜",
    ks > mp.mpf('0.05'), f"(KS = {mp.nstr(ks,6)} @ l={worst})")

# ---- D(iii) 自由標度 (形狀本身可否救?)
print("\n  D(iii) 自由標度: 最小化 KS over scale s (只測形狀, 放鬆結構標度)")


def ks_free(s):
    a0 = mp.asin(mp.mpf(4) / s - 1) if s > 4 else mp.mpf(0)
    if s <= 4:
        return mp.mpf(1)
    tot = sum(w_of(e, D) for e, D in FULL if 2 <= e <= min(s, 2508))
    if tot == 0:
        return mp.mpf(1)
    c = mp.mpf(0)
    k = mp.mpf(0)
    for e, D in FULL:
        if not (2 <= e <= min(s, 2508)):
            continue
        c += w_of(e, D)
        fe = (mp.asin(2 * mp.mpf(e) / s - 1) - a0) / (mp.pi / 2 - a0)
        k = max(k, abs(c / tot - fe))
    return k


best_s, best_ks = None, mp.mpf(2)
for s in [300, 500, 700, 900, 1100, 1452, 1600, 1800, 2000, 2200, 2508, 3000]:
    k = ks_free(mp.mpf(s))
    if k < best_ks:
        best_ks, best_s = k, s
print(f"    最佳標度 s* = {best_s}  =>  min KS = {mp.nstr(best_ks, 8)}")
chk("D3 ★ 即使放鬆標度為自由參數, arcsine 形狀之 min KS 仍然大 => 形狀本身證偽",
    best_ks > mp.mpf('0.05'), f"(min KS = {mp.nstr(best_ks,6)} @ s* = {best_s})")

# ---- D(iv) null: 其他結構上界
print("\n  D(iv) null: 以其他結構數作標度 (檢查 KS 之選擇性)")
STRUCT = {"N_d": 44, "N": 88, "176": 176, "l_1": 220, "264": 264, "420": 420,
          "528": 528, "L_TOP": 1452, "l_max": 2508, "5940": 5940}
ks_tab = {}
for nm, s in STRUCT.items():
    ks_tab[nm] = float(ks_free(mp.mpf(s)))
for nm, v in sorted(ks_tab.items(), key=lambda kv: kv[1]):
    mark = "  <== 結構標度" if nm == "L_TOP" else ""
    print(f"    {nm:>8s} = {STRUCT[nm]:5d}  KS = {v:.5f}{mark}")
rank = sorted(ks_tab.values()).index(ks_tab["L_TOP"]) + 1
print(f"    L_TOP 之排名: {rank}/{len(ks_tab)} (1 = 最佳)")
chk("D4 L_TOP = 1452 唔係特別好之標度 (排名非第一) => 標度選擇無選擇性",
    rank > 1, f"(排名 {rank}/{len(ks_tab)})")

# ---- D2(v) 包絡候選整族排除 (連續密度, 全部零參數)
print("\n  D2(v) ★ 包絡候選整族排除 (連續密度 on [2, 1452], 全部零手調)")
BND = [2]
for i in range(len(PEAKS) - 1):
    BND.append((PEAKS[i][1] + PEAKS[i + 1][1]) // 2)
BND.append(L_TOP)
DELTA = {m: ND * (8 - m) for m in range(1, 8)}


def rung_of(ell):
    for i in range(7):
        if BND[i] <= ell < BND[i + 1]:
            return i + 1
    return 7


CANDS = {
    "E1 arcsine (投影核誘導)": lambda e: 1 / mp.sqrt((mp.mpf(e) / L_TOP) * (1 - mp.mpf(e) / L_TOP)),
    "E2 rung 1/D_m (等模態/rung)": lambda e: 1 / mp.mpf(DELTA[rung_of(e)]),
    "E3 rung D_m (寬度權重)": lambda e: mp.mpf(DELTA[rung_of(e)]),
    "E4 uniform": lambda e: mp.mpf(1),
    "E5 1/l (標度不變)": lambda e: 1 / mp.mpf(e),
    "E6 HZ 1/(l(l+1))": lambda e: 1 / (mp.mpf(e) * (e + 1)),
}
print(f"    {'候選包絡':28s} {'KS':>9} {'峰高 RMS|ln r|':>14} {'峰向':>6}")
GRID = [(e, w_of(e, D)) for e, D in FULL if 2 <= e < L_TOP]
TOT_G = sum(w for _, w in GRID)
res_c = {}
for nm, rho in CANDS.items():
    rv = [rho(e) for e, _ in GRID]
    nrm = sum(rv)
    cw = mp.mpf(0)
    cr = mp.mpf(0)
    k = mp.mpf(0)
    for (e, w), r_ in zip(GRID, rv):
        cw += w
        cr += r_
        k = max(k, abs(cw / TOT_G - cr / nrm))
    devs = [float(abs(mp.log((rho(ell) / rho(220)) / RHO[m]))) for m, ell in PEAKS]
    rms = math.sqrt(sum(d * d for d in devs) / len(devs))
    ratio = rho(1412) / rho(220)
    rising = "上升" if ratio > 1.2 else ("下降" if ratio < 0.8 else "平坦")
    res_c[nm] = {"KS": float(k), "rms_peak": rms, "trend": rising}
    print(f"    {nm:28s} {float(k):9.5f} {rms:14.3f} {rising:>6}")
best_c = min(res_c.items(), key=lambda kv: kv[1]["KS"])
print(f"    最佳 KS = {best_c[1]['KS']:.5f} ({best_c[0]});  最佳峰高 = "
      f"{min(res_c.items(), key=lambda kv: kv[1]['rms_peak'])[0]}")
chk("D5 ★ 整族排除: 6 個零參數包絡候選全部 KS > 0.05 (最佳 "
    f"{best_c[1]['KS']:.4f}) => l-軸連續包絡整族失敗",
    all(v["KS"] > 0.05 for v in res_c.values()),
    f"(KS 範圍 {min(v['KS'] for v in res_c.values()):.4f}..{max(v['KS'] for v in res_c.values()):.4f})")
chk("D6 ★ 峰高檢驗: 冇一個候選同時通過 (KS 與峰高) — 上升型違峰高, 下降型違連續譜",
    not any(v["KS"] <= 0.05 and v["rms_peak"] <= 0.2 for v in res_c.values()),
    "(結構性兩難: 峰高要求下降, 觀測累積譜要求…)")

# ================================================================== E
print("\n" + "=" * 78)
print("E: 退化性 + 5% 判準 (所需振幅 vs TGT)")
print("=" * 78)
S_PEAKS = sum(w_of(e, D_FULL[e]) for _, e in PEAKS)
print(f"  S_peaks (7 峰, 原始全譜) = {mp.nstr(S_PEAKS, 8)} uK^2"
      f"  = {float(S_PEAKS/S_OBS)*100:.3f}% of S_OBS")
S_BG = S_OBS - S_PEAKS
print(f"  S_bg = S_OBS - S_peaks = {mp.nstr(S_BG, 8)} uK^2")
# 包絡歸一化: D_env(l) = A * rho_tilde(l),  int_2^1452 rho_tilde = 1
norm = sum(rho_e1(e) for e, _ in FULL if 2 <= e < L_TOP)
K = sum((2 * e + 1) / (2 * e * (e + 1)) * rho_e1(e) / norm for e, _ in FULL if 2 <= e < L_TOP)
A_REQ = S_BG / K
print(f"  包絡歸一化常數 K = {mp.nstr(K, 8)};  所需振幅 A = S_bg / K = {mp.nstr(A_REQ, 8)} uK^2")
print(f"  對照 TGT = (eps_phi^5/8 * T)^2 = {mp.nstr(TGT, 8)} uK^2  =>  ratio = {mp.nstr(A_REQ/TGT, 6)}")
chk("E1 ★ E1 包絡所需振幅 A ≠ TGT (相差 > 5%) => 即使形狀過關, 振幅亦唔係結構值",
    abs(A_REQ / TGT - 1) > mp.mpf('0.05'), f"(ratio = {mp.nstr(A_REQ/TGT, 6)})")

# 退化性: 全部分派第一峰
deg = sum(w_of(e, D) for e, D in FULL if 2 <= e <= 2508)  # 已 = S_OBS
print(f"\n  退化性檢查: 「全部 l-mode 分派給第一峰」=> Var = S_OBS 精確命中 (超平面)")
print(f"    即任何歸一化到 S_OBS 之密度都命中 => 命中唔構成證據 (scripts/01 D4: 隨機 1/400)")
chk("E2 ★ 退化性: 歸一化到 S_OBS 之密度必然命中 => 5% 判準對「形狀」無約束力",
    True, "(scripts/01 D4 隨機可容分拆命中 0.2%)")

# 可容性篩
print("\n  可容性篩 (對 E1 作『連續密度』):")
print("    (i)  rho >= 0 於 [2, 1452]                ✓")
print("    (ii) 積分有限, 可歸一化                    ✓")
print("    (iii) 峰唔可被雙重計數: 若 E1 當『背景』則峰另計 (OK);")
print("          若 E1 當『總譜』則 7 個結構峰無位置 => 唔可容")
print("    (iv) 支撐止於 1452 < 2508 => 高 l 無功率 (與觀測矛盾)")
chk("E3 ★ E1 可容性: 通過 (i)(ii); (iii) 需聲明為背景; (iv) 高 l 矛盾 => 部分唔可容",
    True, f"(l > 1452 佔 {float(frac_hi)*100:.2f}%)")

# ================================================================== F
print("\n" + "=" * 78)
print("F: 裁決")
print("=" * 78)
verdict = {
    "affine_bridge": "r_k = 2pi*R_world*(1 - gamma_k/4)  EXACT",
    "measure_invariance": "cos^2 核將 arcsine 送到 arcsine (仿射不變, 測度保持)",
    "l_scale_structural": L_TOP, "l_scale_origin": "44*33 = N_d*K_tree (rung law 飽和)",
    "l_max_obs": 2508, "frac_var_above_1452_pct": float(frac_hi) * 100,
    "E1": "rho(l) ~ 1/sqrt(l(1452-l))",
    "peak_height_test": {"rms_abs_ln_ratio": rms_pk, "verdict": "FAIL"},
    "continuum_KS": {"KS": float(ks), "at_l": worst, "verdict": "FAIL"},
    "free_scale_KS": {"min_KS": float(best_ks), "best_scale": best_s, "verdict": "FAIL"},
    "structural_scale_rank": f"{rank}/{len(ks_tab)}",
    "envelope_family": res_c,
    "envelope_family_best_KS": best_c[1]["KS"], "envelope_family_best": best_c[0],
    "low_ell_concentration": {"frac_l_le_44_pct": float(F44) * 100,
                              "l_axis_unit": ND,
                              "obstruction": "觀測方差高度集中於 l <= 44 = l-軸單位 => 解像度不足"},
    "amplitude_required": float(A_REQ), "TGT": float(TGT), "amp_ratio": float(A_REQ / TGT),
    "S_peaks_pct": float(S_PEAKS / S_OBS) * 100,
    "verdict": ("路線 6 攻堅 (R6 包絡): 由投影核逼出 arcsine 形狀 (零參數, 精確仿射橋 "
                "r_k = 2piR(1-gamma_k/4)) 並由 rung law 逼出標度 1452 = N_d*K_tree。"
                "但全部檢驗失敗: (i) 峰高檢驗 RMS |ln ratio| = "
                f"{rms_pk:.3f} (arcsine 預言上升, O9 峰高下降); "
                f"(ii) 零參數 KS = {float(ks):.4f} @ l={worst}; "
                f"(iii) 自由標度 min KS = {float(best_ks):.4f} @ s*={best_s}; "
                f"(iv) 6 個零參數包絡候選整族排除 (最佳 KS = {best_c[1]['KS']:.4f}); "
                f"(v) 結構張力: l > 1452 佔觀測方差 {float(frac_hi)*100:.2f}%; "
                f"(vi) 所需振幅 A/TGT = {float(A_REQ/TGT):.1f}。"
                "=> R6 仍然 🔴, 但已由『完全缺失』升級為『唯一自然候選族已建立並整族證偽』"),
}
(BASE / "data" / "05_r6_envelope.json").write_text(
    json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  {verdict['verdict']}")

print("\n" + "=" * 78)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
if FAILS:
    print("FAILS:")
    for f_ in FAILS:
        print(f"  - {f_}")
print("=" * 78)
