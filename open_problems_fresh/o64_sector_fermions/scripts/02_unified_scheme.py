#!/usr/bin/env python3
"""
O64 整合攻艱 02: 統一 scheme (O234 凍結層 v2) 目標表 + A₅ γ升序重配檢驗
================================================================
承接:
  docs/04 (audit), docs/05 (R1 A₅ 初步), O233 (C_f 生成器 5 線負閉合)
  O234 (同 scheme 比規則), O137 (A₅ γ升序指派 e→1..t→13), O209 (|Δm|^α 冪律)
"""
import math, json
import numpy as np

M0 = 27.900915
gam = lambda n: 4*math.sin(n*math.pi/88)**2
A5 = [1,2,3,4,5,7,9,11,13]

print("="*76)
print("O64 整合 02: 統一 scheme 目標 + A₅ γ升序重配")
print("="*76)

# ==== [1] O234 凍結層 v2 目標表 (同 scheme, FLAG Nf=4 + PDG) ====
print("\n=== [1] 統一 scheme 質量目標表 ===")
# 來源: O234 docs/02 + docs/03 (freeze v2)
# 絕對值 (MS̄): e, μ, τ (pole), s(2GeV), c(3GeV), b(3GeV), t(pole)
# 比值 (Nf=4 同 scheme): m_c/m_s = 11.652, m_b/m_c@3GeV = 4.586, m_d/m_u = 2.1505
targets = {
    # name: (mass_MeV, scheme_note)
    'e':  (0.511,   "PDG pole"),
    'mu': (105.658, "PDG pole"),
    'tau':(1776.86, "PDG pole"),
    'u':  (2.16,    "MS̄ 2GeV (FLAG)"),
    'd':  (4.67,    "MS̄ 2GeV (FLAG)"),
    's':  (93.4,    "MS̄ 2GeV (FLAG)"),
    'c':  (1270.0,  "m_c(m_c) Nf=4 (FLAG)"),
    'b':  (4180.0,  "m_b(m_b) Nf=4 (PDG)"),
    't':  (172690.0,"pole (PDG)"),
}
for name, (m, note) in targets.items():
    print(f"  {name:>4s}: {m:>10.3f} MeV  ({note})")

# 統一 scheme 比 (O234 凍結層 v2, 唔再混標度)
print(f"\n  同 scheme 比 (O234 freeze v2):")
ratios = {
    'c/s': (11.652, 0.065, "Nf=4, FLAG 主值"),
    'b/c': (4.586,  0.012, "@3GeV, HPQCD"),
    'd/u': (2.1505, 0.111, "Nf=4"),
    's/u': (42.890, 1.52,  "derived"),
    's/d': (19.944, 0.33,  "derived"),
}
for k, (v, err, src) in ratios.items():
    print(f"  {k:>5s} = {v} ± {err} ({src})")

# ==== [2] O137 授權 A₅ γ升序指派 ====
print("\n=== [2] O137 授權 A₅ γ升序指派 (e→1..t→13) ===")
# 輕子 {1,5,9} ≡ 1 mod 4; 夸克 {2,3,4,7,11,13}
assigned = {
    'e': 1, 'u': 2, 'd': 3, 's': 4, 'mu': 5, 'c': 7, 'tau': 9, 'b': 11, 't': 13
}
print(f"  A₅ modes: {A5}")
for p in ['e','u','d','s','mu','c','tau','b','t']:
    n = assigned[p]
    resid = n % 4
    print(f"  {p:>4s}: n={n:>2d} (mod 4 = {resid})")

# ==== [3] 同 scheme 目標下 m = M₀·γ_n·C_f 需要嘅 C_f ====
print("\n=== [3] m = M₀·γ_n·C_f → required C_f (γ升序指派) ===")
# 用統一 scheme 目標
req = {}
for p in assigned:
    m = targets[p][0]
    n = assigned[p]
    cf = m / (M0 * gam(n))
    req[p] = (n, m, cf)
    print(f"  {p:>4s}: n={n:>2d}, γ_n={gam(n):.6f}, m={m:>9.3f} MeV → C_f = {cf:>10.4f}")

# ==== [4] required C_f 結構檢驗 ====
print("\n=== [4] required C_f 結構身份檢驗 ===")
print("  O233 結論: C_f 8 值喺框架內無算子身份 (5 線全負)")
print("  → O64 唔可以再宣稱 F_proj 池 = 結構")

# 睇 required C_f 有冇簡單結構 (Lucas/Fibonacci/44±)
fib = {1,2,3,5,8,13,21,34,55}
lucas = {2,1,3,4,7,11,18,29,47}
print(f"\n  required C_f vs 結構數:")
for p in assigned:
    n, m, cf = req[p]
    tags = []
    if abs(cf - round(cf)) < 0.01:
        tags.append(f"≈整数 {round(cf)}")
    for sname, sset in [("Fib", fib), ("Lucas", lucas)]:
        for sv in sset:
            if abs(cf - sv)/sv < 0.02:
                tags.append(f"≈{sname} {sv} ({abs(cf-sv)/sv*100:.1f}%)")
    print(f"  {p:>4s}: C_f={cf:>10.4f} {'; '.join(tags) if tags else '— 冇近結構'}")

# ==== [5] m_c/m_s 同 scheme 檢驗 (O158 交接核心) ====
print("\n=== [5] c/s scheme 裁定 ===")
c_n = assigned['c']; s_n = assigned['s']
c_m = targets['c'][0]; s_m = targets['s'][0]
print(f"  O64 原:  c=γ₁₈×15.5=621 MeV, s=γ₅×15.5=54.5 → c/s = {621/54.5:.3f}")
print(f"  O234:   c/s Nf=4 = 11.652 ± 0.065")
print(f"  A₅ 指派: c/s = γ₇/γ₄ × (C_c/C_s) = {gam(7)/gam(4):.3f} × (C_c/C_s)")
print(f"  需要 C_c/C_s = 11.652 / {gam(7)/gam(4):.3f} = {11.652/(gam(7)/gam(4)):.3f}")

# m 直接比 (統一 scheme)
cf_c = req['c'][2]; cf_s = req['s'][2]
print(f"  required C_c/C_s = {cf_c/cf_s:.4f}")
print(f"  池近鄰? O233 已判: C_f 池匹配要用同 scheme 比; docs/03 嘅 11.39 dev 2.23% vs Nf=4")

# ==== [6] 量綱跨度 = A₅ γ × C_f 池 ====
print("\n=== [6] 跨度檢驗 (統一 scheme 目標) ===")
m_e = targets['e'][0]; m_t = targets['t'][0]
span = m_t/m_e
gam_span = gam(13)/gam(1)
print(f"  t/e 質量跨度 (統一 scheme) = {span:.0f}×")
print(f"  A₅ γ 跨度 = {gam_span:.1f}×")
print(f"  需要 C_f 跨度 = {span/gam_span:.0f}×")
print(f"  required C_f max/min = {max(req[p][2] for p in req)/min(req[p][2] for p in req):.0f}×")

# ==== [7] 結論 ====
print("\n=== [7] 結論 ===")
print("""
O233 負閉合 (C_f 生成器 5 線全負) → O64 舊 F_proj 池唔係結構。

統一 scheme (O234 freeze v2) 下:
1. A₅ γ升序指派 (O137 授權) + m = M₀·γ·C_f 需要 C_f 跨度 {:.0f}×
   (required C_f 值見 §3)
2. required C_f 值大多唔係「標準結構數」→ 符合 O233「無算子身份」
3. c/s 同 scheme 11.652: O64 docs/03 嘅 11.39 dev 2.23% 係 scheme 殘差;
   O158 嘅 13.597 係混標度 (O234 判死)
4. 真正出路 = O209 質量層 (|Δm|^α 冪律) 或 κ 張量非對角 (O53/O59)
   — O64 集成: 接收 O233 負閉合 + 以 A₅ γ升序為指定框架
""".format(span/gam_span))

out = {
    "date": "2026-10-11",
    "targets_unified": {k: v[0] for k, v in targets.items()},
    "a5_assignment_0137": assigned,
    "required_cf": {p: {"n": v[0], "cf": v[2]} for p, v in req.items()},
    "span_needed_cf": float(span/gam_span),
    "note": "O233 C_f 生成器 5 線負閉合 → O64 需重構, 唔可以再用 F_proj 池"
}
with open("data/02_unified_scheme.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n✅ 已儲存 data/02_unified_scheme.json")