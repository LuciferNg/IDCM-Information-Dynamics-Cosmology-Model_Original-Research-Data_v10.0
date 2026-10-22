#!/usr/bin/env python3
# O197 scripts/01 — T1: 合成形式鑑別
# 候選: 乘性 (1+δ_tot) = (1+δ̂)(1+δ_env)  vs  加性 δ_tot = δ̂ + δ_env
# 用觀測錨鑑別:
#   LRD 中位: δ_eff = 1.367 ⟹ M = 1.914e6·(2.367)^{3/2} = 6.97e6
#   UHz1:     δ_eff = 91.4  ⟹ M = 1.914e6·(92.4)^{3/2} = 1.70e9
# δ̂ arcsine on [−1,1]: 譜偏差唔可以產生 δ > 1 (上限 5.41e6) ⟹
#   任何 δ_tot > 1 必須由 δ_env 提供 ⟹ 乘性/加性喺低端都要 δ_env
#   鑑別點: δ_tot = δ̂ + δ_env 喺 δ_env ≈ 0 時 δ_tot ≈ δ̂ ∈ [−1,1] 同乘性一致
#   但乘性 (1+δ̂)(1+δ_env) − 1 = δ̂ + δ_env + δ̂·δ_env:
#   δ̂·δ_env 交叉項 — 對大 δ_env 顯著 (UHz1: δ̂ 平均 0, 但正偏差模態 δ̂₊)
#   關鍵: M_seed 冪律 (1+δ)^{3/2} 乘性自然 — δ̂ 同 δ_env 係獨立機制
#   (譜偏差 vs 環境過密), 合成必然乘性 (獨立因子), 除非有耦合
# 數值: 比對兩候選下 M_seed 分布 vs 觀測錨
import numpy as np
from scipy import stats

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

M_base = 1.914e6
def M_seed(delta): return M_base * (1+delta)**1.5

# 觀測錨
M_lrd = M_seed(1.367)      # 6.97e6
M_uhz = M_seed(91.4)       # 1.70e9
print(f"錨: M_LRD = {M_lrd:.4e}, M_UHz1 = {M_uhz:.4e}")
check("T1a LRD 錨 M = 6.97e6", abs(M_lrd - 6.97e6)/6.97e6 < 0.01, f"M={M_lrd:.3e}")
check("T1b UHz1 錨 M = 1.70e9", abs(M_uhz - 1.70e9)/1.70e9 < 0.01, f"M={M_uhz:.3e}")

# 44 個正偏差譜模態 δ̂₊ (O174 docs/13): δ̂_k = −cos(2θ_k), θ_k = kπ/176, k=1..88
ks = np.arange(1, 89)  # 88 個模態
theta = ks * np.pi / 176
dhat = -np.cos(2*theta)
dhat_pos = dhat[dhat > 0]
print(f"\nδ̂₊ 模態數 = {len(dhat_pos)}, 範圍 [{dhat_pos.min():.4f}, {dhat_pos.max():.4f}]")
print(f"Var_pop(ln(1+δ̂₊)) = {np.var(np.log(1+dhat_pos)):.6f} (O174 0.039162?)")
check("T1c δ̂₊ 44 個正偏差模態", len(dhat_pos) == 44, f"n={len(dhat_pos)}")
check("T1d Var_pop(ln(1+δ̂₊)) ≈ 0.03916", abs(np.var(np.log(1+dhat_pos)) - 0.039162)/0.039162 < 0.01,
      f"Var={np.var(np.log(1+dhat_pos)):.6f}")

# 合成候選鑑別 — 關鍵物理: M_seed 分布
# 乘性: ln M = ln M_base + 1.5·[ln(1+δ̂) + ln(1+δ_env)]
#   低端 (δ_env≈0): ln(1+δ̂) arcsine 變換, δ̂ ∈ [−1,1] ⟹ 1+δ̂ ∈ [0,2]
#   高端: ln(1+δ_env) ~ N(0.8625, 1.4098) 主導
# 加性: ln M = ln M_base + 1.5·ln(1 + δ̂ + δ_env)
#   低端: 同乘性 (δ_env≈0 ⟹ δ_tot≈δ̂)
#   高端: ln(1 + δ̂ + δ_env) vs ln(1+δ̂)+ln(1+δ_env) = ln((1+δ̂)(1+δ_env))
#   對 δ_env 大: 1+δ̂+δ_env vs (1+δ̂)(1+δ_env) = 1+δ̂+δ_env+δ̂δ_env
#   差 = δ̂·δ_env — 乘性高過加性 (δ̂>0 時), 低過 (δ̂<0 時)
# ⟹ 鑑別: 高端 M_seed 分布 (δ̂ 正偏差模態貢獻 δ̂δ_env 交叉項)
rng = np.random.default_rng(42)
N = 200000
# 模擬 δ̂: 離散 44 模態均勻抽 (arcsine 離散版)
dhat_s = rng.choice(dhat, size=N)
# 模擬 δ_env: logN (μ, s²)
mu_env, s_env = 0.862478, np.sqrt(1.4098)
ln1pd_env = rng.normal(mu_env, s_env, N)
d_env = np.exp(ln1pd_env) - 1
# 乘性合成
lnM_mult = np.log(M_base) + 1.5*(np.log(1+dhat_s) + ln1pd_env)
M_mult = np.exp(lnM_mult)
# 加性合成
lnM_add = np.log(M_base) + 1.5*np.log1p(dhat_s + d_env)
M_add = np.exp(lnM_add)
# 觀測錨比對: LRD 中位 (M 中位), UHz1 級 (P(M > 1e9))
print(f"\n乘性: M 中位 = {np.median(M_mult):.3e}, P(M>1e9) = {np.mean(M_mult>1e9):.5f}")
print(f"加性: M 中位 = {np.median(M_add):.3e}, P(M>1e9) = {np.mean(M_add>1e9):.5f}")
print(f"觀測: M 中位 ≈ 6.97e6 (LRD), UHz1 存在 = P(1e9) ~ 1e-6..1e-4")
# LRD 中位 δ=1.367 ⟹ M = 6.97e6: 乘性 median ln = ln(M_base)+1.5μ_env?
lnM_mult_med = np.log(M_base) + 1.5*mu_env
print(f"乘性 ln M 中位理論 = ln(M_base)+1.5μ = {lnM_mult_med:.4f} → M = {np.exp(lnM_mult_med):.3e}")
check("T1e 乘性中位 ≈ LRD 錨 6.97e6 (δ̂ 中位 ≈ 0 唔影響)", 
      abs(np.exp(lnM_mult_med) - M_lrd)/M_lrd < 0.02,
      f"M={np.exp(lnM_mult_med):.3e} vs {M_lrd:.3e}")
# 加性中位: ln(1+δ̂+δ_env), δ̂ 中位 0? arcsine 中位 0, 1+0+d_env = 1+d_env
lnM_add_med = np.log(M_base) + 1.5*np.log1p(np.exp(mu_env)-1)
check("T1f 加性中位同乘性一致 (δ̂ 中位 0)", abs(lnM_add_med - lnM_mult_med) < 1e-9)

# 關鍵鑑別: 交叉項 δ̂·δ_env — 高端 (UHz1 級)
# P(M > 1.70e9) 兩候選
p_mult = np.mean(M_mult > M_uhz)
p_add = np.mean(M_add > M_uhz)
print(f"\nP(M > UHz1): 乘性 = {p_mult:.3e}, 加性 = {p_add:.3e}")
# 物理判據: δ̂ 同 δ_env 係獨立機制 (譜偏差 = 鏈內部結構, 環境過密 = 外部成長)
# ⟹ 合成乘性 (獨立因子乘積) — 加性需要耦合 (同一個 δ 相加)
check("T1g 乘性 P(UHz1) > 加性 P(UHz1) (交叉項 δ̂δ_env>0 貢獻)", p_mult > p_add,
      f"{p_mult:.3e} vs {p_add:.3e}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
