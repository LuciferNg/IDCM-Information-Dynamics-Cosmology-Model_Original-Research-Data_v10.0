#!/usr/bin/python3
"""O238 — Script 15: CSG 網格 vs A₅ — 邊個 mode 分配先係投影 signature?

docs/06/07 已立: SEL9 (A₅ 分配 {1,2,3,4,5,7,9,11,13}) 喺 (log|dm|, logγ) 平面
共線 R²=0.992 (MC p=0.00015) = 投影算符 signature. 但 O206-OPEN-4 提到 CSG v2
網格分配 {1,7,14,20,33,34} (8 粒子: e/u/d 共享 n=1!). 本 script:

  P1 CSG 網格 8 點喺 (log|dm|, logγ) 平面嘅共線性 R² (對照 A₅)
  P2 e/u/d 共享 n=1 嘅後果: 共線嘅話, 單 mode 多 P_f 係咪即係「投影算符+selection」?
  P3 若 CSG 網格唔共線 ⟹ 唔係投影 signature, A₅ 維持
  P4 量度: 兩個分配喺譜平面嘅殘差分布 — 邊個更「選中」結構?
"""
import numpy as np, math, json

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

logd = np.log(admn)
logg = np.log(gam)

# A₅ 分配 (O238 SEL9)
SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
maskA5 = np.zeros(N, bool); maskA5[np.array(SEL9)-1] = True

# CSG 網格分配 (O206 docs/22): e(1), mu(7), tau(20), u(1), d(1), s(14), c(34), b(33)
CSG = {"e": 1, "mu": 7, "tau": 20, "u": 1, "d": 1, "s": 14, "c": 34, "b": 33}
CSG_modes = sorted(set(CSG.values()))
print(f"CSG 網格 modes: {CSG_modes}  (8 粒子 → {len(CSG_modes)} 唯一 modes; e/u/d 共享 n=1)")

def r2_of(mask):
    ld = logd[mask]; lg = logg[mask]
    A = np.vstack([np.ones(mask.sum()), lg]).T
    c, *_ = np.linalg.lstsq(A, ld, rcond=None)
    r = ld - A @ c
    ss_res = (r**2).sum(); ss_tot = ((ld-ld.mean())**2).sum()
    return 1 - ss_res/ss_tot, c

print("\n═══ P1. 兩分配共線性對照 ═══")
r2_a5, c_a5 = r2_of(maskA5)
maskCsg = np.zeros(N, bool); maskCsg[np.array(CSG_modes)-1] = True
r2_csg, c_csg = r2_of(maskCsg)
print(f"  A₅  分配 (9 points): R² = {r2_a5:.6f}  slope={c_a5[1]:+.4f}")
print(f"  CSG 網格 (6 unique modes → 但 8 粒子重複): R² = {r2_csg:.6f}  slope={c_csg[1]:+.4f}")
chk("P1.1 A₅ 共線 R²>0.95 (維持 docs/06)", r2_a5 > 0.95, f"R²={r2_a5:.6f}")

print("\n═══ P2. CSG 網格喺譜平面: 逐點位置 ═══")
for p, n in CSG.items():
    print(f"  {p:>4} n={n:2d}: logγ={logg[n-1]:+8.4f}  log|dm|={logd[n-1]:+9.4f}")

# 全譜 fit 個 reference (唔用 mask, 用 88 點)
A88 = np.vstack([np.ones(N), logg]).T
c88, *_ = np.linalg.lstsq(A88, logd, rcond=None)
r88 = logd - A88 @ c88
r2_88 = 1 - (r88**2).sum() / ((logd-logg.mean()*0 + logd - logd.mean())**2).sum()
ss_tot88 = ((logd - logd.mean())**2).sum()
r2_88 = 1 - (r88**2).sum() / ss_tot88
print(f"\n  全譜 88 點: R² = {r2_88:.4f}")

# 逐點距 (CSG 8 點對 88 譜 fit 線嘅垂直距離)
print("\n  CSG 8 點離全譜線: (log|dm| − [a88 + b88·logγ])")
for p, n in CSG.items():
    dev = logd[n-1] - (c88[0] + c88[1]*logg[n-1])
    print(f"    {p:>4} n={n:2d}: dev={dev:+.4f}")

print("\n═══ P3. 隨機 6-mode 組合 R² 分佈 (CSG 網格係咪選中結構?) ═══")
rng = np.random.default_rng(20261011)
r2s = []
for _ in range(20000):
    pick = rng.choice(N, 6, replace=False)
    m = np.zeros(N, bool); m[pick] = True
    r2s.append(r2_of(m)[0])
r2s = np.array(r2s)
p_csg = (r2s >= r2_csg).mean()
print(f"  隨機 6 modes 20000 次: R² mean={r2s.mean():.4f} max={r2s.max():.4f}  P(R²≥{r2_csg:.4f})={p_csg:.6f}")
chk("P3.1 CSG 網格 6 modes 共線顯著異常", p_csg < 0.05, f"p={p_csg:.6f}")

print("\n═══ P4. 裁決輸入 ═══")
print(f"  A₅ : R²={r2_a5:.6f} (9 points, MC p=0.00015 from docs/06)")
print(f"  CSG: R²={r2_csg:.6f} (6 unique modes, MC p={p_csg:.6f})")

out = {"r2_a5": float(r2_a5), "r2_csg": float(r2_csg), "p_csg": float(p_csg),
       "csg_modes": CSG_modes}
with open("data/15_csg_vs_a5_collinear.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")