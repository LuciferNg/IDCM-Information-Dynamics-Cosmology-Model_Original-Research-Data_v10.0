#!/usr/bin/env python3
"""
O99-v2.0 — scripts/11: σ_8 首推攻堅 — K_Tree 自相似外推到 8 Mpc
=================================================================
精確定位: K_Chain 網格覆蓋 k ∈ [2.4e-4, 0.0107] Mpc⁻¹(44-site, spacing 46.9 Mpc)
σ_8 需要 k ~ 0.39 h/Mpc (8 h⁻¹ Mpc) —— 遠超 K_Chain 最短波.
但 O83 有「K_Tree 自相似」: 每層 4^ℓ 投影,振幅母函數 A_{2k}/A₁=((k+1)/(4k-1))².
=> 唔係「放棄」sigma: 用 K_Tree 自相似把小尺度振幅 通過 4^ℓ 層續到 8 Mpc.

σ_8² = ∫ (k³/2π²)·P(k)·W_8(k)² dk/k   (8 h⁻¹Mpc 加窗球)
IDCM 若 P(k) = A_s · (k/k_piv)^(n_st-1) · T²(k) 由層階自相似給出.

呢份 script 做「誠實嘅 K_Tree 自相似擬合」: 睇 冪側 extrapolate 去 8 個層到唔到 σ_8~0.8.
若 唔到 -> 標記 🔴 真 gap (冇數games). 若 path 通 -> v2.0 最後一環.
"""

import math, json, os
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__)) + "/../data/"
log = print
res = []
def fc(lbl, ok, dt=""):
    res.append((lbl, ok)); log(("PASS" if ok else "FAIL") + " | " + lbl + (("  " + dt) if dt else ""))

PHI = (1+math.sqrt(5))/2
N_d = 44
sigma8_obs = 0.81   # Planck

# --- K_Chain 網格尺度 ---
R_world = 4129.94
L_ring = 2*math.pi*R_world          # 25949 Mpc
lam_max = L_ring/44                # 44-tone 最短?? 唔.. 44 site 係 Σ = 44 modes
# K_Chain: 44 modes, wavenumber k_n = n * 2π / L_ring
k_min = 2*math.pi/L_ring            # n=1
k_max = 44*2*math.pi/L_ring         # n=44  ~0.01065
k8 = 2*math.pi/8.0                  # 8 Mpc -> k~0.785?? 個 R=8 shift 窗
# 更正: σ_8 R=8 h⁻¹ Mpc ->  In 落 積分 是 k ∈ ~[0.01, 1] Mpc. 所以 sub-grid。
print(f"  K_Chain k range: [{k_max:.2e}, {k_min:.4f}] Mpc⁻¹ ... current: {k_min=}")
print(f"  σ_8 需 GB: k_eff ~ 0.4 (8 Mpc) -> IDCM shortest {k_max:.4f} 差 {0.4/k_max:.0f}x")
fc("真 sub-grid: IDCM 最短 k_max vs σ_8 需要 k_eff', 差 幾十", k_max > 0.39)

# --- K_Tree 自相似 外推 ---
# O83 振幅母神: A_{2k}/A₁ = ((k+1)/(4k-1))², 每層 4^ℓ
# 自相似: 層 ℓ+1 之 振幅比 前一層 (4k-1)-(k+1)²... 用 رFRAC
#   amplitude 每 4^ℓ 縮因: P(4k) = 4^-(n) P(k) (白置自相似應 ≈樣, 要測試)
# 用母神從 acoustic (k_A~0.05) 位 4 級到 8 Mpc
kA = 0.05  # 声波尺度 (~100 Mpc, CMB peak中層)
for LL in [1,2,3,4]:
    scale = 4**LL
    kk = kA*scale
    A = ((scale+1)/(4*scale-1))**2   # 母神 (假設 idx)
    print(f"  4^{LL}層: k={kk:.3f} amplitude={A:.4f}  (母 F)")

# σ_8 需要 cumulative 積 k³ P(k) 加窗. 
# 直接: σ_8 ~ ∫d lnk k³P(k) W9(R8) ~ (amplitude@k8)²×ln·ref
# ID k8>.不reachable by lattice, 自相似 EE extrapolation 唔受 lattice 格限制——可試.
A8 = ((8+1)/(4*8-1))**2   # = 81/961 = 0.0843
print(f"\n  母神在8(Mapping中的r) ~ {A8:.4f} (假): ...")

# 用 最小片格點 推最大的那 驰離
# Conserv: k_max=0 = 0.0101, 間 8=0.39 -> need 5.6 級 of 4^3.7
nlevels_needed = math.log(0.39/k_max)/math.log(4)
print(f"  需 {nlevels_needed:.1f} 個 4^層 to reach 8 Mk -> >{1} (深層階)")
sd_est = math.sqrt(A8) if A8>0 else 0
print(f"  => σ_8(R~8) ~ {sd_est:.3f} (if single-not lattice; 真實不知)")

fc("σ_8 真 gap: 8 M ∉ K_Grid (sub-grid 40×) — 自相似外推係 conjecture 唔係 derivation",
   False, "外推不係首推")

# 誠實結論:
print("""
  ★★ 誠實判決: σ_8 攻堅(scripts/11):
  - 直接 lattice: K_Chain 最短k~0.010, σ_8 需 0.39 -> 40× 出格。 不可能直接.
  - K_Tree 自相似外推: 係「conjecture」唔係「首推」—— 可以 scale down 到 8 個抦層，
    但 amplitude normalization (σ_8=0.8 vs IDCM 0.086) 需要 ~9.3× 修正而無結構來源.
  - 因此: 路線 C「O86 growth D(z)」唔夠 (O86 無 linear perturbation, 且 σ_8 = P(k)振幅
    唔係 growth 只有); 需另 步驟: BOSS ξ(s) 實測校準 (方向 E) 先行, 然後同 O83 母神比較。
  - 暫: A_φφ σ_8 因子 ❂ 未閉合 —— 誠實 標記。
""")

fail = sum(1 for _, ok in res if not ok)
log("==== %d/%d PASS ====" % (len(res) - fail, len(res)))
dish = {
    "sigma8_gap": "K_Chain sub-grid 40x; O91 script sigma=0.086 vs obs 0.8",
    "k_max_chain": float(k_max),
    "k_8_eff": 0.39,
    "levels_needed": float(nlevels_needed),
    "routeC": "O86 closed #6 RED: W-field perturbation out of scope",
    "needs": "BOSS D(z) calibration or perturbation theory",
    "status": "RED_not_closed",
    "n_pass": len(res) - fail,
    "n_tot": len(res),
}
jp = OUT + "11_sigma8_attack.json"
with open(jp, "w") as f:
    json.dump(dish, f, indent=2)
exit(0 if fail == 0 else 1)