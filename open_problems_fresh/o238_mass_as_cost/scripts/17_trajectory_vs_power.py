#!/usr/bin/python3
"""O238 — Script 17: 軌跡模型 vs 冪律模型 — LOOCV 樣本外 + freeze v2 預言對表

docs/16: PC1 (譜平面軌跡) ↔ log m Spearman=+1.0 (完美單調), corr=+0.986.
問題: PC1 模型 (log m = a + b·PC1) 同 |dm|^{φ²} 冪律模型, 邊個樣本外預言好?

  P1 LOOCV blind: 每輪 8 點 fit 各自模型, 預言留出點 — MSPE 比較
  P2 軌跡模型預言 quark 比 vs freeze v2 lattice (對照 scripts/09 冪律 5/5 全滅)
  P3 O234 預言 register 對表工程 — 列未量度預言 + 觸發條件 (真 out-of-sample 等待)
  P4 歸納: 「投影 operator 幾何形式 = 沿軌跡單調位置 ↔ 質量」嘅意義
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
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MS2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
       "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
       "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}
logm = np.array([math.log(MS2[p]) for p in names9])
X = np.array([[math.log(gam[n-1]), math.log(admn[n-1])] for n in SEL9])

# PC1 座標 (用 scripts/16 方法, 全 9 點 fit)
Xc = X - X.mean(axis=0)
cov = Xc.T @ Xc / 8
evals, evecs = np.linalg.eigh(cov)
order = np.argsort(evals)[::-1]
evecs = evecs[:, order]
pc1 = Xc @ evecs[:, 0]
logd = np.log([admn[n-1] for n in SEL9])

print("═══ P1. LOOCV blind: PC1 模型 vs |dm|^{φ²} 冪律 ═══")
msp_pc1, msp_pow = [], []
wins = {"PC1": 0, "pow": 0}
for i in range(9):
    tr = [j for j in range(9) if j != i]
    # PC1 模型 (2 參數: a + b·PC1, PC1 由 8 點重算)
    Xctr = X[tr] - X[tr].mean(axis=0)
    covt = Xctr.T @ Xctr / 7
    evt, evct = np.linalg.eigh(covt)
    o = np.argsort(evt)[::-1]
    pc1t = Xctr @ evct[:, o[0]]
    pc1i = (X[i] - X[tr].mean(axis=0)) @ evct[:, o[0]]
    A1 = np.vstack([np.ones(8), pc1t]).T
    c1, *_ = np.linalg.lstsq(A1, logm[tr], rcond=None)
    pred1 = c1[0] + c1[1] * pc1i
    e1 = pred1 - logm[i]
    # 冪律 (固定 φ², 只 fit C)
    Cp = math.exp((logm[tr] - PHI2 * logd[tr]).mean())
    predp = math.log(Cp) + PHI2 * logd[i]
    ep = predp - logm[i]
    msp_pc1.append(e1**2); msp_pow.append(ep**2)
    w = "PC1" if abs(e1) < abs(ep) else "pow"
    wins[w] += 1
    print(f"  {names9[i]:4s}: PC1 err={e1:+.4f}  pow err={ep:+.4f}  win={w}")
mspe1 = np.mean(msp_pc1); mspe2 = np.mean(msp_pow)
print(f"\n  MSPE(PC1)={mspe1:.6f}  MSPE(pow)={mspe2:.6f}  ratio={mspe1/mspe2:.4f}")
print(f"  逐點勝出: PC1 {wins['PC1']}/9  pow {wins['pow']}/9")
chk("P1.1 冪律唔差過 PC1 (MSPE ratio<2)", mspe1/mspe2 < 2, f"ratio={mspe1/mspe2:.4f}")

print("\n═══ P2. 軌跡模型預言 quark 比 vs freeze v2 ═══")
# 用全 9 點 fit PC1 模型
A1 = np.vstack([np.ones(9), pc1]).T
c1, *_ = np.linalg.lstsq(A1, logm, rcond=None)
mp = {}
for i, p in enumerate(names9):
    mp[p] = math.exp(c1[0] + c1[1] * pc1[i])
pairs = [("d","u",2.1505,0.111), ("s","u",42.8893,1.5165), ("c","s",11.652,0.175),
         ("b","c",4.586,0.012), ("b","s",53.3692,0.7374)]
nbig = 0
for a, b, lat, lat_e in pairs:
    fp = mp[a]/mp[b]
    z = (fp-lat)/lat_e
    nbig += (abs(z) > 3)
    print(f"  {a}/{b}: PC1-fit={fp:9.4f} vs lattice={lat:9.4f}±{lat_e:.4f}  z={z:+.1f}σ")
print(f"  >3σ 數: {nbig}/5")
chk("P2.1 軌跡模型比空間照樣全滅 (數量級律特徵)", nbig >= 3, f"{nbig}/5 >3σ")

print("\n═══ P3. O234 預言 register 對表工程 ═══")
print("""
  O234 docs/03 §六 pre-registered 預言 (未來 lattice 量度觸發):
  ┌───────────────────────────────────────────────────────────────┐
  │ 預言             值±誤差         觸發 (新量度)          判決    │
  │ md/mu (MS)     2.1505±0.111   lattice 1–2% mu/md    純γ vs shape│
  │ ms/mu (killer) 42.89±1.52     lattice 直量 1%        一擊即決    │
  │ ms/md          19.944±0.332   lattice 直量           同上架構    │
  │ mc/mu          499.75±17.89   lattice 直量 mc/mu                │
  │ mc/md          232.39±14.60   lattice 直量                      │
  │ mb/ms (RGI)    53.369±0.737   RGI 第二通道         已閉環 z=+0.08│
  │ mb/mc (3GeV)   4.586±0.012    已凍結 (HPQCD-21)                 │
  │ RGI d/u        2.1987±0.092   已凍結               純γ z=+0.51   │
  └───────────────────────────────────────────────────────────────┘
  真 out-of-sample 狀態: 未有新 lattice 量度落地 (web search 2025 無新 FLAG 更新)
  ⟹ O238 冪律/軌跡模型對「未量度比」嘅預言 = O238 自身預言, 等觸發:
    ms/mu: IDCM 冪律預言 s/u ≈ 12.86  (vs O234 42.89 — 若 1% 量度落地即刻判死)
    —— 呢個就係「數量級律非閉合」嘅 out-of-sample 判決點
""")

print("═══ P4. 歸納 ═══")
print(f"  PC1 軌跡: 質量排序 = 軌跡排序 (Spearman +1.0) — 投影 operator 幾何形式")
print(f"  冪律:     log m = log C + φ²·log|dm| — 同 PC1 正交成分嘅差異極細")
print(f"  樣本外:   兩模型 LOOCV 幾乎等價; 比空間預言照樣全滅 (數量級律共有特徵)")

out = {"mspe_pc1": float(mspe1), "mspe_pow": float(mspe2), "wins": wins,
       "nbig_pc1": int(nbig)}
with open("data/17_trajectory_vs_power.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")