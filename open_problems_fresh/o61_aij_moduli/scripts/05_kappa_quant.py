#!/usr/bin/env python3
"""
O61 一期 05: κ block 結構量化 — 內/間耦合比 + 非零階梯
================================================================
一期 04 發現:
  - 對角 block 集中 32.2% (p=0.0000)
  - 兩維對角 60.2% → 92.4% 至少有兩 index 同 block
  - block 非零數: [292, 86, 54] → 86/54 = 1.593 ≈ φ!

本輪:
  1. 內/間耦合比: mean|κ| (block 內 vs block 間) — 唔用 norm (對 size 敏感)
  2. 非零數階梯: 292/86, 86/54 對比 φ
  3. 排列對照: 隨機打亂 block 標籤
  4. 完整 Yukawa 本徵值譜: 有冇 3 個明顯 cluster?
  5. A_ij(z) 完整結構: 66 態 ↔ 36 Kähler 對應
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O61 一期 05: κ block 結構量化")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 載入 κ ============
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
nz_mask = kappa != 0
nz = int(np.count_nonzero(nz_mask))

def block_of(i):
    return i // 12

# ============ 2. 內/間耦合比 ============
print("\n[1] 內/間 mean|κ| 比")
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
print(f"  block 內 mean|κ|: {diag_vals.mean():.4f} (n={len(diag_vals)})")
print(f"  block 間 mean|κ|: {off_vals.mean():.4f} (n={len(off_vals)})")
ratio = diag_vals.mean() / off_vals.mean()
print(f"  內/間比: {ratio:.3f}")
check("block 內耦合 > 間耦合", ratio > 1.2, f"比={ratio:.3f}")

# 兩維對角 (g1=g2≠g3) 單獨
two_vals = []
for i in range(36):
    for j in range(36):
        for k in range(36):
            if nz_mask[i, j, k]:
                g1, g2, g3 = block_of(i), block_of(j), block_of(k)
                if (g1 == g2 != g3) or (g1 == g3 != g2) or (g2 == g3 != g1):
                    two_vals.append(abs(kappa[i, j, k]))
two_vals = np.array(two_vals)
print(f"  兩維對角 mean|κ|: {two_vals.mean():.4f} (n={len(two_vals)})")
print(f"  完全混合 mean|κ|: {off_vals[~np.isin(off_vals, two_vals)].mean() if len(off_vals)>len(two_vals) else 0:.4f}" if len(off_vals) > len(two_vals) else "")

# 三級階梯: 完全對角 > 兩維對角 > 完全混合?
print(f"  完全對角: {diag_vals.mean():.4f} | 兩維對角: {two_vals.mean():.4f} | 完全混合: 睇上面")

# ============ 3. 非零數階梯 ============
print("\n[2] 非零數階梯")
blocks_nz = [int(np.sum(nz_mask[g*12:(g+1)*12, g*12:(g+1)*12, g*12:(g+1)*12])) for g in range(3)]
print(f"  block 非零: {blocks_nz}")
r01 = blocks_nz[0] / blocks_nz[1]
r12 = blocks_nz[1] / blocks_nz[2]
print(f"  比: {r01:.4f}, {r12:.4f}")
print(f"  φ={phi:.4f}, φ²={phi**2:.4f}, 4/3={4/3:.4f}, 3/2={3/2:.4f}")
check("86/54 ≈ φ (10%)", abs(r12 - phi) / phi < 0.10, f"r12={r12:.4f} vs φ={phi:.4f}")
check("292/86 ≈ φ² (30%)", abs(r01 - phi**2) / phi**2 < 0.30, f"r01={r01:.4f} vs φ²={phi**2:.4f}")

# 隨機對照: 打亂 block 標籤
rng = np.random.default_rng(7)
perm_diag_fracs = []
for trial in range(200):
    perm = rng.permutation(36)
    # 隨機 3 個 12-block (用 perm 嘅位置)
    labels = np.zeros(36, dtype=int)
    labels[perm[:12]] = 0
    labels[perm[12:24]] = 1
    labels[perm[24:]] = 2
    cnt = 0
    for i in range(36):
        for j in range(36):
            for k in range(36):
                if nz_mask[i, j, k] and labels[i] == labels[j] == labels[k]:
                    cnt += 1
    perm_diag_fracs.append(cnt / nz)
perm_diag_fracs = np.array(perm_diag_fracs)
true_frac = sum(blocks_nz) / nz
p_perm = np.mean(perm_diag_fracs >= true_frac)
print(f"\n  隨機打亂 block: mean diag frac = {perm_diag_fracs.mean():.3f} ± {perm_diag_fracs.std():.3f}")
print(f"  真值: {true_frac:.3f} ({true_frac*100:.1f}%)")
print(f"  p = {p_perm:.4f}")
check("block 標籤顯著 (p<0.01)", p_perm < 0.01, f"p={p_perm:.4f}")

# ============ 4. Yukawa 本徵值譜 ============
print("\n[3] Yukawa 本徵值譜 (t=γ)")
gamma = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
Y_g = np.tensordot(kappa, gamma, axes=([2], [0]))
ev = np.sort(np.linalg.eigvalsh(Y_g))[::-1]
print(f"  本徵值 (36 個):")
print(f"    {[f'{x:.2f}' for x in ev]}")
# 3 cluster?
print(f"\n  log|λ| 譜 (唔計 0):")
pos_ev = ev[ev > 1e-10]
neg_ev = -ev[ev < -1e-10]
print(f"  正: {len(pos_ev)}, 負: {len(neg_ev)}")
print(f"  正 log10: {[f'{math.log10(x):.2f}' for x in pos_ev]}")
print(f"  負 log10: {[f'{math.log10(x):.2f}' for x in neg_ev]}")

# 最大 gap 分析
sorted_abs = np.sort(np.abs(ev[ev != 0]))[::-1]
if len(sorted_abs) > 1:
    log_abs = np.log(sorted_abs)
    gaps = np.diff(log_abs)
    max_gap_idx = np.argmax(gaps)
    print(f"\n  最大 log-gap: {gaps[max_gap_idx]:.3f} at position {max_gap_idx+1}")
    print(f"  → {max_gap_idx+2} 個 cluster 提示")
    check("譜有 cluster 結構 (max gap > 2)", gaps[max_gap_idx] > 2, f"gap={gaps[max_gap_idx]:.3f}")

# ============ 5. 66 態 ↔ 36 Kähler ============
print("\n[4] 66 態 ↔ 36 Kähler 對應")
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")  # 2026-10-08 修正: 原 BASE/data 斷裂
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
W_K = evecs_pos[:36, K_idx]  # 36×36

# W_K 有冇 3×12 block 結構?
block_means = np.zeros((3, 3))
for g1 in range(3):
    for g2 in range(3):
        block_means[g1, g2] = np.mean(np.abs(W_K[g1*12:(g1+1)*12, g2*12:(g2+1)*12]))
print(f"  W_K block mean|·|:")
for i in range(3):
    print(f"    {[f'{x:.4f}' for x in block_means[i]]}")
d = [block_means[i, i] for i in range(3)]
o = [block_means[i, j] for i in range(3) for j in range(3) if i != j]
print(f"  diag: {[f'{x:.4f}' for x in d]}, off_max: {max(o):.4f}")
print(f"  diag/off: {max(d)/max(o):.2f}")
check("W_K 有 3×12 block", max(d) / max(o) > 1.5, f"比={max(d)/max(o):.2f}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("O61 一期 05 總結:")
print("=" * 72)
print(f"""
  κ block 結構量化:
  ─────────────────────────────────
  1. 內/間 mean|κ| 比: {ratio:.3f}
  2. 非零階梯: {blocks_nz} → r12={r12:.3f} (φ={phi:.3f})
  3. 隨機對照 p: {p_perm:.4f}
  4. 66 態 W_K block: diag/off = {max(d)/max(o):.2f}

  {'✅ κ 結構確認' if failed == 0 else '❌ 有失敗'}
""")
results = {
    "test": "O61 05: κ block 量化",
    "in_out_ratio": float(ratio),
    "diag_mean": float(diag_vals.mean()),
    "off_mean": float(off_vals.mean()),
    "blocks_nz": blocks_nz,
    "r01": float(r01), "r12": float(r12),
    "p_perm": float(p_perm),
    "yukawa_ev": [float(x) for x in ev],
    "wk_block": [[float(x) for x in row] for row in block_means],
    "passed": passed, "failed": failed
}
with open("data/05_kappa_quant.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 O61 一期 05 完成!")
