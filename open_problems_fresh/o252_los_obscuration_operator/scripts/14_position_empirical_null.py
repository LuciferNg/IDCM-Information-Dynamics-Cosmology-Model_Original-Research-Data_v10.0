#!/usr/bin/env python3
"""
O252 — Script 14: position empirical null + sign 源性質相關 (2026-10-17)
=========================================================================
A. Empirical null: 掃描所有候選窗中心 w∈[0,800] 計命中率 (窗半寬 σ_E=189.52)
   問題: 原本 MC null 假設 dip 均勻 ±1500, 但 fit 可能中心聚集 bias。
   如果 289.76 係命中率曲線唯一 peak → 結構證據強;
   如果所有 w 命中率高 (中心聚集) → 9/12 命中唔係結構, 拆彈。
B. sign 相關: 藍側源 vs 紅側源嘅 z / |dv| / depth / σ 分佈 — 側向身份線索
C. 事前 peak 檢驗: 289.76 命中數 vs 全曲線 95% 上限
"""
import json, math, os
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

sig_E = 189.525                  # σ_window 修正值 (script 12)
v_abs = 289.759

with open(f"{DATA}/07_full_sample_scan.json") as f:
    d7 = json.load(f)
res = [r for r in d7["results"] if r["sig"] and abs(r["dv"]) < 700 and r["depth"] < 1.2]
# 去重: 每 (源,線) 一代表 (優先 h)
gr_rank = {'g395h': 0, 'g395m': 1}
best = {}
for r in res:
    key = (r["src"], r["line"])
    g = r.get("grating", "g395m")
    if key not in best or gr_rank.get(g, 1) < gr_rank.get(best[key].get("grating","g395m"),1):
        best[key] = r
uniq = list(best.values())
dv_abs = np.array([abs(r["dv"]) for r in uniq])
n = len(dv_abs)

print("="*84)
print("O252/14 — position empirical null + sign 源性質")
print("="*84)
print(f"去重後 n={n}: |dv| = {sorted(dv_abs.tolist())}")

# ---------- A: 命中率曲線 ----------
wins = np.arange(0, 801, 5)
hits = np.array([np.sum((dv_abs >= w-sig_E) & (dv_abs <= w+sig_E)) for w in wins])
peak_w = wins[np.argmax(hits)]
peak_n = hits.max()
hits_at_vabs = np.sum((dv_abs >= v_abs-sig_E) & (dv_abs <= v_abs+sig_E))
# 95% 上限 (經驗分佈: 曲線嘅 upper quartile 附近 — 保守用命中數 > 50% 分位)
upper5 = np.percentile(hits, 95)
print(f"命中率曲線: peak w={peak_w} km/s (n={peak_n}); "
      f"w=289.76 命中 n={hits_at_vabs}; 95% 上限={upper5:.0f}")
# 獨特性: 289.76 係咪唯一 peak? peak_w 係咪近 289.76?
ck("A1 peak 喺 289.76±40", abs(peak_w - v_abs) < 40,
   f"peak={peak_w}, v_abs={v_abs}")
ck("A2 peak 命中 > 95% 曲線值", peak_n > upper5 + 0.5,
   f"peak_n={peak_n}, 95%={upper5:.0f}")
# 曲線底部 (最低命中 window) — 如果全部窗都高, 係中心聚集
min_n = hits.min()
min_loc = wins[np.argmin(hits)]
print(f"曲線範圍: min n={min_n} (w={min_loc}), max n={peak_n} (w={peak_w})")
ck("A3 曲線有動態範圍 (min<max−1)", max_n := peak_n - min_n >= 2,
   f"range={peak_n-min_n}")

# ---------- B: sign 相關 ----------
blue = [r for r in uniq if r["dv"] < 0]
red  = [r for r in uniq if r["dv"] > 0]
def stat(lst, key):
    return [r[key] for r in lst]
print(f"\n藍側 n={len(blue)}, 紅側 n={len(red)}")
for key, name in [("dv","dv"), ("depth","depth"), ("sig_dip","σ"), ("dAIC","ΔAIC")]:
    b, r = stat(blue, key), stat(red, key)
    if b and r:
        mb, mr = np.mean(b), np.mean(r)
        print(f"  {name:6s}: 藍 mean={mb:8.2f}  紅 mean={mr:8.2f}  Δ={mb-mr:+8.2f}")
# z (唔喺 scan json — 用 SOURCES 表)
zmap = {"A":5.0405,"C":4.1325,"E":6.6847,"F":4.4779,"G":3.6493,
        "I":3.4304,"J":5.8683,"K":5.2394}
zb = [zmap[r["src"]] for r in blue if r["src"] in zmap]
zr = [zmap[r["src"]] for r in red if r["src"] in zmap]
print(f"  z     : 藍 mean={np.mean(zb):.3f} (n={len(zb)})  紅 mean={np.mean(zr):.3f} (n={len(zr)})")
ck("B1 紅側 z 低於藍側 (側向身份線索)", np.mean(zr) < np.mean(zb),
   f"紅 z_mean={np.mean(zr):.3f} < 藍 z_mean={np.mean(zb):.3f}")

# ---------- C: 事前 peak 檢驗 ----------
# 隨機 null: 12 個點放 ±1500 均勻, 窗半寬 189.52 → 期望命中 12×379/3000=1.52
n_sim = 10000
rng = np.random.default_rng(20261017)
null_hits = np.zeros(n_sim)
for i in range(n_sim):
    pts = rng.uniform(0, 1500, n)
    null_hits[i] = np.sum((pts >= v_abs-sig_E) & (pts <= v_abs+sig_E))
p_null = np.mean(null_hits >= hits_at_vabs)
print(f"\nempirical/均勻 null: 289.76 命中 {hits_at_vabs}/{n}, 均勻 null P(≥)={p_null:.4g}")
ck("C1 289.76 命中 vs 均勻 null < 0.01", p_null < 0.01, f"p={p_null:.4g}")

data = {"n": n, "dv_abs": sorted(dv_abs.tolist()),
        "hits_curve": {"wins": wins.tolist(), "hits": hits.tolist()},
        "peak_w": float(peak_w), "peak_n": int(peak_n),
        "hits_at_vabs": int(hits_at_vabs), "upper95": float(upper5),
        "null_uniform_p": float(p_null),
        "blue_n": len(blue), "red_n": len(red),
        "blue_z": float(np.mean(zb)) if zb else None,
        "red_z": float(np.mean(zr)) if zr else None,
        "checks": [{"name": x, "pass": p, "detail": d} for x,p,d in LOG]}
with open(f"{DATA}/14_position_empirical_null.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/14_position_empirical_null.json")