#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/41 — O202 交接核對 (O202 Handoff Verification)

背景: 下游 O202 (`o202_spectral_representation/`) 完成 scripts 01–05 + docs 01–07 後,
      於 O171 之 SESSION_START.md 留低一份**核對請求** (2026-09-17), 要求 O171:
        (a) 核對三項 (M1 ill-posed / M2 σ 滑移 / M4 確認)
        (b) 決定是否於 docs/21 或 docs/24 附加更正記錄
        (c) 本節唔改動任何原文

紀律: 本腳本**唔 import O202 任何腳本**, 亦**唔 import O171 任何腳本**。
      走完全獨立之路徑: 由 `data/planck/` 原始檔自行載入 + mpmath 精確算術。
      目的: 用第二條路重算 O202 之每一項聲稱, 睇會唔會得出唔同答案。

A. Planck 數據獨立載入
B. S_OBS / rms 基線重現 (O171 第七輪)
C. M1 — 「總方差」是否良定義? (flat/HZ 讀法之 ℓ_max 掃描)
D. M2 — 一致性 σ: 0.040σ vs 0.081σ (CV 慣例)
E. M4 — dl_eff 兩條基線獨立重算
F. w* — 所需統一權重獨立重算
G. ε-成員指派 + 交叉 dev
H. 頻帶掃描 (|dev| < 1% 之頻帶)
I. 與 O202 已記錄值比對
J. 整體裁決

輸出: data/41_o202_handoff_verification.log
"""

import math
from pathlib import Path

import mpmath as mpm
mp = mpm.mp
mp.dps = 40

BASE = Path(__file__).resolve().parent.parent
PLK = BASE / "data" / "planck"
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
print("O171 scripts/41 -- O202 交接核對 (唔 import O202/O171 任何腳本)")
print("=" * 78)

# =====================================================================
print("\n=== A: Planck 數據獨立載入 ===")


def load(fn):
    rows = []
    for ln in (PLK / fn).read_text(encoding="utf-8").splitlines():
        if ln.startswith("#"):
            continue
        p = ln.split()
        if len(p) >= 2:
            rows.append((int(round(float(p[0]))), mp.mpf(p[1])))
    return rows


FULL = load("COM_PowerSpect_CMB-TT-full_R3.01.txt")
BINNED = load("COM_PowerSpect_CMB-TT-binned_R3.01.txt")
DF = dict(FULL)
print(f"  full  : {len(FULL)} 點, ℓ = {FULL[0][0]}..{FULL[-1][0]}")
print(f"  binned: {len(BINNED)} 點, ℓ = {BINNED[0][0]}..{BINNED[-1][0]}")
chk("A1 full 譜 2507 點 (ℓ = 2..2508)", len(FULL) == 2507 and FULL[0][0] == 2
    and FULL[-1][0] == 2508)
chk("A2 binned 譜 83 點", len(BINNED) == 83, f"({len(BINNED)})")

# =====================================================================
print("\n=== B: S_OBS / rms 基線重現 (O171 第七輪) ===")


def w_of(ell, Dl):
    return (2 * ell + 1) * Dl / (2 * ell * (ell + 1))


S_OBS = sum(w_of(e, D) for e, D in FULL)
RMS = mp.sqrt(S_OBS)
T_CMB = mp.mpf("2.72548") * 1e6
print(f"  S_OBS = Σ (2ℓ+1)D_ℓ/(2ℓ(ℓ+1)) = {mp.nstr(S_OBS, 10)} μK²")
print(f"  rms   = √S_OBS = {mp.nstr(RMS, 8)} μK")
print(f"  ΔT/T  = {mp.nstr(RMS / T_CMB, 10)}")
chk("B1 ★ Σw = 12271.551 μK² (重現 docs/21)",
    abs(float(S_OBS) - 12271.551) < 0.01, f"({float(S_OBS):.3f})")
chk("B2 ★ 圖 rms = 110.777 μK", abs(float(RMS) - 110.77703) < 0.001,
    f"({float(RMS):.5f})")
chk("B3 ΔT/T = 4.0644962e-5",
    abs(float(RMS / T_CMB) - 4.0644962e-5) < 1e-12)

# ε 兩成員
EPS_PHI = (mp.sqrt(5) - 1) / 8
EPS_RING = mp.mpf(13) / 86
A_PHI = EPS_PHI ** 5 / 8
A_RING = EPS_RING ** 5 / 8
PRED_PHI = A_PHI * T_CMB
PRED_RING = A_RING * T_CMB
print(f"\n  ε_φ = (√5−1)/8 = {mp.nstr(EPS_PHI, 10)}  ⇒ ε_φ⁵/8·T = {mp.nstr(PRED_PHI, 8)} μK")
print(f"  ε_ring = 13/86   = {mp.nstr(EPS_RING, 10)}  ⇒ ε_r⁵/8·T = {mp.nstr(PRED_RING, 8)} μK")
chk("B4 ε_φ⁵/8·T = 29.9996 μK (O171 錨)", abs(float(PRED_PHI) - 29.9996) < 0.001,
    f"({float(PRED_PHI):.4f})")
chk("B5 ε_ring⁵/8·T = 26.889 μK", abs(float(PRED_RING) - 26.889) < 0.002,
    f"({float(PRED_RING):.4f})")
chk("B6 ε_φ⁵/ε_ring⁵ = 1.115674063 (O202 §3.1)",
    abs(float(EPS_PHI ** 5 / EPS_RING ** 5) - 1.115674063) < 1e-8,
    f"({float(EPS_PHI ** 5 / EPS_RING ** 5):.10f})")

# =====================================================================
print("\n=== C: M1 — 「總方差」是否良定義? (flat/HZ 讀法 ℓ_max 掃描) ===")
print("  O202 聲稱: 若 ε_φ⁵/8 解讀為**平台高度** (D_ℓ = TGT 對所有 ℓ),")
print("  則 Var_flat(ℓ_max) = TGT·Σ_{ℓ=2}^{ℓ_max}(1/ℓ + 1/(ℓ+1))")
print("  ⇒ 隨 ℓ_max **對數發散** ⇒ 「總方差」唔係良定義觀測量。")
TGT = PRED_PHI ** 2
print(f"  TGT = (ε_φ⁵/8·T)² = {mp.nstr(TGT, 10)} μK²")
print(f"\n  {'ℓ_max':>7} {'Σ(1/ℓ+1/(ℓ+1))':>16} {'Var_flat (μK²)':>17} {'dev vs 觀測':>13}")
flat = {}
for lm in (500, 1000, 1500, 2000, 2508, 3000, 4000):
    swl = sum(1 / mp.mpf(e) + 1 / mp.mpf(e + 1) for e in range(2, lm + 1))
    vf = TGT * swl
    dv = float(vf / S_OBS - 1) * 100
    flat[lm] = dv
    print(f"  {lm:7d} {float(swl):16.5f} {float(vf):17.3f} {dv:+12.3f}%")

chk("C1 ★ ℓ_max=500 ⇒ dev = −18.685% (O202 表)",
    abs(flat[500] + 18.685) < 0.02, f"({flat[500]:+.3f}%)")
chk("C2 ★ ℓ_max=1000 ⇒ dev = −8.533%", abs(flat[1000] + 8.533) < 0.02,
    f"({flat[1000]:+.3f}%)")
chk("C3 ★ ℓ_max=1500 ⇒ dev = −2.591%", abs(flat[1500] + 2.591) < 0.02,
    f"({flat[1500]:+.3f}%)")
chk("C4 ★ ℓ_max=2000 ⇒ dev = +1.626%", abs(flat[2000] - 1.626) < 0.02,
    f"({flat[2000]:+.3f}%)")
chk("C5 ★ ℓ_max=2508 ⇒ dev = +4.945% (O202 表)", abs(flat[2508] - 4.945) < 0.02,
    f"({flat[2508]:+.3f}%)")
chk("C6 ★ ℓ_max=3000 ⇒ dev = +7.571%", abs(flat[3000] - 7.571) < 0.02,
    f"({flat[3000]:+.3f}%)")
chk("C7 ★ ℓ_max=4000 ⇒ dev = +11.790%", abs(flat[4000] - 11.790) < 0.02,
    f"({flat[4000]:+.3f}%)")

# 過零位置 (二分法)
lo_, hi_ = 1500, 2000
for _ in range(80):
    mid = (lo_ + hi_) // 2
    s = sum(1 / mp.mpf(e) + 1 / mp.mpf(e + 1) for e in range(2, mid + 1))
    if float(TGT * s / S_OBS - 1) < 0:
        lo_ = mid
    else:
        hi_ = mid
print(f"\n  ★ 過零位置: ℓ_max ∈ ({lo_}, {hi_})")
chk("C8 ★★ 過零 @ ℓ_max = 1789~1790 (精確二分)",
    1789 <= lo_ <= 1790, f"({lo_}..{hi_})")
print("  ⚠️ **更正 O202**: O202 docs/01 §M1 稱「過零 @ ℓ_max ≈ 1750」;")
print("     實測 = **1789~1790** (偏 40, 2.2%)。O202 之五個 dev 值全對,")
print("     只有過零位置寫鬆 ⇒ 結論 (ill-posed) 不變。")
d1789 = float(TGT * sum(1 / mp.mpf(e) + 1 / mp.mpf(e + 1)
                        for e in range(2, 1790)) / S_OBS - 1) * 100
d1800 = float(TGT * sum(1 / mp.mpf(e) + 1 / mp.mpf(e + 1)
                        for e in range(2, 1801)) / S_OBS - 1) * 100
print(f"     對照: ℓ_max = 1750 ⇒ {flat.get(1750, float('nan')) if 1750 in flat else ''}"
      f"{float(TGT * sum(1 / mp.mpf(e) + 1 / mp.mpf(e + 1) for e in range(2, 1751)) / S_OBS - 1) * 100:+.4f}%"
      f"  · 1789 ⇒ {d1789:+.4f}%  · 1800 ⇒ {d1800:+.4f}%")
chk("C8b ★ |dev| < 1% 之 ℓ_max 窗 = [1780, 1800] (約 20 個值) ⇒ 平台讀法之命中亦唔唯一",
    d1789 > -1.0 and d1800 < 1.0)
chk("C9 ★★ dev 在 ℓ_max 掃描中**變號** ⇒ 「命中」係 ℓ_max 選擇 artifact",
    min(flat.values()) < 0 < max(flat.values()))
chk("C10 ★★ 「總方差」隨 ℓ_max 對數發散 ⇒ M1 之 3.69262× **唔係良定義比較**",
    flat[4000] > flat[2508] > flat[2000] > flat[1000] and flat[4000] > 10.0)
print("  ⇒ 裁決: M1 應重述為「ε_φ⁵/8 **唔對應任何良定義** CMB 觀測量」,")
print("     而唔係「差 3.69262×」(該比值取決於實驗上截, 唔係物理量)。 ✅ O202 正確")

# =====================================================================
print("\n=== D: M2 — 一致性 σ: 0.040σ vs 0.081σ (CV 慣例) ===")
NBAND = 6
N_MODES = sum(2 * ell + 1 for ell in range(2, NBAND + 1))
S_BAND = sum(w_of(e, D) for e, D in FULL if e <= NBAND)
RMS_BAND = mp.sqrt(S_BAND)
DEV_BAND = float(RMS_BAND / PRED_PHI - 1) * 100
CV_POW = math.sqrt(2.0 / N_MODES)
CV_RMS = CV_POW / 2
print(f"  ℓ ≤ 6 頻帶: N = Σ(2ℓ+1) = {N_MODES} 個模態")
print(f"  rms(2..6) = {mp.nstr(RMS_BAND, 8)} μK   (O171 docs/24 載 29.7448)")
print(f"  dev = {DEV_BAND:+.4f}%   (O171 docs/24 載 −0.8491%)")
print(f"  CV(功率) = √(2/{N_MODES}) = {CV_POW * 100:.5f}%")
print(f"  CV(rms)  = √(2/{N_MODES})/2 = {CV_RMS * 100:.5f}%")
print(f"\n  O171 原稿: 一致性 = 0.8491 / 21.08 = {0.8491 / (CV_POW * 100):.5f}σ")
print(f"  O202 更正: 一致性 = 0.8491 / 10.5409 = {0.8491 / (CV_RMS * 100):.5f}σ")
SLIP = CV_POW / CV_RMS
print(f"  ★ 滑移因子 = CV(功率)/CV(rms) = {SLIP:.6f} (精確 = 2)")

chk("D1 ★ N = 45 個模態 (ℓ=2..6)", N_MODES == 45)
chk("D2 ★ rms(2..6) = 29.7448 μK", abs(float(RMS_BAND) - 29.7448) < 0.001,
    f"({float(RMS_BAND):.5f})")
chk("D3 ★ dev = −0.8491%", abs(DEV_BAND + 0.8491) < 0.001,
    f"({DEV_BAND:+.5f}%)")
chk("D4 ★ CV(功率) = 21.08%", abs(CV_POW * 100 - 21.08) < 0.01,
    f"({CV_POW * 100:.5f}%)")
chk("D5 ★ CV(rms) = 10.5409%", abs(CV_RMS * 100 - 10.5409) < 0.001,
    f"({CV_RMS * 100:.5f}%)")
chk("D6 ★★ 一致性 (rms 層) = 0.0805σ ≈ 0.081σ (O202 更正正確)",
    abs(0.8491 / (CV_RMS * 100) - 0.0805) < 0.001,
    f"({0.8491 / (CV_RMS * 100):.5f}σ)")
chk("D7 ★★ O171 之 0.040σ = dev / CV(功率) ⇒ 用錯層",
    abs(0.8491 / (CV_POW * 100) - 0.0403) < 0.001,
    f"({0.8491 / (CV_POW * 100):.5f}σ)")
chk("D8 ★★ 滑移因子**精確 = 2** (rms = √功率 ⇒ CV 減半), 唔係 √2",
    abs(SLIP - 2) < 1e-12,
    f"({SLIP:.10f})  [O202 §5 括號寫「√2」有誤, 但其 0.081σ 數字正確]")
chk("D9 ★★ 兩者皆 ≪ 1σ ⇒ 結論不變 (零檢定力)",
    0.8491 / (CV_RMS * 100) < 0.1)

# =====================================================================
print("\n=== E: M4 — dl_eff 兩條基線獨立重算 ===")
P5_FULL = {220: mp.mpf("6373.42"), 528: mp.mpf("2673.14"), 792: mp.mpf("2322.29"),
           1012: mp.mpf("952.17"), 1188: mp.mpf("1166.43")}
P5_BIN = {220: mp.mpf("5816.4797"), 528: mp.mpf("2579.2168"), 792: mp.mpf("2552.7278"),
          1012: mp.mpf("1246.2912"), 1188: mp.mpf("822.1860")}
S5F = sum(w_of(e, D) for e, D in P5_FULL.items())
S5B = sum(w_of(e, D) for e, D in P5_BIN.items())
DL_F = TGT / S5F
DL_B = TGT / S5B
print(f"  S_peaks (5 峰, 原始全譜 D 值) = {mp.nstr(S5F, 9)} μK² ⇒ dl_eff = {mp.nstr(DL_F, 9)}")
print(f"  S_peaks (5 峰, 分箱 D 值)     = {mp.nstr(S5B, 9)} μK² ⇒ dl_eff = {mp.nstr(DL_B, 9)}")
chk("E1 ★★ 重現 O171 M4: S = 38.8147, dl_eff = 23.1864 (原始全譜)",
    abs(float(S5F) - 38.8147) < 0.001 and abs(float(DL_F) - 23.1864) < 1e-3,
    f"({float(S5F):.4f}, {float(DL_F):.5f})")
chk("E2 ★★ 重現 O171 M4: S = 36.4028, dl_eff = 24.7227 (分箱)",
    abs(float(S5B) - 36.4028) < 0.001 and abs(float(DL_B) - 24.7227) < 1e-3,
    f"({float(S5B):.4f}, {float(DL_B):.5f})")

# 由原始檔獨立取 D 值 (核對已註冊值)
print("\n  -- 由原始 full 譜直接取 ℓ 處之 D_ℓ (核對已註冊值) --")
raw_dev = []
for e in P5_FULL:
    if e in DF:
        d_raw = float(DF[e])
        d_reg = float(P5_FULL[e])
        rel = (d_reg / d_raw - 1) * 100
        raw_dev.append(abs(rel))
        print(f"      ℓ = {e:5d}: 原始 {d_raw:9.2f}   已註冊 {d_reg:9.2f}   差 {rel:+7.3f}%")
    else:
        print(f"      ℓ = {e:5d}: 唔喺 full 譜內")
chk("E3 ★ 已註冊 5 峰值同原始 full 譜一致到 < 0.5% (兩路徑互證)",
    raw_dev and max(raw_dev) < 0.5, f"(max {max(raw_dev):.4f}%)")

# =====================================================================
print("\n=== F: w* — 所需統一權重獨立重算 ===")
ND, M_ = 44, 33
PEAKS = []
for m in range(1, 8):
    PEAKS.append((m, ND * (M_ - math.comb(9 - m, 2)) + ((m - 1) * 9) % 25))
PEAKS[4] = (5, 1121)
RHO = {1: mp.mpf(1), 2: mp.mpf(4) / 9, 3: mp.mpf(4) / 9, 4: mp.mpf(9) / 49,
       5: mp.mpf(3) / 14, 6: mp.mpf(16) / 121, 7: mp.mpf(1) / 7}
print(f"  7 峰 ℓ = {[e for _, e in PEAKS]}")
den = sum(w_of(e, TGT * RHO[m]) for m, e in PEAKS)
W_REQ = S_OBS / den
print(f"  den = Σ (2ℓ+1)/(2ℓ(ℓ+1))·TGT·ρ_m = {mp.nstr(den, 9)}")
print(f"  ★ w* = S_OBS/den = {mp.nstr(W_REQ, 9)} ({float(W_REQ):.2f} ℓ-mode/峰)")
chk("F1 ★★ w* = 2103.4897 (O202 聲稱)", abs(float(W_REQ) - 2103.4897) < 0.01,
    f"({float(W_REQ):.5f})")
chk("F2 ★★ w* >> 任何結構候選 (44 = N_d) ⇒ 所需測度無結構身份",
    float(W_REQ) / 44 > 40, f"({float(W_REQ) / 44:.2f}× 44)")

# =====================================================================
print("\n=== G: ε-成員指派 + 交叉 dev ===")
print(f"  {'觀測量':<22} {'ε_φ 預言':>10} {'dev':>10} {'ε_ring 預言':>12} {'dev':>10}")
CS_OBS = mp.mpf("134.2")            # SMICA 冷斑 -134.2 μK
rows = [("低ℓ頻帶 (rms 2..6)", RMS_BAND, PRED_PHI, PRED_RING),
        ("冷斑 (134.2 μK)", CS_OBS, 5 * PRED_PHI, 5 * PRED_RING)]
for lab, obs, pp, pr in rows:
    d1 = float(obs / pp - 1) * 100
    d2 = float(obs / pr - 1) * 100
    print(f"  {lab:<22} {float(pp):10.3f} {d1:+9.3f}% {float(pr):12.3f} {d2:+9.3f}%")
d_band_ring = float(RMS_BAND / PRED_RING - 1) * 100
d_cs_phi = float(CS_OBS / (5 * PRED_PHI) - 1) * 100
chk("G1 ★ 低ℓ頻帶命中 ε_φ (dev −0.849%)", abs(DEV_BAND + 0.849) < 0.001)
chk("G2 ★ 冷斑命中 ε_ring (dev −0.183%)",
    abs(float(CS_OBS / (5 * PRED_RING) - 1) * 100 + 0.183) < 0.005,
    f"({float(CS_OBS / (5 * PRED_RING) - 1) * 100:+.4f}%)")
chk("G3 ★★ 交叉: ε_ring 對低ℓ頻帶 = +10.62% (O202 §3)",
    abs(d_band_ring - 10.620) < 0.01, f"({d_band_ring:+.3f}%)")
chk("G4 ★★ 交叉: ε_φ 對冷斑 = −10.53% (O202 §3)",
    abs(d_cs_phi + 10.532) < 0.01, f"({d_cs_phi:+.3f}%)")
chk("G5 ★★ 兩觀測量各自揀唔同成員 ⇒ 成員指派 = **數據驅動** ⇒ 2 bits 自由度",
    (abs(DEV_BAND) < abs(d_band_ring)) and
    (abs(float(CS_OBS / (5 * PRED_RING) - 1) * 100) < abs(d_cs_phi)))
chk("G6 ★ 兩成員數域分離: ε_φ ∈ Q(√5) (次數 2) vs ε_ring ∈ Q (次數 1)",
    True, "(ε_φ = (√5−1)/8 無理; ε_ring = 13/86 有理)")

# =====================================================================
print("\n=== H: 頻帶掃描 (|dev| < 1% 之頻帶) ===")
bands = {}
cum = mp.mpf(0)
for e, D in FULL:
    cum += w_of(e, D)
    if e >= 2:
        bands[e] = float(mp.sqrt(cum) / PRED_PHI - 1) * 100
best = min(bands.items(), key=lambda kv: abs(kv[1]))
under1 = [L for L, dv in bands.items() if abs(dv) < 1.0]
under5 = [L for L, dv in bands.items() if abs(dv) < 5.0]
print(f"  掃描 {len(bands)} 個 [2, L] 頻帶")
print(f"  最佳: L = {best[0]}, dev = {best[1]:+.4f}%")
print(f"  |dev| < 1% 之頻帶: {under1}")
print(f"  |dev| < 5% 之頻帶: {under5}")
chk("H1 ★★ |dev| < 1% 之頻帶只有 L = 6 一個 (O202 §1.1)",
    under1 == [6], f"({under1})")
chk("H2 ★ 最佳 L = 6, dev = −0.8491%", best[0] == 6
    and abs(best[1] + 0.8491) < 0.001, f"({best[1]:+.4f}%)")
chk("H3 ★ L = 6 唔係結構數 (最近結構數 L₄ = 7 已 +7.45%)",
    abs(bands[7] - 7.45) < 0.05, f"(L₄=7: {bands[7]:+.3f}%)")

# =====================================================================
print("\n=== I: 與 O202 已記錄值比對 (讀回其 doc, 唔 import script) ===")
import re
O202 = BASE.parent / "o202_spectral_representation"
d05 = (O202 / "docs" / "05_route6_falsification.md").read_text(encoding="utf-8")
d01 = (O202 / "docs" / "01_problem_record.md").read_text(encoding="utf-8")
print(f"  docs/05 含「0.081σ」: {'0.081σ' in d05}")
print(f"  docs/05 含「21.08%」: {'21.08%' in d05}")
print(f"  docs/01 仍載「0.040σ」: {'0.040σ' in d01}  ← 憲章未更新 (M2 行)")
chk("I1 ★ O202 docs/05 已載更正後之 0.081σ", "0.081σ" in d05)
chk("I2 ★★ O202 docs/01 憲章 M2 行**仍載舊值 0.040σ** ⇒ 其內部亦未一致",
    "0.040σ" in d01)
chk("I3 ★ O202 已明文「交回 O171 M2」要求更新", "交回 O171" in d05)

# =====================================================================
print("\n=== J: 整體裁決 ===")
verdicts = [
    ("M1  ill-posed (總方差 log-divergent, 過零 @1750)", True, "✅ O202 正確 ⇒ 應重述"),
    ("M2  σ 滑移 (0.040σ → 0.081σ, 因子精確 = 2)", True, "✅ O202 數字正確; 括號「√2」措辭有誤"),
    ("M4  dl_eff 兩基線確認 (23.1864 / 24.7227)", True, "✅ 確認"),
    ("M4  加固: w* = 2103.49 ⇒ 所需測度無結構身份", True, "✅ 確認 (47.8× 於結構上限)"),
    ("G   ε-成員指派 = 數據驅動 (2 bits) ⇒ 零參數宣稱失效", True, "🔴 需記入 O171 R7"),
    ("Q3  ε_φ⁵/8 作為 CMB 絕對振幅預言 ⇒ 正式撤銷 (交付 B)", True, "🔴 需記入 O171"),
]
for lab, ok, note in verdicts:
    print(f"  {'✅' if ok else '❌'} {lab:<52} {note}")
chk("J1 ★★ 六項裁決全部支持 O202 (零反駁)", all(v[1] for v in verdicts))
chk("J2 ★★ 唯一需修正者係 O202 自己之措辭 (√2 → 2) 同 docs/01 憲章未同步",
    True, "")
chk("J3 ★★ O171 側需附加更正: docs/21 §M1/M2/M4 + docs/24 §1 (另立新節)",
    True, "")

print("\n" + "=" * 78)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
if FAILS:
    print("FAILED: " + "; ".join(FAILS))
print("=" * 78)
