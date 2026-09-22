#!/usr/bin/env python3
"""
O136 — Script 15: 拍頻表公式完整驗證 (含 φ 因子)
================================================================
核對 beat_periodic_table/data/07_physics_mapping.json 的所有公式,
用完整形式 (含 φ-power 因子), 而非純 sin 比。
"""
import math, json
from pathlib import Path

phi = (1 + math.sqrt(5))/2
B_ = 4
Nd = 44
S = lambda x: math.sin(math.pi * x / 176)
w = lambda n: 2 * math.sin(math.pi * n / 88)

print("=" * 88)
print("O136 Script 15: 拍頻表公式完整驗證 (含 φ 因子)")
print("=" * 88)

# PDG 參考
PDG = {
    "u/d": 2.16/4.67,
    "c/s": 1270.0/93.0,
    "t/b": 172760.0/4180.0,
    "c/b": 1270.0/4180.0,
    "s/d": 93.0/4.67,
    "W/Z": 80.377/91.1876,
    "H/W": 125.25/80.377,
    "mu/tau": 105.658/1776.86,
}

# 拍頻表 mapping (完整公式)
print(f"\n{'─'*88}")
print("1. 完整公式驗證")
print(f"{'─'*88}")

results = []

# 1. u/d
n, m = 10, 24
pred = math.sin(n*math.pi/88)/math.sin(m*math.pi/88)
obs = PDG["u/d"]
dev = (pred-obs)/obs*100
results.append(("u/d", "(10,24)", "sin10/sin24", pred, obs, dev, "O34 ✅ 0.026%"))

# 2. t/b (含 φ 因子)
n, m = 19, 33
exp_ = 2*B_ + 71/132
pred = phi**exp_ * math.sin(n*math.pi/88)/math.sin(m*math.pi/88)
obs = PDG["t/b"]
dev = (pred-obs)/obs*100
results.append(("t/b", "(19,33)", f"φ^{exp_:.5f}·sin19/sin33", pred, obs, dev, "O34 ✅ 0.005%"))

# 3. c/b
n, m = 8, 33
pred = math.sin(n*math.pi/88)/math.sin(m*math.pi/88)
obs = PDG["c/b"]
dev = (pred-obs)/obs*100
results.append(("c/b", "(8,33)", "sin8/sin33", pred, obs, dev, "O34 ✅ 0.368%"))

# 4. c/s (測試多種解讀)
n, m = 8, 22
pred_sin = math.sin(n*math.pi/88)/math.sin(m*math.pi/88)
results.append(("c/s (sin8/sin22)", "(8,22)", "sin8/sin22", pred_sin, PDG["c/s"], 
                (pred_sin-PDG["c/s"])/PDG["c/s"]*100, "O34 ✅ 0.368% (?)"))
# 反向
pred_inv = 1/pred_sin
results.append(("c/s (sin22/sin8)", "(8,22)", "sin22/sin8", pred_inv, PDG["c/s"],
                (pred_inv-PDG["c/s"])/PDG["c/s"]*100, "?"))
# 加 φ 因子?
for e_try in [2*B_+71/132, 2*B_, 12]:
    p2 = phi**e_try * pred_sin
    results.append((f"c/s (φ^{e_try:.4f}·sin8/sin22)", "(8,22)", f"φ^{e_try:.4f}·sin8/sin22",
                    p2, PDG["c/s"], (p2-PDG["c/s"])/PDG["c/s"]*100, "試探"))

# 5. s/d (含 φ 因子)
n, m = 1, 22
exp_ = 10/528
pred = phi**exp_ * math.sin(m*math.pi/88)/math.sin(n*math.pi/88)
obs = PDG["s/d"]
dev = (pred-obs)/obs*100
results.append(("s/d", "(1,22)", f"φ^{exp_:.6f}·sin22/sin1", pred, obs, dev, "O35 ✅ 0.037%"))

# 6. W/Z
n, m = 30, 41
pred = math.sin(n*math.pi/88)/math.sin(m*math.pi/88)
obs = PDG["W/Z"]
dev = (pred-obs)/obs*100
results.append(("W/Z", "(30,41)", "sin30/sin41", pred, obs, dev, "O34 ✅ 0.146%"))

# 7. H/W
n, m = 38, 19
pred = math.sin(n*math.pi/88)/math.sin(m*math.pi/88)
obs = PDG["H/W"]
dev = (pred-obs)/obs*100
results.append(("H/W", "(19,38)", "sin38/sin19", pred, obs, dev, "O34 ✅ 0.064%"))

# 8. mu/tau
n, m = 1, 18
pred = math.sin(n*math.pi/88)/math.sin(m*math.pi/88)
obs = PDG["mu/tau"]
dev = (pred-obs)/obs*100
results.append(("mu/tau", "(1,18)", "sin1/sin18", pred, obs, dev, "O34 ✅ 0.165%"))

print(f"\n{'物理':>22} {'pair':>9} {'公式':>22} {'預言':>11} {'PDG':>11} {'偏差':>9} {'聲稱':>16}")
print("-" * 105)
for name, pair, formula, pred, obs, dev, claim in results:
    mark = "✅" if abs(dev) < 0.5 else ("🟡" if abs(dev) < 2 else "🔴")
    print(f"{name:>22} {pair:>9} {formula:>22} {pred:>11.5f} {obs:>11.5f} {dev:>8.3f}%{mark} {claim:>16}")

# ═══ 2. 總結 ═══
print(f"\n{'─'*88}")
print("2. 總結")
print(f"{'─'*88}")

ok = [(n,d) for n,_,_,_,_,d,_ in results if abs(d) < 0.5]
print(f"\n驗證通過 (<0.5%): {len(ok)} 項")
for n, d in ok:
    print(f"  {n:>22}: {d:>7.3f}%")

fail = [(n,d) for n,_,_,_,_,d,_ in results if abs(d) >= 0.5]
print(f"\n未通過 (≥0.5%): {len(fail)} 項")
for n, d in fail:
    print(f"  {n:>22}: {d:>7.3f}%")

# ═══ 3. 對比 O136 P_f 框架 ═══
print(f"\n{'─'*88}")
print("3. 對比: 拍頻表 vs O136 P_f 框架 (同一質量比)")
print(f"{'─'*88}")

phi_inv = 1/phi
gamma = lambda n: 4*math.sin(n*math.pi/88)**2
M0 = 27.900915

# 共同可比項
common = [
    ("u/d", PDG["u/d"], math.sin(10*math.pi/88)/math.sin(24*math.pi/88),
     (M0*gamma(1)*(31/2))/(M0*gamma(1)*33)),
    ("c/b", PDG["c/b"], math.sin(8*math.pi/88)/math.sin(33*math.pi/88),
     (M0*gamma(34)*13)/(M0*gamma(33)*44)),
    ("mu/tau", PDG["mu/tau"], math.sin(1*math.pi/88)/math.sin(18*math.pi/88),
     (M0*gamma(7)*(31/2))/(M0*gamma(20)*37)),
    ("H/W", PDG["H/W"], math.sin(38*math.pi/88)/math.sin(19*math.pi/88), None),
    ("W/Z", PDG["W/Z"], math.sin(30*math.pi/88)/math.sin(41*math.pi/88), None),
]
print(f"\n{'比值':>8} {'PDG':>11} {'拍頻表':>11} {'偏差':>9} {'O136 P_f':>11} {'偏差':>9} {'勝方':>8}")
print("-" * 74)
for label, obs, bt_pred, pf_pred in common:
    bt_dev = (bt_pred-obs)/obs*100
    if pf_pred:
        pf_dev = (pf_pred-obs)/obs*100
        winner = "拍頻表" if abs(bt_dev) < abs(pf_dev) else "O136"
        print(f"{label:>8} {obs:>11.5f} {bt_pred:>11.5f} {bt_dev:>8.3f}% {pf_pred:>11.5f} {pf_dev:>8.3f}% {winner:>8}")
    else:
        print(f"{label:>8} {obs:>11.5f} {bt_pred:>11.5f} {bt_dev:>8.3f}% {'—':>11} {'—':>9} {'拍頻表':>8}")

# ═══ 4. 密度效應檢驗 ═══
print(f"\n{'─'*88}")
print("4. 密度效應檢驗: 946 個拍頻中有多少能匹配 u/d?")
print(f"{'─'*88}")

obs_ud = PDG["u/d"]
hits = []
for n in range(1, 45):
    for m in range(n+1, 45):
        r = math.sin(n*math.pi/88)/math.sin(m*math.pi/88)
        dev = abs(r-obs_ud)/obs_ud*100
        if dev < 0.5:
            hits.append((n, m, r, dev))
print(f"\nu/d = {obs_ud:.5f} 的匹配 (sin 比, <0.5%): {len(hits)} 個")
for n, m, r, dev in sorted(hits, key=lambda x: x[3])[:10]:
    d_, s_ = m-n, m+n
    print(f"  ({n:>2},{m:>2}) d={d_:>2} s={s_:>2}  ratio={r:.5f}  dev={dev:.3f}%")

print(f"\n→ 946 個拍頻, {len(hits)} 個在 0.5% 內 → 密度效應 {'顯著' if len(hits)>5 else '不顯著'}")

# 保存
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "15_beat_table_full_verify.json", "w") as f:
    json.dump({
        "verified": [{"name": n, "pair": p, "formula": fm, "pred": float(pr), 
                      "obs": float(o), "dev_pct": float(d), "claim": c}
                     for n,p,fm,pr,o,d,c in results],
        "n_pass_0p5": len(ok),
        "n_fail": len(fail),
        "ud_density_hits": len(hits),
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/15_beat_table_full_verify.json")