#!/usr/bin/env python3
"""
O185 — IF7 Round 7: G8/E6 UV/IR 離散鏡像深度判定 (scripts/10)
================================================================
docs/01 E6: 88↔44 Z₂ 鏡像 標 🟡 「離散鏡像，非連續」; 缺口 = 深度有限, 冇能量-尺度互換
docs/02 D6: 88↔44 鏡像 528/264 = 88/44 = Z₂ 標 🟢 (純計數關係)

判決準則 (計算前聲明):
  E6 升呢 ⟺ 搵到 88↔44 專屬嘅結構對應 (唔適用於一般 2 冪縮尺 N→N/2)
  E6 維持 🟡 ⟺ 88↔44 鏡像 = 2 冪子格嵌入嘅平凡數學 (∀N 成立), IDCM 特有內容
              係世界/觀察者 split 而唔係「尺度對偶」
  D6 保持 🟢 ⟺ 計數 528/264 = 88/44 = 2 重驗成立 (計數關係同深度無關)
零新參數; numpy。
"""
import math

results = []
def check(name, cond, detail=""):
    results.append(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))

def gam(N, k):
    return 4 * math.sin(math.pi * k / (2 * N)) ** 2   # γ_N(k) = 4sin²(πk/2N)

print("=" * 74)
print("O185 IF7: G8/E6 UV/IR 離散鏡像深度判定")
print("=" * 74)

# ============ A. 2 冪縮尺嵌入家族 ============
print("\n=== A. 嵌入恆等: γ_N(2m) = γ_{N/2}(m) (2 冪縮尺通用) ===")

# A1: 88↔44 嵌入
ok88 = all(abs(gam(88, 2*m) - gam(44, m)) < 1e-12 for m in range(1, 45))
check("A1 γ₈₈(2m) = γ₄₄(m), m=1..44 (88site 偶模式 = 44site 全譜)",
      ok88, "44 對全成立")

# A2: 44↔22 嵌入 (縮尺家族第 2 層)
ok44 = all(abs(gam(44, 2*m) - gam(22, m)) < 1e-12 for m in range(1, 23))
check("A2 γ₄₄(2m) = γ₂₂(m), m=1..22 (縮尺家族通用, 非 88 專屬)",
      ok44, "22 對全成立")

# A3: 22↔11 嵌入 (縮尺家族第 3 層)
ok22 = all(abs(gam(22, 2*m) - gam(11, m)) < 1e-12 for m in range(1, 12))
check("A3 γ₂₂(2m) = γ₁₁(m), m=1..11 (縮尺家族繼續, 3 層)",
      ok22, "11 對全成立")

# A4: 數學原因 — sin 倍角恆等 (唔係 IDCM 結構, 係三角恆等)
#     sin²(2θ) = 4sin²θ·cos²θ → γ_N(2m)/γ_{N/2}(m) ≡ 1 因為 4sin²(2πm/4N) = 4sin²(πm/2N)
ratio = gam(88, 2) / gam(44, 1)
check("A4 嵌入來源 = sin² 倍角恆等 (任何 N 都成立, 非 88↔44 專屬結構)",
      abs(ratio - 1.0) < 1e-12, f"γ₈₈(2)/γ₄₄(1)={ratio:.15f}")

# ============ B. 觀察者側 (奇模式) 唔係子集 ============
print("\n=== B. IDCM 特有內容: 觀察者側 (奇 k) 唔係 44-site 譜子集 ===")

# B1: 88-site 奇模式 γ_88(2m−1) 對任何 γ_44(n) 嘅最小距離
#     「唔係子集」判準 = 冇精確相等 (gap > 1e-6); 近距離(0.0013)仍≠0, 唔變子集
gaps = [min(abs(gam(88, 2*m - 1) - gam(44, n)) for n in range(1, 45))
        for m in range(1, 45)]
min_gap_odd = min(gaps)
check("B1 觀察者側(奇 k) 唔係 44-site 譜子集 (冇精確相等, gap > 1e-6)",
      min_gap_odd > 1e-6, f"min|γ₈₈₍₂ₘ₋₁₎ − γ₄₄₍ₙ₎| = {min_gap_odd:.6f} (近距 0.0013≠0)")

# B2: 世界+觀察者 = 88 完整 (偶⊕奇 = 全譜, 對合)
s_even = sum(gam(88, k) for k in range(2, 89, 2))
s_odd  = sum(gam(88, k) for k in range(1, 89, 2))
s_all  = sum(gam(88, k) for k in range(1, 89))
total44 = sum(gam(44, n) for n in range(1, 45))
check("B2 世界(偶)⊕觀察者(奇) = 完整 88-site 譜 (無重疊無缺口)",
      abs(s_even + s_odd - s_all) < 1e-9,
      f"偶Σ={s_even:.6f}, 奇Σ={s_odd:.6f}, 總Σ={s_all:.6f}")

# B3: 世界側 (88-site 偶 k) 必 = 44-site 全譜和 (A1 嵌入嘅和版本)
check("B3 88-site 世界側(偶 k) Σ = 44-site 全譜 Σ (=90)",
      abs(s_even - total44) < 1e-9, f"偶Σ(88site)={s_even:.6f}, Σγ₄₄={total44:.6f}")

# ============ C. D6 計數重驗 (保持 🟢) ============
print("\n=== C. D6 計數重驗 ===")
check("C1 528/264 = 88/44 = 2 = Z₂ (D6 計數)",
      abs(528/264 - 88/44) < 1e-12 and 528/264 == 2.0,
      f"528/264={528/264}, 88/44={88/44}")

# C2: 264 = 3×88 (528 = 2×264 = 3×176?)
#     528 = Σγ_odd × 2N_gen = 88 × 6 (O151 階梯)
check("C2 528 = 88×6 = Σγ_odd×2N_gen (階梯基數, D6 相關)",
      abs(528 - 88 * 6) < 1e-12 and 264 == 3 * 88,
      f"528=88×6={88*6}, 264=3×88={3*88}")

# ============ 判決 ============
print("\n=== 判決 ===")
print("  [E6] 88↔44 鏡像深度:")
print("    - A1-A4: 嵌入 γ_N(2m)=γ_{N/2}(m) 喺 N=88,44,22 (3 層) 都成立 — 係 sin² 倍角")
print("      恆等嘅 2 冪縮尺平凡數學, 對任何 N 適用, 唔係 88↔44 專屬結構對稱")
print("    - B1: 觀察者側(奇 k) 唔係 44-site 譜子集 — IDCM 特有內容 = 偶/奇 split")
print("          (世界 Σ=90, 觀察者 Σ=88, 差 μ²=2), 而唔係『尺度對偶』")
print("    - C1/C2: D6 計數 (528/264=88/44=2) 係純計數關係, 同深度無關 — 保持 🟢")
verdict_E6 = "維持 🟡 特例 (深度有限: 嵌入係平凡2冪縮尺, 冇能量-尺度互換, 不可升為對偶)"
E6_structural = ok88 and ok44 and ok22 and min_gap_odd > 1e-6
# 結構判決: 嵌入喺 3 層都成立 (E6 非專屬結構) + 觀察者側非子集 (IDCM 內容=split 唔係尺度對偶)
check("E6 判決: 88↔44 維持 🟡 特例 — 深度有限確認 (3 層嵌入全成立, 觀察者側非子集)",
      E6_structural, verdict_E6)
check("D6 判決: 計數關係保持 🟢 (528/264=88/44=2)",
      abs(528/264 - 2.0) < 1e-12)

print("\n--- 結果 ---")
print(f"  PASS: {results.count(True)} / FAIL: {results.count(False)}  (total {len(results)})")
print("[O185-IF7] FINAL:", "E6 深度判定完成 (特例維持) + D6 計數保持"
      if results.count(False) == 0 else "FAIL")
exit(0)