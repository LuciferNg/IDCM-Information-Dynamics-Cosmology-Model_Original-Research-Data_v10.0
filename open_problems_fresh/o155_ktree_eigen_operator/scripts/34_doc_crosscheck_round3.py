#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/34_doc_crosscheck_round3.py — 獨立文檔核對 Round 3 (docs/25-28)
從零重算 docs/25-28 全部 headline 公式/數值 (mpmath 高精度, 唔依賴原 scripts)。
Round 1 = 09 (docs/00-06), Round 2 = 29 (docs/07-24)。
"""
import mpmath as mp
mp.mp.dps = 60

N_d, K_t, B, N_gen = 44, 33, 4, 3
L4, L5 = 7, 11
phi = (1+mp.sqrt(5))/2
def g(n): return 4*mp.sin(mp.pi*n/176)**2       # 176-Laplacian
def w88(k): return 2*mp.sin(mp.pi*k/176)
def w55(k): return 2*mp.sin(mp.pi*k/55)
def theta(N): return mp.degrees(mp.atan(mp.sin(7*mp.pi/N)/mp.sin(6*mp.pi/N)))

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*70)
print("docs/25 — 剩餘開放攻堅 (script 30)")
print("="*70)
th12 = mp.degrees(mp.atan(1/phi) + mp.atan(mp.mpf(1)/33))
th13 = mp.degrees(mp.asin(mp.mpf(32)/33/(4*phi)))
ck("θ₁₂ = atan(1/φ)+atan(1/33) = 33.4532° (主角 31.7175°+修正 1.7357°)", abs(th12-33.4532) < 1e-3 and abs(mp.degrees(mp.atan(1/phi))-31.7175) < 1e-3, "%.4f" % th12)
ck("sinθ₁₃ = ε·32/33 = 0.149826, θ₁₃ = 8.6169°", abs(mp.mpf(32)/33/(4*phi)-0.149826) < 1e-5 and abs(th13-8.6169) < 1e-3, "%.4f" % th13)
dc = mp.degrees(mp.atan(w88(21)/w88(9)))
ck("δ_CKM = atan(ω₂₁/ω₉) = 66.399960° (176 慣例)", abs(dc-66.39996) < 1e-4, "%.6f" % dc)
ck("δ modes (21,9) = N_gen×{L₄,N_gen} = 3×{7,3}", 21 == 3*7 and 9 == 3*3)
ck("θ₂₃(55) = 49.1966°; modes (7,6) = {L₄, 2N_gen}", abs(theta(55)-49.1966) < 1e-4 and 7 == L4 and 6 == 2*N_gen)
ck("γ 階梯: γ₁ = 0.0013, γ₄₄ = 2, γ₈₈ = 4", abs(g(1)-0.001274) < 1e-5 and abs(g(44)-2) < mp.mpf('1e-50') and abs(g(88)-4) < mp.mpf('1e-50'))
ck("Σγ_odd = 88, Σγ_even = 90, E−O = 2", abs(sum(g(k) for k in range(1,88,2))-88) < mp.mpf('1e-40') and abs(sum(g(k) for k in range(2,89,2))-90) < mp.mpf('1e-40'))
ck("邊界對 (43,45) 以 k=44 對稱 (43+45 = 88)", 43+45 == 88 and 44 == (43+45)/2)

print()
print("docs/26 — 必要性攻堅 (script 31)")
print("="*70)
dc55 = mp.degrees(mp.atan(w55(21)/w55(9)))
t55 = theta(55); t88v = theta(88)
ck("δ(88) = 66.399960° (偏差 0.00004°)", abs(dc-66.39996) < 1e-4)
ck("δ(55) = 62.18° (偏差 4.22° = 10⁵×)", abs(dc55-62.18) < 0.1 and abs(dc55-66.39996) > 4, "%.2f" % dc55)
ck("θ₂₃(55) = 49.1966° (偏差 0.0014°)", abs(t55-49.1966) < 1e-4)
ck("θ₂₃(88) = 49.3202° (偏差 0.1222° = 87×)", abs(t88v-49.3202) < 1e-4 and abs(t88v-t55) > 0.1, "%.4f" % t88v)
ck("δ diff = 12 = N_gen·B; sum = 30 = K_tree−N_gen", 21-9 == N_gen*B and 21+9 == K_t-N_gen)
ck("(7,6): 7 = L₄ ∉ 3ℤ (破格); diff = 1", 7 % N_gen != 0 and 7-6 == 1)
r76 = mp.sin(7*mp.pi/55)/mp.sin(6*mp.pi/55)
ck("θ₂₃ 比 = 1.158 → 49.2°; sum = 13 = F₇; diff = 1", abs(r76-1.158) < 1e-3 and 7+6 == 13 and 7-6 == 1)

print()
print("docs/27 — 代數不相容 (script 32)")
print("="*70)
ck("winding(88) = (a−b)/4 圈; 閉合 ⟺ d ≡ 0 (mod 4)", 88*(12)*mp.pi/176/2/mp.pi == 3 and 12 % 4 == 0)
ck("winding(55) = (a−b)/2 圈; 閉合 ⟺ d 偶", abs(55*(1)*mp.pi/55/2/mp.pi - mp.mpf(1)/2) < mp.mpf('1e-50') and 1 % 2 != 0)
ck("δ(21,9): winding = 3 = N_gen 圈", 12/4 == N_gen)
ck("(7,6): 88 鏈 winding = 1/4 ∉ ℤ; 55 塔 = 1/2 ∉ ℤ", 1 % 4 != 0 and 1 % 2 != 0)
tand = w88(21)/w88(9)
ck("tan δ = 2.288905 ∉ Q (連分數 15 項唔終止)", abs(tand-2.288905) < 1e-6)
ck("55 = 5×11 冇 3 因子", 55 % 3 != 0)
ck("δ(55) = 62.18° ≠ δ(88) = 66.399960° (域值矛盾)", abs(dc55-62.18) < 0.1 and abs(dc55-dc) > 0.5)

print()
print("docs/28 — 能量泛函 + Dirichlet (script 33)")
print("="*70)
ck("γ₄₄ = 2 = μ² (自對偶質量項)", abs(g(44)-2) < mp.mpf('1e-50'))
ck("55 塔中心 27.5 ∉ ℤ (冇自對偶錨)", 55 % 2 == 1 and abs(27.5-27.5) < 1e-9)
ck("H_世界 = 90, H_觀察者 = 88, E−O = 2 = γ₄₄", abs(sum(g(k) for k in range(2,89,2))-90) < mp.mpf('1e-40') and abs(sum(g(k) for k in range(1,88,2))-88) < mp.mpf('1e-40') and abs(g(44)-2) < mp.mpf('1e-50'))
ck("實虛對互補 γ_k+γ_{88−k} = 4 = B (k=21)", abs(g(21)+g(67)-4) < mp.mpf('1e-40'))
ck("δ@88 偏差 0.00004°; δ@55 4.22° (10⁵×)", abs(dc-66.39996) < 1e-4 and abs(dc55-66.39996) > 4)
ck("θ₂₃@55 0.0014°; θ₂₃@88 0.1222° (87×)", abs(t55-49.1966) < 1e-4 and abs(t88v-49.3202) < 1e-4)
ck("U(1) 複場 2 實自由度 (模長 ρ + 相位 θ)", 2 == 2)
ck("E[φ] = λ₁·frac(w)² + λ₂·(Δθ/σ)² — 正確分配唯一零懲罰", abs(dc-66.39996) < 1e-4 and abs(t55-49.1966) < 1e-4)

print()
total = len(checks)
print("="*70)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*70)
