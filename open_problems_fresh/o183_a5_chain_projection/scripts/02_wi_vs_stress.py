#!/usr/bin/env python3
"""
O183-02: O179 W(i) 正式版加權 — M1 預言值 + 結構身份
============================================================
O179: W(i) = (frust+1)·[1+(B/L₅)·cos(π·hop/4)]
對比: stress_S (routing 內建), bc_weighted
目標:
  A. 三種權重加權 M1 vs 背景 0.2444 vs G88 0.2977
  B. 加權預言值有冇譜結構身份? (0.2639 @stress_S → ?)
  C. corr(W, |δT|) 三權重對比 — 邊個權重攜帶最多溫度結構
"""
import json, math
import numpy as np

B, L5 = 4, 11
A = 134.2
T11 = 11/45

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
routing = json.load(open(f'{BASE}/little_red_dots/data/a5_routing_weighted.json'))
nodes = routing['nodes']

hop = np.array([float(n['hop_from_cs']) for n in nodes])
frust = np.array([float(n['frust_count']) for n in nodes])
S_stress = np.array([float(n['stress_S']) for n in nodes])
bc = np.array([float(n['bc_weighted']) for n in nodes])

# O179 W(i) 正式版
W_179 = (frust+1)*(1+(B/L5)*np.cos(np.pi*hop/4))
W_stress = S_stress
W_bc = bc

print("A. 權重對比:")
print(f"   W_179  (frust+1)[1+(B/L₅)cos(π·hop/4)]: [{W_179.min():.4f}, {W_179.max():.4f}] 均值 {W_179.mean():.4f}")
print(f"   stress_S (routing 內建):                [{S_stress.min():.4f}, {S_stress.max():.4f}] 均值 {S_stress.mean():.4f}")
print(f"   bc_weighted:                            [{bc.min():.4f}, {bc.max():.4f}] 均值 {bc.mean():.4f}")
# 權重間相關
print(f"   corr(W_179, stress_S) = {np.corrcoef(W_179, S_stress)[0,1]:+.4f}")
print(f"   corr(W_179, bc)       = {np.corrcoef(W_179, bc)[0,1]:+.4f}")

print(f"\nB. 三權重加權 M1 (SMICA 4.17):")
data = json.load(open(f'{BASE}/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'))
T = np.array(data['A5_60'])[:60]
dT = T - T.mean()
m1_plain = np.mean(np.abs(dT))/A
print(f"   無加權        M1 = {m1_plain:.5f} (dev {(m1_plain/T11-1)*100:+.2f}%)")
for name, W in [('W_179', W_179), ('stress_S', S_stress), ('bc', bc)]:
    m1_w = np.sum(W*np.abs(dT))/(np.sum(W)*A)
    print(f"   {name:>10}  M1 = {m1_w:.5f} (dev {(m1_w/T11-1)*100:+.2f}%)")
    # corr
    c = np.corrcoef(W, np.abs(dT))[0,1]
    print(f"               corr(W,|δT|) = {c:+.4f}")

# C. 加權預言值結構身份 — W_179 加權 M1 係咩?
m1_179 = np.sum(W_179*np.abs(dT))/(np.sum(W_179)*A)
print(f"\nC. W_179 加權預言值 M1 = {m1_179:.5f}")
# 候選身份: 17/64, 7/26, 33/125, 24/91, 0.26 附近
for num, den, name in [(17,64,'17/64'), (7,26,'7/26'), (33,125,'33/125'), (24,91,'24/91'),
                       (13,49,'13/49'), (4,15,'4/15'), (1,4,'1/4')]:
    print(f"   {name} = {num/den:.5f} (dev {(m1_179/(num/den)-1)*100:+.2f}%)")
# G88 對照
print(f"   對照: 背景 11/45 = {T11:.5f}, G88 = 0.29770 (+21.8%)")

# D. W_179 高/低組溫度
hi = np.abs(dT)[W_179 > np.median(W_179)].mean()
lo = np.abs(dT)[W_179 <= np.median(W_179)].mean()
print(f"\nD. W_179 高W組 ⟨|δT|⟩ = {hi:.2f} μK vs 低W組 {lo:.2f} μK (比 {hi/lo:.3f})")

print("\n完成 — 詳情見 O183 docs/02")
