"""
O171 攻堅 44: R_world = 4129.94 Mpc 第一性原理分解
=================================================================
O73 開放項: 「🔴 4129.94 Mpc 結構分解」
O171 遺留: 「🔴 R ≠ 1 之殘餘 (r_d 0.4846%, r* 1.2079%) ⇒ 需第二機制或 R_world 精化」

任務:
  1. R_world 數值是否正確? (c/ω_ring 驗證)
  2. R_world 定義是什麼? (O73 已確立: 世界環半徑)
  3. R_world 結構分解: 有冇第一性原理組合?

O171 提供新結構數 (之前 O73 PSLQ 冇用):
  - 420/421 = (L₇²∓1)/2, 高斯範數 z = 14+15i
  - r_d = (πR/88)(420/421) ← R_world 已經參與家族!
  - L₇ = 29, L₄ = 7, L₅ = 11
  - N/(N+1) 家族: 33/34, 44/45, 55/56, 420/421
"""
import mpmath as mp
mp.mp.dps = 30

c = mp.mpf('299792.458')       # km/s
omega = mp.mpf('72.59')        # (km/s)/Mpc
R = c / omega                  # Mpc
print("=" * 74)
print("1. R_world 數值驗證")
print("=" * 74)
print(f"  R_world = c/ω_ring = {mp.nstr(R, 10)} Mpc")
print(f"  四捨五入 4129.94? {abs(R - mp.mpf('4129.94')) < 0.01}")
print(f"  精確值 = {mp.nstr(R, 15)}")
print(f"  src 用 4129.94 (5 sig fig) — 偏差 {mp.nstr((mp.mpf('4129.94')-R)/R*100, 4)}%")
print()

print("=" * 74)
print("2. R_world 定義 (O73 已確立)")
print("=" * 74)
print("""
  R_world = 世界環半徑 (幾何輸入)
  L_ring = 2πR_world = 25949.2 Mpc (世界環周長)
  ω_ring = c/R_world = 72.59 (km/s)/Mpc (角頻率)
  T_ring = 2π/ω_ring = 84.63 Gyr (周期)
  λ_sync = L_ring/88 = πR_world/44 = 294.88 Mpc (觀察者維度分割)
  身份: 角頻率, T_ring × ω_ring = 2π (O73 docs/03)

  ★ BBN 鎖定 (O73 docs/04): η_B(obs)+T_CMB+Ω_b → ω_ring = 72.73 (0.19%)
  ★ CMB 投影 (O73 docs/05): ω_cmb = ω_ring(1-π/44) = 67.41 (0.07%)
  ★ H5 交叉鎖定 (O73 docs/09): 雙重獨立鎖定, z = 0.32σ
""")

print("=" * 74)
print("3. ★ 已存在嘅 R_world 結構連結 (O171 發現)")
print("=" * 74)
# r_d = (πR/88)(420/421)
rd = (mp.pi * R / 88) * (mp.mpf(420)/421)
print(f"  r_d = (πR/88)(420/421) = {mp.nstr(rd, 8)} Mpc")
print(f"  vs Planck r_d = 147.09: dev {mp.nstr((rd-mp.mpf('147.09'))/mp.mpf('147.09')*100, 4)}%")
print(f"  vs o167 r_d = 147.088: dev {mp.nstr((rd-mp.mpf('147.088'))/mp.mpf('147.088')*100, 5)}%")
print()
print(f"  → R_world 經 r_d 已經參與 N/(N+1) 家族 (420/421)")
print(f"  → R_world 唔係獨立於家族嘅量!")
print()

# 反解: R = r_d × 88×421/(420×π)
r_d_obs = mp.mpf('147.088')
R_from_rd = r_d_obs * 88 * 421 / (420 * mp.pi)
print(f"  反解: R = r_d × 88×421/(420π) = {mp.nstr(R_from_rd, 8)}")
print(f"  vs 4129.94: dev {mp.nstr((R_from_rd-mp.mpf('4129.94'))/mp.mpf('4129.94')*100, 4)}%")
print()

print("=" * 74)
print("4. 結構分解掃描 (O73 PSLQ 未試過嘅新方向)")
print("=" * 74)
struct = {
    "420 (L₇²-1)/2": 420, "421 (L₇²+1)/2": 421, "29 L₇": 29,
    "33 K_tree": 33, "55 F₁₀": 55, "56 F₁₀+1": 56,
    "60 |A₅|": 60, "12 B·N_gen": 12, "34": 34, "45": 45,
    "15 N_gen·F₅": 15, "14 2L₄": 14, "7 L₄": 7, "11 L₅": 11,
    "176 2N_dB": 176, "946 C(44,2)": 946, "554": 554, "264": 264,
}
print(f"  R_world / 結構數:")
for name, n in sorted(struct.items(), key=lambda x: x[1]):
    q = R / n
    flag = ""
    if abs(q - round(q)) < 1e-3:
        flag = f" ★ 接近整數 {round(q)}"
    elif abs(q - round(q*2)/2) < 1e-3:
        flag = f" ☆ 接近半整數 {round(q*2)/2}"
    print(f"  {name:14s}: {mp.nstr(q, 7)}{flag}")
print()

print("=" * 74)
print("5. ★ 新方向: R_world × 家族因子 = 結構數?")
print("=" * 74)
# N/(N+1) 家族: 如果 R_world = X × (d-1)/d 形式?
family = [("33/34", 33, 34), ("44/45", 44, 45), ("55/56", 55, 56), ("420/421", 420, 421)]
for name, a, b in family:
    # R × (d-1)/d
    v1 = R * a / b
    # R × d/(d-1)
    v2 = R * b / a
    print(f"  R × {name} = {mp.nstr(v1, 7)}")
    print(f"  R × {b}/{a} = {mp.nstr(v2, 7)}")
print()

print("=" * 74)
print("6. R_world 其他單位")
print("=" * 74)
# Mpc → Gpc, 光年, m
print(f"  R_world = {mp.nstr(R, 6)} Mpc")
print(f"          = {mp.nstr(R/1000, 6)} Gpc")
print(f"          = {mp.nstr(R*3.261563777, 6)} Mly")
print(f"          = {mp.nstr(R*3.0856775814913673e22/1e27, 6)} Ym (10²⁷ m)")
print(f"          = {mp.nstr(R*3.0856775814913673e22/mp.mpf('1.616255e-35'), 6)} l_P (Planck 長度)")
print()

print("=" * 74)
print("7. ★ 天文交叉: R_world 對應咩?")
print("=" * 74)
print(f"  T_ring = 84.63 Gyr (世界環周期)")
print(f"  宇宙年齡 (ΛCDM) = 13.8 Gyr → T_ring/宇宙年齡 = {mp.nstr(mp.mpf('84.63')/mp.mpf('13.8'), 4)}")
print(f"  13.47 Gyr = R_world/c = T_H (半徑光行時間)")
print(f"  T_ring/T_H = 2π (exact, 環/半徑)")
print(f"  84.63/13.47 = {mp.nstr(mp.mpf('84.6349')/mp.mpf('13.4701'), 5)}")
print()

print("=" * 74)
print("8. 初步判決")
print("=" * 74)
print("""
  🟢 R_world = 4129.94 Mpc 數值正確 (c/72.59, 5 sig fig 四捨五入)
  🟢 R_world 定義 = 世界環半徑 (O73 三重鎖定)
  🟢 R_world 已經有結構連結: r_d = (πR/88)(420/421) (O171)
     → R_world 透過 r_d 參與 N/(N+1) 家族
  🔴 但「R_world = 純結構數組合」未搵到 (PSLQ 負結果 + 本輪掃描)
  → 下一步: 深挖 r_d 鏈, 睇 R_world 點解要係 4129.94 先令 r_d = 147.09
""")
