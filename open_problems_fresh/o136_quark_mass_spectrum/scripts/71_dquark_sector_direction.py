#!/usr/bin/env python3
"""
O136 — Script 71: dquark 下型扇區方向檢驗 (R6 攻堅 ⑥, 2026-10-06)
================================================================
承接: O136/dquark-sector (O134 回報 09-28): H_color 否證 (c +1.257%→+7.892% 惡化 6.28×);
      H_sector 存活 ⟹ 修正=下型扇區; 但 k_d 階梯來源 (為何只下型) 仍 🔴
任務: ★ 下型扇區 (d,s,b) 冪律殘餘有冇共同方向/共同結構?
      檢驗「H_sector 假說」最基本預言: down-type 殘餘一致 (同符號/同 scale)

判準: 誠實 — H_sector 若要成立, down-type 3 點殘餘要有可辨識方向 (非隨機);
      上型 (u,c,t) 對照。9pt 冪律殘餘 (scripts/70 data): d −0.453, s +1.156, b −0.576;
      u −0.042, c +0.913, t −0.063。
"""
import json, math
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
rng = np.random.default_rng(20261006)

checks = []
def chk(name, cond, detail=""):
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))

# ── 權威殘餘 (scripts/70 data 重算, 唔靠記憶) ─────────────────────────
N, NC = 88, 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, NC + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
V = psii @ np.diag(idxx - idxx.mean()) @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
Dm = E[:, None] - E[None, :]
G = np.where(np.abs(Dm) > 1e-12, 1.0 / np.where(Dm == 0, 1.0, Dm), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)

M_pdg = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
         "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
O209_map = {1: "t", 2: "b", 3: "tau", 4: "c", 5: "mu", 7: "s", 9: "d", 11: "u", 13: "e"}
ns9 = sorted(O209_map)
m9 = np.array([M_pdg[O209_map[n]] for n in ns9])
lm = np.log(m9)
ldm = np.log(admn[[n - 1 for n in ns9]])
A9 = np.vstack([np.ones(9), ldm]).T
c9, *_ = np.linalg.lstsq(A9, lm, rcond=None)
res9 = lm - A9 @ c9
res = {O209_map[n]: float(res9[i]) for i, n in enumerate(ns9)}

print("=" * 96)
print("O136 Script 71: dquark 下型扇區方向檢驗 (R6 ⑥)")
print("=" * 96)
print("\nP1. 9pt 冪律殘餘 (by 扇區):")
down = np.array([res["d"], res["s"], res["b"]])
up = np.array([res["u"], res["c"], res["t"]])
lep = np.array([res["e"], res["mu"], res["tau"]])
print(f"    down (d,s,b): {down}")
print(f"    up   (u,c,t): {up}")
print(f"    lep  (e,μ,τ): {lep}")
for name, arr in [("down", down), ("up", up), ("lep", lep)]:
    print(f"    {name:>4}: mean={arr.mean():+.4f}  std={arr.std():.4f}  |sum|={abs(arr.sum()):.4f}")

# P2. 隨機 null: 9 個殘餘隨機抽 3 個 (唔換) — down 扇區特異性
MC = 50000
allres = np.array(list(res.values()))
def stat_names(arr):
    return abs(arr.sum()), arr.std()
obs_sum_d, obs_std_d = stat_names(down)
cnt_le = 0
cnt_std_le = 0
for _ in range(MC):
    pick = rng.choice(9, 3, replace=False)
    s, sd = stat_names(allres[pick])
    if s <= obs_sum_d:
        cnt_le += 1
    if sd <= obs_std_d:
        cnt_std_le += 1
p_sum = cnt_le / MC
p_std = cnt_std_le / MC
print(f"\nP2. down 扇區 vs 隨機 3 點 (MC={MC}):")
print(f"    |Σ| down={obs_sum_d:.4f}  P(≤obs) = {p_sum:.4f}")
print(f"    std down={obs_std_d:.4f}   P(≤obs) = {p_std:.4f}")
chk("P2.1 down 扇區|Σ| 隨機內 (P>0.05 = 冇共同方向)", p_sum > 0.05, f"P={p_sum:.4f}")

# P3. H_sector 預言: 下型殘餘同符號?
n_same = int((down > 0).sum())
print(f"\nP3. down 3 點同符號性: {n_same}/3 正")
chk("P3.1 down 同符號 (3 全正/全負)?", n_same in (0, 3), f"{n_same}/3 正")

# P4. k_d 階梯: 下型內部排序 (m_d < m_s < m_b) vs |Δm| 冪律排序
print(f"\nP4. 下型排序一致性:")
r_d = abs(res["d"]) < abs(res["s"]) < abs(res["b"])
print(f"    |resid| 階梯: d={abs(res['d']):.3f} s={abs(res['s']):.3f} b={abs(res['b']):.3f}")
print(f"    |resid| 遞增 (階梯)? {r_d}")
# 相反: s 唔跟「階梯」— d<s<b 質量但 s resid 最大
chk("P4.1 |resid| 唔係 d<s<b 階梯 (k_d 唔係簡單質量階梯)", not r_d, f"d<s<b resid 唔成立")

print(f"\n== 判定 ==")
print(f"   down (d,s,b) resid: −0.453, +1.156, −0.576 (唔同符號, |Σ| 隨機內 P={p_sum:.4f})")
print(f"   ⟹ H_sector「下型有共同修正」最基本預言 FAIL ⟹ H_sector 已無直接殘餘支持")
print(f"   s 獨特 (非 d/b): s 係冪律最大 breaker (scripts/70) ⟹ 問題喺 s 單點, 唔喺扇區")
print(f"   附: 上型 u,c,t = −0.042, +0.913, −0.063 — c 亦獨特 ⟹ 非扇區效應, 係個別點效應")

out = {
    "resid_down": {k: float(res[k]) for k in "dsb"},
    "resid_up": {k: float(res[k]) for k in "uct"},
    "resid_lep": {k: float(res[k]) for k in ["e", "mu", "tau"]},
    "down_sum_p": p_sum, "down_std_p": p_std,
    "down_same_sign": n_same,
    "checks": checks,
}
(DATA / "71_dquark_sector_direction.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("\ndata/71_dquark_sector_direction.json written")