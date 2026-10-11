#!/usr/bin/python3
"""O239 — Script 08: T2 tick 動力學（時間標併入）
============================================================================
策略 T2（docs/04 §二 缺口 2）: F=dp/dt 嘅 dt = tick，動力學成為離散相位推進。

已證材料:
  O237 §1.6: tick = T_ring/88 = 9.617789e8 yr；「每 tick 一個相位步」
  O212:      ω_ring = 2π/T_ring；c = R_world·ω_ring
  O140/T1:   θ_n = πn/88；η = ln cot(θ/2)；γ = cscθ；p = mc·cotθ
  O237 U4:   U_n = e^{inπ/44}；α_n = nπ/44 (88-gon 相位)；b_n = |1−U_n| = 2sin(nπ/88)

預註冊判據（跑前凍結）:
  G1 tick=相位步: ω_ring·tick = 2π/88 = π/44 = α_1 = U_1 相位（恆等，由定義）
  G2 週期: 88 tick = 2π 一圈（U 週期）；44 tick = 半圈 θ=π/2 (v=0)
  G3 離散質量變化: Δb_n = b_{n+1}−b_n（每 tick 弦長變化, 非線性阻力）
  G4 離散能量: ΔE_n = mc²·Δcsc(θ_n)（每 tick 加速成本）
  G5 離散動量: Δp_n = mc·Δcot(θ_n)；F_n = Δp_n/tick
  G6 離散 γ 上限: γ_max(ℓ=0) = csc(π/88) ≈ 28.02；γ_max(ℓ) = csc(π/(88·4^ℓ))
     ——「c 不可達」= Nyquist/相位步上限 (可證偽預言)

預期（盲測前聲明）:
  各量每 tick 變化 delta 隨 n→44 (θ→π/2) 單調遞減 (v→0 區)；
  但加速成本 ΔE/Δv ∝ csc³θ 單調遞增 (θ→0 區)。
  呢個就係「點解越快加速越難」嘅離散形式: 相位步固定, cot/csc 斜率發散。
"""
import mpmath as mp
mp.mp.dps = 40
import json

N = 44
C, M = mp.mpf(1), mp.mpf(1)         # c=1, m=1（單位化；只睇結構）
T_ring = mp.mpf("84.637e9")         # yr（O121）
tick = T_ring / 88                  # O237 §1.6
omega = 2 * mp.pi / T_ring          # O212

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 76)
print("O239 scripts/08 — T2: tick 動力學（F=dp/dt 離散化）")
print("=" * 76)

# ── G1: tick = 相位步 ──
print("\n── G1: tick = 88-gon 相位步 ──")
dalpha = omega * tick
print(f"   ω_ring·tick = (2π/T_ring)(T_ring/88) = 2π/88 = {mp.nstr(dalpha, 10)}")
print(f"   U_1 相位 α_1 = π/44 = {mp.nstr(mp.pi/44, 10)}")
chk("G1 ω_ring·tick = π/44 = α_1", abs(dalpha - mp.pi/44) < mp.mpf("1e-40"),
    f"Δ={mp.nstr(abs(dalpha-mp.pi/44), 4)}")

# ── G2: 週期 ──
print("\n── G2: 88 tick = 一圈 ──")
u88 = mp.e ** (mp.mpc(0, 88 * mp.pi/44))
print(f"   U_88 = e^{{i·88π/44}} = e^{{i2π}} = {mp.nstr(u88, 4)}  (應 = 1+0i)")
u44 = mp.e ** (mp.mpc(0, 44 * mp.pi/44))
print(f"   U_44 = e^{{iπ}} = {mp.nstr(u44, 4)}  (半圈)")
chk("G2 U_88 = 1 (88 tick 一圈)", abs(u88 - 1) < mp.mpf("1e-40"))
chk("G2' U_44 = −1 (44 tick 半圈, v=0 點)", abs(u44 + 1) < mp.mpf("1e-40"))

# ── G3: 離散質量變化 (非線性阻力) ──
print("\n── G3: 每 tick 質量弦長變化 Δb ──")
# 注意: b_n = 2sin(nπ/88); tick 步: 相位 α 每 tick +π/44 ⟹ n→n+1
rows = []
for n in range(1, N):
    bn  = 2*mp.sin(n*mp.pi/88)
    bn1 = 2*mp.sin((n+1)*mp.pi/88)
    db = bn1 - bn
    rows.append((n, float(bn), float(db)))
for n, bn, db in rows[:4] + rows[-3:]:
    print(f"   n={n:>2}: b_n={bn:.6f}  Δb/tick={db:+.6f}")
db_first = abs(rows[0][2]); db_last = abs(rows[-1][2])
print(f"   |Δb|: n=1→2 {db_first:.6f} vs n=43→44 {db_last:.6f}  (遞減率 {db_last/db_first:.2f})")
chk("G3 Δb_1 vs Δb_43 遞減 (弦長增長率隨 n 收縮)", db_last < db_first,
    f"{db_last:.2e} < {db_first:.2e}")

# ── G4: 離散能量 (加速成本) ──
print("\n── G4: 每 tick 能量變化 ΔE = mc²·Δcscθ ──")
DE = []
for n in range(1, N):
    gn  = 1/mp.sin(n*mp.pi/88)
    gn1 = 1/mp.sin((n+1)*mp.pi/88)
    DE.append((n, float(gn1 - gn)))
# 接近光速區 (n 細) vs 低速區 (n 大) 嘅每 tick 能量成本
print("   n=1 (θ≈2.05°, v≈0.9994c) 開始:")
for n, de in DE[:3]:
    print(f"     n={n}: ΔE/tick = {de:+.4f} mc²")
print("   n=20 (θ≈40.9°) 附近:")
for n, de in DE[19:22]:
    print(f"     n={n}: ΔE/tick = {de:+.4f} mc²")
chk("G4 ΔE(高速) > ΔE(低速) 每 tick（加速成本隨 v 增）",
    abs(DE[0][1]) > abs(DE[19][1]),
    f"n=1: {DE[0][1]:+.3f} vs n=20: {DE[19][1]:+.3f}")

# ── G5: 離散動量 + 力 ──
print("\n── G5: Δp = mc·Δcotθ, F = Δp/tick ──")
Dp = []
for n in range(1, N):
    pn  = mp.cot(n*mp.pi/88)
    pn1 = mp.cot((n+1)*mp.pi/88)
    Dp.append((n, float(pn1 - pn)))
# 每 tick 動量注入:
# 由 n=43→44 (到 v=0) 需要 dp; 由 n=1→2 (高速) 需要 dp
print(f"   由 n=1→2 (θ 2.05°→4.09°): Δp = {Dp[0][1]:+.3f} mc")
print(f"   由 n=20→21 (θ 40.9°→42.95°): Δp = {Dp[19][1]:+.3f} mc")
# 關鍵: 速度嘅加速 — 同一 Δθ (1 tick), 高速區速度變化細
dv_hi = float(mp.cos(1*mp.pi/88) - mp.cos(2*mp.pi/88))
dv_lo = float(mp.cos(20*mp.pi/88) - mp.cos(21*mp.pi/88))
print(f"   同一 tick 嘅 Δv: 高速區 Δv={dv_hi:.5f}c vs 低速區 Δv={dv_lo:.5f}c")
chk("G5 同一相位步, 高速區 Δv 細 (加速效率歸零)",
    dv_hi < dv_lo, f"Δv_hi {dv_hi:.4f} < Δv_lo {dv_lo:.4f}")

# ── G6: 離散 γ 上限 (結構預言) ──
print("\n── G6: γ 上限 = 相位 Nyquist ──")
gmax0 = csc_pi88 = 1/mp.sin(mp.pi/88)
print(f"   γ_max(ℓ=0) = csc(π/88) = {mp.nstr(gmax0, 8)}  (v_min = c·cos(π/88) = {mp.nstr(mp.cos(mp.pi/88),8)}c)")
ladder = []
for ell in range(0, 8):
    gm = 1/mp.sin(mp.pi/(88*4**ell))
    ladder.append((ell, float(gm)))
for ell, gm in ladder[:4]:
    print(f"   ℓ={ell}: γ_max = csc(π/(88·4^ℓ)) = {gm:.4f}")
print(f"   ⟹ 「c 不可達」唔係假設: 相位每 tick π/44, 最小可辨相位 = π/88, γ 最大 = {float(gmax0):.4f}")
print(f"   ⟹ 加速到 γ 需升層 ℓ: γ_max(ℓ) = (88/π)·4^ℓ")
chk("G6 γ_max(ℓ=0) = csc(π/88) ≈ 28.02", abs(gmax0 - mp.mpf("28.0172")) < mp.mpf("1e-3"),
    f"γ_max={mp.nstr(gmax0,6)}")

# ── 總結: 點解越快加速越難 (離散形式) ──
print("\n── T2 結論 ──")
print("   每 tick 相位步 Δα = π/44 固定。但:")
print("   Δp/tick = mc·Δcotθ ∝ mc·csc²θ·(π/88)  — θ→0 (v→c) 時發散")
print("   Δv/tick = −c·sinθ·(π/88)              — θ→0 時 → 0")
print("   ⟹ 加速成本 dE/dv = (ΔE)/(Δv) ∝ csc³θ → ∞")
print("   「越快越難加速」= 離散相位推進嘅 cot/csc 幾何, 唔係新物理")

# ── JSON dump ──
out = {
    "tick_yr": float(tick),
    "alpha_per_tick": float(mp.pi/44),
    "delta_b_sample": rows[:4] + rows[-3:],
    "delta_E_first": DE[0], "delta_E_mid": DE[19],
    "dv_hi_tick": dv_hi, "dv_lo_tick": dv_lo,
    "gamma_max_ladder": ladder[:8],
    "verdict": "T2: tick = 88-gon 相位步; 離散加速成本 ∝ csc³θ 發散; γ_max = csc(π/88)",
}
import os
os.makedirs("data", exist_ok=True)
with open("data/08_tick_dynamics.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")