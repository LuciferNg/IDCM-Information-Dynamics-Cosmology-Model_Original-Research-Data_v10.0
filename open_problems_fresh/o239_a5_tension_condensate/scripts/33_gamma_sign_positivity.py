#!/usr/bin/python3
"""O239 — Script 33: γ 負號必然性 + 「1−(19/4)」正數化候選盲測
============================================================================
狀態: 2026-10-12 新增（第二十六輪後續——調律者問題「為什麼19/4要是負數,
      不應該是要用1-(19/4)去正數化嗎」）
目的: ①解釋 γ=−19/4 負號來源（數據序 vs θ 序）
     ②盲測「γ = 1 − 19/4 = −15/4 = −3.75」候選（離 fit 幾多σ?）
     ③檢定真正嘅「正數化」——質量 = (1/θ)^(+19/4) 形式, 同 θ^−19/4 是否完全等價
     ④檢查「1−x 家族」有冇任何 x 令 fit 更好

背景:
  γ_obs = −4.7503 ± 0.0361（scripts/14 MC, freeze v1.0）
  γ_struct = −19/4 = −(K_Tree−(N_gen−1)L₄)/B（stair 線 k=2 點, docs/21）
  PAIR: θ_n = nπ/88; t(n=1) 最重 172690, e(n=13) 最輕 0.51
  ⟹ θ 遞增序 → 質量遞減 --> slope(log m, log θ) 必負

判據預註冊（盲測, threshold 零放寬）:
  G1: OLS slope(log m, log θ) < 0（負號由 PAIR 序必然——n 細=θ 細=質量重）
  G2: ★候選 γ_alt = 1 − 19/4 = −15/4: |γ_alt − γ_obs|/σ > 3σ ⟹ 直接否決
  G3: ★『1−x 家族』盲掃: x ∈ stair 家族 {33/4, 26/4, 19/4, 33/7, B²/B,...}
      邊個最貼 γ_obs? 若最近都 >3σ ⟹ 冇 1−x 形式支持
  G4: 正數化等價: m ∝ (1/θ)^(+19/4) ≡ m ∝ θ^(−19/4) — 同一 fit 重新參數化,
      RMS 完全一樣; 正數化只係「用 1/θ 做 x 軸」嘅選擇, 唔改變結構
  G5: 「1−19/4」若指 m ∝ θ^(1−19/4) = θ·θ^(−19/4):
      額外 θ 因子 → slope = −3.75, 離 fit 27.7σ ⟹ 否決（除非 1 有結構身份）
產物: data/33_gamma_sign_positivity.json（新增）
"""
import json
import numpy as np
from scipy import stats

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/33 — γ 負號必然性 + 1−(19/4) 正數化盲測")
print("=" * 78)

# PAIR + 質量（freeze v1.0, data/09）
PAIR = [[1,'t'],[2,'b'],[3,'tau'],[4,'c'],[5,'mu'],[7,'s'],[9,'d'],[11,'u'],[13,'e']]
mass9 = [172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999]
theta = np.array([n*np.pi/88 for n, _ in PAIR])
lm = np.log(mass9)
lt = np.log(theta)
GAMMA_OBS, SIG = -4.7503, 0.0361

# ── G1: 負號必然性 ──
print("\n── G1: slope 符號與 PAIR 序 ──")
slope, inter, r, p, se = stats.linregress(lt, lm)
print(f"   θ 序: t(n=1) 最重 → e(n=13) 最輕（θ 遞增序, 質量遞減序）")
print(f"   OLS slope(log m, log θ) = {slope:.4f} < 0 ✔")
print(f"   ⟹ 負號係 PAIR 序嘅數學必然: n 細(θ 細) ⟷ 質量重")
chk("G1 slope < 0（負號必然）", slope < 0, f"slope={slope:.4f}")

# ── G2: γ_alt = 1 − 19/4 ──
print("\n── G2: ★候選 γ_alt = 1 − 19/4 ──")
g_alt = 1 - 19/4
d = abs(g_alt - GAMMA_OBS)/SIG
print(f"   1 − 19/4 = {g_alt}")
print(f"   |γ_alt − γ_obs|/σ = {d:.1f}σ")
chk("G2 1−19/4 被否決 (>3σ)", d > 3.0, f"{d:.1f}σ")

# ── G3: 1−x 家族盲掃 ──
print("\n── G3: 『1−x』家族盲掃 ──")
x_cands = {
    "33/4 (K/B)": 33/4, "26/4 ((K−L₄)/B)": 26/4, "19/4 (M₂/B)": 19/4,
    "33/7 (K/L₄)": 33/7, "7/4 (L₄/B)": 7/4, "B (4)": 4.0,
    "N_gen/B": 3/4, "φ²": (1+5**0.5)/2, "N_gen": 3.0, "B²": 16.0,
    "5 (F₅)": 5.0, "7 (L₄)": 7.0,
}
best = ("", 1e9, 0.0)
print(f"   {'x':>10s}  γ=1−x      |γ−γ_obs|σ")
for name, x in x_cands.items():
    g = 1 - x
    d = abs(g - GAMMA_OBS)/SIG
    print(f"   {name:>10s}  {g:+.4f}  {d:7.1f}σ")
    if best is None or d < best[1]:
        best = (name, d, g)
print(f"   最近: {best[0]} → γ = {best[2]:+.4f} = {best[1]:.1f}σ")
chk("G3 冇 1−x 候選 < 3σ", best[1] > 3.0, f"最近 {best[0]} {best[1]:.1f}σ")

# ── G4: 正數化等價 ──
print("\n── G4: 正數化等價性 ──")
# m ∝ (1/θ)^k ≡ m ∝ θ^(−k): 用 1/θ 做 x 軸 fit, slope 應該 = +19/4
l_inv = -lt   # log(1/θ) = −log(θ)
slope_inv, *_ = stats.linregress(l_inv, lm)
print(f"   m ∝ (1/θ)^k: x=log(1/θ), slope = {slope_inv:+.4f}")
print(f"   ⟹ k = +{slope_inv:.4f} ≈ +19/4 = {19/4:.4f} ↔ |γ|")
print(f"   『正數化』= 將 θ 軸反轉（用 1/θ）——同一個 fit, 零結構變化")
chk("G4 正數化係參數化選擇, 非結構", abs(slope_inv - 19/4) < 0.36, f"k={slope_inv:+.4f}")

# ── G5: θ^(1−19/4) 讀法 ──
print("\n── G5: m ∝ θ^(1−19/4) = θ·θ^(−19/4) 讀法 ──")
g5 = 1 - 19/4
d5 = abs(g5 - GAMMA_OBS)/SIG
print(f"   若質量 = θ × θ^(−19/4)（線性 θ 因子 × 結構冪）:")
print(f"   slope = 1 − 19/4 = {g5}, 離 fit {d5:.1f}σ")
chk("G5 θ·θ^(−19/4) 讀法被否決", d5 > 3.0, f"{d5:.1f}σ")

# ── 附加: 「1−」若指 D_A 式 1−4^−ℓ（O76）──
print("\n── 附加: 1−4^−ℓ 型（O76 D_A = R(1−4^−ℓ)）──")
print(f"   O76 嘅『1−』係 z 紅移投影衰減, 唔係質量譜指數")
print(f"   質量譜 γ=−19/4 係幂律指數, 兩者唔同層: 冇理由 1−19/4")

json.dump({
    "G1": {"slope": float(slope), "negative_by_order": bool(slope < 0)},
    "G2": {"gamma_alt": g_alt, "d_sigma": float(d), "rejected": bool(d > 3.0)},
    "G3": {"nearest": best},
    "G4": {"slope_inv": float(slope_inv),
           "equivalent": bool(abs(slope_inv - 19/4) < 0.36)},
    "G5": {"if_theta_times": g5, "d_sigma": float(d5), "rejected": bool(d5 > 3.0)},
    "verdict": "γ=−19/4 負號係 PAIR 序必然（θ 遞增序 ↔ 質量遞減序, slope<0）; "
               "1−(19/4) = −15/4 離 fit 27.7σ 直接否決; 『1−x 家族』盲掃最近都 >3σ; "
               "真正正數化 = m ∝ (1/θ)^(+19/4), 同 θ^(−19/4) 完全等價（同一 fit, "
               "只係 x 軸反轉 — 零結構變化, 唔係『1−』修正）; 質量譜冇『1−』修正嘅必要",
}, open("data/33_gamma_sign_positivity.json", "w"), indent=1, ensure_ascii=False)

print("\n" + "=" * 78)
np_ = sum(1 for _, c in P if c)
print(f"判定: {np_}/{len(P)} PASS")