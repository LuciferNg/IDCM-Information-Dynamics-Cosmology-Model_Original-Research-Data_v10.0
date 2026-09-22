#!/usr/bin/env python3
"""
O215 — scripts/04: h 結構核對 + Ω_b 版本衝突量化（O38 反證驗收）
================================================================
核對 O38 docs/02_o215_report.md 嘅反證數字（唔照單全收）:
  R1  h_cmb = ω_ring(1−π/44)/100 = 0.67407 (O167) — O215 所用 h=0.674 即此 (dev 0.011%)
  R2  Ω_b 版本衝突: BBN 鎖 ω_ring ∝ 1/√Ω_b; 3/60 下 ω_ring' = 66.83
  R3  ω_ring' 66.83 vs Planck 67.36 (−0.78%) vs IDCM 結構 72.59 (−7.93%)
  R4  M₀ ∝ √ω_ring → m_7 影響 −4.05%
"""
import mpmath as mp

mp.mp.dps = 40

checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


print("=" * 100)
print("O215 scripts/04: h 結構核對 + Ω_b 版本衝突量化")
print("=" * 100)

# ── R1: h_cmb ──
w_ring_src = mp.mpf("72.59")          # 結構值 c/R_H
h_cmb = w_ring_src * (1 - mp.pi / 44) / 100
print(f"\n§R1 h_cmb = ω_ring(1−π/44)/100 = {mp.nstr(h_cmb, 10)}")
print(f"   vs O215 所用 h=0.674: dev = {float((h_cmb - 0.674)/0.674*100):.4f}%")
print(f"   vs Planck h=0.6736:   dev = {float((h_cmb - 0.6736)/0.6736*100):.4f}%")
chk("R1a h_cmb = 0.67407 (O167)", abs(h_cmb - mp.mpf("0.67407")) < mp.mpf("1e-5"),
    f"h_cmb = {mp.nstr(h_cmb, 8)}")
chk("R1b O215 所用 h=0.674 = IDCM 預言 (dev < 0.02%)",
    abs((h_cmb - 0.674) / 0.674) < mp.mpf("2e-4"),
    f"dev = {float((h_cmb-0.674)/0.674*100):.4f}%")

# ── R2/R3: Ω_b 版本衝突 ──
Om_old = mp.mpf(19) / 450            # O73 BBN 鎖用 (O14 鏈)
Om_new = mp.mpf(3) / 60              # O215/O163 現行
w_ring_A_old = mp.mpf("72.73")       # O73 系 A (BBN, Ω_b=0.04221)
w_ring_A_new = w_ring_A_old * mp.sqrt(Om_old / Om_new)   # ∝ 1/√Ω_b
print(f"\n§R2/R3 Ω_b 版本衝突: BBN 鎖 ω_ring ∝ 1/√Ω_b")
print(f"   ω_ring'(3/60) = 72.73 × √((19/450)/(3/60)) = {mp.nstr(w_ring_A_new, 8)}")
print(f"   vs Planck 67.36:  dev = {float((w_ring_A_new-67.36)/67.36*100):+.2f}%")
print(f"   vs IDCM 72.59:    dev = {float((w_ring_A_new-72.59)/72.59*100):+.2f}%")
chk("R2 ω_ring'(3/60) = 66.83", abs(w_ring_A_new - mp.mpf("66.83")) < mp.mpf("0.05"),
    f"ω_ring' = {mp.nstr(w_ring_A_new, 6)}")
chk("R3a ω_ring' 接近 Planck CMB (|dev| < 2%)", abs(w_ring_A_new - 67.36) / 67.36 < mp.mpf("0.02"),
    f"dev = {float((w_ring_A_new-67.36)/67.36*100):+.2f}%")
chk("R3b ω_ring' 遠離結構 72.59 (>5% 張力)", abs(w_ring_A_new - 72.59) / 72.59 > mp.mpf("0.05"),
    f"dev = {float((w_ring_A_new-72.59)/72.59*100):+.2f}%")

# 獨立交叉: 用 η_B(obs) = 6.104e-10, Ω_b = 3/60
eta_obs = mp.mpf("6.104e-10")
K_eta = mp.mpf("2.736e-8")
h_bbn_new = mp.sqrt(eta_obs / (K_eta * Om_new))
print(f"\n   獨立交叉: h(BBN, Ω_b=3/60) = √(6.104e-10/(2.736e-8·0.05)) = {mp.nstr(h_bbn_new, 6)}"
      f" → H₀ = {mp.nstr(h_bbn_new*100, 6)}")
chk("R2b 獨立交叉 h ≈ 0.668 (H₀ ≈ 66.8)", abs(h_bbn_new * 100 - mp.mpf("66.8")) < mp.mpf("0.5"),
    f"H₀ = {mp.nstr(h_bbn_new*100, 6)}")

# ── R4: M₀/m_7 影響 ──
r_scale = mp.sqrt(w_ring_A_new / mp.mpf("72.59"))     # M₀ ∝ √ω_ring
m7 = mp.mpf("13.8002")
m7_new = m7 * r_scale
print(f"\n§R4 M₀ ∝ √ω_ring: 標度比 = √(66.83/72.59) = {mp.nstr(r_scale, 8)} ({float((r_scale-1)*100):+.2f}%)")
print(f"   m_7: {mp.nstr(m7, 8)} → {mp.nstr(m7_new, 8)} MeV (dev {float((m7_new-m7)/m7*100):+.2f}%)")
chk("R4 m_7 影響 ≈ −4.05% (破壞 13.8 閉合)", abs((m7_new - m7) / m7 * 100 - (-4.05)) < mp.mpf("0.3"),
    f"dev = {float((m7_new-m7)/m7*100):+.2f}%")

n_pass = sum(1 for _, ok in checks if ok)
print(f"\n{'='*100}")
print(f"RESULT: {n_pass}/{len(checks)} PASS")
print(f"{'='*100}")
