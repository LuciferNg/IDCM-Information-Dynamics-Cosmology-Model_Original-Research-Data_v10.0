#!/usr/bin/env python3
"""
O10 17: SPT-3G bdp 正確解析 (修正 spec order)
==============================================
正確順序 (spt_tne.yaml spectra_info, 21 spectra):
  TT: 90x90, 90x150, 90x220, 150x150, 150x220, 220x220 (6×52=312)
  TE: 90x90, 90x150, 150x90, 90x220, 220x90, 150x150, 150x220, 220x150, 220x220 (9×72=648)
  EE: 90x90, 90x150, 90x220, 150x150, 150x220, 220x220 (6×72=432)
  總計 312+648+432 = 1392 ✅
"""
import numpy as np, math, os, json

bdp_path = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "spt3g_tne_bdp.txt")
vals = np.array([float(x) for x in open(bdp_path).read().split()])

spec_order = [
    ("TT", "90x90", 52), ("TE", "90x90", 72), ("EE", "90x90", 72),
    ("TT", "90x150", 52), ("TE", "90x150", 72), ("TE", "150x90", 72), ("EE", "90x150", 72),
    ("TT", "90x220", 52), ("TE", "90x220", 72), ("TE", "220x90", 72), ("EE", "90x220", 72),
    ("TT", "150x150", 52), ("TE", "150x150", 72), ("EE", "150x150", 72),
    ("TT", "150x220", 52), ("TE", "150x220", 72), ("TE", "220x150", 72), ("EE", "150x220", 72),
    ("TT", "220x220", 52), ("TE", "220x220", 72), ("EE", "220x220", 72),
]

total = sum(n for _, _, n in spec_order)
print(f"預期總值: {total} {'✅' if total == len(vals) else '❌'}")

tt_spectra = {}
offset = 0
for name, freq, n in spec_order:
    block = vals[offset:offset+n]
    if name == "TT":
        tt_spectra[freq] = block
    offset += n

print(f"TT spectra: {list(tt_spectra.keys())}")

# bin centers: Δℓ=50, 從 ℓ=400 開始
centers = np.array([400 + 50*b + 25 for b in range(52)])

# ============ 對比 Planck (驗證單位) ============
DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl_pl = val * l*(l+1)/(2*np.pi)

print("\nSPT vs Planck 對比 (check 單位):")
print(f"{'ℓ':>6} | {'SPT 90x90':>10} | {'SPT 150x150':>10} | {'Planck':>8} | {'90x90/Planck':>12} | {'150x150/Planck':>12}")
for i in [2, 4, 8, 12, 16, 21]:
    idx_pl = np.argmin(np.abs(l - centers[i]))
    r90 = tt_spectra["90x90"][i]/Dl_pl[idx_pl]
    r150 = tt_spectra["150x150"][i]/Dl_pl[idx_pl]
    print(f"{centers[i]:>6.0f} | {tt_spectra['90x90'][i]:>10.1f} | {tt_spectra['150x150'][i]:>10.3f} | {Dl_pl[idx_pl]:>8.0f} | {r90:>12.3f} | {r150:>12.3f}")

# ============ P₄ 盲測: 峰 8,9 @ 1465/1474 → bin 21 (1450-1500) ============
print("\n" + "=" * 72)
print("P₄ 盲測: SPT bin 21 (ℓ 1450-1500) 涵蓋峰 8,9")
print("=" * 72)

# 方法: 用 SPT bandpower / Planck D₁ (cross-calibration)
# Planck D₁ = 5816 @ 220
D1_pl = Dl_pl[np.argmin(np.abs(l-220))]

for name in tt_spectra:
    spec = tt_spectra[name]
    b21 = spec[21]
    # 如果 90x90 對得上 Planck scale (ratio≈1), 用佢
    ratio = b21 / D1_pl
    print(f"  TT {name}: bin 21 D = {b21:.2f} | A/A₁(Planck D₁) = {ratio:.4f}")

# 峰 6,7 參考 (P₃ 已閉合): bin 19 (1375) + bin 20 (1425) 附近
print("\n對比: P₃ 峰 6,7 位置嘅 SPT bins:")
for name in ["90x90", "150x150"]:
    spec = tt_spectra[name]
    print(f"  TT {name}: bin 19 (ℓ=1375): {spec[19]:.1f} | bin 20 (ℓ=1425): {spec[20]:.1f} | bin 21 (ℓ=1475): {spec[21]:.1f}")

print()
print("關鍵: 峰 8 (1465) + 峰 9 (1474) 都喺 bin 21 入面 (1450-1500)")
print("如果 Fibonacci 階梯成立, bin 21 應該高過 pure damping tail 預期")
print("P₄ 預測 = 3ε·F₄·φ⁻⁶ =", 3*((1+5**0.5)/2)**-1/4*3*((1+5**0.5)/2)**-6, "× A₁")

# 儲存
with open(os.path.join(os.path.dirname(__file__), "..", "data", "spt3g_tt_parsed.json"), "w") as f:
    json.dump({"tt_spectra": {k: v.tolist() for k, v in tt_spectra.items()},
               "bin_centers": centers.tolist()}, f, indent=1)
print("\n已儲存 -> data/spt3g_tt_parsed.json")
