#!/usr/bin/env python3
"""
O10 16: SPT-3G D1 bandpowers 解析 + P₄ 盲測驗證
================================================
SPT-3G D1 TnE bdp 格式:
  - band powers 按 spectrum 順序排列 (spt_tne.yaml spectra_info)
  - 每個 spectrum: TT = 52 bins, TE/EE = 72 bins
  - binning: Δℓ=50, bin b 覆蓋 ℓ∈[50b, 50(b+1)]
  - TT 範圍 ℓ=400-3000 (52 bins), TE/EE ℓ=400-4000 (72 bins)
  - 單位: D_ℓ µK² (直接)

spectra_info 順序 (spt_tne.yaml):
  TT 90x90: 52
  TE 90x90: 72
  EE 90x90: 72
  TT 90x150: 52
  ...
"""
import numpy as np, math, os, json

# ============ 解析 bdp ============
bdp_path = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "spt3g_tne_bdp.txt")
vals = np.array([float(x) for x in open(bdp_path).read().split()])
print(f"bdp 總值: {len(vals)}")

# spectra 順序同 bin 數 (from yaml)
spec_order = [
    ("TT", 90, 90, 52), ("TE", 90, 90, 72), ("EE", 90, 90, 72),
    ("TT", 90, 150, 52), ("TE", 90, 150, 72), ("EE", 90, 150, 72),
    ("TE", 150, 90, 72), ("EE", 150, 90, 72),
    ("TT", 90, 220, 52), ("TE", 90, 220, 72), ("EE", 90, 220, 72),
    ("TE", 220, 90, 72), ("EE", 220, 90, 72),
    ("TT", 150, 150, 52), ("TE", 150, 150, 72), ("EE", 150, 150, 72),
    ("TT", 150, 220, 52), ("TE", 150, 220, 72), ("EE", 150, 220, 72),
    ("TE", 220, 150, 72), ("EE", 150, 220, 72),
    ("TT", 220, 220, 52), ("TE", 220, 220, 72), ("EE", 220, 220, 72),
]

# 驗證總數
total = sum(n for _, _, _, n in spec_order)
print(f"預期總值: {total} {'✅' if total == len(vals) else '❌'}")

# 提取所有 TT spectra
tt_spectra = {}
offset = 0
for name, f1, f2, n in spec_order:
    block = vals[offset:offset+n]
    if name == "TT":
        tt_spectra[f"{f1}x{f2}"] = block
    offset += n

print(f"\nTT spectra 提取: {list(tt_spectra.keys())}")

# ============ bin centers ============
# bin b 覆蓋 ℓ∈[50b, 50(b+1)] (uniform D_ℓ weighting)
# TT 52 bins: 通常 ℓ=400-3000
# bin center = 50b + 25 (midpoint) 或 weighted mean
# 檢查第一個 bin 中心: 假設從 ℓ=400 開始 (bin index 0 = 400-450)
def bin_centers(n_bins, l_start=400):
    return np.array([l_start + 50*b + 25 for b in range(n_bins)])

centers = bin_centers(52)
print(f"\nTT bin centers (前 5): {centers[:5]}, (後 5): {centers[-5:]}")

# ============ 驗證: 對比 Planck 峰位 ============
# 已知: 峰 1 @ 220 (Planck), 但 SPT 由 400 開始 — 峰 1 喺範圍外!
# SPT 覆蓋: 峰 2 (527), 峰 3 (815), 峰 4 (1121), 峰 5 (1409)...
print("\nSPT bin 覆蓋對比 Planck 峰位:")
peaks = {1: 220, 2: 527, 3: 815, 4: 1121, 5: 1409, 6: 1340, 7: 1412, 8: 1465, 9: 1474}
for m, lp in peaks.items():
    in_range = 400 <= lp <= 3000
    print(f"  峰 {m} @ ℓ={lp}: {'✅ 喺 SPT 範圍' if in_range else '❌ 喺範圍外'}")

# ============ SPT TT 90x90 + 150x150 ============
# 用 150x150 (最低噪聲) 做主驗證
print("\nSPT TT 150x150 bandpowers:")
tt150 = tt_spectra["150x150"]
for i in range(len(tt150)):
    if 400 <= centers[i] <= 1600:
        print(f"  bin {i}: ℓ={centers[i]:.0f}, D={tt150[i]:.2f} µK²")

# ============ P₄ 盲測: 峰 8,9 @ 1465/1474 ============
print("\n" + "=" * 72)
print("P₄ 盲測: SPT-3G TT 150x150 @ ℓ 1465/1474")
print("=" * 72)
# 峰 8 = 1465, 峰 9 = 1474 — 兩者都喺 bin ℓ∈[1450,1500] (bin center 1475)
# 檢查該 bin 值
for name in ["150x150", "90x150", "90x90", "150x220", "90x220", "220x220"]:
    spec = tt_spectra[name]
    # bin 21 = 1450-1500 (center 1475)
    # 計算 bin index: (1450-400)/50 = 21
    b_idx = 21
    print(f"  TT {name}: bin 21 (ℓ 1450-1500, center 1475) = {spec[b_idx]:.2f} µK²")

# 對比 Planck 喺相同位置
DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)
for target in [1465, 1474]:
    idx = np.argmin(np.abs(l-target))
    print(f"\n  Planck @ ℓ≈{target}: bin {l[idx]:.0f}, D={Dl[idx]:.0f} µK²")

# 儲存結果
results = {
    "spt_tt_spectra": {k: v.tolist() for k, v in tt_spectra.items()},
    "bin_centers": centers.tolist(),
}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "spt3g_tt_parsed.json"), "w") as f:
    json.dump(results, f, indent=1)
print("\n已儲存 -> data/spt3g_tt_parsed.json")
