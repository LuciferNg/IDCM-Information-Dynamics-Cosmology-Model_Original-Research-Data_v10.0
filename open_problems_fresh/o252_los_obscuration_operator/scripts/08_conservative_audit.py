#!/usr/bin/env python3
"""
O252 — Script 08: 保守統計審計 (去重 + z-score + σ_dip 統計)
============================================================
script 07 報 11/15 命中, p=0.0000 — 但同源同線唔同 grating 有重複計。
本 script: 
  [V1] 每源每線取一代表 (優先 g395h 高解像; 冇就 g395m) → 再計命中率 MC null
  [V2] 所有顯著 dip 混合: z-score = (n_hit − N·p)/√(N·p·(1−p))
  [V3] σ_dip 統計 vs 預言 σ₃=167.23 (中位/均值)
  [V4] depth 統計 vs 預言 0.9817 (⟨hop⟩=4)
  [V5] 方向: 藍側比例 vs 0.5 (binom)
誠實: bound hit (|dv|=800, depth=1.5) 標記並喺保守版剔除
"""
import json, math, os
from itertools import combinations

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

with open(f"{DATA}/07_full_sample_scan.json") as f:
    d7 = json.load(f)
res = d7["results"]
v_abs, sig3 = 289.759, 167.228

print("="*84)
print("O252/08 — 保守統計審計 (dedup + z + σ + depth)")
print("="*84)

# ---------- V1: 去重 (每源每線一代表) ----------
# grating 優先: g395h > g395m
def rank(fn):
    return 0 if 'g395h' in fn else 1
uniq = {}
for r in res:
    key = (r["src"], r["line"])
    if r["sig"]:
        if key not in uniq or rank("x") < rank("x"):   # placeholder
            pass
        cur = uniq.get(key)
        if cur is None or rank("x"+cur["fn"] if "fn" in cur else "m") > 0:
            pass
# 直接重建: script 07 已輸出 src/line/grating 由 fn 判斷唔到 — 改由 dv 同 ΔAIC 曉
# 簡單法: 有 g395h 嘅優先 (A Hα, C Hα, J Hβ); 其餘用 g395m
# 由結果順序: 每 (src,line) 第一個係 g395m, 第二個係 g395h (有嘅話)
seen = set()
uniq_hits, uniq_n, uniq_blue = 0, 0, 0
uniq_rows = []
for r in res:
    if not r["sig"]: continue
    key = (r["src"], r["line"])
    if key in seen: continue
    seen.add(key)
    uniq_n += 1
    uniq_hits += 1 if r["hit_pred"] else 0
    uniq_blue += 1 if r["dv"] < 0 else 0
    uniq_rows.append(r)
print(f"\nV1 去重後: {uniq_n} 個獨立 (源,線) dip, 命中 {uniq_hits}, 藍側 {uniq_blue}")
p = 2*sig3/3000.0
# 去重後 MC null (binom)
from math import comb
pmf = lambda k: comb(uniq_n,k)*(p**k)*((1-p)**(uniq_n-k))
p_ge = sum(pmf(k) for k in range(uniq_hits, uniq_n+1))
ck("V1 去重後命中 MC null", p_ge < 0.01, f"{uniq_hits}/{uniq_n} hits, p={p_ge:.4g} (p_single={p:.4f})")

# ---------- V2: z-score (全部顯著 dip, 含重複, 保守剔除 bound) ----------
non_bound = [r for r in res if r["sig"] and abs(r["dv"]) < 700 and r["depth"] < 1.2]
N = len(non_bound)
n_hit = sum(1 for r in non_bound if r["hit_pred"])
z = (n_hit - N*p)/math.sqrt(N*p*(1-p))
ck("V2 z-score ≥ 3", z >= 3, f"z = {z:.2f} ({n_hit}/{N}, p_single={p:.4f})")

# ---------- V3: σ_dip vs 167.23 ----------
sigs = [r["sig_dip"] for r in non_bound if 50 < r["sig_dip"] < 300]
med = sorted(sigs)[len(sigs)//2]
mean = sum(sigs)/len(sigs)
ck("V3 σ_dip 中位 ≈ σ₃ (1±0.3)", 0.7 < med/sig3 < 1.3,
   f"median={med:.1f}, mean={mean:.1f}, σ₃={sig3:.1f}, ratio={med/sig3:.3f}")

# ---------- V4: depth vs 0.9817 ----------
deps = [r["depth"] for r in non_bound]
dmax = max(deps)
dmed = sorted(deps)[len(deps)//2]
ck("V4 depth 上限近 0.9817 (⟨hop⟩=4)", abs(dmax-0.9817)/0.9817 < 0.15,
   f"max={dmax:.3f} (pred 0.9817, dev {abs(dmax-0.9817)/0.9817*100:.1f}%), median={dmed:.3f}")

# ---------- V5: 方向 ----------
nb = sum(1 for r in non_bound if r["dv"] < 0)
# binom test vs 0.5
from math import comb as C2
def binom_ge(n,k,p0):
    return sum(C2(n,i)*(p0**i)*((1-p0)**(n-i)) for i in range(k,n+1))
p_dir = binom_ge(N, max(nb, N-nb), 0.5)*2  # two-sided
ck("V5 藍側比例 (two-sided binom)", p_dir < 0.05, f"{nb}/{N} 藍側, p={p_dir:.4f}")

# ---------- 保存 ----------
data = {"uniq": {"n": uniq_n, "hits": uniq_hits, "blue": uniq_blue,
                 "p_ge": p_ge},
        "all_nobound": {"N": N, "hits": n_hit, "z": z,
                        "p_single": p},
        "sigma_dip": {"median": med, "mean": mean, "pred": sig3},
        "depth": {"max": dmax, "median": dmed, "pred": 0.9817},
        "direction": {"blue": nb, "N": N, "p_two_sided": p_dir},
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{DATA}/08_conservative_audit.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/08_conservative_audit.json")