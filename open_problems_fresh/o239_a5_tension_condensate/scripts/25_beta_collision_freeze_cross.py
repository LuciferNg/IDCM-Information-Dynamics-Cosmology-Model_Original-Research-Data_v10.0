#!/usr/bin/python3
"""O239 — Script 25: β 名稱碰撞修正 + freeze 層 × γ stair 候選十字表
============================================================================
狀態: 2026-10-12 新增（第十九輪 audit 後續, 繼續推）
目的: ①修正「β」名稱碰撞（docs/16/17/23 用 β 指 sin18° = A5 幾何量,
     同主鏈 β_chain = −19/(4φ²) = −1.8143 完全無關——命名污染）
     ②檢定「−19/4 vs −33/7」winner 係咪版本依賴（新發現）

判據預註冊（唔 fit target）:
  N1: sin(π/10) ≡ 1/(2φ) EXACT (dev<1e-12)——A5 β 身份
  N2: β_chain 同 β_A5 比率 -5.87 唔係有理簡比——確認兩個獨立量
  N3: ★freeze 層 winner: 至少一個 freeze 層令 −33/7 距離 < −19/4 距離
      ⟹ γ stair 分子選擇版本依賴, freeze v3 判決有歧義
  N4: 統一 MC σ (0.036) 視角: v2 下 −33/7 優勢 >0.5σ 差距
產物: data/25_beta_collision_freeze_cross.json（新增）
"""
import json, math
import numpy as np

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/25 — β 名稱碰撞 + freeze 層 × γ stair 候選十字表")
print("=" * 78)

phi = (1 + math.sqrt(5)) / 2

# ── N1: sin18° ≡ 1/(2φ) ──
print("\n── N1: A5 β 身份 ──")
s18 = math.sin(math.pi/10)
inv2phi = 1/(2*phi)
dev = abs(s18 - inv2phi)
print(f"   sin(π/10) = {s18:.12f}")
print(f"   1/(2φ)     = {inv2phi:.12f}")
print(f"   dev        = {dev:.2e}")
chk("N1 sin18° ≡ 1/(2φ) EXACT", dev < 1e-12, f"dev={dev:.1e}")

# ── N2: β_chain 同 β_A5 比率 ──
print("\n── N2: 兩個 β 獨立性 ──")
b_chain = -19/(4*phi**2)
ratio = b_chain / s18
print(f"   β_chain = −19/(4φ²) = {b_chain:.6f}")
print(f"   β_A5    = sin18°     = {s18:.6f}")
print(f"   比率    = {ratio:.4f}")
# 檢查係咪有理簡比 (m/n, n<=20): 唔係整數比
nearest_frac = None
for n in range(1, 21):
    m = round(ratio * n)
    if abs(ratio - m/n) < 1e-4:
        nearest_frac = f"{m}/{n}"
print(f"   最近有理簡比 (n≤20): {nearest_frac or '冇'}")
chk("N2 比率唔係有理簡比", nearest_frac is None, f"ratio={ratio:.4f}")
chk("N2b β_chain·φ² = γ 結構鏈保持", abs(b_chain*phi**2 + 19/4) < 1e-12, f"{b_chain*phi**2:.6f}")

# ── N3: freeze 層 winner 交叉表 ──
print("\n── N3: freeze 層 × γ stair 候選 ──")
# γ 每層: (值, ±stderr OLS)
G = {
    "v1.0 PDG2024": (-4.7503, 0.372),
    "v1.1 ratio":   (-4.7711, 0.349),
    "v2 RGI":       (-4.7213, 0.384),
}
cand = {"−19/4 (Lepton/B)": -19/4, "−33/7 (Up/L₄)": -33/7}
winners = {}
print(f"   {'freeze 層':<14}{'−19/4 σ':>10}{'−33/7 σ':>10}   winner")
for ver, (v, se) in G.items():
    d1 = abs(v - cand["−19/4 (Lepton/B)"]) / se
    d2 = abs(v - cand["−33/7 (Up/L₄)"]) / se
    winners[ver] = {"d_19_4": d1, "d_33_7": d2, "winner": "−19/4" if d1 < d2 else "−33/7"}
    print(f"   {ver:<14}{d1:>10.2f}{d2:>10.2f}   {winners[ver]['winner']}")
flip = any(w["winner"] == "−33/7" for w in winners.values())
chk("N3 至少一層令 −33/7 反超", flip,
    f"v2 RGI: −33/7 {winners['v2 RGI']['d_33_7']:.2f}σ vs −19/4 {winners['v2 RGI']['d_19_4']:.2f}σ")

# ── N4: 統一 MC σ 視角 ──
print("\n── N4: 統一 MC σ=0.036（scripts/14 全域袋）──")
MC = 0.0361
for ver, (v, se) in G.items():
    d1 = abs(v - (-19/4)) / MC
    d2 = abs(v - (-33/7)) / MC
    print(f"   {ver:<14}  −19/4: {d1:>5.2f}σ   −33/7: {d2:>5.2f}σ   {'−33/7' if d2 < d1 else '−19/4'}")
flip_mc = any(abs(v - (-33/7)) / MC < abs(v - (-19/4)) / MC for v, _ in G.values())
chk("N4 MC 視角下 −33/7 有反超層", flip_mc, "v2: −33/7 0.19σ vs −19/4 0.80σ")

# ── JSON 輸出 ──
json.dump({
    "N1_sin18_identity": {"sin18": s18, "inv2phi": inv2phi, "dev": dev},
    "N2_beta_ratio": {"beta_chain": b_chain, "beta_A5": s18, "ratio": ratio,
                      "nearest_frac_n20": nearest_frac},
    "N3_freezelayer_x_gamma": {k: {"value": G[k][0], "stderr": G[k][1],
                                   "d_19_4": winners[k]["d_19_4"],
                                   "d_33_7": winners[k]["d_33_7"],
                                   "winner": winners[k]["winner"]}
                               for k in G.keys()},
    "N4_winners_mc_sigma": {k: {"d_19_4": abs(v - (-19/4))/MC, "d_33_7": abs(v - (-33/7))/MC}
                            for k, (v, _) in G.items()},
    "verdict": "β 名稱碰撞修正: β_A5=sin18°=1/(2φ) 同 β_chain=−19/(4φ²) 係兩個獨立量 "
               "(比率 −5.87 非有理簡比); ★全新發現: −19/4 vs −33/7 嘅 winner 版本依賴 — "
               "v1.0 下 −19/4 贏 (0.01 vs 1.00σ), v2 RGI 下 −33/7 反超 (0.19 vs 0.80σ MC視角) "
               "⟹ freeze v3 若用 lattice(RGI 風格) 數據, γ stair 分子選擇本身有歧義, "
               "『freeze v3 判 γ 數字身份』設計要重新審視",
}, open("data/25_beta_collision_freeze_cross.json", "w"), indent=1, ensure_ascii=False)

print("\n" + "=" * 78)
np = sum(1 for _, c in P if c)
print(f"判定: {np}/{len(P)} PASS")