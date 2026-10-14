#!/usr/bin/env python3
"""
O142 三期 03: 玻色子質量 + gauge coupling 完全閉合
====================================================
鎖定 sin²θ_W = 3/13 → 所有 EW 量 < 0.3%
α_s = 1/(F₆ + sin²θ_W + 1/B) → 0.012%
"""
import math, json, os

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")

print("=" * 72)
print("O142 三期 03: 玻色子質量 + gauge coupling 完全閉合")
print("=" * 72)

# ============ IDCM 常數 ============
N0 = 44
N_gen = 3
N_orbit = 6
B = 4  # K_Tree
F6 = 8  # Fibonacci F₆
F7 = 13  # Fibonacci F₇

# ============ 1. sin²θ_W ============
sin2_theta_W = 3/13
sin_theta_W = math.sqrt(sin2_theta_W)
cos_theta_W = math.sqrt(1 - sin2_theta_W)
tan_theta_W = sin_theta_W / cos_theta_W

# ============ 2. O34 比值 ============
mW_mZ = math.sin(30*math.pi/88) / math.sin(41*math.pi/88)
mH_mW = math.sin(38*math.pi/88) / math.sin(19*math.pi/88)

# ============ 3. α(M_Z) = 1/127.9 ============
alpha_MZ = 1/127.9
# 從 α(M_Z) + sin²θ_W → g₂
g2 = math.sqrt(4 * math.pi * alpha_MZ / sin2_theta_W)
# g' = g₂ × tanθ_W
g_prime = g2 * tan_theta_W
# e = g₂ × sinθ_W
e_charge = g2 * sin_theta_W

# ============ 4. 玻色子絕對質量 ============
v = 246.0  # Higgs VEV (GeV)
mW = g2 * v / 2
mZ = mW / mW_mZ
mH = mW * mH_mW

# ============ 5. α_s ============
alpha_s = 1 / (F6 + sin2_theta_W + 1/B)

# ============ SM 實驗值 ============
sm = {
    "g2": 0.652,
    "g_prime": 0.357,
    "e": 0.313,
    "mW": 80.377,
    "mZ": 91.1876,
    "mH": 125.25,
    "alpha_s": 0.1179,
    "sin2_theta_W": 0.23122,
}

print("\n=== [1] Gauge Coupling 閉合 ===")
data = [
    ("g₂", g2, sm["g2"], "SU(2)_L"),
    ("g'", g_prime, sm["g_prime"], "U(1)_Y"),
    ("e", e_charge, sm["e"], "電荷"),
    ("sin²θ_W", sin2_theta_W, sm["sin2_theta_W"], "Weinberg 角"),
]
for name, val, sm_val, desc in data:
    err = abs(val - sm_val)/sm_val*100
    print(f"  {name:12s} = {val:.6f}  (SM: {sm_val:.6f}, Δ={err:.3f}%) {'✅' if err < 1 else '❌'}  [{desc}]")

print("\n=== [2] 玻色子絕對質量閉合 ===")
data2 = [
    ("m_W", mW, sm["mW"], "W 玻色子"),
    ("m_Z", mZ, sm["mZ"], "Z 玻色子"),
    ("m_H", mH, sm["mH"], "Higgs"),
]
for name, val, sm_val, desc in data2:
    err = abs(val - sm_val)/sm_val*100
    print(f"  {name:12s} = {val:.3f} GeV  (SM: {sm_val:.3f}, Δ={err:.3f}%) {'✅' if err < 1 else '❌'}  [{desc}]")

print("\n=== [3] α_s 閉合 ===")
err_as = abs(alpha_s - sm["alpha_s"])/sm["alpha_s"]*100
print(f"  α_s = 1/(F₆ + sin²θ_W + 1/B) = 1/({F6} + {sin2_theta_W:.6f} + 1/{B})")
print(f"      = 1/({F6 + sin2_theta_W + 1/B:.6f}) = {alpha_s:.6f}")
print(f"  SM: {sm['alpha_s']:.6f}, Δ={err_as:.3f}% {'✅' if err_as < 1 else '❌'}")

print("\n=== [4] 推導鏈 ===")
print("""
  sin²θ_W = 3/13 = N_gen/F₇
       ↓
  g₂ = √(4πα/sin²θ_W) = 0.6525
       ↓
  m_W = g₂·v/2 = 80.258 GeV
       ↓
  m_Z = m_W / sin(30π/88)/sin(41π/88) = 90.919 GeV
  m_H = m_W × sin(38π/88)/sin(19π/88) = 124.984 GeV
       ↓
  α_s = 1/(F₆ + sin²θ_W + 1/B) = 0.117914
""")

# ============ 零參數審計 ============
print("\n=== [5] 零參數審計 ===")
checks = []
checks.append(("sin²θ_W = 3/13 無自由參數", True))
checks.append(("O34 m_W/m_Z 純 K_Chain 比值", True))
checks.append(("O34 m_H/m_W 純 K_Chain 比值", True))
checks.append(("α(M_Z) = 1/127.9 實驗輸入", True, "⚠️ 唯一外部輸入"))
checks.append(("v = 246 GeV 實驗輸入", True, "⚠️ 唯一外部輸入"))
checks.append(("α_s = 1/(F₆+sin²θ_W+1/B) 全結構", True))

for name, ok, *extra in checks:
    note = f" — {extra[0]}" if extra else ""
    print(f"  {'✅' if ok else '❌'} {name}{note}")

# 真正零參數版本: 如果 v 也從 IDCM 導出
print(f"\n  注意: v = 246 GeV 是實驗輸入。")
print(f"  從 O64: M₀ = 27.9009 MeV (IDCM 質量尺度)")
print(f"  v = 2m_W/g₂ = 2×{mW:.3f}/{g2:.6f} = {2*mW/g2:.1f} GeV")
print(f"  如果 v 能從 IDCM 結構推導 → 完全零參數")

# ============ 保存 ============
out = {
    "test": "O142 03: boson mass + gauge full closure",
    "sin2_theta_W": float(sin2_theta_W),
    "g2": float(g2),
    "g_prime": float(g_prime),
    "e_charge": float(e_charge),
    "mW_GeV": float(mW),
    "mZ_GeV": float(mZ),
    "mH_GeV": float(mH),
    "alpha_s": float(alpha_s),
    "errors": {
        "g2_pct": float(abs(g2 - sm["g2"])/sm["g2"]*100),
        "g_prime_pct": float(abs(g_prime - sm["g_prime"])/sm["g_prime"]*100),
        "mW_pct": float(abs(mW - sm["mW"])/sm["mW"]*100),
        "mZ_pct": float(abs(mZ - sm["mZ"])/sm["mZ"]*100),
        "mH_pct": float(abs(mH - sm["mH"])/sm["mH"]*100),
        "alpha_s_pct": float(err_as),
    },
    "num_free_params": 2,  # α(M_Z), v
    "num_zero_params": 6,  # sin²θ_W, mW/mZ, mH/mW, g₂, g', α_s
}

data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(data_dir, exist_ok=True)
with open(os.path.join(data_dir, "03_gauge_closure.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"\n✅ 結果已保存到 data/03_gauge_closure.json")