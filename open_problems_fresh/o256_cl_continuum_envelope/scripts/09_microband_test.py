#!/usr/bin/env python3
"""
O256 — Script 09: Decisive test — 微帶 (1452..1476) 喺實測譜有冇 bump?
=====================================================================
Script 06 結構主張: 峰位公式 m≥8 飽和分支 → 37 模態全塌入 [1452,1476]
⟹ 預言: 實測 Planck/SPT C_ℓ 喺 ℓ=1452..1476 應該見到局部增強 (bump).

Decesive test:
  T1: Planck binned 喺 1452..1476 嘅局部形態 vs 鄰域 (有冇 bump?)
  T2: 若有 bump — 位置/寬度 match [1452,1476]? 
  T3: SPT 高分辨 (52 bins 1437..2962) 有冇 local feature @1452-1476?
  T4: 若無 bump ⟹ 微帶預言 REFUTED — R1 數值閉合終止

禁區: 唔 re-fit; 只睇「有冇 local feature」.
"""
import math, sys
import numpy as np

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"

print("="*76)
print("1. Planck binned 喺 1452..1476 嘅形態 (txt 去 C_ℓ → D_ℓ)")
print("="*76)
planck = []
with open(f"{BASE}/open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        p = line.split()
        if len(p)>=2:
            try: planck.append((float(p[0]), float(p[1])))
            except ValueError: pass
planck = np.array(sorted(planck))
l_p, C_p = planck[:,0], planck[:,1]
D_p = C_p*l_p*(l_p+1)/(2*math.pi)

# 高ℓ尾段 1418..1600 逐 bin 顯示
print("  ℓ     D_ℓ     log(D_ℓ)")
for i in range(len(l_p)):
    if 1410 <= l_p[i] <= 1650:
        print(f"  {l_p[i]:6.0f}  {D_p[i]:8.1f}  {math.log(D_p[i]):8.4f}")

# 1452..1476 喺 Planck binning 嘅位置: 有幾多 bins 落入?
n_in = ((l_p >= 1452) & (l_p <= 1476)).sum()
print(f"\n  Planck bins 落入 [1452,1476]: {n_in} 個")
print(f"  Planck bin 中心: {[f'{x:.0f}' for x in l_p[(l_p>=1450)&(l_p<=1480)]]}")

# 平滑背景估計 (1418..2000 段 fit log-linear) + 殘差
m_est = (l_p >= 1418) & (l_p <= 2000)
sl = np.polyfit(l_p[m_est], np.log(D_p[m_est]), 2)
bg = np.exp(np.polyval(sl, l_p))
res = D_p/bg - 1.0
print("\n  detrend 殘差 (二次 bg, 0 中心):")
for i in range(len(l_p)):
    if 1410 <= l_p[i] <= 1650:
        print(f"  ℓ={l_p[i]:6.0f}  res={res[i]*100:+6.1f}%")

m_micro = (l_p >= 1452) & (l_p <= 1476)
if m_micro.sum() >= 2:
    res_micro = res[m_micro].mean()
    print(f"\n  微帶內平均殘差: {res_micro*100:+.1f}%")
    check("微帶內殘差 > +5% (bump 存在)", res_micro > 0.05, f"({res_micro*100:+.1f}%)")
else:
    print("  ⚠️ Planck bins 唔夠密 — 用 SPT")

print("\n" + "="*76)
print("2. SPT 高分辨 1437..2962 (52 bins) local feature?")
print("="*76)
spt = []
with open(f"{BASE}/open_problems_fresh/o214_energy_budget_definition/data/spt3g_d1/SPT3G_D1_TnE_bdp.txt") as f:
    for line in f:
        p = line.split()
        if len(p)>=2:
            try: spt.append((float(p[0]), float(p[1])))
            except ValueError: pass
spt = np.array(sorted(spt))
# bdp 檔案格式不明, 直接試: 第一列大數可能唔係 ℓ — 印頭 30
print("  SPT bdp raw (頭 25 行):")
for i in range(min(25, len(spt))):
    print(f"    {spt[i]}")

print("\n" + "="*76)
print("3. 判決")
print("="*76)
print("""
  T1: Planck 微帶內 (1452..1476) 有冇 bump?   → 上面殘差
  T2: SPT 高分辨 1452..1476 有冇 feature?   → 睇 SPT bin 結構
  T3: 微帶預言 (25 ℓ 寬 bump) REFUTED / 支持?
""")
print(f"RESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
sys.exit(0 if FAIL==0 else 1)