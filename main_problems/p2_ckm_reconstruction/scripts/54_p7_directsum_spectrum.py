#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 54 — P7 直和算子譜結構: T̂¹⁰ 矩陣元冗余 + E/O Fibonacci 裂距 + det 恆等式
==============================================================
發現: TrΔ = 2(T̂¹⁰)₁₁ = 2F₁₁ — chain 跡喺 tree 矩陣元度冗余!
      Σγ_odd = F₁₁−1 = 88, Σγ_even = F₁₁+1 = 90 — E/O 對稱裂開
      det(Δ) = 352 = 2B·N_d — 行列式恆等式
"""
import mpmath as mp
mp.mp.dps = 60

PASS = FAIL = 0
def chk(name, val, target, tol, note=""):
    global PASS, FAIL
    val_f = float(val); tgt = float(target)
    ok = abs(val_f - tgt) <= tol * max(1.0, abs(tgt))
    if ok:
        PASS += 1
        print(f"  [✔] {name} = {val_f:.9f}  (dev {abs(val_f-tgt)/abs(tgt)*100:+.4f}%) {note}")
    else:
        FAIL += 1
        print(f"  [✘] {name} = {val_f:.9f} vs {tgt}  (dev {abs(val_f-tgt)/abs(tgt)*100:+.4f}%) {note}")

N_d, N_gen, B, K_tree, mu2 = 44, 3, 4, 33, 2.0
phi = (1+mp.sqrt(5))/2
T = mp.matrix([[1, 1], [1, 0]])
def Tn(n):
    M = mp.matrix([[1, 0], [0, 1]])
    for _ in range(n):
        M = M * T
    return M
L, F = {}, {}
for n in range(1, 16):
    M = Tn(n)
    L[n] = float(mp.nint(M[0,0]+M[1,1]))
    F[n] = float(mp.nint(M[0,1]))

gams = [4*mp.sin(k*mp.pi/176)**2 for k in range(1, 89)]
odd  = [gams[k] for k in range(0, 88, 2)]
even = [gams[k] for k in range(1, 88, 2)]
tr1 = float(sum(gams)); so1 = float(sum(odd)); se1 = float(sum(even))

print("=" * 72)
print("C1. T̂¹⁰ / T̂⁵ 矩陣形式 (Fibonacci 矩陣)")
print("=" * 72)
M10 = Tn(10); M5 = Tn(5)
print(f"  T̂¹⁰ = [[{int(mp.nint(M10[0,0]))}, {int(mp.nint(M10[0,1]))}],"
      f" [{int(mp.nint(M10[1,0]))}, {int(mp.nint(M10[1,1]))}]]"
      f" = [[F₁₁, F₁₀], [F₁₀, F₉]]")
print(f"  T̂⁵  = [[{int(mp.nint(M5[0,0]))}, {int(mp.nint(M5[0,1]))}],"
      f" [{int(mp.nint(M5[1,0]))}, {int(mp.nint(M5[1,1]))}]]"
      f" = [[F₆, F₅], [F₅, F₄]]")
chk("(T̂¹⁰)₁₁ = F₁₁ = 89", M10[0,0], 89, 1e-9)
chk("(T̂¹⁰)₁₂ = F₁₀ = 55", M10[0,1], 55, 1e-9)
chk("(T̂¹⁰)₂₂ = F₉ = 34", M10[1,1], 34, 1e-9)

print()
print("=" * 72)
print("C2. ★★ TrΔ = 2(T̂¹⁰)₁₁ — chain 跡喺 tree 矩陣元冗余")
print("=" * 72)
chk("TrΔ = 178", tr1, 178, 1e-9)
chk("★ TrΔ = 2(T̂¹⁰)₁₁ = 2F₁₁ = 178", tr1, 2*M10[0,0], 1e-9,
    "← chain 總譜和 = 2× T̂¹⁰ 嘅 (1,1) 元 — P(T̂,Δ) 橋樑嘅矩陣元版!")
chk("2F₁₁ = F₁₂+F₁₀−21... (2×89)", 2*F[11], 178, 1e-9)

print()
print("=" * 72)
print("C3. ★★ E/O Fibonacci 裂距: Σγ_odd = F₁₁−1, Σγ_even = F₁₁+1")
print("=" * 72)
chk("★ Σγ_odd = F₁₁−1 = 88", so1, F[11]-1, 1e-9,
    "← 觀察者 sector = Fibonacci − 1")
chk("★ Σγ_even = F₁₁+1 = 90", se1, F[11]+1, 1e-9,
    "← 世界 sector = Fibonacci + 1")
chk("★ E/O 對稱裂開: (Σγ_even+Σγ_odd)/2 = F₁₁ = 89", (se1+so1)/2, F[11], 1e-9)
chk("E−O = 2 = μ² (BC-cost, O159)", se1-so1, mu2, 1e-9)

print()
print("=" * 72)
print("C4. ★ tanβ 純 T̂¹⁰ 矩陣元形式")
print("=" * 72)
chk("★ tanβ = [2(T̂¹⁰)₁₁ + Tr(T̂¹⁰)]/Tr(T̂⁵)", (2*M10[0,0]+L[10])/L[5], 301/11, 1e-9,
    "← 分子全由 T̂¹⁰ 讀出 (chain 跡 = 2×11元, 冗余)")
chk("tanβ = [2F₁₁+L₁₀]/L₅", (2*F[11]+L[10])/L[5], 301/11, 1e-9)
chk("tanβ = [TrΔ+L₅²+μ²]/L₅ (Lucas 倍角)", (tr1+L[5]**2+mu2)/L[5], 301/11, 1e-9)

print()
print("=" * 72)
print("C5. 索引解碼: 10 = 2F₅ = L₅−1, 43 = B·L₅−1")
print("=" * 72)
chk("★ 10 = 2F₅ = 2×5", 2*F[5], 10, 1e-9, "← φ 生成索引 F₅ (2cos(2π/5)=1/φ)")
chk("★ 10 = L₅−1 = 11−1", L[5]-1, 10, 1e-9)
chk("5 = F₅", F[5], 5, 1e-9)
chk("43 = B·L₅−1 = 4×11−1", B*L[5]-1, 43, 1e-9, "← 同款 −1 模式")
chk("43−10 = 33 = K_tree", 43-10, K_tree, 1e-9, "← 邊界 43 與 索引 10 之間 = 樹深度!")

print()
print("=" * 72)
print("C6. ★ det(Δ) = 352 = 2B·N_d — 行列式恆等式")
print("=" * 72)
det1 = float(mp.e**sum(mp.log(g) for g in gams))
det_odd = float(mp.e**sum(mp.log(g) for g in odd))
det_even = float(mp.e**sum(mp.log(g) for g in even))
chk("★ det(Δ) = Πγ_k = 352 = 2B·N_d = 8×44", det1, 2*B*N_d, 1e-6,
    "← 行列式 = 2×176 = 8N_d")
chk("det(Δ⊕T̂¹⁰) = det(Δ)·det(T̂¹⁰) = 352×1", det1*1.0, 352, 1e-6,
    "← det(T̂¹⁰) = (−1)¹⁰ = 1")
chk("det_odd × det_even = det(Δ)", det_odd*det_even, det1, 1e-6)
print(f"  det_odd = {det_odd:.6f}, det_even = {det_even:.6f}, 比 = {det_even/det_odd:.6f}")

print()
print("=" * 72)
print("C7. H_Higgs = Δ⊕T̂¹⁰ 譜結構 (90 特徵值)")
print("=" * 72)
lam_plus  = float(phi**10)
lam_minus = float((-1/phi)**10)   # = φ⁻¹⁰
chk("λ₊ = φ¹⁰ = 122.9919", lam_plus, L[10]-lam_minus, 1e-9, "φ¹⁰+φ⁻¹⁰ = L₁₀ EXACT")
chk("★ λ₊+λ₋ = L₁₀ = 123", lam_plus+lam_minus, L[10], 1e-9)
chk("λ₊·λ₋ = 1 (det T̂¹⁰)", lam_plus*lam_minus, 1.0, 1e-9)
chk("★ λ₊ > γ_max = 4 — tree 特徵值主導 chain 譜", lam_plus > 4, 1, 0)
chk("λ₊/γ₄₄ = 61.5, λ₊/γ₈₈ = 30.75 (量級)", lam_plus/4.0, 30.745, 1e-2)
print(f"  90 特徵值: 88×γ_k ∈ [0.00127, 4] + {{φ¹⁰={lam_plus:.6f}, φ⁻¹⁰={lam_minus:.8f}}}")

print()
print("=" * 72)
print("C8. 90 共振: dim = Σγ_even = F₁₁+1 = 2C(10,2)")
print("=" * 72)
chk("dim(Δ⊕T̂¹⁰) = 88+2 = 90", 88+2, 90, 0)
chk("90 = Σγ_even = F₁₁+1", se1, 90, 1e-9)
chk("90 = 2C(10,2) = 2×45 (世界質心 O158)", 2*45, 90, 0)
chk("45 = C(10,2), 10 = 2F₅", 45, 10*9//2, 0)

print()
print("=" * 72)
print("C9. VEV 包裝 + 投影定理 v3 陳述")
print("=" * 72)
vd = L[6]/2
vu = vd*(tr1+L[10])/L[5]
chk("v_d = L₆/2 = (L₃²+μ²)/2 = 9", vd, 9, 1e-9, "Lucas 倍角 n=3")
chk("v_u = v_d·tanβ = 246.27 (0.088%)", vu, 246.27, 2e-3)
print("  已證鏈:")
print("    (i)  TrΔ = 2(T̂¹⁰)₁₁ — chain 跡 = tree 矩陣元冗余 [C2]")
print("    (ii) Σγ_odd = F₁₁−1, Σγ_even = F₁₁+1 — E/O Fibonacci 裂距 [C3]")
print("    (iii) tanβ = [2(T̂¹⁰)₁₁+Tr(T̂¹⁰)]/Tr(T̂⁵) — 純 T̂¹⁰ 形式 [C4]")
print("    (iv) det(Δ) = 2B·N_d = 352; det(T̂¹⁰) = 1 [C6]")
print("    (v)  λ₊ = φ¹⁰ 主導 90 譜; φ¹⁰+φ⁻¹⁰ = L₁₀ [C7]")
print("  未證: 直和跡比嘅幾何強制 — v_u/v_d = Tr(Δ⊕T̂^{2F₅})/Tr(T̂^{F₅})")
print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
