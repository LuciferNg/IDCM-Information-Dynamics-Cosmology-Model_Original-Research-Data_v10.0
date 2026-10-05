#!/usr/bin/env python3
"""
O53 開放問題 3: SM 質量譜映射 λ₁ = φ^(1/3)
=============================================
真實 Y (κ_ijk·J*^k) 譜 vs SM 質量

SM 質量 (GeV):
  t=172.69, b=4.18, c=1.27, τ=1.777, s=0.093, μ=0.1057, d=0.0047, u=0.0022, e=0.000511
  質量比: t/b=41.3, t/c=136, t/τ=97.2, t/μ=1634, t/e=3.38e5

問題:
  1. Y 譜 (λ₁=φ^(1/3)≈1.17) 有冇三代 3×3 塊結構?
  2. 質量比有冇 φ 指數?
  3. e^(-V) 壓抑 vs 直接 φ 結構?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53 開放 3: SM 質量譜映射")
print("=" * 70)

with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)

K = np.zeros(tuple(kappa['shape']))
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val
    K[i, k, j] = val
    K[j, i, k] = val
    K[j, k, i] = val
    K[k, i, j] = val
    K[k, j, i] = val

J0 = np.array(jstar['Jstar_36D'])
Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2

# --- [1] SM 質量 ---
print("\n[1] SM 質量比:")
SM = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
      'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}
sm_ratios = {}
for k1, v1 in SM.items():
    sm_ratios[k1] = v1 / SM['t']
print(f"    m/m_t: " + "  ".join(f"{k}={v:.2e}" for k, v in sm_ratios.items()))

# φ 指數
print(f"\n    SM 質量 φ 指數 (ln(m_t/m)/lnφ):")
for k, v in sm_ratios.items():
    if v > 0:
        print(f"      {k}: φ^({math.log(1/v)/math.log(phi):+6.3f})")

# --- [2] Y 譜三代 ---
print("\n[2] Y 譜 (32 非零):")
ev = np.linalg.eigvalsh(Y)
ev_sorted = np.sort(np.abs(ev))[::-1]
ev_nz = ev_sorted[ev_sorted > 1e-10]
print(f"    |λ| 前 12: {np.array2string(ev_nz[:12], precision=4)}")
print(f"    1/|λ| φ 指數:")
for i in range(12):
    print(f"      λ_{i+1:2d}: 1/λ = φ^({math.log(1/ev_nz[i])/math.log(phi):+6.3f})")

# --- [3] 三代 3×3 塊? ---
print("\n[3] Y 嘅 3×3 三代塊:")
# 36 = 3×12: 檢查 12×12 對角塊
Y12 = np.zeros((3, 3))
for bi in range(3):
    for bj in range(3):
        Y12[bi, bj] = np.abs(Y[bi*12:(bi+1)*12, bj*12:(bj+1)*12]).sum()
print(f"    12×12 塊 |Y| 總和:")
for bi in range(3):
    print(f"      {Y12[bi,0]:8.3f} {Y12[bi,1]:8.3f} {Y12[bi,2]:8.3f}")
print(f"    對角/非對角: {np.trace(Y12):.2f} / {Y12.sum()-np.trace(Y12):.2f}")

# --- [4] φ 指數質量比 ---
print("\n[4] φ 指數候選 (SM 比):")
# t/b = 41.3 → φ^?
tb = SM['t']/SM['b']
tc = SM['t']/SM['c']
ttau = SM['t']/SM['tau']
print(f"    t/b = {tb:.1f} = φ^({math.log(tb)/math.log(phi):.3f})")
print(f"    t/c = {tc:.1f} = φ^({math.log(tc)/math.log(phi):.3f})")
print(f"    t/τ = {ttau:.1f} = φ^({math.log(ttau)/math.log(phi):.3f})")
print(f"    φ⁷ = {phi**7:.1f}, φ⁸ = {phi**8:.1f}, φ⁹ = {phi**9:.1f}")

# --- [5] e^(-V) 壓抑模型 ---
print("\n[5] e^(-V) 壓抑模型:")
print(f"    IDCM 機制: m ~ M_Pl × e^(-V_cycle)")
print(f"    V_cycle ~ 44 (Nd) → e^(-44) ~ 1e-19")
print(f"    M_Pl × e^(-44) = {1.22e22 * math.exp(-44):.2e} MeV = {1.22e19*math.exp(-44):.2e} GeV")
print(f"    top 需要 M_Pl × e^(-V) = 172 GeV → V = {math.log(1.22e19/172):.2f}")
print(f"    → V_top ≈ 41.9 ≈ 42 = ?")
print(f"    42 = 44−2? 42 = 2×21? 42 = L₉? {int(round(phi**9 + (-phi)**-9))}")
print(f"    42 = 3×14 = 3×(2×7)")

# --- [6] λ 譜 → SM 質量直接比? ---
print("\n[6] λ 譜 vs SM 質量比:")
print(f"    Y 譜比: λ₁/λ₂ = {ev_nz[0]/ev_nz[1]:.2f}, λ₁/λ₃ = {ev_nz[0]/ev_nz[2]:.2f}")
print(f"    SM 比:  t/b = 41.3, t/τ = 97.2")
print(f"    → 直接比唔啱 (譜密度唔同)")
print(f"    → 需要 3×3 塊本徵值 (每塊 3 個) 先似 SM")

# 嘗試: 將 32 個 λ 分 3 代 (每代 ~10-11 個) 睇 min/max
print(f"\n    32 個 λ 分 3 代 (10/11/11):")
g1 = ev_nz[:10]
g2 = ev_nz[10:21]
g3 = ev_nz[21:]
print(f"      Gen1 (top 10): mean={g1.mean():.4f}")
print(f"      Gen2 (mid 11): mean={g2.mean():.4f}")
print(f"      Gen3 (bot 11): mean={g3.mean():.4f}")
print(f"      G1/G3 = {g1.mean()/g3.mean():.2f}")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
