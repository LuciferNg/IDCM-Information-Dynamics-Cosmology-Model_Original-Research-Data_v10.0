#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60 FINAL VERIFIER — 逐項核對記錄文檔所有數字
===============================================
獨立重算 (唔重用其他 script code), 核對:
[1] 時標常數
[2] 模式週期
[3] 合併事件匹配
[4] 統計
[5] M31 RAR
[6] 質量階梯
[7] 軌道週期
[8] VPOS 幾何
"""
import math
import numpy as np

print("=" * 72)
print("O60 FINAL VERIFIER (2026-08-24)")
print("=" * 72)
errors = []

def check(label, got, expect, tol, unit=""):
    dev = abs(got - expect)
    ok = dev <= tol
    status = "✅" if ok else "❌"
    if not ok:
        errors.append(label)
    print(f"  {status} {label}: {got:.4f}{unit} vs 期望 {expect:.4f}{unit} (Δ={dev:.4f}, tol={tol})")
    return ok

# [1] 時標
print("\n[1] 時標常數:")
c = 299792.458; R_H = 4129.94
tau = R_H * 3.085677581e19 / c / 3.15576e7 / 1e9
T_sync = 2 * math.pi * tau
check("τ = R_H/c", tau, 13.4701, 0.001, "Gyr")
check("T_sync = 2πτ", T_sync, 84.6349, 0.01, "Gyr")
step = T_sync / 88
check("step = T_sync/88", step, 0.96176, 0.001, "Gyr")
check("τ/step", tau/step, 14.0056, 0.01)

# [2] 模式週期
print("\n[2] 模式週期 T_n = T_sync·sin(π/88)/sin(nπ/88):")
def T_n(n):
    return T_sync * math.sin(math.pi/88) / math.sin(math.pi*n/88)
T_7 = T_n(7); T_8 = T_n(8); T_15 = T_n(15)
T_6 = T_n(6); T_11 = T_n(11)
check("T_7", T_7, 12.215, 0.005, "Gyr")
check("T_8", T_8, 10.722, 0.005, "Gyr")
check("T_15", T_15, 5.920, 0.005, "Gyr")
check("T_6", T_6, 14.211, 0.005, "Gyr")
check("T_11", T_11, 7.894, 0.005, "Gyr")
check("7+8=15 和頻", 7+8, 15, 0, "")

# [3] 合併事件匹配
print("\n[3] 合併事件最佳匹配:")
events = {"LKH": 12.3, "GSE": 10.5, "Sgr": 6.0, "t_iso": 14.48, "M31 盤": 6.0, "M31 合併": 8.0}
expected_n = {"LKH": 7, "GSE": 8, "Sgr": 15, "t_iso": 6, "M31 盤": 15, "M31 合併": 11}
for name, t in events.items():
    best_n = min(range(1, 45), key=lambda n: abs(T_n(n) - t)/t)
    dev = abs(T_n(best_n) - t)/t*100
    exp_n = expected_n[name]
    ok = best_n == exp_n
    if not ok: errors.append(f"event {name}")
    print(f"  {'✅' if ok else '❌'} {name:10s}: {t:5.2f} → n={best_n:2d} (期望 {exp_n}), T={T_n(best_n):6.3f}, 偏差 {dev:5.2f}%")

# [4] 統計: 6 事件 4 強命中 {7,8,15}
print("\n[4] 統計:")
strong = [name for name in ["LKH","GSE","Sgr","t_iso","M31 盤","M31 合併"]
          if expected_n[name] in {7,8,15} and abs(T_n(expected_n[name]) - events[name])/events[name]*100 < 3.0]
print(f"  強命中 (偏差<3%): {len(strong)}/6 → {strong}")
p_val = math.comb(6, len(strong)) * (3/44)**len(strong) * (41/44)**(6-len(strong))
print(f"  p ≈ {p_val:.2e} (期望 2.8e-4)")
check("4 強命中", len(strong), 4, 0, "個")

# [5] M31 RAR
print("\n[5] M31 RAR (Zhang+2024 質量模型):")
G = 4.3009e-6; a0 = 1.1225e-10; kpc_m = 3.085677581e19
Mb = 10**10.57; Md = 10**10.86; q = 0.84; a_mn = 5.77; b_mn = 0.55
def V_rar(R):
    vb2 = G*Mb*R/(R+q)**2
    s = a_mn + b_mn
    vd2 = G*Md*R**2/(R**2+s**2)**1.5
    gbar = (vb2+vd2)/R*1e6/kpc_m
    gobs = gbar*(1+math.sqrt(1+4*a0/gbar))/2
    return math.sqrt(gobs*R*kpc_m)/1e3
# 內圈 χ² (用 verifier 11 嘅 20 點)
obs_disk = [
    (1.86,223.8,10.72),(3.19,226.79,7.96),(4.23,213.74,8.17),(5.32,212.54,7.55),
    (6.27,221.94,7.2),(7.2,223.3,8.49),(8.2,225.97,9.28),(9.14,226.63,9.07),
    (9.93,223.45,10.29),(10.62,221.25,10.24),(11.25,221.17,11.16),(11.83,213.58,9.75),
    (12.48,215.04,12.67),(13.37,215.12,12.82),(14.29,217.92,13.52),(15.2,215.97,13.09),
    (16.08,223.22,13.07),(17.21,213.32,13.44),(18.31,213.85,15.37),(19.38,199.73,15.19),
]
chi2 = sum(((V_rar(R)-vc)/err)**2 for R,vc,err in obs_disk)
chi2_dof = chi2/len(obs_disk)
print(f"  R≤20 kpc χ²/dof = {chi2_dof:.2f} (期望 ~1.0, 含MC 0.19)")
check("RAR 內圈 χ²/dof", chi2_dof, 1.0, 0.3)
V25, V125 = V_rar(25), V_rar(125)
drop_idcm = (V25-V125)/V25*100
print(f"  V(25)={V25:.1f}, V(125)={V125:.1f}, IDCM 下跌 {drop_idcm:.1f}%")
check("IDCM 外圈下跌 ~7%", drop_idcm, 7, 2)

# [6] 質量階梯
print("\n[6] 質量階梯:")
M0 = 1.187e18
M3, M4, M5 = M0/64**3, M0/64**4, M0/64**5
check("d=3", M3/1e12, 4.528, 0.01, "e12")
check("d=4", M4/1e10, 7.075, 0.01, "e10")
check("d=5", M5/1e9, 1.105, 0.01, "e9")
# 合併質量比
f_star = 1/29
M_lkh_tot = 5e8/f_star
d_lkh = math.log(M0/M_lkh_tot)/math.log(64)
ratio = M_lkh_tot/6e10
print(f"  LKH M_tot={M_lkh_tot:.2e}, d={d_lkh:.2f} (期望 4.38)")
check("LKH d 級", d_lkh, 4.38, 0.05)
print(f"  合併質量比 {ratio:.2f} (期望 0.24-0.25)")
check("質量比 0.2-0.3", ratio, 0.245, 0.06)

# [7] 軌道週期
print("\n[7] M31-MW 軌道:")
D = 780.0; M_tot = 2.2e12
T_s = 2*math.pi*math.sqrt(D**3/(G*M_tot))*3.0857e16
T_Gyr = T_s/3.15576e16
check("軌道週期", T_Gyr, 43.5, 0.1, "Gyr")
check("T_orbit/T_sync", T_Gyr/T_sync, 0.514, 0.005)

# [8] VPOS
print("\n[8] VPOS 幾何:")
def gal_vec(l, b):
    l, b = math.radians(l), math.radians(b)
    return np.array([math.cos(b)*math.cos(l), math.cos(b)*math.sin(l), math.sin(b)])
def ang(v1, v2):
    return math.degrees(math.acos(np.clip(np.dot(v1,v2), -1, 1)))
v_vpos = gal_vec(188.5, -13.5)
v_m31 = gal_vec(121.17, -21.57)
a_vm = ang(v_vpos, v_m31)
check("VPOS vs M31 夾角", a_vm, 64.3, 0.5, "°")
v_disk = np.array([0,0,1])
a_vd = ang(v_vpos, v_disk)
check("VPOS vs 銀河盤", a_vd, 103.5, 0.5, "°")

# 總結
print(f"\n{'='*72}")
if errors:
    print(f"❌ {len(errors)} 項 FAIL: {errors}")
else:
    print("✅ 全部 28 項核對 PASS — 記錄文檔數字正確!")
print(f"{'='*72}")
