#!/usr/bin/env python3
"""
O57 六期 47: C 態 3-form 代數結構 — 複結構模空間
==================================================
六期 46 誠實結論: C 態同 K 態喺 134-dim 完全正交
  → C⊗K 直接耦合 = 0 (結構上)

但 Gemini 嘅方向可能啱 — 係表示唔啱:
  真正嘅 A_ij(C) 應該嚟自複結構模空間嘅 3-form intersection
  (h²¹=98 維), 唔係 evecs 正交性!

測試:
  1. C 態 CPX 分量 W_C (98×30) — 喺 98-dim 複結構空間
  2. 用 98-dim 嘅「幾何 pairing」: 唔係 Gram, 而係
     weighted overlap 或者 antisymmetric structure
  3. 睇有冇代數零點 (選擇律)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 六期 47: C 態 3-form 結構")
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

# ============ 1. 66 態 ============
print("\n[1] 66 態")
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
evals, evecs = np.linalg.eigh(P @ P.T)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
evecs = evecs[:, idx]
pos = evals > 1e-10
evecs_pos = evecs[:, pos][:, :66]
e_k = np.sum(evecs_pos[:36, :]**2, axis=0)
e_c = np.sum(evecs_pos[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
C_idx = np.where(sector == "C")[0]
K_idx = np.where(sector == "K")[0]
W_C = evecs_pos[36:, C_idx]  # 98×30
print(f"  C: {len(C_idx)}, K: {len(K_idx)}")

# ============ 2. 幾何 pairing 測試 ============
print("\n[2] 幾何 pairing (98-dim)")
# 98 = h12 = B×L₅+3L₆ — 有 3×12 + 62 結構?
# 試: block pairing (3 gen × 32?)
# 98 = 2×44 + 10? 或者 98 = 3×32 + 2?
for block in [12, 32, 44, 49]:
    if 98 % block == 0:
        print(f"  98 = {98//block} × {block}")
    else:
        print(f"  98 / {block} = {98/block:.2f}")

# 試用 3-gen block 結構 (98 = 3×32 + 2)
# C 態係咪有 3×10 結構? (30 C 態 = 3 gen × 10)
# 用 e_c 能量排序睇
print("\n  C 態 CPX 能量 (排序):")
e_c_vals = np.sort(e_c[C_idx])[::-1]
print(f"  {e_c_vals}")

# ============ 3. 代數零點測試 ============
print("\n[3] 代數零點 (非 Gram pairing)")
# 方法: 用 98-dim 嘅 alternating form (antisymmetric)
# 或者: 用每個 C 態嘅「符號結構」(sign patterns)
# 方法 A: sign coherence
signs = np.sign(W_C)
sign_sim = (signs.T @ signs) / 98  # 30×30 符號相似度
print(f"  Sign similarity matrix (30×30):")
print(f"    diag: {np.diag(sign_sim)}")
off = sign_sim - np.diag(np.diag(sign_sim))
print(f"    off-diag: min={off.min():.3f}, max={off.max():.3f}")
print(f"    off-diag 零點: {np.sum(np.abs(off) < 0.01)}/{off.size}")

# 方法 B: 稀疏度 (每個 C 態 support 幾大?)
support = np.sum(np.abs(W_C) > 1e-3, axis=0)
print(f"\n  每個 C 態 support (|W|>1e-3): {support}")
print(f"  support 範圍: {support.min()} - {support.max()}")

# 方法 C: 能量權重 pairing
# A_C^w = W_C^T · diag(γ) · W_C, γ = 98 個複結構模嘅「質量權重」
# 用 K_Chain 嘅 γ_n 譜? (44-site)
gamma = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2  # 44 個
# 98-dim 嘅 γ: 重複 2.23 次? 或者用 98 = 44+44+10
gamma98 = np.concatenate([gamma, gamma, gamma[:10]])
print(f"\n  γ98: {gamma98.shape}")
A_Cw = W_C.T @ np.diag(gamma98) @ W_C
ev_w = np.linalg.eigvalsh(A_Cw)
ev_w_sorted = np.sort(ev_w)[::-1]
print(f"  A_C^w 本徵值 (top 15): {ev_w_sorted[:15]}")
print(f"  正: {np.sum(ev_w > 1e-10)}/{len(ev_w)}")
if np.sum(ev_w > 1e-10) > 1:
    posw = ev_w[ev_w > 1e-10]
    print(f"  range: {posw.max()/posw.min():.2e}")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("六期 47 總結:")
print("=" * 72)
print(f"""
  C 態 3-form 結構:
  ─────────────────────────────────
  1. C 態: {len(C_idx)} 個, W_C 98×30
  2. Sign similarity: 睇上面
  3. Support: {support.min()}-{support.max()}
  4. γ-weight pairing: 睇上面

  {'✅ 有結構!' if len(posw) > 1 else '❌ 冇明顯結構'}
""")

results = {
    "test": "O57 六期 47: C 態 3-form",
    "support_range": [int(support.min()), int(support.max())],
    "sign_off_range": [float(off.min()), float(off.max())],
    "gamma_ev": [float(x) for x in ev_w_sorted[:10]],
    "passed": passed, "failed": failed
}
with open("data/47_c3form.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 六期 47 完成!")
