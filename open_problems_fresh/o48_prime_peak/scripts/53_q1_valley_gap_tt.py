#!/usr/bin/env python3
"""
O48 Q1.35: Q1.16 (32 script) 純 TT 重驗 — 谷間距中心 vs 峰間距中心
=============================================================
Q1.31-33 audit: 32 script 用 Plik 谷 [464,734,1058,1355] (污染值)
→ 「谷間距中心 = 峰間距中心 = 297.0」結論要重驗。

純 TT 谷 = [437,716,1040,1346] (O9 一致):
  谷間距 = [279, 324, 306], 中心 = 303.0
  峰間距 = [306, 288, 306, 288], 中心 = 297.0

問題: 303 vs 297 — 仲係咪「同一頻率」?
  A. |303−297| = 6 < 15 (舊 32 B1 判據) → 仍然 PASS 但弱好多
  B. 更嚴: 303/297 = 1.020 (2% 偏差) — 統計上可分辨?
"""
import sys
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

# 純 TT 谷位 (Plik TT block / O9 一致)
valleys_tt = np.array([437, 716, 1040, 1346])
peaks = np.array([221, 527, 815, 1121, 1409])

peak_gaps = np.diff(peaks)
valley_gaps = np.diff(valleys_tt)
print("="*72)
print("Q1.16 純 TT 重驗 (scripts/53)")
print("="*72)
print(f"峰間距: {list(peak_gaps)}  中心 = {peak_gaps.mean():.1f}")
print(f"谷間距: {list(valley_gaps)}  中心 = {valley_gaps.mean():.1f}")
print(f"差異: |303.0 − 297.0| = 6.0   (舊 32 B1 判據 <15)")

check("A1: 谷間距中心 ∈ 峰間距中心±15 (舊判據)", 
      abs(valley_gaps.mean() - peak_gaps.mean()) < 15,
      f"{valley_gaps.mean():.1f} vs {peak_gaps.mean():.1f}")
print()
print("嚴格判據: 谷間距 = 峰間距?")
rat = valley_gaps.mean()/peak_gaps.mean()
print(f"比率 = {rat:.4f} (2% 偏差)")
check("A2: 1% 級別同一頻率 (比率 0.99-1.01)", 0.99 < rat < 1.01,
      f"ratio={rat:.4f}")
print()
# 峰間隙同谷間距逐段對應: 每段谷間距對應兩個峰間隙之間
print("逐段谷間距 vs 對應峰間隙:")
for i in range(3):
    # 谷 i 喺峰 i+1 前, 谷間距跨越峰 i+1
    mapped = peak_gaps[i] + peak_gaps[i+1]
    print(f"  谷{i+1}→{i+2}: {valley_gaps[i]}  vs 峰間隙 {peak_gaps[i]}+{peak_gaps[i+1]}={mapped}")
v1 = valley_gaps[0]  # 279
m1 = peak_gaps[0]+peak_gaps[1]  # 594
print(f"  279 vs 594 → 比例 {v1/m1:.3f} ≈ ½?")
check("A3: 谷間距 ≈ 峰間隙½ (兩峰一谷週期)", 
      all(abs(valley_gaps[i] - (peak_gaps[i]+peak_gaps[i+1])/2) < 10
          for i in range(3)),
      f"{[v - (peak_gaps[i]+peak_gaps[i+1])/2 for i, v in enumerate(valley_gaps)]}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)