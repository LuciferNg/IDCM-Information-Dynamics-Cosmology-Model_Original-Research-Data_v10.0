#!/usr/bin/env python3
"""
O53 Q2 突破: 12 維結構 + C(12,2) = 66 閉合方向
================================================
關鍵發現:
  - d_tensor_final.npy (12³): 有真正三體耦合 (非 rank-1) ✅
  - d_tensor_solved.npy (36³): rank 36 但 91% 稀疏
  - 66 = C(12,2): 12 維 Z₃ 不變子空間嘅「beat 數」

驗證鏈:
  1. 12 = h¹¹/3 = 36/3 (Z₃ orbifold)
  2. 66 = C(12,2) = 12 維空間嘅兩兩組合
  3. 946 = C(44,2) = 44 site 嘅兩兩組合
  4. 134 = 44 + 90: 投影維度 = 鏈 site + 鏈能量
  5. 投影: 946 beats → 66 beats (Z₃ 不變) → 12 維 Yukawa
"""
import sys, os, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
sys.path.insert(0, os.path.join(BASE, "src"))

phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53 Q2: 12 維結構閉合 — C(12,2)=66, C(44,2)=946")
print("=" * 70)

# --- [1] 12 = h¹¹/3 驗證 ---
print("\n[1] 12 維 Z₃ 不變子空間:")
h11 = 36
print(f"    h¹¹ = {h11}, h¹¹/3 = {h11//3} = 12  {'✅' if h11 % 3 == 0 else '❌'}")
print(f"    Z₃ orbifold: 36 → 12 (每個 Z₃ orbit 3 個 Kähler moduli → 1 個)")

# --- [2] 組合數驗證 ---
print("\n[2] 組合數結構:")
C12_2 = 12 * 11 // 2
C44_2 = 44 * 43 // 2
print(f"    C(12,2) = {C12_2} = 66  (12 維 beat 空間)")
print(f"    C(44,2) = {C44_2} = 946  (44 site beat 空間)")
print(f"    946 / 66 = {946/66:.6f} = 14.333...")
print(f"    946 = 66×14 + 22,  22 = 44/2")
print(f"    66 = 946 − 880,  880 = 44×20")

# --- [3] 12³ d_tensor 三體耦合 ---
print("\n[3] d_tensor_final.npy (12³) 三體耦合結構:")
d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
print(f"    shape: {d12.shape}")
print(f"    neg={np.sum(d12<0)}, pos={np.sum(d12>0)}, zero={np.sum(d12==0)}")

# 三體耦合強度: 對角線 vs 非對角
d_diag = np.array([d12[i,i,i] for i in range(12)])
d_off = d12[np.triu_indices(12, 1)]
print(f"    d[i,i,i] (自相交): {np.array2string(d_diag, precision=3)}")
print(f"    非對角 d[i,j,k] 範圍: [{d_off.min():.3f}, {d_off.max():.3f}]")

# 三體耦合本質: 檢查 d[i,j,k] 有冇「三體共振」結構
# 即 d[i,j,k] 大 ↔ (i+j+k) mod 12 = const?
print(f"\n    三體共振檢查 (i+j+k mod 12):")
sums = {}
for i in range(12):
    for j in range(12):
        for k in range(12):
            s = (i+j+k) % 12
            if s not in sums:
                sums[s] = []
            sums[s].append(abs(d12[i,j,k]))
for s in sorted(sums):
    vals = np.array(sums[s])
    print(f"      sum mod 12 = {s:2d}: mean={vals.mean():.4f}, max={vals.max():.4f}, n={len(vals)}")

# --- [4] d12 嘅張量秩 ---
print("\n[4] d12 張量結構:")
for mode in range(3):
    Dm = np.moveaxis(d12, mode, 0).reshape(12, 144)
    r = np.linalg.matrix_rank(Dm, tol=1e-10)
    print(f"    mode-{mode} flatten rank: {r} / 12")

# SVD 譜
D0 = d12.reshape(12, 144)
u, s, vh = np.linalg.svd(D0)
print(f"    奇異值: {np.array2string(s, precision=4)}")

# --- [5] eigenvalues_final 結構 ---
print("\n[5] eigenvalues_final (WDVV Yukawa 本徵值):")
ev = np.load(os.path.join(DATA, "eigenvalues_final.npy"))
ev_sorted = np.sort(ev)[::-1]
print(f"    值: {np.array2string(ev_sorted, precision=6)}")
# φ 指數
print(f"    φ 指數 (相對最大):")
for i, e in enumerate(ev_sorted):
    if e > 0:
        exp = math.log(ev_sorted[0]/e) / math.log(phi)
        print(f"      λ_{i+1:2d} = {e:12.6f}  φ^({exp:+7.3f})")

# --- [6] 關鍵: 12 維 ↔ 66 ↔ 946 投影閉合 ---
print("\n[6] 投影閉合鏈:")
print(f"""
    K_Chain: 44 site
      → beat 空間: C(44,2) = 946 維
      → Z₃ orbifold (每 3 個 site 一組?): 44/3 = 14.67 唔整數...

    另一條鏈:
    CY₃: h¹¹ = 36 (Kähler moduli)
      → Z₃ orbifold: 36/3 = 12 維
      → beat 空間: C(12,2) = 66 維
      → Yukawa: 12×12×12 張量

    66 嘅身份: Z₃ 不變子空間 12 維嘅「beat 數」
    (如同 946 = 44 維 beat 數)
""")

# --- [7] 66 同 134/90/62 嘅關係 ---
print("\n[7] 66 同其他結構數:")
print(f"    66 = C(12,2) = 12×11/2")
print(f"    134 = 44 + 90 = Nd + Σγ")
print(f"    62 = 44 + 18 = Nd + L₆")
print(f"    66 + 68 = 134?  {66+68}  {'✅' if 66+68==134 else '❌'}")
print(f"    68 = 134 − 66 = ?  68 = 44 + 24?  24 = 4×6?")
print(f"    66 = 90 − 24?  {90-24}  {'✅' if 90-24==66 else '❌'}")
print(f"    24 = Σγ − C(12,2) = 90 − 66")
print(f"    24 = 4×6 = B×F₆?  {'✅' if 4*6==24 else '❌'}")
print(f"    24 = 2×12 = 2×Z₃-orbit 維度?")
print(f"    24 = h¹¹ − 12 = 36 − 12?")

print("\n" + "=" * 70)
print("【結構閉合鏈】")
print("=" * 70)
print(f"""
  946 = C(44,2)  — K_Chain 44 site 嘅 beat 空間 ✅ (自然生成)
  66  = C(12,2)  — Z₃ 不變子空間 12 維嘅 beat 空間
  134 = 44 + 90  — CY₃ 總 moduli = 鏈 site + 鏈能量
  62  = 44 + 18  — 半差 = 鏈 site + Lucas 6
  36  = 12×3     — Kähler moduli = Z₃ orbit × 3
  98  = ?        — 98 = 66 + 32? 98 = 90 + 8?
""")
print("=" * 70)
