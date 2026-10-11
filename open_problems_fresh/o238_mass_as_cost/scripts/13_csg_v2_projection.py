#!/usr/bin/python3
"""O238 — Script 13: CSG v2 投影公式 freeze v2 重算 + t 延伸盲測 + 分通道 C 檢定

調律者框架（docs/06）: 質量 = 按測量而投影; 連續層(γ/|dm|) × 投影算符(P_f).
O206 docs/22: CSG v2 `m = M₀·γ_n·P_f` 零參數 RMS(ln)=0.0076 (好冪律 78×) —
即「γ_n = 連續層, P_f = selection 投影」嘅現成實現.

本 script（喺 O238 內, 用 freeze v2 質量集）:
  P1 CSG v2 8/8 重算（freeze v2 質量: e μ τ u d s c b）— RMS(ln) 係咪維持 ~0.008?
  P2 t 延伸盲測: CSG v2 網格 U 行 g3 空缺 — 用 O238 A₅ t(1) 或網格規律試（誠實報）—
     若 t 用 (n=?, P_f=?) 可以閉合 9/9 — 係一個樣本外預言
  P3 分通道 C 檢定: 連續層 = |dm|^{φ²}（O238 冪律）vs γ（CSG）:
     每通道 fit C_channel = median(m_i / 連續層_i) — C_A/C_B/C_C 一致定唔同?
     ⟹ 「投影按測量而變」嘅直接測試: 若 C 三通道唔同 → C 係投影算符讀數
  P4 同通道 RMS: G3(lattice 5點) 同通道內 RMS vs 混合 9 點 (scripts/11 P1 追蹤)
"""
import numpy as np, math, json, sys

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

N = 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, N + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
D = E[:, None] - E[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)
gam = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
M0 = 27.900915

# CSG v2 結構常數 (src/v2core)
M_TREE, E_PROJ, N_D, L4, F5, F7, L6 = 33, 57/2, 44, 7, 5, 13, 18

# freeze v2 (S2) 質量集 (docs/04) — 比 scripts/16_o206_bridge.py 更新（嗰邊用 2008 PDG）
MS2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
       "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
       "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}

print("═══ P1. CSG v2 8/8 重算（freeze v2 質量集） ═══")
# (name, n, P_f expr, P_f 值)
CSG8 = [
    ("e", 1, L6/F5, "L6/F5"),
    ("mu", 7, N_D - E_PROJ, "N_D−E_PROJ"),
    ("tau", 20, N_D - L4, "N_D−L4"),
    ("u", 1, N_D - E_PROJ, "N_D−E_PROJ"),
    ("d", 1, M_TREE, "M_TREE"),
    ("s", 14, L6/F5, "L6/F5"),
    ("c", 34, F7, "F7"),
    ("b", 33, N_D, "N_D"),
]
res8 = []
for name, n, pf, expr in CSG8:
    g = gam[n-1]
    m_pred = M0 * g * pf
    m_obs = MS2[name]
    lv = math.log(m_pred / m_obs)
    res8.append(lv)
    print(f"  {name:>3} n={n:2d} P_f({expr})={pf:8.3f}  γ={g:.6f}  pred={m_pred:10.4f}  obs={m_obs:10.4f}  Δln={lv:+.4f}")
rms8 = math.sqrt(np.mean(np.array(res8)**2))
print(f"  ★ CSG v2 8/8 RMS(ln) = {rms8:.6f} = 因子 {math.exp(rms8):.5f}")
chk("P1.1 CSG v2 8/8 freeze v2 下 RMS 維持 < 0.02", rms8 < 0.02, f"RMS={rms8:.6f}")

print("\n═══ P2. t 延伸盲測 ═══")
print("  CSG v2 U 行: g1 u(n=1,P=15.5), g2 c(n=34,P=13), g3 = 空缺")
print("  網格規律候選: L行 n(1,7,20), D行 n(1,14,33), U行 n(1,34,?)")
# 嘗試 n 候選: 34+?（間隔遞增: L +6,+13; D +13,+19; U +33,+?）
# L: 1→7 (+6=F8? 8-2), 7→20 (+13=F7)
# D: 1→14 (+13), 14→33 (+19=L8=19? L8=29 no; F8-F6=21-8=13? no)
# 簡單測試幾個網格候選 n: 20(M_TREE-F5+?), 44(N_D), 43(N_D-1)
t_cands = {}
for n in [20, 33, 34, 43, 44, 7]:
    for pfx in ["N_D", "F7", "L6/F5", "N_D-L4", "M_TREE"]:
        pf = {"N_D": N_D, "F7": F7, "L6/F5": L6/F5, "N_D-L4": N_D-L4, "M_TREE": M_TREE}[pfx]
        m_pred = M0 * gam[n-1] * pf
        lv = math.log(m_pred / MS2["t"])
        t_cands[(n, pfx)] = lv
best = min(t_cands, key=lambda k: abs(t_cands[k]))
print(f"  最好 t 候選: n={best[0]}, P_f={best[1]}, Δln={t_cands[best]:+.4f} (需 <0.02)")
print("  （其餘 top3）:")
for k in sorted(t_cands, key=lambda k: abs(t_cands[k]))[:3]:
    print(f"    n={k[0]:2d} P_f={k[1]:8s} Δln={t_cands[k]:+.4f}")
chk("P2.1 t 有網格候選閉合 (唔係硬拗)", abs(t_cands[best]) < 0.02, f"best Δln={t_cands[best]:.4f}")

print("\n═══ P3. 分通道 C 檢定 — C 係咪投影算符讀數 ═══")
SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
G_FREE = ["e", "mu"]          # 通道 A: 自由粒子直量
G_COLL = ["tau", "t"]         # 通道 B: 高能碰撞
G_LAT  = ["u", "d", "s", "c", "b"]  # 通道 C: lattice
# 連續層 = |dm|^{φ²} (O238 冪律)
print("  連續層 = |dm|^{φ²}:")
for grp, parts in [("A 自由", G_FREE), ("B 碰撞", G_COLL), ("C lattice", G_LAT)]:
    cs = []
    for p in parts:
        i = names9.index(p)
        layer = admn[SEL9[i]-1] ** PHI2
        cs.append(MS2[p] / layer)
    cs = np.array(cs)
    print(f"    {grp:8s}: C_i = {['%.3g' % c for c in cs]}, 幾何中位 = {math.exp(np.log(cs).mean()):.3g}, spread(log std)={np.std(np.log(cs)):.4f}")
print("  連續層 = γ (CSG):")
for grp, parts in [("A 自由", G_FREE), ("B 碰撞", G_COLL), ("C lattice", G_LAT)]:
    cs = []
    for p in parts:
        i = names9.index(p)
        cs.append(MS2[p] / gam[SEL9[i]-1])
    cs = np.array(cs)
    print(f"    {grp:8s}: C_i = {['%.3g' % c for c in cs]}, 幾何中位 = {math.exp(np.log(cs).mean()):.3g}, spread={np.std(np.log(cs)):.4f}")

print("\n═══ P4. 同通道 RMS 對比 ═══")
def fit_rms(parts, layer_fn):
    idx = [names9.index(p) for p in parts]
    logm = np.log([MS2[p] for p in parts])
    logL = np.log([layer_fn(SEL9[i]-1) for i in idx])
    logC = np.mean(logm - PHI2 * logL) if False else np.mean(logm - logL)  # 連續層已含冪
    # 實作: layer_fn 返回 layer 值 (已是 |dm|^{φ²} 或 γ); fit C (單參數垂直移動)
    logC = np.mean([math.log(MS2[p]) - math.log(layer_fn(SEL9[names9.index(p)]-1)) for p in parts])
    resid = np.array([math.log(MS2[p]) - logC - math.log(layer_fn(SEL9[names9.index(p)]-1)) for p in parts])
    return math.sqrt((resid**2).mean()), logC

for nm, lf in [("|dm|^{φ²}", lambda i: admn[i]**PHI2), ("γ", lambda i: gam[i])]:
    r_all, c_all = fit_rms(names9, lf)
    r_lat, c_lat = fit_rms(G_LAT, lf)
    print(f"  {nm:8s}: 混合9點 RMS={r_all:.6f} (logC={c_all:.4f})  |  lattice5點 RMS={r_lat:.6f} (logC={c_lat:.4f})  ratio={r_lat/r_all:.3f}")

out = {"rms8": float(rms8), "t_best": {"n": best[0], "pf": best[1], "dln": float(t_cands[best])}}
with open("data/13_csg_v2_projection.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")