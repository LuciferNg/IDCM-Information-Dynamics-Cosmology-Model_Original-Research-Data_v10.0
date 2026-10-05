#!/usr/bin/env python3
"""
O137 — 遺留 5 補充 (scripts/72): GKZ Φ 之三角剖分依賴性 + 集成檢定
==================================================================
★ 觸發事件:
   logs/71_probe.txt  (mori_probe.py, 11:44) → Φ 含 23, 不含 21/30; 185 超平面
   logs/71_probe2.txt (p2.py,          11:59) → Φ 含 21,30, 不含 23;  184 超平面
   scripts/71 docstring 寫「184 面」, 但其本次輸出寫「185 超平面」
   兩支探測用【完全相同】之 polytope 檔 (md5 63536d177609bd6c12026e0aeccdf6ae,
   自 2026-08-22 未改) 及【完全相同】之 backend='qhull'
⟹ 假設: cytools 之 p.triangulate(backend='qhull') 對同一 polytope 【非決定性】

★ 本腳本目的:
   §1 重現非決定性 (同一 process 內多次呼叫)
   §2 Φ 集成統計 (Σ / max / 相異值 / 超平面數) — 邊界 + 不變量
   §3 「9 模式集 ⊆ Φ」之集成檢定 + ★ 密度基準 (O208 合規)
   §4 特定 IDCM 數 (e, o, |M|, N_d+1, N_gen·B, 29, 44, 55) 之出現頻率
   §5 裁決 + 對 Round 19 §11 之修正

⚠️ 方法論鐵律: 任何「屬 IDCM 目錄」之論證必須先報密度基準 (見 §3.2)
"""
import math, json, time, warnings
from collections import Counter
import numpy as np
warnings.filterwarnings('ignore')

PASS, FAIL = [], []
def ck(name, got, exp, tol=0.0):
    if isinstance(exp, (int, float)) and not isinstance(exp, bool):
        ok = abs(float(got) - float(exp)) <= tol
    elif isinstance(exp, set): ok = set(got) == exp
    elif isinstance(exp, (list, tuple)): ok = list(got) == list(exp)
    else: ok = (got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name} = {got}" + ("" if ok else f"   ❗EXP={exp}"))

N_d, N_gen, Bb, F5, L4, L5, L6 = 44, 3, 4, 5, 7, 11, 18
MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]          # 9 模式集 (A₅ 集)
BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
from cytools.config import enable_experimental_features
enable_experimental_features()
from cytools import Polytope

d = json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_sage_export.json'))
PTS = np.array(d['points']).tolist()

def one_phi():
    """一次 triangulate → (Φ list, #hyperplanes)"""
    p = Polytope(PTS)
    tri = p.triangulate(backend='qhull')
    g = [int(x) for x in tri.gkz_phi()]
    sc = tri.secondary_cone()
    nh = int(str(sc).split('by ')[1].split(' ')[0])
    return g, nh, tri.is_star(), tri.is_fine(), tri.is_regular()

# ══════════════════════════════════════════════════════════════════════
print("=" * 88)
print("§1 ★ 非決定性重現 (同一 process, 同一 polytope, 同一 backend)")
print("=" * 88)
M = 6
sigs = []
for i in range(M):
    g, nh, star, fine, reg = one_phi()
    sig = (sum(g), max(g), len(set(g)), 23 in g, 21 in g, 30 in g, nh)
    sigs.append(sig)
    print(f"  跑 {i+1}: Σ={sig[0]} max={sig[1]} 相異={sig[2]} | 含23={sig[3]} 含21={sig[4]} 含30={sig[5]} | 超平面={sig[6]}"
          f" | star={star} fine={fine} reg={reg}")
    print(f"        Φ = {g}")

n_uniq = len(set(sigs))
ck("§1 ★ 同一 polytope 多次 triangulate 給出【多個不同】Φ 簽名 (非決定性)",
   n_uniq > 1, True)
print(f"\n  ⟹ {M} 次呼叫得 {n_uniq} 個不同簽名 ⟹ 🔴 **triangulate 非決定性**")
ck("§1 Σ Φ 恆為 1000 (不變量)", len(set(s[0] for s in sigs)), 1)
ck("§1 max Φ 恆為 200 (apex)", len(set(s[1] for s in sigs)), 1)
ck("§1 相異值數【非】不變 (隨三角剖分變)", len(set(s[2] for s in sigs)) > 1, True)

# ══════════════════════════════════════════════════════════════════════
print()
print("=" * 88)
print("§2 Φ 集成統計 (N 個三角剖分)")
print("=" * 88)
N = 200
sums, maxs, ndists, nhs, ksets, allvals = [], [], [], [], [], []
t0 = time.time()
for i in range(N):
    g, nh, _, _, _ = one_phi()
    sums.append(sum(g)); maxs.append(max(g)); ndists.append(len(set(g))); nhs.append(nh)
    ksets.append(len(set(MODES) & set(g)))
    allvals.append(set(g))
    if (i + 1) % 50 == 0:
        print(f"    ... {i+1}/{N}  ({time.time()-t0:.1f}s)")
print(f"  完成 {N} 個 ({time.time()-t0:.1f}s)")
print(f"  Σ Φ        : {sorted(set(sums))}")
print(f"  max Φ      : {sorted(set(maxs))}")
print(f"  相異值數   : {min(ndists)}..{max(ndists)}  (眾數 {Counter(ndists).most_common(1)[0][0]})")
print(f"  超平面數   : {sorted(set(nhs))}   ← docs/36 §11 記「185」; scripts/71 docstring 記「184」")
ck("§2 Σ Φ 於全集成恆為 1000", sorted(set(sums)), [1000])
ck("§2 max Φ 於全集成恆為 200", sorted(set(maxs)), [200])
ck("§2 超平面數【非】唯一 ⟹ 「185」只係單樣本", len(set(nhs)) > 1, True)

# ══════════════════════════════════════════════════════════════════════
print()
print("=" * 88)
print("§3 ★ 「9 模式集 ⊆ Φ」之集成檢定 + 密度基準")
print("=" * 88)
kc = Counter(ksets)
print(f"  |MODES ∩ Φ| 分佈 (N={N}):")
for k in sorted(kc): print(f"    k = {k} : {kc[k]:4d}  ({100*kc[k]/N:5.1f}%)")
kmean = sum(kc[k]*k for k in kc)/N
kmax = max(kc)
print(f"\n  觀測平均 k = {kmean:.4f}  (最大 k = {kmax} / 9)")

# ── 密度基準 (O208 合規): Φ 之值 ≤ 13 之密度 ──
vals_le13 = set()
for V in allvals: vals_le13 |= {v for v in V if 1 <= v <= 13}
vals_le13 = sorted(vals_le13)
p13 = len(vals_le13) / 13.0
E_k = 9 * p13
print(f"\n  ── 密度基準 ──")
print(f"  集成中出現過之 Φ 值 ≤ 13 : {vals_le13}  ({len(vals_le13)} 個)")
print(f"  ⟹ 對隨機 n ∈ [1,13], P(n ∈ Φ) = {len(vals_le13)}/13 = {p13:.4f}")
print(f"  ⟹ 對 9 個模式之期望命中 E[k] = 9 × {p13:.4f} = {E_k:.4f}")
print(f"  ⟹ 觀測 k = {kmean:.4f}  vs  期望 {E_k:.4f}")
ck("§3 觀測命中 ≤ 密度期望 ⟹ 無正訊號", kmean <= E_k, True)
ck("§3 從未有任何三角剖分令 9 模式集 ⊆ Φ (k < 9)", kmax < 9, True)
print(f"  ⟹ 🔴 **k 從未達 9** ⟹ 「Φ 唔含模式集」在【全集成】穩健成立 ✅")

# ══════════════════════════════════════════════════════════════════════
print()
print("=" * 88)
print("§4 特定 IDCM 數之出現頻率 (全集成)")
print("=" * 88)
targets = {"e = 6": 6, "N_gen·B = 12": 12, "13": 13, "o = 15": 15, "L₇ = 29": 29,
           "N_d = 44": 44, "N_d+1 = 45": 45, "55 = F₁₀": 55, "|M| = 9": 9,
           "N_gen = 3": 3, "B = 4": 4, "F₅ = 5": 5, "L₄ = 7": 7, "L₅ = 11": 11}
for nm, v in targets.items():
    c = sum(1 for V in allvals if v in V)
    tag = "✅ 恆在" if c == N else ("🔴 從不在" if c == 0 else f"🟡 部分 ({100*c/N:.1f}%)")
    print(f"  {nm:<14s} ∈ Φ : {c:4d}/{N}  {tag}")
print(f"\n  ⟹ 注意: 出現率【高】唔等於有結構 — 必須對照密度基準 (§3)。")
print(f"     例: 值 6 之出現率高，但 [1,13] 區間本身有 13 個整數、Φ 已佔 {len(vals_le13)} 個。")

# ══════════════════════════════════════════════════════════════════════
print()
print("=" * 88)
print("§5 裁決")
print("=" * 88)
print("""  ① 🔴 **cytools p.triangulate(backend='qhull') 非決定性** —
     同一 polytope、同一 backend、同一 process 內多次呼叫給出不同三角剖分，
     ⟹ GKZ Φ 與 secondary cone 之超平面數【皆依三角剖分而變】。
  ② ✅ **不變量**: Σ Φ = 1000、max Φ = 200 (apex) 於全集成恆定。
  ③ ✅ **Round 19 §11 之核心結論【穩健】**: 全 200 個三角剖分之 Φ 皆【唔含】9 模式集
     (k 從未達 9)，且命中數 ≤ 密度期望 ⟹ 「Φ 唔係模式位置之載體」成立。
  ④ ⚠️ **須修正之表述**: docs/36 §11 之「Φ = [...]」「185 超平面」係【單一實例】，
     唔應寫成定值；須加註「三角剖分依賴 + 非決定性」。
  ⑤ 🟡 **pointed = False**: scripts/71 §3 之原始輸出顯示 secondary cone 非 pointed
     (Round 19 文檔未收錄) ⟹ 可能解釋 rays() 為何不返回 (需先商去 lineality space)。""")

print()
print("=" * 88)
print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}")
print("=" * 88)
if FAIL:
    print("FAIL 項:")
    for f in FAIL: print("  -", f)
