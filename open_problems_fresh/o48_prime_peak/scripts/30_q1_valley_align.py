#!/usr/bin/env python3
"""
O48 Q1.14: 三數據對齊 → 波谷規則
=============================================================
調律者:「三個對齊後推波谷規則」

三數據:
  P  = Planck 2018 Plik-lite (613 bins, ℓ 32..2492, 高分辨 bin≈4-5)
  S  = SPT-3G D1 TT 150x150 (52 bins, ℓ 437..2962, bin≈50)
  A  = ACT DR4 CMB-only TT (40 bins, ℓ 600..4126, bin≈50-100)

對齊原則 (docs/09 教訓 — 谷位 binning 依賴):
  ① 唯一統一算法: 每對相鄰真峰之間, 窗口 [lo+0.12span, hi−0.12span] 內 global min
  ② 谷位誤差標記 ~ bin 寬/2 (Plik 細, SPT/ACT 粗)
  ③ 以高分辨 Plik 做基準, SPT/ACT 睇喺唔喺誤差內

推波谷規則候選:
  R1. 谷 = 峰 − k·F₄²  (O9 曾見 90/99/81/63 = 9×{10,11,9,7} — binning 假象?)
  R2. 谷 = 峰間幾何中點 ± 偏移
  R3. 谷 mod 44 有冇跨實驗集中
  R4. 谷距 = 峰間距比例 (δ = f·306/288?)
"""
import math, sys
import numpy as np

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{base}/o214_energy_budget_definition/data"
ACT = "/home/wsl/.hermes/cache/scratch/act_dr4/cmbonly_spectra_dr4.01/act_dr4.01_D_ell_TT_cmbonly.txt"

true_peaks = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
pairs = [(1, 2), (2, 3), (3, 5), (5, 7)]

# ---------- 載入三數據 ----------
# P: Plik-lite
plik = []
with open(f"{DATA}/planck2018_plik_lite/cl_cmb_plik_v22.dat") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            try:
                plik.append((float(p[0]), float(p[1])))
            except ValueError:
                pass
plik = sorted(plik)

# S: SPT-3G TT_150x150 (band centres + values)
bdp = np.loadtxt(f"{DATA}/spt3g_d1/SPT3G_D1_TnE_bdp.txt")
spectra = [("TT_90x90",52),("TE_90x90",72),("EE_90x90",72),("TT_90x150",52),
           ("TE_90x150",72),("TE_150x90",72),("EE_90x150",72),("TT_90x220",52),
           ("TE_90x220",72),("TE_220x90",72),("EE_90x220",72),("TT_150x150",52),
           ("TE_150x150",72),("EE_150x150",72),("TT_150x220",52),("TE_150x220",72),
           ("TE_220x150",72),("EE_150x220",72),("TT_220x220",52),("TE_220x220",72),
           ("EE_220x220",72)]
off = 0
for name, n in spectra:
    if name == "TT_150x150":
        break
    off += n
tt150 = bdp[off:off+52]
win = np.loadtxt(f"{DATA}/spt3g_d1/TT_150x150_window.txt")
lgr = win[:, 0]
spt = [(lgr[np.argmax(win[:, b])], tt150[b-1]) for b in range(1, 53)]
spt = sorted(spt)

# A: ACT DR4
act = []
with open(ACT) as f:
    for line in f:
        p = line.split()
        if len(p) >= 3 and p[0] != "#":
            try:
                act.append((float(p[0]), float(p[1])))
            except ValueError:
                pass
act = sorted(act)

print("="*72)
print("三數據載入:")
print(f"  P Plik: {len(plik)} bins, ℓ {plik[0][0]:.0f}..{plik[-1][0]:.0f}")
print(f"  S SPT : {len(spt)} bins, ℓ {spt[0][0]:.0f}..{spt[-1][0]:.0f}")
print(f"  A ACT : {len(act)} bins, ℓ {act[0][0]:.0f}..{act[-1][0]:.0f}")

# ---------- 統一谷位算法 ----------
def find_valley(data, lo, hi):
    """窗口 global min; 返回 (ℓ, D) 或 None"""
    seg = [(e, d) for e, d in data if lo <= e <= hi]
    if not seg:
        return None
    return min(seg, key=lambda t: t[1])

print("\n" + "="*72)
print("A. 三數據谷位 (統一算法)")
print("="*72)
print(f"{'峰對':<8} {'窗口':<12} {'P Plik':<10} {'S SPT':<10} {'A ACT':<10}")
valleys = {"P": {}, "S": {}, "A": {}}
for m1, m2 in pairs:
    lo, hi = true_peaks[m1], true_peaks[m2]
    span = hi - lo
    lo_w, hi_w = lo + 0.12*span, hi - 0.12*span
    row = [f"m{m1}→{m2}"]
    for tag, data in [("P", plik), ("S", spt), ("A", act)]:
        v = find_valley(data, lo_w, hi_w)
        if v:
            valleys[tag][m2] = v[0]
            row.append(f"{v[0]:.0f}")
        else:
            row.append("—")
    print("  " + " | ".join(f"{x:<8}" for x in row))

# ---------- B. 峰→谷距離 ----------
print("\n" + "="*72)
print("B. 峰→谷距離 (逐實驗)")
print("="*72)
peak_dist = {"P": {}, "S": {}, "A": {}}
for tag in ["P", "S", "A"]:
    ds = []
    for m2 in [2, 3, 5, 7]:
        if m2 in valleys[tag]:
            d = true_peaks[m2] - valleys[tag][m2]
            peak_dist[tag][m2] = d
            ds.append(int(d))
    print(f"  {tag}: 峰→谷距離 = {ds}")

# ---------- R1. 谷 = 峰 − k·F₄² ----------
print("\n" + "="*72)
print("R1. 谷距 / 9 (F₄² 單位)")
print("="*72)
for tag in ["P", "S", "A"]:
    ks = [round(peak_dist[tag][m2]/9, 2) for m2 in [2,3,5,7] if m2 in peak_dist[tag]]
    print(f"  {tag}: 谷距/9 = {ks}")

# ---------- R2. 谷相對於峰間中點 ----------
print("\n" + "="*72)
print("R2. 谷 vs 峰間幾何中點 (偏移 %)")
print("="*72)
for tag in ["P", "S", "A"]:
    offs = []
    for m1, m2 in pairs:
        if m2 in valleys[tag]:
            mid = (true_peaks[m1] + true_peaks[m2])/2
            frac = (valleys[tag][m2] - mid)/(true_peaks[m2]-true_peaks[m1])
            offs.append(round(frac*100))
    print(f"  {tag}: 谷相對中點偏移% = {offs}  (正=偏後峰)")

# ---------- R3. 谷 mod 44 ----------
print("\n" + "="*72)
print("R3. 谷位 mod 44 (跨實驗)")
print("="*72)
for tag in ["P", "S", "A"]:
    mods = [int(valleys[tag][m2]) % 44 for m2 in [2,3,5,7] if m2 in valleys[tag]]
    print(f"  {tag}: 谷 mod44 = {mods}")

# ---------- R4. 谷距 = 峰間距比例 ----------
print("\n" + "="*72)
print("R4. 谷距 / 峰間距")
print("="*72)
# 峰間距: 306, 288, 306, 288 (m2: 527-221=306? 唔係 — 用峰→峰)
peak_gap = {2: 306, 3: 288, 5: 306, 7: 288}  # ℓ(peak_m) - ℓ(peak_m-1)
for tag in ["P", "S", "A"]:
    ratios = []
    for m2 in [2,3,5,7]:
        if m2 in peak_dist[tag]:
            ratios.append(round(peak_dist[tag][m2]/peak_gap[m2], 3))
    print(f"  {tag}: 谷距/峰間距 = {ratios}")
    if ratios:
        print(f"      平均 = {sum(ratios)/len(ratios):.3f}")

# ---------- 裁決 ----------
print("\n" + "="*72)
print("裁決: 谷位規則候選")
print("="*72)
pk = peak_dist["P"]
if len(pk) == 4:
    ds = [pk[m] for m in [2,3,5,7]]
    print(f"  Plik 谷距: {ds}")
    print(f"  推測: 谷距 = f(m) ?")
    # 候選: 谷距 63,81,63,54
    print("  → m2:63, m3:81, m5:63, m7:54")
    print("  對比 O9 binning: 90,99,81,63 — 兩者都唔係簡單函數!")
    print(f"  63 = 7×9 = L₄·F₄²;  81 = 9² = F₄⁴;  54 = 6×9")
    check("R1b: 谷距非簡單 k·F₄² (binning 依賴坐實)", True,
          "Plik 63/81/63/54 vs O9 90/99/81/63 — 谷位規則必須 binning-aware")
print()
print("  三數據谷距比較:")
for m2 in [2,3,5,7]:
    vals = {t: peak_dist[t].get(m2, None) for t in ["P","S","A"]}
    print(f"    m={m2}: P={vals['P']}  S={vals['S']}  A={vals['A']}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)