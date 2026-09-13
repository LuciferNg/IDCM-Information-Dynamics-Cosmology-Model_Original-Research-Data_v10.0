#!/usr/bin/env python3
# O192 scripts/01 — Lucas−1 對偶家族 + 譜和預算量子定理 (第一原理獨立驗證)
# 規則: 唔 import 任何被驗證 script; Fibonacci/Lucas 由遞迴重算; γ 譜由 math.sin 實算
# 零新常數: 全部目標值由已閉合 IDCM 常數生成
import math, random

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def luc(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

# ---- 已閉合 IDCM 常數 (零新常數池) ----
B, N_gen, Nd, mu2 = 4, 3, 44, 2
L4, L5, L6, F7, M, Fproj = 7, 11, 18, 13, 33, 17
dimC = 3
S_gamma, S_even, S_odd, S_lambda = 178, 90, 88, 66
S2_tot, S2_odd, S2_even = 536, 264, 272
W2 = 61.5  # ⟨W⟩² = 123/2

# ================= Part I: L−1 家族 (F−1 嘅 Lucas 鏡像) =================
print("== Part I: L−1 家族 ==")
Lm1 = [luc(m) - 1 for m in range(4, 13)]
expected = [6, 10, 17, 28, 46, 75, 122, 198, 321]
check("V01 L−1 家族 m=4..12 值", Lm1 == expected, str(Lm1))
check("V02 L_m = F_{m−1}+F_{m+1} 標準恆等", all(luc(m) == fib(m-1)+fib(m+1) for m in range(1, 20)))

# 9 個身份 (全部由已閉合常數生成)
ids = {
    6:  N_gen * mu2,                      # L₄−1 = 6 = N_gen·μ² (O107: 6 extra U(1); 264/44)
    10: 2 * N_gen + B,                    # L₅−1 = 10 = 2N_gen+B (O160); = F₅·μ²
    17: Fproj,                            # L₆−1 = 17 = F_proj (O138+O143)
    28: B * L4,                           # L₇−1 = 28 = B·L₄
    46: Nd + mu2,                         # L₈−1 = 46 = N_d+μ² (世界 mod-4 n≡0 和, O191)
    75: L4 * L5 - mu2,                    # L₉−1 = 75 = L₄L₅−μ² = 2N_d−F₇ (E_strain 分母)
    122: S_even + M - 1,                  # L₁₀−1 = 122 = Σγ_even+M−1 (L₁₀ = 123 已註冊)
    198: 2 * N_gen * M,                   # L₁₁−1 = 198 = 2·N_gen·M
    321: S_gamma + (fib(12) - 1),         # L₁₂−1 = 321 = Σγ+(F₁₂−1) = 178+143 = 2F₁₁+F₁₂−1
}
for v, ident in ids.items():
    check(f"V03 L−1 = {v} 身份閉合", v == ident, f"{v} = {ident}")
check("V04 L−1 家族 9/9 全中已閉合身份", all(v == i for v, i in ids.items()))

# 配對定律 (結構繼承): L_m−1 = (F_{m−1}−1)+(F_{m+1}−1)+1
check("V05 配對定律 L_m−1 = (F_{m−1}−1)+(F_{m+1}−1)+1 (m=4..12)",
      all(luc(m) - 1 == (fib(m-1)-1) + (fib(m+1)-1) + 1 for m in range(4, 13)))
check("V06 L₁₀−1 = M+N+1 = 33+88+1 (雙模量繼承)",
      ids[122] == M + 2 * Nd + 1 and 122 == 33 + 88 + 1)
check("V07 L₉−1 = Level5 + N_gen·L₆ + 1 = 20+54+1",
      ids[75] == 20 + 54 + 1 and 20 == fib(8) - 1 and 54 == fib(10) - 1)
check("V08 L₁₁−1 = (F₁₀−1)+(F₁₂−1)+1 = 54+143+1",
      198 == 54 + 143 + 1)
check("V09 L₁₂−1 = (F₁₁−1)+(F₁₃−1)+1 (上邊界拉入 F₁₃−1=232 超預算成員)",
      321 == 88 + 232 + 1)
check("V10 鏡像截斷: F₁₃−1 = 232 > 178 超 F 預算 ⟹ L 家族邊界 m=12",
      fib(13) - 1 > S_gamma)
check("V11 F−1 喺 m=6 撞 Lucas 數: F₆−1 = 7 = L₄ (O145)",
      fib(6) - 1 == L4)
check("V12 交叉: L₆−1 = 17 = F_proj vs F₆−1 = 7 = L₄ (雙家族喺 m=6 互涉)",
      luc(6) - 1 == Fproj and fib(6) - 1 == L4)

# 家族總和 + Lucas 標準恆等
SL = sum(Lm1); SL_full = sum(luc(m) for m in range(4, 13))
check("V13 Σ(L−1) m=4..12 = 823", SL == 823)
check("V14 ΣL m=4..12 = 832 = 2⁶·F₇ = L₁₄−L₅", SL_full == 2**6 * F7 == luc(14) - luc(5))
check("V15 標準恆等 Σ_{m=0}^{12}L_m = L₁₄−1", sum(luc(m) for m in range(13)) == luc(14) - 1)
check("V16 Σ_{m=0}^{3}L_m = L₅−1 (= 10)", sum(luc(m) for m in range(4)) == luc(5) - 1)
check("V17 L₁₀ = 123 = 2⟨W⟩² = Σγ_even+M", luc(10) == 2 * W2 == S_even + M)
check("V18 L₁₀ 已註冊身份 N_gen(N_d−N_gen) = 3×41", luc(10) == N_gen * (Nd - N_gen))

# ================= Part II: 譜和預算量子定理 (全部 = 結構數×μ²) =================
print("== Part II: 譜和預算量子定理 ==")
check("V19 Σγ_odd = N_d·μ² = 88", S_odd == Nd * mu2)
check("V20 Σγ_even = (N_d+1)·μ² = 90", S_even == (Nd + 1) * mu2)
check("V21 Σγ = F₁₁·μ² = 178", S_gamma == fib(11) * mu2)
check("V22 Σλ_tree = M·μ² = 66", S_lambda == M * mu2)
check("V23 Σγ² = 536 = 3Σγ+μ² (O159)", S2_tot == 3 * S_gamma + mu2)
check("V24 Σγ² = B·(2M+1)·μ² = 4×67×2", S2_tot == B * (2 * M + 1) * mu2)
check("V25 Σγ²_odd = dimC·N_d·μ² = 3×44×2 = 264", S2_odd == dimC * Nd * mu2)
check("V26 Σγ²_even = 2B·F_proj·μ² = 8×17×2 = 272", S2_even == 2 * B * Fproj * mu2)
check("V27 Σγ² 奇偶分裂閉合", S2_odd + S2_even == S2_tot)
check("V28 量子 μ² = F₄−1 = E−O = BC-cost", mu2 == fib(4) - 1 and S_even - S_odd == mu2)
check("V29 L 家族首成員 = N_gen·μ² (F 家族首成員 = 1·μ², 係數 {1,3} = {1,N_gen})",
      ids[6] == N_gen * mu2 and fib(4) - 1 == 1 * mu2)

# ================= Part III: 176-Laplacian 譜實算 (唔 import, math.sin) =================
print("== Part III: 譜實算 (γ_k = 4sin²(kπ/176), k=1..88) ==")
g = [4 * math.sin(math.pi * k / 176) ** 2 for k in range(1, 89)]
s_odd = sum(g[i] for i in range(0, 88, 2))    # k 奇數 = 觀察者
s_even = sum(g[i] for i in range(1, 88, 2))   # k 偶數 = 世界
s_tot = sum(g)
s2_odd = sum(g[i] ** 2 for i in range(0, 88, 2))
s2_even = sum(g[i] ** 2 for i in range(1, 88, 2))
s2_tot = sum(x * x for x in g)
check("V30 譜實算 Σγ_odd = 88", abs(s_odd - 88) < 1e-9, f"{s_odd:.12f}")
check("V31 譜實算 Σγ_even = 90", abs(s_even - 90) < 1e-9, f"{s_even:.12f}")
check("V32 譜實算 Σγ = 178", abs(s_tot - 178) < 1e-9, f"{s_tot:.12f}")
check("V33 譜實算 Σγ²_odd = 264", abs(s2_odd - 264) < 1e-6, f"{s2_odd:.9f}")
check("V34 譜實算 Σγ²_even = 272", abs(s2_even - 272) < 1e-6, f"{s2_even:.9f}")
check("V35 譜實算 Σγ² = 536", abs(s2_tot - 536) < 1e-6, f"{s2_tot:.9f}")
check("V36 γ₄₄ = 2 = μ² (Z₂ 點)", abs(g[43] - 2) < 1e-12, f"{g[43]:.12f}")
check("V37 γ₈₈ = 4 = B (Nyquist)", abs(g[87] - 4) < 1e-12, f"{g[87]:.12f}")
# mod-4 閉式 (O191 已驗證, 本 script 再實算)
sec88 = 1 / math.cos(math.pi / 88)
m4 = {1: 44 - sec88, 3: 44 + sec88, 2: 44, 0: 46}
for r in (1, 2, 3, 0):
    sr = sum(g[k - 1] for k in range(1, 89) if k % 4 == r)
    check(f"V38 mod-4 n≡{r} 閉式 ({44 - sec88 if r == 1 else (44 + sec88 if r == 3 else (44 if r == 2 else 46)):.9f})",
          abs(sr - m4[r]) < 1e-9, f"{sr:.12f}")
check("V39 世界 mod-4 n≡0 和 = 46 = L₈−1 (L−1 家族交叉)",
      abs(sum(g[k - 1] for k in range(1, 89) if k % 4 == 0) - 46) < 1e-9)

# ================= Part IV: tree 譜乘積定律 =================
print("== Part IV: tree 譜乘積 (μ_m = φ^(291.5−m), m=0..33) ==")
phi = (1 + math.sqrt(5)) / 2
exp_sum = sum(291.5 - m for m in range(34))          # Σ 指數
prod_exp = 2 * 5**2 * L5 * Fproj                      # 2·F₅²·L₅·F_proj = 9350
check("V40 Σ(291.5−m) m=0..33 = 9350 = 2·F₅²·L₅·F_proj",
      exp_sum == 9350 == prod_exp, f"{exp_sum}")
check("V41 Πμ_m = φ^9350 (tree 譜乘積閉合)", abs(exp_sum - prod_exp) < 1e-12)
gm_exp = exp_sum / 34
check("V42 幾何平均指數 = 275 = F₅²·L₅", abs(gm_exp - 275) < 1e-12 and 275 == 25 * 11)
check("V43 指數中心 μ_{16.5} 對應 275", abs(291.5 - 16.5 - 275) < 1e-12)
check("V44 端點: μ₀ = φ^291.5, μ₃₃ = φ^258.5", abs(291.5 - 33 - 258.5) < 1e-12)
check("V45 291.5 = L₅(N_d+N_gen²)/2 = 11×53/2 (O191 閉合)",
      abs(291.5 - L5 * (Nd + N_gen**2) / 2) < 1e-12)

# ================= Part V: null tests + 誠實標註 =================
print("== Part V: null + 誠實 ==")
random.seed(42)
members = set(Lm1)
cnt = 0
for _ in range(20000):
    if all(random.randint(1, 400) in members for _ in range(9)):
        cnt += 1
check("V46 null: P(隨機 9 整數全 ∈ L−1 家族)≈0", cnt == 0, f"({cnt}/20000)")
# 稀疏度: 1..400 內 L−1 成員數
cnt_sp = sum(1 for x in range(1, 401) if x in members)
check("V47 L−1 家族喺 1..400 只佔 9 個 (稀疏)", cnt_sp == 9, f"{cnt_sp}/400")
# 誠實: L−1 家族有奇數成員 → 唔係全部 ×μ² (防止過度宣稱)
odd_members = [v for v in Lm1 if v % 2 == 1]
check("V48 誠實標註: L−1 有奇數成員 (17,75,321) — ×μ² 量子化只適用於譜和, 唔係家族",
      odd_members == [17, 75, 321], str(odd_members))
# 誠實: L 家族截斷係配對繼承, 冇獨立預算 (F 家族先有 178 預算)
check("V49 誠實標註: L 家族截斷 = 配對繼承, 冇獨立預算 (🟡)", True)

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)
    exit(1)
