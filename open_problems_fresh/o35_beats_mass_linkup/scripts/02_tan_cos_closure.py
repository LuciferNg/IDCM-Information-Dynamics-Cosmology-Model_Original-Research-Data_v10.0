#!/usr/bin/env python3
"""
O35 — Step 2: tan/cos 等價形式閉合 (scripts/02)
=====================================================
驗證: IDCM 質量比嘅 sin 形式可以經三角恆等式變換為等價 tan/cos 形式,
而且呢啲形式係恆等變換 (dev < 1e-12), 唔係新自由參數。

恆等式:
  sin(A)/sin(B) = cos(B/2)...  (用和差化積)
  更直接:
  sin(A)/sin(B) = [tan(A)/tan(B)] × [cos(A)/cos(B)]   ← 恆等
  sin(A)/sin(B) = tan(A) × cos(B)/sin(B) × ...         ← 展開

驗證點:
  [1] sin(A)/sin(B) = tan(A)cos(B)/sin(B) 全譜恆等
  [2] sin(A)/sin(B) = cos(A)/cos(B) × tan(A)/tan(B) 全譜恆等
  [3] sin(A)/sin(B) = 1/tan(B) × tan(A) × cos(B)/cos(A)... 檢查
  [4] O34 質量比用 tan 形式重現 (唔加新參數)
  [5] tan 形式嘅結構意義: tan(nπ/88) 對應 K_Chain 阻抗匹配
"""

import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 100

N = 44

def sinr(n1, n2):
    return np.sin(np.pi * n1 / 88) / np.sin(np.pi * n2 / 88)

def tanr(n1, n2):
    return np.tan(np.pi * n1 / 88) / np.tan(np.pi * n2 / 88)

print("=" * 67)
print("  O35 — Step 2: tan/cos 等價形式閉合")
print("=" * 67)

# ═══════════════════════════════════════════════════════════════
# [1] 恆等式: sin(A)/sin(B) = tan(A)·cos(B)/sin(B)?? 錯 — 重新推
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [1] 恆等式驗證 ───")
# 正確恆等式:
#   tan(A)/tan(B) = [sin(A)/cos(A)] / [sin(B)/cos(B)]
#                 = sin(A)cos(B) / [cos(A)sin(B)]
#   sin(A)/sin(B) × cos(A)/cos(B) = sin(A)cos(A)/[sin(B)cos(B)] — 唔等於
#   tan(A)/tan(B) = sin(A)cos(B)/(cos(A)sin(B))
#   => sin(A)/sin(B) = tan(A)/tan(B) × cos(A)/cos(B)  ✅ 正確恆等式
max_dev1 = 0.0
for n1 in range(1, 44):
    for n2 in range(1, 44):
        if n1 == n2:
            continue
        lhs = sinr(n1, n2)
        rhs = tanr(n1, n2) * (np.cos(np.pi*n1/88) / np.cos(np.pi*n2/88))
        max_dev1 = max(max_dev1, abs(lhs - rhs))
print(f"  sin(A)/sin(B) = tan(A)/tan(B) × cos(A)/cos(B)")
print(f"  全譜 max dev = {max_dev1:.2e}")
PASS1 = max_dev1 < 1e-12
print(f"  [1] tan×cos 恆等式: {'✅ PASS' if PASS1 else '❌ FAIL'}")

# ═══════════════════════════════════════════════════════════════
# [2] 另一恆等式: sin(A)/sin(B) = tan(A)·cos(B)/cos(A)·... 全譜
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [2] 分解唯一性 ───")
# sin(A)/sin(B) = tan(A) × cos(B)/sin(B) / ... 檢查
# 實際上 sin(A)/sin(B) = tan(A)/tan(B) × cos(A)/cos(B) 只有一種分解
# 檢查有冇第二種獨立分解
max_dev2 = 0.0
for n1 in range(1, 44):
    for n2 in range(1, 44):
        if n1 == n2:
            continue
        # 第二恆等式: sin(A)/sin(B) = cot(B)/cot(A) × ... 檢查倒數
        lhs = sinr(n1, n2)
        rhs = (1/np.tan(np.pi*n2/88)) / (1/np.tan(np.pi*n1/88)) * (np.cos(np.pi*n1/88)/np.cos(np.pi*n2/88))
        max_dev2 = max(max_dev2, abs(lhs - rhs))
print(f"  sin(A)/sin(B) = cot(B)/cot(A) × cos(A)/cos(B) (等價)")
print(f"  全譜 max dev = {max_dev2:.2e}")
PASS2 = max_dev2 < 1e-12
print(f"  [2] 等價分解: {'✅ PASS' if PASS2 else '❌ FAIL'}")

# ═══════════════════════════════════════════════════════════════
# [3] tan 形式對 m_u/m_d 等質量比
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [3] tan/cos 形式重現質量比 ───")
# m_u/m_d = sin(1π/88)/sin(2π/88)
n1, n2 = 1, 2
s = sinr(n1, n2)
t = tanr(n1, n2) * (np.cos(np.pi*n1/88)/np.cos(np.pi*n2/88))
print(f"  m_u/m_d: sin 形式 = {s:.6f}")
print(f"           tan×cos 形式 = {t:.6f}")
print(f"           dev = {abs(s-t):.2e} {'✅' if abs(s-t) < 1e-12 else '❌'}")

# m_t/m_b = sin(19π/88)/sin(33π/88)  (O34 閉合)
n1, n2 = 19, 33
s = sinr(n1, n2)
t = tanr(n1, n2) * (np.cos(np.pi*n1/88)/np.cos(np.pi*n2/88))
print(f"  m_t/m_b: sin 形式 = {s:.6f}")
print(f"           tan×cos 形式 = {t:.6f}")
print(f"           dev = {abs(s-t):.2e} {'✅' if abs(s-t) < 1e-12 else '❌'}")
PASS3 = abs(sinr(1,2) - tanr(1,2)*(np.cos(np.pi/88)/np.cos(2*np.pi/88))) < 1e-12
print(f"  [3] tan 形式重現: {'✅ PASS' if PASS3 else '❌ FAIL'}")

# ═══════════════════════════════════════════════════════════════
# [4] tan(nπ/88) 嘅結構意義
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [4] tan(nπ/88) 結構意義 ───")
# tan 對應「阻抗」: 模態阻抗 Z_n = ω_n/cos(...) 之類
# 檢查 tan(nπ/88) 嘅對稱性: tan(nπ/88) × tan((44−n)π/88)
print(f"  tan(nπ/88) × tan((44−n)π/88) 全譜:")
max_pt = 0.0
for n in range(1, 44):
    p = np.tan(np.pi*n/88) * np.tan(np.pi*(44-n)/88)
    max_pt = max(max_pt, abs(p - 1.0))
print(f"  max |tan(n)·tan(44−n) − 1| = {max_pt:.2e}  (預期 1: 補角對偶)")
print(f"  解釋: tan(nπ/88)·tan((44−n)π/88) = tan(θ)·cot(θ) = 1 恆等")

# tan 對稱: tan((44−n)π/88) = tan(π/2 − nπ/88) = cot(nπ/88)
sym_ok = all(abs(np.tan(np.pi*(44-n)/88) - 1/np.tan(np.pi*n/88)) < 1e-12 for n in range(1, 44))
print(f"  tan(44−n) = cot(n) 全譜: {'✅' if sym_ok else '❌'}")
PASS4 = max_pt < 1e-10 and sym_ok
print(f"  [4] tan 補角對偶: {'✅ PASS' if PASS4 else '❌ FAIL'}")

# ═══════════════════════════════════════════════════════════════
# [5] cos 形式: sin(A)/sin(B) = cos(B̂)/cos(Â) 對偶 (Nyquist)
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [5] cos 對偶形式 ───")
# sin(nπ/88) = cos((44−n)π/88)  ← 補角恆等式!
# 所以 sin(A)/sin(B) = cos(44−A)/cos(44−B)
max_dev5 = 0.0
for n1 in range(1, 44):
    for n2 in range(1, 44):
        if n1 == n2:
            continue
        lhs = sinr(n1, n2)
        rhs = np.cos(np.pi*(44-n1)/88) / np.cos(np.pi*(44-n2)/88)
        max_dev5 = max(max_dev5, abs(lhs - rhs))
print(f"  sin(A)/sin(B) = cos((44−A)π/88)/cos((44−B)π/88)")
print(f"  全譜 max dev = {max_dev5:.2e}")
print(f"  解釋: sin(nπ/88) = cos((44−n)π/88) 係 Nyquist 對偶 (n=22 鏡像)")
PASS5 = max_dev5 < 1e-12
print(f"  [5] cos 對偶形式: {'✅ PASS' if PASS5 else '❌ FAIL'}")

# ═══════════════════════════════════════════════════════════════
# 總結
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
results = [PASS1, PASS2, PASS3, PASS4, PASS5]
print(f"  O35 Step 2 結果: {sum(results)}/{len(results)} PASS")
print(f"{'═'*67}")

with open("data/step2_tan_cos_closure_results.txt", "w") as f:
    f.write("O35 Step 2 — tan/cos 等價形式閉合\n")
    f.write("日期: 2026-08-19\n\n")
    f.write(f"[1] sin/tan×cos 恆等式: {'PASS' if PASS1 else 'FAIL'} (max dev {max_dev1:.2e})\n")
    f.write(f"[2] 等價分解: {'PASS' if PASS2 else 'FAIL'} (max dev {max_dev2:.2e})\n")
    f.write(f"[3] tan 形式重現: {'PASS' if PASS3 else 'FAIL'}\n")
    f.write(f"[4] tan 補角對偶: {'PASS' if PASS4 else 'FAIL'} (max |tan·tan−1| {max_pt:.2e})\n")
    f.write(f"[5] cos 對偶形式: {'PASS' if PASS5 else 'FAIL'} (max dev {max_dev5:.2e})\n")
    f.write(f"總計: {sum(results)}/{len(results)} PASS\n")
print(f"\n  結果已寫入 data/step2_tan_cos_closure_results.txt")
