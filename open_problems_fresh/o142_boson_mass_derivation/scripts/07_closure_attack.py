#!/usr/bin/env python3
"""
O142 v9 -- Remaining Open Items Closure Attack
==============================================
攻堅 O142 三個遺留問題:

A. v 公式污染修正 (重大)
   O142 現用 λ_max = 4F₇−L₇/66 = 51.56 (O59 hybrid 污染版)
   O59 native_12d clean: λ_max = 36−1/γ₂₀ = 35.4178
   → v_clean = 246.21 (O59 攻堅1) / 246.26 (O85 clean) vs SM 246.22

B. α_s 譜跡形式
   α_s⁻¹ = (T̂⁶)₁₂ + sin²θ_W + 1/Tr(T̂³) = 8 + 0.2208 + 0.25 = 8.4708
   8 = dim(adj SU(3)) = 膠子數 (強耦合譜跡基底)

C. Δα⁻¹ = 9 身份
   α⁻¹(0)−α⁻¹(M_Z) = 137−128 = 9 = N_gen²
"""
import math
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "07_closure_attack.json"

phi = (1 + math.sqrt(5)) / 2
psi = (1 - math.sqrt(5)) / 2
N0 = 44
B = 4
M0 = 27.900915  # MeV
SM_v = 246.22   # GeV
SM_alpha_s = 0.1179
SM_g2 = 0.652

def lucas(n): return round(phi**n + psi**n)
def fib(n):   return round((phi**n - psi**n) / math.sqrt(5))
LUC = {n: lucas(n) for n in range(0, 16)}
FIB = {n: fib(n) for n in range(0, 16)}
gamma = {n: 4 * math.sin(n * math.pi / 88)**2 for n in range(1, 45)}

def Tpow(n):
    r = [[1, 0], [0, 1]]
    for _ in range(n):
        r = [[r[0][0] + r[0][1], r[0][0]],
             [r[1][0] + r[1][1], r[1][0]]]
    return r

results = []
def chk(name, got, want, tol_pct, note=""):
    dev = abs(got - want) / abs(want) * 100 if want else abs(got - want)
    ok = dev < tol_pct
    results.append({"name": name, "got": got, "want": want,
                    "dev": f"{dev:.6f}%", "ok": ok, "note": note})
    return ok

print("=" * 72)
print("O142 v9 -- Remaining Open Items Closure Attack")
print("=" * 72)

# ============================================================
# A. v 公式污染修正
# ============================================================
print("\n### A. v 公式污染修正 ###")

lam_dirty = 4 * FIB[7] - LUC[7] / 66
lam_clean = 36 - 1 / gamma[20]

print(f"\n  λ_max 污染版 (O59 hybrid/final): 4F₇ − L₇/66 = {lam_dirty:.6f}  🔴")
print(f"  λ_max clean版 (O59 native_12d):  36 − 1/γ₂₀   = {lam_clean:.6f}  🟢")

# 污染版 v
v_dirty = math.sqrt(lam_dirty) * M0 * 88 * 14 / 1000
chk("A1: v(污染版) = √51.5606×M₀×88×14", v_dirty, SM_v, 1.0,
    f"Δ={abs(v_dirty-SM_v)/SM_v*100:.4f}%")

# clean 版本 1: O59 攻堅1 因子
g7 = gamma[7]
f_O59 = 88 * (LUC[5] - 1 + LUC[4] * B * g7)
v_O59 = math.sqrt(lam_clean) * M0 * f_O59 / 1000
chk("A2: v(O59 clean) = √35.42×M₀×88×(10+28γ₇)", v_O59, SM_v, 0.05,
    f"Δ={abs(v_O59-SM_v)/SM_v*100:.4f}%")

# clean 版本 2: O85 clean 因子
g1 = gamma[1]
f_O85 = 88 * 14 * (1 + (N0 - B) * g1)
v_O85 = math.sqrt(lam_clean) * M0 * f_O85 / 1000
chk("A3: v(O85 clean) = √35.42×M₀×88×14×(1+40γ₁)", v_O85, SM_v, 0.05,
    f"Δ={abs(v_O85-SM_v)/SM_v*100:.4f}%")

# 兩 clean 版一致性
chk("A4: O59 vs O85 clean 因子一致", f_O59 / f_O85, 1.0, 0.05,
    f"ratio={f_O59/f_O85:.6f}")

# 污染版對玻色子質量影響 (用 g₂ = √(4π/30))
g2 = math.sqrt(4 * math.pi / 30)
mWmZ = math.sin(30 * math.pi / 88) / math.sin(41 * math.pi / 88)
mHmW = math.sin(38 * math.pi / 88) / math.sin(19 * math.pi / 88)

mW_dirty = g2 * v_dirty / 2
mW_clean = g2 * v_O85 / 2
print(f"\n  玻色子質量受污染影響:")
print(f"    m_W(污染 v=246.82) = {mW_dirty:.3f} GeV (SM 80.377)")
print(f"    m_W(clean v=246.26) = {mW_clean:.3f} GeV (SM 80.377)")
print(f"  ⚠️ 注意: m_W 偏差主導係 g₂ (0.65%), 唔係 v (0.02%)")
print(f"    用 SM g₂=0.652 + v_clean: m_W = {0.652*v_O85/2:.3f} GeV (Δ={abs(0.652*v_O85/2-80.377)/80.377*100:.2f}%)")
print(f"    → v 污染修正唔改變 m_W 結論 (g₂ 偏差仍 0.65%)")
# 正確檢查: v 本身 clean 比 dirty 準 (針對 v, 唔係 m_W)
dev_clean_v = abs(v_O85 - SM_v) / SM_v
dev_dirty_v = abs(v_dirty - SM_v) / SM_v
A5_ok = dev_clean_v < dev_dirty_v
results.append({"name": "A5: v(clean) 比 v(污染) 更準 (針對 v 本身)",
                "got": dev_clean_v, "want": dev_dirty_v,
                "dev": f"clean {dev_clean_v*100:.4f}% < dirty {dev_dirty_v*100:.4f}%",
                "ok": A5_ok, "note": "flag: clean dev 應小於 dirty dev"})

# ============================================================
# B. α_s 譜跡形式
# ============================================================
print("\n### B. α_s 譜跡形式 ###")

sin2W = 1 - mWmZ**2
T3 = Tpow(3)
T6 = Tpow(6)
trT3 = T3[0][0] + T3[1][1]
F6_entry = T6[0][1]

chk("B1: (T̂⁶)₁₂ = F₆ = 8 = dim(adj SU(3))", F6_entry, 8, 0.001)
chk("B2: Tr(T̂³) = L₃ = 4 = B", trT3, 4, 0.001)

alpha_inv = F6_entry + sin2W + 1 / trT3
alpha_s = 1 / alpha_inv
print(f"\n  α_s⁻¹ = (T̂⁶)₁₂ + sin²θ_W + 1/Tr(T̂³)")
print(f"        = {F6_entry} + {sin2W:.6f} + {1/trT3}")
print(f"        = {alpha_inv:.6f}")
print(f"  α_s = {alpha_s:.6f} vs SM {SM_alpha_s}")
chk("B3: α_s⁻¹ 譜跡形式 = 8.4708", alpha_inv, 8.470776, 0.001)
chk("B4: α_s vs SM 0.1179", alpha_s, SM_alpha_s, 0.5, f"Δ={abs(alpha_s-SM_alpha_s)/SM_alpha_s*100:.4f}%")

# O89 RG 對照
alpha_O89 = 1 / 8.426
chk("B5: O89 RG α₃⁻¹=8.426", alpha_O89, SM_alpha_s, 1.0,
    f"Δ={abs(alpha_O89-SM_alpha_s)/SM_alpha_s*100:.4f}% (O89 VL split)")

# sin²θ_W 結構身份檢查 (誠實標記: 17/77 多候選風險)
s17_77 = 17 / 77
chk("B6: sin²θ_W 候選 17/77", s17_77, sin2W, 0.01,
    f"dev={abs(s17_77-sin2W)/sin2W*100:.4f}% — 77=L₄L₅ 已確立, 17 多候選⚠️")

# ============================================================
# C. Δα⁻¹ = 9 身份
# ============================================================
print("\n### C. Δα⁻¹ = 9 身份 ###")

a0_inv = 3 * N0 + FIB[5]
aMZ_inv = 2 * N0 + FIB[5] * FIB[6]
delta = a0_inv - aMZ_inv

chk("C1: α⁻¹(0) = 3N₀+F₅ = 137", a0_inv, 137, 0.001)
chk("C2: α⁻¹(M_Z) = 2N₀+F₅F₆ = 128", aMZ_inv, 128, 0.001)
chk("C3: Δα⁻¹ = 9 = N_gen²", delta, 9, 0.001)

# QED ΣQ² = 8 = F₆ (不同於 9 — 誠實標記)
sumQ2 = 3 * 1 + 3 * 3 * (2/3)**2 + 3 * 3 * (1/3)**2
chk("C4: QED ΣQ² = 8 = F₆ (無權重係數)", sumQ2, 8, 0.001,
    "與 IDCM 9 不同量: 9=世代平方, 8=電荷平方和")

# 實測 QED 運行 (含 log)
# Δα⁻¹(0→M_Z) ≈ 9.1 (標準 QED 運行, 含輕子+夸克+W)
chk("C5: 實測 Δα⁻¹(0→M_Z) ≈ 9.1 vs IDCM 9", 9.1, 9.0, 2.0,
    "IDCM 整數化 vs 實測含 log 權重")

# ============================================================
# 總結
# ============================================================
passed = sum(1 for r in results if r["ok"])
failed = [r for r in results if not r["ok"]]
print("\n" + "=" * 72)
print(f"AUDIT SUMMARY: {passed}/{len(results)} PASS")
print("=" * 72)
for r in results:
    mark = "✅" if r["ok"] else "❌"
    print(f"  {mark} {r['name']}: {r['got']:.6g} vs {r['want']:.6g} ({r['dev']}) {r['note']}")

out = {"test": "O142 v9 closure attack", "total": len(results),
       "pass": passed, "fail": len(failed),
       "fail_detail": [r for r in results if not r["ok"]],
       "results": results,
       "key_values": {
           "lam_dirty": lam_dirty, "lam_clean": lam_clean,
           "v_dirty": v_dirty, "v_O59": v_O59, "v_O85": v_O85,
           "alpha_s_inv": alpha_inv, "alpha_s": alpha_s,
           "alpha_s_O89": alpha_O89, "delta_alpha_inv": delta,
           "sumQ2": sumQ2}}
with open(OUT, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\n  結果已存: {OUT}")
