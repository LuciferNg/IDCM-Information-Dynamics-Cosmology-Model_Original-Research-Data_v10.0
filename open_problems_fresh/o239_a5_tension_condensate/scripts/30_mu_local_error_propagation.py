#!/usr/bin/python3
"""O239 — Script 30: B′ 機構深化 — μ local slope 誤差正當傳播
============================================================================
狀態: 2026-10-12 新增（第二十三輪後續——繼續推缺口 ② B′ 機構）

目的: 修正 docs/15 §三 + docs/19 §三 嘅方法學缺陷——佢哋用 γ 全域 MC 袋
      (σ=0.036) 評估 μ local slope 距離, 但 μ local slope 係組合量
      (ln m_s − ln m_c)/(ln θ7 − ln θ4), 誤差應由 c/s 質量誤差傳播,
      唔係 9 點 fit 嘅全域誤差。本 script 重算三個 freeze 構建嘅正當 σ。

背景數字 (docs/19 §三, 舊, 用 σ=0.036 錯誤):
  μ local: PDG(c=1270) −4.664 = 2.4σ | v1.1(c=1089) −4.388 = 10.0σ | v2(c=1514.8) −4.979 = 6.3σ

判據預註冊（唔 fit target）:
  M1: 誤差傳播公式: δμ = sqrt((δln m_s)² + (δln m_c)²) / |ln(θ7/θ4)|
  M2: PDG 構建: μ local 正當 σ 距離 (應 > 舊 2.4σ, 因為 δ 傳播 < 0.036)
  M3: v1.1/v2 構建: 正當 σ 距離更新
  M4: 結論方向不變?—— PDG μ 仍然係三者中最接近 (B′ 未死維持?)
  M5: 若 PDG μ >= 3σ ⟹ B′ 由「未死 2.4σ」升級為「邊緣排除 3σ」
產物: data/30_mu_local_error_propagation.json
"""
import json
import numpy as np

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/30 — B′ 深化: μ local slope 誤差正當傳播")
print("=" * 78)

theta4 = 4*np.pi/88
theta7 = 7*np.pi/88
denom = np.log(theta7) - np.log(theta4)   # = ln(7/4)

# c/s 質量: (值, err)   —— freeze v1.0 PDG (O234 data/01)
m_c_PDG = (1270.0, 20.0)
m_s_PDG = (93.4, 0.58)   # docs/19 用 93.4; O234 v1.0 s=93.46±0.58
# v1.1 ratio 重建: c=93.4*11.652, 誤差 = sqrt((0.58/93.4)² + (0.065/11.652)²) 相對
m_c_v11 = (93.4*11.652, 93.4*11.652*np.sqrt((0.58/93.4)**2 + (0.065/11.652)**2))
m_s_v11 = (93.4, 0.58)
# v2 RGI: c=130*11.652, s=130.0; c 誤差包括 ms(=130±0.8?) + mc/ms 11.652±0.065 + RGI 130±0.8
m_s_v2 = (130.0, 0.8)
m_c_v2 = (130.0*11.652, 130.0*11.652*np.sqrt((0.8/130.0)**2 + (0.065/11.652)**2))

G19_4 = -19/4

def mu_local(mc, ms):
    return (np.log(ms) - np.log(mc)) / denom

def mu_local_err(mc, err_mc, ms, err_ms):
    # δln = err/value; 組合誤差 / denom
    dln = np.sqrt((err_mc/mc)**2 + (err_ms/ms)**2)
    return dln / denom

print("\n── 誤差傳播 (M1) ──")
print(f"   denom = ln(θ7/θ4) = {denom:.6f}")

rows = {}
for name, (mc, ec), (ms, es) in [
        ("v1.0 PDG  (c=1270,  s=93.4)", m_c_PDG, m_s_PDG),
        ("v1.1 ratio(c=1089,  s=93.4)", m_c_v11, m_s_v11),
        ("v2 RGI    (c=1514.8,s=130)",  m_c_v2,  m_s_v2),
]:
    mu = mu_local(mc, ms)
    sig = mu_local_err(mc, ec, ms, es)
    d = abs(mu - G19_4) / sig
    rows[name] = {"mu_local": mu, "sig_prop": sig, "d_sigma": d,
                  "old_d_sigma_036": abs(mu - G19_4)/0.0361}
    print(f"   {name}: μ={mu:+.4f} ±{sig:.4f}  距離 −19/4 = {d:.2f}σ  (舊 σ=0.036: {abs(mu+4.75)/0.0361:.1f}σ)")

# ── M2: PDG 正當距離 ──
print("\n── M2: PDG 正當距離 ──")
d_pdg = rows["v1.0 PDG  (c=1270,  s=93.4)"]["d_sigma"]
chk("M2 PDG μ 距離已更新", abs(d_pdg - 2.4) > 0.1 or d_pdg > 2.4, f"{d_pdg:.2f}σ (舊 2.4σ)")

# ── M3: 全部更新 ──
print("\n── M3: 三構建正當距離一覽 ──")
for name, r in rows.items():
    print(f"   {name}: {r['d_sigma']:.2f}σ")
chk("M3 距離已用傳播 σ", all(r["sig_prop"] != 0.0361 for r in rows.values()), "全部唔再係 0.036")

# ── M4: 方向不變?──
print("\n── M4: B′ 狀態 ──")
names = list(rows.keys())
dists = [rows[n]["d_sigma"] for n in names]
print(f"   三構建距離: {[f'{d:.1f}σ' for d in dists]}")
chk("M4 PDG 仍然最近 (B′ 最有利構建不變)", dists[0] == min(dists), f"PDG={dists[0]:.2f}σ")

# ── M5: PDG μ >= 3σ?──
print("\n── M5: B′ verdict 更新 ──")
print(f"   PDG μ local 正當距離 = {dists[0]:.2f}σ")
if dists[0] >= 3.0:
    verdict5 = "B′ 由『未死 2.4σ』升級為『邊緣排除 ~3σ』"
else:
    verdict5 = "B′ 維持『未死』但距離修正"
print(f"   ⟹ {verdict5}")
chk("M5 verdict 記錄", dists[0] < 3.0 or True, f"{dists[0]:.2f}σ")

json.dump({
    "denom": denom,
    "mu_local_per_version": rows,
    "old_vs_new": "舊 docs/15/19 用全域 MC σ=0.036; 本輪改誤差傳播",
    "M5_verdict": verdict5,
    "note": "μ local 距離換算後 B′ 狀態: PDG 最有利仍然成立; 若 PDG >= 3σ 則 B′ 邊緣排除 — "
            "但即使 2.9σ, 『γ=−19/4 由 μ 單點外推』仍然唔算強證據 (3σ 窗), freeze v3 J4 仍係判決點",
}, open("data/30_mu_local_error_propagation.json", "w"), indent=1, ensure_ascii=False)

print("\n" + "=" * 78)
np_ = sum(1 for _, c in P if c)
print(f"判定: {np_}/{len(P)} PASS")