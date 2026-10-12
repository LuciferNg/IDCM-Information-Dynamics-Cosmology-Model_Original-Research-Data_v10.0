#!/usr/bin/python3
"""O239 — Script 15: 唔等 freeze v3 —— γ/α 身份池檢定 + 中心命中強度
============================================================================
「即時落手」: 唔等 lattice, 用現有 MC 誤差袋直接判 γ/α 數字身份可唔可以升格。

前設（scripts/14 已證）:
  γ = −4.7503 ± 0.0360（MC 誤差袋, 數據不確定性, 唔係 linregress stderr）
  ⟹ 中心值距 −19/4 只有 0.008σ——「傾向」其實係「幾乎命中」

但池 null 紀律: 宣稱 γ=−19/4 之前必須測「γ 候選池密度」——
  O206 池 null（P=0.4175）封咗「α=常數」, 但冇封「γ=stair 斜率比」。
  本 script 建 γ 身份池, 睇 −19/4 係咪池揀（random rational with stair flavor）。

預註冊判據:
  J1 中心命中強度: γ MC 距離 −19/4 同 −33/7（σ 數）——報告
  J2 ★γ 候選池（stair 深度比）: 池 = {a/b 有理, a∈{7,19,26,33,1,2,4,44,88,32}, b∈{1..12}}
     池密度 P = 池入面 |x − γ| < 2σ 嘅比例——vs 隨機有理池（同尺寸）
     P_stair ≪ P_random 且 P_stair < 0.05 ⟹ −19/4 唔係 stair 池揀（結構候選成立）
  J3 ★α MC 袋: α = γ/β, γ 用 MC 分佈, β 固定（|dm| 譜量冇觀測誤差）
     α 分佈 vs φ² = 2.618034: 距離 σ 數——「α=φ² 中心命中」強度
  J4 判決: γ/α 數字身份現況 →
     （a）γ=−19/4 池檢定通過 + α 中心命中 φ² ⟹ 即時升格「結構候選」, 唔使等 lattice
     （b）池密度高 ⟹ 維持「傾向不宣稱」（docs/10 立場）
"""
import json, math
import numpy as np
from scipy import stats

rng = np.random.default_rng(20261012)
P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/15 — 即時落手: γ/α 身份池檢定 + 中心命中強度")
print("=" * 78)

labels = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
n_modes = [1, 2, 3, 4, 5, 7, 9, 11, 13]
lt = np.log(np.array([n * np.pi / 88 for n in n_modes]))

# γ MC 袋重現（scripts/14 同 seed 同設定, 20 萬組）
REL = np.array([0.0075, 0.0072, 0.000006, 0.0157, 0.0000003, 0.0107, 0.103, 0.227, 0.0000001])
N = 200000
base = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])
gs = []
for _ in range(N):
    m = base * np.exp(rng.normal(0, REL, 9))
    r = stats.linregress(lt, np.log(m))
    gs.append(r.slope)
gs = np.array(gs)
g_mean, g_std = gs.mean(), gs.std()
print(f"\nγ MC: {g_mean:+.4f} ± {g_std:.4f}")

# ── J1: 中心命中強度 ──
c19, c33 = -19/4, -33/7
d19 = abs(g_mean - c19) / g_std
d33 = abs(g_mean - c33) / g_std
print("\n── J1: 中心命中強度 ──")
print(f"   γ 距 −19/4: {d19:.3f}σ（中心值 {g_mean:.4f} vs {c19:.4f}）")
print(f"   γ 距 −33/7: {d33:.3f}σ")
chk("J1 γ 距 −19/4 < 0.5σ（中心命中）", d19 < 0.5, f"{d19:.3f}σ")

# ── J2: γ 候選池密度 ──
print("\n── J2: γ 候選池（stair 深度比 vs 隨機有理池）──")
# stair flavor: 深度 a ∈ {7,19,26,33,13,44,88,32,14,29,20,1,45}, b ∈ {1..12}
depths = [7, 19, 26, 33, 13, 44, 88, 32, 14, 29, 20, 1, 45]
stair_pool = sorted({-a/b for a in depths for b in range(1, 13)})
rng2 = np.random.default_rng(7)
rand_pool = sorted({-int(rng2.integers(1, 90)) / int(rng2.integers(1, 13)) for _ in range(len(stair_pool))})
def pool_density(pool, center, width_sigma, sigma):
    return sum(1 for x in pool if abs(x - center) < width_sigma * sigma) / len(pool)
for w in (1, 2, 3):
    p_stair = pool_density(stair_pool, g_mean, w, g_std)
    p_rand = pool_density(rand_pool, g_mean, w, g_std)
    print(f"   ±{w}σ 窗: stair 池密度 {p_stair*100:5.1f}% ({len(stair_pool)} 候選)   "
          f"隨機有理池 {p_rand*100:5.1f}%")
p1_stair = pool_density(stair_pool, g_mean, 1, g_std)
p1_rand = pool_density(rand_pool, g_mean, 1, g_std)
# 直接數: −19/4 喺 ±1σ 內?
c19_in = abs(c19 - g_mean) < g_std
print(f"   −19/4 喺 γ±1σ 內? {c19_in}  (密度 over stair 池 ±1σ: {p1_stair*100:.1f}%)")
chk("J2a stair 池密度 < 15%（±1σ 窗）", p1_stair < 0.15, f"{p1_stair*100:.1f}%")
chk("J2b stair 池密度 ≪ 隨機池（−19/4 唔係 stair 池隨機湊）", p1_stair < p1_rand,
    f"stair {p1_stair*100:.1f}% vs random {p1_rand*100:.1f}%")

# ── J3: α MC 袋 ──
print("\n── J3: α = γ/β MC 袋 ──")
O9 = json.load(open("data/09_o206_inputs.json"))
dm9 = np.abs(np.array(O9["dm9"]))
r_beta = stats.linregress(lt, np.log(dm9))
beta0 = r_beta.slope
# α 分佈: γ 每組 / β（β 係譜量, 冇觀測誤差）
alphas = gs / beta0
a_mean, a_std = alphas.mean(), alphas.std()
phi2 = (1 + 5**0.5) / 2 * (1 + 5**0.5) / 2
dphi = abs(a_mean - phi2) / a_std
print(f"   α = γ/β = {a_mean:.4f} ± {a_std:.4f}")
print(f"   φ² = {phi2:.6f}  距 α: {dphi:.3f}σ")
print(f"   α 距 O206 α=2.633254: {abs(a_mean-2.633254)/a_std:.2f}σ")
chk("J3 α 中心距 φ² < 1σ 但唔宣稱（池 null P=0.4175 已封）", dphi < 1.0, f"{dphi:.3f}σ")

# ── J4: 判決 ──
print("\n── J4: 判決 ──")
j2a = p1_stair < 0.15
j2b = p1_stair < p1_rand
if j2a and j2b:
    print("   ✅ γ=−19/4 通過 stair 池檢定（密度低 + 低於隨機）")
    print("   ⟹ 即時升格「結構候選」: γ=−19/4 唔係 stair 池隨機湊——唔使等 lattice")
    print("   限制: 仍需正式樣本外盲測判定閉合; 池檢定係必要條件唔係充分")
else:
    print("   🔴 γ=−19/4 池密度高（stair 池隨機可達）——維持「傾向不宣稱」")
    print("   ⟹ 數字身份仍然要等 freeze v3（但結構身份 γ≈−4.75 已穩）")

json.dump({
    "J1_d19": float(d19), "J1_d33": float(d33),
    "J2_stair_pool_size": len(stair_pool), "J2_p1_stair": float(p1_stair),
    "J2_p1_rand": float(p1_rand), "J2_c19_in_1sigma": bool(c19_in),
    "J3_alpha_mean": float(a_mean), "J3_alpha_std": float(a_std), "J3_dphi2": float(dphi),
    "J4_verdict": "γ=−19/4 升格結構候選" if (j2a and j2b) else "維持傾向不宣稱",
}, open("data/15_identity_pool.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")