#!/usr/bin/python3
"""O238 — Script 32: P2 純 γ decisiveness 分析 — 用現有數據模擬 lattice 直量有冇決定性

調律者: 「根據O239經驗, 可以直接以現有數據重整化模擬 lattice 直量下的值到底有沒有決定性;
         在第一性原理推導下, 數據精度只是驗證的對照組 — O238是否可用同樣邏輯處理」

反轉邏輯: 唔好「等」— 用 FLAG 2024 現有個別 collab 值 + 多 scheme 值做「重整化模擬」:
  P1 現有 collab 散佈: BMW 16A(Nf=2+1), RM123+FNAL/MILC(Nf=2+1+1), FLAG avg, RGI
     — 各自 md/mu 中心值 vs IDCM P2 預言 γ3/γ2=2.245204 嘅 z
  P2 未來 1-2% 精度模擬: 若中心值維持現有位置(最中性假設), 誤差縮到 1%/2% 後 z 係幾多 — 有冇決定性?
  P3 IDCM 存活空間: P2 要成立, lattice 中心值需要落喺邊? 現有 collab 有冇支持者?
  P4 QED/IB 修正方向 (文獻): QED α_em 同 strong δm 各 ~1% — 修正後中心值向邊?

判準 (第一性原理立場): P2 預言係零參數純譜比 (無誤差); 決定性 = |z|≥5 (判死) / 3≤|z|<5 (傾向) / <3 (唔決定)

FLAG 2024 真實值 (arXiv:2411.04268):
  BMW 16A [65] Nf=2+1: md/mu = 4.67(9)/2.27(9) = 2.057, err~0.086
  RM123 17 [63] + FNAL/MILC/TUMQCD 18 [42] Nf=2+1+1: md/mu = 4.70(5)/2.14(8) = 2.196, err~0.090
  FLAG avg Nf=2+1+1: mu/md = 0.465(24) → md/mu = 2.1505±0.111
  FLAG RGI: md(RGI) = 6.49(12)(7) MeV; mu(RGI) 由 0.465? → 用 O234 docs/04: md/mu RGI = 2.1987±0.092
"""
import math, json

GAMMA3_G2 = 2.245204  # IDCM P2 純 γ 預言 (88-chain) — 零誤差

# 現有資料 (來源: FLAG 2024 arXiv:2411.04268 + O234 docs/04)
# (label, md/mu 中心值, 誤差, scheme)
data = [
    ("BMW 16A Nf=2+1",                2.057,  0.0860, "MS@2GeV"),
    ("RM123+FNAL/MILC Nf=2+1+1",      2.196,  0.0900, "MS@2GeV"),
    ("FLAG avg Nf=2+1+1",             2.1505, 0.1110, "MS@2GeV"),
    ("FLAG avg (RGI)",                2.1987, 0.0920, "RGI"),
]

print("═══ P1. 現有 collab 散佈 vs IDCM P2 預言 ═══")
print(f"IDCM P2 預言 γ3/γ2 = {GAMMA3_G2} (零誤差, 第一性原理)")
for label, center, err, scheme in data:
    z = (center - GAMMA3_G2) / err
    verdict = "✅ 68%內" if abs(z) < 1 else ("🟡 1-3σ" if abs(z) < 3 else "🔴 >3σ")
    print(f"  {label:28s} md/mu={center:.4f}±{err:.4f} ({scheme}) → z = {z:+.2f}σ {verdict}")

print("\n═══ P2. 未來 1-2% 精度模擬 (中心值維持現有位 — 中性假設) ═══")
print("若 FLAG avg 中心值 2.1505 唔郁, 誤差縮到 1%/2%:")
for pct in (0.02, 0.015, 0.01):
    err_new = 2.1505 * pct
    z = (2.1505 - GAMMA3_G2) / err_new
    d = "判死 IDCM (P2 錯 4-5σ+)" if abs(z) >= 5 else ("傾向判死 3-5σ" if abs(z) >= 3 else "唔決定性")
    print(f"  {pct*100:.1f}% 精度 (err={err_new:.4f}): z = {z:+.2f}σ → {d}")
print("若中心值漂向 RM123 (2.196):")
for pct in (0.02, 0.01):
    err_new = 2.196 * pct
    z = (2.196 - GAMMA3_G2) / err_new
    d = "判死" if abs(z) >= 5 else ("傾向判死" if abs(z) >= 3 else "唔決定性")
    print(f"  {pct*100:.1f}% 精度: z = {z:+.2f}σ → {d}")

print("\n═══ P3. IDCM 存活空間 (P2 要成立, lattice 中心值需要落喺邊) ═══")
for pct in (0.02, 0.015, 0.01):
    # |z|<3 存活, |z|>=5 判死
    lo3 = GAMMA3_G2 * (1 - 3 * pct)
    hi3 = GAMMA3_G2 * (1 + 3 * pct)
    lo5 = GAMMA3_G2 * (1 - 5 * pct)
    hi5 = GAMMA3_G2 * (1 + 5 * pct)
    print(f"  {pct*100:.1f}% 精度: 存活(<3σ) 需中心值 ∈ [{lo3:.4f}, {hi3:.4f}]; 判死(>5σ) ∈ [{lo5:.4f},{hi5:.4f}] 外")
print("  現有平均 2.1505: 距預言 2.245 差 4.4% — 1% 精度下需中心值漂移 +1.0% 先入存活區")

print("\n═══ P4. QED/IB 修正方向 (文獻 FLAG/BMW) ═══")
print("""
  QED 同 strong-IB 各 ~1% (α_em ≈ 1/137, (md−mu)/Λ_QCD ≈ 1/100)
  u 電荷 +2/3 > d −1/3: QED 自能正比 Q² ⟹ QED 效應令 m_u 相對 m_d 上移?
  FLAG 報告: 『isospin-breaking effects 用 pheno input 嘅計算會 code ■』
  ⟹ 現有 mu/md 大部分未完全處理 QED; 完整 QED 計算(FNAL/MILC/RM123 路線)中心值可能漂 ±1-2%
  方向不確定 — 呢個就係「現有數據重整化模擬」嘅上限: 中心值漂移幅度冇第一性原理鎖
""")

out = {
    "prediction": GAMMA3_G2,
    "data": [{"label": l, "center": c, "err": e, "scheme": s} for l, c, e, s in data],
    "P2_sim": {"1pct_center_21505": (2.1505-GAMMA3_G2)/(2.1505*0.01),
               "1pct_center_2196": (2.196-GAMMA3_G2)/(2.196*0.01)},
}
with open("data/32_p2_decisiveness.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("\nRESULT: decisiveness 分析完成 (details 見輸出)")