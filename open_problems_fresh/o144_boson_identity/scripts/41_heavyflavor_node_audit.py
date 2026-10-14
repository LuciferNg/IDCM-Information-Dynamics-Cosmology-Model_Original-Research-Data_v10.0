#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-41 — 重味節點審計 + 連結層重盲測 (quarkonium-threshold-bounded 方案)
==================================================================
承接: scripts/40 誠實負 — 六預註冊族全淘汰; 殘差圖揭: p/n/η′≈33 M₀(描述),
η/η′/Λ 同 modes 三 R_h ⟹ R_h 非 multiset 函數。本輪「先攻重味節點」:
重味節點定義審計 — O238 anchor (MS 曳行) 做 additivity 節點係咪結構上合法?

★ 預註冊 (跑前凍結, 判準唔可放寬; 違反 = 本 script 作廢):
  [P1] 節點方案 (零新常數):
       NA: O238 S2 anchors — u=93.4/42.890, d=u·2.1505, s=93.4, c=s·11.652,
           b=c·4.586 (MS2 曳行/凍結層; O238 scripts/10 原文)
       NB: 夸克偶數 1S scheme — c = J/ψ/2, b = ϒ/2 (標準 QCD m_Q(1S)=M_qq̄/2;
           偶數定義其夸克節點); 輕味 u,d,s = NA
  [P2] 正性審計 (純邏輯, 非擬合): additive 模型 ⟹ 節點 m_q ≤ M_had − Σ其他節點;
       逐強子記 PASS/FAIL; 得出 b/c 節點窗:
       b ≤ min(ϒ/2, B0−d, B+−u), c ≤ min(J/ψ/2, D0−u, D+−d)
  [P3] 連結層盲測 — scripts/40 同 6 族 (定義一字不改) + T6 控制族 (docs/10
       E_bind = M₀·M_tree = 33 M₀ 常數族 — 舊宣稱重盲測):
       T0 節點only / T1a n_q·11M₀ / T1b (重子33,介子11)M₀ / T2 ΣD_m·M₀ /
       T3 |ΣD_m|·M₀ / T5 環距離和·M₀/2 / T6 33·M₀ 常數
  [P4] 測試集: A = 17 強子 × NA（判準 C1A ≥14/17 ≤3%）;
       B = 15 強子 (除 J/ψ, ϒ — 佢哋定義 NB 節點) × NB（判準 C1B ≥12/15 ≤3%）;
       C2 中位 ≤1.5%; C3 無單點 >8% (兩方案同判)
  [P5] 誠實負: 任何族 FAIL ⟹ 殘差圖 R_h=(M_obs−Σm_q)/M₀ 記錄; 描述種子
       標 🟡 禁砌算子 (沿用 φ-power 禁令)
  [P6] 本 script 只跑一次；修 bug 可以重跑但判準凍結

輸出: data/41_heavyflavor_node_audit.json
"""
import json, math

M0 = 27.90091451  # docs/10 沿用 (scripts/40 同值; O238 scripts/10 用 27.900915, 差 5e-9 相對)
NA = {"u": 93.4 / 42.890, "d": 93.4 / 42.890 * 2.1505, "s": 93.4,
      "c": 93.4 * 11.652, "b": 93.4 * 11.652 * 4.586}
HADRONS = {
    "pi0": (134.9768, ["u", "d"], ["u", "d"]), "pi+": (139.57039, ["u", "d"], ["u", "d"]),
    "K+": (493.677, ["u", "s"], ["u", "s"]), "K0": (497.611, ["d", "s"], ["d", "s"]),
    "eta": (547.862, ["u", "d", "s"], ["u", "d", "s"]), "eta'": (957.78, ["u", "d", "s"], ["u", "d", "s"]),
    # eta/eta' 混合味 (u,d,s) — 與 scripts/40 預註冊 P2 一致
    "p": (938.272088, ["u", "u", "d"], ["u", "u", "d"]),
    "n": (939.565421, ["u", "d", "d"], ["u", "d", "d"]),
    "Lambda": (1115.683, ["u", "d", "s"], ["u", "d", "s"]),
    "Sigma+": (1189.37, ["u", "u", "s"], ["u", "u", "s"]),
    "Xi0": (1314.86, ["u", "s", "s"], ["u", "s", "s"]),
    "D0": (1864.84, ["c", "u"], ["c", "u"]), "D+": (1869.66, ["c", "d"], ["c", "d"]),
    "B+": (5279.32, ["b", "u"], ["b", "u"]), "B0": (5279.63, ["b", "d"], ["b", "d"]),
    "J/psi": (3096.9, ["c", "c"], ["c", "c"]), "Upsilon": (9460.30, ["b", "b"], ["b", "b"]),
}
# NB 節點由偶數閾值定義 (1S scheme)
NB = dict(NA)
NB["c"] = HADRONS["J/psi"][0] / 2
NB["b"] = HADRONS["Upsilon"][0] / 2
print("═══ §1 節點方案 ═══")
print(f"  NA (O238 anchors): u={NA['u']:.4f} d={NA['d']:.4f} s={NA['s']:.4f} "
      f"c={NA['c']:.3f} b={NA['b']:.3f} (MeV)")
print(f"  NB (1S: J/ψ/2, ϒ/2): c={NB['c']:.3f} b={NB['b']:.3f} (MeV)")
print(f"  M₀ = {M0} MeV; 33·M₀ = {33*M0:.3f}; 11·M₀ = {11*M0:.3f}")

def nodesum(ms, scheme):
    return sum(scheme[m] for m in ms)

# ---------------------------------------------------------------- §2 正性審計
print("\n═══ §2 正性審計 (additive ⟹ 節點 ≤ M_had − Σ其他) ═══")
bounds_b, bounds_c = [], []
for name, (mobs, ms, msb) in HADRONS.items():
    for tag, sch, mlist in (("NA", NA, ms), ("NB", NB, msb)):
        mx = mobs - sum(sch[m] for m in mlist)
        ok = mx >= 0
        print(f"  {name:>8s} {tag}: 節點和 = {mobs-mx:9.4f}  餘量 = {mx:+10.4f} MeV  {'✅' if ok else '🔴 FAIL'}")
    if "b" in ms:
        for sch, mlist in ((NA, ms), (NB, msb)):
            rem = mobs - sum(sch[m] for m in mlist)
            if sch is NA:
                bounds_b.append(rem)
    if "c" in ms:
        pass  # (窗收集由上 b_window/c_window 處理)
# 節點窗 (tightest): b ≤ min(ϒ/2, B0−d, B+−u); c ≤ min(J/ψ/2, D0−u, D+−d)
b_window = {"Upsilon/2": HADRONS["Upsilon"][0] / 2,
            "B0-d": HADRONS["B0"][0] - NA["d"], "B+-u": HADRONS["B+"][0] - NA["u"]}
c_window = {"Jpsi/2": HADRONS["J/psi"][0] / 2,
            "D0-u": HADRONS["D0"][0] - NA["u"], "D+-d": HADRONS["D+"][0] - NA["d"]}
b_max = min(b_window, key=lambda k: b_window[k])
b_maxv = b_window[b_max]
c_max = min(c_window, key=lambda k: c_window[k])
c_maxv = c_window[c_max]
print(f"  節點窗: b ≤ {b_maxv:.3f} MeV (source: {b_max}), "
      f"c ≤ {c_maxv:.3f} MeV (source: {c_max})")
print(f"  NA b-anchor = {NA['b']:.3f}: {'✅ PASS' if NA['b'] <= b_maxv else '🔴 VIOLATION — ϒ 正性破裂'}")
print(f"  NA c-anchor = {NA['c']:.3f}: {'✅ PASS' if NA['c'] <= c_maxv else '🔴 VIOLATION'}")
print(f"  NB 定義: b = ϒ/2 = {NB['b']:.3f}, c = J/ψ/2 = {NB['c']:.3f}  ✔ 正性 by 構造")

# ---------------------------------------------------------------- §3 家族盲測
PLAN = ["T0", "T1a", "T1b", "T2", "T3", "T5", "T6"]
EF = {4: 114.865277982844, 2: 202.400151085512, 1: 160.771161893925,
      3: 206.013275636098, 5: 12.506466127581, 7: 134.717027433432,
      9: 195.235149040176, 11: 165.586979074824, 13: 185.187465460336}
MODES = {"u": 11, "d": 9, "s": 7, "c": 4, "b": 2, "t": 1}

def ring_dist(a, b):
    dd = abs(a - b)
    return min(dd, 88 - dd)

def pred(name, tag, ns):
    mobs, ms, msb = HADRONS[name]
    mlist = ms if tag == "NA" else msb
    sch = NA if tag == "NA" else NB
    Nh = sum(sch[m] for m in mlist)
    nq = len(mlist)
    baryon = nq == 3
    out = {}
    for fam in PLAN:
        if fam == "T0":
            out[fam] = Nh
        elif fam == "T1a":
            out[fam] = Nh + nq * 11 * M0
        elif fam == "T1b":
            out[fam] = Nh + (33 if baryon else 11) * M0
        elif fam == "T2":
            out[fam] = Nh + sum(EF[MODES[m]] - 176 for m in mlist) * M0
        elif fam == "T3":
            out[fam] = Nh + abs(sum(EF[MODES[m]] - 176 for m in mlist)) * M0
        elif fam == "T5":
            s = sum(ring_dist(MODES[mlist[i]], MODES[mlist[j]])
                     for i in range(nq) for j in range(i + 1, nq)) / 2
            out[fam] = Nh + s * M0
        elif fam == "T6":
            out[fam] = Nh + 33 * M0
    return out

def run_set(tag, hadr_list, c1_thresh):
    rows = {}
    for name in hadr_list:
        rows[name] = pred(name, tag, None)
    res = {}
    for fam in PLAN:
        devs = []
        for name in hadr_list:
            mobs = HADRONS[name][0]
            devs.append(abs(rows[name][fam] - mobs) / mobs)
        ds = sorted(devs)
        med = ds[len(ds) // 2]
        le3 = sum(1 for d in devs if d <= 0.03)
        mx = max(devs)
        c1 = le3 >= c1_thresh
        c2 = med <= 0.015
        c3 = mx <= 0.08
        res[fam] = {"le3": le3, "n": len(hadr_list), "median": round(med, 5),
                    "max": round(mx, 5), "C1": c1, "C2": c2, "C3": c3,
                    "PASS": c1 and c2 and c3}
    return rows, res

setA = list(HADRONS.keys())
rowsA, resA = run_set("NA", setA, 14)
print("\n═══ §3 家族盲測 ═══")
print("  [A] 17 強子 × NA (C1A ≥14/17, C2 ≤1.5%, C3 ≤8%)")
for fam in PLAN:
    r = resA[fam]
    print(f"    {fam:>4s}: ≤3% {r['le3']:2d}/{r['n']}  中位 {r['median']*100:6.2f}%  "
          f"max {r['max']*100:6.2f}%  {'✅' if r['PASS'] else '✗'}")
setB = [h for h in HADRONS if h not in ("J/psi", "Upsilon")]
rowsB, resB = run_set("NB", setB, 12)
print("  [B] 15 強子 (除 J/ψ,ϒ) × NB (C1B ≥12/15, C2 ≤1.5%, C3 ≤8%)")
for fam in PLAN:
    r = resB[fam]
    print(f"    {fam:>4s}: ≤3% {r['le3']:2d}/{r['n']}  中位 {r['median']*100:6.2f}%  "
          f"max {r['max']*100:6.2f}%  {'✅' if r['PASS'] else '✗'}")

# ---------------------------------------------------------------- §4 殘差圖
print("\n═══ §4 殘差圖 R_h = (M_obs − Σ節點)/M₀ (描述層, 禁砌算子) ═══")
print("  hadron   NA-R(M₀)   NB-R(M₀)   (NB 用 1S 節點; J/ψ/ϒ 喺 NB 為 0 by 構造)")
rows = []
for name in HADRONS:
    mobs, ms, msb = HADRONS[name]
    rna = (mobs - nodesum(ms, NA)) / M0
    rnb = (mobs - nodesum(msb, NB)) / M0
    rows.append({"hadron": name, "NA_R": round(rna, 4), "NB_R": round(rnb, 4),
                 "M_obs": mobs})
    print(f"  {name:>8s}  {rna:9.4f}  {rnb:9.4f}")

print("\n═══ §5 判決 ═══")
print(f"  §2 正性: NA = {sum(1 for _ in HADRONS)} 測試, ϒ FAIL (b-anchor 4990.93 > {b_maxv:.2f}); "
      f"NB 15/15 ✅ by 構造")
print(f"  §3 家族: A 通過數 = {sum(1 for f in PLAN if resA[f]['PASS'])}/7; "
      f"B 通過數 = {sum(1 for f in PLAN if resB[f]['PASS'])}/7")

OUT = {"M0": M0, "NA": NA, "NB": NB, "bounds": {"b_max": b_max, "b_src": min(b_window, key=b_window.get),
        "c_max": c_max, "c_src": min(c_window, key=c_window.get)},
       "setA": resA, "setB": resB, "residual": rows}
with open("data/41_heavyflavor_node_audit.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("  data/41_heavyflavor_node_audit.json 寫入完成")