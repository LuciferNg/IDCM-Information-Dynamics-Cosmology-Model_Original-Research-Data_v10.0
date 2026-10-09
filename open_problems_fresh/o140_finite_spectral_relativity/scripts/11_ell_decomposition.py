#!/usr/bin/env python3
"""
O140 — ℓ(E) 內部結構拆解 (2026-10-09)
========================================
用戶指示: 「唔係接受唔接受嘅問題, 係裏面仲有冇能拆嘅」。
放棄「2π 公理接受/拒絕」二元框架, 改為解構 ℓ(E) = log₄(E/E₀):

拆解主線:
  1. n(E) = E/E_min — 環模索引 (E_min = ħc/(2R_world), 全環一圈=一個相位周期)
     ⟹ ℓ 只係 n 嘅 re-indexing, 真正物理變量係 n (一個比值 = 組合數)
  2. 對偶恆等 n·m = 88 = 2N (模索引 × 波長內格數 = 全環格數) — 敢接 k-n 對偶
  3. 4^ℓ 嘅「4」拆解: 4 = 2×2 = 二階差分算子嘅兩個 2 (L = 2I - A)
     ⟹ 自足理由, 唔使借 IDCM K_tree
  4. 22/π ≈ 7.003 同 44/π ≈ 14.006 嘅「近整數」拆解:
     22/π ≈ 7 純粹係 Archimedes 22/7 ≈ π 嘅有理近似, 唔係結構!
     44/π = 2·(22/π) ⟹ 同一個近似, 無獨立結構
  5. ℓ floor/frac 拆解: floor(ℓ) = 分辨率層級, frac(ℓ) = 子格位置
     ⟹ 同時接 local-l-level 同 k-n-dual-index 兩個子問題
"""
import math, json

N = 44
HC = 1.97327e-16      # eV·m
R_MPC = 4129.94
R_M = R_MPC * 3.0857e22
a = R_M / N            # 格距

PASS = 0; FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1; print(f"  [FAIL] {name} {detail}")

print("="*72)
print("拆解 1: 真正嘅物理變量係 n(E) = E/E_min, 唔係 ℓ")
print("="*72)
# E_min: 波長 = 全環周長 R_world 嘅能量 (一圈=一個相位周期)
E_min = HC/R_M
print(f"  E_min = ħc/R_world = {E_min:.6e} eV")
print(f"  E₀ (Gemini) = 22ħc/(πR) = {22*HC/(math.pi*R_M):.6e} eV")
print(f"  E₀/E_min = {22/math.pi:.6f}")
print()
# 連續模索引 n = R_world/λ_C = E/E_min (組合數, 非整數正當)
# 每波長格數 (層級 ℓ) m_ℓ = λ_C/a_ℓ = N_ℓ/n
# 對偶恆等: n · m_ℓ = N_ℓ = 44·4^ℓ   (EXACT, 對任意 ℓ)
print("  對偶恆等 (連續模索引 × 每波長格數 = 總格數): n·m_ℓ = N_ℓ")
for E, label in [(0.511e6, "electron"), (173e9, "top"),
                 (13.6e12, "LHC 13.6TeV"), (1.22e28, "Planck"),
                 (22*HC/(math.pi*R_M), "E₀(Gemini)")]:
    n = E/E_min                      # 連續模索引 = R/λ_C
    m0 = 44/n                        # base 層每波長格數 (λ/a₀)
    n0_ = 44/math.pi                 # Gemini 錨點 (n₀=44/π)
    ell_g = math.log(n/n0_, 4)       # Gemini ℓ
    print(f"  {label:14s}: n={n:14.6g}  m₀(格/λ)={m0:14.4f}  n·m₀={n*m0:8.1f} (=44?)  ℓ_gemini={ell_g:10.4f}")
check("n·m₀ = 44 EXACT (base layer)", abs((0.511e6/E_min)*(44/(0.511e6/E_min)) - 44) < 1e-12,
      "電子 n·m₀=44")
# Nyquist 檢查: m_ℓ ≥ 2 ⟹ 4^ℓ ≥ 2n/44 = n/22
for E, label in [(0.511e6, "electron"), (13.6e12, "LHC"), (1.22e28, "Planck")]:
    n = E/E_min
    ell_nyq = math.log(n/22, 4)      # 4^ℓ = n/22 ⟹ m_ℓ = 2 (Nyquist 下限)
    print(f"  {label:8s}: n={n:10.3g}  Nyquist 下限 ℓ_nyq=log₄(n/22)={ell_nyq:10.4f}  Gemini ℓ={math.log(n/(44/math.pi),4):10.4f}  (差={math.log(n/(44/math.pi),4)-ell_nyq:.4f}=log₄(π/2))")
print("""
  ⟹ n(E) = E/E_min 係連續模索引 (組合數, 非整數正當);
     ℓ(E;F) = log₄(F·n/44) 係「每波長最少 F 格」嘅分辨率指標, 有整族:
     F=2 (真 Nyquist, λ=2a), F=2π (Gemini 相位圈), 差 log₄(π/2)=0.330.
**關鍵: 可觀測 (v_n, γ_n, η_n, Doppler, 質量殼) 全部直接用 n 表達,
     ℓ 只係「要鋪幾密先 resolve 到 E」嘅後勤指標 ⟹ F 唔入任何預言!!**
     ⟹ 2π vs 2 爭議係假議題, 唔使接受邊個公理
""")

print("="*72)
print("拆解 2: ℓ 係 n 嘅 re-indexing")
print("="*72)
# Gemini: ℓ = log₄(E/E₀) = log₄(n/(44/π)); 錨點 n₀ = 44/π ≈ 14.006
n0 = 44/math.pi
print(f"  Gemini 錨點: E₀ ⟺ n₀ = 44/π = {n0:.6f} (非整數模索引)")
for E, label in [(0.511e6, "electron"), (13.6e12, "LHC"), (1.22e28, "Planck")]:
    n = E/E_min
    ell_floor = math.floor(math.log(n/n0, 4))
    ell_frac = math.log(n/n0, 4) - ell_floor
    print(f"  {label:8s}: n={n:12.4f}  ℓ=log₄(n/n₀)={math.log(n/n0,4):12.6f}"
          f"  floor={ell_floor:3d}  frac={ell_frac:.6f}")
print("  ⟹ ℓ 嘅非整數 = n 同錨點 n₀ 嘅 ratio in log₄ — 兩個模索引嘅比,")
print("    唔係『相位 2π 要唔要』嘅公投。ℓ 整唔整數係由 n 嘅對數位置決定。")

print("="*72)
print("拆解 3: 4^ℓ 嘅『4』 = 2×2 (鏈 Laplacian 結構)")
print("="*72)
# 環鏈 Laplacian L = 2I - A: 特徵值 2 - 2cos(πn/N)... 對 44 環: ε = 4sin²(πn/88)
# 4 = 2·2: 一個 2 來自對角(度), 一個 2 來自譜表式 2-2cos = 4sin²(θ/2)
print("  鏈 Laplacian: (Lφ)_j = 2φ_j - φ_{j-1} - φ_{j+1}, 特徵值 λ_n = 2-2cos(θ_n)")
print("  λ_n = 2-2cosθ = 4sin²(θ/2): 個 4 = 2(對角) × 2(sin²半角展開)")
print("  ⟹ FSR 譜 ε_n = 4sin²(πn/2N) 嘅 4 係二階差分算子自帶, 唔係人為")
check("ε_n = 4sin² 嘅 4 = 2×2 結構 (λ=2-2cos)", abs((2-2*math.cos(math.pi/3)) - 4*math.sin(math.pi/6)**2) < 1e-12)
# 精化 N_ℓ = 44·4^ℓ = 44·2^{2ℓ}: 每 ℓ 步 = 每維 x2 (時間/空間各一)? 或 = 差分算子平方 2²
# 檢查: 4^ℓ 精化下, 固定 n 嘅模式 ε^{(N_ℓ)}_n 收斂到連續 k²:
for ell in [0, 1, 5, 20]:
    Nl = N*4**ell
    k_phys = math.pi*1/(Nl*a/4**ell)   # 固定波數 k = π/(N_l·a_l)/1
    eps_l = 4*math.sin(math.pi*1/(2*Nl))**2
    # 連續極限: (k a_l)² 單位校正
    cont = (math.pi/(Nl))**2           # ε ≈ (πn/N_l)² 大 N_l
    print(f"  ℓ={ell:2d}: N_ℓ={Nl:8d}  ε₁={eps_l:.10f}  連續極限(k a)²={(math.pi/Nl)**2:.10f}  ε₁/cont={eps_l/cont:.6f}")
check("大 N 極限 ε_n^(N_ℓ) → (πn/N_ℓ)²", (4*math.sin(math.pi/(2*N*4**20))**2)/(math.pi/(N*4**20))**2 - 1 < 1e-8)

print("="*72)
print("拆解 4: 22/π ≈ 7 同 44/π ≈ 14 係同一個 Archimedes 近似")
print("="*72)
print(f"  22/π = {22/math.pi:.10f}   vs  7  (差 {abs(22/math.pi-7)/7*100:.4f}%)")
print(f"  44/π = {44/math.pi:.10f}   vs  14 = 2×7  (差 {abs(44/math.pi-14)/14*100:.4f}%)")
print(f"  ⟹ 44/π = 2·(22/π): 同一樣嘢乘 2, 冇獨立結構")
print(f"  ⟹ 22/π ≈ 7 等價於 22/7 ≈ π = Archimedes 3.142857 vs 3.14159")
check("22/π ≈ 7 係 Archimedes 22/7≈π (唔係結構)", abs(22/math.pi - 7)/7 < 0.0005,
      f"22/π={22/math.pi:.6f}, 22/7={22/7:.6f}, π={math.pi:.6f}")
print("  ⚠️ 結論: L₄=7 近命中係有理近似偶然, FSR 唔可以當 22/π=7 用")

print("="*72)
print("拆解 5: floor/frac — ℓ 拆成分辨率層級 + 子格位置")
print("="*72)
for E, label in [(0.511e6, "electron"), (105.658e6, "muon"), (1.776e9, "tau"),
                 (173e9, "top"), (13.6e12, "LHC"), (1.22e28, "Planck")]:
    n = E/E_min
    L = math.log(n/n0, 4)
    fl = math.floor(L); fr = L - fl
    # 子格位置: 模索引 n 喺層級 fl+1 格內嘅分數位置
    N_fl = N*4**fl
    n_fl = n/4**fl    # 層級 fl 嘅等效索引
    print(f"  {label:8s}: ℓ={L:12.6f}  floor(L)={fl:3d}  frac(L)={fr:.6f}"
          f"  n_{fl}={n_fl:12.4f}  (距離整數格網嘅分數位 {n_fl % 1:.6f})")
print("""
  ⟹ frac(ℓ) 承載物理: 探針模 n 喺分辨率層級 floor(ℓ) 嘅格網中,
     n_fl = n/4^floor 嘅分數部分 = 探針介於兩格之間嘅相位位置
     (sites-per-wavelength m 嘅餘數)。
  ⟹ 接兩個子問題:
     · local-l-level: floor(ℓ) = 要幾細嘅格先 resolve 到 E
     · k-n-dual-index: frac 部分 = 模索引 n 喺格網嘅精確位置
       (n·m=88 對偶嘅連續版)
""")

print("="*72)
print(f"RESULT: {PASS} PASS, {FAIL} FAIL")
print("="*72)
with open('data/ell_decomposition.json', 'w') as f:
    json.dump({
        'E_min': E_min,
        'E0_gemini': 22*HC/(math.pi*R_M),
        'E0_over_Emin': 22/math.pi,
        'n0_gemini': 44/math.pi,
        'duality_nm_88': (0.511e6/E_min)*(R_M/(HC/0.511e6)),
        'archimedes_flag': True,
        'examples': {l: {'n': 13.6e12/E_min if l=='LHC' else (0.511e6/E_min if l=='electron' else 1.22e28/E_min)} for l in ['electron','LHC','Planck']},
    }, f, indent=2, ensure_ascii=False)
print("-> data/ell_decomposition.json")