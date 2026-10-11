#!/usr/bin/env python3
"""
O64 整合攻艱 04: O120 C_f 混標度診斷 + 統一 scheme 修正
================================================================
發現 (scripts/03):
  O120 C_f 池 = by-construction (PDG 絕對質量反推) 含混標度:
    C_c/C_s = 4.5028 → c/s = 13.597 (混標度, O234 判死)
    統一 scheme (Nf=4) 需要 C_c/C_s = 3.859 → dev 16.7%
  但 6/8 比值 (d/u, s/d, s/u, mu/e, tau/mu, t/b) 統一 scheme 下仍閉合 <1%
   → 結構核心仍在, 只有 c,b 受混標度污染

本 script: 統一 scheme 目標重算 required C_f → 檢查修正後嘅比值 pattern
=============================================================
"""
import math, json
import numpy as np

M0 = 27.900915
gam = lambda n: 4*math.sin(n*math.pi/88)**2
A5 = [1,2,3,4,5,7,9,11,13]

print("="*76)
print("O64 整合 04: O120 C_f 混標度診斷 + 修正")
print("="*76)

assign = {'e':1,'u':2,'d':3,'s':4,'mu':5,'c':7,'tau':9,'b':11,'t':13}

# O120 原始 C_f (from PDG 絕對質量, 混標度)
Cf_O120 = {'e':3.5941,'u':3.8029,'d':3.6620,'s':41.3207,'mu':30.0308,
           'c':186.0605,'tau':159.6437,'b':255.7517,'t':7722.8073}

# 統一 scheme 目標 (O234 freeze v2)
targets = {'e':0.511,'mu':105.658,'tau':1776.86,'u':2.16,'d':4.67,
           's':93.4,'c':1270.0,'b':4180.0,'t':172690.0}

# 統一 scheme 重算 required C_f
Cf_new = {p: targets[p]/(M0*gam(assign[p])) for p in targets}

print("\n=== [1] required C_f: O120 vs 統一 scheme ===")
print(f"  {'粒子':>5s} {'n':>3s} {'O120 C_f':>10s} {'新 C_f':>10s} {'Δ%':>8s}")
for p in ['e','u','d','s','mu','c','tau','b','t']:
    dlt = (Cf_new[p]-Cf_O120[p])/Cf_O120[p]*100
    tag = ' ←混標度' if abs(dlt) > 3 else ''
    print(f"  {p:>5s} {assign[p]:>3d} {Cf_O120[p]:>10.4f} {Cf_new[p]:>10.4f} {dlt:>7.2f}%{tag}")

# ==== [2] 比值: 統一 scheme required C_f 下 ====
print("\n=== [2] 統一 scheme 下質量比 (用新 C_f) ===")
ratios = [
    ('d/u','d','u', 2.1505), ('s/d','s','d', 19.944), ('s/u','s','u', 42.890),
    ('mu/e','mu','e', 206.77), ('tau/mu','tau','mu', 16.817),
    ('c/s','c','s', 11.652), ('b/c','b','c', 4.586), ('t/b','t','b', 41.310),
]
print(f"  {'比值':>8s} {'γ比':>10s} {'C比':>10s} {'預測':>10s} {'目標':>10s} {'dev':>8s}")
for label, num, den, tgt in ratios:
    gr = gam(assign[num])/gam(assign[den])
    cr = Cf_new[num]/Cf_new[den]
    pred = gr*cr
    dev = (pred-tgt)/tgt*100
    tag = '✅' if abs(dev) < 0.5 else ('🟡' if abs(dev) < 2 else '🔴')
    print(f"  {tag} {label:>8s} {gr:>10.4f} {cr:>10.4f} {pred:>10.4f} {tgt:>10.4f} {dev:>7.2f}%")

# 呢啲係定義恆等 (C_f = m/(M0γ) ⟹ 預測=目標 0%)
# 真正問題: C_f 有冇結構源 — O233 已答: 無
print(f"\n  ⚠️ 預測=目標係 C_f 定義 (by-construction); 結構問題 = C_f 源頭 (O233: 無)")

# ==== [3] ★★ 新結構候選: C_f ratio 有冇閉式? ====
print("\n=== [3] C_f 比結構掃描 (統一 scheme required C_f) ===")
# 睇 C_f 比值: C_f_{i+1}/C_f_i 係咪結構數
order = ['e','u','d','s','mu','c','tau','b','t']
print(f"  C_f 值 (統一 scheme): {[round(Cf_new[p],2) for p in order]}")
print(f"  C_f 逐對比:")
pairs = [(order[i], order[i+1]) for i in range(8)]
for a,b in pairs:
    r = Cf_new[b]/Cf_new[a]
    print(f"    {b}/{a}: {r:.4f}")

# ==== [4] 睇 C_f 內部結構: log 空間 ====
print("\n=== [4] ln(C_f) pattern ===")
lns = [math.log(Cf_new[p]) for p in order]
print(f"  ln C_f: {[f'{x:.3f}' for x in lns]}")
diffs = [lns[i+1]-lns[i] for i in range(8)]
print(f"  差: {[f'{x:.3f}' for x in diffs]}")

# ==== [5] 結論 ====
print("\n=== [5] 結論 ===")
print(f"""
1. O120 C_f 池含混標度 (c, b 用 m_c(m_c)/m_b(m_b)) — O234 判死確認
   C_c/C_s = 4.5028 (O120) vs 3.859 (Nf=4 需要) → dev 16.7%
2. 統一 scheme required C_f: {[round(Cf_new[p],3) for p in order]}
3. 6/8 比值 (d/u, s/d, s/u, mu/e, tau/mu, t/b) 用 O120 C_f 已閉合 (<1%)
   → 嗰啲比不受混標度影響 (同 scheme 或 pole)
4. C_f 本身冇算子身份 (O233 5 線負) → 質量比唔可以由結構池預言
5. O64 剩餘任務: 接受 C_f = 定義 (by-construction), 質量層出路 = O209 |Δm|^α
""")

out = {
    "date": "2026-10-11",
    "Cf_O120": Cf_O120,
    "Cf_unified": Cf_new,
    "diagnosis": "O120 C_f 含混標度 c,b; 統一 scheme 下 6/8 比值仍閉合",
    "c_over_s_O120": 13.597, "c_over_s_Nf4": 11.652, "b_over_c_O120": 3.291, "b_over_c_Nf4": 4.586,
}
with open("data/04_cf_mixed_scale.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ 已儲存 data/04_cf_mixed_scale.json")