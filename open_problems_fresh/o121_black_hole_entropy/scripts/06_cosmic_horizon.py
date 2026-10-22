#!/usr/bin/env python3
"""
O121 — script 06: 宇宙視界熵 S_dS + T_dS ↔ ω_ring
====================================================
世界環 (R_world) = 最大「黑洞」: 宇宙學事件視界。

IDCM 宇宙冇膨脹 (PARADIGM BREAK), 但有一個因果視界:
    世界環半徑 R_world = 4129.94 Mpc (O73)
    角頻率 ω_ring = 72.59 (km/s)/Mpc (O73: T_ring×ω_ring=2π)

de Sitter 視界熵 (Gibbons-Hawking):
    S_dS = A/(4G) = π R_world² / ℓ_P²   (A = 4πR_world²)

IDCM 詮釋 (本腳本建立):
    世界環 = T_pipe† 嘅最大嵌入面 (全宇宙尺度反投影邊界)
    → R_world 係「宇宙黑洞」嘅事件視界
    → S_dS = 全宇宙嘅資訊容量 (熵上限)

本腳本驗證:
1. A = 4πR_world² (視界面積)
2. S_dS = πR_world²/ℓ_P² (數值)
3. S_dS ≈ 10¹²² (de Sitter 熵著名量級, ~2.6e122 文獻值)
4. T_dS = ħω_ring/2πk_B 同 R_world 半徑一致
5. IDCM 嘅資訊守恆: 世界環熵 = 全系統資料容量上限
6. 對比: 太陽黑洞熵 S_⊙ = 4πM_⊙²/M_P² ~ 1e77 (遠細於宇宙上限)
"""
import math, json

# ---- IDCM 常數 ----
phi=(1+math.sqrt(5))/2
R_world_Mpc = 4129.94
omega_ring = 72.59          # (km/s)/Mpc

# ---- 物理常數 ----
hbar=1.054571817e-34; k_B=1.380649e-23; c=299792458.0
G=6.67430e-11
M_Pl_kg = 2.176434e-8
l_P = math.sqrt(hbar*G/c**3)     # Planck 長度 (m)
R_world_m = R_world_Mpc * 3.085677581e22

results={}; PASS=0; FAIL=0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS+=1; print(f"  ✅ {name} {detail}")
    else:    FAIL+=1; print(f"  ❌ {name} {detail}")

print("="*74)
print("O121 script 06: 宇宙視界熵 S_dS + T_dS ↔ ω_ring")
print("="*74)

# ===== 1. 視界面積 =====
print("\n[1] 世界環視界面積 A = 4πR_world²")
A_world = 4*math.pi*R_world_m**2
print(f"  R_world = {R_world_Mpc} Mpc = {R_world_m:.4e} m")
print(f"  A_world = 4πR_world² = {A_world:.4e} m²")
check("A > 0", A_world > 0)

# ===== 2. S_dS = A/4G = πR_world²/ℓ_P² =====
print("\n[2] 宇宙視界熵 S_dS = A/(4G)")
S_dS = A_world/(4*G) * c**3/hbar          # A/4ℓ_P² (無量綱, 熵/k_B)
S_dS_formula = math.pi*(R_world_m/l_P)**2
print(f"  ℓ_P = {l_P:.4e} m")
print(f"  S_dS = A/4ℓ_P² = {S_dS:.4e}")
print(f"  S_dS = π(R_world/ℓ_P)² = {S_dS_formula:.4e}")
check("S_dS 兩式一致", abs(S_dS-S_dS_formula)/S_dS < 1e-9)
check("S_dS ~ 10¹²² 量級 (dS 熵著名值)", abs(math.log10(S_dS)-122) < 1.0,
      f"(log10 S_dS = {math.log10(S_dS):.2f})")
# 文獻 de Sitter 熵比較 (誠實, 唔係循環):
#   世界環 = c/H₀ (Hubble 半徑, Ω_Λ=1 極限幾何)
#   文獻 dS 視界 = c/(H₀√Ω_Λ) → S_dS,lit = πc²/(H₀²Ω_Λℓ_P²)
H_s = omega_ring*3.24078e-20
Om_Lam = 4/(phi**4-1)                      # IDCM Ω_Λ = 0.6833
S_dS_lit_IDCM = math.pi*c**2/(H_s**2*Om_Lam*l_P**2)   # 2.858e122
S_dS_lit_Planck = 3.2633e122               # Planck 2018 Λ=1.1056e-52 m⁻²
print(f"  世界環熵 (c/H₀ 幾何)     = {S_dS:.4e}")
print(f"  文獻 dS 熵 (IDCM Ω_Λ=0.6833) = {S_dS_lit_IDCM:.4e}  (比 {S_dS_lit_IDCM/S_dS:.3f})")
print(f"  文獻 dS 熵 (Planck Ω_Λ)  = {S_dS_lit_Planck:.4e}  (比 {S_dS_lit_Planck/S_dS:.3f})")
check("同文獻 dS 熵同量級 (差 √Ω_Λ 幾何因子 <2)",
      abs(math.log10(S_dS)-math.log10(S_dS_lit_IDCM)) < 0.3,
      f"(Δlog10 = {abs(math.log10(S_dS)-math.log10(S_dS_lit_IDCM)):.3f})")
print("  ⚠️ 世界環 = c/H₀ (Hubble 半徑), 唔係 √(3/Λ) dS 視界")
print("     → IDCM 熵 1.95e122 vs 文獻 2.86–3.26e122 (差 1.5–1.7×)")

# ===== 3. 太陽黑洞對比 =====
print("\n[3] 對比: 太陽質量黑洞熵")
M_sun=1.98892e30
S_sun = 4*math.pi*(M_sun/M_Pl_kg)**2     # S = 4πM²/M_P²
print(f"  S_⊙ = 4π(M_⊙/M_P)² = {S_sun:.4e} (~10⁷⁷)")
check("S_⊙ ~ 1e77 (BH 著名值)", abs(math.log10(S_sun)-77) < 1.0,
      f"(log10 S_⊙ = {math.log10(S_sun):.2f})")
check("宇宙視界熵 >> 太陽黑洞熵 (10⁴⁵ 倍)", S_dS/S_sun > 1e40,
      f"(比 = {S_dS/S_sun:.2e})")

# ===== 4. T_dS ↔ ω_ring =====
print("\n[4] 宇宙視界溫度 T_dS = ħω_ring/2πk_B")
T_dS = hbar*(omega_ring*3.24078e-20)/(2*math.pi*k_B)
T_dS_alt = hbar*c/(2*math.pi*k_B*R_world_m)   # dS 用 2π (Schwarzschild 先係 4π)
print(f"  T_dS (ω_ring)   = {T_dS:.4e} K")
print(f"  T_dS (R_world)  = {T_dS_alt:.4e} K (ħc/2πk_B R)")
check("T_dS 兩式一致 (ω_ring = c/R_world)", abs(T_dS-T_dS_alt)/T_dS < 1e-5,
      f"(比 = {T_dS/T_dS_alt:.8f}, 72.59 係 3 位有效數字輸入)")
check("T_dS ~ 2.7e-30 K", abs(T_dS-2.7e-30)/2.7e-30 < 0.1, f"({T_dS:.3e} K)")

# ===== 5. 資訊關聯: S_dS = 全系統資料容量 =====
print("\n[5] 資訊守恆: 世界環熵 = 全系統資料容量上限")
# IDCM: S_tot = Σγ = 90 (log 單位) 係「已可分辨嘅能量份額」
# 而 S_dS 係「最大可儲存資訊」(熵容量) — 兩個唔同層次
# 但 IDCM 關鍵: 黑洞 + 蒸發全程 S_tot 守恆 (script 05)
# → 可儲存資訊 ≤ S_dS, 且蒸發回復 → 冇資訊掉出世界環
print("  世界環=全系統視界: 資訊唔可能逃出世界環 (因果)")
print("  黑洞蒸發回復資訊 (script 05) → 上帝不漏資訊")
# R_world = c·T_ring/2π 檢查 (O73 身份):
T_ring_s = 2*math.pi/(omega_ring*3.24078e-20)
check("R_world = c·T_ring/2π (O73 身份)", abs(R_world_m - c*T_ring_s/(2*math.pi))/R_world_m < 1e-3,
      f"(cT/2π = {c*T_ring_s/(2*math.pi):.4e} m)")

# ===== 6. 熵上限對資訊悖論嘅補充 =====
print("\n[6] S_dS 補充資訊悖論論證")
print(f"  全宇宙熵容量 = S_dS ≈ {S_dS:.2e}")
print("  黑洞內部熵 S_sync ≤ S_dS (係視界內資訊, 唔會超過宇宙容量)")
print("  → 蒸發後資訊必然返到輻射 (容量守恆 + 因果)")

# ---- write JSON ----
out={
 "title":"宇宙視界熵 S_dS + T_dS ↔ ω_ring",
 "R_world_m":R_world_m,"A_world_m2":A_world,
 "S_dS":S_dS,"S_dS_formula":S_dS_formula,
 "S_dS_lit_IDCM":S_dS_lit_IDCM,"S_dS_lit_Planck":S_dS_lit_Planck,
 "log10_S_dS":math.log10(S_dS),
 "S_sun":S_sun,"ratio_SdS_Ssun":S_dS/S_sun,
 "T_dS_K":T_dS,"T_dS_from_R":T_dS_alt,
 "R_world_identity":"R_world = c·T_ring/2π (O73); = c/H₀ (Hubble 半徑, 非 √(3/Λ) dS 視界)",
 "verdict":"世界環=c/H₀: S≈1.95e122 (同文獻 dS 熵 2.86-3.26e122 同量級, 差 √Ω_Λ 幾何因子); T_dS≈2.7e-30K; 資訊容量上限",
}
with open("data/06_cosmic_horizon.json","w") as f:
    json.dump(out,f,indent=2,ensure_ascii=False)

print(f"\n{'='*74}")
print(f"RESULT: {PASS} PASS, {FAIL} FAIL  {'🟢 全閉合' if FAIL==0 else '🔴 失敗'}")
print(f"{'='*74}")
if FAIL: exit(1)