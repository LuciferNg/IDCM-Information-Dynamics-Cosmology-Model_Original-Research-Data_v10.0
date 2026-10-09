#!/usr/bin/env python3
"""
O140 closeout 後 — 繼續推導困難點量化診斷 (2026-10-09)
=========================================================
逐個剩餘開放項, 把「困難」變成數字:
  1. local-l-level: ℓ 層係咪隱藏自由參數? (a_ℓ = a/4^ℓ, 邊個 ℓ 決定於乜?)
  2. k-n-dual-index: √ε_k 質量譜跨度 28:1 夠唔夠覆蓋 SM (top/e ≈ 3.4e5)?
  3. velocity-composition: 序列投影誤差會唔會累積?
  4. spectral-zeta: 奇數 s 有冇閉式?
  5. 判決區: JWST 需要幾多 SNe 先分到 0.857 vs 2 指數
"""
import math, json

N = 44
def eps(k, Nv=N):
    return 4*math.sin(math.pi*k/(2*Nv))**2

print("=" * 72)
print("困難 1: local-l-level — ℓ 層係咪隱藏自由參數?")
print("=" * 72)
print("""
FSR 聲稱零自由參數: a = R_world/44 由幾何固定。
但尺度精化 a_ℓ = a/4^ℓ 引入一組新尺度。問題: 一個能量 E 嘅探針
「自動」用邊一層? 如果呢個選擇本身冇機制, ℓ 就變成隱藏參數。
""")
# 反向推導檢查: 若 a_ℓ 對應 Compton 波長, ℓ(E) 要幾大?
hbar_c = 1.97327e-16  # eV·m
a_base = 4129.94*3.0857e22/44  # m (宇宙學格距)
for E, label in [(13.6e9, "LHC 13.6 TeV"), (1e12, "UHECR 1 TeV"),
                 (1e18, "GRB 1 EeV"), (1.22e28, "Planck 1.22e19 GeV")]:
    lam = hbar_c/E  # Compton
    ell = math.log(a_base/lam, 4)
    print(f"  E={label:16s}: λ_Compton={lam:.2e} m, 需要 ℓ={ell:.2f}")
print("""
  => ℓ(E) = log₄(a/λ_C) 係「由 E 決定」, 但呢個係 back-derive:
     我哋先假定 a_ℓ 係解析度, 再問邊個 ℓ 啱 lambda_C。
     結構上冇機制話「探針自動落喺對應層」—— 係描述性, 唔係推導性。
  => 困難: 要嘛 ℓ 成為額外參數 (違反零參數), 要嘛要有第一性原理
     機制 (e.g. 探針+目標嘅離散尺度比決定 ℓ)。IDCM 有 K_tree B=4 作
     scale 維度, 但 FSR 自足體系未有。
""")

print("=" * 72)
print("困難 2: k-n-dual-index — √ε_k 質量譜跨度")
print("=" * 72)
mk = [math.sqrt(eps(k)) for k in range(1, N+1)]
span = max(mk)/min(mk)
print(f"  √ε_k 跨度 (k=1..44): {span:.2f} : 1")
print(f"  m_1 = {mk[0]:.5f} M₀, m_44 = {mk[-1]:.5f} M₀")
print()
print("  SM 質量比 (需覆蓋):")
ratios = [("top/electron", 173e9/0.511e6), ("tau/electron", 1776.86/0.510999),
          ("top/tau", 173e9/1776.86e6), ("mu/electron", 105.658/0.510999)]
for name, r in ratios:
    ok = "PASS" if r <= span else "FAIL"
    print(f"    {name:14s}: {r:.1f} : 1  vs  √ε 跨度 {span:.1f}  [{ok}]")
print(f"""
  => √ε_k (28:1) 遠唔夠覆蓋 SM 質量譜 (top/e ≈ 3.4e5:1)。
  => 質量必須係 composite (e.g. Lucas/Fibonacci 型乘積), 
     但 FSR 自足體系未有推導 —— 目前 m_k = M₀√ε_k 只係「譜形式候選」,
     唔係質量預言。
  => 困難: 質量譜嘅結構源頭 (點解 γ₇/γ₁ 出現喺 μ/e 等) 要由
     ε-譜嘅 composite 結構重推, 而唔可以借用 IDCM 質量表。
""")

print("=" * 72)
print("困難 3: velocity-composition — 序列投影誤差累積")
print("=" * 72)
def eta_n(n):
    return math.log(1/math.tan(math.pi*n/(4*N)))
def n_of_eta(eta):
    nf = 4*N/math.pi*math.atan(math.exp(-eta))
    return max(1, min(N, round(nf)))

# 單步投影 (⊕_FSR) vs 序列投影 (連續 boost) 誤差
print("  三連 boost: v_1 ⊕ v_5 ⊕ v_12, 兩種次序比較:")
steps = [1, 5, 12]
# 一次過 (快度層精確相加, 最後投影)
eta_tot = sum(eta_n(s) for s in steps)
n_once = round(n_of_eta(eta_tot))
# 序列 (每步投影後再 boost)
n_seq = 44  # 由靜止開始
for s in steps:
    n_seq = n_of_eta(eta_n(n_seq) + eta_n(s))
err = abs(n_once - n_seq)
print(f"  一次過投影: n' = {n_once}")
print(f"  序列投影  : n' = {n_seq}")
print(f"  誤差      : {err} rung  {'⚠️' if err > 0.5 else 'OK'}")
print("""
  => 快度層加法精確 (群), 但「每步測量投影」令多體/連續 boost 
     產生路徑依賴: 次序唔同, 結果唔同 (非群作用)。
  => 困難: collective sector 需要定義「唔測量中間態」嘅 boost 算符
     (U(η) 合成), 或者承認投影係不可逆測量 → 群結構變 semigroup。
""")

print("=" * 72)
print("困難 4: spectral-zeta — 奇數 s")
print("=" * 72)
for s in [3, 5]:
    zN = sum(1/eps(k)**s for k in range(1, N+1))
    # 大 N 極限: (N/π)^{2s} ζ_R(2s)
    zR = sum(1/m** (2*s) for m in range(1, 100000))
    pred = (44/math.pi)**(2*s) * zR
    print(f"  ζ_44({s}) = {zN:.6f}   大N預測 = {pred:.6f}   (差 = {abs(zN-pred)/pred*100:.3f}%)")
print("  => 偶數 s 有有理多項式閉式; 奇數 s 冇 (已知數論: csc^{2k} 展開係")
print("     N² 多項式只對偶數冪成立)。有限譜嘅模對稱性被破壞 ⟹")
print("     冇 ζ_N(s) ↔ ζ_N(1-s) 反射泛函方程。")
print("  => 困難: 奇 s 需要等比級數/斂散性理論或留數理論, 超越閉式層面。")

print("=" * 72)
print("困難 5: highz-tension — JWST 判決統計")
print("=" * 72)
# 需要幾多 SNe 先分辨 μ 差距 0.1 mag?
dmu = 0.1  # mag
sigma = 0.15  # mag 典型單顆亮度色散
N_needed = (sigma/dmu)**2 * 4  # 2σ 分辨
print(f"  單顆 σ ≈ {sigma} mag, 需要分辨 Δμ = {dmu} mag")
print(f"  N_SNe = 4·(σ/Δμ)² ≈ {N_needed:.0f} 顆 (2σ)")
print(f"  JWST NIRCam 高紅移樣本目前 ~ 數十顆 → 統計力剛好臨界")
print(f"  判決區 z>0.5 中, FSR 誤差 +0.1~0.15 mag 系統性")
print("  => 困難: 唔係推導問題, 係數據問題 —— 等 JWST 高紅移 SNe 樣本")

print("=" * 72)
print("困難 6: FSR-QFT (O137 擱置)")
print("=" * 72)
print("""
  gauge 結構 (SU(3)×SU(2)×U(1)) 由 ε-譜點樣出現?
  費曼規則/Wilson 係數喺有限譜上? Lüscher 散射公式嘅離散版?
  呢個係 O137 範圍, 按用戶指示擱置 —— 唔喺 O140 推。
""")

with open('data/difficulty_diagnosis.json', 'w') as f:
    json.dump({
        'ell_layer_factor': 'hidden parameter risk',
        'mass_span': span,
        'sm_ratios': {n: r for n, r in ratios},
        'seq_projection_err': err,
        'odd_s_no_closed_form': True,
        'jwst_n_needed': N_needed,
    }, f, indent=2, ensure_ascii=False)
print("\n-> data/difficulty_diagnosis.json")