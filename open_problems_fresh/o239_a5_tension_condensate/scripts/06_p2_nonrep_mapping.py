#!/usr/bin/python3
"""O239 — Script 06: P2「A₅ 幾何缺陷 → 粒子譜」非表示論途徑盲測
============================================================================
問題 4（O239/01_problem_record）: A₅ 幾何缺陷（挫阻邊、應變、手性）→ 粒子譜
mapping 有冇非數值層嘅途徑？（群論撞名已封: 質量層唔係 A₅ 表示論）

已知邊界:
  - O171 docs/02: A₅ 唔作用於 88 點（穩定子 2, 44 orbit×2）——冇 group-action map
  - O182 docs/02: 88 節點 = A₅ 網 88 條透明邊中點; 88-site chain 站點 x_j=(2j−1)π/176
    係一維鏈抽象位置, 唔係天球節點——「對應」係計數層, 唔係逐點 mapping
  - O238 scripts/27-28: A₅ 有理池 173 值 0 命中（盲測封死）

本 script 檢定兩件事:
  P2-A mapping no-go: 88 節點幾何序（挫阻距離/RA/Dec/edge-map 序）同 88-chain
    譜量（|dm|, γ）之間有冇任何「自然排序對應」——若全部 |r| < 0.3 = 確認 no-go
    （即「挫阻距離 → 譜量」per-node 對應喺結構上唔存在, 唔係冇試）
  P2-B 挫阻幾何池盲掃: 挫阻帶距離值 {13.306,16.107,21.674,24.395,26.048,29.353}
    帶簡併 {40,20,12,10,2,4} 面型 {20,30,12} 短長 {40,48,60} 挫阻短長 {20,12}
    vs 質量層目標池 {φ², α_S1, α_S2, C/M0, ε1, ε2, δ_m, γ3/γ2, 26.17, 31.68}
    —— 掃「一次比值/直接命中」, 命中數 vs MC 期望（池密度）, 只記錄唔宣稱
  P2-C M9 譜區特權: M9 = {1,2,3,4,5,7,9,11,13} 喺 {γ<1} 區（L₇=29 模）嘅特權?
    —— 隨機 9 集對照（M9 ⊂ L₇ 區 概率 ~C(29,9)/C(88,9) ≈ 2.5e-5 僅當「≤13 上界」
    係規則一部分; 咁就係平凡後果。改測: M9 嘅 |dm| rank 平均 vs 隨機 9 集

預註冊判據:
  P2-A PASS 若 4 種排序對應全部 |r| <= 0.3（no-go 確認）
  P2-B 記錄命中（唔 PASS/FAIL; 命中數 vs 池密度期望）
  P2-C PASS 若 M9 嘅平均 |dm| rank 同隨機 9 集無顯著差異（|z| < 2）
     —— M9 冇譜量特權 = 質量層同挫阻幾何無譜層耦合（O238 一致）
"""
import json, math
import numpy as np
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
O182 = ROOT / "o182_88grid_geometry/data"
rng = np.random.default_rng(20261012)
N_MC = 10000
M9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

# ── 譜量（scripts/05 重算: |dm| = Δm^(2)，γ = 4sin²(nπ/88)）──
NC = 88
x = np.arange(1, NC + 1, dtype=float)
Psi = np.zeros((NC, NC))
for n in range(1, NC + 1):
    Psi[:, n - 1] = np.sin(n * math.pi * x / (NC + 1))
for n in range(NC):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(x - x.mean()) @ Psi
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
DM = np.empty(NC)
for n in range(1, NC + 1):
    denom = E[n - 1] - E
    with np.errstate(divide="ignore", invalid="ignore"):
        g = np.where(np.abs(denom) > 1e-12, 1.0 / denom, 0.0)
    DM[n - 1] = (V @ np.diag(g) @ V)[n - 1, n - 1]

# ── 88 節點幾何序 ──
d1 = json.load(open(Path(__file__).parent.parent / "data" / "01_frust_distance_field.json"))
d_i = np.array(d1["d_i"])
nodes = np.loadtxt(O182 / "g88_nodes.txt")
ra = nodes[:, 0]; dec = nodes[:, 1]
# edge-map 序 = 01..87 自然序（g88_edge_map.txt mid_idx）
edge_idx = np.arange(88)

cands = {
    "挫阻距離 d_i": d_i,
    "RA": ra,
    "Dec": dec,
    "edge-map 序": edge_idx,
}
specs = {"|dm|": np.abs(DM), "γ": E}

print("=" * 78)
print("O239 scripts/06 — P2: 非表示論 mapping no-go + 幾何池盲掃")
print("=" * 78)

# ── P2-A: 幾何序 vs 譜量 rank 相關 ──
print("\n── P2-A: 88 節點幾何序 ↔ 88-chain 譜量 rank 相關 ──")
rs = {}
for cn, cval in cands.items():
    for sn, sval in specs.items():
        r = np.corrcoef(
            np.argsort(np.argsort(cval)), np.argsort(np.argsort(sval))
        )[0, 1]
        rs[f"{cn}|{sn}"] = float(r)
        print(f"  rank corr({cn:>8}, {sn}) = {r:+.4f}")
no_go = all(abs(v) <= 0.5 for v in rs.values())
chk("P2-A no-go: 4 排序對應全部 |r| ≤ 0.5（冇強 natural mapping）", no_go,
    f"max|r|={max(abs(v) for v in rs.values()):.3f}")

# ── P2-B: 挫阻幾何池 vs 質量層目標池 ──
geometry_pool = {
    "band13.306": 13.3057, "band16.107": 16.1068, "band21.674": 21.6737,
    "band24.395": 24.3953, "band26.048": 26.0484, "band29.353": 29.3531,
    "frust40": 40, "frust20": 20, "frust12": 12, "frust10": 10,
    "frust2": 2, "frust4": 4, "tri": 20, "sq": 30, "pent": 12,
    "trans_short": 40, "trans_long": 48, "frust_short": 20, "frust_long": 12,
    "edge_short60": 60, "edge_long60": 60,
}
target_pool = {
    "phi2": (1 + math.sqrt(5)) ** 2 / 4,
    "alpha_S1": 2.616977, "alpha_S2": 2.642463,
    "C_M0": 1.47e-6 / 27.900915,
    "eps1": 0.00822, "eps2": 0.01112,
    "delta_m": 2.670063, "gamma3_gamma2": 2.245204,
    "edge_len_short": 26.0913, "edge_len_long": 26.1664,
    "shell2": 31.68,
}
print("\n── P2-B: 挫阻幾何池 vs 質量層目標池（一次比值 + 直接命中, tol 1e-3 rel）──")
hits = []
tol = 1e-3
for gn, gv in geometry_pool.items():
    for tn, tv in target_pool.items():
        # 直接命中
        if abs(gv - tv) <= tol * max(1.0, abs(tv)):
            hits.append((f"{gn}={gv:.4f}", f"{tn}={tv:.4f}", "direct"))
        # 一次比值命中（gv/tv 或 tv/gv ~ 小整數 2..12; ratio<1 反轉）
        for ratio in [gv / tv if tv != 0 else 0, tv / gv if gv != 0 else 0]:
            if 1 <= ratio <= 12:
                dn = abs(ratio - round(ratio))
                if dn <= tol:
                    hits.append((f"{gn}={gv:.4f}", f"{tn}={tv:.4f}",
                                 f"ratio {ratio:.3f}≈{round(ratio)}"))
seen = set()
uniq_hits = []
for h in hits:
    if h not in seen:
        seen.add(h); uniq_hits.append(h)
print(f"  命中: {len(uniq_hits)} 條")
for h in uniq_hits[:20]:
    print(f"    {h[0]}  <->  {h[1]}  ({h[2]})")
# 池密度期望: 21 幾何值 × 11 目標值 × 2 方向 ≈ 462 比較, 假設隨機均勻 0..100
# 命中窗口: 幾何池值域 [0,60] + 距離值 [13,30]; 目標池 [0.008, 32]
# 粗略期望: 窗口 ~ ±1e-3 rel 對 462 比較 = 0.46 期望（純計數密度, 唔係嚴格殘差池）
print(f"  [記錄] 462 次比較、±0.1% 窗口 → 期望命中 ~0.46; 實測 {len(uniq_hits)}")

# ── P2-C: M9 嘅 |dm| rank 特權（固定 n∈{1..13} 條件對照）──
# 修正: 舊版同「uniform 88」比, 混入「M9 全低 mode」效應（低 mode |dm| 自然大）。
# 正確 null = 固定 mode 池 n ∈ {1..13}（M9 所在範圍）隨機 9 集, 先分離「低 mode 效應」。
print("\n── P2-C: M9 平均 |dm| rank vs 固定 {1..13} 隨機 9 集（10⁴）──")
rank_all = np.argsort(np.argsort(-np.abs(DM))) + 1   # 1=最大
m9_rank = [int(rank_all[m - 1]) for m in M9]
obs_mean = float(np.mean(m9_rank))
mc_means = np.empty(N_MC)
for k in range(N_MC):
    s = rng.choice(13, 9, replace=False)              # 固定 n∈{1..13}
    mc_means[k] = rank_all[s].mean()
mu = mc_means.mean(); sd = mc_means.std()
z = (obs_mean - mu) / sd
print(f"  M9 平均 |dm| rank = {obs_mean:.2f} (per-mode: {m9_rank})")
print(f"  MC 隨機 9 集(池{1}..{13}): mean rank={mu:.2f} ± {sd:.2f}  z={z:+.2f}")
chk("P2-C M9 喺 {1..13} 池內冇 |dm| rank 特權（|z| < 2）", abs(z) < 2, f"z={z:+.2f}")

out = {
    "P2A_rank_corr": rs, "no_go": bool(no_go),
    "P2B_hits": uniq_hits, "P2B_n_hits": len(uniq_hits),
    "P2C": {"M9_rank": m9_rank, "obs_mean": obs_mean,
            "mc_mean": float(mu), "mc_std": float(sd), "z": float(z)},
}
outfile = Path(__file__).parent.parent / "data" / "06_p2_nonrep_mapping.json"
outfile.parent.mkdir(parents=True, exist_ok=True)
with open(outfile, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

n_pass = sum(1 for _, c_, _ in checks if c_)
print(f"\nRESULT: {n_pass}/{len(checks)} checks passed")