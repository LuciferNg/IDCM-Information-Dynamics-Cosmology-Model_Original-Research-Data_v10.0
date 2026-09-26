#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_treephase_nogo.py — B(a): W-field tree-sector 相位算子 no-go 判定
=====================================================================
問題 (O123 SESSION_START 指定路線的替代):
  能否由 tree sector (ℚ(√5) 實子域) 導出 δ_PMNS 嘅唯一相位算子 arg(O)?

結構事實 (本 script 驗證):
  T1. T̂ = [[1,1],[1,0]] 譜 {φ, −1/φ} 全實; tree 常數 (φ, β, ε, K_tree, Lucas/Fib)
      全實 ⟹ tree sector 冇內在複結構 ⟹ 唯一可能嘅相位形式 = atan(實比) (+0/180/360 offset)
  T2. 以 tree 常數池、預算 ≤2 常數 生成 atan(比) 家族 → 覆蓋 [0,360) 嘅程度 (null control)
  T3. 對觀測候選 δ (NuFIT 6.1 NO 212°, PDG 2025 217.8°, IDCM 230°, 222.5°, 177°, 144°, 72°)
     做最佳命中 + 多重度 + 選擇規則
  T4. 剛性: 擾動常數 ±1 → 命中係否存活
判準 (o-series 精度階梯): 結構要求 err ≤ 1e-8 + multiplicity 1 + null < 5%
"""
import math, itertools, random
from fractions import Fraction
import mpmath as mp

mp.mp.dps = 50
D = lambda x: float(mp.degrees(x))

# ── tree / structural constant pool (real) ────────────────────────────────
phi = (1 + mp.sqrt(5)) / 2
beta = 1 / phi
eps = beta / 4

# 常數池: 名 -> 精確值 (mpf/Fraction)
POOL = {}
POOL['phi']   = phi
POOL['beta']  = beta
POOL['beta2'] = beta**2
POOL['beta3'] = beta**3
POOL['eps']   = eps
POOL['K']     = mp.mpf(33)     # K_tree
POOL['Ngen']  = mp.mpf(3)
POOL['B']     = mp.mpf(4)
POOL['L5']    = mp.mpf(11)
POOL['L4']    = mp.mpf(7)
POOL['L6']    = mp.mpf(18)
POOL['L7']    = mp.mpf(29)
POOL['F5']    = mp.mpf(5)
POOL['F6']    = mp.mpf(8)
POOL['F7']    = mp.mpf(13)
POOL['F8']    = mp.mpf(21)
POOL['Nd']    = mp.mpf(44)
POOL['SgE']   = mp.mpf(90)
POOL['SgO']   = mp.mpf(88)
POOL['N46']   = mp.mpf(46)
POOL['N42']   = mp.mpf(42)
POOL['B2']    = mp.mpf(16)
POOL['KpF7']  = mp.mpf(46)
POOL['m5']    = mp.mpf(5)      # L5-2Ngen
# chain γ / ω (由 tree 表達唔到, 但屬「已閉合既有算子」— 一併測, 因為 δ_CKM 就係 chain)
NCH = 176
gam = lambda k: 4*mp.sin(k*mp.pi/NCH)**2
for k in [1,2,3,4,6,7,9,21,44]:
    POOL[f'g{k}'] = gam(k)
    POOL[f'w{k}'] = mp.sqrt(gam(k))

names = list(POOL.keys())
print("="*74)
print("  B(a) tree-sector 相位算子 no-go 判定")
print("="*74)
print(f"  常數池: {len(names)} 個")

# ── T1: tree sector 冇複結構 ──────────────────────────────────────────────
print("\n  T1. tree sector 複結構檢查")
ev = mp.eigsy(mp.matrix([[1,1],[1,0]]))
evs = [mp.mpf(e) for e in ev[0]]
print(f"     T̂ 譜 = {[mp.nstr(e,12) for e in evs]}  (全實: {all(abs(mp.im(e))<1e-40 for e in evs)})")
print(f"     φ = {mp.nstr(phi,15)} ∈ ℝ;  β,ε,K_tree ∈ ℝ")
print("     ⟹ tree sector ⊂ ℝ ⟹ arg(O) 只可能係 0 或 π ⟹ 相位必為 atan(實比)+offset")
c1 = True

# ── T2: atan(比) 家族覆蓋度 + null control ───────────────────────────────
def gen_angles(pool):
    """生成 {0,180,360} + atan(a/b) 家族 (預算 ≤2 常數)。"""
    out = []
    for na, a in pool.items():
        # atan(a) 單常數
        if a > 0:
            out.append((float(mp.degrees(mp.atan(a))), f"atan({na})"))
    for (na, a), (nb, b) in itertools.combinations_with_replacement(pool.items(), 2):
        if b <= 0: continue
        r = a / b
        if r > 0:
            th = float(mp.degrees(mp.atan(r)))
            out.append((th, f"atan({na}/{nb})"))
            out.append((180+th, f"180+atan({na}/{nb})"))
            out.append((360-th, f"360-atan({na}/{nb})"))
    return out

ANG = gen_angles(POOL)
print(f"\n  T2. atan(實比) 家族: {len(ANG)} 條生成式")

def best_hit(target, tol_list=(1e-6, 1e-9)):
    res = {}
    for tol in tol_list:
        hits = sorted([(abs(th-target), expr) for th, expr in ANG if abs(th-target) < tol])
        res[tol] = hits
    bd, be = min(((abs(th-target), expr) for th, expr in ANG), key=lambda z: z[0])
    return bd, be, res

# null control: 200 個隨機 target, 睇 tol=1e-6 命中率
random.seed(12345)
NNULL = 400
hit6 = 0; hit9 = 0; dists = []
for _ in range(NNULL):
    T = random.uniform(0, 360)
    bd, be, r = best_hit(T)
    if r[1e-6]: hit6 += 1
    if r[1e-9]: hit9 += 1
    dists.append(bd)
mean_d = sum(dists)/len(dists)
print(f"     null control ({NNULL} 隨機 target): 命中率(tol=1e-6) = {hit6/NNULL*100:.1f}% ; (tol=1e-9) = {hit9/NNULL*100:.1f}%")
print(f"     平均最近距離 = {mean_d:.6f}°")

# ── T3: 觀測/框架候選 δ ──────────────────────────────────────────────────
CANDS = [
    ("NuFIT 6.1 NO bfp", 212.0,  "global fit Nov-2025"),
    ("PDG 2025 (1.21π)", 1.21*180, "PDG avg"),
    ("NuFIT 6.0 NO bfp", 177.0,  "global fit Sep-2024"),
    ("IDCM docs/09 §14", 230.0,  "(K+F7)(L5-2Ng)"),
    ("v9.0 2π/φ",        360/float(phi), "φ-trap"),
    ("Z5 twisted 4π/5",  144.0,  "Z5"),
    ("Z5 2π/5",          72.0,   "Z5"),
    ("NuFIT 6.1 IO",     274.0,  "IO bfp"),
]
print("\n  T3. 候選 δ 最佳 atan-比 命中 (含多重度):")
print(f"     {'候選':<20s}{'值°':>9s}{'最近生成式':>22s}{'dev°':>12s}{'#1e-6':>7s}{'#1e-9':>7s}")
row3 = []
for nm, val, src in CANDS:
    bd, be, r = best_hit(val)
    row3.append((nm, val, be, bd, len(r[1e-6]), len(r[1e-9])))
    print(f"     {nm:<20s}{val:9.4f}{be:>22s}{bd:12.2e}{len(r[1e-6]):7d}{len(r[1e-9]):7d}")

# 有冇 1e-8 級唯一命中?
struct_ok = any((bd < 1e-8 and n6 == 1) for _,_,_,bd,n6,_ in row3)
print(f"\n     ⟹ 任何候選達結構級 (dev<1e-8 ∧ mult=1)? {'是' if struct_ok else '否'}")

# ── T4: 剛性 (對 230 = 46×5 及 any atan 命中) ────────────────────────────
print("\n  T4. 剛性測試")
def rigidity_check():
    """對候選 δ=230 嘅整數分解 (K_tree+F7)(L5-2Ngen) 做 ±1 擾動。"""
    surv = 0; tot = 0
    for Ng in (2,3,4):
        for L5 in (10,11,12):
            for F7 in (12,13,14):
                for B in (3,4,5):
                    v = (Ng*L5+F7)*(L5-2*Ng)
                    tot += 1
                    if abs(v-230) < 1e-12: surv += 1
    return surv, tot
s, t = rigidity_check()
print(f"     (Ngen·L5+F7)(L5−2Ngen) 在 ±1 擾動 (Ngen,L5,F7) 下 =230: {s}/{t}")
print(f"     ⇒ 剛性 {'強' if s<=1 else '弱'} (但 T2 覆蓋度已決定信息量)")

# ── 裁決 ────────────────────────────────────────────────────────────────
print("\n" + "="*74)
print("  B(a) 裁決")
print("="*74)
verdict_a = []
verdict_a.append(("T1 tree 實域 ⇒ 相位形式受限 atan(實比)", c1))
verdict_a.append(("T2 null 命中率 tol=1e-6 < 5%?", hit6/NNULL < 0.05))
verdict_a.append(("T3 存在 dev<1e-8 ∧ mult=1 候選?", struct_ok))
verdict_a.append(("T4 剛性 ≤1 存活?", s <= 1))
for k, v in verdict_a:
    print(f"     [{'✔' if v else '✘'}] {k}")
npass = sum(1 for _, v in verdict_a if v)
print(f"\n  RESULT: {npass}/{len(verdict_a)} PASS")
print(f"  註: T2 null 命中率 {hit6/NNULL*100:.1f}% (tol=1e-6) — "
      f"{'<5% ⇒ 有結構選擇性' if hit6/NNULL<0.05 else '>=5% ⇒ 密度太高, 命中無信息量'}")
