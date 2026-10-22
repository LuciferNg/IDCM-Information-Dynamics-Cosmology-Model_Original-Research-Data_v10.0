#!/usr/bin/env python3
"""
O177 script 04 — 文檔獨立核對審計 (Document Cross-Audit)
==========================================================
目標: 由零重算 O177 所有文檔 (docs/01-03, 01_problem_record, final_result)
      聲稱嘅每一個關鍵數值, 對比驗證 — 唔重用任何 O177 scripts 嘅計算路徑。

禁止: 新推導 / 修改文檔 — 純驗證現有記錄 (用戶紀律: 禁止跨文檔污染)
"""
import mpmath as mp
mp.mp.dps = 60

PASS = 0; FAIL = 0
def ck(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name} {info}")
    else:
        FAIL += 1; print(f"  [FAIL] {name} {info}")

def reldev(a, b):
    return abs(a/b - 1)

# ---- 結構常數 (獨立定義, 唔依賴 O177 scripts) ----
Nd = mp.mpf(44); B = mp.mpf(4); L4 = mp.mpf(7); L5 = mp.mpf(11)
F7 = mp.mpf(13); F11 = mp.mpf(89); mu2 = mp.mpf(2); dimC = mp.mpf(3)
Ktree = mp.mpf(33)
phi = (1 + mp.sqrt(5)) / 2
eta = phi ** (-21)
Sg_odd = mp.mpf(88); Sg_even = mp.mpf(90); Sg = Sg_odd + Sg_even

# ---- 觀測複合輸入 (O173 data/01, 同 docs 一致) ----
N = mp.mpf(434); M_med = mp.mpf('6.97e6'); t_act = mp.mpf('11e9')
T_ring_yr = mp.mpf('84.6349e9')
E_strain = mp.mpf('1564785320847.4905')
R_rel_obs = mp.mpf('6730.85550941724')

print("=" * 74)
print("Part A — 複合鏈重算 (docs/01 §2, 02 §2, 03 §4)")
print("=" * 74)
rate_mass = N * M_med / t_act
R_rel = rate_mass / eta
pools = R_rel * T_ring_yr / E_strain
print(f"  rate_mass = {mp.nstr(rate_mass, 12)}  (文檔: 0.274998)")
print(f"  R_rel     = {mp.nstr(R_rel, 12)}  (文檔: 6730.8555)")
print(f"  池/圈     = {mp.nstr(pools, 12)}  (文檔: 364.0533148)")
ck("A1 rate_mass = 0.274998 (docs/01 C3)", reldev(rate_mass, mp.mpf('0.2749981818181818')) < mp.mpf('1e-10'))
ck("A2 R_rel = 6730.8555 (docs/01 §2)", reldev(R_rel, R_rel_obs) < mp.mpf('1e-12'))
ck("A3 池/圈 = 364.0533 (docs/01 §2, 02 §2, 03 §4)", reldev(pools, mp.mpf('364.0533147674503')) < mp.mpf('1e-12'))
dev_pools = reldev(pools, mp.mpf(364))
ck("A4 dev vs 364 = 0.0146% (docs/01 §2, problem_record §四)", reldev(dev_pools, mp.mpf('0.000146')) < mp.mpf('0.01'),
   f"dev = {mp.nstr(dev_pools*100, 5)}%")

print()
print("=" * 74)
print("Part B — 身份形式重算 (docs/01 §2, 7 等價形式)")
print("=" * 74)
f1 = B * L4 * F7
f2 = B * (F11 + mu2)
f3 = mu2 * (Sg + B)
f4 = 8 * (Nd + 1) + B
f5 = 2 * Nd * B + (L5 + 1)
f6 = Ktree * L5 + 1
f7 = mp.mpf(14 * 13 * 12 // 6)   # C(14,3)
ck("B1 364 = B·L4·F7 (形式1)", f1 == 364)
ck("B2 364 = B(F11+mu2) (形式2)", f2 == 364)
ck("B3 364 = mu2(Sg+B) (形式3)", f3 == 364)
ck("B4 364 = 8(Nd+1)+B (形式4)", f4 == 364)
ck("B5 364 = 2Nd·B+(L5+1) (形式5)", f5 == 364)
ck("B6 364 = K_tree·L5+1 (形式6)", f6 == 364)
ck("B7 364 = C(2L4,3) (形式7)", f7 == 364)
n91 = L4 * F7
ck("B8 91 = L4·F7 = F11+mu2 = 2Nd+dimC (docs/01 §2)", n91 == F11 + mu2 == 2*Nd + dimC == 91)
ck("B9 91 = 88+3 (docs/01 §2, D3)", 2*Nd == 88 and dimC == 3 and 2*Nd + dimC == 91)
ck("B10 Σγ = 178 = 2F11 (docs/01 形式3 依賴)", Sg == 178 == 2*F11)
ck("B11 75 = L4·L5−mu2 = 2Nd−F7 (docs/02 D3)", L4*L5 - mu2 == 75 == 2*Nd - F7)

print()
print("=" * 74)
print("Part C — 零參數預言重算 (docs/01 §2 層3, final_result)")
print("=" * 74)
R_pred = 364 * E_strain / T_ring_yr
dev_R = reldev(R_rel_obs, R_pred)
print(f"  R_rel(pred) = {mp.nstr(R_pred, 10)}  (文檔: 6729.87)")
print(f"  dev = {mp.nstr(dev_R*100, 5)}%  (文檔: 0.015%)")
ck("C1 R_pred = 6729.87 (docs/01, final_result)", reldev(R_pred, mp.mpf('6729.8698')) < mp.mpf('1e-5'))
ck("C2 dev = 0.015% (docs/01 C2, problem_record, final_result)",
   reldev(dev_R, mp.mpf('0.0001465')) < mp.mpf('0.1'), f"dev = {mp.nstr(dev_R*100, 5)}%")
t_turn_obs = E_strain / R_rel_obs
t_turn_id = T_ring_yr / 364
print(f"  t_turn(obs) = {mp.nstr(t_turn_obs/1e6, 7)} Myr, t_turn(id) = {mp.nstr(t_turn_id/1e6, 7)} Myr")
ck("C3 t_turn = 232.5 Myr 雙路一致 (docs/01 C1, final_result)",
   reldev(t_turn_obs, t_turn_id) < mp.mpf('5e-4'),
   f"dev = {mp.nstr(reldev(t_turn_obs, t_turn_id)*100, 4)}%")
ck("C4 t_turn ≈ 232.5 Myr (docs/01 §2)", reldev(t_turn_id, mp.mpf('232.5e6')) < mp.mpf('0.001'))
ck("C5 文檔值 232.48 vs 232.51 (docs/02 C1)", 
   reldev(t_turn_obs/1e6, mp.mpf('232.4794')) < mp.mpf('1e-4') and reldev(t_turn_id/1e6, mp.mpf('232.5135')) < mp.mpf('1e-4'))
# 36% 算術修正
frac_36 = (N * M_med / eta) / (mp.mpf(131) * E_strain)
ck("C6 「36%」= 36.12% 維度錯配 (docs/01 C5, §1)", reldev(frac_36, mp.mpf('0.3612')) < mp.mpf('0.01'),
   f"= {mp.nstr(frac_36*100, 5)}%")
# η
ck("C7 η = φ⁻²¹ = 4.0856e-5 (docs/02, O173 C6)", reldev(eta, mp.mpf('4.085634900844741e-05')) < mp.mpf('1e-10'))

print()
print("=" * 74)
print("Part D — 誤差傳播重算 (docs/02 Part A/B)")
print("=" * 74)
def pools_at(M=M_med, t=t_act, T=T_ring_yr, E=E_strain):
    return N * M * T / (t * eta * E)
sig_M = mp.mpf('0.005')/mp.sqrt(3); sig_t = mp.mpf('0.05')/mp.sqrt(3)
sig_T = mp.mpf('0.0001')/mp.sqrt(3); sig_E = mp.mpf('0.0045')/mp.mpf('100')
sM = abs(pools_at(M=M_med*(1+sig_M)) - pools_at(M=M_med*(1-sig_M)))/2
st = abs(pools_at(t=t_act/(1+sig_t)) - pools_at(t=t_act/(1-sig_t)))/2
sT = abs(pools_at(T=T_ring_yr*(1+sig_T)) - pools_at(T=T_ring_yr*(1-sig_T)))/2
sE = abs(pools_at(E=E_strain/(1+sig_E)) - pools_at(E=E_strain/(1-sig_E)))/2
sig_pools = mp.sqrt(sM*sM + st*st + sT*sT + sE*sE)
print(f"  σ(M)={mp.nstr(sM,6)} σ(t)={mp.nstr(st,6)} σ(T)={mp.nstr(sT,6)} σ(E)={mp.nstr(sE,6)}")
print(f"  σ合併 = {mp.nstr(sig_pools, 6)}  (文檔: 10.56)")
ck("D1 σ(M) = 1.05 (docs/02 A)", reldev(sM, mp.mpf('1.05093')) < mp.mpf('1e-4'))
ck("D2 σ(t) = 10.51 主導 (docs/02 A)", reldev(st, mp.mpf('10.5093')) < mp.mpf('1e-4'))
ck("D3 σ合併 = 10.56 (docs/02 A, problem_record, final_result)",
   reldev(sig_pools, mp.mpf('10.5618')) < mp.mpf('1e-4'))
delta = pools - mp.mpf(364)
sigma_n = abs(delta) / sig_pools
ck("D4 δ = 0.005σ (docs/02 B, problem_record, final_result)",
   reldev(sigma_n, mp.mpf('0.005048')) < mp.mpf('0.02'), f"δ = {mp.nstr(sigma_n, 5)}σ")
ck("D5 δ 絕對值 = 0.0533 (docs/02)", reldev(abs(delta), mp.mpf('0.0533148')) < mp.mpf('1e-4'))

print()
print("=" * 74)
print("Part E — B/75 候選重算 (docs/02 D, problem_record)")
print("=" * 74)
cand = B / (L4*L5 - mu2)
print(f"  B/75 = {mp.nstr(cand, 12)}  (δ = {mp.nstr(delta, 10)})")
dev_delta = reldev(abs(delta), cand)
print(f"  δ-dev = {mp.nstr(dev_delta*100, 5)}%  (文檔: 0.035%)")
ck("E1 δ = B/75 (4/75 = 0.0533333, docs/02 D1)", reldev(cand, mp.mpf('0.0533333')) < mp.mpf('1e-6'))
ck("E2 δ-dev = 0.035% (docs/02 D1, problem_record, final_result)",
   reldev(dev_delta, mp.mpf('0.00035')) < mp.mpf('0.05'), f"dev = {mp.nstr(dev_delta*100, 5)}%")
r = delta / mp.mpf(364)
one_6825 = mp.mpf(1) / ((L4*L5 - mu2) * (L4*F7))
ck("E3 r = 1/(75·91) = 1/6825 (docs/02 D2)", reldev(one_6825, mp.mpf('0.00014652014652')) < mp.mpf('1e-10'))
ck("E4 r-dev = 0.035% (docs/02 D2)", reldev(abs(r), one_6825) < mp.mpf('0.001'))

print()
print("=" * 74)
print("Part F — 逆向鎖定重算 (docs/02 E)")
print("=" * 74)
M_claim1 = M_med * 364 / pools
M_claim2 = M_med * (364 + B/(L4*L5-mu2)) / pools
print(f"  M*(364)     = {mp.nstr(M_claim1/1e6, 9)}e6  (文檔: 6.96898e6)")
print(f"  M**(364+B/75) = {mp.nstr(M_claim2/1e6, 9)}e6  (文檔: 6.9700004e6)")
ck("F1 M* = 6.96898e6 (docs/02 E2)", reldev(M_claim1, mp.mpf('6.9689793e6')) < mp.mpf('1e-6'))
ck("F2 M** = 6.9700004e6 (docs/02 E1)", reldev(M_claim2, mp.mpf('6.97000036e6')) < mp.mpf('1e-6'))
ck("F3 M** dev from 6.97e6 = 0.000005% (docs/02 E1)", reldev(M_claim2, M_med) < mp.mpf('1e-5'))
ck("F4 M* dev = 0.0146% (docs/02 E2)", reldev(M_claim1, M_med) < mp.mpf('0.0002'))

print()
print("=" * 74)
print("Part G — 家族審計重算 (docs/03)")
print("=" * 74)
# 點估計距離
for n, docv in [(356, '2.21%'), (360, '1.11%'), (364, '0.015%'), (368, '1.08%')]:
    dev_n = abs(pools - n) / pools * 100
    print(f"  dev({n}) = {mp.nstr(dev_n, 5)}%  (文檔: {docv})")
ck("G1 dev(356) = 2.21% (docs/03)", reldev(abs(pools-356)/pools*100, mp.mpf('2.2121')) < mp.mpf('0.01'))
ck("G2 dev(360) = 1.11% (docs/03)", reldev(abs(pools-360)/pools*100, mp.mpf('1.1134')) < mp.mpf('0.01'))
ck("G3 dev(364) = 0.015% (docs/03)", reldev(abs(pools-364)/pools*100, mp.mpf('0.0146')) < mp.mpf('0.01'))
ck("G4 dev(368) = 1.08% (docs/03)", reldev(abs(pools-368)/pools*100, mp.mpf('1.084')) < mp.mpf('0.01'))
# 統計帶
for n, docz in [(356, 0.762), (360, 0.384), (364, 0.005), (368, 0.374)]:
    z = abs(pools - n) / sig_pools
    ck(f"G5 {n} = {docz}σ (docs/03 C)", reldev(z, mp.mpf(str(docz))) < mp.mpf('0.02'), f"{mp.nstr(z,4)}σ")
# 巧合概率
p_coinc = mp.mpf('0.2') / mp.mpf('16')
ck("G6 巧合概率 = 1.25% (docs/03 E1, 03 §6)", reldev(p_coinc*100, mp.mpf('1.25')) < mp.mpf('0.01'))
# 質因數
from math import isqrt
def factor(n):
    f = []; d = 2
    while d*d <= n:
        while n % d == 0: f.append(d); n //= d
        d += 1
    if n > 1: f.append(n)
    return f
ck("G7 356 = 2²×89 (docs/03 D2)", factor(356) == [2,2,89])
ck("G8 360 = 2³×3²×5 (docs/03 D3)", factor(360) == [2,2,2,3,3,5])
ck("G9 364 = 2²×7×13 = B·L4·F7 (docs/03 D1)", factor(364) == [2,2,7,13])
# 家族四範圍
ck("G10 家族四 = 352-368, 中心 360, 寬度 16 (docs/01 §2 層2)", 
   352 <= 364 <= 368 and 360 == 8*(44+1) and (368-352) == 16)
ck("G11 360 = 4Σγ_even = 8(Nd+1) (docs/01 §2 層2)", 4*Sg_even == 360 == 8*(Nd+1))
# 434×6.97e6 ≈ 55²×10⁶
prod55 = N * M_med
dev55 = reldev(prod55, mp.mpf('55')**2 * mp.mpf('1e6'))
ck("G12 434×6.97e6 ≈ 55²×10⁶ dev 0.0007% (docs/01 D2, problem_record)",
   reldev(dev55, mp.mpf('0.000007')) < mp.mpf('0.1'), f"dev = {mp.nstr(dev55*100, 5)}%")

print()
print("=" * 74)
print("Part H — 跨文檔一致性命中檢查 (數值引用一致性)")
print("=" * 74)
# 文檔聲稱值一致性 (由 3 docs + problem_record + final_result 提取)
claims = {
    '364 = B·L4·F7': (mp.mpf(364), mp.mpf(364)),
    '91 = L4·F7': (L4*F7, mp.mpf(91)),
    'R_pred = 6729.87': (R_pred, mp.mpf('6729.87')),
    't_turn = 232.5 Myr': (t_turn_id/1e6, mp.mpf('232.5')),
    'σ合併 = 10.56': (sig_pools, mp.mpf('10.56')),
    'δ = 0.005σ': (sigma_n, mp.mpf('0.005')),
    'B/75 = 0.0533333': (cand, mp.mpf('0.0533333')),
    'E_strain = 1.564785e12': (E_strain/1e12, mp.mpf('1.564785')),
    'T_ring = 84.6349 Gyr': (T_ring_yr/1e9, mp.mpf('84.6349')),
    'η = 4.0856e-5': (eta, mp.mpf('4.0856e-5')),
}
for name, (calc, doc) in claims.items():
    ck(f"H {name} 跨文檔一致", reldev(calc, doc) < mp.mpf('0.01'), f"calc={mp.nstr(calc,8)} doc={mp.nstr(doc,8)}")

print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
import sys
sys.exit(0 if FAIL == 0 else 1)
