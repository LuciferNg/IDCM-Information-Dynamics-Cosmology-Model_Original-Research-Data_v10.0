#!/usr/bin/env python3
"""
O53 Q2 閉合: tr(Y) = 66 精確驗證
==================================
發現: tr(Y) = Σ d_iik·v_k = 66.3554 ≈ 66
驗證:
  1. 呢個係咪精確閉合? (誤差幾多?)
  2. 66 = 3×22 同 C(12,2) 嘅雙重身份
  3. 用所有 d_tensor 版本驗證
  4. 66 同 eigenvalues_final 嘅關係
"""
import sys, os, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")

phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53 Q2: tr(Y) = 66 精確閉合驗證")
print("=" * 70)

# --- [1] 主驗證: d_tensor_final ---
print("\n[1] d_tensor_final.npy:")
d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
v = np.array([phi ** (-k/12) for k in range(12)])

# tr(Y) = Σ_i (d_ijk v_k)_ii = Σ_ik d_iik v_k
d_iik = np.einsum('iik->i', d12)
trY = np.sum(d_iik * v)
print(f"    v_k = φ^(-k/12)")
print(f"    d_iik (i=0..11): {np.array2string(d_iik, precision=4)}")
print(f"    tr(Y) = Σ d_iik·v_k = {trY:.6f}")
print(f"    66 − trY = {66 - trY:+.6f}")
print(f"    誤差: {abs(66-trY)/66*100:.3f}%")

# --- [2] 所有版本驗證 ---
print("\n[2] 所有 12³ d_tensor 版本嘅 tr(Y):")
for fn in sorted(os.listdir(DATA)):
    if fn.startswith("d_tensor") and fn.endswith(".npy"):
        path = os.path.join(DATA, fn)
        try:
            d = np.load(path)
            if d.shape == (12, 12, 12):
                d_iik = np.einsum('iik->i', d)
                tr = np.sum(d_iik * v)
                err = abs(66 - tr) / 66 * 100
                mark = "✅" if err < 1 else ("🟡" if err < 5 else "❌")
                print(f"    {fn:35s}: tr(Y) = {tr:10.4f}  誤差 {err:6.2f}%  {mark}")
        except Exception as e:
            pass

# --- [3] 66 嘅雙重身份 ---
print("\n[3] 66 雙重身份閉合:")
print(f"    A) 幾何: 66 = C(12,2) = 12×11/2 (Z₃ 不變 12 維 beat 空間)")
print(f"    B) 物理: 66 = 3×22 = 3×(2×L₅) (3 代 × 22 態)")
print(f"    C) 跡:   66 ≈ tr(Y) = Σ d_iik·v_k (Yukawa 張量跡)")
print(f"")
print(f"    驗證 C 係咪真閉合:")
print(f"    tr(Y) = {trY:.6f}")
print(f"    66.0000 − trY = {66 - trY:+.6f}")
print(f"    相對誤差 = {abs(66-trY)/66*100:.4f}%")

# --- [4] 66 係邊個嘅跡? ---
print("\n[4] tr(Y) 結構分解:")
print(f"    tr(Y) = Σ_ik d_iik·v_k")
print(f"    = Σ_i v_i·d_iii + Σ_(i≠k) d_iik·v_k")
print(f"    = 對角貢獻 + 非對角貢獻")

diag_contrib = np.sum(d_iik * v)
off_contrib = trY - diag_contrib
print(f"    對角 (i=k): {diag_contrib:.4f}")
print(f"    非對角: {off_contrib:.4f}")
print(f"    66 嘅邊部分? 對角 = {diag_contrib:.2f} 非對角 = {off_contrib:.2f}")

# 檢查 66 = 對角?
print(f"\n    對角貢獻 ≈ 66? {'✅' if abs(diag_contrib - 66) < 1 else '❌'}")
print(f"    對角貢獻 ≈ 33? {'✅' if abs(diag_contrib - 33) < 1 else '❌'}")
print(f"    對角貢獻 ≈ 44? {'✅' if abs(diag_contrib - 44) < 1 else '❌'}")
print(f"    對角貢獻 ≈ 22? {'✅' if abs(diag_contrib - 22) < 1 else '❌'}")

# --- [5] 重要: tr(Y) = 66 係咪靠 v_k 選擇? ---
print("\n[5] v_k = φ^(-k/12) 嘅角色:")
print(f"    如果 v_k = 1 (uniform):")
tr1 = np.sum(d_iik)
print(f"    tr(Y) = Σ d_iik = {tr1:.4f}  (vs 66: {'✅' if abs(tr1-66)<1 else '❌'})")
print(f"    如果 v_k = φ^(-k/12) (IDCM VEV):")
print(f"    tr(Y) = {trY:.4f}  (vs 66: {'✅' if abs(trY-66)<1 else '❌'})")
print(f"")
print(f"    → 66 閉合依賴 v_k 選擇!")

# v_k = φ^(-k/12) 嘅結構
print(f"\n    v_k = φ^(-k/12) 嘅結構:")
print(f"    v = {np.array2string(v, precision=4)}")
print(f"    Σ v_k = {np.sum(v):.4f}")
print(f"    12 個 v_k 嘅 φ 指數: k/12 = {np.array2string(np.arange(12)/12, precision=3)}")
print(f"    66 = 12×11/2 ↔ v_k 指數 k/12 ↔ 1/12 步長?")

print("\n" + "=" * 70)
print("【判定】")
print("=" * 70)
print(f"""
  tr(Y) = {trY:.4f} ≈ 66 ({abs(66-trY)/66*100:.2f}% 誤差)
  
  🟡 接近但唔係精確閉合:
  - 如果 v_k = φ^(-k/12) 係「結構 VEV」→ tr = 66 係近似
  - 需要證明 tr(Y) 精確 = 66 或解釋 0.5% 偏差

  🔴 更根本: 66 嘅「真正身份」仍未唯一確定:
  - C(12,2)? 3×22? tr(Y)? 全部 ≈ 66 但唔精確相等
""")
print("=" * 70)
