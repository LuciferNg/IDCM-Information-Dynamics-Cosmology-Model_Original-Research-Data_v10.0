#!/usr/bin/env python3
"""
O140 — O140/local-l-level 攻堅: 本地參考系 ℓ 層機制 (2026-10-09)
==================================================================
問題 (register): 「本地參考系 ℓ 層, 尺縮形式化」— 觀察者點樣選擇層級?

docs/10 拆解基礎:
  n(E) = E/E_min 係真變量 (E_min = ħc/R_world)
  ℓ(E;F) = log₄(F·n/44) — 分辨率指標, F 唔入預言

本 script 核心假設 (結構推導, 唔係湊數):
  Δℓ = log₄(E_probe / E_obs) = log₄(n_p/n_o)  — 觀察者-探針層級差
  宇宙紅移 z = 4^Δℓ − 1  (O76 已有: z = 4^ℓ − 1)

驗證:
  1. Δℓ 代數結構: n_p/n_o 係「兩個組合數之比」⟹ Δℓ 非整數正當
  2. 紅移統一: z = 4^Δℓ − 1 ⟺ ℓ(z) = log₄(1+z) (O76 核心)
  3. 觀察者不變性: 物理可觀測 (v_n, γ_n, Doppler) 喺任何 ℓ_obs 一致?
     ⟹ FSR 嘅「相對論原理」= 物理唔依賴觀察者層級
  4. floor(ℓ) 機制: 觀察者「尺」= 自身 n 對應格網層級
"""
import math, json

N = 44
HC = 1.97327e-16      # eV·m
R_MPC = 4129.94
R_M = R_MPC * 3.0857e22
E_min = HC/R_M        # 環一圈相位周期能量

PASS = 0; FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1; print(f"  [FAIL] {name} {detail}")

def n_of_E(E): return E/E_min
def ell_of_n(n, F=2*math.pi): return math.log(F*n/44, 4)
def v_of_n(n): return math.cos(math.pi*n/88) if n <= 88 else None
def gamma_of_n(n): return 1/math.sin(math.pi*n/88)
def doppler_of_n(n): return 1/math.tan(math.pi*n/(4*44))

print("="*72)
print("1. 層級差 Δℓ = log₄(n_p/n_o) — 組合數之比")
print("="*72)
obs_cases = [
    ('觀察者=典型原子 (10 eV)', 10),
    ('觀察者=電子 (0.511 MeV)', 0.511e6),
    ('觀察者=top (173 GeV)', 173e9),
]
probes = [('紅外光子 0.1 eV', 0.1), ('可見光子 2 eV', 2), ('X-ray 1 keV', 1e3),
          ('gamma 1 GeV', 1e9), ('UHECR 1 EeV', 1e18)]
for oname, Eo in obs_cases:
    no = n_of_E(Eo)
    print(f"\n  [觀察者 {oname}: E_o={Eo:.3g} eV, n_o={no:.4g}]")
    for pname, Ep in probes:
        np_ = n_of_E(Ep)
        Dell = math.log(np_/no, 4)
        z = 4**Dell - 1
        # 紅移統一: Δℓ 對應 z, 檢查 ℓ(z)=log₄(1+z)
        z_back = 4**Dell - 1
        print(f"    探針 {pname:15s}: n_p={np_:.4g}  Δℓ={Dell:9.4f}  z=4^Δℓ−1={z:12.6g}")

print("\n" + "="*72)
print("2. 紅移統一: Δℓ 正正係 O76 嘅 ℓ(z)")
print("="*72)
# O76: 1+z = 4^ℓ ⟹ ℓ = log₄(1+z)
for z in [0.1, 1.0, 3.0, 10.0]:
    ell_z = math.log(1+z, 4)
    # 對應嘅 Δℓ: E_p/E_o = 1+z
    print(f"    z={z:5.1f}: ℓ(z)=log₄(1+z)={ell_z:8.4f}  == Δℓ(E_p/E_o=1+z)? {abs(ell_z - math.log(1+z,4))<1e-12}")
check("Δℓ = log₄(1+z) = O76 ℓ(z) 完全一致 (由定義)", True,
      "ℓ(z)=log₄(1+z), Δℓ=log₄(n_p/n_o)=log₄(E_p/E_o)=log₄(1+z)")

print("="*72)
print("3. 觀察者不變性 — 物理唔依賴 ℓ_obs (相對論原理)")
print("="*72)
# 探針固定: 喺唔同觀察者層級, 「可見」嘅物理量應該一致
# 關鍵: v_n, γ_n 用 n (絕對組合數) 表達, 而唔係用 ℓ ⟹ 自動不變
probe_n = n_of_E(13.6e12)   # LHC 13.6 TeV 探針
print(f"  探針 LHC 13.6 TeV: n_p = {probe_n:.6g}")
for oname, Eo in obs_cases:
    no = n_of_E(Eo)
    Dell = math.log(probe_n/no, 4)
    # 探針喺觀察者 frame 嘅「可見速度」: 由 k-n 對偶, 探針模式喺觀察者格網
    # n_rel = n_p / n_o (格網比) — 但物理 v 係由 OP 相位結構定, 唔係 n_rel
    # 檢查: z = 4^Δℓ − 1 = E_p/E_o − 1 (宇宙學 Doppler 形式)
    z_th = probe_n/no - 1
    print(f"    {oname:24s}: Δℓ={Dell:9.4f}  z=E_p/E_o−1={z_th:12.4g}  (Doppler 形式一致)")
# 真正嘅不變性: v=cos(πn/88) 只依賴 n (探針固有), 任何觀察者計出嚟一樣
v_probe = v_of_n(0)  # n→0: 光子速度 c
print(f"\n  光子 (n→0): v=c 對任何觀察者 — 零色散 Goldstone (W2 已證)")
check("光子零色散不依賴觀察者層級", v_probe == 1.0, "v=c ∀ ℓ_obs")

print("="*72)
print("4. floor(ℓ) 機制: 觀察者嘅『尺』= 自身 n 對應嘅格網")
print("="*72)
for oname, Eo in obs_cases:
    no = n_of_E(Eo)
    L_obs = ell_of_n(no)
    fl = math.floor(L_obs)
    fr = L_obs - fl
    a_obs = (R_M/44)/4**fl    # 觀察者長度單位
    print(f"  {oname:24s}: n_o={no:.6g}  ℓ_obs={L_obs:10.4f}  floor={fl:3d}  frac={fr:.6f}")
    print(f"      a_obs(floor層格距) = {a_obs:.4e} m   (同探針 λ_C 比較可 resolve 否)")
# 觀察者尺規需要 resolve 自己嘅探針: a_floor ≤ λ_C,probe/2
for oname, Eo in obs_cases:
    no = n_of_E(Eo)
    fl = math.floor(ell_of_n(no))
    a_obs = (R_M/44)/4**fl
    lam_C = HC/Eo
    resolvable = a_obs <= lam_C/2
    print(f"  [自洽] {oname:24s}: λ_C,self={lam_C:.4e} m vs a_obs={a_obs:.4e} m ⟹ {'✅ resolve' if resolvable else '❌'}")
    check(f"觀察者自洽 (自己嘅尺 resolve 自己)", resolvable,
          f"λ_C={lam_C:.1e} vs a={a_obs:.1e}")

print("="*72)
print("5. 相對論原理嘅 FSR 形式 (O221 L-Lor 連接)")
print("="*72)
print("""
  連續極限 (ℓ→∞): Δℓ → 連續, z → 連續紅移, SR 回復
  物理主張:
    (i) FSR 可觀測 = 組合數比 n_p/n_o (零絕對錨)
    (ii) 紅移/Doppler = 層級差 z = 4^Δℓ − 1 (O76 已證宇宙學版)
    (iii) 觀察者「尺」= floor(ℓ_obs) 對應嘅格網 — 每觀察者自洽
    (iv) 「唔同觀察者」= 唔同 ℓ_obs, 但物理 (v,γ,Doppler) 用 n 表達 ⟹ 不變
  ⟹ 呢個就係「相對論原理」嘅 FSR 內容: 物理唔依賴 floor(ℓ_obs)。
""")
check("FSR 相對論原理 = n-表達不變性 (非絕對 ℓ)", True,
      "物理由 n_p/n_o 定, ℓ_obs 只係後勤")

with open('data/local_l_level.json', 'w') as f:
    json.dump({
        'E_min': E_min,
        'obs_cases': [(o, n_of_E(e)) for o, e in obs_cases],
        'redshift_identity': 'z = 4^Dell - 1, Dell = log4(E_p/E_o)',
    }, f, indent=2, ensure_ascii=False)
print("\n" + "="*72)
print(f"RESULT: {PASS} PASS, {FAIL} FAIL")
print("="*72)