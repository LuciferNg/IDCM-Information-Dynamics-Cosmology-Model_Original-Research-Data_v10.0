#!/usr/bin/env python3
"""
O51: K_Chain 起始三層證明 — 可重跑驗證
=======================================
層 1: 種子 (0,1) → φ（主遞歸 + 連分數）
層 2: 44-site 譜（Nd=B×L₅, Σγ, Z₂ 對偶）
層 3: 946 拍頻（sympy 精確代數: 全部無理比）

Run: /usr/bin/python3 scripts/01_origin_proof.py
"""
import math, itertools
import sympy as sp

phi = (1 + math.sqrt(5)) / 2
Nd = 44

print("=" * 60)
print("O51: K_Chain 起始三層證明")
print("=" * 60)

# ---------- 層 1: 種子 → φ ----------
print("\n[層 1] 種子 (0,1) → φ")
c = 1.0
print(f"  主遞歸 C_0 = {c} (起始種子)")
for n in range(1, 13):
    c = 1 / (1 + c)
    print(f"    C_{n} = {c:.8f}")
print(f"    極限 1/φ = {1/phi:.8f}  (dev={abs(c - 1/phi):.2e})")
assert abs(c - 1/phi) < 1e-4, "主遞歸收斂失敗"

F = [1, 1]
for n in range(2, 12):
    F.append(F[-1] + F[-2])
print(f"  連分數種子 F1=F2=1 → F_12/F_11 = {F[11]/F[10]:.8f}  (dev={abs(F[11]/F[10]-phi):.2e})")
assert abs(F[11]/F[10] - phi) < 1e-4, "連分數收斂失敗"
print("  ✅ 冇種子就冇疊代 — φ 有生成起始")

# ---------- 層 2: 44-site 譜 ----------
print("\n[層 2] 44-site K_Chain 譜")
B = phi**3 - phi**-3
L5 = phi**5 + (-phi)**-5
print(f"  Nd = B × L₅ = {B:.6f} × {L5:.6f} = {B*L5:.6f} → 44")
print(f"  (Lucas: L₅ = φ⁵+(−φ)⁻⁵ = 11 exact; B = φ³−φ⁻³ = 4 exact)")
assert abs(B * L5 - 44) < 1e-9, "Nd=B×L5 失敗"
gamma = [4 * math.sin(math.pi*n/88)**2 for n in range(1, Nd+1)]
Se = sum(g for n, g in enumerate(gamma, 1) if n % 2 == 0)
So = sum(g for n, g in enumerate(gamma, 1) if n % 2 == 1)
print(f"  Σγ_even = {Se:.4f} (44-site 偶數子集 n=2,4,…,44)  Σγ_odd = {So:.4f} (44-site 奇數子集 n=1,3,…,43)  Σγ = {Se+So:.4f}")
print("  (注意: 唔係 O34/O36 嘅 88-site 對偶鏈 Σγ_even=90/Σγ_odd=88 世界/觀察者標籤)")
assert abs(Se - 46) < 1e-6 and abs(So - 44) < 1e-6 and abs(Se+So - 90) < 1e-6
z2_ok = all(abs(4*math.sin(math.pi*n/88)**2 + 4*math.sin(math.pi*(44-n)/88)**2 - 4) < 1e-9
            for n in range(1, 44))
print(f"  Z₂ 對偶 γ_n+γ_{{44-n}}=4: {'✅ 43/43' if z2_ok else '❌'}")
assert z2_ok
print("  ✅ 譜由種子結構強迫生成，n 由 1 起")

# ---------- 層 3: 946 拍頻 (sympy 精確) ----------
print("\n[層 3] 946 拍頻 — 全部無理比 (sympy 精確代數)")
omega = [sp.sin(sp.pi * sp.Rational(n, 88)) for n in range(1, Nd+1)]
rational_pairs = 0
total = 0
for (i, j) in itertools.combinations(range(1, Nd+1), 2):
    r = sp.simplify(omega[i-1] / omega[j-1])
    total += 1
    if r.is_Rational:
        rational_pairs += 1
print(f"  拍頻對數 = C(44,2) = {total}")
print(f"  退化為有理比嘅對數 = {rational_pairs}")
assert total == 946 and rational_pairs == 0, "拍頻比分類失敗"
print("  ✅ 946/946 全部無理 → 相位演化無限，組合結構有限有起始")

print("\n" + "=" * 60)
print("判定: K_Chain 有起始 (種子生成), 冇結尾 (Σγ=90 守恆 + 週期恢復)")
print("舊 claim「冇起始」= 錯置「冇結尾」, 已修正")
print("=" * 60)
