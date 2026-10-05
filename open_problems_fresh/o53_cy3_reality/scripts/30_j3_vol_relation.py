#!/usr/bin/env python3
"""
O53 開放 1 深入: J3 同 Vol 關係 + κ 一致性
==============================================
發現: J3 = 0.0014648 = 6×Vol? 但 Vol(J0) 用 κ = 0.000474 ≠ 0.000244

查:
  1. J3/Vol = ?
  2. 用 J0 計算 Vol_κ = κ_ijk J^i J^j J^k — 邊個先係啱?
  3. Jstar 檔案嘅 Vol/J3 點嚟?
"""
import os, json, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53 開放 1: J3/Vol 關係")
print("=" * 70)

with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)

K = np.zeros(tuple(kappa['shape']))
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val
    K[i, k, j] = val
    K[j, i, k] = val
    K[j, k, i] = val
    K[k, i, j] = val
    K[k, j, i] = val

J0 = np.array(jstar['Jstar_36D'])
Vol_file = jstar['Vol']
J3_file = jstar['J3']
Ind_file = jstar['Ind']

print("\n[1] 檔案值:")
print(f"    Vol (file) = {Vol_file:.10f} = 1/{1/Vol_file:.0f}")
print(f"    J3 (file)  = {J3_file:.10f} = 1/{1/J3_file:.0f}")
print(f"    Ind (file) = {Ind_file:.6f}")
print(f"    J3/Vol = {J3_file/Vol_file:.6f}")
print(f"    6×Vol = {6*Vol_file:.10f}")
print(f"    J3 = 6×Vol? {'✅' if abs(J3_file - 6*Vol_file) < 1e-12 else '❌'}")

# 用 κ 計算
print("\n[2] 用 κ_ijk 計算:")
Vol_kappa = np.einsum('ijk,i,j,k->', K, J0, J0, J0)
print(f"    Vol_κ(J0) = {Vol_kappa:.10f} = 1/{1/Vol_kappa:.4f}")
print(f"    檔案 Vol = {Vol_file:.10f}")
print(f"    比例: {Vol_kappa/Vol_file:.6f}")

# J3 = κ_ijk J^i J^j J^k / 6 (CY 標準: Vol = J³/6)
J3_kappa = Vol_kappa / 6
print(f"    J³/6 = {J3_kappa:.10f} vs 檔案 J3 = {J3_file:.10f}")
print(f"    比例: {J3_kappa/J3_file:.6f}")

# 標準 toric: Vol = J³/6 定義
print(f"\n[3] 標準定義檢查:")
print(f"    如果 Vol = J³/6: J³ = {6*Vol_kappa:.6f}")
print(f"    檔案 J3 應該 = J³/6 = Vol_kappa/6?")
print(f"    檔案 J3 = {J3_file:.10f}")
print(f"    Vol_kappa/6 = {Vol_kappa/6:.10f}")
print(f"    J3_file/(Vol_kappa/6) = {J3_file/(Vol_kappa/6):.4f}")

# Ind = index
print(f"\n[4] Ind:")
print(f"    Ind = {Ind_file:.6f}")
print(f"    48.0004 ≈ 48? 誤差 {abs(Ind_file-48):.4f}")

# Vol 檔案值 = 2^-12?
print(f"\n[5] Vol_file = 2^(-12)?")
print(f"    {Vol_file:.10f} vs {2**-12:.10f}")
print(f"    差: {abs(Vol_file - 2**-12):.2e}")

# 如果用檔案 Vol = 2^-12 做 normalization, J 應該縮幾多?
print(f"\n[6] 如果 Vol 規範 = 2^(-12):")
print(f"    Vol_κ(J0) = {Vol_kappa:.6f} 需要縮到 {2**-12:.6f}")
s = (2**-12 / Vol_kappa) ** (1/3)
print(f"    J → s·J, s = {s:.6f}")
J1 = s * J0
Y1 = np.einsum('ijk,k->ij', K, J1)
Y1 = (Y1 + Y1.T) / 2
ev1 = np.linalg.eigvalsh(Y1)
tr1 = np.trace(Y1 @ Y1)
print(f"    Vol_κ(sJ) = {np.einsum('ijk,i,j,k->', K, J1, J1, J1):.10f}")
print(f"    tr(Y²) = {tr1:.6f} (誤差 vs 5: {abs(tr1-5)/5*100:.2f}%)")
print(f"    1/λ₁ = {1/max(ev1):.6f} (φ^(-1/3)={phi**(-1/3):.6f}, 誤差 {abs(1/max(ev1)-phi**(-1/3))/phi**(-1/3)*100:.2f}%)")
print(f"    → {'✅ Vol=2^-12 規範下兩閉合' if abs(tr1-5)/5 < 0.02 and abs(1/max(ev1)-phi**(-1/3))/phi**(-1/3)*100 < 0.1 else '❌'}")

print("\n" + "=" * 70)
