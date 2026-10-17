#!/usr/bin/env python3
"""
script 21 — LRD 巴爾末雙峰結構: 共軛模態對定理 (2026-09-13)
================================================================================
背景 (觀測, 2026): LRD 嘅 broad Balmer 線發現雙峰 / 多峰結構 —
  - Naidu+2025 (MoM-BH*-1): broad multi-peaked Hα (Lyα-like 雙峰)
  - Rusakov+2026 Nature: objects B/G「three apparent peaks」
  - Chang & Gronke 2026 (MNRAS): 共振散射可產生雙峰 Hα, 但 **Hβ 唔得**
    (4p→n=3 分支 BR3 = 0.261 → Hβ 光子轉 Paα, 冇足夠散射次數)
  - Naidu+2025 主張雙峰 Hβ 來自共振散射 (類 Lyα)

IDCM 側: O180 投影核 (r_k = 2πR_world·cos²θ_k, v_k = c·cosθ_k, v_k² = a₀r_k EXACT)
         + O159/O174 中心模定理 (γ_44 = μ² = 2)
         + O140 FSR 精化階梯 (N_ℓ = 88·4^ℓ)

本 script 推導: 雙峰結構係 176-Laplacian 共軛模態對嘅**結構必然**, 唔係散射效應。

Part A — 共軛模態對定理 (代數精確)
Part B — 中心模態 → 三峰結構預言
Part C — 階梯量子化 (FSR 精化)
Part D — 44-級聯平軌上限
Part E — 觀測錨點對比 (誠實: 區分「選擇門檻」vs「實測」)
Part F — 可證偽判別 (Hα vs Hβ)
================================================================================
"""
import math

# ---- 常量 (O180 / O140 / O159) ----
c = 299792.458            # km/s
N = 88                    # 88-site dual chain
N_d = 44
B = 4
mu2 = 2                   # μ² = E − O = 2 = γ_44
R_world = 1.275e26        # m (IDCM 世界環半徑, c/H₀ 讀法)
R_world_kpc = R_world/3.0857e19
a0 = c*1e3 * (c*1e3) / (2*math.pi*R_world)   # m/s² = c²/(2πR_world)

checks = []
def chk(name, val, expect, tol_rel=1e-9, note="", tol_abs=None):
    if tol_abs is not None:
        ok = abs(val-expect) <= tol_abs
    elif expect != 0:
        ok = abs(val-expect) <= tol_rel*abs(expect)
    else:
        ok = abs(val) < tol_rel
    checks.append((name, ok))
    print(f"  {'✅' if ok else '❌'} {name}: {val:.10g} vs {expect:.10g} {note}")
    return ok

print("="*80)
print("Part A — 共軛模態對定理 (176-Laplacian 模態對 k ↔ 176−k)")
print("="*80)
print("""
  O180 投影核: θ_k = kπ/176, v_k = c·cosθ_k, r_k = 2πR_world·cos²θ_k
  共軛對: cos(π − θ) = −cos θ  ⟹  θ_{176−k} = π − θ_k
""")
# 精確驗證 (k 同 176−k 同一半徑, 反號速度)
for k in [1, 22, 44, 66, 87, 88]:
    th1 = k*math.pi/176
    th2 = (176-k)*math.pi/176
    v1, v2 = c*math.cos(th1), c*math.cos(th2)
    r1 = 2*math.pi*R_world_kpc*math.cos(th1)**2
    r2 = 2*math.pi*R_world_kpc*math.cos(th2)**2
    print(f"  k={k:>3} (θ={math.degrees(th1):7.3f}°) ↔ k={176-k:>3}: "
          f"v={v1:>10.3f} / {v2:>10.3f} km/s,  r={r1:>10.3f} / {r2:>10.3f} kpc")
chk("共軛對速度反號 v_k + v_{176−k} = 0", c*math.cos(44*math.pi/176)+c*math.cos(132*math.pi/176), 0.0, tol_abs=1e-9)
chk("共軛對半徑相等 r_k = r_{176−k}",
    2*math.pi*R_world_kpc*math.cos(44*math.pi/176)**2 - 2*math.pi*R_world_kpc*math.cos(132*math.pi/176)**2, 0.0, tol_abs=1e-6)
print("""
  ⟹ **共軛模態對定理**: 每個半徑 r_k 同時承載 ±v_k 兩個模態
     (因為 r ∝ cos²θ 對 θ → π−θ 不變, 而 v ∝ cosθ 反號)
  ⟹ 對稱雙峰係結構必然 (唔需要散射, 唔需要雙錐/雙 AGN)
  ⟹ Δv(k) = 2c·cosθ_k = 2√(a₀·r_k)   (由 O180 EXACT 身份 v_k² = a₀r_k)
""")
chk("Δv(k) = 2√(a₀ r_k) EXACT (k=87)",
    2*math.sqrt(a0*(2*math.pi*R_world*math.cos(87*math.pi/176)**2))/1e3,
    2*c*math.cos(87*math.pi/176), 1e-9)

print("\n" + "="*80)
print("Part B — 中心模態 → 三峰結構預言")
print("="*80)
th88 = 88*math.pi/176
chk("中心模態 k=88: θ=π/2, v=0", math.cos(th88), 0.0, 1e-15)
chk("中心模態 γ_44 = μ² = 2 (γ_n = 4sin²(nπ/176))", 4*math.sin(44*math.pi/176)**2, 2.0, tol_abs=1e-12)
chk("中心模態半徑 r_88 = 0 (線心)", 2*math.pi*R_world_kpc*math.cos(th88)**2, 0.0, 1e-12)
print("""
  ⟹ **結構預言**: 線心 (v=0) 由中心模態佔據 → 中央峰
     加上共軛對嘅 ±v_k → **天然三峰結構** (中央 + 對稱雙峰)
  ⟹ 對照觀測: MoM-BH*-1「broad multi-peaked Hα」; Rusakov objects B/G
     「three apparent peaks」— 定性吻合 🟡 (但 RT 散射亦可能造出多峰, 需判別)
""")

print("\n" + "="*80)
print("Part C — 階梯量子化 (FSR 精化 N_ℓ = 88·4^ℓ)")
print("="*80)
print("  近中心模態: v_j ≈ c·jπ/(2N_ℓ)  ⟹  Δv_quantum = cπ/N_ℓ")
for l in range(0, 4):
    Nl = N*4**l
    dq = c*math.pi/Nl
    print(f"    ℓ={l}: N_ℓ={Nl:>6}  Δv_quantum = cπ/N_ℓ = {dq:>10.3f} km/s")
dq3 = c*math.pi/(N*4**3)
chk("ℓ=3 量子 cπ/(88·4³)", dq3, 167.2279, 1e-4)
print(f"\n  ℓ=3 rungs (Δv = n·{dq3:.3f} km/s):")
for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12]:
    print(f"    n={n:>2}: Δv = {n*dq3:>9.2f} km/s")

print("\n" + "="*80)
print("Part D — 44-級聯 (O180) 平軌上限")
print("="*80)
R_c = R_world_kpc/44**3
V_max = c/math.sqrt(2*math.pi)*44**(-1.5)
print(f"  R_c = R_world/44³ = {R_c:.3f} kpc")
chk("V_max = c/√(2π)·44^(−3/2)", V_max, 409.78, 1e-3, "km/s")
chk("V_max = √(a₀R_c)", math.sqrt(a0*R_c*3.0857e19)/1e3, V_max, 1e-6)
print(f"  2·V_max (邊緣對稱雙峰) = {2*V_max:.2f} km/s")
R_d = R_c/4
print(f"  R_d = R_c/4 = {R_d:.3f} kpc  →  v(R_d) = {math.sqrt(a0*R_d*3.0857e19)/1e3:.2f} km/s, "
      f"Δv = {2*math.sqrt(a0*R_d*3.0857e19)/1e3:.2f} km/s")

print("\n" + "="*80)
print("Part E — 觀測錨點對比 (誠實: 區分門檻 vs 實測)")
print("="*80)
anchors = [
    ("LRD broad Hα FWHM 選擇門檻", 1000, "門檻", "Matthee+2024/Greene+2024"),
    ("The Cliff Hα FWHM",          1500, "實測", "A&A 2025 aa54681-25"),
    ("本徵 Doppler 寬度 (散射修正後)", 300, "實測", "Rusakov+2026 Nature 10/12"),
    ("窄線 LRD FWHM",               250, "實測", "Zhang+2026 (150–300)"),
    ("Hα/Hβ 速度偏移中位",           106, "實測", "Pang+2026 (<250)"),
]
print(f"  {'錨點':<32} {'值':>6} {'類':>4}  對比 IDCM 預言")
for name, val, kind, src in anchors:
    print(f"  {name:<32} {val:>6} {kind:>4}")
    for lname, lval in [("2V_max (平軌)", 2*V_max), ("n=6 量子", 6*dq3), ("n=9 量子", 9*dq3),
                        ("2v(R_d)", 2*math.sqrt(a0*R_d*3.0857e19)/1e3)]:
        dev = (lval/val-1)*100
        if abs(dev) < 25:
            flag = "🟡" if kind == "門檻" else "🟢?"
            print(f"      vs {lname:<14} {lval:>8.2f} km/s : dev {dev:+7.2f}%  {flag}")

print("\n  ⚠️ 誠實標記:")
print("     - 「1000 km/s」係選擇門檻 (broad line 定義), 唔係測量 → 命中係循環論證 🟡")
print("     - 「1500 km/s」(The Cliff) 係實測, n=9 量子 dev +0.34% — 但 FWHM ≠ 峰距, 需小心")
print("     - 平軌上限 2V_max = 819.6 km/s < 觀測 raw FWHM 1000–1500 km/s")
print("       → 運動學單獨不足以解釋 raw 寬度; 散射修正後本徵 ~300 km/s 才係運動學比較對象")

print("\n" + "="*80)
print("Part F — Δv ↔ 半徑反演 + 可證偽判別")
print("="*80)
print("  反演: Δv = 2√(a₀r) ⟹ r = (Δv/2)²/a₀")
for dv in [300, 409.8, 819.6, 1000, 1500]:
    v = dv/2*1e3
    r = v*v/a0
    print(f"    Δv = {dv:>7.1f} km/s → r = {r/3.0857e19:>9.3f} kpc  "
          f"({'≤ R_c' if r/3.0857e19 <= R_c else '> R_c (超平軌!)'})")
print("""
  可證偽判別 (pre-registered):
  T1 🔴 **Hβ 雙峰 + Δv(Hβ) = Δv(Hα)** → 殺死共振散射 (BR3=0.261 令 Hβ 冇雙峰),
        支持運動學 (IDCM)。反之只有 Hα 雙峰 → 支持 RT 散射。
  T2 🔴 峰距量子化: Δv ∈ {n·cπ/(88·4^ℓ)} — 需高解像 (R≳2700) 多源樣本。
  T3 🔴 對稱性: 共軛對 ⟹ 關於線心**精確**對稱 (唔係近似) — outflow/雙錐模型給不對稱。
  T4 🔴 跨尺度 a₀: 雙峰 Δv 反演嘅 r 必須坐喺同一 a₀-locus (同星系轉動曲線 BTFR 共用 a₀)。
  T5 🟡 三峰結構: 中央模態 + 共軛對 → 中央峰 + 對稱雙峰 (MoM-BH*-1 定性吻合)。
""")

print("="*80)
npass = sum(1 for _, ok in checks if ok)
print(f"判定: {npass}/{len(checks)} PASS")
print("="*80)
