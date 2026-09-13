#!/usr/bin/env python3
"""
O178-D1: null 轉正候選精確審計 (O175 SESSION_START D1)
=====================================================
Claim (session_start): 60·B(n)·0.2443 = 20.49 = 61.5/3 (dev 0.059%);
  修正候選 <|cosθ|> = 11/45 = 0.24444 vs 實測 0.2443 (dev 0.06%)
誠實判準: dev << 噪聲地板 → 候選「一致但未證明」; 11/15 null 站得住
→ 升級需結構推導 1/3 或獨立地圖驗證 (data-gated)
"""
import numpy as np
import mpmath as mp
from pathlib import Path
mp.mp.dps = 60
BASE = Path(__file__).resolve().parent.parent.parent

PASS = 0; FAIL = 0
def ck(claim, cond, info=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  [✔] {claim} {info}")
    else:    FAIL += 1; print(f"  [✘] {claim} {info}")

Nd, B, L5, F5, Ngen = 44, 4, 11, 5, 3
Bn = mp.mpf(123)/88
A = mp.mpf('134.2')

# ── 讀 A5 節點溫度 ──
rows = []
with open(str(BASE/"cmb_cold_spot/data/smica_smoothed.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split(); rows.append((int(p[0]), int(p[1]), float(p[2])))
Ts = np.array([r[2] for r in rows]); cols = np.array([r[1] for r in rows])
dT = Ts - Ts.mean()
mean_abs = float(np.mean(np.abs(dT)))
ratio = mp.mpf(str(mean_abs))/A
print(f"n = {len(rows)}, <|dT|>/A = {mp.nstr(ratio,10)}")

# ── 1. 60·B(n)·<|cosθ|> vs 61.5/3 ──
cost60 = mp.mpf(60)*Bn*ratio
target13 = mp.mpf('61.5')/3
dev13 = abs(cost60/target13 - 1)
print(f"60·B(n)·<|cosθ|> = {mp.nstr(cost60,10)}  vs  61.5/3 = 20.5  dev = {mp.nstr(dev13*100,5)}%")
ck("D1-1: 60·B(n)·<|cosθ|> = 61.5/3 (dev < 5e-4)", dev13 < mp.mpf('5e-4'), f"dev={mp.nstr(dev13*100,5)}%")

# ── 2. 11/45 候選 (=(11/15)/N_gen) ──
c11_45 = mp.mpf(11)/45
c11_15 = mp.mpf(11)/15
dev_45 = abs(ratio/c11_45 - 1)
dev_15 = abs(ratio/c11_15 - 1)
print(f"11/45 = {mp.nstr(c11_45,10)}  dev = {mp.nstr(dev_45*100,5)}%   |   11/15 = {mp.nstr(c11_15,10)}  dev = {mp.nstr(dev_15*100,5)}%")
ck("D1-2: 11/45 候選一致 (dev < 1e-3)", dev_45 < mp.mpf('1e-3'))
ck("D1-3: 11/15 null 站得住 (dev > 0.5)", dev_15 > mp.mpf('0.5'))

# ── 3. Σ|cosθ| vs N_d/3 ──
S = mp.mpf(60)*ratio
dev_Nd3 = abs(S/(mp.mpf(Nd)/3) - 1)
print(f"Σ|cosθ| = {mp.nstr(S,10)}  vs  N_d/3 = 44/3 = {mp.nstr(mp.mpf(44)/3,10)}  dev = {mp.nstr(dev_Nd3*100,5)}%")
ck("D1-4: Σ|cosθ| = N_d/3 (同一身份)", dev_Nd3 < mp.mpf('5e-4'))

# ── 4. 噪聲地板: 11/45 可否被區分? ──
sigma_dT = float(np.std(np.abs(dT)))
sigma_mean = sigma_dT/np.sqrt(60)              # σ of the mean of |dT|
ratio_floor = mp.mpf(str(sigma_mean))/A
print(f"σ(|dT|) = {sigma_dT:.2f} μK, σ_mean = {sigma_mean:.2f} μK, 噪聲地板 = {mp.nstr(ratio_floor*100,4)}%")
ck("D1-5: 11/45 dev (0.04%) << 噪聲地板 (~2-3%) → 一致但未證明",
   dev_45 < ratio_floor, f"dev={mp.nstr(dev_45*100,4)}% < floor={mp.nstr(ratio_floor*100,4)}%")
ck("D1-6: 11/15 null (66.7%) >> 噪聲地板 → 確鑿證偽",
   dev_15 > 10*ratio_floor)

# ── 5. Ising color-split 不變性 (獨立交叉檢查) ──
print()
for c in (0, 1):
    sub = dT[cols == c]
    r_c = mp.mpf(str(float(np.mean(np.abs(sub)))))/A
    print(f"  color {c}: n={len(sub)} <|cosθ|> = {mp.nstr(r_c,6)}  dev vs 11/45 = {mp.nstr(abs(r_c/c11_45-1)*100,4)}%")
r0 = mp.mpf(str(float(np.mean(np.abs(dT[cols==0])))))/A
r1 = mp.mpf(str(float(np.mean(np.abs(dT[cols==1])))))/A
ck("D1-7: 兩個 Ising 色類各自 ~11/45 (唔係均值巧合)", 
   abs(r0/c11_45-1) < mp.mpf('5e-2') and abs(r1/c11_45-1) < mp.mpf('5e-2'))

# ── 6. 二階矩探測: <cos²θ> 有冇精確值? ──
c2 = mp.mpf(str(float(np.mean((dT/A)**2))))
print(f"<cos²θ> = {mp.nstr(c2,8)}  候選: 1/8={mp.nstr(mp.mpf(1)/8,8)} (dev {mp.nstr(abs(c2*8-1)*100,3)}%), 3/16={mp.nstr(mp.mpf(3)/16,8)} (dev {mp.nstr(abs(c2*16/3-1)*100,3)}%)")
ck("D1-8: <cos²θ> 冇精確小分母候選 (記錄, 唔強推)",
   abs(c2*8-1) > mp.mpf('1e-2') and abs(c2*16/mp.mpf(3)-1) > mp.mpf('1e-2'),
   f"<cos²θ> = {mp.nstr(c2,8)}")

print()
print(f"D1 AUDIT: {PASS}/{PASS+FAIL} — 判決: null (11/15) 站得住; 11/45 一致未證明; 升級需結構 1/3 推導")
import sys; sys.exit(0 if FAIL == 0 else 1)
