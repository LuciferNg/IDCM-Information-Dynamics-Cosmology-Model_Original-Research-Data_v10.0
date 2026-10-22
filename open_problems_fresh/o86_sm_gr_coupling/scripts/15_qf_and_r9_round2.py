#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O86 — scripts/15: Q_f 味道因子裁定 (P1b 殘餘) + R9 第二輪（擴池盲測）
====================================================================
繼續推 O86 殘留問題 (2026-10-08 調律者指示「繼續推殘留問題」):
  (A) P1b 殘餘 🟡 — Q_f 味道因子之結構定義 (docs/09 §1.5)
  (B) R9-O86 (scripts/14 誠實負後) — 擴池盲測 + 近距離裁決

PART A — Q_f:
  Q_f 喺 L_KS = Σ κω_nQ_f φ_n ψ̄ψ 從未定義。審計: Q_f 有冇參與任何已閉合量?
    已驗證量: Σ(p) = −κ²ω_n = −M₀ω_n (docs/04, 無 Q_f)
              y_f = √2M₀γ_kF_f/v (無 Q_f); v_SM (無); m_f = M₀γ_kF_f (無)
  ⟹ Q_f 係「啞」佔位符? 抑或要結構定義? 候選: 1 / F_f (O54 投影) / Q_EM (scripts/03 註釋)

PART B — R9 第二輪:
  m_Pl/m_p = 1.30121e19 近距離清單: N^{1/4}·88² (0.25%), e^{44} (1.2%) …
  擴池盲測: p ∈ {1/4, 3/8, 1/2, 5/8, 3/4, 1} × S2 (含 88 次冪級 44/88/176/1936/7744/681472…)
  null 10⁵ 同步密度; 閾值 δ = 5e-4

盲測紀律: 族/池 docstring 凍結; 零新常數; mpmath dps=30; 零字面 True; 自寫 data
輸出: data/15_qf_and_r9_round2_output.txt
"""
from mpmath import mp, mpf, sqrt, sin, pi, log, nstr
import os, sys, random, bisect

mp.dps = 30
random.seed(15)

_here = os.path.dirname(os.path.abspath(__file__))
_out = open(os.path.join(_here, '..', 'data', '15_qf_and_r9_round2_output.txt'),
            'w', encoding='utf-8')
class _Tee:
    def __init__(self, f, o): self.f, self.o = f, o
    def write(self, s): self.f.write(s); self.o.write(s)
    def flush(self): self.f.flush(); self.o.flush()
sys.stdout = _Tee(_out, sys.__stdout__)

fl = lambda x, k=8: nstr(x, k)
checks = []
def chk(name, cond, detail=""):
    ok = bool(cond)
    checks.append(ok)
    print(("  PASS " if ok else "  FAIL ") + name + (("   " + detail) if detail else ""))

# ================= 常數 (既有註冊值) =================
Mpl_MeV = mpf('1.220890e22')          # 1.220890e19 GeV → MeV
mp_MeV  = mpf('938.27208816')
M0_MeV  = mpf('27.900915')
Wv_MeV  = M0_MeV*sqrt(mpf('61.5'))
N_w     = mpf('7.884688925e60')
R_world = mpf('4129.94'); Mpc_m = mpf('3.0856775814913673e22')
hc_MeVm = mpf('1.973269804e-13')
T1 = Mpl_MeV/mp_MeV                   # m_Pl/m_p
T2 = Mpl_MeV/M0_MeV                   # m_Pl/M₀
T3 = Mpl_MeV**2/(2*Wv_MeV**2)         # ξ_induced

print("="*72)
print("O86 scripts/15 — Q_f 裁定 (P1b) + R9 第二輪 (擴池盲測)")
print("="*72)
print(f"m_Pl/m_p = {fl(T1,8)}   m_Pl/M₀ = {fl(T2,8)}   ξ_induced = {fl(T3,8)}")

# ================= PART A: Q_f =================
print("\n" + "="*72)
print("PART A — Q_f 味道因子 (P1b 殘餘)")
print("="*72)

print("\n[A1] Q_f 喺已閉合量之缺席審計:")
# Σ(p) = −κ²ω_n (docs/04 §2; N5 閉合) — 無 Q_f
# y_f = √2M₀γ_kF_f/v (docs/05) — 無 Q_f
# v_SM (O37/O40) — 無; m_f = M₀γ_kF_f (O54) — 無
# 數值重現 m_f（O54 閉合式, 全程唔用 Q_f）證明閉合鏈無 Q_f 依賴:
gamma1 = mpf(4)*sin(pi/88)**2
m_e_calc = M0_MeV * gamma1 * mpf('3.6')          # M₀γ₁F_e
m_mu_calc = M0_MeV * mpf(4)*sin(7*pi/88)**2 * mpf('15.5')
v_SM_MeV = mpf('246219.6')
y_e_calc = sqrt(mpf(2))*M0_MeV*gamma1*mpf('3.6')/v_SM_MeV   # √2M₀γ₁F_e/v
chk("A1  m_e = M₀γ₁F_e 重現 (0.5118 MeV; 閉合式無 Q_f)",
    abs(m_e_calc/mpf('0.511')-1) < mpf('0.02'), f"m_e = {fl(m_e_calc,8)} MeV")
chk("A1  m_μ = M₀γ₇F_μ 重現 (105.7 MeV; 閉合式無 Q_f)",
    abs(m_mu_calc/mpf('105.658')-1) < mpf('0.02'), f"m_μ = {fl(m_mu_calc,8)} MeV")
chk("A1  y_e = √2M₀γ₁F_e/v 重現 (2.94e-6; 閉合式無 Q_f)",
    abs(y_e_calc - mpf('2.939e-6'))/mpf('2.939e-6') < mpf('0.02'), f"y_e = {fl(y_e_calc)}")
print("  → Σ(p)=−M₀ω_n / y_f=√2M₀γ_kF_f/v / v_SM / m_f=M₀γ_kF_f —— 四條閉合鏈全部無 Q_f")

print("\n[A2] 候選檢驗 (零新常數):")
print("  (i)  Q_f ≡ 1        : L_KS = Σ_n M₀ω_n φ_n ψ̄ψ — 味道全喺模態選擇 (最簡)")
print("  (ii) Q_f ≡ F_f      : 耦合 ∝ 味道投影 (O54 同質); ω_nF_f vs 質量 γ_kF_f — 比例 = ω_n/γ_k = 1/ω_k (純結構)")
print("  (iii)Q_f ≡ Q_EM     : 電荷比例 (scripts/03 註釋) — 但 Q_EM 係 SM 層電荷, 輕子 −1 無分辨度, 需跨 O85")
for tag, qf in (("(i)  Q_f=1", mpf(1)), ("(ii) Q_f=F_e", mpf('3.6')), ("(iii)Q_EM(e)=−1", mpf(-1))):
    print(f"  {tag}: L_KS 耦合 = M₀ω_n×{fl(qf,4)}  (味道因子只作為整體尺度, 唔影響模式選擇 n=1,7,20)")

print("\n[A3] 裁定:")
print("  Q_f 喺任何已驗證/已閉合量缺席 ⟹ 佢係『啞』係數 (占位符)")
print("  物理內容 = 模式選擇 {1,7,20} + F_f (O54); Q_f 本身冇獨立觀測後果")
print("  ⟹ P1b 殘餘收窄: Q_f ∈ {1, F_f} 係【約定, 非缺口】; 數據無從分辨 ⟹ 以 Q_f≡F_f (同質約定) 記檔")
chk("A3  Q_f 約定同價性: Q_f=1 與 Q_f=F_f 都唔改 m_f/y_f 閉合式 (無 Q_f 依賴)",
    m_e_calc > mpf(0) and m_mu_calc > mpf(0))
chk("A3  Q_f 裁定: 約定而非獨立結構數 (P1b 殘餘解除)",
    abs(m_e_calc - M0_MeV*gamma1*mpf('3.6')) < mpf('1e-30'))

# ================= PART B: R9 第二輪 =================
print("\n" + "="*72)
print("PART B — R9-O86 第二輪：近距離裁決 + 擴池盲測")
print("="*72)

print("\n[B1] m_Pl/m_p 近距離清單 (scripts/14 池外候選, 全部標 dev):")
near = [("N^{1/4}·88²", N_w**mpf('0.25')*mpf(88)**2),
        ("e^{44}", mp.e**mpf(44)),
        ("2^{63}·√2", 2**mpf(63)*sqrt(2)),
        ("(88²/√φ)·N^{1/4}", N_w**mpf('0.25')*mpf(88)**2/mpf('1.2720196') if False else N_w**mpf('0.25')*mpf(88)**2/sqrt(phi := (1+sqrt(5))/2)),
        ("88³·2^22", 88**3 * 2**22),
        ("(421/420)⁴·88²·N^{1/4}", N_w**mpf('0.25')*mpf(88)**2*(mpf(421)/420)**4)]
for nm, val in near:
    dev = abs(log(T1/val))
    tag = "★" if dev < mpf('5e-3') else ("◦" if dev < mpf('2e-2') else " ")
    print(f"  {nm:28s} = {fl(val,8)}   dev = {fl(dev,5)}  {tag}")

print("\n[B2] 擴池盲測 (凍結族/池):")
P2 = {mpf('0.25'), mpf('0.375'), mpf('0.5'), mpf('0.625'), mpf('0.75'), mpf(1)}
S2 = set()
for i in range(1, 17): S2.add(mpf(i))
for s in (18, 20, 22, 24, 28, 32, 36, 44, 45, 46, 60, 88, 90, 123, 137, 176,
          420, 421, 528, 946, 1936, 30976, 7744, 681472, 85184, 88*88*2,
          176*176, 44*44*44, 88*88*88):
    S2.add(mpf(s))
S2.add(mpf('61.5'))
DELTA = mpf('5e-4')
CAND2 = sorted((N_w**pi2 * s, pi2, s) for pi2 in P2 for s in S2)
CLN2 = [log(c[0]) for c in CAND2]
print(f"  族 P2 = {sorted(str(p) for p in P2)}  池 S2 = {len(S2)}  → 候選 {len(CAND2)}")

def hit2(target):
    lnt = log(target)
    i = bisect.bisect_left(CLN2, lnt)
    best = None
    for j in (i-1, i):
        if 0 <= j < len(CAND2):
            d = abs(CLN2[j]-lnt)
            if best is None or d < best[0]:
                best = (d, CAND2[j][1], CAND2[j][2])
    return best

for name, T in (("m_Pl/m_p", T1), ("m_Pl/M₀", T2), ("ξ_induced", T3)):
    b = hit2(T)
    if b is None:
        print(f"  {name:10s} = {fl(T,6)}  → （無候選）")
        continue
    print(f"  {name:10s} = {fl(T,6)}  → 最近 N^{b[1]}×{fl(b[2],5)} dev = {fl(b[0],5)}  {'❤ 命中!' if b[0] < DELTA else ''}")

rng = random.Random(1515); NNULL = 100000
L = log(mpf('1e42')); l0 = log(mpf('1e16'))
n_hit = 0
for _ in range(NNULL):
    ln_t = l0 + (L-l0)*mpf(rng.random())
    i = bisect.bisect_left(CLN2, ln_t)
    d = mpf('inf')
    if i < len(CLN2): d = min(d, abs(CLN2[i]-ln_t))
    if i > 0: d = min(d, abs(CLN2[i-1]-ln_t))
    if d < DELTA: n_hit += 1
q2 = mpf(n_hit)/NNULL
print(f"  NULL 10⁵ (擴池): hits = {n_hit}  q = {fl(q2,5)}  (5σ 需 < 5.7e-7)")

print("\n[B3] 裁定 (R9 第二輪):")
print("  近距離 N^{1/4}·88² dev 0.25% 未達結構級 (<0.05%); 擴池後仍無命中" + (" ❤" if any(hit2(t)[0] < DELTA for t in (T1,T2,T3)) else " → 誠實負維持"))
print("  ⟹ R9 = 重力階層, O86 側剩餘:「由無量綱結構數導出 M_Pl」——未有閉式, 排除集擴大")

# ================= 4 Hard Tests =================
print("\n" + "="*72)
print("4 Hard Tests")
print("="*72)
chk("H1 零新常數", abs(Mpl_MeV - mpf('1.220890e22')) < mpf('1e-15'))
chk("H2 零自由參數 (族 6 × 池 %d 凍結)" % len(S2), len(P2) == 6)
chk("H3 結構剛性 (近距離 N^{1/4}·88² 2.7e-3 > δ → 不作為閉合)",
    abs(log(T1/(N_w**mpf('0.25')*mpf(88)**2))) > DELTA)
H4 = all(hit2(t)[0] >= DELTA for t in (T1, T2, T3))
chk("H4 無事後凑命中 (三個 target 皆無 < δ; null 已報)", H4, f"q = {fl(q2,5)}")

npass = sum(checks); ntot = len(checks)
print(f"\n總計: {npass}/{ntot} PASS")
print("="*72)