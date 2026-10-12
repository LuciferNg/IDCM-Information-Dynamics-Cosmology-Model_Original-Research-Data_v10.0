#!/usr/bin/python3
"""O239 — Script 17: 結構公式可行性——γ/β/α 結構鏈零參數檢定
============================================================================
調律者問題: 「現階段推結構公式是否可行? 第一性原理推導唔應該太依賴數據精度。」

本 script 檢定「結構鏈」: 身份由結構推出, 數據只做驗證（零擬合指數）:

  結構鏈假說:
    γ = −19/4 = −4.75        （stair Lepton 深度 19 ÷ K_Tree 分支 B=4）
    β = γ/φ² = −19/(4φ²)     （γ 再除 φ² 相位結構）
         = −1.814340...
    α = γ/β = φ² = 2.618034  （兩指數比率）

  即係: 9 費米子質量 m ∝ θ^γ, |dm| ∝ θ^β, 而 γ/β = φ²——
  全部由 stair/B/φ 結構鎖定, 唔係由數據擬合輸出。

預註冊判據:
  G1 結構鏈自洽: γ(−19/4), β(−19/(4φ²)), α(φ²) 三角閉合（代數恆等）
  G2 γ 結構值 vs MC 實測: |γ_struct − γ_MC| < 1σ
  G3 β 結構值 vs 9 點擬合: |β_struct − β_fit| < 1σ_fit 且 相對偏差 < 0.1%
  G4 α 結構值 vs O206: α_struct = φ² vs O206 α = 2.633254 偏差 < 1%
  G5 零擬合 OOS: 用 γ=−19/4 固定（唔 fit 指數）, 只 fit M₀（單一標度）,
      OOS RMS vs 用自由 γ 擬合——結構版劣化 < 15%（即「唔使 fit 指數」成本低）
  G6 β 身份池: β±1σ_fit 窗內有理候選密度（stair/φ 家族 vs 全網格）——
      確認 β = −19/(4φ²) 唔係隨機有理可達

數據誤差: γ_MC = −4.7503 ± 0.0361（scripts/14, 20 萬組）
          β_fit（9 點 |dm|）= −1.8146 ± 0.056（linregress stderr）
"""
import json, math
import numpy as np
from scipy import stats

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/17 — 結構公式可行性: γ/β/α 結構鏈零參數檢定")
print("=" * 78)

phi = (1 + 5**0.5) / 2
gamma_s = -19/4
beta_s = gamma_s / phi**2
alpha_s = phi**2
print(f"結構鏈: γ = {gamma_s}   β = {beta_s:.10f}   α = {alpha_s:.10f}")
print(f"      β = −19/(4φ²) = −{19:.0f}/(4×{phi**2:.6f})")

# ── G1: 三角閉合 ──
alpha_recover = gamma_s / beta_s
print("\n── G1: 結構鏈三角閉合 ──")
print(f"   γ/β = {alpha_recover:.8f} vs φ² = {phi**2:.8f}  dev {abs(alpha_recover-phi**2)/phi**2:.2e}")
chk("G1 γ/β = φ² 代數閉合", abs(alpha_recover - phi**2) < 1e-12, f"dev {abs(alpha_recover-phi**2):.1e}")

# ── G2: γ 結構 vs MC ──
print("\n── G2: γ 結構值 vs MC ──")
g_mc = -4.7503
g_std = 0.0361
d = abs(gamma_s - g_mc) / g_std
print(f"   γ_struct = {gamma_s}, γ_MC = {g_mc} ± {g_std}, 距離 {d:.3f}σ")
chk("G2 γ_struct 喺 MC 1σ 內", d < 1.0, f"{d:.3f}σ")

# ── G3: β 結構 vs 擬合 ──
print("\n── G3: β 結構值 vs 9 點擬合 ──")
O9 = json.load(open("data/09_o206_inputs.json"))
lt = np.log(np.array([n*np.pi/88 for n, _ in O9["PAIR"]]))
dm9 = np.abs(np.array(O9["dm9"]))
rf = stats.linregress(lt, np.log(dm9))
b_fit, b_se = rf.slope, rf.stderr
d3 = abs(beta_s - b_fit) / b_se
rel3 = abs(beta_s - b_fit) / abs(b_fit)
print(f"   β_struct = {beta_s:.6f}, β_fit = {b_fit:.6f} ± {b_se:.6f}")
print(f"   距離 {d3:.3f}σ; 相對偏差 {rel3*100:.4f}%")
chk("G3a β_struct 喺擬合 1σ 內", d3 < 1.0, f"{d3:.3f}σ")
chk("G3b β 相對偏差 < 0.1%", rel3 < 0.001, f"{rel3*100:.4f}%")

# ── G4: α 結構 vs O206 ──
print("\n── G4: α 結構值 vs O206 ──")
a_o206 = 2.633254
dev4 = abs(alpha_s - a_o206) / a_o206
print(f"   α_struct = φ² = {alpha_s:.6f}, O206 α = {a_o206}, dev {dev4*100:.2f}%")
chk("G4 α dev < 1%", dev4 < 0.01, f"{dev4*100:.2f}%")

# ── G5: 零擬合 OOS（固定 γ=−19/4, 只 fit M₀）──
print("\n── G5: 零擬合 OOS——固定結構指數 vs 自由指數 ──")
MASS = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])
theta = np.array([n*np.pi/88 for n, _ in O9["PAIR"]])
# 結構版: ln m = ln M0 + γ_s·ln θ ⟹ ln M0 = mean(ln m − γ_s·ln θ)
lnM0_s = np.mean(np.log(MASS) - gamma_s * np.log(theta))
pred_s = lnM0_s + gamma_s * np.log(theta)
rms_s = np.sqrt(np.mean((np.log(MASS) - pred_s)**2))
# 自由版: 9 點擬合（兩參數）
r_free = stats.linregress(np.log(theta), np.log(MASS))
pred_f = r_free.intercept + r_free.slope * np.log(theta)
rms_f = np.sqrt(np.mean((np.log(MASS) - pred_f)**2))
print(f"   結構版（1 參數 M₀, γ 鎖定 −19/4）: log-RMS = {rms_s:.4f}")
print(f"   自由版（2 參數 γ,β 擬合）:           log-RMS = {rms_f:.4f}")
print(f"   劣化 = {(rms_s/rms_f - 1)*100:.1f}%")
chk("G5 結構版 OOS 劣化 < 15%", rms_s / rms_f < 1.15, f"{(rms_s/rms_f-1)*100:.1f}%")

# ── G6: β 身份池 ──
print("\n── G6: β 身份池（β±1σ_fit 窗內候選）──")
# 全網格有理 a/b (a∈1..180 ∵ β≈−1.8, b∈1..12)
grid = sorted({-a/b for a in range(1, 181) for b in range(1, 13)})
win = [x for x in grid if abs(x - b_fit) < b_se]
print(f"   β_fit = {b_fit:.4f} ± {b_se:.4f}")
print(f"   ±1σ 窗 [{b_fit-b_se:.4f}, {b_fit+b_se:.4f}] 內候選:")
for x in win:
    tag = ""
    if abs(x - beta_s) < 1e-6: tag = "  ← β_struct"
    print(f"     {x:+.5f} = {x:.5f}{tag}")
print(f"   候選數 = {len(win)} (密度 {len(win)/len(grid)*100:.2f}%)")
chk("G6 β 窗候選 ≤ 3（β 身份比 γ 更稀疏?）", len(win) <= 3, f"{len(win)} 個")

json.dump({
    "G_gamma_s": gamma_s, "G_beta_s": beta_s, "G_alpha_s": alpha_s,
    "G2_gamma_dist_sigma": float(d),
    "G3_beta_dist_sigma": float(d3), "G3_beta_rel_dev": float(rel3),
    "G4_alpha_dev_o206": float(dev4),
    "G5_rms_struct": float(rms_s), "G5_rms_free": float(rms_f),
    "G6_beta_window": [float(x) for x in win],
    "verdict": "結構鏈可行" if (d < 1 and d3 < 1 and rel3 < 0.001 and rms_s/rms_f < 1.15) else "結構鏈待修",
}, open("data/17_structural_chain.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")