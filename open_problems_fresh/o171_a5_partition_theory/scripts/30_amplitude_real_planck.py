#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/30 — Q3 攻堅: 絕對振幅 ε⁵/8 嘅真實 Planck 譜驗證

背景 (docs/18 §3 遺留 🔴 Q3):
  docs/16 §9 斷言「IDCM 有零參數絕對振幅預測 ΔT/T = ε⁵/8 = 1.100707e-5
  (× T_CMB = 29.9996 μK) ⇒ A_s 非自由 ⇒ R7 判別力 107× → 1.93×」。
  但 docs/18 發現「rms ↔ D_ℓ 峰高」歸一化鏈缺 Δℓ 測度 ⇒ 判為結構不相容。

本節用**真實 Planck 2018 TT 全譜** (新下載, PR3 R3.01, ℓ=2..2508) 做三件事:
  (1) 實測 CMB 圖 rms —— 究竟 ε⁵/8 對應邊個觀測量?
  (2) 查 o77 「vs Planck 1.1e-5 (0.06%)」嘅來源
  (3) 反解 Δℓ_eff 並掃描結構身份 + null control

數據: data/planck/COM_PowerSpect_CMB-TT-{full,binned}_R3.01.txt
      (Planck Legacy Archive / IRSA, 官方 PR3 功率譜)
"""

import json
import math
from pathlib import Path

import mpmath as mpm
mp = mpm.mp
mp.dps = 40

BASE = Path(__file__).resolve().parent.parent
PLK = BASE / "data" / "planck"
T_CMB = mp.mpf('2.72548') * 1e6        # μK

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


print("=" * 72)
print("O171 scripts/30 — Q3 攻堅: 絕對振幅 ε⁵/8 嘅真實 Planck 譜驗證")
print("=" * 72)

# ---------------------------------------------------------------- 常數
PHI = (1 + mp.sqrt(5)) / 2
EPS_PHI = 1 / (4 * PHI)                 # 樹/黃金 (docs/17)
EPS_RING = mp.mpf(13) / 86              # 環退化 F₇/(2N_d−2)
B, NGEN, ND, L4, L5, L7 = 4, 3, 44, 7, 11, 29
F5, F7, KTREE, FPROJ, A5 = 5, 13, 33, 17, 60
RMS_PHI = EPS_PHI ** 5 / 8              # 1.100707e-5
RMS_RING = EPS_RING ** 5 / 8

# IDCM 常數庫 (結構量, 供身份掃描)
LIB = {
    "B": 4, "N_gen": 3, "N_d": 44, "L4": 7, "L5": 11, "L7": 29,
    "F5": 5, "F6": 8, "F7": 13, "F8": 21, "F10": 55, "F11": 89,
    "K_tree": 33, "F_proj": 17, "A5": 60, "mu2": 2, "N_gen2": 9,
    "B2": 16, "S_odd": 88, "S_even": 90, "S_all": 178, "N176": 176,
    "d420": 420, "d421": 421, "L10": 123, "n99": 99, "n198": 198,
    "n528": 528, "n22": 22, "n45": 45, "n46": 46, "n34": 34, "n56": 56,
    "n176": 176, "n360": 360, "n720": 720, "a137": 137, "a128": 128,
    "n48": 48, "n12": 12, "n6": 6, "n10": 10, "n27": 27, "n28": 28,
    "n36": 36, "n66": 66, "n78": 78, "n264": 264, "lD": 9055,
    "n180": 180, "n89": 89, "n90": 90, "n44": 44, "n11": 11, "n7": 7,
    "n13": 13, "n29": 29, "n55": 55, "n33": 33, "n17": 17, "n60": 60,
    "n5": 5, "n3": 3, "n4": 4, "n8": 8, "n21": 21, "n2": 2, "n1": 1,
}


# ---------------------------------------------------------------- 載入譜
def load_spectrum(fn, ncol=2):
    rows = []
    for ln in open(fn, encoding="utf-8"):
        if ln.startswith("#"):
            continue
        p = ln.split()
        if len(p) >= ncol:
            rows.append((int(float(p[0])), float(p[1])))
    return rows


FULL = load_spectrum(PLK / "COM_PowerSpect_CMB-TT-full_R3.01.txt")
BINNED = load_spectrum(PLK / "COM_PowerSpect_CMB-TT-binned_R3.01.txt")


def w_of(ell, Dl):
    """w = (2l+1)/(4pi) C_l = (2l+1) D_l / (2 l (l+1))  [μK²]"""
    return (2 * ell + 1) * mp.mpf(Dl) / (2 * ell * (ell + 1))


def sum_w(rows, lo=0, hi=10 ** 9):
    return sum(w_of(e, D) for e, D in rows if lo <= e <= hi)


# ================================================================ A
print("\n=== A: 真實 Planck 2018 TT 全譜 → 實測 CMB 圖 rms ===")
print(f"  數據: {PLK.name}/COM_PowerSpect_CMB-TT-full_R3.01.txt (官方 PR3 R3.01)")
chk("A1 全譜覆蓋 l = 2..2508, 2507 點",
    FULL[0][0] == 2 and FULL[-1][0] == 2508 and len(FULL) == 2507,
    f"(實際 {FULL[0][0]}..{FULL[-1][0]}, n={len(FULL)})")

S_FULL = sum_w(FULL)
RMS_FULL = mp.sqrt(S_FULL)
DTT_FULL = RMS_FULL / T_CMB
print(f"  Σ_ℓ (2ℓ+1)C_ℓ/4π = {mp.nstr(S_FULL, 8)} μK²")
print(f"  ⇒ CMB 圖 rms = {mp.nstr(RMS_FULL, 8)} μK")
print(f"  ⇒ ΔT/T = {mp.nstr(DTT_FULL, 8)}")
chk("A2 全譜 Σw ≈ 12271.6 μK² (圖變異)", abs(float(S_FULL) - 12271.55) < 0.05,
    f"({float(S_FULL):.3f})")
chk("A3 ⇒ ΔT/T(全圖) = 4.0645e-5", abs(float(DTT_FULL) - 4.06450e-5) < 1e-9,
    f"({float(DTT_FULL):.6e})")

print("\n  ★★ 對比 IDCM 預測:")
print(f"     ε_φ⁵/8    = {mp.nstr(RMS_PHI, 8)}  (= {mp.nstr(RMS_PHI*T_CMB, 8)} μK)")
print(f"     ε_ring⁵/8 = {mp.nstr(RMS_RING, 8)}  (= {mp.nstr(RMS_RING*T_CMB, 8)} μK)")
r_full = DTT_FULL / RMS_PHI
print(f"     ratio 全圖 rms / ε_φ⁵/8 = {mp.nstr(r_full, 8)}  (dev {float(r_full-1)*100:+.2f}%)")
chk("A4 ★ 全圖 rms 比 ε_φ⁵/8 大 3.69× (唔匹配)",
    abs(float(r_full) - 3.69262) < 1e-4, f"({float(r_full):.5f})")

# ================================================================ B
print("\n=== B: o77「vs Planck 1.1e-5 (0.06%)」嘅來源核查 ===")
o77 = BASE.parent / "o77_occam_deep"
src = (o77 / "scripts" / "01_occam_verification.py").read_text(encoding="utf-8")
has_hard = "obs_rms = 1.1e-5" in src
print(f"  o77/scripts/01_occam_verification.py 內 'obs_rms = 1.1e-5' : {has_hard}")
chk("B1 ★ o77 嘅「Planck 1.1e-5」係 hardcode 常數, 非量測值", has_hard)
import re
n_data = len(re.findall(r"loadtxt|genfromtxt|json\.load|open\(", src))
print(f"  o77/scripts/01 內數據載入呼叫數 = {n_data}")
chk("B2 ★ o77/scripts/01 冇載入任何 Planck 頻譜數據", n_data == 0,
    f"(載入數 {n_data})")
# 全圖 rms 對「1.1e-5」嘅偏離
dev_11 = (DTT_FULL / mp.mpf('1.1e-5') - 1) * 100
print(f"  全圖 rms 4.0645e-5 vs 硬編 1.1e-5 ⇒ dev {float(dev_11):+.1f}%")
chk("B3 ★ 聲稱「0.06%」實為 +269.5% (對真圖 rms)", abs(float(dev_11) - 269.5) < 1.0,
    f"({float(dev_11):+.2f}%)")

# ================================================================ C
print("\n=== C: ε⁵/8 對應邊個 ℓ-band? (band 依賴性掃描) ===")
bands = [(2, 5), (2, 7), (2, 10), (2, 15), (2, 20), (2, 30), (2, 50),
         (2, 100), (2, 200), (2, 2508), (2, 2508)]
seen = set()
print(f"  {'band':>12} {'Σw (μK²)':>12} {'ΔT/T':>12} {'dev vs ε_φ⁵/8':>14}")
for lo, hi in bands:
    if (lo, hi) in seen:
        continue
    seen.add((lo, hi))
    c = sum_w(FULL, lo, hi)
    d = mp.sqrt(c) / T_CMB
    dv = (d / RMS_PHI - 1) * 100
    print(f"  {f'{lo}..{hi}':>12} {float(c):12.2f} {float(d):12.6e} {float(dv):+13.2f}%")

c_2_5 = sum_w(FULL, 2, 5)
c_2_7 = sum_w(FULL, 2, 7)
d_2_5 = mp.sqrt(c_2_5) / T_CMB
d_2_7 = mp.sqrt(c_2_7) / T_CMB
chk("C1 ℓ=2..5 rms ΔT/T = 1.0368e-5 (dev −5.79%)",
    abs(float(d_2_5) - 1.03677e-5) < 1e-9, f"({float(d_2_5):.6e})")
chk("C2 ℓ=2..7 rms ΔT/T = 1.1828e-5 (dev +7.46%)",
    abs(float(d_2_7) - 1.18275e-5) < 1e-9, f"({float(d_2_7):.6e})")
# 冇任何 band 命中 <1%
best = min(range(4, 2509), key=lambda hi: abs(float(mp.sqrt(sum_w(FULL, 2, hi)) / T_CMB / RMS_PHI - 1)))
dev_best = abs(float(mp.sqrt(sum_w(FULL, 2, best)) / T_CMB / RMS_PHI - 1) * 100)
nmod = sum(2 * e + 1 for e in range(2, best + 1))
cv = math.sqrt(2.0 / nmod) * 100
print(f"  ★ 掃描 ℓ=2..hi 之最佳: hi = {best}, dev = {dev_best:.4f}%")
print(f"     該 band 模式數 N = Σ(2ℓ+1) = {nmod} ⇒ 宇宙變異 σ_CV = √(2/N) = {cv:.1f}%")
chk("C3 ★ 最佳 band 之 dev (0.85%) ≪ 宇宙變異 (21%) ⇒ 吻合無信息量",
    dev_best < 1.0 and cv > 15,
    f"(dev {dev_best:.3f}% vs σ_CV {cv:.1f}%)")

# ================================================================ D
print("\n=== D: 5 個 IDCM 峰嘅 delta-sum vs 全譜 ===")
PEAKS = {220: 6373.42, 528: 2673.14, 792: 2322.29, 1012: 952.17, 1188: 1166.43}
S_PEAK = sum(w_of(e, D) for e, D in PEAKS.items())
print(f"  (a) 原始全譜逐 ℓ 值 (本輪新算):")
print(f"      Σw(5 峰, delta) = {mp.nstr(S_PEAK, 8)} μK²  (佔全譜 {float(S_PEAK/S_FULL)*100:.3f}%)")
chk("D1 5 峰 delta-sum = 38.81 μK² (原始全譜)",
    abs(float(S_PEAK) - 38.8147) < 0.01, f"({float(S_PEAK):.4f})")
chk("D2 ★ 5 峰只佔全譜變異 0.316%",
    abs(float(S_PEAK / S_FULL) * 100 - 0.316) < 0.01,
    f"({float(S_PEAK/S_FULL)*100:.4f}%)")

# docs/18 基線: O10 分箱 D 值 (雜訊較低), 同一 IDCM ℓ 位
PEAKS_B = {220: 5816.4797, 528: 2579.2168, 792: 2552.7278, 1012: 1246.2912, 1188: 822.1860}
S_PEAK_B = sum(w_of(e, D) for e, D in PEAKS_B.items())
print(f"  (b) docs/18 基線 (O10 分箱 D 值):")
print(f"      Σw = {mp.nstr(S_PEAK_B, 8)} μK²")
chk("D2b docs/18 基線 Σw = 36.403 μK² (重現 docs/18 §3)",
    abs(float(S_PEAK_B) - 36.403) < 0.005, f"({float(S_PEAK_B):.4f})")

TGT = (RMS_PHI * T_CMB) ** 2
DL_EFF = TGT / S_PEAK
DL_EFF_B = TGT / S_PEAK_B
print(f"  目標 (ε_φ⁵/8 × T)² = {mp.nstr(TGT, 8)} μK²")
print(f"  ⇒ 反解 Δℓ_eff (原始全譜) = {mp.nstr(DL_EFF, 8)}")
print(f"  ⇒ 反解 Δℓ_eff (docs/18 基線) = {mp.nstr(DL_EFF_B, 8)}")
chk("D3 Δℓ_eff = 23.1864 (原始全譜)", abs(float(DL_EFF) - 23.1864) < 1e-3,
    f"({float(DL_EFF):.5f})")
chk("D3b Δℓ_eff = 24.7227 (docs/18 基線, 重現)",
    abs(float(DL_EFF_B) - 24.7227) < 1e-3, f"({float(DL_EFF_B):.5f})")

# ================================================================ E
print("\n=== E: Δℓ_eff 結構身份掃描 + null control ===")


def scan_hits(target, tol_rel=1e-3):
    """由 LIB 生成 a/b, a*b, a*b/c 之所有組合, 數命中數"""
    t = float(target)
    hits = []
    names = list(LIB.keys())
    for na in names:
        a = LIB[na]
        for nb in names:
            b = LIB[nb]
            for nm, val in ((f"{na}/{nb}", a / b),
                            (f"{na}*{nb}", a * b)):
                if abs(val - t) / t <= tol_rel:
                    hits.append((nm, val))
    # a*b/c 抽樣 (三層, 控制規模)
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


hits = scan_hits(DL_EFF)
hits_b = scan_hits(DL_EFF_B)
print(f"  Δℓ_eff (原始全譜) = {float(DL_EFF):.4f}: 0.1% 內命中 {len(hits)} 條:")
for nm, v in hits[:8]:
    print(f"    {nm:24s} = {v:.6f}  (dev {abs(v-float(DL_EFF))/float(DL_EFF)*100:.4f}%)")
print(f"  Δℓ_eff (docs/18 基線) = {float(DL_EFF_B):.4f}: 0.1% 內命中 {len(hits_b)} 條:")
for nm, v in hits_b[:8]:
    print(f"    {nm:24s} = {v:.6f}  (dev {abs(v-float(DL_EFF_B))/float(DL_EFF_B)*100:.4f}%)")
chk("E1 Δℓ_eff 喺 0.1% 內有結構命中 (兩個基線)", len(hits) > 0 and len(hits_b) > 0,
    f"({len(hits)} / {len(hits_b)} 條)")

# null control: 隨機 target 之命中數
import random
random.seed(20260916)
null_counts = []
for _ in range(60):
    rt = random.uniform(15.0, 35.0)
    null_counts.append(len(scan_hits(rt)))
mean_null = sum(null_counts) / len(null_counts)
print(f"  null control (60 個隨機 target, U(15,35)): 平均命中 {mean_null:.1f} 條")
chk("E2 ★ 兩個基線之命中數 ≤ 1.5× null ⇒ 掃描無鑑別力 (密度背景)",
    len(hits) < 1.5 * mean_null and len(hits_b) < 1.5 * mean_null,
    f"(實測 {len(hits)}/{len(hits_b)} vs null {mean_null:.1f})")

# ================================================================ F
print("\n=== F: 比值掃描 (rms 全圖 / ε_φ⁵/8 = 3.69262) + null ===")
RATIO = float(DTT_FULL / RMS_PHI)
hits_r = scan_hits(mp.mpf(RATIO))
print(f"  0.1% 內命中 {len(hits_r)} 條:")
for nm, v in hits_r[:12]:
    print(f"    {nm:24s} = {v:.6f}  (dev {abs(v-RATIO)/RATIO*100:.4f}%)")
null_r = []
for _ in range(60):
    rt = random.uniform(2.5, 5.0)
    null_r.append(len(scan_hits(mp.mpf(rt))))
mean_null_r = sum(null_r) / len(null_r)
print(f"  null control (60 隨機 target U(2.5,5)): 平均 {mean_null_r:.1f} 條")
chk("F1 ★ 比值 3.69262 之命中數 (64) ≈ null 平均 (52.6) ⇒ 無結構身份 (差 1.2×, 1.6σ)",
    len(hits_r) < 1.5 * mean_null_r,
    f"(實測 {len(hits_r)} vs null {mean_null_r:.1f} = {len(hits_r)/mean_null_r:.2f}×)")
print(f"  ⇒ 命中數/null = {len(hits_r)/mean_null_r:.2f}× ⇒ 密度背景 (掃描組合 ~8.3e4)")

# ================================================================ G
print("\n=== G: 裁決 ===")
verdict = {
    "full_spectrum_rms_muK": float(RMS_FULL),
    "full_spectrum_dTdT": float(DTT_FULL),
    "eps_phi5_8": float(RMS_PHI),
    "eps_ring5_8": float(RMS_RING),
    "ratio_full_over_eps_phi": float(r_full),
    "o77_source_hardcoded": has_hard,
    "o77_claimed_dev_pct": 0.06,
    "actual_dev_vs_1.1e-5_pct": float(dev_11),
    "best_band_dev_pct": best,
    "dl_eff_required": float(DL_EFF),
    "dl_eff_struct_hits": len(hits),
    "dl_eff_null_mean": mean_null,
    "ratio_struct_hits": len(hits_r),
    "ratio_null_mean": mean_null_r,
    "verdict": "絕對振幅錨定未通過驗證: ε⁵/8 非 CMB 圖 rms; o77 之 0.06% 對比硬編常數",
}
(BASE / "data" / "30_amplitude_real_planck.json").write_text(
    json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  裁決: {verdict['verdict']}")
print(f"  🔴 ε_φ⁵/8 = {mp.nstr(RMS_PHI,6)} vs 真圖 rms {mp.nstr(DTT_FULL,6)} ⇒ 差 {float(r_full-1)*100:+.1f}%")
print(f"  🔴 o77「Planck 1.1e-5」= hardcode (非量測) ⇒ 0.06% 無效")
print(f"  🟡 最接近之 band: ℓ=2..5 (dev {float(d_2_5/RMS_PHI-1)*100:+.2f}%) —— 宇宙變異主導, 唔穩健")
print(f"  🔴 Δℓ_eff = {float(DL_EFF):.4f}: 0.1% 內命中 {len(hits)} 條 vs null 平均 {mean_null:.1f} ⇒ 密度背景")

print("\n" + "=" * 72)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
if FAILS:
    print("FAILS:")
    for f_ in FAILS:
        print(f"  - {f_}")
print("=" * 72)
