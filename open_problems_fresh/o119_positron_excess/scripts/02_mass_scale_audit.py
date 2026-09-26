#!/usr/bin/env python3
"""
O119 - Script 02: 兩套質量公式對照 + 正電子能量標度搜尋
========================================================
目標:
  1. 驗證 O116 v_EW 質量公式 m_n = (kappa - e^-n)·v_EW·e^-n 完整譜
  2. 對照 O54/O36 質量公式 m_n = M0·omega_n
  3. 搵 IDCM 結構中邊個標度可以產生 10-300 GeV 正電子
  4. 搜尋 O54 冪律 fit 指數 0.258 嘅結構來源

物理問題: AMS-02 正電子 10-300 GeV, W-field 靜止質量得 MeV 級。
          O54 用 CR boost (E_e+ = gamma_p·E_res) 繞過, 但 gamma_p 係外部輸入。
          O119 需要零參數能量標度接駁。
"""
import json, math
import numpy as np

M0 = 27.9009     # MeV
Nd = 44
phi = (1 + math.sqrt(5)) / 2
kappa = 1/16     # B^-2
v_EW = 246.2196  # GeV (O40 閉合)

print("=" * 72)
print("[1] 兩套 W-field 質量公式對照")
print("=" * 72)

omega_n = np.array([2 * math.sin(math.pi * n / 88) for n in range(1, Nd + 1)])
gamma_n = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, Nd + 1)])

# 公式 A: O54/O36 (M0 制)
m_A = M0 * omega_n  # MeV

# 公式 B: O116 (v_EW 制, Higgs portal)
m_B = np.array([(kappa - math.exp(-n)) * v_EW * math.exp(-n) for n in range(1, Nd + 1)])  # GeV

print(f"  公式 A: m_n = M0·omega_n (O54/O36, M0 = {M0} MeV)")
print(f"  m_A(1..7..22..44) = [{m_A[0]:.2f}, {m_A[6]:.2f}, {m_A[21]:.2f}, {m_A[-1]:.2f}] MeV")
print()
print(f"  公式 B: m_n = (kappa - e^-n)·v_EW·e^-n (O116 Higgs portal, v_EW = {v_EW} GeV)")
print(f"  kappa = {kappa} = B^-2")
for n in [1, 2, 3, 4, 5, 6, 7, 8, 10, 14, 20]:
    en = math.exp(-n)
    m = (kappa - en) * v_EW * en
    sign = "tachyon(-)" if (kappa - en) < 0 else "stable(+)"
    print(f"    n={n:2d}: e^-n={en:.6f}, (k-e^n)={kappa-en:+.6f} {sign}, m = {m*1000:9.1f} MeV")
print()
print(f"  ⚠️ 公式 B 快子條件 (k - e^-n) < 0: n < ln(16) = 2.77 → n = 1, 2 快子")
print(f"     n=3..44 穩定, 質量範圍 {min(m_B[2:])*1000:.1f} - {max(m_B[2:])*1000:.1f} MeV")
print(f"     最高穩定質量 (n=4): {max(m_B[2:])*1000:.1f} MeV")
print(f"     ⟹ 公式 B 都係 MeV 級, 唔到 GeV")

print()
print("=" * 72)
print("[2] IDCM GeV 級標度盤點 (正電子 10-300 GeV 候選)")
print("=" * 72)
candidates = [
    ("v_SM", 246.2196, "O40: v_SM = v_eff·88·71·(1-4/(90(M+mu^2))) dev=0"),
    ("m_W(SM)", 80.258, "O142: SM 電弱 W 玻色子"),
    ("m_Z(SM)", 90.919, "O142"),
    ("m_H(SM)", 124.984, "O142"),
    ("v_eff*88", 39.46*88/1000, "O40: v_eff·88 (中間值)"),
    ("M0*88*71", 27.9*88*71/1e6, "M0·88·71 (v_SM 分子)"),
    ("M0*F_proj*2", 27.9*17*2/1000, "O54: F_proj×M0×omega_44"),
    ("M0*88", 27.9*88/1000, "M0·88"),
    ("1496 mode", 27.9*1496/1e6*1000, "O87: 1496 = 34×44?"),
]
print(f"  {'標度':<18} {'值 (GeV)':>12}  來源")
for name, val, src in candidates:
    mark = "★" if 10 <= val <= 400 else " "
    print(f"  {mark}{name:<16} {val:>12.4f}  {src}")

print()
print(f"  AMS-02 正電子異常區間: 10 - 300 GeV")
print(f"  IDCM 唯一 GeV 級結構標度 = v_SM = 246.22 GeV (dev=0)")
print(f"  ⟹ 正電子異常能量標度 ~ 246 GeV 係結構候選 (v_SM 參與)")
print()

print("=" * 72)
print("[3] O54 冪律 fit 指數 0.258 結構來源搜尋")
print("=" * 72)
target = 0.25812150940979006
print(f"  目標: gamma_W = {target:.6f}")
print(f"  f_W(E) = 0.0400·E^0.258 (冪律上升)")

# 搜尋結構數組合
struct = {
    "N_d": 44, "B": 4, "F5": 5, "F6": 8, "F7": 13,
    "L4": 7, "L5": 11, "L6": 18, "L7": 29,
    "M": 33, "mu2": 2, "F_proj": 17, "N_gen": 3,
    "90": 90, "88": 88, "178": 178, "36": 36, "98": 98,
    "omega22": 2*math.sin(22*math.pi/88),
    "omega20": 2*math.sin(20*math.pi/88),
    "gamma7": 4*math.sin(7*math.pi/88)**2,
    "gamma20": 4*math.sin(20*math.pi/88)**2,
}
print(f"  搜尋 a/b, a/(b+c), (a-b)/c, a^b 組合接近 {target:.6f}:")
found = []
for ka, va in struct.items():
    for kb, vb in struct.items():
        if vb == 0: continue
        for kind in ["div", "ratio"]:
            val = va/vb
            if abs(val - target)/target < 0.002:
                found.append((abs(val-target)/target, f"{ka}/{kb} = {val:.6f}"))
        for kc, vc in struct.items():
            val = va/(vb+vc)
            if abs(val - target)/target < 0.002:
                found.append((abs(val-target)/target, f"{ka}/({kb}+{kc}) = {val:.6f}"))
            val = (va-vb)/vc
            if abs(val - target)/target < 0.002:
                found.append((abs(val-target)/target, f"({ka}-{kb})/{kc} = {val:.6f}"))
found.sort()
for dev, expr in found[:15]:
    print(f"    dev {dev*100:.3f}%: {expr}")

# 特別檢查
print()
print(f"  直接檢查:")
print(f"    gamma7/gamma20 = {struct['gamma7']/struct['gamma20']:.6f} (e/mu 質量比, O54)")
print(f"    omega22/88     = {struct['omega22']/88:.6f}")
print(f"    17/66          = {17/66:.6f}")
print(f"    17/(44+22)     = {17/66:.6f}")
print(f"    F_proj/66      = {17/66:.6f} (66 = 48+18 態)")
print(f"    gamma_44/90    = {4/90:.6f}")
print(f"    L4/27          = {7/27:.6f}")
print(f"    1/phi^2/4      = {1/phi**2/4:.6f}")

print()
print("=" * 72)
print("[4] 正電子能量標度接駁 - 零參數候選")
print("=" * 72)
print(f"""
  AMS-02 正電子異常特徵:
    - 分數 e+/(e++e-) 由 10 GeV 10% 升到 300 GeV 20%
    - 純次級模型預測下降 -> 需要初級源
    - 初級源能量標度 ~ GeV-TeV

  IDCM 零參數候選:
    A) v_SM = 246.22 GeV  (O40, dev=0): 電弱標度
       → W 衰變到 e+e- 需要 m_W > 2m_e, 但能量上限 = m_W/2
       → 246 GeV 源 → 正電子能量 < 123 GeV (唔夠 300 GeV)
    
    B) O54 CR boost: E_e+ = gamma_p · E_res
       → E_res = 47.6 MeV (模式加權), gamma_p = E_p/m_p
       → 需要 E_p ~ 200 GeV-6 TeV 質子 -> 正電子 10-300 GeV
       → 但 gamma_p 分佈 = CR 譜 (p = 2.7 外部輸入!)
    
    C) 如果正電子能量 = E_n·(v_SM/M0) = M0·omega_n · (246/0.0279)
       = omega_n · 8824 GeV?? 唔對 (標度錯)

  🔴 核心開放: IDCM 冇「天然 GeV 正電子」結構
     W-field 得 MeV 級, 唯一 GeV 標度係 SM 電弱 sector (v_SM/m_W)
     O54 用 CR boost 係唯一接駁, 但 gamma_p 冇 IDCM 結構
""")
print(f"  結論: O119 需要決定 (1) 正電子源係咪 W-field 靜止衰變 (唔可能到 GeV)")
print(f"              (2) 定係 W-field 共振 + CR 加速 (O54 方向, 但 gamma_p 要結構化)")
print(f"              (3) 定係 v_SM = 246 GeV 電弱過程 (SM W -> e+e-? 唔允許)")

results = {
    "m_formula_A_MeV": [float(m_A[0]), float(m_A[6]), float(m_A[-1])],
    "m_formula_B_tachyon_n": [1, 2],
    "m_formula_B_stable_range_MeV": [float(min(m_B[2:])*1000), float(max(m_B[2:])*1000)],
    "v_SM_GeV": v_EW,
    "gamma_W_fit": target,
    "gamma_W_structure": "本 script 搜尋 (a/b, a/(b+c), (a-b)/c) 未覆蓋 a/(b-c) 格式 → miss 8/31 = F6/(Nd-F7) dev 0.022% (見 script 04)",
    "highest_W_field_mass_MeV": float(max(m_A)),
    "conclusion": "W-field 兩套質量公式都係 MeV 級; 唯一 GeV 標度 v_SM=246 GeV; O54 CR boost 嘅 gamma_p 係外部輸入"
}
with open("data/02_mass_scale_audit.json", "w") as f:
    json.dump(results, f, indent=1, ensure_ascii=False)
print("✅ data/02_mass_scale_audit.json")
