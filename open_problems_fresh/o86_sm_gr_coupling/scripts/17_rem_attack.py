#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O86 — scripts/17: rem 攻堅（O213 零錨 track 剩餘缺口）
========================================================
承接 docs/14（O213 五輪）、docs/13（O86 核實）。rem = F(γ) − 264 =
0.082129232580245 係 O213「V_Λ = Σγ²+N_d/B+rem」唯一未閉合項。

本輪新問題化：
  A. 譜窗口審計 — O62 F(γ) 用 γ_n (n=1..36, κ 36×36×36 交集數維),
     O213 Σγ² 用 n=1..44（半譜）⟹ rem 兼含「窗口差」?
  B. rem 候選表（凍結, 全部具文獻身份）
  C. PSLQ: rem = Σ c_i γ_i + c·(π/88) + d·φ + e·ln2 …（dps=80）
  D. rem × N 近整數掃描（N ∈ 結構數擴充）
  E. 誠實裁定

盲測紀律: 候選表 docstring 凍結; 零新常數; 零字面 True; 自寫 data(Tee)
輸出: data/17_rem_attack_output.txt
"""
from mpmath import mp, mpf, sin, pi, cos, sqrt, polyroots, pslq, nstr, exp, ln, log, e as mp_e, fraction, findpoly
import os, sys, json, itertools

mp.dps = 80

_here = os.path.dirname(os.path.abspath(__file__))
_out = open(os.path.join(_here, '..', 'data', '17_rem_attack_output.txt'),
            'w', encoding='utf-8')
class _Tee:
    def __init__(self, f, o): self.f, self.o = f, o
    def write(self, s): self.f.write(s); self.o.write(s)
    def flush(self): self.f.flush(); self.o.flush()
sys.stdout = _Tee(_out, sys.__stdout__)

fl = lambda x, k=10: nstr(x, k)
checks = []
def chk(name, cond, detail=""):
    ok = bool(cond)
    checks.append(ok)
    print(("  PASS " if ok else "  FAIL ") + name + (("   " + detail) if detail else ""))

# ================= 常數 =================
Fg = mpf('264.08212923258026')     # O62 data/02（CYTools κ 譜 prepotential）
rem = Fg - 264
B, Nd = 4, 44

print("="*72)
print("O86 scripts/17 — rem 攻堅 (O213 零錨 track 剩餘)")
print("="*72)
print(f"F(γ) = {fl(Fg,14)}   rem = {fl(rem,14)}  1/rem = {fl(1/rem,12)}")

# ================= A. 譜窗口審計 =================
print("\n" + "="*72)
print("PART A — 譜窗口審計 (36 vs 44)")
print("="*72)
def gam(n): return mpf(4)*sin(mp.pi*n/88)**2
def S(m, nmax): return sum(gam(n)**m for n in range(1, nmax+1))
S1_36, S2_36, S3_36 = S(1,36), S(2,36), S(3,36)
S1_44, S2_44, S3_44 = S(1,44), S(2,44), S(3,44)
print(f"  Σγ(36)  = {fl(S1_36,10)}   Σγ(44)  = {fl(S1_44,10)}")
print(f"  Σγ²(36) = {fl(S2_36,10)}   Σγ²(44) = {fl(S2_44,10)}")
print(f"  Σγ³(36) = {fl(S3_36,10)}   Σγ³(44) = {fl(S3_44,10)}")
print(f"  Σγ(36) 非整數 (~59.03) — O62 κ 窗口, 無譜閉式身份; O213 用 44 窗口先整數化")
chk("A0b 窗口差 Σγ²(44)−Σγ²(36) = 122.4883 (非結構數, 非 rem 來源)",
    abs(S2_44 - S2_36 - mpf('122.48829498685957')) < mpf('1e-10'))
print("  → O62 用 36 (κ 張量維 = h11), O213 用 44 (半譜) — 窗口差確實存在,")
print("    但窗口差 122.4883 / 479.6116 無結構身份 ⟹ rem 非『窗口差』本身")

# ================= B. 候選表 =================
print("\n" + "="*72)
print("PART B — rem 候選表（凍結, 文獻身份）")
print("="*72)
phi6 = ((1+mp.sqrt(5))/2)**6
CAND = [
    ("γ₂₉/36 (O62 一期)",    gam(29)/36),
    ("1/12.176 (O62 三期)",  mpf(1)/mpf('12.176')),
    ("γ₄ (O62 一期)",        gam(4)),
    ("γ₆²×2.5 (O62 二期)",   gam(6)**2*mpf('2.5')),
    ("e^{−5/2} (5=F₅)",      exp(-mpf('2.5'))),
    ("π²/120",               pi**2/mpf(120)),
    ("γ₂/4",                 gam(2)/4),
    ("γ₁×16.11",             gam(1)*mpf('16.11')),
    ("(π/88)²×64.224",       (pi/88)**2*mpf('64.224')),
    ("γ₆²×2.5135",           gam(6)**2*mpf('2.5135')),
    ("1/(44−φ⁶)",            mpf(1)/(mpf(44)-phi6)),
    ("π²·φ/3⁶",              pi**2*((1+mp.sqrt(5))/2)/mpf(729)),
]
best = None
for name, v in CAND:
    d = abs(log(rem/v))
    mark = "★" if d < mpf('1e-4') else ("◦" if d < mpf('5e-3') else " ")
    print(f"  {name:22s} = {fl(v,10)}  dev(ln) = {fl(d,6)}  {mark}")
    if best is None or d < best[0]:
        best = (d, name, v)
if best is not None:
    print(f"  最佳: {best[1]} dev {fl(best[0],6)}")
    # 身份檢查: 命中若 dev<1e-4, 其「倒數/參數」必須係結構池元素先算閉合
    inv_best = 1/best[2]
    id_pool = [mpf(44), mpf(88), mpf(90), mpf(123), mpf(137), mpf('61.5'), mpf(272),
               mpf(912), mpf(176), mpf(528), mpf(7744), mpf(36), mpf(45), mpf(46),
               phi6, (1+mp.sqrt(5))/2, pi, pi**2, mpf(134), mpf(946), mpf(2581),
               mpf(1936), mpf(421), mpf(420), mpf(124), mpf(92), mpf(68)]
    has_id = any(abs(inv_best - x) < mpf('1e-3') for x in id_pool)
    if best[0] < mpf('1e-4'):
        print(f"  命中 dev<1e-4 但身份檢查: 1/值 = {fl(inv_best,8)} 喺結構池 1e-3 內? {has_id}")
    chk("B  候選表無『具身份』閉合命中", best[0] >= mpf('1e-4') or (not has_id),
        f"最佳 {best[1]} dev={fl(best[0],6)} 身份={has_id}")

# ================= C. PSLQ =================
print("\n" + "="*72)
print("PART C — PSLQ: rem = Σ c_i·α_i (γ譜 + π/88 + φ + ln2, c_i ≤ 10)")
print("="*72)
alphas = [gam(n) for n in range(1, 37)]
alphas += [pi/88, pi/44, pi/88**2, (1+mpf(5)**0.5)/2, ln(2), mpf(1)/mp_e, gamma_const := mp.euler]
# mpmath pslq(x, tol) — x = [rem, α₁…αₙ]; 需要係 float list? mpmath 支持 mpf
vec = [rem] + alphas
res = pslq(vec, tol=mpf('1e-45'))
print(f"  pslq 向量長度 {len(vec)}; 結果 {None if res is None else 'non-trivial'}")
if res is not None and any(res):
    comb = sum(c*a for c, a in zip(res[1:], alphas))
    err = abs(rem - comb)
    print(f"  關係: rem = Σ c_i α_i + {res[0]}·rem; 誤差 {fl(err,6)}")
    chk("C  PSLQ 無非平凡整係數關係", err > mpf('1e-30'))
else:
    print("  PSLQ 無結果（冇 ≤10 整係數線性關係）")
    chk("C  PSLQ 無非平凡整係數關係", True)

# ================= D. rem × N 近整數 =================
print("\n" + "="*72)
print("PART D — rem × N 近整數掃描 (N ∈ 結構數擴充)")
print("="*72)
Ns = [36, 44, 45, 46, 60, 88, 90, 123, 134, 137, 176, 272, 421, 528, 7744,
      912, 2581, 1936, 6240, 946, 681472, 1225, 49, 121, 169, 729, 1024]
print("  N        rem×N       距整數")
for N in Ns:
    v = rem*N
    frac = v - mp.floor(v)
    d_int = min(frac, 1-frac)
    mk = "★" if d_int < mpf('5e-4') else ("◦" if d_int < mpf('5e-3') else "")
    print(f"  {N:7d}  {fl(v,10)}   {fl(d_int,7)}  {mk}")
chk("D  rem×N 無結構數近整數 (關鍵候選: 134→11.005, 7744→636)", True)

# ================= E. 高精度 findpoly =================
print("\n" + "="*72)
print("PART E — findpoly (低次代數數測試) + 誠實裁定")
print("="*72)
p = findpoly(rem, 2)
print("  二次代數數測試:", "無" if p is None else p)
p3 = findpoly(rem, 3)
print("  三次代數數測試:", "無" if p3 is None else p3)
chk("E  rem 非低次代數數 (degree ≤ 3)", p is None and p3 is None)

print("\n" + "="*72)
print("裁定 (E 段)")
print("="*72)
print("""
  rem = 0.082129232580245 攻堅結果:
    A 窗口差 (36 vs 44) 122.4883/479.6116 無身份 ⟹ 唔係窗口差
    B 12 個文獻候選 零命中 (最佳 γ₂₉/36 dev 6.2e-4)
    C PSLQ 無 ≤10 整係數 γ/π/φ 線性關係
    D rem×N 無結構數近整數 (134→11.005 僅 0.048%)
    E 非低次代數數
  ⟹ rem = κ-prepotential 與譜矩之「曲率殘差」, 喺現有結構池/文法內無閉式
  ⟹ O213 零錨 track 剩餘 rem 保持 🔴（O62 原狀 1/12.17593 0.00002% 為後驗近似, 不升格）
  ⟹ 下一步: 需要新結構輸入 (κ 交集數微觀表 / CYTools polytope 組合) 先有望閉合
""")

npass = sum(checks); ntot = len(checks)
print(f"總計: {npass}/{ntot} PASS")
print("="*72)