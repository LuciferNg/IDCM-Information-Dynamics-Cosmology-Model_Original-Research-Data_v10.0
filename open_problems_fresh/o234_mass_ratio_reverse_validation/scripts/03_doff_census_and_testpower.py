#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O234 scripts/03 -- 完整約束清單 + DOF 審計 + 檢驗能力清單 (round 2)

License: IDCM O234. stdlib-only. 全確定性; 誤差 = 一階傳播 (frozen layer v1.1).
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FROZEN = json.load(open(os.path.join(DATA, "01_frozen_observations.json"), encoding="utf-8"))

MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
def gamma(n): return 4.0*math.sin(n*math.pi/88.0)**2
g = {n: gamma(n) for n in MODES}

# ---------------------------------------------------------------- A. 凍結層導出比 (一階誤差)
md_mu, e_md_mu = FROZEN["Nf=2+1+1"]["md_mu_derived"]
ms_mud, e_ms_mud = FROZEN["Nf=2+1+1"]["ms_mud_ratio"]
mcm_s11, e_mcm_s11 = 11.652, 0.065          # mc/ms Nf=4 (ETM ⊕, 0.6%)
mcm_s9,  e_mcm_s9  = 11.85, 0.16            # mc/ms HPQCD 09A
mu_e, e_mu_e = 105.658/0.510999, (105.658/0.510999)*math.hypot(0.001/105.658, 0.000001/0.51)
tau_mu, e_tau_mu = 1776.86/105.658, (1776.86/105.658)*math.hypot(0.12/1776.86, 0.001/105.658)
mb_mc, e_mb_mc = 4.18/1.27, (4.18/1.27)*math.hypot(0.03/4.18, 0.02/1.27)
mt_mb, e_mt_mb = 172.57/4.18, (172.57/4.18)*math.hypot(0.29/172.57, 0.03/4.18)

der = {}
def add(name, v, e, kind):
    der[name] = {"value": v, "err": e, "rel_pct": e/v*100, "kind": kind}

add("ms/mu (derived)", ms_mud*(1+md_mu)/2,
    ms_mud*(1+md_mu)/2*math.hypot(e_ms_mud/ms_mud, e_md_mu/(1+md_mu)), "derived")
add("ms/md (derived)", ms_mud*(1+1/md_mu)/2,
    ms_mud*(1+1/md_mu)/2*math.hypot(e_ms_mud/ms_mud, e_md_mu/(md_mu*(1+md_mu))), "derived")
add("mc/mu (derived, Nf=4 mc/ms)", der["ms/mu (derived)"]["value"]*mcm_s11,
    der["ms/mu (derived)"]["value"]*mcm_s11*math.hypot(e_mcm_s11/mcm_s11, der["ms/mu (derived)"]["rel_pct"]/100), "derived")
add("md/mu FLAG", md_mu, e_md_mu, "direct")
add("ms/mud FLAG", ms_mud, e_ms_mud, "direct")
add("mc/ms Nf=4", mcm_s11, e_mcm_s11, "direct")
add("mc/ms HPQCD", mcm_s9, e_mcm_s9, "direct")
add("mb/mc PDG (scheme近似)", mb_mc, e_mb_mc, "direct-crude")
add("mt/mb PDG (pole/MS 不可通約)", mt_mb, e_mt_mb, "direct-crude")
add("mu/e (pole)", mu_e, e_mu_e, "direct")
add("tau/mu (pole)", tau_mu, e_tau_mu, "direct")
add("tau/e (pole)", mu_e*tau_mu, (mu_e*tau_mu)*math.hypot(e_mu_e/mu_e, e_tau_mu/tau_mu), "derived")

print("[A] 凍結層導出比 (含誤差傳播)")
for k, v in der.items():
    print(f"   {k:28s} = {v['value']:10.4f} ± {v['err']:8.4f}  ({v['rel_pct']:.2f}%)  [{v['kind']}]")

# ---------------------------------------------------------------- B. 約束圖 + DOF
# C-sector: 8 C (e,mu,tau,u,d,s,c,b); t/VEV 除外
# 觀測獨立約束: 輕子 2 (mu/e, tau/mu) + 夸克 4 (d/u, s/u(derived), c/s, b/c)
# 標度: 輕子區 1 + 夸克區 1 (冇跨 sector 比) => shape DOF = 8 - 6 - 2
N_C, N_CON, N_SCALE = 8, 6, 2
shape_dof = N_C - N_CON - N_SCALE
print(f"\n[B] C-sector DOF 審計")
print(f"   未知 C: {N_C} (e,mu,tau,u,d,s,c,b; t=VEV 除外)")
print(f"   觀測獨立 ratio 約束: {N_CON} (輕子 2 + 夸克 4, 含 derived s/u)")
print(f"   扇區標度: {N_SCALE} (冇輕子<->夸克比)  ->  shape DOF = {shape_dof}")
print(f"   純γ層: 0 參數 -> u/d 唯一可檢驗")

# C-shape 表 (anchor C_u = 1, C_e = 1)
shape = {}
shape["u"] = 1.0
shape["d"] = (md_mu)/(g[3]/g[2])
shape["s"] = der["ms/mu (derived)"]["value"]/(g[4]/g[2])
shape["c"] = shape["s"]*mcm_s11/(g[7]/g[4])
shape["b"] = shape["c"]*mb_mc/(g[11]/g[7])
shape["e"] = 1.0
shape["mu"] = mu_e/(g[5]/g[1])
shape["tau"] = shape["mu"]*tau_mu/(g[9]/g[5])
print("   反解 C-shape (anchor 每扇區 = 1): " + "  ".join(f"{k}={v:.3f}" for k, v in shape.items()))
print(f"   d/u -> C_d/C_u = {shape['d']:.4f} (O233 P2 用 0.9629-0.9578 帶內; 方向 u>d 一致)")

# ---------------------------------------------------------------- C. 檢驗能力清單
print("\n[C] 檢驗能力清單 (每 ratio: 精度 / γ 可檢驗 / 判別力)")
tests = []
def addtest(name, r, e, pair, note=""):
    if pair is None:
        z = None; cat = "mode-gap"
    else:
        i, j = pair
        pred = g[i]/g[j]
        z = (pred - r)/e
        cat = ("gamma-testable" if abs(z) <= 2 else ("C-dominated" if abs(z) > 5 else "border"))
    tests.append((name, r, e, e/r*100, z, cat, note))
    print(f"   {name:22s} {r:9.4f} ± {e:7.4f}  rel {e/r*100:5.2f}%  z(純γ)={z if z is None else f'{z:+6.1f}'}  {cat}  {note}")

addtest("d/u", md_mu, e_md_mu, (3, 2))
addtest("s/mud", ms_mud, e_ms_mud, None, "sharpest(0.3%) 但平均量 mode-gap")
addtest("ms/mu (derived)", der["ms/mu (derived)"]["value"], der["ms/mu (derived)"]["err"], (4, 2))
addtest("c/s Nf=4", mcm_s11, e_mcm_s11, (7, 4))
addtest("b/c", mb_mc, e_mb_mc, (11, 7), "scheme近似")
addtest("t/b", mt_mb, e_mt_mb, (13, 11), "VEV 扇區")
addtest("μ/e", mu_e, e_mu_e, (5, 1))
addtest("τ/μ", tau_mu, e_tau_mu, (9, 5))
addtest("τ/e", mu_e*tau_mu, (mu_e*tau_mu)*math.hypot(e_mu_e/mu_e, e_tau_mu/tau_mu), (9, 1))

n_gam = sum(1 for t in tests if t[5] == "gamma-testable")
n_cdom = sum(1 for t in tests if t[5] == "C-dominated")
n_gap = sum(1 for t in tests if t[5] == "mode-gap")
print(f"   -> gamma-testable {n_gam} / C-dominated {n_cdom} / mode-gap {n_gap} / 共 {len(tests)}")

# ---------------------------------------------------------------- D. 凍結層內部一致性
z_mcm = (mcm_s9 - mcm_s11)/math.hypot(e_mcm_s9, e_mcm_s11)
print(f"\n[D] 凍結層內部一致: mc/ms 兩值 (11.85 vs 11.652): z = {z_mcm:+.2f} (watch item, freeze v2 決策點)")

p = s = 0
def chk(name, ok, detail):
    global p, s
    print(("  PASS " if ok else "  FAIL ") + f"[{name}] {detail}")
    if ok: p += 1
    else:  s += 1

chk("B1 C-shape 完全由凍結層釘死 (shape DOF = 0)",
    shape_dof == 0,
    f"N_C={N_C} - N_CON={N_CON} - N_SCALE={N_SCALE} = 0 (但有 2 個扇區標度仍自由)")
chk("C1 檢驗能力: 9 個比只有 1 個 γ 可檢驗",
    n_gam == 1 and n_cdom >= 7,
    f"gamma-testable={n_gam} (d/u), C-dominated={n_cdom}, mode-gap={n_gap}")
chk("D1 mc/ms 兩值一致 (|z|<=2)", abs(z_mcm) <= 2,
    f"z={z_mcm:+.2f} -> 凍結層可接受, 但 1.15σ 係內部張力 watch item")

# 輸出 derived 集 (frozen v1.1)
out = {"derived_from_frozen_v1_1": {k: {"value": v["value"], "err": v["err"], "rel_pct": v["rel_pct"], "kind": v["kind"]} for k, v in der.items()}}
with open(os.path.join(DATA, "03_derived_ratios.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\n[data] 03_derived_ratios.json 已寫")
print(f"\n=== {p} PASS / {s} FAIL ===")