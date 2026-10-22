#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O127 / scripts/03_xi2_structural_derivation.py
==============================================
P2: ξ₂ 各向異性嘅結構源頭 — 由 IDCM 紅移-距離律第一性推導 RSD kernel

IDCM:
  紅移 = 尺度階  1 + z = 4^ℓ   (O76)
  距離律        D(ℓ) = R_world (1 − 4^{−ℓ}) E(ℓ),  E(ℓ) = ℓ + 1.11911398 (O76/O169)
  本動速度 v_r → 1 + z_obs = 4^ℓ (1 + v_r/c) ⟹ δℓ = v_r/(c ln4)  (★ z-無關)
  觀測位移      δD = K(z)·v_r,  K(z) ≡ (dD/dℓ)/(c ln4)
ΛCDM 對照: δs = v_r (1+z)/H(z) ⟹ K_Λ(z) = (1+z)/H(z)

★ IDCM 冇 Hubble flow ⟹ 冇 Hubble drag ⟹ RSD kernel 完全由紅移-距離律決定。
"""
import numpy as np, os, json
import mpmath as mpm
mp = mpm.mp; mp.dps = 40

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
PASS, FAIL = [], []
def chk(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f"  | {d}" if d else ""))

def load_xi(fn):
    return np.array([[float(x) for x in l.split()]
                     for l in open(os.path.join(RAW, fn)) if not l.startswith("#") and l.strip()])

C_KMS, W_RING = 299792.458, 72.59
R_WORLD = C_KMS / W_RING
LN4 = float(mp.log(4)); E0 = 1.11911398

print("="*78); print("  O127 / 03 — P2: ξ₂ 結構源頭 (IDCM RSD kernel)"); print("="*78)

def ell(z): return float(mp.log(1+z)/mp.log(4))
def dD_dell(z):
    l = ell(z); f = 4.0**(-l)
    return R_WORLD*(f*LN4*(l+E0) + (1-f))
def K_idcm(z): return dD_dell(z)/(C_KMS*LN4)

Om, h_l = 0.31, 0.676
H0 = 100*h_l
def K_lcdm(z): return (1+z)/(H0*np.sqrt(Om*(1+z)**3 + (1-Om)))

print(f"\n[A] IDCM RSD kernel (第一性推導)")
print(f"    δℓ = v_r/(c ln4)  ⟹  δD = (dD/dℓ)·δℓ = K(z)·v_r")
print(f"\n    {'z':>6} {'ℓ':>8} {'dD/dℓ':>10} {'K_IDCM':>10} {'K_ΛCDM':>10} {'R':>8}")
zs = [0.0, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 2.33]
Rtab = {}
for z in zs:
    R = K_idcm(z)/K_lcdm(z); Rtab[z] = R
    print(f"    {z:6.2f} {ell(z):8.4f} {dD_dell(z):10.1f} {K_idcm(z)*1000:10.3f} {K_lcdm(z)*1000:10.3f} {R:8.4f}")
print("    (K: Mpc per 1000 km/s)")

chk("K_IDCM(0) = R_world·E₀/c (解析)", abs(K_idcm(0) - R_WORLD*E0/C_KMS) < 1e-12, f"{K_idcm(0)*1000:.4f}")
zmin = min(Rtab, key=lambda z: Rtab[z])
chk("★ R(z) 喺 z∈[0.3,1.0] 有極小 (非單調) — 鑑別力最弱處正係 LRG 紅移",
    0.3 <= zmin <= 1.0, f"R_min={Rtab[zmin]:.4f} @ z={zmin}")
chk("★ z<1.5 內 |R−1| < 5% ⟹ eBOSS/DESI LRG 無法鑑別", max(abs(Rtab[z]-1) for z in [0.3,0.5,0.7,1.0]) < 0.05,
    f"max|R−1| = {max(abs(Rtab[z]-1) for z in [0.3,0.5,0.7,1.0])*100:.2f}%")
chk("★ R(2.33) > 1.05 (Lyα 紅移 kernel 增強 ~7%)", Rtab[2.33] > 1.05, f"R(2.33)={Rtab[2.33]:.4f}")
chk("R(0) ≈ 1 (低 z 兩框架接近)", abs(Rtab[0.0]-1) < 0.1, f"R(0)={Rtab[0.0]:.4f}")

# ---------------------------------------------------------------
print(f"\n[B] eBOSS DR16 LRG ξ₂/ξ₀ 實測 (pre & post recon)")
Dp = load_xi("Data_LRGxi_NGCSGC_0.6z1.0_prerecon.txt")
D = load_xi("Data_LRGxi_NGCSGC_0.6z1.0_postrecon.txt")

def ratio(D, tag, lo=37.5, hi=80.0):
    s, x0, e0, x2, e2 = D[:,0], D[:,1], D[:,2], D[:,3], D[:,4]
    m = (s >= lo) & (s <= hi)
    r = x2[m]/x0[m]
    er = np.abs(r)*np.sqrt((e2[m]/x2[m])**2 + (e0[m]/x0[m])**2)
    w = 1/er**2
    rm = float(np.sum(w*r)/np.sum(w)); erm = float(1/np.sqrt(np.sum(w)))
    print(f"    {tag} (s∈[{lo},{hi}], {m.sum()} bins): <ξ₂/ξ₀> = {rm:+.4f} ± {erm:.4f}")
    return rm, erm

r_pre, e_pre = ratio(Dp, "pre-recon ")
r_post, e_post = ratio(D, "post-recon")
print(f"    (pre-recon ξ₂<0 = RSD 壓縮視線; post-recon ξ₂>0 — 同 BOSS DR12 Ross+2016 一致)")

chk("pre-recon <ξ₂/ξ₀> < 0 (RSD 定性正確)", r_pre < 0, f"{r_pre:+.4f}")
chk("post-recon <ξ₂/ξ₀> > 0 且細 (recon 後 BAO 尺度)", 0 < r_post < 1.5, f"{r_post:+.4f}")

# 線性 Kaiser 對照
def kaiser(b): return -(4/3*b + 4/7*b**2)/(1 + 2/3*b + 1/5*b**2)
print(f"\n    線性 Kaiser ξ₂/ξ₀: β=0.397 (文獻 fσ8/bσ8) → {kaiser(0.397):+.4f}")
print(f"    實測 pre-recon {r_pre:+.3f} ≫ |Kaiser| ⟹ 非線性 RSD 主導, 非零參數檢定")
chk("實測 |ξ₂/ξ₀| 大於線性 Kaiser ⟹ 數據唔能乾淨檢定 kernel",
    abs(r_pre) > abs(kaiser(0.397)), f"obs={r_pre:+.3f} vs Kaiser={kaiser(0.397):+.3f}")

# ---------------------------------------------------------------
print(f"\n[C] 裁定")
print(f"    (1) IDCM RSD kernel K(z) 由紅移-距離律結構推導 (新結果)")
print(f"    (2) R(z)=K_IDCM/K_ΛCDM: {Rtab[0.0]:.3f}(z=0) → {Rtab[0.7]:.3f}(z=0.7) → {Rtab[2.33]:.3f}(z=2.33)")
print(f"    (3) z<1.5: |R−1|<5% ⟹ eBOSS/DESI LRG ξ₂ 無法鑑別 IDCM vs ΛCDM")
print(f"    (4) IDCM 速度場振幅 (growth) 未閉合 ⟹ 完整 ξ₂ 振幅 🟡")
print(f"    (5) 唯一 IDCM 特異預言喺 z>1.5 (Lyα, R≈1.07) — 弱信號")

out = dict(K_ratio={str(k): v for k, v in Rtab.items()}, R_min_z=float(zmin), R_min=float(Rtab[zmin]),
           xi2_xi0_prerecon=r_pre, xi2_xi0_postrecon=r_post,
           kaiser_beta0397=kaiser(0.397))
json.dump(out, open(os.path.join(BASE, "data", "03_results.json"), "w"), indent=2)

print("\n" + "="*78)
print(f"  RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("  FAILED: " + ", ".join(FAIL))
print("="*78)
