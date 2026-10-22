#!/usr/bin/env python3
"""
O133 — scripts/03_pk_broadband.py (v3 最終)
============================================
P(k) broadband 形狀判定 — 誠實量化, 避免 slope-fit 範圍假象

v1/v2 教訓:
  - 9 峰全範圍 fit (k→0.53) 出現 −1.25≈−1.21 假閉合 → 6/9 線超出 BOSS 數據!
  - BOSS 實際範圍 [0.079, 0.3] 只有 3 條 IDCM 線 (m=1,2,3): slope −0.67 vs −1.21

v3 方法 (穩健):
  [A] 用線位比值: r_m = P_IDCM(k_m)/P_obs(k_m) for m=1,2,3 (BOSS 範圍內)
      若形狀匹配 → r 常數 (只差 bias b²); 若 r ∝ k^q → 形狀差 k^q
  [B] BOSS 範圍內 slope 對照 (3 線 vs 連續)
  [C] 全範圍 slope (外推, 標記 🟡 冇數據覆蓋)
"""
import os, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")

R_world = 4129.94
h = 0.6727
res = []
def check(name, cond, detail=""):
    res.append(bool(cond))
    print(f"  [{'✅ PASS' if cond else '❌ FAIL'}] {name}  {detail}")

print("="*76)
print("  O133 — P(k) Broadband 形狀判定 (v3, 線位比值法)")
print("="*76)

def load_gm(path):
    rows=[l.split() for l in open(path) if l.strip() and not l.startswith('#')]
    return np.array([float(r[0]) for r in rows]), np.array([float(r[1]) for r in rows])

M=33; F6,F8=8,21
from math import comb
def ell_m(m):
    if m==5: return 44*(M-F6)+F8
    return 44*(M-comb(9-m,2)) + ((m-1)*9)%25
def A_m(m):
    if m==1: return 1.0
    if m%2==0:
        k=m//2; return ((k+1)/(4*k-1))**2
    return {3:4/9,5:3/14,7:1/7}.get(m,1/16)

# IDCM 線譜 P(k_m) = 2π²·Δ²_m/k_m³  ∝ A_m (已驗證 script02)
D1=5750.0; Tcmb=2.72548e6
ells=[ell_m(m) for m in range(1,10)]
k_m=np.array(ells)/R_world/h
A=np.array([A_m(m) for m in range(1,10)])

# ═══════════════════════════════════════════════════════════
# [A] 線位比值 (穩健核心)
# ═══════════════════════════════════════════════════════════
print("\n─── [A] 線位比值 r_m = P_IDCM/P_obs (k∈BOSS 範圍) ───")
for name, path in [("CMASS", "GilMarin_2016_CMASSDR12_measurement_monopole_post_recon.txt"),
                   ("LOWZ", "GilMarin_2016_LOWZDR12_measurement_power_spectrum_monopole_post_recon.txt")]:
    k, P = load_gm(os.path.join(DATA, path))
    print(f"\n  {name}:")
    rs=[]
    for i in range(3):   # m=1,2,3 喺 BOSS 範圍
        if k_m[i] < k.min() or k_m[i] > k.max(): continue
        P_obs = np.interp(k_m[i], k, P)
        r = A[i]*(k_m[i]**3/(2*np.pi**2))/P_obs   # P_IDCM/P_obs (P_IDCM∝A·k³係數)
        # 實際 P_IDCM = 2π²Δ²/k³, Δ² = 2ℓ⁴D1A(2ℓ+1)/(4πT²ℓ(ℓ+1))·...  — 用 script02 嘅 Δ² 值:
        # 直接用 v10 構建: P_Mpc3 (script02 data/02)
        rs.append((k_m[i], A[i], float(P_obs)))
        print(f"    m={i+1}: k={k_m[i]:.4f}  A={A[i]:.4f}  P_obs={P_obs:.0f}")
    # r 指數: P_IDCM∝A → r∝A/P_obs; 若 P_obs∝k^n → r∝k^(n_ID−n)
    if len(rs)>=3:
        ks2=np.array([r[0] for r in rs]); A2=np.array([r[1] for r in rs]); P2=np.array([r[2] for r in rs])
        q=np.polyfit(np.log(ks2), np.log(A2/P2),1)[0]   # r ∝ k^q
        print(f"    r ∝ k^q, q = {q:+.2f}  (q=0 → 形狀閉合)")
        if q > 0: print(f"    → IDCM 相對 BOSS 高 k 過強 (形狀太扁 Δn≈{q:+.2f})")

# ═══════════════════════════════════════════════════════════
# [B] BOSS 範圍內 slope (3 線 vs 連續)
# ═══════════════════════════════════════════════════════════
print("\n─── [B] BOSS 範圍 slope 對照 (k∈[0.079, 0.3]) ───")
sel = k_m <= 0.30
n_A_in = np.polyfit(np.log(k_m[sel]), np.log(A[sel]),1)[0]
print(f"  IDCM 3 線 (m=1,2,3): n = {n_A_in:+.2f}")
n_obs=[]
for name, path in [("CMASS", "GilMarin_2016_CMASSDR12_measurement_monopole_post_recon.txt"),
                   ("LOWZ", "GilMarin_2016_LOWZDR12_measurement_power_spectrum_monopole_post_recon.txt")]:
    k, P = load_gm(os.path.join(DATA, path))
    m=(k>=0.079)&(k<=0.30)
    n_obs.append(np.polyfit(np.log(k[m]), np.log(P[m]),1)[0])
n_ref=np.mean(n_obs)
print(f"  BOSS 觀測 (k∈[0.079,0.3]): n = {n_ref:+.2f}  (CMASS {n_obs[0]:+.2f}, LOWZ {n_obs[1]:+.2f})")
d_in = n_A_in - n_ref
print(f"  Δn(in-range) = {d_in:+.2f}")
check("B1 in-range 形狀閉合 |Δn|<0.15", abs(d_in)<0.15, f"Δn={d_in:+.2f}")

# ═══════════════════════════════════════════════════════════
# [C] 全範圍 slope (外推標記)
# ═══════════════════════════════════════════════════════════
print("\n─── [C] 全範圍 slope (9 峰, 外推) ───")
n_A_full = np.polyfit(np.log(k_m), np.log(A),1)[0]
print(f"  IDCM 9 峰: n = {n_A_full:+.2f} (6/9 線 k>0.3, 超出 BOSS)")
print(f"  vs BOSS in-range {n_ref:+.2f}: Δn = {n_A_full-n_ref:+.2f}")
check("C1 全範圍閉合 (外推, 標記🟡)", abs(n_A_full-n_ref)<0.10,
      f"Δn={n_A_full-n_ref:+.2f} (外推)")

# ═══════════════════════════════════════════════════════════
# [D] 缺口結構化: 需要嘅額外 steepening
# ═══════════════════════════════════════════════════════════
print("\n─── [D] 缺口量化 + 候選來源 ───")
print(f"  in-range 缺口: P_IDCM ∝ k^{n_A_in:+.2f}, 觀測 ∝ k^{n_ref:+.2f}")
print(f"  需要額外 steepening (k^{d_in:.2f}) 令 IDCM 匹配")
print(f"  候選:")
print(f"   1. O86 W-field 線性微擾轉換 (未建立) — 官方標記 🔴")
print(f"   2. 星系 bias b²(k) — 大尺度常數, k>0.08 準非線性區或 scale-dependent (觀測即含)")
print(f"   3. ℳ 需加 k 依賴修正 (超出 2ℓ² Poisson+SW) — 需結構推導")
d_abs = abs(d_in)
check("D1 缺口 ≈ 結構值? (1/2=0.5, φ⁻¹=0.618)", min(abs(d_abs-0.5),abs(d_abs-0.618))<0.08,
      f"|Δn|={d_abs:.3f}")

json.dump({"inrange": {"idcm_n": n_A_in, "boss_n": n_ref, "delta_n": d_in, "cmass_n": n_obs[0], "lowz_n": n_obs[1]},
           "fullrange": {"idcm_n": n_A_full, "note": "6/9 lines k>0.3 out of BOSS range"},
           "line_ratios_q": None,
           "checks": res},
          open(os.path.join(DATA,"03_pk_broadband.json"),"w"), indent=2, default=float)

n_pass=sum(res); n_tot=len(res)
print("\n"+"="*76)
print(f"  RESULT: {n_pass}/{n_tot} PASS")
print("="*76)
exit(0)