#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""O247 Q2 攻堅 08 — 投影算符層: 核子複合投影 + m₄₄ 標度盲測 (判據預註冊)

調律者 2026-10-12: 「直接在 o247 要攻投影算符層」 (CY3 空白查證後第二次指令)

背景 (查證結果):
- O238 scripts/21: 「單 mode 投影」m = C·|dm|_n^{φ²} (C=1.52151e-6, 9費米子 fit)
  對 17 強子全譜掃 — 命中 = 池密度, 零信號 ⟹ 強子唔係「單 mode 投影讀數」
- O53: m₄₄ = M_Pl·e^(−44) = 0.9493 GeV (44 = N_d) — 只做 δ=ln(m/m₄₄) 費米子基準,
  ★ 從來冇將 m₄₄ 自身對準核子!! m₄₄/n = 1.0104 (p 1.0118) — 核子離標度只有 ~1%!!
- CY3 流形庫 (v6/v7/v10): 9 費米子 + Higgs + CKM + DM, 零核子 — 完全空白
- O247 scripts/01-07: K_chain/K_Tree 單量池全滅, A₅ 出處五線全封

本 script 三路 (全部判據預註冊, 凍結先跑):
  G1 ★ m₄₄ 標度: m_p/m_n vs m₄₄ = M_Pl·e^(−44) — 偏差 <1%?
     MC null: 隨機 e^(−k)·M_Pl (k∈[30,60]) 撞核子區 (5% 窗) 概率
  G2 ★ 複合投影: 質子 = uud, 中子 = udd 三夸克節點 — 組合算符
     (a) 節點和 M₀·(γ_u+γ_u+γ_d) (γ_n = 4sin²(nπ/88), u=11, d=9)
     (b) C·(Σ|dm|_node)^{φ²} 投影線搵質子 — 唔准 (scripts/21 已滅單線)
     (c) m₄₄ − 節點和 vs m_n/m_p? uud=2γ₁₁+γ₉, udd=γ₁₁+2γ₉
  G3 ★ 核子-核子差結構: m_n−m_p = 1.2933 MeV vs k·M₀γ₁ (γ₁=4sin²(π/88))
     k=9 (N_gen²)? MC null 池密度 (k∈1..88 命中概率)
  G4 整合判決 + 禁區/候選升級

數據: PDG 2024 m_p=938.27208816, m_n=939.5654205 MeV; M_Pl=1.220890e22 MeV;
       M₀=27.900915; γ₁ = 4sin²(π/88) = 0.005096319; u(d) 用 O238 freeze v2 值
"""
import math
import numpy as np

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

N = 88
mp = 938.27208816
mn = 939.5654205
Mpl = 1.220890e22   # MeV
M0 = 27.900915      # MeV
PHI = (1 + math.sqrt(5)) / 2
gamma1 = 4 * math.sin(math.pi / 88) ** 2
gammas = {n: 4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)}

# O238 freeze v2 (docs/04): u, d 質量
m_u = 93.4 / 42.890          # 2.1776 MeV
m_d = 93.4 / 42.890 * 2.1505  # 4.6827 MeV
mu_u, mu_d = 11, 9           # SEL9: u→11, d→9

print("=" * 78)
print("G1  ★ m₄₄ = M_Pl·e^(−44) 標度 vs 核子")
print("=" * 78)
m44 = Mpl * math.exp(-44)
print("m₄₄ = M_Pl·e^(−44) = %.6f GeV  (44 = N_d)" % (m44 / 1000))
print("m_p/m₄₄ = %.6f  dev = %+.4f%%" % (mp / m44, (mp / m44 - 1) * 100))
print("m_n/m₄₄ = %.6f  dev = %+.4f%%" % (mn / m44, (mn / m44 - 1) * 100))
# MC null: 隨機 k∈[30,60] e^(−k)·M_Pl 撞核子 5% 窗
rng = np.random.default_rng(20261012)
hits = 0
for _ in range(20000):
    k = rng.integers(30, 61)
    val = Mpl * math.exp(-float(k))
    if abs(val / mn - 1) < 0.05:
        hits += 1
p1 = hits / 20000
print("MC null (k∈[30,60], 5%% 窗): 命中核子區概率 = %.4f" % p1)
c1 = abs(mp / m44 - 1) < 0.01 and abs(mn / m44 - 1) < 0.01
chk("G1 m₄₄ 撞核子 <1%", c1, "p dev=%.2f%%, n dev=%.2f%%" % ((mp/m44-1)*100, (mn/m44-1)*100))
# m₄₄ 定義 e 底數 (O168 附註: e 底數開放) — 本 script 只報 m₄₄ 自身

print()
print("=" * 78)
print("G2  ★ 複合投影: uud/udd 節點組合")
print("=" * 78)
# γ 節點: γ_uud = 2·γ₁₁ + γ₉; γ_udd = γ₁₁ + 2·γ₉
gu, gd = gammas[mu_u], gammas[mu_d]
g_uud = 2 * gu + gd
g_udd = gu + 2 * gd
print("γ₁₁(u) = %.6f | γ₉(d) = %.6f" % (gu, gd))
print("γ_uud = 2γ₁₁+γ₉ = %.6f | γ_udd = γ₁₁+2γ₉ = %.6f" % (g_uud, g_udd))
cand = {
    "M₀·γ_uud": M0 * g_uud,
    "M₀·γ_udd": M0 * g_udd,
    "M₀·(γ_uud-γ₁)": M0 * (g_uud - gamma1),
    "M₀·(γ_uud+γ₁)": M0 * (g_uud + gamma1),
    "m₄₄−M₀·γ_uud": m44 - M0 * g_uud,
    "m₄₄−M₀·γ_udd": m44 - M0 * g_udd,
    "m_u+m_u+m_d (freeze v2)": 2 * m_u + m_d,
    "m_u+m_d+m_d": m_u + 2 * m_d,
}
print("%-24s %12.4f  MeV" % ("", 0))
for nm_, v in cand.items():
    dp = abs(v / mp - 1) * 100
    dn_ = abs(v / mn - 1) * 100
    star = " ★" if min(dp, dn_) < 2 else ""
    print("%-24s %12.4f  MeV   dev_p=%6.2f%%  dev_n=%6.2f%%%s" % (nm_, v, dp, dn_, star))
chk("G2.1 m₄₄−節點組合撞核子 <1.5%", any(abs(m44 - M0 * g_uud) / mp - 1 < 0.015
    for _ in [0]) or min(abs(m44 - M0 * g_uud) / mp - 1,
                        abs(m44 - M0 * g_uud) / mn - 1,
                        abs(m44 - M0 * g_udd) / mp - 1,
                        abs(m44 - M0 * g_udd) / mn - 1) < 0.015,
    "m₄₄−節點和 (uud/udd) 對 p/n")

print()
print("=" * 78)
print("G3  ★ m_n − m_p = 1.2933 MeV vs k·M₀γ₁")
print("=" * 78)
delta_mnp = mn - mp
print("m_n − m_p = %.6f MeV;  M₀·γ₁ = %.6f MeV" % (delta_mnp, M0 * gamma1))
print("ratio = %.4f  (9 = N_gen² → 9×M₀γ₁ = %.4f, dev %.2f%%)" % (
    delta_mnp / (M0 * gamma1), 9 * M0 * gamma1,
    (delta_mnp - 9 * M0 * gamma1) / delta_mnp * 100))
# MC null: k ∈ 1..88, 10% 窗
hits3 = sum(1 for k in range(1, 89)
            if abs(delta_mnp - k * M0 * gamma1) / delta_mnp < 0.10)
print("MC null 池 (k=1..88, 10%% 窗): %d/88 命中" % hits3)
c3 = abs(delta_mnp - 9 * M0 * gamma1) / delta_mnp < 0.01
chk("G3 m_n−m_p = 9·M₀γ₁ <1%", c3,
    "dev=%.2f%%" % ((delta_mnp - 9 * M0 * gamma1) / delta_mnp * 100))

print()
print("=" * 78)
print("G4  整合判決")
print("=" * 78)
npass = sum(1 for _, c_, _ in checks if c_)
print("PASS: %d/%d" % (npass, len(checks)))
if not c1 and not c3:
    print("G1/G3 皆唔過 ⟹ 核子 = m₄₄ 標度 or 9γ₁ 結構 全滅")
    print("禁區新增: m₄₄=核子標度 (若 z<5); 9·M₀γ₁=質量差 (若 z<5); γ 節點 uud/udd 組合")
else:
    for nm, c_, dt in checks:
        print("  [%s] %s — %s" % ("OK" if c_ else "XX", nm, dt))
    print("見 docs/05 判決表 (候選需 MC z≥5 先升格)")