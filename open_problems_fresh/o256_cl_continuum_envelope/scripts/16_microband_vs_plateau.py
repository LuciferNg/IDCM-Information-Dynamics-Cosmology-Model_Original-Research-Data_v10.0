#!/usr/bin/env python3
"""
O256 — Script 16: ★ 微帶 vs 後峰平台 — Lorentz tail 殘差區分測試
=====================================================================
Script 15 矛盾: ACT/SPT 正增強 (+12~18%), Planck 微帶內三 bin 負 (−3%).

關鍵問題: 「增強」係 25ℓ 微帶 bump 定 50-100ℓ 後峰平台?
區分方法: 用峰 7 Lorentz tail (O48 γ≈38, 已閉合) 做「無微帶模型」,
    睇殘差喺 [1452,1476] 係咪「局部 bump」(峰型) 定「平台」(板塊抬起).

判定:
  T1: Planck 微帶內三 bin 殘差 vs 兩側 — 局部 bump 應峰型正
  T2: ACT 1448/1498 — 微帶佔比 21/25 vs 4/25 → 應 1448 遠高 1498
  T3: SPT 1437/1487 — 微帶佔比 10/25 vs 15/25 → 應 1487 高過 1437 (若微帶集中 1452-1476)
  T4: Lorentz tail 預言 ratio vs 實測 ratio — 平台檢出

注意: T3 係關鍵 — 如果微帶 bump 真係喺 [1452,1476] 集中,
    1487 (含 1462-1476) 應該高過 1437 (含 1452-1462) — 倒轉 = 唔係微帶!
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
N_d, M = 44, 33
A7 = 1/7
ELL7 = 1409
GAMMA = 306/8.0   # 峰形 γ = 峰間隙/8 = 38.25 (O48 閉合)

def lorentz_tail(dl):
    """峰 7 Lorentz tail (Δ = ℓ−1409)."""
    return A7*(GAMMA/math.pi)/(dl**2 + GAMMA**2)

print("="*76)
print("1. 峰 7 Lorentz tail 預言 vs 實測 (ACT 高ℓ bins)")
print("="*76)
# 用平滑背景喺 1550+ fit 峯高 A7? — 零 fit 原則: 用已閉合 γ=38.25,
# A7 由 O83 振幅母函數 (已閉合) → 只比較「形狀」(ratio), 唔比較絕對值
print("  Lorentz tail (γ=38.25) 形狀預言 (Δ=ℓ−1409):")
pts = [
    ("ACT 1398.5", 1398.5, 799.84, -10.5),
    ("ACT 1448.5", 1448.5, 800.45, 39.5),
    ("ACT 1498.5", 1498.5, 675.92, 89.5),
    ("ACT 1548.5", 1548.5, 533.94, 139.5),
    ("SPT 1387.0", 1387.0, 771.4, -22.0),
    ("SPT 1437.0", 1437.0, 820.2, 28.0),
    ("SPT 1487.0", 1487.0, 748.2, 78.0),
    ("SPT 1537.0", 1537.0, 624.1, 128.0),
    ("SPT 1587.0", 1587.0, 492.4, 178.0),
]
for name, ell, D, dl in pts:
    lt = lorentz_tail(dl)
    print(f"  {name:>13}: D={D:7.1f}  Lorentz-tail Δ={dl:6.1f} L={lt:.5f}")

print("\n  Lorentz ratio 預言 (Δ₁→Δ₂):")
# ACT 1448→1498: L(39.5)/L(89.5)
r_act_lor = lorentz_tail(39.5)/lorentz_tail(89.5)
r_act_obs = 800.45/675.92
print(f"  ACT 1448/1498: Lorentz={r_act_lor:.2f} vs 實測={r_act_obs:.2f}")
check("ACT ratio 實測 ≪ Lorentz (平台/微帶托住)", r_act_obs < r_act_lor*0.5, f"({r_act_obs:.2f} vs {r_act_lor:.2f})")

r_sp_lor = lorentz_tail(28.0)/lorentz_tail(78.0)
r_sp_obs = 820.2/748.2
print(f"  SPT 1437/1487: Lorentz={r_sp_lor:.2f} vs 實測={r_sp_obs:.2f}")
check("SPT ratio 實測 ≪ Lorentz", r_sp_obs < r_sp_lor*0.5, f"({r_sp_obs:.2f} vs {r_sp_lor:.2f})")

# ── 2. ★ 微帶集中性測試 (T3 關鍵) ────────────────────────────────
print("\n" + "="*76)
print("2. ★ 微帶集中性: SPT 1437 vs 1487 佔微帶比例")
print("="*76)
# SPT bin 1437: 1412..1462 → 微帶 [1452,1476] 含 1452-1462 = 10/25
# SPT bin 1487: 1462..1512 → 微帶含 1462-1476 = 15/25
# 若微帶 bump 集中 1452-1476: 1487 相對增強應 ≥ 1437
# 但係 1437 覆蓋峰 7 tail (1409-1462), 1487 喺 tail 之外 — 要扣 Lorentz
# 扣 Lorentz 後殘差 (log scale): res = log(D/L) — 平台效應
print("  扣除峰 7 Lorentz tail 後之殘差 (零參數, 形狀比較):")
for name, ell, D, dl in pts:
    lt = lorentz_tail(dl)
    res = math.log(D) - math.log(lt)
    print(f"  {name:>13}: log(D/L) = {res:+7.3f}")
# 用近峰 D(1398.5) 或 D(1387) 定標(形狀): log(D/L) 應該常數 (純 tail)
# 若 log(D/L) 上升 (微帶) → 1450-1500 有結構
# 用 ACT: log(D/L)@1398 vs @1448 vs @1498 vs @1548
print("\n  ACT log(D/L) 演化 (純 tail 應常數):")
Dp = [799.84, 800.45, 675.92, 533.94]
dls = [-10.5, 39.5, 89.5, 139.5]
logs = [math.log(D) - math.log(lorentz_tail(dl)) for D, dl in zip(Dp, dls)]
for nm, lg in zip(["1398","1448","1498","1548"], logs):
    print(f"    ℓ={nm}: log(D/L)={lg:+.3f}")
print(f"    spread = {max(logs)-min(logs):.3f}  (純 tail 應 ≈ 0)")
check("ACT log(D/L) spread < 0.3 (純 tail)", max(logs)-min(logs) < 0.3)

# ── 3. Planck 微帶內三 bin 局部形態 ──────────────────────────────
print("\n" + "="*76)
print("3. Planck 微帶內 bins vs 兩側 (9ℓ 高分辨)")
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
print("  ℓ     D        log(D/L)  (L=峰7 tail 形狀)")
for i in range(len(l_p)):
    if 1418 <= l_p[i] <= 1550:
        dl = l_p[i]-ELL7
        res = math.log(D_p[i]) - math.log(lorentz_tail(dl)) if dl != 0 else float('nan')
        print(f"  {l_p[i]:5.0f}  {D_p[i]:7.1f}  {res:+7.3f}")
# 微帶內 (1452-1476) 平均 log(D/L) vs 兩側 (1420-1450, 1477-1550)
band = (l_p>=1452)&(l_p<=1476)
left = (l_p>=1420)&(l_p<1452)
right = (l_p>1476)&(l_p<=1550)
lb = np.mean([math.log(D_p[i])-math.log(lorentz_tail(l_p[i]-ELL7)) for i in range(len(l_p)) if band[i]])
ll = np.mean([math.log(D_p[i])-math.log(lorentz_tail(l_p[i]-ELL7)) for i in range(len(l_p)) if left[i]])
lr = np.mean([math.log(D_p[i])-math.log(lorentz_tail(l_p[i]-ELL7)) for i in range(len(l_p)) if right[i]])
print(f"\n  log(D/L) mean: 微帶內={lb:+.3f}  左={ll:+.3f}  右={lr:+.3f}")
print(f"  微帶相對兩側: {lb-(ll+lr)/2:+.3f} (log) = {math.exp(lb-(ll+lr)/2)-1:+.1%}")
check("微帶內部相對兩側 < +10% (無局部 bump)", math.exp(lb-(ll+lr)/2)-1 < 0.10)

print("\n" + "="*76)
print("4. 判決")
print("="*76)
print("""
  T1 (Planck 局部形態): 微帶內 vs 兩側 — 邊個結果
  T2 (ACT/S ratio): Lorentz 爆但實測平 = 後峰平台存在 (托住)
  T3 (SPT 1437/1487): 若微帶集中 1452-1476, 1487 應 ≥ 1437 (扣除 Lorentz 後)
  T4 (log(D/L) 常數性): 純 tail 應常數 → 上升 = 平台/微帶

  關鍵: T3 決定「25ℓ 微帶」定「50ℓ+ 平台」:
  ⟹ 若 1487 唔特別高過 1437 (log(D/L) flat 過 1450) → 係平台唔係微帶
  ⟹ 微帶 S5 預言 (25ℓ bump) 未獲支持; ACT/SPT 增強 = P3 連續背景
""")
print(f"RESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
sys.exit(0 if FAIL == 0 else 1)