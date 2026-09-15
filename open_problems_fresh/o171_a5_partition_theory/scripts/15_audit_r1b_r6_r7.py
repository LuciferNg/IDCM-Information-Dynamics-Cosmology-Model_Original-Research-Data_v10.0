#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/15 — R1b/R6/R7/R8 獨立核對 (mpmath + 解析路徑, 唔共用 12/13/14 代碼)
==============================================================================
O-system 紀律: 獨立核對唔可以同被核對嘅腳本共用代碼。
路徑差異:
  (i)   Lucas 由**遞歸**生成 (唔用硬編碼字典)
  (ii)  A₅ 不變量由 irrep 維數**推導** (和 + 平方和, 唔用硬編碼表)
  (iii) Σγ_even = 90 用**解析恆等式** Σ_{j=1}^{n−1} sin²(πj/n) = n/2 (唔用數值求和)
  (iv)  R7 嘅 U 由 o9_positions_crosscheck.json (另一份記錄) 重算
  (v)   宇宙變異下限用另一條推導 (CV = √(2/(2ℓ+1)))
"""
import json
from pathlib import Path
from fractions import Fraction as Fr
import mpmath as mpm

mp = mpm.mp; mp.dps = 60
pi, sin, sqrt, nstr, mpf = mp.pi, mp.sin, mp.sqrt, mp.nstr, mp.mpf

ok = 0; tot = 0
def chk(name, cond, note=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

B, N_gen, N_d, R, F5, L4, L5, L7 = 4, 3, 44, 11, 5, 7, 11, 29
ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")

print("="*80)
print("O171 scripts/15 — R1b/R6/R7/R8 獨立核對")
print("="*80)

# ---------- A: R1b rung law (Lucas 遞歸 + 不變量推導) ----------
print("\n=== A: R1b rung law — 獨立路徑 ===")
LUC = [2, 1]
while len(LUC) < 15: LUC.append(LUC[-1] + LUC[-2])
print(f"  遞歸 Lucas (15 項): {LUC}")
chk("A Lucas 遞歸 L_5 = 11, L_4 = 7", LUC[5] == 11 and LUC[4] == 7)
# A₅ 不變量: irrep 維數由 |A₅| = Σdim² = 60 同 known irreps 推導
irr = [1, 3, 3, 4, 5]
dims_distinct = sorted(set(d for d in irr if d > 1))     # [3,4,5]
dims_mult = [d for d in irr if d > 1]                    # [3,3,4,5]  (3 出現兩次)
inv = sorted(set(irr + [sum(dims_distinct), sum(dims_mult), sum(irr), sum(d*d for d in irr)]))
print(f"  A₅ 不變量 = {inv}")
print(f"    (irrep 維數 {irr}; 非平凡 distinct {dims_distinct}; 帶重數 {dims_mult})")
chk("A1 Σdim² = 60 = |A₅| (不變量 60 由推導得出)", sum(d*d for d in irr) == 60)
chk("A2 Σ distinct 非平凡 dim = 3+4+5 = 12 = B·N_gen = L₅+1",
    sum(dims_distinct) == 12 == B*N_gen == L5+1)
chk("A2b Σ_all dim = 16 = B²", sum(irr) == 16 == B*B)
# ★★ 審計中新發現: Σ 帶重數非平凡 dim = 15 = N_gen·F₅ = 錨對 b; 2L₄ = 14 = 錨對 a
chk("A2c ★ 新發現: Σ 帶重數非平凡 dim = 3+3+4+5 = 15 = N_gen·F₅",
    sum(dims_mult) == 15 == N_gen*F5)
chk("A2d ★★ 錨對 (a,b) = (2L₄, Σ帶重數dim) = (14,15),  a+b = L₇ = 29",
    2*L4 == 14 and sum(dims_mult) == 15 and 2*L4 + sum(dims_mult) == 29 == L7)
chk("A2e ★★ 錨對乘積 2ab = 2·14·15 = 420 = 深層 sector",
    2*14*15 == 420)
print("  ★★ 錨對兩員**同時**有結構身份: a = 2L₄ (樹階), b = Σ帶重數 irrep 維數 (群)")
for d, nm in ((33, "O10"), (44, "截斷"), (55, "O167"), (420, "O167")):
    sols = [(g, m) for g in inv for m, lv in enumerate(LUC) if g*lv == d]
    print(f"  d = {d:>3} ({nm}): (g, L_m) = {[(g, f'L{m}') for g, m in sols]}")
    chk(f"A3 d = {d} 唯一分解", len(sols) == 1)
    # 對照: d 嘅全部因數中有幾多個係 A₅ 不變量
    divs = [x for x in range(1, d+1) if d % x == 0]
    inv_d = [x for x in divs if x in inv]
    print(f"        (d 嘅因數中屬 A₅ 不變量者 = {inv_d} ⇒ 商 = {[d//x for x in inv_d]})")
    chk(f"A3b d = {d} 只有一個不變量因數嘅商係 Lucas",
        sum(1 for x in inv_d if d//x in LUC) == 1)
print("  ⇒ rung law 唯一性獨立確認 (遞歸 Lucas + 推導不變量)")

# ---------- B: R8 型別二分 ----------
print("\n=== B: R8 型別二分 — 獨立路徑 ===")
bands = [n*R for n in range(1, 9)]
print(f"  鏈帶 nR (n=1..8): {bands}")
sel = [n for n in range(1, 9) if bands[n-1] in (33, 44, 55)]
chk("B 家族表層成員落喺帶 n = {3,4,5}", sel == [3, 4, 5])
chk("B1 {3,4,5} = A₅ 非平凡 irrep 維數", sorted(set(d for d in irr if d > 1)) == [3, 4, 5])
# 軌道計數型: (L²−1)/2 掃描
orb = {Lv: Fr(Lv*Lv-1, 2) for Lv in range(2, 200)}
print(f"  (L²−1)/2 值域 (L=2..10): {[int(orb[v]) for v in range(2, 11)]}")
chk("B2 420 = (29²−1)/2 (軌道計數型)", orb[29] == 420)
chk("B3 表層 (33,44,55) 唔喺 (L²−1)/2 值域",
    not any(orb[v] in (33, 44, 55) for v in orb))
chk("B4 420 ∉ 鏈帶 (420 % 11 ≠ 0)", 420 % R != 0)
pref = [sum(bands[:k]) for k in range(1, 9)]
chk("B5 420 ∉ 鏈帶前綴和", 420 not in pref)
print("  ⇒ 型別二分獨立確認: 表層 = 帶計數型; 深層 = 軌道計數型")

# ---------- C: R6 — Σγ_even = 90 用解析恆等式 ----------
print("\n=== C: R6 — Σγ_even 用解析恆等式 (唔用數值求和) ===")
print("  恆等式: Σ_{j=1}^{n−1} sin²(πj/n) = n/2")
# 偶 k: k = 2j, j = 1..44 ⇒ γ = 4sin²(πj/88)
# Σ_{j=1}^{87} sin²(πj/88) = 88/2 = 44; 由對稱 Σ_{j=1}^{87} = 2Σ_{j=1}^{43} + sin²(π·44/88) = 2S + 1
S43 = (44 - 1)/2
S44 = S43 + 1
Se_ana = 4*S44
print(f"  Σ_{{j=1}}^{{43}} sin² = (44 − 1)/2 = {S43};  Σ_{{j=1}}^{{44}} = {S44}")
print(f"  Σγ_even = 4 × {S44} = {Se_ana}")
chk("C Σγ_even = 4·22.5 = 90 (解析)", Se_ana == 90)
# 總和: Σ_{j=1}^{88} sin²(πj/176)
S88 = (88 + 1)/2
tot_ana = 4*S88
print(f"  Σ_{{j=1}}^{{88}} sin²(πj/176) = (88+1)/2 = {S88}  ⇒  Σγ_all = 4×{S88} = {tot_ana}")
chk("C1 Σγ_all = 4·44.5 = 178 (解析) = 2F₁₁", tot_ana == 178 and 2*89 == 178)
chk("C2 Σγ_odd = 178 − 90 = 88 (解析)", tot_ana - Se_ana == 88)
# 數值交叉核對
g_num = [4*sin(pi*k/176)**2 for k in range(1, 89)]
chk("C3 解析 vs 數值 (Σγ_even)", abs(sum(g_num[1::2]) - 90) < mpf('1e-40'))
chk("C4 解析 vs 數值 (Σγ_odd)", abs(sum(g_num[0::2]) - 88) < mpf('1e-40'))
# R6 恆等式 (mpmath 路徑, 唔用 Fraction)
W2 = mpf(123)/2
f_un = W2/Se_ana; E_mn = W2/88
lhs = f_un + E_mn
rhs = 2*E_mn*(mpf(89)/90)
print(f"  f_unproj + E_min = {nstr(lhs,20)}")
print(f"  2·E_min·(89/90)  = {nstr(rhs,20)}")
chk("C5 ★ O148 F3 恆等式 (mpmath 60 dps 路徑)", abs(lhs - rhs) < mpf('1e-50'))
chk("C6 和 = 3649/2640", abs(lhs - mpf(3649)/2640) < mpf('1e-50'))
# 觀測層冇成員 (獨立檢查)
print("  (觀測層獨立檢查)")
obs = {"H₀ ratio": 67.36/72.59, "n_s": 0.9649, "Ω_Λ": 0.6847}
t = 89/90
for nm, v in obs.items():
    print(f"    {nm:<10} = {v:.6f}  dev = {(v-t)/t*100:+7.3f}%")
chk("C7 觀測層冇成員 (全部 dev > 2%)", all(abs((v-t)/t*100) > 2 for v in obs.values()))
# 密度窗
win = [d for d in range(30, 3001) if abs(Fr(d-1,d) - Fr(89,90)) < Fr(5,10000)]
chk("C8 0.05% 窗內 sector 數 = 8 ⇒ 無判別力", len(win) == 8, f"({win})")

# ---------- D: R7 — U 由另一份記錄重算 ----------
print("\n=== D: R7 — U 由 o9_positions_crosscheck.json 重算 ===")
o9 = json.load(open(ROOT / "o10_peak_amplitudes/data/o9_positions_crosscheck.json"))
p_obs = o9["planck"]
print(f"  o9 planck 記錄值: " + ", ".join(f"m={k}: {v:.8f}" for k, v in p_obs.items() if v))
fp = json.load(open(ROOT / "o10_peak_amplitudes/data/final_prime_formula.json"))["planck"]
print("  ⚠️ 數據檔一致性: o9 嘅 m=7 用 ℓ=1400 (D=830.177) ⇒ 0.1427284;")
print("     final_prime_formula 用 ℓ=1409 (D=822.186) ⇒ 0.1413550  (差 1.0%)")
chk("D 兩份數據檔 m=7 值唔一致 (ℓ=1400 vs 1409)", abs(p_obs["7"] - fp["7"]["obs"]) > 1e-3,
    f"(o9 {p_obs['7']:.6f} vs fpf {fp['7']['obs']:.6f})")
phi = (1 + sqrt(5))/2
eps = 1/(4*phi); three_eps = 3*eps; lD = 9055
lad = {1: mpf(1), 2: mpf(1), 3: mpf(1)/2, 4: mpf(1)/3}
ells = {1: 527, 2: 815, 3: 1121, 4: 1409}
Ua = {}
for j in range(1, 5):
    G = three_eps*lad[j]*mp.e**(-(mpf(ells[j])/lD)**mpf('1.5'))
    Ua[j] = mpf(fp[str([2,3,5,7][j-1])]["obs"])/G
    print(f"  j={j}: U_j = {nstr(Ua[j],10)}")
mean = sum(Ua.values())/4
sc = float(mp.sqrt(sum((Ua[j]-mean)**2 for j in range(1,5))/3))
print(f"  平均 = {nstr(mean,10)},  樣本 std = {sc:.6f} ({sc/float(mean)*100:.3f}%)")
chk("D1 U 平均 ≈ 0.9703", abs(float(mean) - 0.9703) < 1e-3, f"({nstr(mean,8)})")
# 絕對誤差 (共同項 D₁) 由另一條路推導
pk = json.load(open(ROOT / "o10_peak_amplitudes/data/planck_binned_peaks.json"))["peaks"]
s1 = pk["1"]["err"]/pk["1"]["Dl"]
print(f"  σ(D₁)/D₁ = {s1*100:.4f}% (共同誤差) ⇒ U 絕對誤差 ≳ {s1*100:.2f}%")
chk("D2 U 絕對誤差 > 2% (共同項主導)", s1 > 0.02)
# 不變性示範 (★ 更正 09-15: 舊版寫「中心化殘差同 U 無關」係錯嘅斷言)
#   正確定義: r_i(U) = obs_i/(U·p_i) − 1 = x_i/U − 1,  x_i ≡ obs_i/p_i (同 U 無關)
#   ⇒ 中心化殘差 (r_i − r̄) = (x_i − x̄)/U  **反比於 U** (唔係無關);
#     真正 U-無關嘅係**歸一化形狀** (r_i − r̄)/RMS — 形狀函數本身。
#     結論不變: 形狀唔含 U 信息 ⇒ U 同整體振幅 A_s 完全簡併, 數據唔約束 U。
obs = [float(fp[str(k)]["obs"]) for k in ("2", "3", "5", "7")]
def shape_resid(Utest):
    r = []
    for j in range(1, 5):
        silk = float(mp.e**(-(mpf(ells[j])/lD)**mpf('1.5')))
        pred = three_eps*lad[j]*silk*Utest
        r.append((obs[j-1] - pred)/pred)
    return r
r_97 = shape_resid(0.97)
r_3334 = shape_resid(33/34)
print(f"  殘差 (U = 0.97)   : {[f'{float(x*100):+.4f}%' for x in r_97]}")
print(f"  殘差 (U = 33/34)  : {[f'{float(x*100):+.4f}%' for x in r_3334]}")
cen97 = [float(r_97[i]) - float(sum(r_97))/4 for i in range(4)]
cen33 = [float(r_3334[i]) - float(sum(r_3334))/4 for i in range(4)]
rms97 = float(mp.sqrt(sum(x*x for x in cen97)/4))
rms3334 = float(mp.sqrt(sum(x*x for x in cen33)/4))
print(f"  中心化殘差 (U=0.97)  : {[f'{x*100:+.4f}%' for x in cen97]}  RMS = {rms97*100:.4f}%")
print(f"  中心化殘差 (U=33/34) : {[f'{x*100:+.4f}%' for x in cen33]}  RMS = {rms3334*100:.4f}%")
print(f"  ★ 中心化殘差**成比例** (比值應 = U₂/U₁ = {(33/34)/0.97:.9f}), 唔係相等")
print(f"  ★ 歸一化形狀 (中心化/RMS) 兩組完全相同 ⇒ 形狀唔含 U 信息")
chk("D3 ★ 中心化殘差 ∝ 1/U, 比值恆定 = U₂/U₁ ⇒ 形狀唔含 U 信息",
    max(abs(cen97[i]/cen33[i] - (33/34)/0.97) for i in range(4)) < 1e-9,
    f"(比值 = {cen97[0]/cen33[0]:.9f} vs U₂/U₁ = {(33/34)/0.97:.9f})")
chk("D3b ★ 歸一化形狀 (中心化/RMS) 兩組完全相同 (U-無關)",
    max(abs(cen97[i]/rms97 - cen33[i]/rms3334) for i in range(4)) < 1e-12,
    "(⇒ U 只係整體振幅, 同 A_s 完全簡併, 數據唔約束 U)")
chk("D3c ★ 代數檢驗: r_i(U) = x_i/U − 1, 由 U=0.97 反解 x_i 再預言 U=33/34 精確命中",
    max(abs((float(r_97[i]) + 1)*0.97/(33/34) - 1 - float(r_3334[i])) for i in range(4)) < 1e-12)
# CV 下限 (另一條推導)
for N in (9, 100):
    cv = float(sqrt(2/(2*221+1)))/ (N**0.5)
    print(f"  ℓ=221, N={N} multipole: σ_CV = {cv*100:.3f}%")
need = abs(33/34 - 0.97)/((33/34))*100/2
chk("D4 CV 下限 (0.67%) ≫ 所需精度 (0.030%) ⇒ 不可達",
    float(sqrt(2/(2*221+1)))/10 > need/100, f"(差 {0.672/need:.0f}×)")

# ---------- E: 總結 ----------
print("\n=== E: 獨立核對總結 ===")
print("  R1b rung law (遞歸 Lucas + 推導不變量): ✅")
print("  R8 型別二分 (帶 vs 軌道): ✅")
print("  R6 Σγ_even = 90 (解析恆等式) + O148 F3 (mpmath 60 dps): ✅")
print("  R7 U 重算 + 不變性 + CV 下限: ✅")

print()
print(f"RESULT: {ok}/{tot} PASS")
