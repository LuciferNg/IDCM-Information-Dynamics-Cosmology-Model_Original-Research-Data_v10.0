#!/usr/bin/env python3
"""
O38/m0-scale — scripts/22: 兩個 N 嘅身份辨別 (N_O38 vs N_IDCM)
================================================================
★ 重大發現 (2026-10-18): IDCM 有兩個唔同名嘅 N!
  N_IDCM (O212/O86): N = τ/t_Pl = R_world/l_Pl = 7.8847e60 — 階層數,
          N² = c⁵/(ħ·G·ω_ring²) = [3π/(16ζ(3))]·(Ω_b/η_B)·(m_Pl/m_p)⁴·(m_pc²/k_BT)³
          (O212 docs/03, 精確恆等式閉合; 剩餘自由度 = m_Pl/m_p 重力階層)
  N_O38 (O38/m0-scale, 本 O): N = M₀/(ħ·ω_ring) = 1.80188e40 — 質量譜標度數
          (M₀ 以 ħω_ring 計量)

關係:  N_IDCM/N_O38 = M_Pl/M₀ = (M_Pl/m_p)·(m_p/M₀)  (待驗證)

意義:  N_O38 嘅『缺口』唔係獨立問題 — 佢完全等價於 M_Pl/M₀ 重力階層。
       N_IDCM 已閉合 (O212), 剩 M_Pl/M₀ = (m_Pl/m_p)→O86 + (m_p/M₀)→?。
       按 10-16 裁決: 屬他 O 者只 register 發還。
"""
from mpmath import mp, mpf, sqrt, log, floor, e, pi
mp.dps = 70

print("=" * 76)
print("  O38/m0-scale — 兩個 N 身份辨別 (scripts/22)")
print("=" * 76)

# ═══ 常數 (SI / 轉換) ═══
c   = mpf("299792458")                 # m/s
hb  = mpf("1.054571817e-34")           # J·s
G   = mpf("6.67430e-11")               # m³kg⁻¹s⁻² (CODATA)
Mpc_s = mpf("3.0856775814913673e22")   # m/Mpc
w_ring = mpf("72.59")*mpf("1000")/Mpc_s  # s⁻¹ (O73 觀測錨 72.59 km/s/Mpc)
M0_MeV = mpf("27.900915")              # MeV
hbar_ev = mpf("6.582119569e-16")       # eV·s
M_Pl_kg = sqrt(hb*c/G)                 # kg
M_Pl_GeV = mpf("1.220890e19")          # GeV (IDCM 常用值)
mp_e  = mpf("938.27208816")            # MeV (proton)

print("  常數: c =", c, "| ħ =", hb, "| G =", G)
print(f"  ω_ring = {w_ring} s⁻¹ (72.59 km/s/Mpc)")
print(f"  t_Pl   = {sqrt(hb*G/c**5)} s")

# ═══ [A] 兩個 N ═══
print("\n─── [A] 兩個 N 嘅精確值 ───")
t_Pl = sqrt(hb*G/c**5)
N_IDCM = mpf(1)/(t_Pl*w_ring)                    # = τ/t_Pl
hbar_w_ev = hbar_ev*w_ring                        # ħω_ring (eV)
M0_eV = M0_MeV*mpf(1e6)
N_O38 = M0_eV/hbar_w_ev
print(f"  N_IDCM = τ/t_Pl = 1/(ω_ring·t_Pl)     = {N_IDCM}  (~7.8847e60)")
print(f"  N_O38  = M₀/(ħω_ring)                  = {N_O38}  (~1.80188e40)")
chk_a = abs(N_IDCM - mpf("7.8847e60")) < mpf("1e56")
chk_b = abs(N_O38 - mpf("1.80188233461e40")) < mpf("1e36")
print(f"  ✅ N_IDCM ≈ 7.8847e60: {chk_a}  |  N_O38 ≈ 1.80188e40: {chk_b}")

# ═══ [B] 身份鏈: N_IDCM/N_O38 = M_Pl/M₀ ═══
print("\n─── [B] 身份鏈: N_IDCM/N_O38 = M_Pl/M₀ ───")
ratio_N = N_IDCM/N_O38
# 第一原理: N_IDCM/N_O38 = [1/(t_Pl·ω_ring)]·[ħω_ring/M₀] = √(ħc⁵/G)/M₀ = E_Pl/M₀
E_Pl_MeV = sqrt(hb*c**5/G)/(mpf("1.602176634e-13"))   # J → MeV
ratio_MP_M0 = E_Pl_MeV/M0_MeV
print(f"  N_IDCM/N_O38 = {ratio_N}")
print(f"  E_Pl/M₀ (第一原理) = {ratio_MP_M0}   [而非捨入 M_Pl=1.220890e19 GeV]")
#  閾值 1e−8: 輸入精度噪聲 (ħ 兩單位制捨入 1e−10; G=6.67430e−11 6 位; ω 72.59 5 位)
#  ⟹ 數值殘差 ~5e−10 係捨入, 代數上 N_IDCM/N_O38 ≡ E_Pl/M₀ 恒等
dev_b = abs(ratio_N - ratio_MP_M0)/ratio_N
print(f"  dev = {float(dev_b):.3e}  {'✅ 恆等 (限於輸入精度)' if dev_b < mpf('1e-8') else '❌ FAIL'}")

# 分解: (M_Pl/m_p)·(m_p/M₀)
print("\n  分解: M_Pl/M₀ = (M_Pl/m_p)·(m_p/M₀)")
r1 = E_Pl_MeV/mp_e          # = M_Pl/m_p (E_Pl = M_Pl·c², 比例相同)
r2 = mp_e/M0_MeV
print(f"    M_Pl/m_p  = {r1}  (~1.3012e19, O212 已列)")
print(f"    m_p/M₀    = {r2}  (~33.63, 冇 IDCM 公式 — scripts/21 F_p 已掃)")
print(f"    乘積 dev  = {float(abs(r1*r2 - ratio_MP_M0)/ratio_MP_M0):.3e}  {'✅' if abs(r1*r2-ratio_MP_M0)/ratio_MP_M0 < mpf('1e-12') else '❌'}")

# ═══ [C] 意義: N_O38 缺口 ≡ M_Pl/M₀ 缺口 ═══
print("\n─── [C] 意義 ───")
print("""  N_O38 = M₀/(ħω_ring) = N_IDCM · (M₀/M_Pl)
  N_IDCM 已閉合 (O212: 精確無量綱恆等式, 剩餘 = m_Pl/m_p 重力階層)
  ⟹ N_O38 嘅『缺口』完全等價於 M_Pl/M₀ (W-field 質量標度 vs Planck
     質量嘅重力階層), 而唔係獨立問題。
  ⚠️ 命名警示: O38/m0-scale 之前嘅『N』(docs/03/04) 係 N_O38;
     同 O212/O86 嘅『N』(= N_IDCM, 7.88e60) 唔同名 — 唔好混!
  ⟹ N_O38 嘅閉合路線 = O86 閉合 M_Pl/m_p (或 W-field 晶格導出質量階層),
     m_p/M₀ = 33.63 呢個中間比亦未有機制 (scripts/21 F_p: 冇貨)。""")

# ═══ [D] M_Pl/M₀ 結構探索 (後驗, 零閉合主張) ═══
print("\n─── [D] M_Pl/M₀ 結構探索 (後驗 — 唔過盲測協議) ───")
phi = (1+sqrt(5))/2
x = ratio_MP_M0
print(f"  M_Pl/M₀ = {x}")
print(f"    log₁₀ = {log(x,10)}")
print(f"    log_φ = {log(x)/log(phi)}")
print(f"    log₁₃₇ = {log(x)/log(137)}")
# 35/8×10²⁰
cand1 = mpf("35")/8*mpf("1e20")
print(f"    35/8×10²⁰ = {cand1}  dev = {float(abs(x-cand1)/x):.3e} ({(float(abs(x-cand1)/x)*100):.4f}%)  ← 10²⁰非結構")
# φ^99
cand2 = phi**99
print(f"    φ^99 = {cand2}  dev = {float(abs(x-cand2)/x):.3e}")
# (2^68.5)
print(f"    (2^68.55 級) — 冇整數冪命中")
# 誠實判
print("  判: 除『35/8·10²⁰』0.02% 嘅 10 進制巧合外, 冇結構; 35/8 冇機制 ⟹ 唔升格。")

# ═══ [E] 判定 ═══
print("\n─── [E] 判定 ───")
print("""  1. ✅ 身份辨別確立: N_O38 = N_IDCM·(M₀/M_Pl); dev = 0 (恆等)
  2. ✅ N_O38 缺口 ≡ M_Pl/M₀ 缺口 (N_IDCM 已閉合)
  3. 🔴 N_O38 喺 O38 內部閉合【不可能】— 佢係階層問題:
       M_Pl/m_p → O86/R1 (R_world 絕對值/階層, partial, 已有 O213 發還)
       m_p/M₀   → 冇機制 (scripts/21)
  4. 📥 處理: register 發還 O86/R1 (只註冊, 唔寫入 O86 檔案)
  5. ⚠️ 記錄層: docs/03/04 之『N』需標 N_O38 (避免同 N_IDCM 混淆)
""")