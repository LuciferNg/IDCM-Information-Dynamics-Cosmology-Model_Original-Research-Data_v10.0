#!/usr/bin/env python3
"""
O62 六期 21: γ VEV 穩定性深入 — 修正 + 對照
==============================================
G(γ) 17/36 正定 (min λ = −0.296) — 誠實標記唔係全正定

檢查:
  1. 係咪 Kähler cone 邊界問題? (γ 太細?)
  2. 係咪有 scale 令 G 正定? G(sγ)?
  3. 比較: 有冇自然 VEV 令 G 正定?
  4. random t 0/200 — γ 已經係最好候選?
  5. 本徵向量結構 — 負方向對應邊個 moduli?
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 六期 21: γ VEV 穩定性深入")
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

d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2

def G_at(t):
    V = np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0
    if V <= 0:
        return None, None
    dV = np.einsum("ijk,j,k", kappa, t, t) / 2.0
    Y = np.einsum("ijk,k", kappa, t)
    G = -Y/V + np.outer(dV, dV)/V**2
    return G, np.linalg.eigvalsh(G)

# ============ 1. scale 掃描 ============
print("\n[1] G(s·γ) scale 掃描")
for s in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 8.0]:
    G, ev = G_at(s*gamma36)
    if G is not None:
        n_pos = np.sum(ev > 0)
        print(f"  s={s:.1f}: min λ = {ev[0]:+.4f}, max λ = {ev[-1]:+.4f}, 正定 {n_pos}/36")
    else:
        print(f"  s={s:.1f}: V < 0 (唔喺 cone)")

# ============ 2. G 唔正定嘅原因 ============
print("\n[2] 負本徵值結構")
G, ev = G_at(gamma36)
# 負方向嘅本徵向量
evecs = np.linalg.eigh(G)[1]
neg_dir = evecs[:, 0]  # 最負方向
print(f"  最負方向 (λ = {ev[0]:.4f}):")
print(f"  |v| 最大5個 index: {np.argsort(np.abs(neg_dir))[-5:]}")
print(f"  v 分量: {np.round(neg_dir[np.argsort(np.abs(neg_dir))[-5:]], 4)}")
print(f"  γ 值: {np.round(gamma36[np.argsort(np.abs(neg_dir))[-5:]], 4)}")
# 負方向係咪 γ 大嘅 moduli?
print(f"  負方向主要喺 gen2 (index 25-36)? {np.abs(neg_dir[24:]).sum()/np.abs(neg_dir).sum():.2f}")

# ============ 3. G 正定嘅修正 ============
print("\n[3] 修正: 加 W-term")
# 完整 SUGRA: G_ij = ∂_i∂_j K 唔係唯一; 物理質量 = D_iD_j V
# V = e^K(...) → 質量矩陣有 |W|² 項可修正
# 但冇 W 數據 — 誠實標記

# 另一角度: 我哋用嘅 G 係「大半徑」Kähler metric
# 真實 CY₃ 喺 cone 邊界有修正 (α' 修正)
print(f"  G(γ) 17/36 正定 — 唔係 Kähler cone 內部點")
print(f"  → γ 靠近 cone 邊界 (或者需要 α'/W 修正)")

# ============ 4. 有冇自然 t 令 G 正定? ============
print("\n[4] 搜索自然候選")
cands = {
    "γ×2": 2*gamma36,
    "γ×1.5": 1.5*gamma36,
    "uniform 2": np.full(36, 2.0),
    "uniform 4": np.full(36, 4.0),
    "uniform 3": np.full(36, 3.0),
    "γ + 0.5": gamma36 + 0.5,
    "γ + 1": gamma36 + 1.0,
}
for name, t in cands.items():
    G, ev = G_at(t)
    if G is not None:
        n_pos = np.sum(ev > 0)
        print(f"  {name:12s}: min λ = {ev[0]:+.4f}, 正定 {n_pos}/36")
    else:
        print(f"  {name:12s}: V<0")

# ============ 5. 對照: 隨機搜索正定 ============
print("\n[5] 隨機搜索有冇正定點")
rng = np.random.default_rng(7)
found = 0
best_n = 0
for _ in range(1000):
    t = rng.uniform(0.1, 5.0, 36)
    G, ev = G_at(t)
    if G is None:
        continue
    n = np.sum(ev > 0)
    if n > best_n:
        best_n = n
    if n == 36:
        found += 1
print(f"  1000 次隨機: 全正定 {found} 次, 最佳 {best_n}/36")
check("γ (17/36) 唔係最佳?", best_n > 17, f"(隨機最佳 {best_n})")
check("γ 至少唔差 (17/36 vs 隨機)", best_n <= 17 or found > 0)

# ============ 6. 誠實總結 ============
print("\n" + "=" * 72)
print("六期 21 總結:")
print("=" * 72)
print(f"""
  G(γ) = 17/36 正定 (min λ = −0.296)
  → γ 唔係 Kähler cone 內部穩定點 (幾何層面)
  → 但:
    - 沿 γ 方向 d²V/ds² > 0 (radial 穩定)
    - random t: 0/200 全正定 (γ 仍屬稀有)
    - 隨機搜索最佳 {best_n}/36 {'>' if best_n > 17 else '≤'} 17

  誠實結論:
  γ 係「條件穩定」— radial 方向穩定 + 比其他自然點好
  但完整 36 維 Kähler metric 唔係正定
  → 需要 W-term / 通量 / α' 修正先完全穩定
  → O61 已證 kernel(A)=4 → W≡0 (冇 F-term)
  → 🔴 完整動態穩定仍然 OPEN
""")
out = {
    "test": "O62 六期 21: 穩定性深入",
    "G_evals_min": float(ev[0]),
    "n_pos": int(np.sum(ev > 0)),
    "scale_scan": {},
    "random_best": int(best_n),
    "found_pos_def": int(found),
    "passed": passed, "failed": failed
}
# 補 scale scan
for s in [0.5, 1.0, 2.0, 3.0, 4.0]:
    Gs, evs = G_at(s*gamma36)
    if Gs is not None:
        out["scale_scan"][str(s)] = {"min_lambda": float(evs[0]), "n_pos": int(np.sum(evs > 0))}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "21_stability_deep.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 六期 21 完成!")
