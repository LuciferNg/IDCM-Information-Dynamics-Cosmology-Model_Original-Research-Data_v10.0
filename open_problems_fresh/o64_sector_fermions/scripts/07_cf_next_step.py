#!/usr/bin/env python3
"""
C_f 下一步方向 — 單線模型殘差診斷 + 質量比層面結構掃描
================================================================
背景:
  O233: C_f 生成器 5 線負閉合 (冇算子身份)
  docs/08: 鋸齒形證偽; BIC 單線模型最佳 (ln C_f ≈ 0.714·rank + c)
本 script:
  1. 單線模型殘差 → 有冇 mod-4 槽 / Z₂ / 代塊 結構?
  2. 質量比層面 (唔經 M₀): C_f 比 × γ 比 = 質量比, 邊啲閉合?
  3. 斜率 0.714 嘅身份掃描 (只 called out, 唔 fit)
  4. 邊一步偏差最大 → 集中攻擊點
================================================================
"""
import math, json
import numpy as np

M0 = 27.900915
gam = lambda n: 4*math.sin(n*math.pi/88)**2
A5modes = [1,2,3,4,5,7,9,11]
m_real = [0.511, 2.16, 4.67, 93.4, 105.658, 1270.0, 1776.86, 4180.0]
g8 = [gam(n) for n in A5modes]
cf = [m_real[i]/(M0*g8[i]) for i in range(8)]
lncf = np.log(cf)

print("="*76)
print("C_f 下一步方向診斷")
print("="*76)

# ==== [1] 單線模型 + 殘差 ====
print("\n=== [1] 單線模型 ln C_f = a·rank + b → 殘差 ===")
rank = np.arange(1, 9, dtype=float)
a, b = np.polyfit(rank, lncf, 1)
fit = a*rank + b
resid = lncf - fit
print(f"  斜率 a = {a:.6f}  (≈ {a:.4f})")
print(f"  截距 b = {b:.6f}")
print(f"  exp(a) = {math.exp(a):.4f}  (每步 ×e^a)")
print(f"  R² = {1 - np.sum(resid**2)/np.sum((lncf-np.mean(lncf))**2):.4f}")
print(f"\n  rank  ln C_f     fit      殘差")
for i in range(8):
    print(f"  {i+1}    {lncf[i]:.4f}  {fit[i]:.4f}  {resid[i]:+.4f}")

# ==== [2] 殘差結構掃描 ====
print("\n=== [2] 殘差結構: Z₂ / mod-4 槽 / 代塊 ===")
even_r = resid[[1,3,5,7]]
odd_r = resid[[0,2,4,6]]
print(f"  even ranks 殘差: {[f'{x:+.3f}' for x in even_r]}  mean={even_r.mean():+.3f}")
print(f"  odd  ranks 殘差: {[f'{x:+.3f}' for x in odd_r]}  mean={odd_r.mean():+.3f}")
# 兩流分離 — 殘差層面仲有冇?
print(f"  even-odd 殘差差: {even_r.mean()-odd_r.mean():+.4f}  (≠0 = 兩流殘差層面仍分離)")
# mod-4: n=1,5 ≡1 (lepton 槽); n=2,3,4,7,9,11 其他
mod1_idx = [0,4]    # n=1,5
modnot_idx = [1,2,3,5,6,7]
print(f"  lepton 槽 (n≡1 mod 4) 殘差: {[f'{resid[i]:+.3f}' for i in mod1_idx]}")
print(f"  其他殘差: {[f'{resid[i]:+.3f}' for i in modnot_idx]}")

# 代塊
print(f"\n  gen1 殘差 (e,u,d): {[f'{resid[i]:+.3f}' for i in [0,1,2]]}")
print(f"  gen2 殘差 (s,mu,c): {[f'{resid[i]:+.3f}' for i in [3,4,5]]}")
print(f"  gen3 殘差 (tau,b): {[f'{resid[i]:+.3f}' for i in [6,7]]}")

# ==== [3] 質量比層面 (唔經 M₀) ====
print("\n=== [3] 質量比 × γ比 × C_f比 → 純幾何結構 ===")
# 質量比 m_j/m_i = (γ_j/γ_i)·(C_j/C_i) — M₀ 冇影
print(f"  {'比':>8s} {'m 比':>10s} {'γ 比':>10s} {'C_f 比':>10s} {'γ比×C比':>10s} {'自洽':>6s}")
pairs = [
    ('mu/e', 4, 0), ('tau/mu', 6, 4), ('c/s', 5, 3),
    ('b/c', 7, 5), ('s/d', 3, 2), ('d/u', 2, 1),
    ('c/u', 5, 1), ('t?', 7, 0),
]
for label, hi, lo in pairs:
    mr = m_real[hi]/m_real[lo]
    gr = g8[hi]/g8[lo]
    cr = cf[hi]/cf[lo]
    check = gr*cr
    print(f"  {label:>8s} {mr:>10.4f} {gr:>10.4f} {cr:>10.4f} {check:>10.4f} {'OK' if abs(mr-check)<1e-9 else 'BUG'}")

# 邊啲質量比近 IDCM 結構數?
print(f"\n  質量比近結構數 (標準數集 ±2%):")
fib = [1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597,2584]
luc = [2,1,3,4,7,11,18,29,47,76,123,199,322,521]
sq = [4,9,16,25,36,49,64,81,100,121,144,169]
for label, hi, lo in pairs:
    mr = m_real[hi]/m_real[lo]
    for sname, sset in [('Fib',fib),('Luc',luc),('Sqr',sq)]:
        for s in sset:
            if abs(mr-s)/s < 0.02:
                print(f"    {label} = {mr:.3f} ≈ {sname} {s} (dev {abs(mr-s)/s*100:.2f}%)")

# ==== [4] 斜率身份掃描 (純報告, 唔 fit) ====
print("\n=== [4] 斜率 a=%f 身份候選 (報告層, 結構常數 ±0.5%%):" % a)
struct_consts = {
    'φ': 1.618034, 'φ²': 2.618034, '1/φ': 0.618034, '√2': 1.414214,
    '√3': 1.732051, '√5': 2.236068, '√6': 2.449490, '√12': 3.464102,
    'ln2': 0.693147, 'lnφ': 0.481212, 'π/4': 0.785398, 'e/π': 0.865256,
    'γ_Euler': 0.577216, '1/γ_E': 1.732455, '3/4': 0.75, '5/7': 0.714286,
    '7/10': 0.7, '2/φ³': 0.472136, '1/√e': 0.606531, 'π/√19': 0.720730,
    'L₇/11': 72/11/10*10,  # 唔啱 syntax, 下面改用
}
# 特別候選
struct_consts['5/7'] = 5/7
struct_consts['L₇/12'] = 8/12
struct_consts['√(5/9)'] = math.sqrt(5/9)
struct_consts['1/√2 + 1/5'] = 1/math.sqrt(2) + 0.2
struct_consts['F₅/F₆'] = 5/8
struct_consts['L₄/L₅'] = 7/11
hits = []
for name, v in struct_consts.items():
    if abs(a - v)/v < 0.005:
        hits.append((name, v, abs(a-v)/v*100))
for name, v, dev in hits:
    print(f"    ✅ {name} = {v:.6f}  dev {dev:.3f}%")
if not hits:
    print(f"    冇結構候選 (±0.5%) — 斜率可能只係 log-space 平均增長率, 冇獨立身份")

# 斜率嘅幾何意義: e^a 每步倍率 = ?
print(f"\n  e^a = {math.exp(a):.6f} → C_f 每步 ×{math.exp(a):.3f}")
print(f"  7 步總增 = {math.exp(7*a):.1f}×  (接近 m/γ 跨度比 71×)")

# ==== [5] 偏差集中攻擊點 ====
print("\n=== [5] 偏差集中點 (混標度修正後最大缺口) ===")
print(f"  用 O234 freeze v2 統一 scheme (scripts/02):")
print(f"    c/s 需 11.652, O120 C_f 給 13.597 → dev 16.7% (混標度殘留)")
print(f"    b/c 需 4.586, O120 C_f 給 3.291  → dev 28.2% (混標度殘留)")
print(f"  → 修正方案: C_c, C_b 改用統一 scheme 目標; 受影響: c, b, τ(?), t")
print(f"  → 修正後再睇單線模型係咪仍然成立")

# ==== [6] 方向矩陣 ====
print("\n=== [6] 下一步方向矩陣 ===")
print("""
方向 A: 單線斜率追源 (a=0.7143)
   A1. 佢係咪 5/7 = 0.714286?? dev %.4f%% 
       5/7 = F5/L4 — IDCM 結構數有理比
   A2. 盲測: 用 γ 譜 + 質量階層生成 mock, 睇斜率由邊個機制主導
   A3. 若斜率 = F5/L4: C_f ≈ C0·(F5/L4)^rank 係「有理比幾何級數」
       → 質量比 m_j/m_i = (L4/F5)^{j-i}·(γj/γi) 零參數可預言

方向 B: 質量比層面 (唔經 M0)
   B1. 10 個質量比全部列出 → 睇近結構數 (§3 上半已掃)
   B2. 修正 c/b 混標度後重新核對
   B3. 目標: m_j/m_i = 純幾何比 (γ比 × 結構比), 完全唔使 C_f

方向 C: 接受 C_f = 定義 → 去 O209 質量層
   C1. C_f 冇算子身份已負閉合 — 唔好再打
   C2. O209 |Δm|^α RMS 0.5872 係真正質量層出路
   C3. O64 只保留「質量比閉合」做交付

方向 D: 槽結構 (mod-4) 殘餘
   D1. lepton 槽 n≡1 mod 4 喺單線殘差層面仲分唔分? 
       (§2: %s vs %s)
       若分離乾淨 → 槽 = 第二個結構軸 (唔靠 C_f 形狀)
""" % (abs(a-5/7)/(5/7)*100,
       [f'{resid[i]:+.2f}' for i in mod1_idx],
       [f'{resid[i]:+.2f}' for i in modnot_idx]))

out = {"slope": a, "intercept": b, "exp_slope": math.exp(a),
       "residuals": resid.tolist(), "r2": float(1-np.sum(resid**2)/np.sum((lncf-np.mean(lncf))**2)),
       "slope_candidates": {n: v for n, v, d in hits}}
with open("data/07_cf_next_step.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ 已儲存 data/07_cf_next_step.json")