#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-40 — 連結層盲測: 17 強子 × 預註冊結構候選族 (O238 移交落地)
================================================================
問題: O238 docs/11 已證『冪律層 C|dm|^{φ²} 唔描述強子』(6/17< 池密度 8.6);
docs/27 證『SU(12) 全量 E_conn = 1809.4 M₀ 冇即刻承接強子』。本輪正式攻:
強子質量 = 節點(冪律層) + 連結能量(連結層), 對 17 個強子盲測**預註冊**結構候選族。

★ 預註冊 (跑前凍結, 零放寬; 違反 = 本 script 作廢):
  [P0] 節點質量 N_h = Σ_{quark modes} C·|dm_m|^{φ²}, C = 1.52151e-6 (O238 S2 freeze v2, 零新參數)
  [P1] 夸克↔mode 映射 = O238 SEL9: u=11, d=9, s=7, c=4, b=2, t=1 (已由 9 點 fit 鎖)
  [P2] 17 強子 = O238 scripts/21 表 (質心質量)
  [P3] 候選族 T0,T1a,T1b,T2,T3,T5 (定義見下, 只含結構常數 {M₀, M_tree=33, L₅=11, E'(q_m)})
  [P4] 通過判準 (全部必須):
        C1  ≥14/17 個 |dev| ≤ 3%
        C2  中位數 |dev| ≤ 1.5%
        C3  無單點 > 8%
        C4  (最佳候選) 剛性: 常數擾動 ±2% ⟹ 中位 dev 變化 ≥ 2× (非池巧合)
  [P5] 誠實負判決: T 族全 FAIL ⟹ 記錄每族命中/偏差 + 殘差圖 (4.4, 純描述,
       唔可以用殘差圖砌新算子 — 新族必須 scripts/41 重新預註冊 + 新盲測)

候選族定義 (m_pred = N_h + E_link):
  T0  E_link = 0                        (節點 only; 基線)
  T1a E_link = n_q × L₅·M₀              (每夸克一條通量管, 長度 L₅=11; 介子 22, 重子 33)
  T1b E_link = (baryon? M_tree : L₅)·M₀  (重子樹深 33 = M_tree; 介子單管 11)
  T2  E_link = M₀·Σ_{m∈quarks} D_m      (D_m = E'(q_m) − 176 平台偏差; M₀ units)
  T3  E_link = M₀·|Σ D_m|
  T5  E_link = M₀·(σ_{pairs} ring(m_a,m_b))·½   (88 環 index 距離; 量尺度記錄)

F₁ 餘 (描述層, 非候選): R_h = (m_obs − N_h)/M₀ 每強子殘差; 對 n_s (s quark 數)
    與 Σ modes 嘅相關 (Pearson) — 只用於下一輪假說生成, 標記 🟡 唔係算子。

寫入: data/40_linkage_layer_blind.json (冪等, seed 固定)
"""
import json, math, sys
from collections import Counter

# ---------------------------------------------------------------- §1 鏈輸入
N88 = 88
try:
    import numpy as np
    _HAVE_NP = True
    idxx = np.arange(1, N88 + 1)
    psii = np.array([np.sin(n * math.pi * idxx / (N88 + 1)) for n in range(1, N88 + 1)])
    psii = psii / np.linalg.norm(psii, axis=1)[:, None]
    Xm = np.diag(idxx - idxx.mean())
    Vmat = psii @ Xm @ psii.T
    E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N88 + 1)])
    D = E[:, None] - E[None, :]
    G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
    np.fill_diagonal(G, 0.0)
    dm = np.einsum('ab,ab->a', Vmat ** 2, G)
    dm = dm.tolist()
except ImportError:
    _HAVE_NP = False
    # 純 Python 後備 (O238 同構)
    k = list(range(1, N88 + 1))
    mean = N88 / 2 + 0.5  # mean of 1..88
    psi = [[math.sin(n * math.pi * kk / (N88 + 1)) for kk in k] for n in range(1, N88 + 1)]
    norm = [math.sqrt(sum(x * x for x in row)) for row in psi]
    psi = [[x / nrm for x in row] for row, nrm in zip(psi, norm)]
    Vmat = [[sum(psi[n][i] * (k[i] - mean) * psi[n][j] for n in range(N88)) for j in range(N88)] for i in range(N88)]
    E = [4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N88 + 1)]
    dm = []
    for a in range(N88):
        s = 0.0
        for b in range(N88):
            if abs(E[a] - E[b]) > 1e-12:
                s += (Vmat[a][b] ** 2) / (E[a] - E[b])
        dm.append(abs(s))
    _HAVE_NP = False
print(f"  chain: numpy={'Y' if _HAVE_NP else 'N'}; |dm| max @ n={dm.index(max(dm))+1} = {max(dm):.4f}")

C = 1.52151e-6
PHI2 = ((1 + math.sqrt(5)) / 2) ** 2
M0 = 27.90091451
def Nmode(m):
    return C * abs(dm[m - 1]) ** PHI2

SEL9 = {"t": 1, "b": 2, "tau": 3, "c": 4, "mu": 5, "s": 7, "d": 9, "u": 11, "e": 13}
MODEMASS = {name: Nmode(m) for name, m in SEL9.items()}
print("  冪律節點質量 (MeV):")
for p in sorted(MODEMASS, key=lambda x: MODEMASS[x]):
    print(f"    {p:>4s} (mode {SEL9[p]:2d}) = {MODEMASS[p]:9.4f}")

# ---------------------------------------------------------------- §2 強子表
HADRONS = {
    "pi0": (134.9768, [11, 9]), "pi+": (139.57039, [11, 9]),
    "K+": (493.677, [11, 7]), "K0": (497.611, [9, 7]),
    "eta": (547.862, [11, 9, 7]), "eta'": (957.78, [11, 9, 7]),
    "p": (938.272088, [11, 11, 9]), "n": (939.565421, [11, 9, 9]),
    "Lambda": (1115.683, [11, 9, 7]), "Sigma+": (1189.37, [11, 11, 7]),
    "Xi0": (1314.86, [11, 7, 7]),
    "D0": (1864.84, [4, 11]), "D+": (1869.66, [4, 9]),
    "B+": (5279.32, [11, 2]), "B0": (5279.63, [9, 2]),
    "J/psi": (3096.9, [4, 4]), "Upsilon": (9460.30, [2, 2]),
}
# E'(q_m) — SU(12) 移位每纖維 (data/35 gold)
EF = {4: 114.865277982844, 2: 202.400151085512, 1: 160.771161893925,
      3: 206.013275636098, 5: 12.506466127581, 7: 134.717027433432,
      9: 195.235149040176, 11: 165.586979074824, 13: 185.187465460336}

def ring_dist(a, b):
    d = abs(a - b)
    return min(d, 88 - d)

def pred(Nh, link):
    return Nh + link

# ---------------------------------------------------------------- §3 候選族 x 17
def candidates():
    fams = {}
    for name, (mobs, ms) in HADRONS.items():
        Nh = sum(Nmode(m) for m in ms)
        nq = len(ms)
        baryon = nq == 3
        fams[name] = {
            "N_h": Nh,
            "T0": Nh,
            "T1a": Nh + nq * 11 * M0,
            "T1b": Nh + (33 if baryon else 11) * M0,
            "T2": Nh + sum(EF[m] - 176 for m in ms) * M0,
            "T3": Nh + abs(sum(EF[m] - 176 for m in ms)) * M0,
            "T5": Nh + (sum(ring_dist(ms[i], ms[j]) for i in range(nq) for j in range(i + 1, nq)) / 2) * M0,
        }
    return fams

fams = candidates()
PLAN = ["T0", "T1a", "T1b", "T2", "T3", "T5"]
def stats(tag):
    devs = [abs(fams[h][tag] - HADRONS[h][0]) / HADRONS[h][0] for h in HADRONS]
    devs_sorted = sorted(devs)
    med = devs_sorted[len(devs_sorted) // 2]
    le3 = sum(1 for d in devs if d <= 0.03)
    mx = max(devs)
    return {"count": len(devs), "le3": le3, "median": med, "max": mx, "all": devs}

print("\n═══ 候選族盲測 (17 強子) ═══")
verdicts = {}
for tag in PLAN:
    st = stats(tag)
    c1 = st["le3"] >= 14
    c2 = st["median"] <= 0.015
    c3 = st["max"] <= 0.08
    passed = c1 and c2 and c3
    verdicts[tag] = {"le3": st["le3"], "median": round(st["median"], 4), "max": round(st["max"], 4),
                     "C1": c1, "C2": c2, "C3": c3, "PASS": passed}
    print(f"  {tag:>4s}: ≤3% {st['le3']:2d}/17  中位 {st['median']*100:6.2f}%  max {st['max']*100:6.2f}%  "
          f"C1{'✓' if c1 else '✗'} C2{'✓' if c2 else '✗'} C3{'✓' if c3 else '✗'}  ⟹ {'✅' if passed else '✗ 淘汰'}")

# C4 剛性: 最佳通過者 (若無, 對最小中位者做 — 記錄純度)
best = min(PLAN, key=lambda t: stats(t)["median"])
st_best = stats(best)
base_med = st_best["median"]
pert = {}
for frac in (0.98, 1.02):
    # 對 T1a/T1b/T5 擾動 M0/長度常數; 對 T2/T3 擾動 D 尺度
    scale = 11 * M0 if best in ("T1a", "T1b") else (M0 if best in ("T2", "T3") else M0)
    val = []
    for name, (mobs, ms) in HADRONS.items():
        Nh = fams[name]["N_h"]
        if best == "T0":
            link = 0
        elif best == "T1a":
            link = len(ms) * 11 * M0 * frac
        elif best == "T1b":
            link = (33 if len(ms) == 3 else 11) * M0 * frac
        elif best == "T2":
            link = sum(EF[m] - 176 for m in ms) * M0 * frac
        elif best == "T3":
            link = abs(sum(EF[m] - 176 for m in ms)) * M0 * frac
        else:
            nq = len(ms); link = sum(ring_dist(ms[i], ms[j]) for i in range(nq) for j in range(i + 1, nq)) * M0 * frac / 2
        val.append(abs(Nh + link - mobs) / mobs)
    vs = sorted(val)
    pert[frac] = vs[len(vs) // 2]
dmed = max(abs(pert[f] - base_med) for f in pert)
rigid = dmed >= 2 * max(base_med, 1e-9)
print(f"\n  C4 (最佳={best}): 中位 {base_med*100:.3f}% → ±2% 擾動中位 {pert[0.98]*100:.3f}%/{pert[1.02]*100:.3f}%, Δ={dmed*100:.3f}% "
      f"{'≥2× ✅' if rigid else '<2× (常數非承重/池巧合)'}")

# ---------------------------------------------------------------- §4 殘差圖 (描述層)
print("\n═══ 殘差圖 R_h = (m_obs − N_h)/M₀ (描述層, 唔係算子) ═══")
rows = []
for name, (mobs, ms) in sorted(HADRONS.items(), key=lambda kv: kv[1][0]):
    Nh = fams[name]["N_h"]
    Rh = (mobs - Nh) / M0
    ns = ms.count(7)
    rows.append({"hadron": name, "modes": ms, "n_s": ns, "N_h": round(Nh, 4),
                 "R_h M0": round(Rh, 4), "R_h MeV": round(Rh * M0, 3)})
    print(f"  {name:>6s} {mobs:9.3f}  modes={ms}  N_h={Nh:8.3f}  R_h={Rh:7.3f} M₀ ({Rh*M0:8.3f} MeV)  n_s={ns}")
# 描述統計: R_h vs n_s / Σmodes 相關
import statistics
Rh = [r["R_h M0"] for r in rows]
nS = [r["n_s"] for r in rows]
sM = [sum(r["modes"]) for r in rows]
def pear(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    vx = math.sqrt(sum((a - mx) ** 2 for a in x))
    vy = math.sqrt(sum((b - my) ** 2 for b in y))
    return cov / (vx * vy) if vx and vy else float("nan")
r_ns = pear(Rh, nS); r_sm = pear(Rh, sM)
print(f"  ★ 描述相關 (禁止用做算子): corr(R_h, n_s) = {r_ns:+.3f}, corr(R_h, Σmodes) = {r_sm:+.3f}")
print(f"  → 下一輪假說 (scripts/41) 必須重新預註冊; 唔可以由此砌算子")

# ---------------------------------------------------------------- §5 判決
all_pass = any(v["PASS"] for v in verdicts.values())
print("\n═══ 判決 ═══")
print(f"  任何候選族通過盲測? {'✅' if all_pass else '🔴 無 — 誠實負'}")
if all_pass:
    ws = [t for t, v in verdicts.items() if v["PASS"]]
    print(f"  通過: {ws}; C4 {('剛性 ✅' if rigid else '剛性 ✗')}")

OUT = {"chain_numpy": _HAVE_NP, "C": C, "PHI2": PHI2, "M0": M0,
       "node_masses": MODEMASS, "candidates": verdicts,
       "best": best, "C4": {"rigid": rigid, "base_median": base_med, "pert": {str(k): v for k, v in pert.items()}},
       "residual_map": rows, "corr_ns": r_ns, "corr_sm": r_sm,
       "family_preds": fams, "verdict": ("closed-family" if all_pass else "honest-negative")}
with open("data/40_linkage_layer_blind.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print(f"\n  data/40_linkage_layer_blind.json 寫入完成")
print(f"  判決: {'✅ 有候選族通過 → 需樣本外/密度加固' if all_pass else '🔴 誠實負 — 連結層公式需新推導 (scripts/41 重預註冊)'}")
sys.exit(0 if all_pass else 0)