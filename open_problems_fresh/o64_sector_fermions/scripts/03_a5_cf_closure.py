#!/usr/bin/env python3
"""
O64 整合攻艱 03: A₅ γ升序 + O120 C_f → 質量比閉合檢驗
================================================================
目標: 用 O137 授權指派 (e→1..t→13) + O120 C_f 值,
      對統一 scheme (O234 freeze v2) 目標做全面比對:
      - 個別質量
      - 比值 (m_d/m_u, m_s/m_d, m_c/m_s, m_b/m_c, m_t/m_b, μ/e, τ/μ)
      - 同 O233 已閉合結構 (u/d 身份, d 落 odd, t 槽) 對齊
"""
import math, json
import numpy as np

M0 = 27.900915
gam = lambda n: 4*math.sin(n*math.pi/88)**2
A5 = [1,2,3,4,5,7,9,11,13]

print("="*76)
print("O64 整合 03: A₅ γ升序 + O120 C_f → 質量比閉合")
print("="*76)

# O137 授權指派 (γ升序): e→1 u→2 d→3 s→4 μ→5 c→7 τ→9 b→11 t→13
assign = {'e':1,'u':2,'d':3,'s':4,'mu':5,'c':7,'tau':9,'b':11,'t':13}

# O120 C_f 值 (O233 SESSION_START §四, 9 粒子含 t=7722.8 係 O137)
Cf_O120 = {'e':3.5941,'u':3.8029,'d':3.6620,'s':41.3207,'mu':30.0308,
           'c':186.0605,'tau':159.6437,'b':255.7517,'t':7722.8073}

# 統一 scheme 目標 (O234 freeze v2)
targets = {'e':0.511,'mu':105.658,'tau':1776.86,'u':2.16,'d':4.67,
           's':93.4,'c':1270.0,'b':4180.0,'t':172690.0}

print("\n=== [1] 個別質量: m = M₀·γ_n·C_f (預測 vs 目標) ===")
preds = {}
ok_all = True
for p in ['e','u','d','s','mu','c','tau','b','t']:
    n = assign[p]
    cf = Cf_O120[p]
    m_pred = M0 * gam(n) * cf
    m_tgt = targets[p]
    dev = (m_pred - m_tgt)/m_tgt*100
    preds[p] = m_pred
    tag = '✅' if abs(dev) < 1 else ('🟡' if abs(dev) < 5 else '🔴')
    if abs(dev) >= 5: ok_all = False
    print(f"  {tag} {p:>4s}: n={n:>2d} C_f={cf:>9.4f} → m={m_pred:>10.2f} MeV (目標 {m_tgt:>10.2f}, dev {dev:>6.2f}%)")

# 由於 C_f 就係由 m/(M₀γ) 定義, 預測 = 目標 (trivially 0%)
# 但呢度用 O120 儲存嘅 C_f (可能係舊 scheme) 同新目標比對 → 睇 scheme 差異
print(f"\n  ⚠️ C_f 係由 m/(M₀γ) 定義 → 預測=目標係必然 (定義重言式)")
print(f"     真正問題 = C_f 有冇算子身份 (O233: 無)")

# ==== [2] 比值閉合 (核心 !) ====
print("\n=== [2] 質量比閉合檢查 (A₅ γ升序) ===")
print(f"  質量比 = (γ_n/γ_m)·(C_f_i/C_f_j)")

ratios_to_check = [
    ('d/u', 'd','u', 2.1505, 0.111),
    ('s/d', 's','d', 19.944, 0.33),
    ('s/u', 's','u', 42.890, 1.52),
    ('mu/e', 'mu','e', 206.77, 0),   # μ/e pole ratio
    ('tau/mu', 'tau','mu', 16.817, 0),
    ('c/s', 'c','s', 11.652, 0.065),
    ('b/c', 'b','c', 4.586, 0.012),
    ('t/b', 't','b', 41.31, 0),       # 172690/4180
]
print(f"\n  {'比值':>8s} {'γ比':>10s} {'C_f比':>10s} {'預測':>10s} {'目標':>10s} {'dev':>8s}")
for label, num, den, tgt, terr in ratios_to_check:
    gam_ratio = gam(assign[num]) / gam(assign[den])
    cf_ratio = Cf_O120[num] / Cf_O120[den]
    pred = gam_ratio * cf_ratio
    dev = (pred - tgt)/tgt*100 if tgt else float('nan')
    tag = '✅' if abs(dev) < 1 else ('🟡' if abs(dev) < 5 else '🔴')
    print(f"  {tag} {label:>8s} {gam_ratio:>10.4f} {cf_ratio:>10.4f} {pred:>10.3f} {tgt:>10.3f} {dev:>7.2f}%")

# ==== [3] O233 已閉合結構對齊 ====
print("\n=== [3] O233 已閉合結構對齊 ===")
checks = []
# 3a. u/d 身份: C_u > C_d 但 γ₂ < γ₃ → m_d > m_u
checks.append(("u/d: C_u>C_d (3.80>3.66) 但 γ₂<γ₃ ⟹ m_d>m_u (m 次序由 γ 主導)",
               Cf_O120['u'] > Cf_O120['d'] and gam(2) < gam(3)))
# 3b. d 落 odd 流: 質量次序 rank3 = d (e,u,d)
checked_b = preds['e'] < preds['u'] < preds['d']
checks.append(("d 落 odd 流: 質量次序 e<u<d (rank 3 = d)", checked_b))
# 3c. lepton 槽 ≡1 mod 4: e(1), μ(5), τ(9)
checks.append(("lepton 槽 ≡1 mod 4: e=1, μ=5, τ=9",
               all(assign[p] % 4 == 1 for p in ['e','mu','tau'])))
# 3d. t 槽: n=13 ≡1 mod 4 (t 同 lepton 槽但走 VEV)
checks.append(("t 槽: n=13 ≡1 mod 4 (但 y_t≈1 VEV)", assign['t'] % 4 == 1))
# 3e. 鋸齒: even 流 {u,s,c,b} 純夸克 / odd {e,d,μ,τ} 3輕子+1夸克
even = {'u','s','c','b'}  # n even: 2,4,7?, 11? — 用指派
# n: u=2(ev), d=3(od), s=4(ev), μ=5(od), c=7(od!), τ=9(od), b=11(od), t=13(od)
# 等等 — O233 嘅 even/odd 係質量 rank parity, 唔係 n parity!
# O233 docs/14: 質量升序 rank 1..8 = e,u,d,s,μ,c,τ,b → even ranks {u,s,c,b} 純夸克
# 但 c rank=6 (even), τ rank=7 (odd) — 用 rank 而非 n
rank_order = ['e','u','d','s','mu','c','tau','b']  # 質量升序 rank 1..8
even_rank = [rank_order[i] for i in range(8) if (i+1)%2==0]  # ranks 2,4,6,8
odd_rank = [rank_order[i] for i in range(8) if (i+1)%2==1]   # ranks 1,3,5,7
all_even_quark = all(p in {'u','s','c','b'} for p in even_rank)
checks.append((f"鋸齒: even ranks {even_rank} 全夸克 (O233 閉合)",
               all_even_quark))
# 3f. m_d/m_u EXACT: O233 docs/15 P2 ★ 2.1620
m_d_over_u = (gam(3)*Cf_O120['d'])/(gam(2)*Cf_O120['u'])
checks.append((f"m_d/m_u = {m_d_over_u:.4f} (O233 P2 2.1620)", abs(m_d_over_u-2.1620) < 0.002))

print(f"\n  {'結果':>5s} 檢驗")
for label, ok in checks:
    print(f"  {'✅' if ok else '🔴'} {label}")

# ==== [4] 盲測框架: C_f 無算子身份 ⟹ 質量比 = γ 比 × 未知因子 ====
print("\n=== [4] 結構性結論 ===")
print(f"""
A₅ γ升序指派 (O137 授權) 結構性質:
  1. m_d/m_u = (γ₃/γ₂)·(C_d/C_u) = {gam(3)/gam(2):.4f} × {Cf_O120['d']/Cf_O120['u']:.4f}
     = {m_d_over_u:.4f} ← O233 P2 已閉合 (EXACT 2.1620)
  2. mass 次序 = γ 主導 (C_f 只微調) — u(d) 對比: C_u/C_d = 1.038 但 γ₃/γ₂ = 2.245
  3. C_f 無算子身份 (O233) ⟹ 質量比唔可以由結構池預言
     ⟹ 真正出路 = κ 非對角已死 (O59), O209 |Δm|^α 並行
""")

# Save
out = {
    "date": "2026-10-11",
    "assignment": assign,
    "cf_o120": Cf_O120,
    "predicted_mass": preds,
    "m_d_over_m_u": m_d_over_u,
    "structure_checks": [l for l, ok in checks if ok],
    "note": "A₅ γ升序 + O120 C_f 結構閉合檢驗; C_f 無算子身份 (O233)"
}
with open("data/03_a5_cf_closure.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ 已儲存 data/03_a5_cf_closure.json")