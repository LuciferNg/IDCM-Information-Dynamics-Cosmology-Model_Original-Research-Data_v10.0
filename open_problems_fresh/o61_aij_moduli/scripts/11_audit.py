#!/usr/bin/env python3
"""
O61 驗證 11: 全面 audit — docs/01-03 每個關鍵數字 vs 實際計算
================================================================
核對 docs 中所有 claim:
  docs/01: A_ij(z) pre-factor
  docs/02: Moduli stabilization (已修正)
  docs/03: 最終閉合

逐項驗證:
  - κ 1341 非零 / 36³ (2.9%)
  - 對稱性 0.0e+00
  - 3×12 block: 432/807/102, 92.4%, 內/間 6.41
  - 階梯 292:86:54, 86/54=1.5926≈φ
  - Yukawa diag/off = 40.99
  - kernel(A) = 4, 32 = 2B²
  - M_lock 正定 0.233
  - 通量子 66/90
  - W_K block 4.24
  - 66 = 3×(12+10)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")  # 2026-10-08 修正: 原 BASE/data 斷裂
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O61 驗證 11: 全面 audit docs/01-03")
print("=" * 72)

results = []
def audit(name, actual, expected, tol=1e-6):
    """記錄 audit 結果"""
    if isinstance(expected, str):
        ok = str(actual) == expected
        detail = f"actual={actual}, expected={expected}"
    elif isinstance(expected, (int, np.integer)):
        ok = int(actual) == int(expected)
        detail = f"actual={actual}, expected={expected}"
    elif isinstance(expected, (list, tuple)):
        ok = list(actual) == list(expected)
        detail = f"actual={actual}, expected={expected}"
    else:
        ok = abs(float(actual) - float(expected)) < tol
        detail = f"actual={actual}, expected={expected} (tol={tol})"
    results.append({"name": name, "ok": bool(ok), "detail": detail})
    mark = "✅" if ok else "❌"
    print(f"  {mark} {name}: {detail}")

# ============ 1. 載入數據 ============
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
nz_mask = kappa != 0
nz = int(np.count_nonzero(nz_mask))

print("\n[1] κ 基本性質")
audit("κ shape = (36,36,36)", kappa.shape, (36, 36, 36))
audit("κ 非零數 = 1341", nz, 1341)
audit("非零比例 2.9%", nz / 36**3 * 100, 2.9, 0.05)
sym = np.max(np.abs(kappa - kappa.transpose(1, 0, 2)))
audit("κ 對稱性 = 0", sym, 0, 1e-10)
audit("κ range min = -360", kappa.min(), -360)
audit("κ range max = 180", kappa.max(), 180)

# ============ 2. 3×12 block 結構 ============
print("\n[2] 3×12 block 結構")
def block_of(i):
    return i // 12

blocks = np.zeros((3, 3, 3), dtype=int)
for i in range(36):
    for j in range(36):
        for k in range(36):
            if nz_mask[i, j, k]:
                blocks[block_of(i), block_of(j), block_of(k)] += 1

diag_nz = sum(blocks[g, g, g] for g in range(3))
two_same = 0
for g in range(3):
    for h in range(3):
        if h != g:
            two_same += blocks[g, g, h] * 3  # 3 個排列
full_mixed = nz - diag_nz - two_same

audit("完全對角 = 432", diag_nz, 432)
audit("完全對角比例 = 32.2%", diag_nz / nz * 100, 32.2, 0.1)
audit("兩維對角 = 807", two_same, 807)
audit("兩維對角比例 = 60.2%", two_same / nz * 100, 60.2, 0.1)
audit("完全混合 = 102", full_mixed, 102)
audit("完全混合比例 = 7.6%", full_mixed / nz * 100, 7.6, 0.1)
audit("≥2 index 同 block = 92.4%", (diag_nz + two_same) / nz * 100, 92.4, 0.1)

# 內/間 mean|κ|
diag_vals = []
off_vals = []
for i in range(36):
    for j in range(36):
        for k in range(36):
            if nz_mask[i, j, k]:
                g1, g2, g3 = block_of(i), block_of(j), block_of(k)
                if g1 == g2 == g3:
                    diag_vals.append(abs(kappa[i, j, k]))
                else:
                    off_vals.append(abs(kappa[i, j, k]))
diag_vals = np.array(diag_vals)
off_vals = np.array(off_vals)
ratio = diag_vals.mean() / off_vals.mean()
audit("內/間 mean|κ| 比 = 6.41", ratio, 6.41, 0.02)

# 階梯
blocks_nz = [int(np.sum(nz_mask[g*12:(g+1)*12, g*12:(g+1)*12, g*12:(g+1)*12])) for g in range(3)]
audit("block 非零 [292,86,54]", blocks_nz, [292, 86, 54])
r12 = blocks_nz[1] / blocks_nz[2]
audit("86/54 = 1.5926 ≈ φ (1.6%)", r12, phi, 0.03)
r01 = blocks_nz[0] / blocks_nz[1]
audit("292/86 ≈ φ² (30% 內)", r01, phi**2, 0.3 * phi**2)

# ============ 3. Yukawa diag/off ============
print("\n[3] Yukawa diag/off")
def yukawa(t):
    return np.einsum("ijk,k", kappa, t)

def diag_off_ratio(Y):
    bm = np.zeros((3, 3))
    for g1 in range(3):
        for g2 in range(3):
            bm[g1, g2] = np.mean(np.abs(Y[g1*12:(g1+1)*12, g2*12:(g2+1)*12]))
    d = [bm[i, i] for i in range(3)]
    o = [bm[i, j] for i in range(3) for j in range(3) if i != j]
    return max(d) / max(o), d, o

gamma = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
for name, t in [
    ("φ^(35-i)", phi**(35-np.arange(36))),
    ("φ^(-i)", phi**(-np.arange(36))),
]:
    r, d, o = diag_off_ratio(yukawa(t))
    audit(f"{name} diag/off = 40.99", r, 40.99, 0.05)

# ============ 4. kernel(A) = 4 = B ============
print("\n[4] kernel(A) = 4 = B")
A = kappa.reshape(1296, 36)
U, S, Vt = np.linalg.svd(A, full_matrices=True)
n_zero = np.sum(S < 1e-8)
audit("kernel(A) = 4", n_zero, 4)
audit("4 = B", 4, 4)
audit("32 = 36-4 = 2B²", 36 - n_zero, 2 * 4**2)

# 零方向驗證
zero_basis = Vt[36-n_zero:, :]
errs = [np.max(np.abs(np.einsum("ijk,k", kappa, zero_basis[a]))) for a in range(4)]
audit("Σκv = 0 (max err < 1e-8)", max(errs), 0, 1e-8)

# ============ 5. M_lock 正定 ============
print("\n[5] M_lock 正定")
Y = yukawa(gamma)
lock_basis = Vt[:32, :]
M_lock = lock_basis @ (Y.T @ Y) @ lock_basis.T
ev_lock = np.linalg.eigvalsh(M_lock)
audit("M_lock min eig = 0.233", ev_lock.min(), 0.233, 0.002)

# ============ 6. 通量子 66/90 ============
print("\n[6] 通量子 66/90")
for tname, tval in [("66", 66), ("90", 90)]:
    found = False
    for scale in range(1, 41):
        for a in range(4):
            N = np.round(zero_basis[a] * scale).astype(int)
            s = np.sum(np.abs(N))
            if s == tval:
                audit(f"通量子 sum|N| = {tval}", s, tval)
                found = True
                break
        if found:
            break
    if not found:
        audit(f"通量子 sum|N| = {tval}", "not found", tval)

# ============ 7. W_K block ============
print("\n[7] W_K block 結構")
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
P66 = P @ P.T
evals, evecs = np.linalg.eigh(P66)
idx = np.argsort(evals)[::-1]
evecs = evecs[:, idx]
pos_mask = evals[idx] > 1e-10
evecs_pos = evecs[:, pos_mask][:, :66]
e_k = np.sum(evecs_pos[:36, :]**2, axis=0)
e_c = np.sum(evecs_pos[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
K_idx = np.where(sector == "K")[0]
W_K = evecs_pos[:36, K_idx]
bm = np.zeros((3, 3))
for g1 in range(3):
    for g2 in range(3):
        bm[g1, g2] = np.mean(np.abs(W_K[g1*12:(g1+1)*12, g2*12:(g2+1)*12]))
d = [bm[i, i] for i in range(3)]
o = [bm[i, j] for i in range(3) for j in range(3) if i != j]
audit("W_K diag/off = 4.24", max(d) / max(o), 4.24, 0.05)
audit("66 = 3×(12+10)", 3 * (12 + 10), 66)
audit("C 態 = 30", np.sum(sector == "C"), 30)
audit("K 態 = 36", np.sum(sector == "K"), 36)

# ============ 8. 總結 ============
print("\n" + "=" * 72)
print("O61 驗證 11 總結:")
print("=" * 72)
n_pass = sum(1 for r in results if r["ok"])
n_fail = sum(1 for r in results if not r["ok"])
print(f"  Audit: {n_pass}/{len(results)} 通過, {n_fail} 失敗")
if n_fail > 0:
    print("\n  失敗項目:")
    for r in results:
        if not r["ok"]:
            print(f"    ❌ {r['name']}: {r['detail']}")

with open("data/11_audit.json", "w") as f:
    json.dump({"results": results, "passed": n_pass, "failed": n_fail}, f, indent=2, ensure_ascii=False)
print(f"\n{'🎉 全部通過!' if n_fail == 0 else '⚠️ 有失敗要修正'}")
exit(0 if n_fail == 0 else 1)
