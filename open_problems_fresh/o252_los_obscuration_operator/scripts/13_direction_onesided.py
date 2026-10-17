#!/usr/bin/env python3
"""
O252 — Script 13v2: 方向 one-sided 檢驗 — 事前性拆彈 (2026-10-17)
=================================================================
R3/R4 用 two-sided: 10/13 藍側 p=0.092 (未閉合)。
本 script 檢驗「改用 one-sided 會唔會閉合?」— 並嚴格拆事前性:

record 21 §3 事前預言內容: 「藍峰弱紅峰強 (R<1), 方向固定」
  → 呢個係「峰高比」預言 (peak ratio), **唔係**「dip 位置 sign」預言!
  → τ(v) 嘅 ±v_abs 係 per-source 側向身份, O252 從未事前預言「dip 喺藍側」
  → R4 已證明帶唔製造 sign bias (q_blue≈0.50)

統計學:
  若事前有「dip 藍側」預言 → one-sided p=0.0461 顯著
  若冇事前預言 → must use two-sided, p=0.092 唔顯著
  ⚠️ 用 one-sided 收窄 = post-hoc (揀方向嚟測) — 用戶標準: 禁止

判定:
  [X1] 報告 one-sided p 值 (探索性上界)
  [X2] 事前性檢查: record 21 有冇「dip sign」預言 → 冇 → one-sided 不適用
  [X3] 結論: 方向 gap 維持未閉合 (two-sided p=0.092)
"""
import json, math, os
from math import comb

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

def binom_ge(n, k, p=0.5):
    return sum(comb(n,i)*p**i*(1-p)**(n-i) for i in range(k, n+1))

print("="*84)
print("O252/13v2 — 方向 one-sided 事前性拆彈")
print("="*84)

with open(f"{DATA}/07_full_sample_scan.json") as f:
    d7 = json.load(f)
res = [r for r in d7["results"] if r["sig"] and abs(r["dv"]) < 700 and r["depth"] < 1.2]
n_total = len(res)
n_blue = sum(1 for r in res if r["dv"] < 0)
n_red = n_total - n_blue

p1 = binom_ge(n_total, n_blue)          # one-sided
p2 = 2*min(binom_ge(n_total, n_blue), binom_ge(n_total, n_red))  # two-sided approx
print(f"n={n_total}, 藍={n_blue}, 紅={n_red}")
print(f"one-sided   P(≥{n_blue}/{n_total}) = {p1:.4f}")
print(f"two-sided   P = {p2:.4f}")

ck("X1 報告 one-sided 探索性值", p1 < 0.05,
   f"p_one={p1:.4f} — 只係探索性上界, 唔係閉合")

# 事前性: record 21 內容自查 (內容直接寫喺度, 唔靠外部)
record21_claims = """
  §散射保對稱定理: 散射淨效果對模態對 (k,176−k) 對稱 → 唔對稱必來自遮蔽
  §吸收 channel: 「藍峰弱紅峰強 (R<1), 方向固定」— 峰高比預言
  §A Hα 負振幅: P-Cygni 直接證據 (record 24 fit)
  並無任何「dip 位置 sign 普適藍側」預言 — ±v_abs 係 per-source 側向
"""
pre_has_dip_sign = False   # record 21 冇 dip sign 預言
ck("X2 事前性: record 21 有 dip sign 預言", pre_has_dip_sign,
   "record 21 只預言峰比 R<1, O252 τ(v) 從未事前預言 dip 藍側")

# 剔除邊緣 K Hβ (ΔAIC=9.3) 敏感度
resS = [r for r in res if not (r["src"]=="K" and r["line"]=="Hβ")]
nS = len(resS); bS = sum(1 for r in resS if r["dv"]<0)
print(f"\n敏感度 (剔除 K Hβ 邊緣): n={nS}, 藍={bS}, "
      f"one={binom_ge(nS,bS):.4f}, two={2*min(binom_ge(nS,bS),binom_ge(nS,nS-bS)):.4f}")

data = {"n": n_total, "blue": n_blue, "red": n_red,
        "p_one_sided": p1, "p_two_sided": p2,
        "pre_registered_dip_sign": False,
        "record21": "峰比 R<1 事前預言, 冇 dip sign 預言",
        "conclusion": ("方向 gap 維持未閉合: two-sided p=0.092 唔顯著; "
                       "one-sided p=0.046 係 post-hoc 收窄, 唔當閉合"),
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{DATA}/13_direction_onesided.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS (X2 PASS=one-sided 唔適用) → "
      f"data/13_direction_onesided.json")