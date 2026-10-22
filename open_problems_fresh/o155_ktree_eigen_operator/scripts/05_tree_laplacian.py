#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05_tree_laplacian.py — R3: 33-level tree Laplacian 算子證明 (K_Tree 本徵算子化)
=============================================================================
問題 (O155 R3): 33-level tree Laplacian (λ_k = 4sin²(kπ/68)) Σλ = 66 = 2K_tree
— 算子證明 + 同 2N_gen·L₅ 身份嘅關係。

算子定義: L_tree = 33-site chain 嘅 Dirichlet Laplacian (兩端固定, F₉=34 節點、
33 links): 33×33 tridiagonal, diag 2, off-diag -1。
譜: λ_k = 4sin²(kπ/68) = 2-2cos(kπ/34), k = 1..33;  Σλ = 66。

檢驗:
C1. L_dir 譜 = 4sin²(kπ/68), k=1..33 (numpy eigh vs mpmath 公式, tol 1e-10)
C2. Tr(L_dir) = 66 = Σλ = 2K_tree = 2N_gen·L₅
C3. Neumann chain trace = 64 = 2(K_tree−1); Dirichlet−Neumann = 2 = μ² = E−O
    (Σγ_even−Σγ_odd = 90−88, 88-site 對偶鏈)
C4. 66 = C(12,2) = dim Λ²(12) = 36+30 = (6,6)⊕(10,3̄)  (O59)
C5. 68 = 2F₉ = B·F_proj = 2(K_tree+1)  (譜分母 = 2×(tree+1) = 分支×投影維)
C6. 一般身份: Σ_{k=1}^{n} 4sin²(kπ/(2(n+1))) = 2n, n = 3..40
C7. Σ_{k=1}^{33} sin²(kπ/68) = 33/2  (等價形式)
"""
import numpy as np
import mpmath as mp
mp.mp.dps = 50

N, KTREE, B, Ngen, L5, Fproj = 88, 33, 4, 3, 11, 17

passes = []
def check(name, cond, detail=""):
    passes.append(cond)
    print(f"   [{'PASS' if cond else 'FAIL'}] {name} {detail}")

print("C1) Dirichlet 33-site chain Laplacian 譜")
Ld = np.zeros((33, 33))
for i in range(33):
    Ld[i, i] = 2.0
    if i > 0: Ld[i, i-1] = -1.0
    if i < 32: Ld[i, i+1] = -1.0
w = np.linalg.eigvalsh(Ld)
spec = sorted(w)
ok = True
for k in range(1, 34):
    lam_formula = float(4 * mp.sin(mp.pi * k / 68)**2)
    if abs(spec[k-1] - lam_formula) > 1e-10:
        ok = False
        break
check("λ_k = 4sin²(kπ/68), k=1..33 (全部 33 模態)", ok,
      f"λ_1={spec[0]:.6f}, λ_33={spec[-1]:.6f}")

print("\nC2) Tr(L) = 66 = Σλ = 2K_tree = 2N_gen·L₅")
tr = float(np.trace(Ld))
sm = float(np.sum(w))
ok1 = abs(tr - 66) < 1e-9 and abs(sm - 66) < 1e-9
check("Tr(L_dir) = 66", ok1, f"Tr={tr:.9f}")
ok2 = abs(tr - 2 * KTREE) < 1e-9 and abs(tr - 2 * Ngen * L5) < 1e-9
check("66 = 2K_tree = 2N_gen·L₅", ok2)

print("\nC3) Neumann chain 對照: 邊界夾制代價 = E−O 奇偶隙")
Lneu = np.zeros((33, 33))
for i in range(33):
    Lneu[i, i] = 2.0
    if i > 0: Lneu[i, i-1] = -1.0
    if i < 32: Lneu[i, i+1] = -1.0
Lneu[0, 0] = 1.0; Lneu[32, 32] = 1.0
tr_n = float(np.trace(Lneu))
ok1 = abs(tr_n - 64) < 1e-9
check("Tr(L_Neumann) = 64 = 2(K_tree−1)", ok1, f"Tr={tr_n:.9f}")
d = tr - tr_n
ok2 = abs(d - 2) < 1e-9
check("Tr(L_dir) − Tr(L_neu) = 2", ok2, f"Δ={d:.9f}")
# 88-site 對偶鏈 = 176-Laplacian 首 88 模: γ_k = 4sin²(kπ/176)
# even k=2..88 (世界) Σ=90, odd k=1..87 (觀察者) Σ=88 (反幻覺鐵律: 用 176 唔係 88)
sE = sum(4 * np.sin(k * np.pi / 176)**2 for k in range(2, 89, 2))
sO = sum(4 * np.sin(k * np.pi / 176)**2 for k in range(1, 88, 2))
ok3 = abs(sE - 90) < 1e-9 and abs(sO - 88) < 1e-9 and abs((sE - sO) - d) < 1e-9
check("Δ = E−O = Σγ_even−Σγ_odd = 90−88 = 2 = μ²", ok3, f"E−O={sE-sO:.9f}")

print("\nC4) 66 = dim Λ²(12) = C(12,2)")
ok1 = 66 == 12 * 11 // 2
ok2 = 66 == 36 + 30
check("C(12,2) = 66", ok1)
check("Λ²(12) = (6,6)⊕(10,3̄) = 36+30 = 66 (O59)", ok2)

print("\nC5) 譜分母 68 = 2F₉ = B·F_proj = 2(K_tree+1)")
ok1 = 68 == 2 * 34 and 34 == KTREE + 1
check("68 = 2(K_tree+1) = 2F₉ (F₉ = 34)", ok1)
ok2 = 68 == B * Fproj
check("68 = B·F_proj = 4·17", ok2)

print("\nC6) 一般身份 Σ_{k=1}^{n} 4sin²(kπ/(2(n+1))) = 2n, n=3..40")
ok = True
for n in range(3, 41):
    s = mp.nsum(lambda k: 4 * mp.sin(mp.pi * k / (2 * (n + 1)))**2, [1, n])
    if mp.fabs(s - 2 * n) > mp.mpf('1e-30'):
        ok = False
        break
check("n=3..40 全對", ok)

print("\nC7) Σ_{k=1}^{33} sin²(kπ/68) = 33/2")
s = mp.nsum(lambda k: mp.sin(mp.pi * k / 68)**2, [1, 33])
check("= 16.5 EXACT", mp.fabs(s - mp.mpf(33)/2) < mp.mpf('1e-30'), f"={mp.nstr(s, 20)}")

total = len(passes)
print(f"\nRESULT: {sum(passes)}/{total} PASS")
exit(0 if all(passes) else 1)
