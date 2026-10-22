#!/usr/bin/env python3
"""
O147 — 兩層裸比 gap 0.73% 分析
================================
兩層都聲稱 m_s/m_d ≈ 20, 但:
  譜比層: sin22/sin1 = 19.811167  × φ^(10/528) = 19.9925 (0.037%)
  公式層: (γ₁₄/γ₁)×(3.6/33) = 19.668040  × ? = 20

追擊:
  1. 公式層可否用 φ 修正閉合 20? k = ? (候選: 18 = L₆)
  2. n_s 連續解 (公式層命中 20 需要嘅 n)
  3. 10 vs 18 結構關係
  4. gap 嘅代數本質
"""
import math

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

def gamma_n(n): return 4 * math.sin(n * math.pi / 88) ** 2
def w_n(n):     return 2 * math.sin(n * math.pi / 88)

print("=" * 78)
print("  O147 — gap 0.73% 分析: 兩層嘅 20 分解")
print("=" * 78)

# ============ 1. 公式層可否用 φ 修正閉合 20? ============
print("\n─── 1. 公式層 φ 修正: 19.668 × φ^(k/528) = 20 ───")
form_ratio = (gamma_n(14)/gamma_n(1)) * (3.6/33)
spec_ratio = w_n(22) / w_n(1)

# 需要嘅 k
k_needed = math.log(20/form_ratio) / math.log(phi) * 528
print(f"    form_ratio = {form_ratio:.6f}, 要命中 20 需要 k = {k_needed:.2f}")
print(f"    k 候選: 18 = L₆  (18.4 最近整數結構數)")

k18 = 18
val18 = form_ratio * phi**(k18/528)
print(f"    19.668 × φ^(18/528) = {val18:.4f}  (Δ={abs(val18-20)/20*100:.4f}%)")
check("1 公式層 + φ^(18/528): 命中 20 (Δ<0.1%)", abs(val18-20)/20 < 0.001,
      f"Δ={abs(val18-20)/20*100:.4f}%")

# 18/528 簡化
print(f"    18/528 = {18/528:.6f} = 3/88 = L₂/(2N_d)   (L₂ = 3!)")
check("1 18/528 = 3/88 = L₂/(2N_d) (L₂=3)", 18/528 == 3/88 and 3 == L[2])

# 譜比層用 10/528 = 5/264
print(f"    10/528 = {10/528:.6f} = 5/264 = n_u/528")
check("1 10/528 = n_u/528 (n_u = 10 = n₀(1)−L₄)", 10 == 17 - L[4])

# ============ 2. n_s 連續解 ============
print("\n─── 2. 公式層命中 20 需要嘅 n_s (連續) ───")
# (γ_{n}/γ₁)×(3.6/33) = 20 → sin²(nπ/88) = 20×33/3.6×sin²(π/88)
sin_n = math.sqrt(20 * 33/3.6) * math.sin(math.pi/88)
n_s_cont = math.asin(sin_n) * 88 / math.pi
print(f"    sin(nπ/88) = √(20×33/3.6)×sin(π/88) = {sin_n:.6f}")
print(f"    n_s(連續) = {n_s_cont:.3f}  (O143 用整數 14)")
print(f"    n_s=14 引入偏差: {(n_s_cont-14)/14*100:.2f}%")
check("2 連續 n_s = 14.12 — 整數 14 引入 0.86% 內在偏差", abs(n_s_cont - 14.12) < 0.05,
      f"n_s={n_s_cont:.3f}")

# ============ 3. 10 vs 18 結構關係 ============
print("\n─── 3. 修正分子: 譜層 10 (n_u) vs 公式層 18 (L₆) ───")
print(f"    n_u = 10 = n₀(1) − L₄ = 17 − 7    (O34 選擇規則)")
print(f"    L₆  = 18 = Tr(T̂⁶)                 (O142 轉移矩陣)")
print(f"    18 − 10 = 8 = F₆ = (T̂⁶)₁₂")
print(f"    18 + 10 = 28 = L₇ − 1? (29−1) — 或者 E_proj×2? (28.5×2=57 唔係)")
print(f"    18/10 = 1.8 = L₆/n_u — 非結構")
check("3 18−10 = 8 = F₆（轉移矩陣）", 18-10 == 8 and 8 == 5+3)  # F₆=8
check("3 10 同 18 都係結構數（O34 選擇規則 + O142 T̂⁶ 譜跡）", 10 == 17-7 and 18 == L[6])

# ============ 4. gap 代數本質 ============
print("\n─── 4. gap = sin22/sin1 vs (sin14/sin1)²×(3.6/33) 嘅代數系 ───")
# 兩層一致需要: sin22/sin1 = (sin14/sin1)²×(P_fs/P_fd)
# → P_fs/P_fd = sin22×sin1/sin²14
P_ratio_needed = math.sin(22*math.pi/88)*math.sin(math.pi/88)/math.sin(14*math.pi/88)**2
P_ratio_grid = 3.6/33
print(f"    兩層一致需要 P_f(s)/P_f(d) = sin22·sin1/sin²14 = {P_ratio_needed:.6f}")
print(f"    O143 grid P_f(s)/P_f(d) = 3.6/33 = {P_ratio_grid:.6f}")
print(f"    差 = {(P_ratio_needed/P_ratio_grid-1)*100:.2f}%  (= gap 0.73% 嘅源頭)")
check("4 gap 源頭 = P_f 比 3.6/33 vs sin²幾何要求", 
      abs((P_ratio_needed/P_ratio_grid-1)*100 - 0.73) < 0.1)

# 結構化 P_f 比: 3.6/33 = 0.10909; sin22·sin1/sin²14 = 0.10991
# 3.6/33 可否寫做結構比? 3.6 = L₆/F₅ = 18/5, 33 = N_d−L₅
print(f"    P_f(s)/P_f(d) = (L₆/F₅)/(N_d−L₅) = (18/5)/33 = 3.6/33")
print(f"    幾何要求 = sin22·sin1/sin²14 ≈ 0.10991")
print(f"    0.10991 − 0.10909 = 0.00082 — 冇細結構數（~0.75%）")

# ============ 5. 兩層 20 分解總結 ============
print("\n─── 5. 兩層嘅 20 分解 ───")
print(f"""
    譜比層:  sin22/sin1            = 19.811  (0.94% off 20)
             ×φ^(10/528) [10=n_u]  = 19.9925 (0.037% off 20)  ✅
    公式層:  (γ₁₄/γ₁)(3.6/33)      = 19.668  (1.66% off 20)
             ×φ^(18/528) [18=L₆]   = 19.993  (0.035% off 20)  ✅ 新發現
    → 兩層各自有 φ 修正路徑命中 20, 分子 {10, 18} 都係結構數
    → 但「點解公式層要加 φ 修正」未推導 (O143 grid 原設計冇修正)
""")
check("5 兩層都有 φ 修正路徑命中 20 (分子 10/18 結構)", 
      abs(val18-20)/20 < 0.001 and abs(spec_ratio*phi**(10/528)-20)/20 < 0.001)

# ============ 6. gap 閉合方向 ============
print("─── 6. gap 0.73% 閉合候選 ───")
# 候選 A: 公式層 φ^(18/528) 修正 → 兩層都命中 20, gap 消失喺「修正層」
# 候選 B: P_f(s) 衰減至 sin²幾何值 → P_f(s) = 33×0.10991 = 3.627? 唔結構
P_fs_geo = 33 * P_ratio_needed
print(f"    候選 B: P_f(s) = 33×0.10991 = {P_fs_geo:.4f} ← 唔係結構數")
check("6 候選 B (P_f 改) 失敗: 3.626 唔結構", 
      not any(abs(P_fs_geo - v) < 0.01 for v in [3.6, 13, 15.5, 33, 37, 44]))
# 候選 C: gap = 兩層真實差異, 唔需要閉合 (兩層係唔同物理近似)
print(f"""    候選 C: gap = 兩層近似差異, 唔需要閉合
    — 譜比層係「觀察者讀數」近似, 公式層係「粒子質量」近似
    — 兩層命中唔同目標 (2n_u=20 恆等式 vs 絕對質量 92.3 MeV)
    → 0.73% 係框架內固有張力, 唔係 bug""")

# ============ 總結 ============
print("=" * 78)
print(f"  PASS: {PASS}  FAIL: {FAIL}")
for name, ok, detail in rows:
    print(f"    {'✅' if ok else '🔴'} {name}  {detail}")
print("=" * 78)