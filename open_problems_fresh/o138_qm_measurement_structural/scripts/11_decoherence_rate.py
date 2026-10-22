#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O138 - Script 11: 退相干速率 Gamma 之 IDCM 結構形式
=====================================================
閉合殘餘: 退相干速率 Gamma (量子 -> 經典轉變動力學)

機制 (結構性, 零擬合):
  O41 已閉合: 觀察者一次完整世界快照 = N_d = 44 次讀數
    (全預算 61.5, 每次讀數 B(n) = 123/88, 而 61.5 * 88/123 = 44 精確)
  快照週期 = 世界環週期 T_ring
  => 讀數時鐘 f_read = N_d / T_ring
  每次讀數 = 一次投影塌縮  =>  Gamma = f_read

  Gamma = N_d/T_ring = N_d*f_ring = N_d*w_ring/(2*pi) = f_44/2 = c/(2*lam_sync)

日期: 2026-09-17 | 前置: O41 綠, O34 綠, O164 綠
"""

from mpmath import mp, mpf, pi, sin, sqrt
mp.dps = 40

Nd, B, Ngen = 44, 4, 3
w_ring   = mpf('72.59')            # (km/s)/Mpc  世界環角頻率 (O73 命名)
R_world  = mpf('4129.94')          # Mpc
Mpc_km   = mpf('3.085677581e19')
Gyr_s    = mpf('3.15576e16')
c_kms    = mpf('299792.458')

w_s      = w_ring / Mpc_km         # s^-1 (角頻率)
f_ring   = w_s / (2*pi)            # Hz
T_ring_s = 1 / f_ring
T_ring_G = T_ring_s / Gyr_s
lam_sync = (2*pi*R_world) / 88     # Mpc  (L_ring/88)

PASS = FAIL = 0
def chk(name, ok, detail=""):
    global PASS, FAIL
    if ok: PASS += 1
    else:  FAIL += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if detail: print(f"          {detail}")

def nstr(x, n=10):
    return mp.nstr(x, n)

print("=" * 76)
print("O138 Script 11: 退相干速率 Gamma 之 IDCM 結構形式")
print("=" * 76)

# ============================================================
print("\n[1] 環參數 (O73 命名; 身份鐵律 T_ring * w_ring = 2*pi)")
print("-" * 76)
print(f"    w_ring  = {nstr(w_ring)} (km/s)/Mpc  = {nstr(w_s)} s^-1")
print(f"    f_ring  = {nstr(f_ring)} Hz")
print(f"    T_ring  = {nstr(T_ring_G)} Gyr")
print(f"    lam_sync= L_ring/88 = {nstr(lam_sync)} Mpc")

chk("T_ring * w_ring = 2*pi (角頻率身份, 非頻率)",
    abs(T_ring_s * w_s - 2*pi) < mpf('1e-30'),
    f"T*w = {nstr(T_ring_s*w_s, 20)}  vs 2*pi = {nstr(2*pi, 20)}")
chk("f_ring = 1/T_ring (真正繞圈頻率)",
    abs(f_ring * T_ring_s - 1) < mpf('1e-30'), f"f*T = {nstr(f_ring*T_ring_s, 20)}")

# ============================================================
print("\n[2] O41 讀數結構: 一次世界快照 = 44 次讀數 (精確)")
print("-" * 76)
B_alloc   = mpf(123)/88          # B(n) = L10/(2*Nd) 每模態預算
budget    = mpf('61.5')          # <W>^2 = 觀察者預算
n_reads   = budget / B_alloc
print(f"    B(n)   = L10/(2Nd) = 123/88 = {nstr(B_alloc)}")
print(f"    budget = <W>^2     = 61.5")
print(f"    reads  = 61.5 * 88/123 = {nstr(n_reads)}")

chk("讀數數目 = N_d = 44 精確 (61.5*88 = 44*123)",
    budget*88 == 44*123 and abs(n_reads - Nd) < mpf('1e-30'),
    f"61.5*88 = {nstr(budget*88)};  44*123 = {44*123}")

# ============================================================
print("\n[3] 退相干速率 Gamma = 讀數速率 = N_d / T_ring")
print("-" * 76)
Gamma = Nd / T_ring_s
tau   = 1 / Gamma
print(f"    Gamma = 44 / T_ring = {nstr(Gamma)} s^-1")
print(f"    tau   = T_ring/44   = {nstr(tau/Gyr_s)} Gyr")

# 等價形式 (全部由 T_ring = 2*pi*R_world/c 與 f_44 = 88*f_ring 推得)
G_a = Nd * f_ring                       # N_d * f_ring
G_b = Nd * w_s / (2*pi)                 # N_d * w_ring/(2*pi)
G_c = 88 * f_ring / 2                   # f_44/2   (f_44 = 2*Nd*f_ring)
G_d = c_kms / (2 * lam_sync * Mpc_km)   # c/(2*lam_sync)
f_44 = 88 * f_ring

chk("Gamma = N_d * f_ring", abs(Gamma - G_a) < mpf('1e-40'), f"{nstr(G_a)}")
chk("Gamma = N_d * w_ring/(2*pi)", abs(Gamma - G_b) < mpf('1e-40'), f"{nstr(G_b)}")
chk("Gamma = f_44/2  (f_44 = 88 f_ring)", abs(Gamma - G_c) < mpf('1e-40'), f"{nstr(G_c)}")
chk("Gamma = c/(2*lam_sync)", abs(Gamma - G_d)/G_d < mpf('1e-6'), f"{nstr(G_d)}")
chk("f_44 = c/lam_sync (O164 Nyquist 身份)",
    abs(f_44 - c_kms/(lam_sync*Mpc_km))/f_44 < mpf('1e-6'),
    f"f_44 = {nstr(f_44)} Hz;  c/lam_sync = {nstr(c_kms/(lam_sync*Mpc_km))} Hz")
chk("tau/T_ring = 1/N_d 精確",
    abs((tau/T_ring_s) - mpf(1)/Nd) < mpf('1e-40'), f"tau/T_ring = {nstr(tau/T_ring_s)}")

# ============================================================
print("\n[4] 與模態階梯之尺度一致性 (O164: f_n = 88 f_ring sin(n*pi/88))")
print("-" * 76)
f1  = 88*f_ring*sin(pi/88)
print(f"    f_1  = 88 f_ring sin(pi/88) = {nstr(f1)} Hz")
print(f"    f_44 = 88 f_ring            = {nstr(f_44)} Hz")
print(f"    Gamma= 44 f_ring            = {nstr(Gamma)} Hz")
print(f"    範圍: f_1 < Gamma < f_44 ?  {f1 < Gamma < f_44}")

chk("Gamma 落於模態頻帶內 (f_1, f_44)",
    f1 < Gamma < f_44, "讀數時鐘快於基頻, 慢於 Nyquist")
chk("Gamma / f_44 = 1/2 (Nyquist 之半)",
    abs(Gamma/f_44 - mpf(1)/2) < mpf('1e-30'), f"{nstr(Gamma/f_44)}")

# ============================================================
print("\n[5] 陷阱排除: 44/(2*pi) = 7.0028 近似 L4 = 7 係 pi-近似偽影")
print("-" * 76)
ratio = Nd/(2*pi)
print(f"    44/(2*pi) = {nstr(ratio)}   vs L4 = 7   dev = {nstr(abs(ratio-7)/7*100, 6)} %")
print(f"    22/7 = {nstr(mpf(22)/7)} vs pi = {nstr(pi)}  dev = {nstr(abs(mpf(22)/7-pi)/pi*100, 6)} %")
chk("標記為偽影 (44/7 約 2*pi 係 22/7 經典 pi-近似, 非結構)",
    abs(ratio-7)/7 < mpf('1e-3') and abs(mpf(22)/7-pi)/pi < mpf('1e-3'),
    "結論: 不採用 44/(2pi) = L4 之分解; Gamma 之結構形式用 N_d/T_ring")

# ============================================================
print("\n[6] 與 Route B (模態色散) 之關係")
print("-" * 76)
dt_over_T = mpf('0.3551')
print(f"    Route B 疊加分離時間 max dt/T_ring = {dt_over_T}")
print(f"    讀數週期 T_ring/N_d              = {nstr(mpf(1)/Nd, 8)} T_ring")
chk("讀數週期 << 色散分離時間 (兩種機制時間尺度分離)",
    mpf(1)/Nd < dt_over_T,
    f"{nstr(mpf(1)/Nd,6)} << {nstr(dt_over_T,6)} : 塌縮先於空間分離")

# ============================================================
print("\n" + "=" * 76)
print(f"Script 11 完成: {PASS} PASS / {FAIL} FAIL")
print("=" * 76)
print(f"\n  ★ 退相干速率: Gamma = N_d/T_ring = {nstr(Gamma)} s^-1")
print(f"  ★ 退相干時間: tau   = T_ring/N_d = {nstr(tau/Gyr_s)} Gyr")
print(f"  ★ 等價: N_d f_ring = N_d w_ring/(2pi) = f_44/2 = c/(2 lam_sync)")
