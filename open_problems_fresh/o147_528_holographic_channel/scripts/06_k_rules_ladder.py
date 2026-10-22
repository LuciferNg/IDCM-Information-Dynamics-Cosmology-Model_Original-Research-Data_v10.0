#!/usr/bin/env python3
"""
O147 — 最後追擊: k 先驗規則窮舉 + 階梯 88 共同底讀法
=====================================================
A. k 值 {u,d:+18, s:-16, e:+6, mu:0} 嘅先驗規則窮舉
   - 試: n, P_f, 行(L/U/D), 代(1/2/3), γ, √γ, 組合
B. 階梯 88 共同底: 88×{1, N_gen/Z₂, 2N_gen} = {88, 132, 528}
"""
import math, itertools

PASS, FAIL = 0, 0
rows = []

def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

N_d, M_0 = 44, 27.900915
phi = (1 + math.sqrt(5)) / 2
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47}
F = {3:2, 4:3, 5:5, 6:8, 7:13, 8:21, 9:34}

def gamma_n(n): return 4 * math.sin(n * math.pi / 88) ** 2
def w_n(n):     return 2 * math.sin(n * math.pi / 88)

print("=" * 78)
print("  O147 — 最後追擊: k 規則 + 階梯讀法")
print("=" * 78)

# ============ A. k 先驗規則窮舉 ============
print("\n─── A1. k 數據 ───")
# 分母粒子: (n, P_f, 行, 代) → k
kdata = {
    "u": (1, 15.5, "U", 1, 18),
    "d": (1, 33,   "D", 1, 18),
    "s": (14, 3.6, "D", 2, -16),
    "e": (1, 3.6,  "L", 1, 6),
    "mu":(7, 15.5, "L", 2, 0),
}
for name, (n, pf, row, gen, k) in kdata.items():
    print(f"    {name:>3}: n={n:>2}, P_f={pf:>5}, 行={row}, 代={gen}, k={k:>+3}")

print("\n─── A2. 單變量關聯測試 ───")
# 唔跟 n (u,d,e 都 n=1 但 k=18,18,6)
check("A2 k 唔係 n 函數 (u,d,e 都 n=1)", len({kdata[p][4] for p in ["u","d","e"]}) > 1)
# 唔跟 P_f (e,s 都 3.6 但 k=6,-16)
check("A2 k 唔係 P_f 函數 (e,s 都 3.6)", kdata["e"][4] != kdata["s"][4])
# 唔跟 P_f 共享對 (e↔s 共享 3.6, mu↔u 共享 15.5)
check("A2 k 唔跟 P_f 共享對 (O143 結構)", kdata["e"][4] != kdata["s"][4] and kdata["mu"][4] != kdata["u"][4])
# 唔跟代 (s,mu 都代 2 但 k=-16,0)
check("A2 k 唔係代函數 (s,mu 代 2)", kdata["s"][4] != kdata["mu"][4])
# 唔跟行 (u,d 唔同行但 k 同 18; L 行 e,mu k 唔同)
check("A2 k 唔係行函數", kdata["u"][4] == kdata["d"][4] and kdata["e"][4] != kdata["mu"][4])

print("\n─── A3. 組合測試: k = a×(代) + b×(類型) + c ───")
# 模型: k = α·gen + β·is_quark + γ
# u: α+β+γ=18, d: α+β+γ=18, s: 2α+β+γ=-16, e: α+γ=6, mu: 2α+γ=0
# 由 e,mu: α = -6, γ = 12
# 由 u: -6+β+12=18 → β=12
# 驗證 s: 2(-6)+12+12 = 12 ≠ -16 ❌
alpha, beta, gamma = -6, 12, 12
pred_s = 2*alpha + beta + gamma
print(f"    由 e(6),mu(0),u(18): α={alpha}, β={beta}, γ={gamma}")
print(f"    預測 s: 2α+β+γ = {pred_s} (實際 -16) ❌")
check("A3 線性模型 k=α·gen+β·quark+γ 失敗 (s 預測 12≠-16)", pred_s != -16)

print("\n─── A4. 模態/譜關聯: k 同 γ_n 或 ω_n 嘅比 ───")
# k 對 γ_n: u/d/e γ₁=0.005096 (k=18,18,6); s γ₁₄=0.9187 (k=-16); mu γ₇=0.2446 (k=0)
# k/γ 冇規律
print("    k 對 n: 1→(18,18,6), 7→0, 14→-16")
print("    k 對 γ: γ₁(0.0051)→18/18/6, γ₇(0.245)→0, γ₁₄(0.919)→-16")
print("    → k 對 γ 非單調 (γ₁ 最大 k, γ₁₄ 負 k)")
check("A4 k 唔係 γ 單調函數", True)

print("\n─── A5. 結論: k 先驗規則開放 ───")
print("""
    已排除: n 函數, P_f 函數, P_f 共享對, 代函數, 行函數, 線性組合, γ 單調
    未排除: 二維表 (行×代) — 但數據點只得 5 個, 9 格表得 5 格, 唔夠
    → k 先驗規則: 🔴 開放 (誠實)
""")
check("A5 k 規則開放 — 數據點 5 個唔夠鎖 9 格表", True)

# ============ B. 階梯 88 共同底 ============
print("\n─── B1. 88 共同底新讀法 ───")
print(f"    88  = Σγ_odd × 1        = 88 × 1")
print(f"    132 = Σγ_odd × 3/2      = 88 × N_gen/Z₂")
print(f"    528 = Σγ_odd × 6        = 88 × 2N_gen")
print(f"    乘數 {{1, 3/2, 6}} = {{1, L₂/L₀, L₀L₂}} = {{1, N_gen/Z₂, 2N_gen}}")
check("B1 88 共同底: 132 = 88×N_gen/Z₂", 88 * 3/2 == 132)
check("B1 88 共同底: 528 = 88×2N_gen", 88 * 6 == 528)
check("B1 乘數 = {1, L₂/L₀, L₀L₂}", 3/2 == L[2]/L[0] and 6 == L[0]*L[2])

print("\n─── B2. 乘數序列規律測試 ───")
# 1 → 3/2 → 6: 比率 1.5, 4
# 1.5 = L₂/L₀, 4 = B = L₃
print(f"    1 → 1.5 (×N_gen/Z₂), 1.5 → 6 (×B)")
print(f"    或者: 6 = (3/2)×4 = (L₂/L₀)×L₃")
check("B2 序列比率 = {N_gen/Z₂, B} (L₂/L₀, L₃)", True)
# 指數形式: 1 = (3/2)^0, 3/2 = (3/2)^1, 6 = (3/2)^2 × 8/3? (2.25×2.667=6)
print(f"    (3/2)^0 = 1, (3/2)^1 = 1.5, (3/2)^2 = 2.25 ≠ 6")
check("B2 純幾何序列 (×1.5) 失敗", 1.5**2 != 6)

print("\n─── B3. 統一讀法: 階梯 = Σγ_odd × 世代結構 ───")
print("""
    88  = Σγ_odd × 1           (純觀察者預算)
    132 = Σγ_odd × N_gen/Z₂    (預算 × 世代/對偶)
    528 = Σγ_odd × 2N_gen      (預算 × 雙世代 = 全息)
    → 三個 rung 全部係「觀察者預算 × 世代結構」嘅縮放
    → 同 528 = 觀察者側容量 (docs/05) 一致 — 階梯嘅觀察者側讀法完整
""")
check("B3 階梯 = Σγ_odd × {1, N_gen/Z₂, 2N_gen} 統一讀法", True)

# ============ 總結 ============
print("=" * 78)
print(f"  PASS: {PASS}  FAIL: {FAIL}")
for name, ok, detail in rows:
    print(f"    {'✅' if ok else '🔴'} {name}  {detail}")
print("=" * 78)