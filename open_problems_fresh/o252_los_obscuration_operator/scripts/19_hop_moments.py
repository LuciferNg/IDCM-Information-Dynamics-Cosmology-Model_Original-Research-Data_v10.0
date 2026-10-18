#!/usr/bin/env python3
"""
O252 — Script 19: R13 hop 階梯統計量落碟 (closeout backfill) (2026-10-17)
==========================================================================
docs/13 §6 註記嘅 ⟨v⟩=280.03 / 質量中位 289.8 係 terminal inline 計算 —
按 §4.9 規則 5 補落碟 (零新推導, 純重現 R13 數字)。
輸出: data/19_hop_moments.json
"""
import json, math, os

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data"
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

Vmax = 409.78
N = [1,4,8,11,12,11,8,4,1]      # hop 階梯 h=0..8 (O179)
S = sum(N)
v = [Vmax*math.sqrt(h/8) for h in range(9)]
v[0] = 0.0
sv = sum(nn*vv for nn,vv in zip(N, v))
mean_v = sv/S
# 質量中位層: 累積 ≥ S//2
cum = 0; med_h = None
for h in range(9):
    cum += N[h]
    if cum >= S//2:
        med_h = h
        break
print(f"Σn = {S}")
print(f"v(h) = {[round(x,2) for x in v]}")
print(f"⟨v⟩ = Σn·v/Σn = {mean_v:.4f}")
print(f"質量中位層 h = {med_h}, v = {v[med_h]:.2f}")
print(f"hop=2 候選 v = {v[2]:.2f}, hop=4 候選 v = {v[4]:.2f}")
print(f"觀測 μ_hat = 235.7±21.6 (R10)")

ck("Σn=60 (O179 正典)", S == 60, f"S={S}")
ck("⟨v⟩=280.03 (R13 註記重現)", abs(mean_v - 280.03) < 0.05, f"{mean_v:.4f}")
ck("質量中位層 h=4 (289.8)", med_h == 4, f"h={med_h}, v={v[med_h]:.2f}")
ck("hop=2 v=204.9 ≠ ⟨v⟩ (窗中心偏離質量統計)", abs(v[2]-mean_v) > 60,
   f"Δ={abs(v[2]-mean_v):.1f}")

data = {"S": S, "v_h": v, "mean_v": mean_v, "median_h": med_h,
        "median_v": v[med_h], "v_hop2": v[2], "v_hop4": v[4],
        "obs_mu_hat": 235.7, "obs_se": 21.6,
        "note": "R13 註記數字落碟; 零新推導",
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{DATA}/19_hop_moments.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {ok}/{len(LOG)} PASS → data/19_hop_moments.json")