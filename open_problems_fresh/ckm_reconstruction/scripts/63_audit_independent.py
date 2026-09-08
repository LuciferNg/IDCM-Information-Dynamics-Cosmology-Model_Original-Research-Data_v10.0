#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 63 — AUDIT 獨立重驗證 (2026-09-09 審計輪)
==============================================================
T1: 唔 import 任何原 scripts (47-62), 從第一原理重算全部 headline numbers。
    核對 docs/09 §19-28 + record rows 35-44 嘅每個公式/數值。
Conventions (O155 審計鐵律):
    - γ_k = 4sin²(kπ/176), k = 1..88  (176-Laplacian 首 88 模)
    - Σγ_odd = k∈{1,3,...,87}; Σγ_even = k∈{2,4,...,88}
    - T̂ = [[1,1],[1,0]]; Lₙ = Tr(T̂ⁿ); Fₙ = (T̂ⁿ)₁₂
    - P_Δ(x) = Π_{k=1}^{88}(x−γ_k); P_odd/P_even = sector 限制
    - R(P_Δ,P_T̂ⁿ) = Π_{k=1}^{88} P_T̂ⁿ(γ_k) = Π(γ_k²−Lₙγ_k+1)
"""
import mpmath as mp
mp.mp.dps = 50

PASS = FAIL = 0
def chk(name, got, expected, tol=1e-40, note=""):
    """got/expected 均為 mp 表達式 — mp-vs-mp 直接比較"""
    global PASS, FAIL
    g, e = mp.mpf(got), mp.mpf(expected)
    if abs(g - e) <= tol:
        PASS += 1
        print(f"  [✔] {name} = {mp.nstr(g, 16)}{'  ' + note if note else ''}")
    else:
        FAIL += 1
        print(f"  [✘] {name} = {mp.nstr(g, 16)} vs {mp.nstr(e, 16)} (dev {float(abs(g-e)):.2e})  {note}")

# ---- 第一原理定義 (全 mpf, 避免 int/int float 污染) ----
N_d, N_gen, B, K_tree = mp.mpf(44), mp.mpf(3), mp.mpf(4), mp.mpf(33)
L5, L4, L6 = mp.mpf(11), mp.mpf(7), mp.mpf(18)
mu2 = mp.mpf(2)
T = mp.matrix([[1,1],[1,0]])
def Tn(n):
    M = mp.eye(2)
    P = mp.matrix(T)
    for _ in range(n):
        M = M * P
    return M
def Lucas(n): return mp.mpf(Tn(n)[0,0] + Tn(n)[1,1])
def Fib(n):   return mp.mpf(Tn(n)[0,1])
gamma = [4*mp.sin(k*mp.pi/176)**2 for k in range(1, 89)]   # γ_k, k=1..88
g_odd  = [gamma[k] for k in range(0, 88, 2)]   # k=1,3,...,87
g_even = [gamma[k] for k in range(1, 88, 2)]   # k=2,4,...,88

def prod(xs): 
    r = mp.mpf(1)
    for x in xs: r *= x
    return r

print("=" * 72)
print("A. 鏈譜基本 (docs/09 §19.1-19.2, §25.1, §28)")
print("=" * 72)
S_odd, S_even = mp.fsum(g_odd), mp.fsum(g_even)
chk("Σγ_odd = 88", S_odd, 88, note="= 2B·L₅ = F₁₁−1")
chk("Σγ_even = 90", S_even, 90, note="= 2B·L₅+μ² = F₁₁+1")
chk("E−O = 2 = μ² = B/2", S_even - S_odd, mu2)
chk("TrΔ = Σγ = 178 = 2F₁₁", S_odd + S_even, 2*Fib(11), note="= B²L₅+μ²")
S2_odd  = mp.fsum([g*g for g in g_odd])
S2_even = mp.fsum([g*g for g in g_even])
chk("Σγ_odd² = 264 = 6·N_d", S2_odd, 6*N_d)
chk("Σγ_even² = 272 = 6N_d+2B", S2_even, 6*N_d + 2*B)
chk("AP 方差 = 264/44 − 4 = 2 = μ²", S2_odd/44 - 4, mu2)
S3_odd  = mp.fsum([g**3 for g in g_odd])
S3_even = mp.fsum([g**3 for g in g_even])
chk("Σγ_odd³ = 880 = 5×176", S3_odd, 880)
chk("Σγ_even³ = 912 = 5×176+32", S3_even, 912)
T2 = mp.fsum([g*g for g in gamma])
chk("Tr(Δ²) = 536", T2, 536, note="= 4(TrΔ−N_d) = 4(h¹¹+h²¹) = 4(L₁₀+L₅)")
T3 = mp.fsum([g**3 for g in gamma])
chk("Tr(Δ³) = 1792 = 2⁸L₄", T3, 2**8 * L4)
T4 = mp.fsum([g**4 for g in gamma])
chk("Tr(Δ⁴) = 6288 = 48(L₉+F₁₀)", T4, 48*(Lucas(9)+Fib(10)))

print()
print("=" * 72)
print("B. 樹跡 (docs/09 §21.1, §23.2)")
print("=" * 72)
chk("L₅ = Tr(T̂⁵) = 11", Lucas(5), 11)
chk("L₁₀ = Tr(T̂¹⁰) = 123 = L₅²+μ²", Lucas(10), L5**2 + mu2, note="Lucas 倍角 L₂ₙ=Lₙ²−2(−1)ⁿ")
chk("L₁₀+L₅ = 134 = h¹¹+h²¹", Lucas(10)+Lucas(5), 134)
chk("F₁₁ = (T̂¹¹)₁₂ = 89", Fib(11), 89)
chk("L₂ = 3 = N_gen", Lucas(2), N_gen)
chk("L₃ = 4 = B", Lucas(3), B)
chk("T̂¹⁰ = [[89,55],[55,34]]", Tn(10)[1,0], 55)
chk("T̂⁵ = [[8,5],[5,3]]", Tn(5)[1,0], 5)
chk("L₆ = 18", Lucas(6), 18)
chk("L₄ = 7", Lucas(4), 7)

print()
print("=" * 72)
print("C. 301 編碼家族 (docs/09 §19.3, §20.1-20.2, §26.4, §27.3)")
print("=" * 72)
chk("(a) TrΔ+L₁₀ = 178+123", 178 + Lucas(10), 301)
chk("(b) L₄·43 = 7×43", L4*43, 301)
chk("(c) Tr(Δ²)/2+K_tree = 268+33", 536/2 + K_tree, 301)
chk("301 = (B+N_gen)(B·L₅−1) = 7×43", (B+N_gen)*(B*L5-1), 301)
chk("301 = B²L₅+L₅²+B = 176+121+4", B**2*L5 + L5**2 + B, 301)
chk("301 = N_gen³L₅+B = 27×11+4", N_gen**3*L5 + B, 301)
chk("301 = v_d·K_tree+B = 9×33+4", 9*K_tree + B, 301)
chk("301 = 4BL₅+L₅²+B = 176+121+4", 4*B*L5 + L5**2 + B, 301)
chk("301−B = 297 = v_d·K_tree = 9×33", 297, 9*K_tree)
chk("TrΔ = 4·43+2N_gen = 178", 4*43 + 2*N_gen, 178, note="邊界樞軸")
chk("L₁₀ = 3·43−2N_gen = 123", 3*43 - 2*N_gen, Lucas(10))
chk("43 = B·L₅−1 = 2F₅+K_tree = 10+33", 2*Fib(5)+K_tree, 43)

print()
print("=" * 72)
print("D. det 家族 + 特徵多項式求值 (docs/09 §21.4, §22, §24)")
print("=" * 72)
det_odd, det_even = prod(g_odd), prod(g_even)
chk("det_odd = 2 = μ² = γ₄₄", det_odd, mu2)
chk("det_even = 176 = 4N_d = B²L₅", det_even, B**2*L5)
chk("det(Δ) = det_even×det_odd = 352 = 2B·N_d", det_even*det_odd, 2*B*N_d)
chk("det_even/det_odd = 88 = 2N_d = 8L₅", det_even/det_odd, 88)
chk("TrΔ = det_even+det_odd (加性對偶)", det_even+det_odd, 178)
chk("det T̂¹⁰ = (−1)¹⁰ = 1", mp.mpf(Tn(10)[0,0]*Tn(10)[1,1] - Tn(10)[0,1]*Tn(10)[1,0]), 1)
def P_D(x):  return prod([x - g for g in gamma])
def P_odd(x): return prod([x - g for g in g_odd])
def P_even(x): return prod([x - g for g in g_even])
chk("P_Δ(1) = −3 = −N_gen", P_D(1), -N_gen, note="Chebyshev U₈₇(1/2) = −1")
chk("P_odd(1) = −1", P_odd(1), -1)
chk("P_even(1) = +3 = N_gen", P_even(1), N_gen)
chk("P_odd(μ²) = P_odd(B) = +2 = μ²", P_odd(mu2), mu2)
chk("P_Δ(μ²) = 0 (γ₄₄ 本徵值)", P_D(mu2), 0, note="γ₄₄ = 2 ∈ 譜")
chk("P_Δ(B) = 0 (γ₈₈ = 4 Nyquist)", P_D(B), 0)
chk("P_odd(1)·P_even(1) = −N_gen", P_odd(1)*P_even(1), -N_gen)
def R_sec(gs, n):
    Ln = Lucas(n)
    return prod([g*g - Ln*g + 1 for g in gs])
chk("R_odd(P_T̂²) = −1 (sector resultant)", R_sec(g_odd, 2), -1, note="§24.2 R_odd(−1)")
chk("R_even(P_T̂²) = +5", R_sec(g_even, 2), 5, note="§24.2 R_even(+5)")
chk("R_odd(P_T̂³) = +1", R_sec(g_odd, 3), 1, note="§24.2 R_odd(+1)")
chk("R_even(P_T̂³) = −3", R_sec(g_even, 3), -3, note="§24.2 R_even(−3)")
chk("乘積 n=2: R_odd×R_even = −F₅", R_sec(g_odd,2)*R_sec(g_even,2), -Fib(5))
chk("乘積 n=3: R_odd×R_even = −N_gen", R_sec(g_odd,3)*R_sec(g_even,3), -N_gen)

print()
print("=" * 72)
print("E. resultant 譜黏合 (docs/09 §23)")
print("=" * 72)
def Res(n):
    Ln = Lucas(n)
    return prod([g*g - Ln*g + 1 for g in gamma])
chk("R(P_Δ,P_T̂²) = −5 = −F₅", Res(2), -Fib(5))
chk("R(P_Δ,P_T̂³) = −3 = −N_gen", Res(3), -N_gen)
chk("ΣP_T̂⁵(γ_k) = −1334", mp.fsum([g*g - L5*g + 1 for g in gamma]), -1334)
chk("ΣP_T̂¹⁰(γ_k) = −21270", mp.fsum([g*g - Lucas(10)*g + 1 for g in gamma]), -21270)

print()
print("=" * 72)
print("F. 世代立方 / 樹強制 / 幾何生成 (docs/09 §26-28)")
print("=" * 72)
chk("N_gen = K_tree/L₅ = 3", K_tree/L5, N_gen, note="樹密度 = 世代數")
chk("K_tree = N_gen·L₅ = 33", N_gen*L5, K_tree)
chk("B²+L₅ = 27 = N_gen³", B**2 + L5, N_gen**3)
chk("v_d = N_gen² = 9", N_gen**2, 9)
chk("v_d = (L₅+L₄)/2 = 9", (L5+L4)/2, 9, note="Lucas 平均")
chk("v_d = (B²+μ²)/2 = 9", (B**2+mu2)/2, 9)
chk("L₅−L₄ = B = 4", L5-L4, B)
chk("μ² = B/2 = 2", mu2, B/2, note="Nyquist = 分支半數")
chk("2μ² = B (半分支合成)", 2*mu2, B)
chk("γ₄₄ = 4sin²(π/4) = 2", 4*mp.sin(mp.pi/4)**2, 2)
chk("k=44 唯一 (γ_k = B/2)", sum(1 for g in gamma if abs(g - 2) < 1e-30), 1)
chk("tanβ = N_gen³+B/L₅ = 301/11", N_gen**3 + B/L5, mp.mpf(301)/11)
chk("tanβ = v_d·(K_tree/L₅)+B/L₅", 9*(K_tree/L5) + B/L5, mp.mpf(301)/11)
chk("tanβ·L₅ = v_d·K_tree+B = 301", 9*K_tree + B, 301)
chk("v_u = v_d·tanβ = 2709/11 = 246.27", 9*mp.mpf(301)/11, mp.mpf(2709)/11)
chk("v_u = N_gen⁵+B·N_gen²/L₅ (修正後 mpf)", N_gen**5 + B*N_gen**2/L5, mp.mpf(2709)/11)
chk("tanβ = B²+L₅+B/L₅ (三層)", B**2 + L5 + B/L5, mp.mpf(301)/11)
chk("tanβ = 11+180/11 (兩項)", 11 + mp.mpf(180)/11, mp.mpf(301)/11)
chk("180 = B²L₅+B = B(BL₅+1) = 4×45 = TrΔ+μ² = 2Σγ_even", B**2*L5 + B, 180)
chk("45 = B·L₅+1 = C(10,2)", B*L5+1, 45)
chk("297/11 = 27 = N_gen³ (每樹跡世代立方)", mp.mpf(297)/11, N_gen**3)
chk("90 = 2×45 = 2(B·L₅+1)", S_even, 2*(B*L5+1))
chk("88 = 2×44 = 2N_d", S_odd, 2*N_d)
chk("90:88 = 45:44", mp.mpf(90)/88, mp.mpf(45)/44)

print()
print("=" * 72)
print("G. 多項式生成函數 (docs/09 §26-27, scripts/60)")
print("=" * 72)
chk("指數 {2,3,5} = {F₃,F₄,F₅}", Fib(3)*Fib(4)*Fib(5), 30)
def vd(t): return t**2
def tanb(t): return t**3 + B/L5
def vu(t): return t**2 * tanb(t)
chk("v_d(N_gen) = 3² = 9", vd(N_gen), 9)
chk("tanβ(N_gen) = 301/11", tanb(N_gen), mp.mpf(301)/11)
chk("v_u(N_gen) = t²·tanβ(t)", vu(N_gen), mp.mpf(2709)/11)
chk("v_u = t⁵+(B/L₅)t²", N_gen**5 + (B/L5)*N_gen**2, mp.mpf(2709)/11)
chk("tanβ(t=φ) = 4.59970 (非結構, C3 無命中)", tanb((1+mp.sqrt(5))/2), mp.mpf('4.599704341136153'), tol=1e-9)

print()
print("=" * 72)
print("H. 收縮候選證偽數字 (docs/09 §19.5)")
print("=" * 72)
mean_e, mean_o = S_even/44, S_odd/44
chk("⟨Δ⟩_even/⟨Δ⟩_odd = 1.0227", mean_e/mean_o, mp.mpf('1.0227272727'), tol=1e-6)
chk("Σγ_even²/Σγ_odd² = 1.0303", S2_even/S2_odd, mp.mpf('1.0303030303'), tol=1e-6)
chk("γ₂/γ₁ = 3.9987 (scripts/52 顯示)", gamma[1]/gamma[0], mp.mpf('3.998725651313983'), tol=1e-9)
chk("λ₊ = φ¹⁰ = 122.9919, λ₊+λ₋ = L₁₀", ((1+mp.sqrt(5))/2)**10 + ((1-mp.sqrt(5))/2)**10, Lucas(10))
chk("⚠️ λ₊/γ₄₄ = 61.4959 (docs §21.5 寫 61.5 係捨入 — 應 ≈61.50)", ((1+mp.sqrt(5))/2)**10 / 2, mp.mpf('61.495934690622114'), tol=1e-9, note="docs 發現: 61.5 唔 EXACT")
chk("λ₊/γ₈₈ = 30.748 (scripts/54 實際算式)", ((1+mp.sqrt(5))/2)**10 / 4, mp.mpf('30.747967345311057'), tol=1e-9, note="scripts/54 量級檢查用 γ₈₈=4")
chk("P_Δ(φ⁻¹⁰) ≈ 44.15 (0.34% form-grade)", abs(P_D(mp.mpf(1)/((1+mp.sqrt(5))/2)**10)), 44.15, tol=0.35, note="form-grade 唔宣稱")
# Π sin 解析確認 (§22.2)
p_odd_sin = prod([mp.sin((2*j+1)*mp.pi/176) for j in range(44)])
chk("Π sin((2j+1)π/176) = 2^−43.5", p_odd_sin, 2**mp.mpf('-43.5'))
p_even_sin = prod([mp.sin(k*mp.pi/88) for k in range(1,45)])
chk("Π sin(kπ/88) = √88·2^−43.5", p_even_sin, mp.sqrt(88)*2**mp.mpf('-43.5'))

print()
print("=" * 72)
print(f"RESULT: {PASS}/{PASS+FAIL} PASS  (docs/09 §19-28 + record rows 35-44 全量獨立重算)")
print("=" * 72)
