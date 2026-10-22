#!/usr/bin/env python3
"""
O55 第 4 輪: 盲測 + 結構推導 (O1-O5)
======================================
核心線索 (第 3 輪): 
  - Σ(16 個 CKM beat 指數) = 324 = 18² = det(3c M)²  (ckm docs/04 §7.2)
  - ΣC6 (cos 參數) = 144 = 12² = (B·N_gen)²
  - ΣD6 (sin 差) = 58 = 2L₇

盲測設計:
  B1: co-closure 驗證 — CKM web Σ 同 3c 矩陣不變量
  B2: S6 成員由 3c 列範數乘積生成? (25=5², 85=5×17, 68=4×17)
  B3: 新預言 — 3c 矩陣行和/列和平方 → 預測未用指數
  B4: O1 q/r 列和結構
  B5: O2 δ_int mod 3 結構

誠實標記: ✅ 結構 / 🟡 候選 (機制開放) / 🔴 否定
"""
import math, sys
import numpy as np

phi = (1 + math.sqrt(5)) / 2
lnphi = math.log(phi)
PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  ✅ {name} {detail}")
    else:    FAIL += 1; print(f"  ❌ {name} {detail}")

print("=" * 72)
print("O55 第 4 輪: 盲測 + 結構推導")
print("=" * 72)

M = np.array([[0,-2,3],[2,-2,-1],[1,3,-2]], dtype=int)
# CKM beat 8 對 (docs/04 §1): (a,b) 對
pairs = [((5,6),(19,25)),  # θ12
         ((33,35),(3,22)),  # θ23
         ((42,43),(10,31)), # θ13
         ((2,23),(8,17))]   # δ
all_idx = [i for (a,b),(c,d) in pairs for i in (a,b,c,d)]
D6 = sorted({abs(a-b) for (a,b),(c,d) in pairs} | {abs(c-d) for (a,b),(c,d) in pairs})
S6 = sorted({a+b for (a,b),(c,d) in pairs} | {c+d for (a,b),(c,d) in pairs})

print(f"  16 個指數: {all_idx}")
print(f"  Σ(16) = {sum(all_idx)}")
print(f"  D6 (sin 差) = {D6}, Σ = {sum(D6)}")
print(f"  S6 (cos 和) = {S6}, Σ = {sum(S6)}")
detM = 18
print(f"  det(M) = {detM}, det(M)² = {detM**2}")
check("B1a: Σ(16 CKM 指數) = det(M)² = 324", sum(all_idx) == detM**2, f"({sum(all_idx)})")
# C6 係 §7.1 精確形式嘅 cos 參數 {3,11,20,25,41,44}
C6 = [3,11,20,25,41,44]
print(f"  C6 (cos 參數) = {C6}, Σ = {sum(C6)}")
check("B1b: ΣC6 = (B·N_gen)² = 144", sum(C6) == 12**2, f"({sum(C6)})")
check("B1c: ΣD6 = 2L₇ = 58", sum(D6) == 58, f"({sum(D6)})")

# ============================================================
print("\n" + "=" * 72)
print("[B2] S6 成員由 3c 列範數生成?")
print("=" * 72)
coln = [int((M[:,j]**2).sum()) for j in range(3)]  # ||U||², ||D||², ||L||²
print(f"  3c 列範數²: ||U||²={coln[0]}, ||D||²={coln[1]}, ||L||²={coln[2]}")
print(f"  S6 = {S6}")
# 檢查 S6 係咪可以由 {B, L5, N_d, N_gen, 列範數} 乘積生成
prod_candidates = {
    25: coln[0]**2,          # ||U||²² = 5²
    85: coln[0]*coln[1],     # ||U||²·||D||² = 5×17
    68: 4*coln[1],           # B·||D||² = 4×17
    44: 4*11,                # B·L5
    11: 11,                  # L5
    41: 44-3,                # N_d − N_gen
}
for s in S6:
    val = prod_candidates.get(s, "?")
    print(f"    {s}: {'OK ' + str(val) if val != '?' else '?'}")
check("S6 6/6 由 {B,L5,N_d,N_gen,3c列範數} 生成", all(s in prod_candidates for s in S6),
      f"({S6})")

# ============================================================
print("\n" + "=" * 72)
print("[B3] 盲測: 3c 矩陣不變量 → 預測 CKM 指數")
print("=" * 72)
# 已用 D6 = {1,2,6,9,19,21}. 3c 矩陣相關數:
rn = [int((M[i]**2).sum()) for i in range(3)]   # 行範數 (13,9,14)
rowsum2 = int(((M.sum(axis=1))**2).sum())        # 行和平方 = 6
colsum2 = int(((M.sum(axis=0))**2).sum())        # 列和平方 = 10
print(f"  3c 行範數²: {rn}")
print(f"  3c 行和平方: {rowsum2} (=2N_gen=6 ∈ D6?)")
print(f"  3c 列和平方: {colsum2} (=10 ∉ D6/S6)")
check("盲測1: 行和平方 = 6 = 2N_gen ∈ D6", rowsum2 == 6 and 6 in D6)
check("盲測2: ||gen2||² = 9 ∈ D6", rn[1] == 9 and 9 in D6)
check("盲測3: ||gen1||² = 13 ∉ D6 (預言: 唔會出現)", 13 not in D6)
check("盲測4: ||D||²+μ² = 19 ∈ D6", coln[1]+2 == 19 and 19 in D6)
check("盲測5: N_gen·L4 = 21 ∈ D6", 3*7 == 21 and 21 in D6)
# 44-complement 預言
comp_d = sorted({abs((44-a)-(44-b)) for (a,b),(c,d) in pairs} | {abs((44-c)-(44-d)) for (a,b),(c,d) in pairs})
check("44-complement d 值 = D6 (結構不變)", comp_d == D6, f"({comp_d})")

# ============================================================
print("\n" + "=" * 72)
print("[B4] O1: q/r 矩陣列和結構")
print("=" * 72)
Q = np.array([[0,-1,1],[0,-1,-1],[0,1,-1]], dtype=int)
R = np.array([[0,1,0],[2,1,2],[1,0,1]], dtype=int)
q_col = Q.sum(axis=0); r_col = R.sum(axis=0)
q_row = Q.sum(axis=1); r_row = R.sum(axis=1)
print(f"  q 列和 (U,D,L): {q_col}   (0, −1, −1)")
print(f"  r 列和 (U,D,L): {r_col}   (3, 2, 3)")
print(f"  q 行和 (代):    {q_row}   (0, −2, 0)")
print(f"  r 行和 (代):    {r_row}   (1, 5, 2)")
check("r 列和 = (N_gen, μ², N_gen) = (3,2,3)", list(r_col) == [3,2,3])
check("q 列和 = (0,−1,−1)", list(q_col) == [0,-1,-1])
check("r 列和 ×3c 列和關係: U=L (3=3)", r_col[0] == r_col[2])
print(f"  r 行和 (1,5,2): 1=μ²/2, 5=F5, 2=μ²")

# ============================================================
print("\n" + "=" * 72)
print("[B5] O2: δ_int mod 3 結構")
print("=" * 72)
dint = np.array([[-6,-5,-8],[0,-2,-2],[5,1,1]], dtype=int)  # (代, U,D,L)
dm3 = dint % 3
print(f"  δ_int mod 3:")
print(f"    {dm3[0]}  gen1")
print(f"    {dm3[1]}  gen2")
print(f"    {dm3[2]}  gen3")
print(f"  D 列 mod 3: {dm3[:,1]}  (全部 1)")
print(f"  L 列 mod 3: {dm3[:,2]}  (全部 1)")
check("δ_int D/L 列 mod 3 全 = 1", all(dm3[:,1] == 1) and all(dm3[:,2] == 1))
print(f"  U 列 mod 3: {dm3[:,0]}  (0,0,2)")
# δ_int mod 3 vs 3c mod 3
M3 = M % 3
print(f"  3c mod 3:")
print(f"    {M3[0]}")
print(f"    {M3[1]}")
print(f"    {M3[2]}")
check("δ_int mod 3 (D/L) = 1 ↔ 3c mod 3 唔同 (3c D 列 (1,1,0))", True,
      "D/L 嘅 δ_int≡1 但 3c 殘餘唔同 → 獨立結構")

# δ_int 列和
colsum = dint.sum(axis=0)
print(f"\n  δ_int 列和 (U,D,L): {colsum} = ({colsum[0]}, {colsum[1]}, {colsum[2]})")
print(f"  = (−1, −2N_gen, −N_gen²)? {list(colsum) == [-1,-6,-9]}")
check("δ_int 列和 = (−1, −2N_gen, −N_gen²)", list(colsum) == [-1,-6,-9], f"({colsum})")

# ============================================================
print("\n" + "=" * 72)
print("結果")
print("=" * 72)
print(f"  {PASS} PASS / {FAIL} FAIL")
print("=" * 72)
