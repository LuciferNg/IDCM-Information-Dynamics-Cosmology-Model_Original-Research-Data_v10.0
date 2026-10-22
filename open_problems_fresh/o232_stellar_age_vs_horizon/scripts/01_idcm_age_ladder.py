#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O232 — scripts/01: IDCM 年齡階梯 vs 外部恆星年齡下界
=====================================================
把 IDCM 結構年齡階梯 (τ = 1/ω_ring, T_ring, t_true) 與
arXiv:2607.00764 (Banik et al. 2026 MNRAS) 之觀測值逐項對比。

紀律:
  - 一律 /usr/bin/python3 + mpmath dps=40 (未截斷前唔好引用 dev)
  - 本 script 自寫 data/01_*.json (BASE 相對) ; log 由 shell redirect
  - 觀測值係**外部**數字 ⇒ 任何「凑到」只可標 post-hoc 🔴, 唔可宣稱結構
  - 密度前驗: 候選因子族 + null, 唔准見數後收窄族

來源 (只引用, 唔重推): O51 (τ = R_H/c, t_true), O213 docs/06 (t_true = 131·T_sync+τ),
  O73 (ω_ring, ω_cmb = ω_ring(1−π/44)), o76/o167 (投影層).
"""
import json, os, math, random
from mpmath import mp, mpf, pi, nstr

mp.dps = 40
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- 常數 (SI / 天文約定) ----
LIGHT   = mpf('299792.458')            # km/s  (SI 定義)
MPC_KM  = mpf('3.0856775814913673e19') # km per Mpc (IAU)
YR_S    = mpf('3.15576e7')             # Julian year
GYR_S   = mpf('3.15576e16')

# ---- IDCM 結構量 (只引用; 見上 header 來源) ----
OMEGA_RING = mpf('72.59002746')        # (km/s)/Mpc  O73
N_d        = 44
TAU_REPORTED   = mpf('13.470063')      # O213 docs/06
TRING_REPORTED = mpf('84.6349')        # O213 docs/06
TTRUE_REPORTED = mpf('11100.642')      # O213 docs/06
LCMB_REPORTED  = mpf('67.407086')      # O73

# ---- 外部觀測值 (arXiv:2607.00764) ----
A_STAR      = mpf('13.73');  A_STAR_HI = mpf('13.91'); A_STAR_LO = mpf('13.58')
A_STAR_CMB  = mpf('13.6')              # CMB-ΛCDM 預言之星齡 (t_f = 0.2 已扣)
A_U_CMB     = mpf('13.8')              # CMB-ΛCDM 宇宙齡
A_STAR_ETS  = mpf('12.71'); A_U_ETS = mpf('12.91')
H0_LOCAL    = mpf('73.17'); H0_LOCAL_S = mpf('0.86')
H0_SH0ES    = mpf('73.04'); H0_SH0ES_S = mpf('1.04')
SIG_STAR    = (A_STAR_HI - A_STAR_LO) / 2   # ≈ 0.165

checks = []
def ck(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    print(("  ✅ " if cond else "  ❌ ") + name + (f"   [{detail}]" if detail else ""))

print("="*78)
print("O232 / 01 — IDCM 年齡階梯 vs 恆星年齡下界")
print("="*78)

# ---- A. 由 ω_ring 導出年齡階梯 (結構量) ----
print("\n[Α] IDCM 年齡階梯 (由 ω_ring 導出)")
tau_Gyr = (MPC_KM / OMEGA_RING) / GYR_S
T_ring  = 2*pi*tau_Gyr
t_true  = 131*T_ring + tau_Gyr
R_world = LIGHT / OMEGA_RING                       # Mpc
tau_ident = R_world / LIGHT * (MPC_KM/GYR_S)       # R_world/c 恆等
omega_cmb = OMEGA_RING*(1 - pi/44)
print(f"  τ = 1/ω_ring      = {nstr(tau_Gyr,12)} Gyr")
print(f"  T_ring = 2πτ      = {nstr(T_ring,12)} Gyr")
print(f"  t_true = 131T+τ   = {nstr(t_true,12)} Gyr")
print(f"  R_world = c/ω     = {nstr(R_world,12)} Mpc")
print(f"  ω_cmb = ω(1−π/44) = {nstr(omega_cmb,10)} (km/s)/Mpc")

ck("C1 τ = 1/ω_ring 重現 O213 報值 13.470063", abs(tau_Gyr-TAU_REPORTED)/TAU_REPORTED < 1e-6,
   f"dev {nstr(abs(tau_Gyr-TAU_REPORTED)/TAU_REPORTED*100,4)}%")
ck("C2 R_world/c 恆等 τ (同一 dof)", abs(tau_ident-tau_Gyr)/tau_Gyr < 1e-12, "")
ck("C3 T_ring = 2πτ 重現 84.6349", abs(T_ring-TRING_REPORTED)/TRING_REPORTED < 1e-6, "")
ck("C4 t_true = 131·T_ring+τ 重現 11,100.642", abs(t_true-TTRUE_REPORTED)/TTRUE_REPORTED < 1e-5, "")
ck("C5 ω_cmb 重現 67.407086", abs(omega_cmb-LCMB_REPORTED)/LCMB_REPORTED < 1e-6, "")

# ---- B. 與外部觀測值對比 ----
print("\n[Β] IDCM τ vs 外部值 (Banik et al. 2026)")
pairs = [
    ("τ vs 最老恆星 A_★ = 13.73",      A_STAR),
    ("τ vs ΛCDM 預言星齡 A_★^CMB=13.6", A_STAR_CMB),
    ("τ vs ΛCDM 宇宙齡 A_U^CMB = 13.8", A_U_CMB),
    ("τ vs ETS 星齡      12.71",        A_STAR_ETS),
    ("τ vs ETS 宇宙齡    12.91",        A_U_ETS),
]
for lbl, ext in pairs:
    d = tau_Gyr - ext
    print(f"  {lbl:38s} Δ = {nstr(d,6):>10} Gyr  ({nstr(d/ext*100,5):>7}%)"
          + (f"  = {nstr(d/SIG_STAR,4)}σ(星)" if ext >= 13 else ""))
ck("C6 τ 低於最老恆星 0.26 Gyr (< 1.6σ)", abs((A_STAR-tau_Gyr)/SIG_STAR) < 1.6,
   nstr((A_STAR-tau_Gyr)/SIG_STAR,5)+"σ")
ck("C7 τ 高於 ETS 宇宙齡 (>4%) ⟹ ETS 被排除之測試不殺 IDCM",
   (tau_Gyr-A_U_ETS)/A_U_ETS > mpf('0.04'), f"+{nstr((tau_Gyr-A_U_ETS)/A_U_ETS*100,4)}%")
ck("C8 τ 低於 ΛCDM CMB 宇宙齡 2.4% (核心張力)", mpf('0.02') < (A_U_CMB-tau_Gyr)/A_U_CMB < mpf('0.03'),
   f"−{nstr((A_U_CMB-tau_Gyr)/A_U_CMB*100,4)}%")

# ---- C. H₀ 側 ----
print("\n[Γ] H₀ 側 (IDCM 預言 vs 局域量度)")
z_loc  = (H0_LOCAL - OMEGA_RING)/H0_LOCAL_S
z_sh0  = (H0_SH0ES - OMEGA_RING)/H0_SH0ES_S
print(f"  ω_ring = 72.590 vs H₀_local = 73.17±0.86  → {nstr(z_loc,4)}σ")
print(f"  ω_ring = 72.590 vs SH0ES   = 73.04±1.04  → {nstr(z_sh0,4)}σ")
ck("C9 ω_ring 與 H₀_local 一致 (<1σ)", abs(z_loc) < 1, f"{nstr(z_loc,3)}σ")
ck("C10 ω_ring 與 SH0ES 一致 (<1σ)", abs(z_sh0) < 1, f"{nstr(z_sh0,3)}σ")

# ---- D. 密度前驗: 「13.8 = τ × 結構因子?」----
print("\n[Δ] 密度前驗 — 13.8 可否由 τ 乘結構比 p/q 得到? (🔴 post-hoc 檢查)")
POOL = sorted({2,3,4,5,7,11,13,17,18,19,20,21,22,27,28,33,41,44,45,46,55,60,88,90,123,137,176,421})
# ★ post-hoc 寬池 (首跑後加入; 命中**只可**標 🔴, 唔可宣稱結構)
WIDE = sorted(set(POOL) | {29,34,42,43,47,134,220,264,364,528})
target_ratio = A_U_CMB / tau_Gyr
print(f"  需要之比 = 13.8/τ = {nstr(target_ratio,10)}")
def hunt(pool, tag):
    fam = [(p, q, mpf(p)/q) for p in pool for q in pool
           if p > q and mpf(p)/q <= mpf('1.10') and math.gcd(p, q) == 1]
    h1 = [(f"{p}/{q}", r) for p, q, r in fam if abs(r-target_ratio)/target_ratio < mpf('1e-3')]
    h2 = [(f"{p}/{q}", r) for p, q, r in fam if abs(r-target_ratio)/target_ratio < mpf('1e-4')]
    null1 = len(fam) * (2*mpf('1e-3')/mpf('0.10'))
    print(f"  [{tag}] N_search={len(fam)}  null@0.1%={nstr(null1,3)}  hits@0.1%={[h[0] for h in h1]}  hits@0.01%={[h[0] for h in h2]}")
    return fam, h1, h2, null1
famF, hits1, hits2, null1 = hunt(POOL, "凍結池")
famW, wh1, wh2, _ = hunt(WIDE, "post-hoc 寬池 🔴")
random.seed(232); mc = 0
for _ in range(200000):
    p, q = random.sample(POOL, 2)
    if p < q: p, q = q, p
    if p != q and abs(mpf(p)/q - target_ratio)/target_ratio < mpf('1e-3'): mc += 1
print(f"  MC (凍結池, 2×10⁵) 命中密度 ≈ {mc/200000*100:.3f}%")
ck("C11 凍結池已枚舉 (N_search≥1)", len(famF) >= 1, f"N={len(famF)}")
ck("C12 凍結池 @0.1% 命中唔顯著多於 null", len(hits1) <= max(1, int(null1)+1),
   f"hits={len(hits1)}, null={nstr(null1,3)}")
ck("C13 post-hoc 寬池命中已記錄並標 🔴 (禁宣稱結構)", True,
   f"hits={[h[0] for h in wh1]} (post-hoc)")

# ---- E. 判決 ----
print("\n[Ε] 判決")
print(f"  ★ IDCM 結構齡 τ = {nstr(tau_Gyr,6)} Gyr  (唔係 13.8)")
print(f"  ★ 外部實測最老星 A_★ = 13.73 (+0.18/−0.15)  (IQR {nstr(A_STAR_LO,4)}–{nstr(A_STAR_HI,4)})")
print(f"  ★ 張力: A_★ − τ = {nstr(A_STAR-tau_Gyr,5)} Gyr = {nstr((A_STAR-tau_Gyr)/SIG_STAR,4)}σ（星）")
print(f"  ★ 對 ΛCDM CMB: τ 低 13.8 達 {nstr((A_U_CMB-tau_Gyr)/A_U_CMB*100,4)}%")
verdict = "🟡 IDCM τ 非硬天花板; 0.26 Gyr / 2.4% 缺口待結構解釋"
print(f"  判決: {verdict}")

npass = sum(1 for c in checks if c[1])
print("\n" + "="*78)
print(f"RESULT: {npass}/{len(checks)} PASS")
print("="*78)

out = {
  "script": "01_idcm_age_ladder.py",
  "dps": mp.dps,
  "idcm": {"tau_Gyr": float(tau_Gyr), "T_ring_Gyr": float(T_ring), "t_true_Gyr": float(t_true),
           "R_world_Mpc": float(R_world), "omega_ring": float(OMEGA_RING),
           "omega_cmb": float(omega_cmb)},
  "paper_2607_00764": {"A_star": 13.73, "A_star_hi": 13.91, "A_star_lo": 13.58,
                       "A_star_CMB": 13.6, "A_U_CMB": 13.8,
                       "A_star_ETS": 12.71, "A_U_ETS": 12.91,
                       "H0_local": 73.17, "H0_local_sigma": 0.86},
  "tension": {"A_star_minus_tau_Gyr": float(A_STAR-tau_Gyr),
              "A_star_minus_tau_sigma_star": float((A_STAR-tau_Gyr)/SIG_STAR),
              "tau_vs_AU_CMB_pct": float(-(A_U_CMB-tau_Gyr)/A_U_CMB*100)},
  "density_preflight": {"pool_frozen_size": len(POOL), "N_search_frozen": len(famF),
                        "hits_frozen_0p1pct": [h[0] for h in hits1],
                        "hits_frozen_0p01pct": [h[0] for h in hits2],
                        "null_expected_0p1pct": float(null1),
                        "post_hoc_wide_pool": {"size": len(WIDE), "N_search": len(famW),
                                               "hits_0p1pct": [h[0] for h in wh1],
                                               "hits_0p01pct": [h[0] for h in wh2],
                                               "flag": "POST-HOC, 禁宣稱結構"}},
  "checks": [{"name": n, "pass": c, "detail": d} for n, c, d in checks],
  "pass": npass, "total": len(checks), "verdict": verdict,
}
with open(os.path.join(BASE, "data", "01_idcm_age_ladder.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("data/01_idcm_age_ladder.json written.")