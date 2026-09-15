#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 交回 — B' 判定: P_n = 1 + 2φ⁻¹n + K₂n² 係咪同被證偽嘅伸長定律同一結構對象?
================================================================================
背景
----
O169 交回分類將 2φ⁻¹ 分三類:
  A  伸長/投影因子 (1 + 2φ⁻¹ℓ) → 🔴 已證偽
  B  φ-代數常數 (Ω_b = 2φ⁻¹/(5(φ⁴−1)) 等) → ✅ 唔受影響
  B′ 同形函數 P_n = 1 + 2φ⁻¹n + K₂n² → 🟡 待核對   ← 本腳本

判定準則 (三問)
--------------
  Q1 結構角色: P_n 嘅 n 同伸長嘅 ℓ 係咪同一個「層索引」?
  Q2 導數身份: P_n 嘅線性係數 2φ⁻¹ 係咪「每層增益」呢個被證偽嘅對象?
  Q3 承載性:   P_n 嘅數值輸出 (Ω_DM/Ω_b = 6.5030) 喺現行 v10.0 鏈仲有冇承載?

反幻覺鐵律
----------
  - 所有數值 mpmath 重算 (dps = 40), 唔抄文檔
  - 文檔聲稱一律當「待驗證」, 唔當事實
  - 判定唔靠推斷: 逐條列證據 + 反證據
"""
import mpmath as mp

mp.mp.dps = 40

# ============ 結構常數 ============
phi = (1 + mp.sqrt(5)) / 2
inv = 1 / phi
N_d, B, L5, N_gen, M, CY3 = 44, 4, 11, 3, 33, 134
h11, h21 = 36, 98
K2_doc = mp.mpf("0.029238")
RATIO_V9 = mp.mpf("6.5030")          # v9.0 CY₃ 二階輸出
F5, F7, L0 = 5, 13, 2

GAM = {n: 4 * mp.sin(mp.pi * n / 88) ** 2 for n in range(1, N_d + 1)}
VG = {n: mp.cos(mp.pi * n / 88) for n in range(1, N_d + 1)}
SIG_ODD = sum(GAM[n] for n in range(1, N_d + 1) if n % 2 == 1)

def sec(x): return 1 / mp.cos(x)

print("=" * 78)
print("O169 交回 — B' 判定: P_n = 1 + 2φ⁻¹n + K₂n²")
print("=" * 78)

# ---------------------------------------------------------------
print("\n[Q1] 結構角色: P_n 嘅 n 同伸長嘅 ℓ 係咪同一個層索引?")
print("-" * 78)
print("""
  伸長 (O76/O51):  ℓ = log₄(1+z)           — 距離/尺度投影嘅「層」索引
                   E(ℓ) = 1 + 2φ⁻¹ℓ        (ℓ 連續, ℓ ∈ [0, ℓ_Nyq])
  P_n  (v9.0 65):  n = K_Chain mode 索引   — 質量分配嘅「層」索引
                   P_n = 1 + 2φ⁻¹n + K₂n²  (n 離散, n ∈ [1, 44])

  文檔證據 (o116 docs/02 §2.3):
    「v9.0 的 CY₃ 投影算子 P_n 與 v10.0 的 K_Chain 質量分配 P_n 為同一結構」
    「2φ⁻¹ 作為跨尺度幾何不變量, 在兩框架中一致」
  文檔證據 (o116 docs/02 §1 表): 65_projection_jacobian_micro.md = 「P_n 推導」
    → 檔名即 "projection jacobian" — 同 H_eff = c/(dD/dz) 用嘅詞一樣
  文檔證據 (o116 docs/02 §1 表): 「✅ 跨尺度自相似」(cross-scale self-similarity)
    → 即宣稱「同一個每層因子跨質量/距離尺度共用」 = 正是 O169 證偽嘅對象
""")

# 檢查: 兩個索引嘅數值範圍/定義係咪同一回事
l_nyq = mp.log(1 + 2, 4)   # z = 2 對應值 (僅示範連續性)
print(f"  ℓ 取值示例: z=2 → ℓ = log₄3 = {float(l_nyq):.6f}   (連續, 可取任意非負值)")
print(f"  n 範圍: [1, 44]              (離散, 44 = N_d)")
print(f"  → 索引定義唔同 (連續尺度 vs 離散 mode); 但宣稱嘅「每層因子」係同一個 2φ⁻¹")
Q1 = "SAME_OBJECT"     # 「每層因子」層面
print(f"\n  Q1 判定: 索引定義唔同, 但**宣稱嘅每層因子係同一個 2φ⁻¹** → 同一結構對象 (角色層面)")

# ---------------------------------------------------------------
print("\n[Q2] 導數身份: 2φ⁻¹ 係咪「每層增益」呢個被證偽嘅對象?")
print("-" * 78)

# 伸長: 舊宣稱 dE/dℓ = 2φ⁻¹ ; O169 實測 (DESI DR2 D_M×6 自由擬合) a = 0.994278 ± 0.04951
# 新結構: a = ⟨γ⟩_odd/2 = Σγ_odd/N_d = μ²/2 = 1 EXACT
a_struct = SIG_ODD / N_d
print(f"  舊宣稱「每層增益」 = 2φ⁻¹ = {float(2*inv):.10f}")
print(f"  O169 自由擬合     = 0.994278 ± 0.04951  → 距 2φ⁻¹ = "
      f"{float((2*inv - mp.mpf('0.994278'))/mp.mpf('0.04951')):.2f}σ  ← 排除")
print(f"  新結構身份        = ⟨γ⟩_odd/2 = Σγ_odd/N_d = {float(SIG_ODD):.6f}/{N_d} = {float(a_struct):.10f}  EXACT")
print(f"  ★ 即「每層增益 = 2φ⁻¹」被證偽; 真值 = {a_struct} = 1")
print(f"  ★ P_n 嘅線性係數 = 2φ⁻¹ = {float(2*inv):.10f}  → **同一個被證偽嘅量**")
print(f"  → 若 P_n 嘅 2φ⁻¹ 亦係「每層增益」語義 → 同受證偽")
Q2 = "FALSIFIED_IF_SAME_SEMANTICS"
print(f"\n  Q2 判定: 數值相同 (2φ⁻¹) 且文檔明確宣稱「跨尺度自相似 / projection jacobian」")
print(f"           → 語義上係同一個「每層增益」→ **受證偽**")

# ---------------------------------------------------------------
print("\n[Q3] 承載性: P_n 嘅數值輸出喺現行 v10.0 鏈仲有冇承載?")
print("-" * 78)

# P_n 唯一數值輸出: Ω_DM/Ω_b = 6.5030 (v9.0 CY₃ 二階)
print(f"\n  P_n 唯一數值輸出 = Ω_DM/Ω_b = {RATIO_V9}  (v9.0, 偏差 0.05% vs 6.5)")
print(f"  v10.0 (O14) 取代式: Ω_DM/Ω_b = F₇/L₀ = {F7}/{L0} = {float(mp.mpf(F7)/L0)}  EXACT")
print(f"                             Ω_b/Ω_m  = 2/(3F₅) = 2/{3*F5} = {float(mp.mpf(2)/(3*F5))}  EXACT")

# 驗: 兩個 v10.0 比率係咪自洽 (純 φ-代數, 唔涉伸長)
r_dm_b = mp.mpf(F7) / L0
r_b_m = mp.mpf(2) / (3 * F5)
print(f"\n  自洽檢查 (純 F-數, 唔涉伸長):")
print(f"    Ω_m/Ω_b = 1 + Ω_DM/Ω_b = 1 + {r_dm_b} = {float(1 + r_dm_b)} = 15/2 = {float(mp.mpf(15)/2)}")
print(f"    1/(Ω_b/Ω_m) = 1/{r_b_m} = {float(1/r_b_m)} = 15/2 = {float(mp.mpf(15)/2)}")
print(f"    → 一致: {abs((1+r_dm_b) - 1/r_b_m) < mp.mpf('1e-30')}  ✅ (兩式皆純 φ-代數 → 角色 B)")

# 但 v9.0 值 6.5030 仍在活躍腳本中!
print(f"\n  ⚠️ 掃描: v9.0 值 {RATIO_V9} 喺現行腳本/文檔嘅殘留")
import os, re
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
assert os.path.isdir(os.path.join(REPO, "bbn")), f"REPO 推導錯: {REPO}"
pat = re.compile(r"6\.5030|6\.503")
hits = []
for root, dirs, files in os.walk(REPO):
    dirs[:] = [d for d in dirs if d not in (".git", "data")]
    for fn in files:
        if not fn.endswith((".py", ".md", ".json", ".txt")):
            continue
        p = os.path.join(root, fn)
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    if pat.search(line):
                        hits.append((os.path.relpath(p, REPO), i, line.strip()[:110]))
        except Exception:
            pass
for h in hits:
    print(f"    {h[0]}:{h[1]}  {h[2]}")
print(f"    → 共 {len(hits)} 處")

# ---------------------------------------------------------------
print("\n[Q3b] P_n 殘留嘅數值代價: η_B 各版本精算 (mpmath dps=40)")
print("-" * 78)

H0_si = mp.mpf("72.59") * 1000 / mp.mpf("3.0856775814913673e22")
G_si = mp.mpf("6.67430e-11")
rho_c = 3 * H0_si**2 / (8 * mp.pi * G_si)
T_cmb = mp.mpf("2.7284")
kB = mp.mpf("1.380649e-23")
hbar = mp.mpf("6.62607015e-34") / (2 * mp.pi)
c_si = mp.mpf("299792458.0")
n_gamma = 2 * mp.zeta(3) / mp.pi**2 * (kB * T_cmb / (hbar * c_si))**3
m_p_kg = mp.mpf("938.27208816") * mp.mpf("1.78266192e-30")
def eta_B(Ob): return Ob * rho_c / (m_p_kg * n_gamma)

OL_O39, Om_O39 = mp.mpf(41) / 60, mp.mpf(19) / 60
OL_O37 = 4 / (phi**4 - 1); Om_O37 = 1 - OL_O37

variants = [
    ("v9.0 殘留: Ω_m(O39)/(1+6.5030)", Om_O39 / (1 + RATIO_V9)),
    ("v10.0 現行: Ω_m(O39)×2/15",      Om_O39 * 2 / 15),
    ("O14 文檔:  2φ⁻¹/(5(φ⁴−1))",      2 * inv / (5 * (phi**4 - 1))),
    ("★ bbn 文檔實際用: Ω_m(O37)/(1+6.5030)", Om_O37 / (1 + RATIO_V9)),
]
DOC_ETA = mp.mpf("6.0622e-10"); PLANCK_ETA = mp.mpf("6.10e-10")
print(f"  {'變體':<40}{'Ω_b':>13}{'η_B':>16}{'vs 6.0622e-10':>15}{'vs 6.10e-10':>13}")
print("  " + "-" * 97)
for name, Ob in variants:
    e = eta_B(Ob)
    print(f"  {name:<40}{float(Ob):>13.9f}{float(e):>16.6e}"
          f"{float((e - DOC_ETA) / DOC_ETA * 100):>14.4f}%{float((e - PLANCK_ETA) / PLANCK_ETA * 100):>12.4f}%")

print(f"""
  ★★ 判定: bbn/06_complete_record.md 嘅 η_B = 6.0622×10⁻¹⁰ **精確重現**於
     「Ω_m(O37)/(1+6.5030)」行 (dev 0.0000%) — 即該數值係**雙重 stale**:
        (i)  Ω_Λ 用已撤銷嘅 O37 版 4/(φ⁴−1) = 0.6832816 (非 O39 版 41/60)
        (ii) Ω_DM/Ω_b 用 v9.0 P_n 輸出 6.5030 (非 v10.0 F₇/L₀ = 6.5)

  ★ v10.0 現行結構鏈給出 η_B = {float(eta_B(Om_O39*2/15)):.6e}
      = {float((eta_B(Om_O39*2/15) - PLANCK_ETA) / PLANCK_ETA * 100):.3f}% vs 6.1×10⁻¹⁰
      （文檔聲稱 0.62% → 現行鏈其實**更準**）
    且 Ω_b = 19/450 = {float(Om_O39*2/15):.9f} 完全由 F-數比率給出, 零 P_n 依賴。
""")

# ---------------------------------------------------------------
print("\n" + "=" * 78)
print("[判定]")
print("=" * 78)
print(f"""
  Q1 結構角色 : 索引定義唔同, 但宣稱嘅「每層因子」係同一個 2φ⁻¹  → 同一對象
  Q2 導數身份 : 2φ⁻¹ = 「每層增益」被 O169 證偽 (真值 = 1)      → 🔴 受影響
  Q3 承載性   : P_n 唯一輸出 6.5030 已被 v10.0 的 F₇/L₀ = 6.5 取代
                但 {len(hits)} 處殘留 (含活躍腳本)               → 🔴 需清理

  ★ B' 判定: **P_n 屬 A 類 (受證偽), 唔係 B 類**
     理由: (i) 文檔明確自稱 "projection jacobian" + "跨尺度自相似"
           (ii) 線性係數數值 = 2φ⁻¹ = 被證偽嘅「每層增益」
           (iii) O169 新結構喺**同一個 K_Chain 譜機制**上給出斜率 1
                 (⟨γ⟩_odd/2 = Σγ_odd/N_d) — 即質量層與距離層共用嘅每層增益
                 係 1, 唔係 2φ⁻¹

  ★ 但 P_n 嘅**數值後果已被 v10.0 隔離**:
     Ω_DM/Ω_b = 13/2 = F₇/L₀ 同 Ω_b/Ω_m = 2/15 = 2/(3F₅) 都係純 F-數比率,
     唔經 P_n、唔經伸長 → 屬角色 B, **唔受影響**。
     ⇒ 清理工作 = 移除 P_n 作為「推導來源」嘅語言, 唔係改任何數值。
""")
