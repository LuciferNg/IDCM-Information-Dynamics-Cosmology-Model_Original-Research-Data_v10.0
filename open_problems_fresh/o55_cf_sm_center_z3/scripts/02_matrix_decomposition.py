#!/usr/bin/env python3
"""
O55 — 3c 矩陣結構分解: 不變量、對角化、生成元
================================================
深入分析 3c 矩陣嘅代數結構:
  A. 特徵值/特徵向量分解
  B. Smith 正規形 (SNF)
  C. 生成元分解: 3c = f(SU(3), SU(2), U(1))
  D. 與 SM 電荷嘅關係
  E. 3c 矩陣嘅 SL(3,Z) 分類
"""

import numpy as np
import math, sys

phi = (1 + math.sqrt(5)) / 2
PASS = 0; FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1; print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O55 02: 3c 矩陣結構分解")
print("=" * 70)

# 3c 矩陣
M = np.array([[0, -2, 3],
              [2, -2, -1],
              [1, 3, -2]], dtype=int)

print(f"\n  M = {M[0]}")
print(f"      {M[1]}")
print(f"      {M[2]}")

# ============================================================
# [A] 特徵值/特徵向量分解
# ============================================================
print("\n" + "-" * 70)
print("[A] 特徵值/特徵向量分解")
print("-" * 70)

evals, evects = np.linalg.eig(M)
print(f"\n  本徵值 λ:")
for i, e in enumerate(evals):
    print(f"    λ_{i} = {e:.10f}")

# 特徵多項式: det(λI - M)
print(f"\n  特徵多項式係數:")
coeffs = np.poly(M)
print(f"    det(λI - M) = λ³ + c₂λ² + c₁λ + c₀")
for i, c in enumerate(coeffs):
    print(f"    c_{2-i} = {c:.10f}")

# 檢查: 整數係數?
print(f"  係數整數性: {[abs(c-round(c.real)) < 1e-10 for c in coeffs]}")
check("特徵多項式係數整數", all(abs(c-round(c.real)) < 1e-10 for c in coeffs))

# tr(M) = Σλ
trace_sum = sum(evals)
print(f"\n  tr(M) = {np.trace(M)} = Σλ = {trace_sum:.6f}")
check("tr(M) = Σλ", abs(trace_sum - np.trace(M)) < 1e-10)

# det(M) = Πλ
det_prod = np.prod(evals)
print(f"  det(M) = {round(np.linalg.det(M))} = Πλ = {det_prod:.6f}")
check("det(M) = Πλ", abs(det_prod - round(np.linalg.det(M))) < 1e-6)

# 檢查: 特徵向量結構
print(f"\n  特徵向量 (列):")
for i in range(3):
    v = evects[:, i]
    print(f"    v_{i} = {v}")

# ============================================================
# [B] Smith 正規形 (SNF) — 整數矩陣分類
# ============================================================
print("\n" + "-" * 70)
print("[B] Smith 正規形 (SNF)")
print("-" * 70)

# 手動計算 SNF: 用 numpy 嘅 gcd 等效
# SNF: M = U·D·V, D = diag(d₁, d₂, d₃), d₁|d₂|d₃
# 用 GCD 行列式方法
def smith_normal_form(A):
    """Compute Smith Normal Form of integer matrix A."""
    A = A.copy().astype(int)
    m, n = A.shape
    U = np.eye(m, dtype=int)
    V = np.eye(n, dtype=int)
    
    # 用基本變換化到對角
    # 先處理第一行第一列
    row, col = 0, 0
    while row < min(m, n):
        # 找非零元素
        found = False
        for i in range(row, m):
            for j in range(col, n):
                if A[i, j] != 0:
                    # 交換行/列將非零元素移到 (row, col)
                    if i != row:
                        A[[row, i]] = A[[i, row]]
                        U[[row, i]] = U[[i, row]]
                    if j != col:
                        A[:, [col, j]] = A[:, [j, col]]
                        V[:, [col, j]] = V[:, [j, col]]
                    found = True
                    break
            if found:
                break
        
        if not found:
            break
        
        # 用歐幾里得算法消去同行同列嘅其他元素
        # 簡化版: 只輸出 gcd 結構
        row += 1
        col += 1
    
    # 計算行列式因子 (determinantal divisors)
    # d₁ = gcd of all 1×1 minors
    d1 = abs(np.gcd.reduce(A.flatten()))
    
    # d₂ = gcd of all 2×2 minors
    minors2 = []
    for i1 in range(3):
        for i2 in range(i1+1, 3):
            for j1 in range(3):
                for j2 in range(j1+1, 3):
                    det2 = M[i1, j1]*M[i2, j2] - M[i1, j2]*M[i2, j1]
                    minors2.append(abs(det2))
    d2 = abs(np.gcd.reduce(minors2))
    
    # d₃ = |det(M)|
    d3 = abs(round(np.linalg.det(M)))
    
    # SNF: diag(d₁, d₂/d₁, d₃/d₂)
    s1 = d1
    s2 = d2 // d1 if d1 > 0 else d2
    s3 = d3 // d2 if d2 > 0 else d3
    
    print(f"\n  行列式因子:")
    print(f"    d₁ = gcd(所有元素) = {d1}")
    print(f"    d₂ = gcd(所有 2×2 子式) = {d2}")
    print(f"    d₃ = |det(M)| = {d3}")
    
    print(f"\n  Smith 正規形: diag({s1}, {s2}, {s3})")
    print(f"  驗證: d₁·d₂·d₃ = {s1}×{s2}×{s3} = {s1*s2*s3} = |det(M)| = {d3}")
    check("d₁|d₂|d₃", d2 % d1 == 0 and d3 % d2 == 0, f"({d1}|{d2}|{d3})")
    check("d₁·d₂·d₃ = |det|", s1*s2*s3 == d3, f"({s1}×{s2}×{s3} = {d3})")
    
    # 不變因子
    print(f"\n  不變因子: {s1}, {s2}, {s3}")
    inv_factors = [s1, s2, s3]
    return inv_factors

snf = smith_normal_form(M)

# SNF 嘅意義
print(f"\n  SNF 分類:")
print(f"    M 嘅整數矩陣類型: Z³ → Z³")
print(f"    影像索引: [Z : {snf[0]}Z] × [Z : {snf[1]}Z] × [Z : {snf[2]}Z]")
print(f"    核: 秩 = {np.linalg.matrix_rank(M)}")
print(f"    余核: det = {abs(round(np.linalg.det(M)))}")
print(f"    → 余核大小 = {snf[0]}×{snf[1]}×{snf[2]} = {snf[0]*snf[1]*snf[2]}")

# ============================================================
# [C] 生成元分解: 3c = f(SU(3), SU(2), U(1))
# ============================================================
print("\n" + "-" * 70)
print("[C] 生成元分解 — SM 規範群量子數")
print("-" * 70)

# SM 量子數
# Quarks: SU(3)_c = 3, SU(2)_L = 2, U(1)_Y = 1/6 (doublet)
# 3c_f values vs SM quantum numbers

# 構建 SM 量子數矩陣
# 粒子: u, d, e, c, s, μ, t, b, τ
# Q = electric charge, T₃ = weak isospin, Y = hypercharge
# SU(3)_c triality: quarks=1, leptons=0

sm_data = {
    # particle: (Q, T₃, Y, triality, 3c)
    'u':  (2/3,  1/2, 1/3, 1, 0),
    'd':  (-1/3, -1/2, 1/3, 1, -2),
    'e':  (-1,   -1/2, -1,  0, 3),
    'c':  (2/3,  1/2, 1/3, 1, 2),
    's':  (-1/3, -1/2, 1/3, 1, -2),
    'μ':  (-1,   -1/2, -1,  0, -1),
    't':  (2/3,  1/2, 1/3, 1, 1),
    'b':  (-1/3, -1/2, 1/3, 1, 3),
    'τ':  (-1,   -1/2, -1,  0, -2),
}

print(f"{'粒子':>4} {'Q':>6} {'T₃':>6} {'Y':>6} {'tri':>4} {'3c':>4} {'3c-baryonic':>12}")
print("-" * 50)
for p, (q, t3, y, tr, c3) in sm_data.items():
    # 3c = ?
    # 嘗試: 3c = a·Q + b·T₃ + c·Y + d·triality
    print(f"  {p:>3} {q:>6.2f} {t3:>6.2f} {y:>6.2f} {tr:>4} {c3:>4}")

# 線性回歸: 3c = a·Q + b·T₃ + c·Y + d·triality
X = np.array([[sm_data[p][0], sm_data[p][1], sm_data[p][2], sm_data[p][3]] for p in sm_data])
y = np.array([sm_data[p][4] for p in sm_data])

# 求解線性系統
coeff, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
print(f"\n  線性模型: 3c = a·Q + b·T₃ + c·Y + d·triality")
print(f"    a = {coeff[0]:.6f}")
print(f"    b = {coeff[1]:.6f}")
print(f"    c = {coeff[2]:.6f}")
print(f"    d = {coeff[3]:.6f}")

# 預測
y_pred = X @ coeff
errors = y - y_pred
print(f"\n  預測誤差:")
max_err = 0
for i, (p, _) in enumerate(sm_data.items()):
    err = abs(errors[i])
    max_err = max(max_err, err)
    print(f"    {p}: 3c_true={y[i]}, 3c_pred={y_pred[i]:.4f}, err={err:.6f}")

check("線性模型 max_err < 1e-10", max_err < 1e-10, f"(max_err={max_err:.2e})")

# 如果成功, 顯示整數係數
if max_err < 1e-10:
    coeff_int = [round(c) for c in coeff]
    print(f"\n  ✅ 精確線性關係!")
    print(f"  3c = {coeff_int[0]}·Q + {coeff_int[1]}·T₃ + {coeff_int[2]}·Y + {coeff_int[3]}·triality")
    print(f"  驗證: 代入 u: Q=2/3, T₃=1/2, Y=1/3, tri=1")
    print(f"    3c = {coeff_int[0]}×2/3 + {coeff_int[1]}×1/2 + {coeff_int[2]}×1/3 + {coeff_int[3]}×1")
else:
    print(f"\n  ❌ 無精確線性關係 (max_err = {max_err:.2e})")
    print(f"  → c_f 唔係 SM 量子數嘅簡單線性組合")

# 嘗試: 只靠 Q 同 triality
X2 = np.array([[sm_data[p][0], sm_data[p][3]] for p in sm_data])
coeff2, residuals2, rank2, s2 = np.linalg.lstsq(X2, y, rcond=None)
y_pred2 = X2 @ coeff2
errors2 = y - y_pred2
max_err2 = max(abs(errors2))
print(f"\n  簡化模型: 3c = a·Q + b·triality")
print(f"    a = {coeff2[0]:.6f}, b = {coeff2[1]:.6f}")
for i, (p, _) in enumerate(sm_data.items()):
    print(f"    {p}: 3c_true={y[i]}, 3c_pred={y_pred2[i]:.4f}, err={errors2[i]:.6f}")
check("2-參數模型 max_err < 1e-10", max_err2 < 1e-10, f"(max_err={max_err2:.2e})")

# 嘗試: 3c = 3Q - 3T₃ - 3Y + triality? (猜測有理組合)
# Q = T₃ + Y/2 (SM 恆等式)
# 所以 3Q = 3T₃ + 3Y/2

# 嘗試: 3c = A·Q + B·T₃ + C (只用 Q, T₃)
X3 = np.array([[sm_data[p][0], sm_data[p][1], 1] for p in sm_data])
coeff3, residuals3, rank3, s3 = np.linalg.lstsq(X3, y, rcond=None)
y_pred3 = X3 @ coeff3
errors3 = y - y_pred3
max_err3 = max(abs(errors3))
print(f"\n  3-參數模型: 3c = a·Q + b·T₃ + c")
print(f"    a = {coeff3[0]:.6f}, b = {coeff3[1]:.6f}, c = {coeff3[2]:.6f}")
for i, (p, _) in enumerate(sm_data.items()):
    print(f"    {p}: 3c_true={y[i]}, 3c_pred={y_pred3[i]:.4f}, err={errors3[i]:.6f}")
check("3-參數模型 max_err < 1e-10", max_err3 < 1e-10, f"(max_err={max_err3:.2e})")

# ============================================================
# [D] 3c 矩陣同 SM 電荷嘅關係
# ============================================================
print("\n" + "-" * 70)
print("[D] 3c 矩陣 vs SM 電荷矩陣")
print("-" * 70)

# SM 電荷矩陣 (3c 格式)
# 粒子: u/d/e, c/s/μ, t/b/τ
# SM 電荷: u=2/3, d=-1/3, e=-1, c=2/3, s=-1/3, μ=-1, t=2/3, b=-1/3, τ=-1
# 3Q: u=2, d=-1, e=-3, c=2, s=-1, μ=-3, t=2, b=-1, τ=-3

Q_sm = np.array([[2, -1, -3],
                 [2, -1, -3],
                 [2, -1, -3]], dtype=int)

print(f"\n  SM 3Q 矩陣:")
print(f"  {Q_sm[0]}  ← gen1 (u, d, e)")
print(f"  {Q_sm[1]}  ← gen2 (c, s, μ)")
print(f"  {Q_sm[2]}  ← gen3 (t, b, τ)")

print(f"\n  IDCM 3c 矩陣:")
print(f"  {M[0]}")
print(f"  {M[1]}")
print(f"  {M[2]}")

# 差異: SM 3Q 係常數列, IDCM 3c 係可變
print(f"\n  SM 3Q: 每列常數 (所有世代同電荷)")
print(f"  IDCM 3c: 每列可變 (世代相關)")
print(f"  → c_f 包含世代信息, Q 唔包含")
print(f"  → c_f 係「代相關電荷」, 唔係 SM 電荷")

# 但兩者嘅關係?
# 3c - 3Q = ?
diff = M - Q_sm
print(f"\n  3c - 3Q 差異:")
print(f"  {diff[0]}")
print(f"  {diff[1]}")
print(f"  {diff[2]}")
print(f"  U column diff: {diff[:, 0]}")
print(f"  D column diff: {diff[:, 1]}")
print(f"  L column diff: {diff[:, 2]}")
print(f"  → U: u/c/t 各差 [-2, 0, -1]")
print(f"  → D: d/s/b 各差 [-1, -1, 4]")
print(f"  → L: e/μ/τ 各差 [6, 2, 1]")

# 3c + 3Q = ?
sum_mat = M + Q_sm
print(f"\n  3c + 3Q:")
print(f"  {sum_mat[0]}")
print(f"  {sum_mat[1]}")
print(f"  {sum_mat[2]}")

# ============================================================
# [E] 3c 矩陣嘅 SL(3,Z) 分類
# ============================================================
print("\n" + "-" * 70)
print("[E] SL(3,Z) 分類 — 矩陣嘅整數對稱群")
print("-" * 70)

# 檢查: M 係咪 SL(3,Z) 元素?
det_M = round(np.linalg.det(M))
print(f"  det(M) = {det_M}")
check("det(M) = ±18 ≠ ±1, 唔係 SL(3,Z)", abs(det_M) != 1, f"(det={det_M})")

# 但 M/3 呢?
M3 = M / 3
print(f"\n  M/3 (c_f 矩陣):")
print(f"  {M3[0]}")
print(f"  {M3[1]}")
print(f"  {M3[2]}")
print(f"  det(M/3) = {np.linalg.det(M3):.6f} = {det_M}/27 = {det_M/27:.6f}")

# 檢查 M mod 3
M_mod3 = M % 3
print(f"\n  M mod 3:")
print(f"  {M_mod3[0]}")
print(f"  {M_mod3[1]}")
print(f"  {M_mod3[2]}")
print(f"  det(M mod 3) = {round(np.linalg.det(M_mod3))}")
check("M mod 3 可逆? (det ≠ 0 mod 3)", 
      round(np.linalg.det(M_mod3)) % 3 != 0, 
      f"(det(M) mod 3 = {round(np.linalg.det(M_mod3)) % 3})")

# 特徵值嘅代數結構
# λ³ - tr(M)λ² + ... - det(M) = 0
# λ³ + 4λ² - 23λ - 18 = 0 (大約)
print(f"\n  特徵多項式: det(λI - M) = λ³ + c₂λ² + c₁λ + c₀")
print(f"    c₂ = -tr(M) = {round(-np.trace(M))}")
print(f"    c₁ = {coeffs[1]:.0f}")
print(f"    c₀ = -det(M) = {-det_M}")

# ============================================================
# 總結
# ============================================================
print("\n" + "-" * 70)
print("[F] 結論")
print("-" * 70)

print(f"""
  SNF: diag({snf[0]}, {snf[1]}, {snf[2]})
  → 整數矩陣分類: Z³/im(M) = Z_{snf[0]} × Z_{snf[1]} × Z_{snf[2]}
  → 余核大小 = {snf[0]*snf[1]*snf[2]} = |det(M)| = 18

  3c 同 SM 量子數嘅關係:
  {"✅ 有精確線性關係" if max_err < 1e-10 else "❌ 無精確線性關係"}
  {"✅ 2-參數模型成立" if max_err2 < 1e-10 else "❌ 2-參數模型唔成立"}
  {"✅ 3-參數模型成立" if max_err3 < 1e-10 else "❌ 3-參數模型唔成立"}

  M mod 3:
  {"✅ 可逆 (Z₃ 上非退化)" if round(np.linalg.det(M_mod3)) % 3 != 0 else "❌ 唔可逆"}

  🔴 未解決:
    □ c_f 嘅生成元公式: 3c = ?
    □ 點解 D column 有 d=s=-2 但 b=3?
    □ 3c 矩陣嘅 K_Chain 起源?
""")

print("=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)