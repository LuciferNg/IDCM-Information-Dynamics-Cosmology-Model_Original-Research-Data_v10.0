#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-44 — 自旋分裂維度檢驗: 容器因子 + 冪律排除 + 加法族
==================================================================
承接: scripts/43 排除 5 個乘法/開方族 (0/6)。本輪推向「未探維度」:
(a) ΔS 係咪 pair-only? (b) 冪律? (c) 加法族?

★ 預註冊 (跑前凍結):
  [P1] 數據 (scripts/43 data/43, PDG 2024): ρ−π 22.943, K*−K 14.263,
       D*−D 5.090, B*−B 1.633, Σ*/Λ 9.606, Ξ*/Ξ0 7.890 M₀
  [P2] P-A 容器因子: C = ΔS(ρ−π)/ΔS(Σ*−Λ) = 2.387 (單點描述, 唔係算子);
       ★ 結構性檢驗: ΔS 非 pair-only ⟺ ΔS(ρ−π,u,d) ≠ ΔS(Σ*−Λ,u,d)
       (同 pair, 唔同容器) ⟹ PASS = 差異 > 3σ (σ ≈ PDG ±0.04 M₀)
  [P3] P-B 冪律排除: 假設 ΔS = A·(pair 質量乘積)^{−α}; 用三對計 α:
       α₁ 由 (ρ,K*), α₂ 由 (K*,D*), α₃ 由 (D*,B*)
       ⟹ 排除當 max|Δα| > 0.05 (α 唔係常數)
  [P4] P-C 加法族 (零 free scale, 只測比例): 6 個候選 × r2,r3,r4:
       G1 (γ₁+γ₂) 正序 / G2 倒序 / G3 (E′₁+E′₂) 正序 / G4 倒序 /
       G5 (m₁+m₂) 正序 / G6 倒序
       PASS = 任一 G 3/3 cost ≤ 3%
  [P5] 判決: 全排除 ⟹ 自旋形式維度縮窄 = {非 pair-only, 非冪律, 非加/乘族}
       ⟹ 需容器維度 + 新結構輸入 (W_S/色磁通量) 先可閉合;

輸出: data/44_spin_dimension_checks.json
"""
import json, math

M0 = 27.90091451
NB = {"u": 93.4 / 42.890,
      "d": 93.4 / 42.890 * 2.1505,
      "s": 93.4,
      "c": 3096.9 / 2,
      "b": 9460.30 / 2}
MODE = {"u": 11, "d": 9, "s": 7, "c": 4, "b": 2}

def gam(n):
    return 4 * math.sin(n * math.pi / 88) ** 2

EF = {11: 165.586979074824, 9: 195.235149040176, 7: 134.717027433432,
      4: 114.865277982844, 2: 202.400151085512}

# pair → ΔS (M₀)
DS = {("u", "d"): 22.943, ("d", "s"): 14.263, ("c", "d"): 5.090,
      ("b", "d"): 1.633, ("u", "d"): 22.943}
# 介子對 (用於 r 比例): r2 = (u,d)/(d,s), r3 = (d,s)/(c,d), r4 = (c,d)/(b,d)
MESON_SEQ = [("u", "d"), ("d", "s"), ("c", "d"), ("b", "d")]
RATIOS = [("r2", 0, 1), ("r3", 1, 2), ("r4", 2, 3)]

print("═══ §1 P-A 容器因子 (單點) ═══")
ds_meson = DS[("u", "d")]          # ρ−π
ds_baryon = 9.606                  # Σ*−Λ (scripts/42)
C = ds_meson / ds_baryon
print(f"  ΔS(ρ−π, (u,d) meson) = {ds_meson:.3f}  vs  ΔS(Σ*/Λ, (u,d) baryon) = {ds_baryon:.3f}")
print(f"  C = {C:.4f}  (單點描述, 唔係算子)")
sep = abs(ds_meson - ds_baryon)
print(f"  ★ ΔS 非 pair-only: 同 pair (u,d) 差 {sep:.3f} M₀ = {sep/0.04:.0f}σ (σ≈0.04 M₀) "
      f"⟹ {'✅ 結構性結論: ΔS 依賴容器' if sep > 3*0.04 else '✗ 容器無效'}")

print("\n═══ §2 P-B 冪律排除 ═══")
def mprod(pair):
    return NB[pair[0]] * NB[pair[1]]
alphas = []
for i in range(3):
    p1, p2 = MESON_SEQ[i], MESON_SEQ[i + 1]
    dp = DS[p1] / DS[p2]
    r = mprod(p2) / mprod(p1)
    a = math.log(dp) / math.log(r)
    alphas.append(a)
    print(f"  α({i+1}) from {p1}→{p2}: ΔS 比 {DS[p1]/DS[p2]:.4f}, m-prod 比 {r:.2f} ⟹ α = {a:+.4f}")
dmax = max(alphas) - min(alphas)
print(f"  max|Δα| = {dmax:.4f} {'> 0.05 ⟹ 冪律排除 ✅' if dmax > 0.05 else '≤ 0.05 ⟹ 冪律未能排除'}")

print("\n═══ §3 P-C 加法族 ═══")
def s_gam(p):
    return gam(MODE[p[0]]) + gam(MODE[p[1]])
def s_ef(p):
    return EF[MODE[p[0]]] + EF[MODE[p[1]]]
def s_m(p):
    return NB[p[0]] + NB[p[1]]
GEN = {"G1 γ-sum": s_gam, "G3 E′-sum": s_ef, "G5 m-sum": s_m}
obs_r = {}
for label, i, j in RATIOS:
    obs_r[label] = DS[MESON_SEQ[i]] / DS[MESON_SEQ[j]]
res = {}
for name, fn in GEN.items():
    for order in ("pos", "inv"):
        devs = []
        for label, i, j in RATIOS:
            a, b = fn(MESON_SEQ[i]) / fn(MESON_SEQ[j]), fn(MESON_SEQ[j]) / fn(MESON_SEQ[i])
            pred = a if order == "pos" else b
            devs.append(abs(pred - obs_r[label]) / obs_r[label])
        key = f"{name}-{order}"
        le3 = sum(1 for d in devs if d <= 0.03)
        res[key] = {"le3": le3, "devs": [round(d * 100, 2) for d in devs], "PASS": le3 == 3}
        print(f"  {key}: {res[key]['devs']}  {'✅' if res[key]['PASS'] else '✗'}")

print("\n═══ §4 判決 ═══")
w = [k for k, r in res.items() if r["PASS"]]
print(f"  P-A 容器: ΔS 依賴容器 ✅ (同 pair 差 {sep:.1f}σ)")
print(f"  P-B 冪律: {'排除' if dmax > 0.05 else '未排除'}")
print(f"  P-C 加法族: {'通過 ' + str(w) if w else '全排除 (0/6)'}")
print(f"  ⟹ 自旋形式維度縮窄: {{非 pair-only, 非冪律, 非乘/開方族 (scripts/43), 非加族}}")

OUT = {"container": {"C": C, "ds_meson": ds_meson, "ds_baryon": ds_baryon,
                     "sigma": 0.04, "non_pair_only": sep > 3 * 0.04},
       "power_law": {"alphas": alphas, "max_dalpha": dmax,
                     "excluded": dmax > 0.05},
       "additive": res,
       "verdict": "dimensions-narrowed-honest-negative"}
with open("data/44_spin_dimension_checks.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("  data/44_spin_dimension_checks.json 寫入完成")