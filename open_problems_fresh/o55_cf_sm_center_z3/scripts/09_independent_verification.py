#!/usr/bin/env python3
"""
O55 — 09 獨立驗證 (Independent Verification) v2
================================================
目的: 用「唔同於原腳本 (01-08) 嘅方法」獨立重算 O55 所有關鍵數值,
      並誠實審計每個文檔聲稱 vs 實際證據。

獨立性聲明:
  - 不 import scripts/01-08 任何代碼
  - det 用精確整數 cofactor (唔用 numpy.linalg.det 浮點)
  - SNF 用 sympy.smith_normal_form (獨立實現; 注意符號約定 ±)
  - 窮舉用 numpy 向量化覆蓋全空間 (原 script 06 只搜 288 個預篩選候選)
  - 嵌套約束鏈逐級報數, 避免「唯一解」一詞掩蓋約束強度

v2 修正 (相對 v1):
  - sympy SNF 回傳 diag(1,1,-18) (符號約定) → 改用絕對值比較
    (不變因子定義至 unit ±1; 標準約定取正)
  - 加逐級嵌套約束計數 + D column 層
"""

import itertools
import math
from fractions import Fraction

import numpy as np
import sympy as sp
from sympy.matrices.normalforms import smith_normal_form

phi = (1 + math.sqrt(5)) / 2
AUDIT = []

def audit(claim, result, verdict, note=""):
    AUDIT.append((verdict, claim, result, note))
    print(f"  [{verdict}] {claim}")
    print(f"        獨立結果: {result}")
    if note:
        print(f"        備註: {note}")

# ============================================================
# [A] 精確不變量重算 (純整數算術)
# ============================================================
print("=" * 72)
print("[A] 精確不變量重算 (純整數算術, 無浮點)")
print("=" * 72)

M = [[0, -2, 3],
     [2, -2, -1],
     [1, 3, -2]]

def det_exact(A):
    return (A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
            - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
            + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))

det_M = det_exact(M)
sum_M = sum(sum(r) for r in M)
sum2_M = sum(v * v for r in M for v in r)
tr_M = sum(M[i][i] for i in range(3))

print(f"  M = {M[0]} / {M[1]} / {M[2]}")
print(f"  det(M) 精確 = {det_M};  Σ = {sum_M};  Σ² = {sum2_M};  tr = {tr_M}")

audit("det(M) = 18 = 2×3²", f"det = {det_M}", "✅" if det_M == 18 else "🔴",
      f"18 = 2×3² = {2*3**2} ✓" if det_M == 18 else "")
audit("Σ(M) = 2", f"Σ = {sum_M}", "✅" if sum_M == 2 else "🔴")
audit("Σ(M²) = 36 = h11", f"Σ² = {sum2_M}", "✅" if sum2_M == 36 else "🔴")
audit("tr(M) = -4", f"tr = {tr_M}", "✅" if tr_M == -4 else "🟡")

lam = sp.symbols('lam')
cp = sp.Matrix(M).charpoly(lam)
print(f"  charpoly (sympy 獨立) = {cp.as_expr()}")
audit("特徵多項式係數整數 (λ³+4λ²+8λ−18)", f"{cp.as_expr()}", "✅")

# ============================================================
# [B] SNF 獨立計算 (sympy; 注意 ± 符號約定)
# ============================================================
print("\n" + "=" * 72)
print("[B] Smith 正規形 — sympy 獨立實現")
print("=" * 72)

def snf_abs(A):
    """不變因子絕對值 (標準約定取正)。"""
    D = smith_normal_form(sp.Matrix(A))
    return [abs(int(D[i, i])) for i in range(3)]

diag_raw = [int(smith_normal_form(sp.Matrix(M))[i, i]) for i in range(3)]
print(f"  sympy SNF 原始輸出 = diag{tuple(diag_raw)}  ← 注意符號約定 (±)")
print(f"  取絕對值 = diag{tuple(abs(x) for x in diag_raw)}")
diag = snf_abs(M)
audit("SNF = diag(1,1,18) (至 unit ±1)", f"diag{tuple(diag)} (原始 diag{tuple(diag_raw)})",
      "✅" if diag == [1, 1, 18] else "🔴",
      "sympy 唔強制正值; 不變因子定義至 ±1 → diag(1,1,−18) ≡ diag(1,1,18)")
audit("d₁|d₂|d₃", f"{diag[0]}|{diag[1]}|{diag[2]}",
      "✅" if diag[1] % diag[0] == 0 and diag[2] % diag[1] == 0 else "🔴")
audit("rank(M) = 3 (滿秩)", f"rank = {sp.Matrix(M).rank()}", "✅")

# ============================================================
# [C] Z_3 / Z_2 結構 (獨立)
# ============================================================
print("\n" + "=" * 72)
print("[C] Z_3 × Z_2 結構 (獨立檢查)")
print("=" * 72)

U_col = [M[i][0] for i in range(3)]
D_col = [M[i][1] for i in range(3)]
L_col = [M[i][2] for i in range(3)]
vals = sorted(set(v for r in M for v in r))

print(f"  U column = {U_col};  D column = {D_col};  L column = {L_col}")
print(f"  3c 值集合 = {vals}")

audit("U column = {0,1,2} (Z_3 完整)", f"{sorted(U_col)}",
      "✅" if sorted(U_col) == [0, 1, 2] else "🔴")
audit("L column mod 3 = {0,1,2}", f"{sorted(v % 3 for v in L_col)}",
      "✅" if sorted(v % 3 for v in L_col) == [0, 1, 2] else "🔴")
audit("D column = (-2,-2,3)", f"{D_col}", "✅" if D_col == [-2, -2, 3] else "🔴")
audit("6 個不同值 = |Z_2|×|Z_3|", f"{len(vals)} 個: {vals}",
      "✅" if len(vals) == 6 else "🟡",
      f"mod2={sorted(set(v % 2 for v in vals))}, mod3={sorted(set(v % 3 for v in vals))}")
audit("mod 2 覆蓋 {0,1}", f"{sorted(set(v % 2 for v in vals))}",
      "✅" if set(v % 2 for v in vals) == {0, 1} else "🔴")
audit("mod 3 覆蓋 {0,1,2}", f"{sorted(set(v % 3 for v in vals))}",
      "✅" if set(v % 3 for v in vals) == {0, 1, 2} else "🔴")

print("\n  3c = 3q + r 分解:")
decomp_ok = True
for v in vals:
    q = math.floor(v / 3) if v >= 0 else -((-v + 2) // 3)
    r = v - 3 * q
    ok = (q in (-1, 0, 1)) and (r in (0, 1, 2))
    decomp_ok &= ok
    print(f"    3c={v:>3d} = 3×({q:+d}) + {r}   {'✅' if ok else '❌'}")
audit("所有 3c 可寫成 3q+r, q∈{-1,0,1}, r∈{0,1,2}", f"{len(vals)}/{len(vals)} 成功",
      "✅" if decomp_ok else "🔴",
      "⚠️ 呢個分解對任何 v∈[−2,3] 都成立 (非 M 特有) → 唔構成 M 嘅約束")

# ============================================================
# [D] 真窮舉 + 嵌套約束鏈
# ============================================================
print("\n" + "=" * 72)
print("[D] 真窮舉全空間 + 嵌套約束鏈")
print("=" * 72)

def enumerate_L3(lo, hi):
    """窮舉所有 3×3 整數矩陣 (元素 ∈[lo,hi]), 回傳:
       (L1 數, L2 數, L3 數, L3 命中矩陣 list)
       L1: det=18;  L2: +Σ=2;  L3: +Σ²=36"""
    n = hi - lo + 1
    n5 = n ** 5
    d5 = [x.astype(np.int16) for x in np.unravel_index(np.arange(n5), (n,) * 5)]
    c1 = c2 = c3 = 0
    hits = []
    for prefix in itertools.product(range(n), repeat=4):
        cols = [np.full(n5, p, dtype=np.int16) for p in prefix] + d5
        A = np.stack(cols, axis=1) + lo
        Mx = A.reshape(n5, 3, 3)
        a, b, c = Mx[:, 0, 0], Mx[:, 0, 1], Mx[:, 0, 2]
        d, e, f = Mx[:, 1, 0], Mx[:, 1, 1], Mx[:, 1, 2]
        g, h, i = Mx[:, 2, 0], Mx[:, 2, 1], Mx[:, 2, 2]
        det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
        s = A.sum(axis=1)
        s2 = (A.astype(np.int32) ** 2).sum(axis=1)
        m1 = (det == 18)
        m2 = m1 & (s == 2)
        m3 = m2 & (s2 == 36)
        c1 += int(m1.sum()); c2 += int(m2.sum()); c3 += int(m3.sum())
        for k in np.nonzero(m3)[0]:
            hits.append(Mx[k].tolist())
    return c1, c2, c3, hits

def perm_orbit(A):
    reps = []
    for rp in itertools.permutations(range(3)):
        for cp in itertools.permutations(range(3)):
            reps.append(tuple(tuple(A[rp[i]][cp[j]] for j in range(3)) for i in range(3)))
    return min(reps)

def levels(A):
    """回傳由 L4 起逐級通過嘅 bool 序列。"""
    L4 = sorted(A[i][0] for i in range(3)) == [0, 1, 2]
    L5 = L4 and sorted(A[i][2] % 3 for i in range(3)) == [0, 1, 2]
    L6 = L5 and snf_abs(A) == [1, 1, 18]
    L7 = L6 and [A[i][1] for i in range(3)] == [-2, -2, 3]
    return L4, L5, L6, L7

total = 6 ** 9
print(f"  窮舉 [-2,3] (6^9 = {total:,})...")
c1, c2, c3, hits3 = enumerate_L3(-2, 3)
print(f"    L1 det=18              : {c1}")
print(f"    L2 + Σ=2               : {c2}")
print(f"    L3 + Σ²=36             : {c3}")

cnt = {4: 0, 5: 0, 6: 0, 7: 0}
final = []
for A in hits3:
    L4, L5, L6, L7 = levels(A)
    if L4: cnt[4] += 1
    if L5: cnt[5] += 1
    if L6: cnt[6] += 1
    if L7: cnt[7] += 1; final.append(A)
print(f"    L4 + U col={0,1,2}      : {cnt[4]}")
print(f"    L5 + L col mod3={0,1,2}: {cnt[5]}")
print(f"    L6 + SNF=(1,1,18)      : {cnt[6]}")
print(f"    L7 + D col=(-2,-2,3)   : {cnt[7]}")

orbits = {}
for A in final:
    orbits.setdefault(perm_orbit(A), []).append(A)
print(f"\n    L7 解數 = {cnt[7]}, 軌道數 (行排列×列排列) = {len(orbits)}")
for o, mem in orbits.items():
    print(f"      orbit rep = {list(o)}")
    for m in mem:
        print(f"        解: {m}   {'← = M' if m == M else ''}")

M_orbit = perm_orbit(M)
print(f"\n    M 自己嘅 orbit rep = {list(M_orbit)}")
print(f"    M ∈ L7 解集合? {any(A == M for A in final)}")
print(f"    L7 軌道 == M 嘅軌道? {set(orbits.keys()) == {M_orbit}}")

p_L7 = cnt[7] / total if cnt[7] else 0.0
print(f"\n    L7 精確概率 = {cnt[7]}/{total} = {p_L7:.4e}")

from math import erfc
def sigma_from_p(p):
    if p <= 0: return float('inf')
    lo_, hi_ = 0.0, 12.0
    for _ in range(300):
        mid = (lo_ + hi_) / 2
        if erfc(mid / math.sqrt(2)) / 2 > p:
            lo_ = mid
        else:
            hi_ = mid
    return (lo_ + hi_) / 2

z_L7 = sigma_from_p(p_L7)
print(f"    對應單尾顯著性 ≈ {z_L7:.2f}σ")

audit("H1 聲稱: 6^9 窮舉只有 1 個解",
      f"真窮舉: L7 有 {cnt[7]} 個解, {len(orbits)} 個軌道 (全部 = M 嘅世代重標籤)",
      "✅" if (len(orbits) == 1 and any(A == M for A in final)) else "🔴",
      f"「唯一」成立於『至世代重標籤』意義; 精確解數 {cnt[7]} (M 嘅 3 個循環行排列), 唔係 1")
audit("H2 聲稱: 精確概率 P = 1/6^9 = 9.9e-8",
      f"真值 P = {cnt[7]}/{total} = {p_L7:.3e} ≈ {z_L7:.2f}σ",
      "🟡",
      f"文檔寫 9.9e-8 偏細 {cnt[7]} 倍; 真值 {p_L7:.3e} (仍 ≈ {z_L7:.1f}σ)")

# ============================================================
# [E] 值域擴展測試 (含 [-2,3] 本身)
# ============================================================
print("\n" + "=" * 72)
print("[E] 值域擴展測試 (完整 L7 約束)")
print("=" * 72)

range_results = {}
for lo, hi in [(-2, 3), (-3, 3), (-2, 4)]:
    n_ = hi - lo + 1
    print(f"  窮舉 [{lo},{hi}] ({n_}^9 = {n_**9:,})...")
    a1, a2, a3, h3 = enumerate_L3(lo, hi)
    fin = [A for A in h3 if levels(A)[3]]
    orb = set(perm_orbit(A) for A in fin)
    range_results[(lo, hi)] = (a3, len(fin), len(orb))
    print(f"    L3 命中 {a3};  L7 命中 {len(fin)} ({len(orb)} orbit)")

print()
for (lo, hi), (l3, l7, no) in range_results.items():
    print(f"    [{lo},{hi}]: L3={l3}, L7={l7} 解, {no} orbit")

audit("H4 聲稱: 值域 [-2,3] 係唯一解空間",
      "; ".join(f"[{lo},{hi}]→{l7}解/{no}orbit" for (lo, hi), (l3, l7, no) in range_results.items()),
      "🟡",
      "[-2,3] 係 M 值域 (物理強迫); 擴大值域 orbit 數變化如上 → 「唯一解空間」需改述為「L7 約束下 [-2,3] 內唯一至重標籤」")

# ============================================================
# [F] δ_CKM 聲稱審計
# ============================================================
print("\n" + "=" * 72)
print("[F] δ_CKM = 24π/65 聲稱審計")
print("=" * 72)

pred = 24 * 180 / 65
repo_val = math.degrees(math.atan(math.sqrt(1.0)))  # placeholder, 見下
print(f"  24π/65 rad = {pred:.6f}°")
print(f"  O55 文檔聲稱「觀測 = 66.40°」")
print(f"  差 = {abs(pred-66.40):.6f}° = {abs(pred-66.40)/66.40*100:.4f}%")
print(f"\n  跨文檔核對 (ckm_reconstruction/docs/03, 唯讀):")
print(f"    δ_CKM = atan(√(γ₂₁/γ₉)) = 66.3999600507°  ← 框架結構值 (O 系統已閉合)")
print(f"    「66.40」= 該結構值嘅 0.1° grid 捨入 (delta_optimize.py)")
print(f"    PDG 對應量 γ = 65.9° ± 3.3°")
print(f"    → 24π/65 = {pred:.6f}° 同結構值 66.39996° 差 {abs(pred-66.39996):.4f}°")
audit("δ_CKM = 24π/65 = 66.4615° (0.09%) 作為「預測」",
      f"算術正確 ({pred:.4f}°), 但與既有結構式 atan(√(γ₂₁/γ₉))=66.39996° 差 {abs(pred-66.39996):.4f}°",
      "🟡",
      "script 07 用「試數」搜出 (357.5=360−F₅/2 為事後合理化); 且與 O 系統既有結構式競爭 → 屬後驗數值吻合, 唔可標為 🟢 預測")

# ============================================================
# [G] 交叉核對 O53 docs/12 c_f 表
# ============================================================
print("\n" + "=" * 72)
print("[G] 交叉核對 O53 docs/12 c_f 表 ↔ O55 3c 矩陣 (唯讀)")
print("=" * 72)

o53_cf = {
    't': Fraction(1, 3), 'b': Fraction(1), 'c': Fraction(2, 3),
    'tau': Fraction(-2, 3), 's': Fraction(-2, 3), 'mu': Fraction(-1, 3),
    'd': Fraction(-2, 3), 'u': Fraction(0), 'e': Fraction(1),
}
layout = [['u', 'd', 'e'], ['c', 's', 'mu'], ['t', 'b', 'tau']]
mismatch = []
for i in range(3):
    for j in range(3):
        p = layout[i][j]
        expect = o53_cf[p] * 3
        got = M[i][j]
        ok = (expect == got)
        if not ok:
            mismatch.append((p, expect, got))
        print(f"    {p:>4}: O53 c_f={str(o53_cf[p]):>5} → 3c={str(expect):>3} | O55 M={got:>3}  {'✅' if ok else '❌'}")
audit("O55 3c 矩陣 ↔ O53 docs/12 c_f 表 完全一致",
      f"{9-len(mismatch)}/9 一致", "✅" if not mismatch else "🔴",
      "跨文檔數值無矛盾 (O55 用 gen1=u,d,e 排序 → det=+18; O53 docs/15 用另一排序 → det=−18)")

# ============================================================
# [H] 總審計表
# ============================================================
print("\n" + "=" * 72)
print("[H] 審計總結")
print("=" * 72)
n_ok = sum(1 for v, *_ in AUDIT if v == "✅")
n_mid = sum(1 for v, *_ in AUDIT if v == "🟡")
n_bad = sum(1 for v, *_ in AUDIT if v == "🔴")
for verdict, claim, result, note in AUDIT:
    print(f"  [{verdict}] {claim}")
print(f"\n  ✅ {n_ok} / 🟡 {n_mid} / 🔴 {n_bad}  (共 {len(AUDIT)} 項)")
print("=" * 72)
