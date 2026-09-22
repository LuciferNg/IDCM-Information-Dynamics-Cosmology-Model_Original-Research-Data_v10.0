#!/usr/bin/env python3
"""
O136 — Script 38: 質量 = 穿透率 × 模式能量? (二參數模型)
================================================================
Script 35-37 結果:
  sin 譜 (模式能量):        σ(α) = 15.09  🔴
  Σln cos² (88 中點):      σ(α) = 0.2388 🟡 ← 好 60 倍
  Σln cos² (60 節點):      σ(α) = 0.2454 🟡

★ 假設: 質量 = 模式能量 × 穿透率
  ln m = a + β·ln sin(nπ/88) + α·T(n)
  或 m ∝ sin^β · T^α

本 script: 系統測試二參數模型 + 變體
"""
import numpy as np, math, json, itertools
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
O182 = ROOT / "o182_88grid_geometry/data"
OUT = Path(__file__).parent.parent / "data"

mass = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
M = [1,2,3,4,5,7,9,11,13]
sp = sorted(mass, key=lambda p: mass[p])

# 幾何
nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
U = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
l, b = math.radians(209.0), math.radians(-57.0)
cold = np.array([math.cos(b)*math.cos(l), math.cos(b)*math.sin(l), math.sin(b)])
beta = np.arccos(np.clip(U @ cold, -1, 1))

emap=[]
for line in (O182/"g88_edge_map.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p=line.split(); emap.append((int(p[0]),int(p[1]),int(p[2])))
emap.sort()
tm = np.array([U[u]+U[v] for _,u,v in emap]); tm/=np.linalg.norm(tm,axis=1,keepdims=True)
bP = np.arccos(np.clip(tm@cold,-1,1))
fn = np.loadtxt(O182/"g32_frustration_midpoints.txt")
fm = np.column_stack([np.cos(np.radians(fn[:,1]))*np.cos(np.radians(fn[:,0])),
                      np.cos(np.radians(fn[:,1]))*np.sin(np.radians(fn[:,0])),
                      np.sin(np.radians(fn[:,1]))])
fm/=np.linalg.norm(fm,axis=1,keepdims=True)
bO = np.arccos(np.clip(fm@cold,-1,1))

print("=" * 96)
print("O136 Script 38: 質量 = 穿透率 × 模式能量?")
print("=" * 96)

# ═══ 定義各種 T ═════════════════════════════════════
def T60(n): return float(np.log(np.clip(np.cos(n*beta/2)**2,1e-300,1)).sum())
def T88(n): return float(np.log(np.clip(np.cos(n*bP/2)**2,1e-300,1)).sum())
def T32(n): return float(np.log(np.clip(np.cos(n*bO/2)**2,1e-300,1)).sum())
def Tdiff(n): return T88(n) - T32(n)

DEFS = {
    "T60": T60, "T88": T88, "T32": T32, "T88-T32": Tdiff,
    "T88-2*T32": lambda n: T88(n) - 2*T32(n),
    "T60-T32": lambda n: T60(n) - T32(n),
}

# ═══ 1. 一參數 vs 二參數擬合 (單調配對) ══════════════
print(f"\n{'─'*96}")
print("1. 一參數 vs 二參數擬合 (單調配對: 最小 f ↔ 最小質量)")
print(f"{'─'*96}")

Y = np.array([math.log(mass[p]) for p in sp])
S = np.array([math.sin(n*math.pi/88) for n in M])
lnS = np.log(S)

print(f"\n{'定義':>12} {'模型':>22} {'RMS':>10} {'參數':>26}")
print("-" * 74)

res_all = []
for name, f in DEFS.items():
    Tv = np.array([f(n) for n in M])
    order = np.argsort(Tv); Tp = Tv[order]
    # 一參數: ln m = a + α T
    A1 = np.vstack([np.ones(9), Tp]).T
    c1, *_ = np.linalg.lstsq(A1, Y, rcond=None)
    r1 = float(np.sqrt(np.mean((A1@c1 - Y)**2)))
    print(f"{name:>12} {'a + α·T':>22} {r1:>10.4f} {f'a={c1[0]:.3f}, α={c1[1]:.6f}':>26}")
    res_all.append((r1, name, "1p", c1))
    # 二參數: ln m = a + α T + β ln sin
    Sp = S[order]; lnSp = np.log(Sp)
    A2 = np.vstack([np.ones(9), Tp, lnSp]).T
    c2, *_ = np.linalg.lstsq(A2, Y, rcond=None)
    r2 = float(np.sqrt(np.mean((A2@c2 - Y)**2)))
    print(f"{name:>12} {'a + α·T + β·ln sin':>22} {r2:>10.4f} {f'α={c2[1]:.5f}, β={c2[2]:.3f}':>26}")
    res_all.append((r2, name, "2p", c2))

print(f"\n★ 對照: 純 sin 譜 (a + β ln sin):")
A0 = np.vstack([np.ones(9), lnS]).T
c0, *_ = np.linalg.lstsq(A0, Y, rcond=None)
r0 = float(np.sqrt(np.mean((A0@c0 - Y)**2)))
print(f"   RMS = {r0:.4f}, β = {c0[1]:.3f}")
print(f"★ ln(m) 本身的標準差 = {Y.std():.4f} (完全無解釋的上限)")

res_all.sort(key=lambda z: z[0])
print(f"\n★ 最佳: {res_all[0][1]} / {res_all[0][2]}, RMS = {res_all[0][0]:.4f}")
print(f"→ {'🟢 解釋質量' if res_all[0][0] < 0.5 else ('🟡 部分' if res_all[0][0] < 1.5 else '🔴 唔解釋')}")

# ═══ 2. ★ 全配對搜索 (最佳定義) ══════════════════════
print(f"\n{'─'*96}")
print("2. ★ 全配對搜索 (二參數模型, 最佳定義)")
print(f"{'─'*96}")

best_name = res_all[0][1]
Tv = np.array([DEFS[best_name](n) for n in M])
best = []
for perm in itertools.permutations(range(9)):
    Tp = Tv[list(perm)]; Sp = S[list(perm)]
    A2 = np.vstack([np.ones(9), Tp, np.log(Sp)]).T
    c2, *_ = np.linalg.lstsq(A2, Y, rcond=None)
    rms = float(np.sqrt(np.mean((A2@c2 - Y)**2)))
    best.append((rms, perm, c2))
best.sort(key=lambda z: z[0])
print(f"\n搜索: 9! = {math.factorial(9)} 配對 (定義 = {best_name})")
print(f"\n最佳 5 個:")
print(f"\n{'RMS':>9} {'配對 (模式→粒子)':>46} {'α':>10} {'β':>10}")
print("-" * 78)
for rms, perm, c2 in best[:5]:
    ps = " ".join(f"{p}:{M[i]}" for p, i in zip(sp, perm))
    print(f"{rms:>9.4f} {ps:>46} {c2[1]:>10.5f} {c2[2]:>10.4f}")

print(f"\n★ 最佳 RMS = {best[0][0]:.4f}")
print(f"→ {'🟢 強解釋' if best[0][0] < 0.3 else ('🟡 部分解釋' if best[0][0] < 1.0 else '🔴 唔解釋')}")

# ═══ 3. ★★ 最佳配對的逐粒子檢驗 ════════════════════
print(f"\n{'─'*96}")
print("3. ★★ 最佳配對的逐粒子檢驗")
print(f"{'─'*96}")

rms_b, perm_b, c2_b = best[0]
Tp = Tv[list(perm_b)]; Sp = S[list(perm_b)]
pred = c2_b[0] + c2_b[1]*Tp + c2_b[2]*np.log(Sp)
print(f"\n{'粒子':>6} {'模式':>5} {'觀測 (MeV)':>13} {'預測 (MeV)':>13} {'比':>9} {'偏差%':>10}")
print("-" * 62)
for k, (p, i) in enumerate(zip(sp, perm_b)):
    obs = mass[p]; pr = math.exp(pred[k])
    print(f"{p:>6} {M[i]:>5} {obs:>13.4f} {pr:>13.4f} {pr/obs:>9.4f} {(pr/obs-1)*100:>+10.2f}")

print(f"\n★ 平均 |偏差| = {np.mean([abs(math.exp(pred[k])/mass[p]-1) for k,p in enumerate(sp)])*100:.2f}%")
print(f"★ 最大 |偏差| = {np.max([abs(math.exp(pred[k])/mass[p]-1) for k,p in enumerate(sp)])*100:.2f}%")

# ═══ 4. 保存 ════════════════════════════════════════
with open(OUT / "38_transmission_energy_model.json", "w") as f:
    json.dump({
        "definitions": list(DEFS.keys()),
        "one_param_best": {"rms": res_all[0][0], "defn": res_all[0][1], "model": res_all[0][2]},
        "pure_sin_rms": r0,
        "ln_m_std": float(Y.std()),
        "best_pairing": {"rms": best[0][0], "defn": best_name,
                         "pairing": dict(zip(sp, [M[i] for i in best[0][1]])),
                         "alpha": best[0][2][1], "beta": best[0][2][2]},
        "verdict": "見 stdout",
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/38_transmission_energy_model.json")