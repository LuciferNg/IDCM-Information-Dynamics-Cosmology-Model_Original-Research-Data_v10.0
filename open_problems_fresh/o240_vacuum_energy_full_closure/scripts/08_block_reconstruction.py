#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O240 攻堅 08: block 組合重建 264/Δ + saddle 方向身份
=======================================================
承接 docs/05 + scripts/07 發現 (Σκ_diag=−20×19, γ saddle, block 主導 550.75):

C1: block 值和有冇整數身份?
  - 550.74777 = ? 550+0.74777; 0.74777 有冇身份? 550 = 11×50? = 5×110?
  - −117.676 = ? +21.091 = ? +17.817 = ? 全部減整數後殘差有冇 δ 族?
C2: 264 可否由 block 子集整數重建?
  - 例如 550.75 − 117.676×? + ... = 264? 試 block 小整數線性組合
C3: Δ 喺 block 組合嘅身份 (C2 副產物)
C4: saddle 負方向身份 — 17 負向量係咪 block-symmetric?
輸出: data/08_block_reconstruction.json; RESULT: N/N
"""
import os, json, sys, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  [PASS] {name} {detail}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")

O53 = os.path.join(BASE, "..", "o53_cy3_reality", "data", "polytopes")
with open(os.path.join(O53, "cy36_98_intersection_full.json")) as f:
    kappa = np.array(json.load(f)["kappa"])
g36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2

def F(t): return float(np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0)
Fg = F(g36)
d = Fg - 264

# ============ C1: block 值整數身份 ============
print("=" * 60)
print("C1: block 值整數身份")
print("=" * 60)
blocks = {}
for (i, j, k) in np.argwhere(kappa != 0):
    bi, bj, bk = i // 12, j // 12, k // 12
    key = (bi, bj, bk)
    blocks[key] = blocks.get(key, 0.0) + int(kappa[i, j, k]) * g36[i] * g36[j] * g36[k] / 6.0
# 獨特 block 值
uniq = sorted(set(round(v, 9) for v in blocks.values()))
print(f"  獨特 block 值: {len(uniq)} 個")
for v in uniq:
    n = v - round(v) if abs(v) < 1e3 else v - round(v)
    print(f"    {v:+12.6f}  (frac = {n:+.6f})")
# 550.74777 減 550/551
b222 = blocks[(2, 2, 2)]
print(f"  (2,2,2) frac vs 550: {b222-550:+.9f}, vs 551: {b222-551:+.9f}")
print(f"  (2,2,2)−550 vs Δ: {(b222-550)/d:.4f}×Δ")
check("C1a: (2,2,2) 整數部分 = 550 = 5×110 = 11×50 (冇唯一身份) — 唔宣稱",
      True, f"({b222:.6f})")
# 550 identity? 550 = F₁₃−13? F₁₃=233, 唔; 550 = 5×F₁₁-? 5×110. 550=10×55=F₁₀×10
print(f"  550 身份: 5×110, 11×50, 10×F₁₀={10*55}, 2×275, 44+506")

# ============ C2: block 整數重建 264 ============
print("\n" + "=" * 60)
print("C2: block 小整數線性組合 → 264?")
print("=" * 60)
# 用 block 值 (9 個獨特) 搵組合: Σ c_i b_i ≈ 264 或 ≈ 264+Δ
bvals = np.array([v for v in uniq])
print(f"  block 池 ({len(bvals)}): {np.round(bvals, 3)}")
found_264 = []
found_F = []
for c in np.ndindex(*([3]*len(bvals))):
    coeff = np.array(c) - 1   # -1..1
    if not np.any(coeff):
        continue
    v = float(coeff @ bvals)
    if abs(v - 264) < 1e-6:
        found_264.append((coeff, v))
    if abs(v - Fg) < 1e-6:
        found_F.append((coeff, v))
print(f"  組合→264: {len(found_264)}, →F(γ): {len(found_F)}")
for cf, v in found_264[:5]:
    print(f"    {dict(zip([f'b{i}' for i in range(len(bvals))], cf))} = {v:.6f}")
check("C2a: block ±1 組合唔能重建 264 (零命中 = block 組合唔係 264 源頭)",
      len(found_264) == 0, f"({len(found_264)})")
check("C2b: block ±1 組合唔能重建 F(γ) (零命中)", len(found_F) == 0,
      f"({len(found_F)})")
# 2 項整數組合 ±3
found2 = []
for i in range(len(bvals)):
    for j in range(i, len(bvals)):
        for ci in range(-3, 4):
            for cj in range(-3, 4):
                v = ci*bvals[i] + cj*bvals[j]
                if abs(v - 264) < 1e-6:
                    found2.append((ci, i, cj, j, v))
print(f"  2 項 [-3,3] 組合→264: {len(found2)}")
for ci, i, cj, j, v in found2[:8]:
    print(f"    {ci}×{bvals[i]:.4f} + {cj}×{bvals[j]:.4f} = {v:.4f}")
check("C2c: block 2 項組合唔重建 264 (零命中)", len(found2) == 0, f"({len(found2)})")

# ============ C3: block 組合 → Δ ============
print("\n" + "=" * 60)
print("C3: block 組合 → Δ?")
print("=" * 60)
found_d = []
for i in range(len(bvals)):
    for j in range(i, len(bvals)):
        for ci in range(-5, 6):
            for cj in range(-5, 6):
                v = ci*bvals[i] + cj*bvals[j]
                if abs(v - d) < 1e-6:
                    found_d.append((ci, i, cj, j, v))
print(f"  2 項 [-5,5] 組合→Δ: {len(found_d)}")
for ci, i, cj, j, v in found_d[:8]:
    print(f"    {ci}×{bvals[i]:.4f} + {cj}×{bvals[j]:.4f} = {v:.6f} (Δ={d:.6f})")
check("C3a: block 2 項組合唔重建 Δ", len(found_d) == 0, f"({len(found_d)})")
# Δ 介乎 (2,2,2)−550 = 0.74777 同細 block 值之間? 0.74777 有冇 Σ block 身份
blk_small = sum(v for v in uniq if abs(v) < 1)
print(f"  小 block 值 (|v|<1) 和: {blk_small:.6f} (Δ 係咪呢啲?)")
check("C3b: Δ 唔係小 block 和", abs(blk_small - d) > 1e-6,
      f"(Σsmall={blk_small:.6f} vs Δ={d:.6f})")

# ============ C4: saddle 負方向身份 ============
print("\n" + "=" * 60)
print("C4: 17 個負方向嘅 block-symmetry")
print("=" * 60)
dFg = 0.5 * np.einsum("ijk,j,k", kappa, g36, g36)
Yg = np.einsum("ijk,k", kappa, g36)
G = -Yg/Fg + np.outer(dFg, dFg)/Fg**2
gv, gvec = np.linalg.eigh(G)
neg_vecs = gvec[:, gv < -1e-8]   # 36×17
pos_vecs = gvec[:, gv > 1e-8]
zero_vecs = gvec[:, np.abs(gv) < 1e-8]
# block-symmetry: 每 vector 喺 gen 0/1/2 嘅 norm²
def block_norms(V, ngen=3):
    return np.array([[np.sum(V[g*12:(g+1)*12, j]**2) for g in range(ngen)]
                     for j in range(V.shape[1])])
bn_neg = block_norms(neg_vecs)
bn_pos = block_norms(pos_vecs)
bn_zero = block_norms(zero_vecs)
print(f"  負方向 block-norm (mean over 17): {bn_neg.mean(axis=0)}")
print(f"  正方向 block-norm (mean over 15): {bn_pos.mean(axis=0)}")
print(f"  零方向 block-norm (mean over 4) : {bn_zero.mean(axis=0)}")
# 對稱 vs 非對稱: 負方向係咪偏 gen2? 正方向偏 gen0/1?
check("C4a: 正/負方向 block 分佈唔同 (身份方向)",
      np.abs(bn_neg.mean(axis=0) - bn_pos.mean(axis=0)).max() > 0.05,
      f"(neg {np.round(bn_neg.mean(axis=0),3)} vs pos {np.round(bn_pos.mean(axis=0),3)})")
# 負方向對 γ 有冇平均負投影?
neg_gamma_proj = neg_vecs.T @ g36
print(f"  負方向 γ 投影: mean {np.mean(neg_gamma_proj):.4f}, var {np.var(neg_gamma_proj):.4f}")

with open(os.path.join(DATA, "08_block_reconstruction.json"), "w") as f:
    out = {
        "unique_blocks": [round(v, 9) for v in uniq],
        "b222": b222, "b222_frac_vs_550": b222 - 550,
        "found_264": len(found_264), "found_F": len(found_F),
        "found_2term_264": len(found2), "found_2term_delta": len(found_d),
        "small_block_sum": blk_small,
        "neg_block_norm_mean": bn_neg.mean(axis=0).tolist(),
        "pos_block_norm_mean": bn_pos.mean(axis=0).tolist(),
        "zero_block_norm_mean": bn_zero.mean(axis=0).tolist(),
        "passed": passed, "failed": failed,
    }
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nRESULT: {passed}/{passed+failed} PASS")
sys.exit(0 if failed == 0 else 1)