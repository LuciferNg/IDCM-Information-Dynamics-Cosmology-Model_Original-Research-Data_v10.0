#!/usr/bin/env python3
"""
O57 十二期 72: 方向 A — Worldsheet Instanton Yukawa 指數壓抑
==============================================================
Gemini 方向 A: 世代間距唔係 φ⁻², 而係 Worldsheet Instantons
  Yukawa ~ e^{-2π·Volume} (Kähler Cone 指數壓抑)

五期發現: φ^(35-i) Kähler 參數 → curve volumes:
  V1=1.00, V2=9.47, V3=22.18, V4=24.80, V5=40.12 (Lucas 結構)

測試:
  1. e^{-V_i} 指數壓抑譜 (5 個有限質量)
  2. 世代階梯: e^{-V} 之間嘅比
  3. 對 SM 9 費米子 (用 3 type × 3 gen)
  4. φ⁴~φ⁸ 級距出現?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十二期 72: Worldsheet Instanton Yukawa")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 五期 curve volumes ============
print("\n[1] 五期 curve volumes (Lucas)")
V = [1.0, 9.47213595, 22.18033989, 24.79837388, 40.1246118]
print(f"  V: {V}")
print(f"  e^-V: {[f'{math.exp(-v):.2e}' for v in V]}")

# 指數壓抑
m = [math.exp(-v) for v in V]
print(f"  質量譜 (e^-V): {[f'{x:.3e}' for x in m]}")
print(f"  質量比 max/min: {m[0]/m[-1]:.2e}")

# ============ 2. 世代階梯 ============
print("\n[2] 世代階梯")
# 相鄰比
for i in range(4):
    r = m[i]/m[i+1]
    print(f"  m{i+1}/m{i+2} = {r:.2e}")

# 3 代結構: V 值本身有 φ 結構?
print(f"\n  V 值嘅世代比:")
print(f"  V2/V1 = {V[1]:.2f} (≈9.47)")
print(f"  V3/V2 = {V[2]/V[1]:.2f}")
print(f"  V4/V3 = {V[3]/V[2]:.2f}")
print(f"  V5/V4 = {V[4]/V[3]:.2f}")

# V 差 = 世代間距 (Yukawa 指數)
print(f"\n  ΔV (世代間距):")
for i in range(4):
    print(f"  ΔV_{i+1} = V[{i+1}] - V[{i}] = {V[i+1]-V[i]:.4f}")

# ΔV 有冇 φ 結構?
print(f"\n  ΔV vs φ 冪:")
dVs = [V[i+1]-V[i] for i in range(4)]
for i, d in enumerate(dVs):
    for k in range(1, 8):
        if abs(d - k*math.log(phi)) < 1 or abs(d - phi**k) < 1:
            print(f"  ΔV_{i+1} = {d:.3f} ≈ φ^{k} = {phi**k:.3f} 或 k·lnφ = {k*math.log(phi):.3f}")

# ============ 3. SM 對應 ============
print("\n[3] SM 9 費米子對應")
# SM 質量 (GeV)
m_SM = {
    "u": 2.2e-3, "c": 1.27, "t": 172.76,
    "d": 4.7e-3, "s": 0.093, "b": 4.18,
    "e": 0.511e-3, "mu": 0.10566, "tau": 1.77686,
}
# 世代比 (每 type)
print(f"  世代比 (SM):")
for type_name, keys in [("u", ["u","c","t"]), ("d", ["d","s","b"]), ("l", ["e","mu","tau"])]:
    ms = [m_SM[k] for k in keys]
    r12 = ms[1]/ms[0]
    r23 = ms[2]/ms[1]
    print(f"  {type_name}: m2/m1 = {r12:.1f}, m3/m2 = {r23:.1f}")

# 對比模型: e^{-ΔV} 世代比
print(f"\n  模型世代比 (e^-ΔV):")
for i in range(4):
    print(f"  e^-ΔV_{i+1} = e^-({V[i+1]-V[i]:.3f}) = {math.exp(-(V[i+1]-V[i])):.3e}")

# ============ 4. 3×3 Yukawa ============
print("\n[4] 3×3 Yukawa 矩陣 (用 curve volumes)")
# Yukawa_ij = e^{-(V_i + V_j)/2} (對稱) 或 e^{-|V_i-V_j|} (off-diag)
# 全矩陣:
Y = np.zeros((5, 5))
for i in range(5):
    for j in range(5):
        Y[i, j] = math.exp(-abs(V[i]-V[j]))
print(f"  隨穿型 Yukawa Y_ij = e^-|V_i-V_j|:")
for i in range(5):
    print(f"    {[f'{Y[i,j]:.3f}' for j in range(5)]}")

# 對角: e^{-V_i} = 質量
print(f"\n  對角 (質量): {[f'{Y[i,i]:.3e}' for i in range(5)]}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("十二期 72 總結:")
print("=" * 72)
print(f"""
  Worldsheet Instanton Yukawa:
  ─────────────────────────────────
  1. 5 個 curve volumes: {V}
  2. 質量譜 e^-V: {[f'{x:.1e}' for x in m]}
  3. 質量比: {m[0]/m[-1]:.1e}
  4. 世代間距 ΔV: {[f'{d:.2f}' for d in dVs]}

  誠實: 5 個 volume 只俾 5 個質量 (SM 要 9)
  → 需要 3 type × 3 gen = 9 個獨立 volume
  → 117 positive curves 可能提供更多!
""")

results = {
    "test": "O57 十二期 72: Instanton Yukawa",
    "volumes": V,
    "masses": [float(x) for x in m],
    "mass_ratio": float(m[0]/m[-1]),
    "dVs": [float(d) for d in dVs],
    "passed": passed, "failed": failed
}
with open("data/72_instanton_yukawa.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十二期 72 完成!")
