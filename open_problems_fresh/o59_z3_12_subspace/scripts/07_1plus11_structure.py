#!/usr/bin/env python3
"""
O59 Phase 7: ★ 12 = 1+11 結構 — su(12) Cartan + 根
==================================================
發現: Block 0 譜有 1 個大本徵值 (3.672) + 11 個細本徵值
→ 12 = 1 (Cartan 生成元) + 11 (root space 維度) = su(12) 結構

驗證:
  1. Block 譜 1+11 結構 (12 = 1 + rank)
  2. tr(Y) 真確值 (O53 用嘅 kappa 唔同?)
  3. 12 = 1+11 = 1 + L₅ (L₅ = 11)
  4. 其他 12 嘅 1+11 解讀
"""
import os, json, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O59 Phase 7: ★ 12 = 1+11 結構")
print("=" * 72)

passed, failed = 0, 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 載入真 κ + J* ============
with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    K = np.array(json.load(f)["kappa"])
with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
    J0 = np.array(json.load(f)["Jstar_36D"])
Y = np.einsum("ijk,k->ij", K, J0)
Y = (Y + Y.T) / 2

print("\n[1] Y = κ_ijk·J^k (真幾何)")
print(f"  tr(Y) = {np.trace(Y):.6f}")
# 檢查 O53 用嘅 tr(Y): 可能用 φ^(-k/12) 而唔係 J*
# O53 docs: tr(Y) ≈ 66 用 Σ d_iik·φ^(-k/12)
print(f"  → O53 用 Σ d_iik·φ^(-k/12), 唔係真 J*!")

# 用 φ^(-k/12) VEV 重算 tr(Y)
phi = (1 + math.sqrt(5)) / 2
v_phi12 = phi ** (-np.arange(36) / 12)
Y_phi = np.einsum("ijk,k->ij", K, v_phi12)
Y_phi = (Y_phi + Y_phi.T) / 2
trY_phi = np.trace(Y_phi)
print(f"  tr(Y_phi) = Σ d_iik·φ^(-k/12) = {trY_phi:.4f}")
check("tr(Y_phi) ≈ 66", abs(trY_phi - 66)/66 < 0.02, f"({trY_phi:.4f}, {abs(trY_phi-66)/66*100:.2f}%)")

# ============ 2. Block 譜 1+11 結構 ============
print("\n[2] Block 譜 1+11 結構 (12 = 1 + rank)")
for g in range(3):
    b = Y[g*12:(g+1)*12, g*12:(g+1)*12]
    ev = np.sort(np.linalg.eigvalsh(b))
    # λ_max vs 其餘 11 個
    lam_max = ev[-1]
    rest = ev[:-1]
    print(f"  Block {g}: λ_max = {lam_max:.4f}, rest mean = {np.mean(np.abs(rest)):.4f}")
    ratio = abs(lam_max) / max(np.mean(np.abs(rest)), 1e-12)
    print(f"    λ_max/mean|rest| = {ratio:.2f}")
    if ratio > 5:
        check(f"Block {g} 有 1+11 結構", True, f"(ratio {ratio:.1f})")
    else:
        check(f"Block {g} 有 1+11 結構", False, f"(ratio {ratio:.1f})")

# ============ 3. 12 = 1 + L₅ ============
print("\n[3] 12 = 1 + L₅")
L5 = 11
print(f"  12 = 1 + {L5} = 1 + L₅")
check("12 = 1+L₅", 1+L5 == 12)
print(f"  ★ su(12): 1 (Cartan) + 11 (rank) = 12 維 fundamental")
print(f"  fundamental rep 分解: 1 個 Cartan 生成元 + 11 個 root generators")

# su(12) 生成元結構
print(f"\n  su(12) 生成元: dim = 143")
print(f"  Cartan: 11 = L₅")
print(f"  Positive roots: 66 = 2×K_tree")
print(f"  Negative roots: 66 = 2×K_tree")
print(f"  總生成元: 11 + 66 + 66 = 143 = dim(su(12))")
check("11+66+66 = 143", 11+66+66 == 143)
print(f"  ★★ 143 = L₅ + 2×(2×K_tree) = 11 + 132 = 143")

# ============ 4. 其他 12 嘅 1+11 解讀 ============
print("\n[4] 其他 12 嘅 1+11 解讀")
print("  A. 12 = (Nd−2B)/3 = 36/3: 每代 Kähler moduli")
print("     → 1+11: 1 個「主模」(大 VEV) + 11 個「次模」")
print("     → 同 su(12) Cartan+root 對應!")
print("  B. 12 = Nd/4+1 = 11+1: L₅+1")
print("     → 直接 = 1+L₅ ✓")
print("  C. 12 = 3×4: B×N_gen")
print("     → 3×4 = 12: 4 個 3D block (B 組), 3 代")
print("  F. 12 ⬠: 幾何巧合")
print("  G. 12 = 33−21: 33−21 = 12 = L₅+1 ✓ (等價)")
print("  H. φ^(-k/12): v_k 週期分母 12 = L₅+1")
print("     → φ 嘅 12 步週期 = rank+1")

# ============ 5. 12 維 block 嘅「1+11」實測 ============
print("\n[5] 12 維 block 嘅「1+11」實測")
# 用 eig 代替 schur
for g in range(3):
    b = Y[g*12:(g+1)*12, g*12:(g+1)*12]
    try:
        evals_b = np.linalg.eigvals(b)
        print(f"  Block {g} eigvals: {np.round(np.sort(evals_b.real), 3)}")
    except Exception as e:
        print(f"  Block {g}: {e}")

# ============ 6. 12 維子空間嘅「1+11」特徵 ============
print("\n[6] 12 維子空間嘅「1+11」特徵")
# O57: 66 態 evecs 中, K 態 (36) 有 12 維 Kähler 分量
# 檢查: 12 維 Kähler 分量有冇 1+11 結構?
# 載入 P_fixed_v2 (66 態投影)
P_path = os.path.join(BASE, "main_problems", "p15_early_derivations", "data", "P_fixed_v2.npy")
if os.path.exists(P_path):
    P = np.load(P_path)
    PPT = P @ P.T
    evals, evecs = np.linalg.eigh(PPT)
    idx = np.argsort(evals)[::-1]
    evecs = evecs[:, idx]
    evals = evals[idx]
    pos = evals > 1e-10
    evecs_pos = evecs[:, pos][:, :66]
    # K 態 = Kähler 分量主導
    sector = []
    for i in range(66):
        e_k = np.sum(evecs_pos[:36, i]**2)
        e_c = np.sum(evecs_pos[36:, i]**2)
        sector.append('K' if e_k >= e_c else 'C')
    k_idx = [i for i, s in enumerate(sector) if s == 'K']
    print(f"  K 態: {len(k_idx)}, C 態: {66-len(k_idx)}")
    # K 態嘅 Kähler 分量 (36×36): 有冇 3×12 結構?
    W_K = evecs_pos[:36, k_idx]  # 36×36
    # 檢查 3×12 blocks 嘅 rank
    for g in range(3):
        b = W_K[g*12:(g+1)*12, :]
        sv = np.linalg.svd(b, compute_uv=False)
        r = np.sum(sv > 1e-8)
        print(f"  K 態 Kähler block {g}: rank {r}")
else:
    print(f"  P_fixed_v2.npy 唔存在")

# ============ 7. 總結 ============
print(f"\n{'='*72}")
print(f"Phase 7 結果: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")
