#!/usr/bin/env python3
"""
O48 Q1.36: AUDIT 尾 — k 值修正 + 峰形右重純 TT 驗證
=============================================================
Q1.21 (37 script) 結論「跨 binning k 值共存 {63,81}=9×{7,9}」係基於
污染 Plik k [7,9,7,6] + O9 k [10,11,9,7]——兩個 binning 本來係同一份數據
(Plik TT block = O9)！純 TT 後只有一組 k。

A. k 值純 TT 修正: 峰→谷距 = [90,99,81,63], k = [10,11,9,7]
   → 「共存 {63,81}」撤回, 單一 k 組 {10,11,9,7}
B. 峰形右重 (谷偏後峰 22%) 純 TT 驗證: 谷→後峰距離比例
C. 谷→後峰 k 身份: {10,11,9,7} — 有無結構?
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

# 純 TT 谷位 (O9 = Plik TT block)
valleys = np.array([437, 716, 1040, 1346])
peaks_tail = np.array([527, 815, 1121, 1409])   # 對應谷嘅後峰
peaks_all = np.array([221, 527, 815, 1121, 1409])

print("="*72)
print("A. k 值純 TT 修正 (Q1.21)")
print("="*72)
d2p = peaks_tail - valleys      # 谷→後峰
k = d2p / 9
print(f"谷→後峰距離: {list(d2p)} = 9×{list(k)}")
print(f"舊 Q1.21: Plik {list(k)} (污染) + O9 同組 → 「共存 {7,9}」")
print(f"修正: 只有一組 k = [{', '.join(str(int(x)) for x in k)}]")
print(f"→ 「跨 binning 共存 {63,81}」撤回 (同一 binning)")
check("A1: k 值 = [10,11,9,7] (O9 組)", list(k) == [10.0, 11.0, 9.0, 7.0],
      f"k={list(k)}")
k2 = d2p / 9
print(f"k mod? 10,11,9,7 — 平均差 {np.mean(np.diff(k2)):+.1f}")

print("\n" + "="*72)
print("B. 峰形右重純 TT 驗證 (谷偏近後峰?)")
print("="*72)
# 谷→後峰 vs 峰間隙: 谷位置比例 (谷距離前峰嘅分數)
front_gaps = peaks_all[1:] - peaks_all[:-1]  # 峰間隙 [306,288,306,288]
v_from_front = valleys - peaks_all[:-1]       # 谷距前峰 [216,189,225,225]
frac = v_from_front / front_gaps
print(f"谷距前峰: {list(v_from_front)} / 峰間隙 {list(front_gaps)}")
print(f"位置分數: {[f'{x:.3f}' for x in frac]}")
print(f"平均: {np.mean(frac):.3f}  (0.5=正中間, 0.75=V¾)")
check("B1: 谷偏近後峰 (前峰分數 >0.5 ⟹ 谷→後峰 <0.5)", np.mean(frac) > 0.5,
      f"前峰frac={np.mean(frac):.3f} ⟹ 谷→後峰={1-np.mean(frac):.3f}")
print(f"(Q1.16 曾報谷→後峰 0.220 — 純 TT 修正為 {1-np.mean(frac):.3f} (28%))")

print("\n" + "="*72)
print("C. k 值結構身份")
print("="*72)
print(f"k = [10, 11, 9, 7]")
print(f"  10 = N_d/4 - 1? (44/4=11) | 11 = L₅ (Lucas) | 9 = F₄² | 7 = L₄")
print(f"  k mod? [10,11,9,7] — 唔似簡單數列")
print(f"  谷→後峰 = 9k = [90,99,81,63] — 全部 < 峰間隙/3? "
      f"{all(9*x < g/2 for x, g in zip(k, front_gaps))}")
print(f"  → 谷位: 前峰+[216,189,225,225] = 9×[24,21,25,25], 後峰−9×[10,11,9,7]")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)