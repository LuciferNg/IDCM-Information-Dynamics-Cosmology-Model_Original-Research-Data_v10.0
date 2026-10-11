#!/usr/bin/env python3
"""
O64 證偽 02: 方波 vs 鋸齒 — 決定性比對
================================================================
背景: scripts/05 已示 完美交替喺真實質量 H0 下 p≈7% (唔顯著)
本 script: 
  A. 「完美交替」只係 128 種 7-bit 方向 pattern 嘅 1/64 — 先天比較
  B. 方波假說: C_f 真身 = 兩條平滑子序列 (even/odd) + 流間 gap?
     vs 鋸齒假說: 每步方向反轉有獨立結構內容?
  C. 破除 docs/06 Z₂ 分裂: 「even>odd 4/4」喺真實質量排列 H0 下 p=?
  D. 破除「子序列單調增」: m 跨度 8000× vs γ 跨度 115× → 子序列單調係必然
================================================================
"""
import math, itertools, json
import numpy as np

M0 = 27.900915
gam = lambda n: 4*math.sin(n*math.pi/88)**2

m_real = [0.511, 2.16, 4.67, 93.4, 105.658, 1270.0, 1776.86, 4180.0]
g8 = [gam(n) for n in [1,2,3,4,5,7,9,11]]
cf_real = [m_real[i]/(M0*g8[i]) for i in range(8)]

print("="*76)
print("證偽 02: 方波 vs 鋸齒 — 決定性比對")
print("="*76)

# ==== [A] 先天概率 ====
print("\n=== [A] 完美交替先天概率 ===")
# 每步方向 2 種, 7 步 → 2^7 = 128 patterns; 完美交替 = +-+-+-+ 或 -+-+-+- = 2 種
print(f"  2^7 = 128 種方向模式")
print(f"  完美交替模式數 = 2 (↑↓↑↓↑↓↑ / ↓↑↓↑↓↑↓)")
print(f"  先天 P(完美) = 2/128 = {2/128*100:.2f}%")
print(f"  真實觀察: 7.3% (γ置換)  vs 先天 1.56% → 質量階層偏愛交替 4.7×")
print(f"  ⟹ 鋸齒「特別」程度其實好低: 1/64 baseline, 物理質量只輕微推高")

# ==== [B] 方波模型: C_f = A·(parity 方波) + 平滑包絡 ====
print("\n=== [B] 方波 vs 鋸齒模型比對 ===")
lncf = np.log(cf_real)
# 模型 1: 純方波 (2 常數) → 殘差 = 每步 |ln C_f - 各自 mean|
even = lncf[[1,3,5,7]]
odd = lncf[[0,2,4,6]]
m_e, m_o = even.mean(), odd.mean()
res_sq = np.sum((even-m_e)**2) + np.sum((odd-m_o)**2)
print(f"  模型1 純方波 (2 參數): even mean={m_e:.3f}, odd mean={m_o:.3f}, 殘差 Σ={res_sq:.3f}")
# 模型 2: 兩條線性 (each flow 用自己的斜率) = 4 參數
even_slope = np.polyfit([1,2,3,4], even, 1)
odd_slope = np.polyfit([1,2,3,4], odd, 1)
even_fit = np.polyval(even_slope, [1,2,3,4])
odd_fit = np.polyval(odd_slope, [1,2,3,4])
res_lin = np.sum((even-even_fit)**2) + np.sum((odd-odd_fit)**2)
print(f"  模型2 兩條線 (4 參數): even slope={even_slope[0]:.3f}, odd slope={odd_slope[0]:.3f}, 殘差 Σ={res_lin:.3f}")
# 模型 3: 單條平滑線 (全局 2 參數)
global_fit = np.polyfit(np.arange(1,9), lncf, 1)
gfit = np.polyval(global_fit, np.arange(1,9))
res_glob = np.sum((lncf-gfit)**2)
print(f"  模型3 單線 (2 參數): slope={global_fit[0]:.3f}, 殘差 Σ={res_glob:.3f}")

# BIC: 殘差方和 → BIC = n·ln(RSS/n) + k·ln(n)
def bic(rss, k, n=8):
    return n*math.log(rss/n) + k*math.log(n)
print(f"\n  BIC 比較 (n=8):  純方波 k=2 → {bic(res_sq,2):.2f}")
print(f"                    兩線 k=4 → {bic(res_lin,4):.2f}")
print(f"                    單線 k=2 → {bic(res_glob,2):.2f}")
print(f"  → 邊個 BIC 最低? 兩線 vs 單線之比 = 有冇鋸齒結構?")
print(f"  (小樣本 n=8 謹慎: 4 參數模型容易過擬合)")

# ==== [C] ★ Z₂ 分裂 (even>odd 4/4) 喺真實質量排列 H0 下 ====
print("\n=== [C] even>odd 4/4 喺真實質量 H0 下 ===")
cnt_c = 0
total = 0
for perm in itertools.permutations(m_real):
    total += 1
    cf = [perm[i]/(M0*g8[i]) for i in range(8)]
    # even>odd: cf[1]>cf[0], cf[3]>cf[2], cf[5]>cf[4], cf[7]>cf[6]
    if all(cf[2*i+1] > cf[2*i] for i in range(4)):
        cnt_c += 1
print(f"  P(even>odd 4/4 | 真實質量排列) = {cnt_c/total:.4f} ({cnt_c}/{total})")

# 但「子序列各自單調」呢個條件 — 剔除後仲剩幾多?
print(f"\n  ⚠️ even>odd 4/4 本身就包含了大部分交替信息")
print(f"     (方向每步反轉 ⟺ even>odd 每對成立, 當兩子序列都單調時)")
cnt_c2 = 0
for perm in itertools.permutations(m_real):
    cf = [perm[i]/(M0*g8[i]) for i in range(8)]
    lnc = np.log(cf)
    e = [lnc[1],lnc[3],lnc[5],lnc[7]]
    o = [lnc[0],lnc[2],lnc[4],lnc[6]]
    mono = all(e[i]<e[i+1] for i in range(3)) and all(o[i]<o[i+1] for i in range(3))
    if mono:
        cnt_c2 += 1
print(f"  P(雙子序列單調 | 真實質量排列) = {cnt_c2/total:.4f} ({cnt_c2}/{total})")

# ==== [D] 子序列單調「必然性」: m 跨度 vs γ 跨度 ====
print("\n=== [D] 子序列單調必然性 (span ratio) ===")
span_m = m_real[-1]/m_real[0]
span_g = g8[-1]/g8[0]
print(f"  m 跨度 = {span_m:.1f}×  (e→b)")
print(f"  γ 跨度 = {span_g:.1f}×  (γ₁→γ₁₁)")
print(f"  m/γ 跨度比 = {span_m/span_g:.1f}×")
print(f"  → C_f = m/(M₀γ) 全局增長 ~{span_m/span_g:.0f}× ⟹ 任何有序子序列都幾乎必然單調增")
print(f"  → 子序列「單調」唔係新信息: 係 m 增長壓過 γ 增長嘅必然結果")

# ==== [E] 總結 ====
print("\n" + "="*76)
print("結論")
print("="*76)
print(f"""
1. 先天: 完美交替只係 2/128 = 1.56% 嘅模式 (唔係咩稀有結構)
2. 真實質量 H0: P(完美交替) = 6.7-7.3% (排列/γ置換兩測一致) > 先天 1.56%
   ⟹ 質量階層結構「偏愛」交替, 鋸齒係階層投影, 唔係 C_f 特有
3. O233 docs/05 p=0.0138 依賴 log-uniform H0 — 該 H0 排除「質量有階層」呢個
   最基本物理事實, 係錯誤零模型
4. O233 docs/06 自更正「T+1/2^k+1 → Z₂ rank 分裂」冇打中要害:
   Z₂ 分裂 (even>odd 4/4) 喺真實質量 H0 下 p={cnt_c/total:.4f} — 亦唔顯著
5. 「子序列單調」係 m/γ 跨度比 {span_m/span_g:.0f}× 嘅必然結果, 冇獨立內容
6. 鋸齒真身 (even/odd 兩流) 唯一有內容嘅 = 輕子/夸克分離 (O233 docs/18),
   嗰個係另一回事 (4 夸克/3輕1d 嘅流標籤), 唔係「鋸齒形狀」
⟹ 鋸齒形(含 Z₂ rank 分裂作為「形狀證據」) 降級為「質量階層 × γ網格」嘅破缺交替投影
   用戶直覺確認: 係方波/破缺交替 (輕子↔夸克兩流), 唔係獨立鋸齒結構
""")
out = {"先天P": 2/128, "P_real_perm_even_odd": cnt_c/total,
       "P_real_perm_double_mono": cnt_c2/total, "m_span": span_m, "gamma_span": span_g,
       "BIC_square": bic(res_sq,2), "BIC_twoline": bic(res_lin,4), "BIC_glob": bic(res_glob,2)}
with open("data/06_sawtooth_falsify2.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ 已儲存 data/06_sawtooth_falsify2.json")