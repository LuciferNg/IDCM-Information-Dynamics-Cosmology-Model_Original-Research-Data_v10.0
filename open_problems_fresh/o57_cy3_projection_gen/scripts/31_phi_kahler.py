#!/usr/bin/env python3
"""
O57 四期 31: φ 結構 Kähler 參數搜索 — 質量階層 10⁸
====================================================
三期發現: 隨機 log-normal Kähler 參數可達 e^-V 範圍 1.9×10⁷ (spread=4)
四期目標: 用 φ 結構 (φ 冪 / Lucas 數) 構造 Kähler 參數,
          睇下能唔能達到 SM 質量階層 10⁸, 而且係「結構性」唔係隨機!

φ 結構候選:
  1. t_i = φ^{k_i}, k_i 整數 (0..36?)
  2. t_i = L_k (Lucas 數)
  3. t_i = F_k (Fibonacci 數)
  4. t_i = φ^{n_i} 按 divisor index 排列
  5. t_i = 3×12 block 結構: 每代一個 φ 冪尺度

物理: 質量階層 = Kähler moduli 嘅指數壓抑
      e^{-V} = e^{-Σ t_i κ_ijk}
      V 大 → 質量細; V 細 → 質量大
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 四期 31: φ 結構 Kähler 參數搜索")
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

# ============ 1. 載入 ============
kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])
print(f"  κ: {kappa.shape}, 非零 {np.count_nonzero(kappa)}")

SM_NEED = 1.7e8  # m_t/m_ν

def eval_range(t):
    """計 e^-V 範圍比 (positive volumes)"""
    v = np.einsum('i,ijk->jk', t, kappa)
    v = (v + v.T) / 2
    np.fill_diagonal(v, 0)
    pos = v[v > 1e-10]
    if len(pos) < 2:
        return 1.0
    return pos.max() / pos.min()

def eval_masses(t):
    """計 e^-V 質量譜"""
    v = np.einsum('i,ijk->jk', t, kappa)
    v = (v + v.T) / 2
    np.fill_diagonal(v, 0)
    pos = v[v > 1e-10]
    return np.exp(-pos)

# ============ 2. φ 冪候選 ============
print("\n[1] φ 冪 Kähler 參數")
# t_i = φ^{k_i}: 有好多選擇
# 候選 A: k_i = i-1 (0..35)
tA = phi ** np.arange(36)
rA = eval_range(tA)
print(f"  A: t_i = φ^(i-1), range = {rA:.2e}")
print(f"     {'✅ 達標' if rA > 1e7 else '❌ 唔夠'} (SM 需 {SM_NEED:.0e})")

# 候選 B: k_i = 36-i (反轉)
tB = phi ** (35 - np.arange(36))
rB = eval_range(tB)
print(f"  B: t_i = φ^(35-i), range = {rB:.2e}")

# 候選 C: k_i = (i mod 12) (3×12 block, 每代一樣)
tC = phi ** (np.arange(36) % 12)
rC = eval_range(tC)
print(f"  C: t_i = φ^(i mod 12), range = {rC:.2e}")

# 候選 D: k_i = (i mod 12) + 12×(i//12) (每代遞增)
tD = phi ** ((np.arange(36) % 12) + 12 * (np.arange(36) // 12))
rD = eval_range(tD)
print(f"  D: t_i = φ^(i mod 12 + 12×gen), range = {rD:.2e}")

# 候選 E: 每代一個尺度 t = [1, φ^a, φ^b] ⊗ 1₁₂
for (a, b) in [(6, 12), (8, 16), (4, 12), (6, 14), (5, 10), (3, 9), (7, 14), (4, 8), (6, 13)]:
    tE = np.concatenate([np.ones(12), phi**a * np.ones(12), phi**b * np.ones(12)])
    rE = eval_range(tE)
    print(f"  E({a},{b}): t = [1, phi^{a}, phi^{b}]⊗1_12, range = {rE:.2e}")

# ============ 3. Lucas/Fibonacci ============
print("\n[2] Lucas/Fibonacci 候選")
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199]
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

# 候選 F: t_i = L_{i mod 12} (3×12 block)
tF = np.array([L[i % 12] for i in range(36)])
rF = eval_range(tF)
print(f"  F: t_i = L_{'{i mod 12}'}, range = {rF:.2e}")

# 候選 G: t_i = F_{i mod 12 + 1} (1..12, 避開 F_0=0)
tG = np.array([F[(i % 12) + 1] if (i % 12) + 1 < len(F) else F[11] for i in range(36)])
rG = eval_range(tG)
print(f"  G: t_i = F_{'{i mod 12 + 1}'}, range = {rG:.2e}")

# ============ 4. 3×12 block + 代尺度 ============
print("\n[3] 3×12 block + 代尺度 (φ 冪)")
# J* 本身: t_i = Jstar (三期已知 range 1.85)
jd = json.load(open(os.path.join(O53, "Jstar_36D.json")))
Jstar = np.array(jd.get("Jstar_36D", jd))
rJ = eval_range(Jstar)
print(f"  J*: range = {rJ:.2f} (已知)")

# 候選 H: J* × φ^{gen 尺度} (block-wise scaling)
for a in [3, 4, 5, 6, 7, 8, 10]:
    scale = np.concatenate([np.ones(12), phi**a * np.ones(12), phi**(2*a) * np.ones(12)])
    tH = Jstar * scale
    rH = eval_range(tH)
    print(f"  H(a={a}): J*×[1,phi^" + str(a) + f",phi^{2*a}]⊗1, range = {rH:.2e}")

# ============ 5. 最佳 φ 候選質量譜 ============
print("\n[4] 最佳 φ 候選質量譜")
# 揀 range 最大嘅候選
candidates = {
    "A": (tA, rA), "B": (tB, rB), "C": (tC, rC), "D": (tD, rD),
    "F": (tF, rF), "G": (tG, rG), "J*": (Jstar, rJ),
}
best_name = max(candidates, key=lambda k: candidates[k][1])
best_t, best_r = candidates[best_name]
print(f"  最佳: {best_name}, range = {best_r:.2e}")
masses = eval_masses(best_t)
m_sorted = np.sort(masses)[::-1]
print(f"  e^-V 質量譜 (top 15):")
for i, m in enumerate(m_sorted[:15]):
    print(f"    m{i+1:2d}: {m:.4e}")

# 統計: 有幾多個「代」?
# 如果質量譜有 3 個 cluster → 代結構
log_m = np.log(m_sorted)
gaps = np.diff(log_m)
big_gaps = np.sort(gaps)[::-1][:5]
print(f"  最大 log-gaps: {[f'{g:.3f}' for g in big_gaps]}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("四期 31 總結:")
print("=" * 72)
print(f"""
  φ 結構 Kähler 參數搜索:
  ─────────────────────────────────
  1. φ 冪候選:
     A (t=φ^(i-1)): {rA:.2e}
     C (t=φ^(i mod 12)): {rC:.2e}
     D (3×12 代遞增): {rD:.2e}
  2. Lucas/Fibonacci:
     F (L mod 12): {rF:.2e}
     G (F mod 12): {rG:.2e}
  3. J* block scaling:
     H(a): {[f'{eval_range(Jstar * np.concatenate([np.ones(12), phi**a*np.ones(12), phi**(2*a)*np.ones(12)])):.1e}' for a in [3,4,5,6,7,8,10]]}
  4. 最佳: {best_name} ({best_r:.2e})
  SM 需要: {SM_NEED:.0e}

  {'✅ 有 φ 結構候選達標!' if best_r > 1e7 else '❌ 冇 φ 結構候選達標'}
""")

results = {
    "test": "O57 四期 31: φ Kähler 搜索",
    "A": float(rA), "B": float(rB), "C": float(rC), "D": float(rD),
    "F_lucas": float(rF), "G_fib": float(rG),
    "Jstar": float(rJ),
    "best": best_name,
    "best_range": float(best_r),
    "sm_needed": SM_NEED,
    "passed": passed, "failed": failed
}
with open("data/31_phi_kahler.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 四期 31 完成!")
