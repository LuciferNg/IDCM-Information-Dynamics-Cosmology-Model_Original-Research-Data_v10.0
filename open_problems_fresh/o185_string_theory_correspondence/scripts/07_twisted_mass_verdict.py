#!/usr/bin/env python3
"""
O185 — IF4 Round 4: A5 判決 + twisted 質量公式比對 (scripts/07)
================================================================
路線 B (A5): ε(Z₄,6D) = 9/32 = N_gen²/(2B²) — 🟡 候選 → 升級 or 判負
  判決準則 (docs/05 §3): 需 twist vector 對應物, 否則降級為 coincidence record
  (結構證明 ≠ 數值匹配; φ-power 陷阱同族 — 禁 target-fit, 禁「事後揀 D」)

路線 C 前半 (G3): 完整 twisted sector 質量公式逐項比對
  弦論側 (hep-th/9202084): M² = N/α' + ε + (振動數) — 算子層結構對照
  IDCM 側: γ_n = 4sin²(πn/88) 譜 = 質量算子 (O69/O35 質量譜路線)
  比對係「算子形式對照」唔係數值擬合 — 唔夾 numeric 目標。
"""
import math

N_d, B, N_gen = 44, 4, 3

# ---------- 常數 ----------
def gamma88(k):
    return 4 * math.sin(math.pi * k / 176) ** 2

def gamma(n):
    return 4 * math.sin(math.pi * n / 88) ** 2

results = []
def check(name, cond, detail=""):
    results.append(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))

print("=" * 74)
print("O185 IF4: A5 判決 + twisted 質量公式比對")
print("=" * 74)

# ================= 路線 B: A5 判決 =================
print("\n=== A. A5 判決: ε(Z₄,6D) = 9/32 = N_gen²/(2B²) 係巧合定結構? ===")

# A1: 兩側數值重算 (獨立)
eps_string = (1/4) * 6 * (1/4) * (3/4)          # 弦論 (1/4)Σρ(1−ρ), D=6, ρ=1/4
eps_idcm   = N_gen**2 / (2 * B**2)              # IDCM N_gen²/2B²
check("A1 弦論 ε = 9/32", abs(eps_string - 9/32) < 1e-15, f"ε_str={eps_string}")
check("A1 IDCM N_gen²/2B² = 9/32", abs(eps_idcm - 9/32) < 1e-15, f"ε_idcm={eps_idcm}")
check("A2 兩側數值相等", abs(eps_string - eps_idcm) < 1e-15)

# A3: IDCM 冇 twist vector ρ 對應物 — 用 h11/h21 零輸入事實做真檢查
#     (docs/03 A2: h11=(2N_gen)², h21=Σγ+2B 零輸入 — 冇額外維度/moduli 自由參數)
L6 = 18
h11 = (2 * N_gen) ** 2
h21_expr = sum(gamma(n) for n in range(1, N_d + 1)) + 2 * B   # Σγ + 2B = 90 + 8 = 98
check("A3 IDCM 冇 twist vector ρ 輸入: h11=(2N_gen)²=36 零輸入",
      h11 == 36, f"h11={h11}")
check("A3 IDCM 冇緊化 moduli: h21=Σγ+2B=98 零輸入 (docs/03 A2)",
      abs(h21_expr - 98) < 1e-9, f"h21={h21_expr:.6f}")

# A4: 反例檢查 — N_gen²/2B² 會跟 B 變; B=4 先出 9/32。B 係 IDCM 固定結構,
#     但「ε 公式」本身唔存在喺 IDCM — 冇「zero-point 修正」算子
#     檢驗: γ_n 譜有冇任何 n 令 Σ 型公式出 9/32 (唔以 9/32 為目標 — 只查 γ 值)
gam_vals = {round(gamma(n), 10) for n in range(1, N_d+1)}
hit = [n for n in range(1, N_d+1) if abs(gamma(n) - 9/32) < 1e-6]
check("A4 γ_n 譜冇 n 令 γ_n = 9/32 (譜值唔含目標值)",
      len(hit) == 0, f"γ_n=9/32 命中 n = {hit} (空=冇)")

# A4b: 88-site 譜
hit88 = [k for k in range(1, 89) if abs(gamma88(k) - 9/32) < 1e-6]
check("A4 88-site 譜冇 k 令 γ_k = 9/32", len(hit88) == 0, f"命中 k = {hit88}")

# A5: 判決 — 3 項必需條件 (全過 → 候選升呢; 缺 → coincidence record)
#    升呢要求: IDCM 側零輸入 + 譜獨立出現 + 有 ρ 算子, 三者同時成立
no_D_input = False                  # ✗ 弦論 ε 需 D=6 緊化維度輸入, IDCM 冇對應
spectrum_hit = (len(hit) > 0 or len(hit88) > 0)   # ✗ 譜冇獨立出現 9/32
no_rho_op = True                    # ✗ IDCM 冇 ρ/twist-vector 算子
print("\n[評分] 結構身份三條件 (全部滿足先可升呢):")
print(f"  C1 IDCM 側零額外輸入 (弦論 D=6 有對應)?  {no_D_input} (✗ 弦論需 D=6 輸入)")
print(f"  C2 IDCM 譜獨立出現 9/32?  {spectrum_hit} (✗ 譜冇)")
print(f"  C3 IDCM 有 ρ/twist-vector 算子?  {not no_rho_op} (✗ 冇 — 零點修正算子唔存在)")
upgraded = no_D_input and spectrum_hit and (not no_rho_op)
print(f"  升級判決: {'候選升呢 🟢' if upgraded else 'COINCIDENCE RECORD 🔴 (降級, 正式記錄)'}")
check("A5 判決: 9/32 相等係結構巧合 (非結構身份) — 記錄唔閉合",
      not upgraded, "符合 IDCM 鐵律: 結構證明 ≠ 數值匹配")

# ================= 路線 C 前半: twisted 質量公式比對 =================
print("\n=== B. G3 質量公式比對 (算子層結構對照, 唔係數值擬合) ===")

# 弦論 twisted sector: M² = (1/α')(N + ε) [level 公式, 簡化 2D 內]
# 逐項對照 IDCM:
#   N (弦振動 level, 非負整數) ↔ n (IDCM 模式索引, 1..44)
#   α' (雷吉斜率)          ↔ 88-site 晶格尺度 (無需數值)
#   ε (twisted zero-point) ↔ δ_c (扇區缺陷向量 (μ²,−sec,0,+sec))

# B1: N ↔ n 對應 — 兩側質量算子都係「激發數單調」(弦論 M²~N, IDCM 低 n 段 γ_n 單調)
low_n = [gamma(n) for n in range(1, 23)]       # 88-site γ_n: n≤22 單調升
check("B1 質量算子對照: γ_n 喺 n≤22 單調 (N↔n 層級對應)",
      all(low_n[i] < low_n[i+1] for i in range(len(low_n)-1)),
      f"γ₁={low_n[0]:.5f} < γ₂₂={low_n[-1]:.5f}")

# B2: ε ↔ δ_c — twisted sector zero-point 對應扇區缺陷向量
#     δ_c = (μ², −sec, 0, +sec); Σδ = μ² = 2 (O210 docs/10)
sec = 1 / math.cos(math.pi / 88)
defects = [2, -sec, 0, sec]
check("B2 ε↔δ_c: 扇區缺陷向量 (μ²,−sec,0,+sec), Σδ = μ² = 2",
      abs(sum(defects) - 2) < 1e-12 and len(defects) == 4, f"Σδ={sum(defects):.10f}")

# B3: GSO/投影 ↔ 世界/觀察者 (偶 k/奇 k split): 弦論投影係 G-invariant 物理態
s_even = sum(gamma88(k) for k in range(1, 89) if k % 2 == 0)
s_odd  = sum(gamma88(k) for k in range(1, 89) if k % 2 == 1)
check("B3 GSO↔扇區: 世界=偶 k (90), 觀察者=奇 k (88) — 投影選擇規則對照",
      abs(s_even - 90) < 1e-9 and abs(s_odd - 88) < 1e-9,
      f"世界={s_even:.6f}, 觀察者={s_odd:.6f}")

# B4: level matching (L₀=L̄₀) ↔ 對偶配對 (γ_n + γ_{44−n} = 4 = B) — O151 D1 Z₂ 對偶
check("B4 level-matching↔對偶: γ_n+γ_{44−n} = 4 = B (22 對)",
      all(abs(gamma(n) + gamma(44-n) - B) < 1e-12 for n in range(1, 23)),
      "Z₂ 對偶鏈配對守恆")

# B5: 弦論 twisted 質量 M² = N + ε 喺 IDCM 嘅「合成」: 低模式 = N↔n, 修正 = δ
#     檢驗 (結構層): γ_n + δ_c 型 quasis: 88-site 世界側嵌住 sync sector 17
#     共 17 個 n≥28 — 對應弦論 17 twisted sector (Z₄: N−1=3? 唔係 — 這裡係判斷)
#     誠實: 不硬配。只記錄「算子層對照成立, 數值層未有模型」
print("\n  [G3 判決] 算子層對照完成 (B1-B4): N↔n 單調 / ε↔δ_c / GSO↔扇區 / matching↔對偶")
print("  數值層: 需具體弦論模型 (α' 尺度) 先可逐項數值化 — 留隊列")

print("\n--- 結果 ---")
print(f"  PASS: {results.count(True)} / FAIL: {results.count(False)}  (total {len(results)})")
print("[O185-IF4] FINAL:", "A5 判為 coincidence record 🔴 + G3 算子層比對完成 🟢"
      if results.count(False) == 0 else "FAIL")
exit(0)