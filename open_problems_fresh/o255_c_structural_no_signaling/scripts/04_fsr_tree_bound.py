#!/usr/bin/env python3
"""
O255 scripts/04 — FSR 精化層 v_g 上界 + K_Tree 樹狀譜上界
=========================================================
預註冊 (2026-10-20 Round 2, 跑前凍結):

F1  精化層 N_ℓ = 44·4^ℓ (O140): 每層譜 γ_n(N_ℓ) = 4sin²(πn/N_ℓ)
    ⟹ v_g(n) = cos(πn/N_ℓ) ≤ 1, 等號唯一 n=0 — c 上限層級不變
F2  最低非零模速度 v_g(1; N_ℓ) = cos(π/N_ℓ) → 1 由下逼近 (ℓ→∞,
    SR 連續極限): 有質量模 v<c 喺一切精化層嚴格
F3  O140 速度階梯: v_n = c·cos(πn/88) ≡ 我哋嘅 v_g(n) — FSR 階梯就係
    群速度階梯; Lorentz 階梯 γ_L(n) = csc(πn/88) = 2/√γ_n EXACT
    (γ_n/4 = sin² = 1/csc² = 1/γ_L²)
F4  自對偶模統一: 鏈 n=22 (γ₂₂=2) 同 樹 c=17 (λ₁₇=2=μ², O160) 都係
    v_g = cos(π/4) = 1/√2 = c/√2 — O140 v_22 = c/√2 命題
F5  K_Tree Dirichlet 譜: λ_c = 4sin²(cπ/68), c=0..33, ω_c = 2sin(cπ/68),
    v_g(c) = cos(cπ/68) ≤ 1, 等號唯一 c=0 (樹根 Goldstone)
F6  Σλ = 66 = 2K_tree (O160) 重現; 半整數 shift 層 (2N_ℓ denominator)
    v_g ≤ 1 照舊

執行: /usr/bin/python3 scripts/04_fsr_tree_bound.py > logs/04.txt 2>&1
"""
import math

TOL = 1e-12
checks = []
def chk(name, cond, note=""):
    checks.append((name, bool(cond), note))

def vg(N, n):
    return math.cos(math.pi * n / N)

# F1: 精化層 N_ℓ = 44·4^ℓ, ℓ=0..8 (88 係 44·2, 有 ℓ=0.5? — 用 N ∈ {44·4^ℓ} 官方)
def gap_of(N):
    """1 − cos(π/N) = 2sin²(π/2N) — 半角形式, 小 gap 可精確表示 (唔受 float epsilon 困死)"""
    return 2.0 * math.sin(math.pi / (2.0 * N)) ** 2

for ell in range(0, 9):
    Nl = 44 * 4 ** ell
    g = gap_of(Nl)
    # v_g(0) = 1 精確
    chk(f"F1.l{ell}.gold", abs(vg(Nl, 0) - 1.0) < TOL, f"N_ℓ={Nl} n=0 v_g=1")
    # 所有 n≥1 嚴格低於 1, 且差距 ≥ gap(1) (最接近 1 嘅模係 n=1, 差距 = g)
    for n in range(1, Nl // 2 + 1):
        gap = 1.0 - vg(Nl, n)
        chk(f"F1.l{ell}.n{n}", gap >= 0.99 * g, f"N_ℓ={Nl} v_g({n})={vg(Nl,n):.15f} gap={gap:.3e}")

# F2: v_g(1; N_ℓ) → 1 由下逼近 — gap(N_ℓ) = 1−cos(π/N_ℓ) = 2sin²(π/2N_ℓ) > 0 且單調收縮
for ell in range(0, 9):
    Nl = 44 * 4 ** ell
    g = gap_of(Nl)
    v1 = math.cos(math.pi / Nl)
    chk(f"F2.l{ell}", g > 0.0 and v1 < 1.0 - 0.9 * g,
        f"N_ℓ={Nl} v_g(1)={v1:.15f} gap={g:.3e} (嚴格 <c)")
    if ell > 0:
        chk(f"F2.l{ell}.mono", g < gap_of(44 * 4 ** (ell - 1)), "gap 單調收縮 (由下逼近)")
chk("F2.limit", gap_of(44 * 4 ** 20) < 1e-25,
    "ℓ→∞ SR 連續極限: gap→0 (v_g(1)→c 由下)")

# F3: O140 速度階梯 ≡ v_g; Lorentz 階梯 csc = 2/√γ
for n in range(1, 45):
    v_fsr = math.cos(math.pi * n / 88)          # O140 v_n = c·cos(πn/88)
    gamma_c = 4.0 * math.sin(math.pi * n / 88) ** 2   # K_Chain γ_n
    vg_n = vg(88, n)
    chk(f"F3.ladder.n{n}", abs(v_fsr - vg_n) < TOL, "FSR 速度階梯 = v_g")
    gamL = 1.0 / math.sin(math.pi * n / 88)     # O140 Lorentz csc
    chk(f"F3.lorentz.n{n}", abs(gamL - 2.0 / math.sqrt(gamma_c)) < 1e-9,
        f"γ_L(n)=csc=2/√γ_n: {gamL:.9f}")
    # SR 恆等: 1/γ_L² + (v/c)² = 1 ⇔ sin²+cos²=1
    chk(f"F3.sr.n{n}", abs(1.0 / gamL ** 2 + vg_n ** 2 - 1.0) < 1e-12,
        "SR 恆等 sin²+cos²=1 (速度-Lorentz 關係 EXACT)")
# 極端: n=22 → γ_L=√2, v=c/√2
chk("F3.n22", abs(1.0 / math.sin(22 * math.pi / 88) - math.sqrt(2.0)) < 1e-12,
    "n=22: γ_L=√2, v_g=c/√2")

# F4: 自對偶模統一 — 鏈 n=22 v_g=c/√2; 樹 c=17 v_g=c/√2
vg_chain22 = math.cos(22 * math.pi / 88)
vg_tree17 = math.cos(17 * math.pi / 68)
chk("F4.chain22", abs(vg_chain22 - 1.0 / math.sqrt(2.0)) < 1e-12, f"鏈 n=22 v_g={vg_chain22:.12f}")
chk("F4.tree17", abs(vg_tree17 - 1.0 / math.sqrt(2.0)) < 1e-12, f"樹 c=17 v_g={vg_tree17:.12f}")
chk("F4.equal", abs(vg_chain22 - vg_tree17) < 1e-12, "雙自對偶模同一速度 c/√2")
# λ₁₇ = 2 = μ² 重現
chk("F4.lam17", abs(4.0 * math.sin(17 * math.pi / 68) ** 2 - 2.0) < 1e-12, "λ₁₇=μ²=2")

# F5: K_Tree Dirichlet 譜 c=0..33 (c=0 Goldstone, c=1..33 O160 S3)
for c in range(0, 34):
    v = math.cos(c * math.pi / 68)
    chk(f"F5.c{c}", v <= 1.0 + TOL, f"樹 v_g({c})={v:.12f}")
chk("F5.unique", sum(abs(math.cos(c * math.pi / 68) - 1.0) < TOL for c in range(1, 34)) == 0,
    "樹譜唯一 Goldstone 喺 c=0")
# 樹頻率 ω_c monotic: c=1..33 ω 升 (Γ=4sin², sin 喺 (0,π/2) 升)
for c in range(1, 33):
    t = 2.0 * math.sin(c * math.pi / 68)
    t2 = 2.0 * math.sin((c + 1) * math.pi / 68)
    chk(f"F5.mono.c{c}", t2 > t, "樹 ω_c 單調升")

# F6: Σλ = 66 = 2K_tree (O160) + 半整數 shift 層
sl = sum(4.0 * math.sin(c * math.pi / 68) ** 2 for c in range(1, 34))
chk("F6.treesum", abs(sl - 66) < 1e-9, f"Σλ={sl:.12f} = 2K_tree (66)")
# 半整數 shift: 2N_ℓ denominator (O159 176-Laplacian 推廣)
for ell in range(0, 5):
    N2 = 2 * 44 * 4 ** ell
    for n in range(1, N2 // 2 + 1):
        v = math.cos(n * math.pi / N2)
        chk(f"F6.half.l{ell}.n{n}", abs(v) <= 1.0 + TOL, f"2N_ℓ={N2} |v_g|≤1")

npass = sum(1 for _, c, _ in checks if c)
nfail = len(checks) - npass
print(f"[結果] 精化層 N_ℓ=44·4^ℓ (ℓ=0..8): v_g≤1 每層成立, 唯一 n=0, v_g(1)→c 由下逼近 (SR ℓ→∞)")
print(f"[結果] O140 速度階梯 v_n=c·cos(πn/88) ≡ v_g; Lorentz 階梯 γ_L=csc=2/√γ_n EXACT; SR 恆等 sin²+cos²=1")
print(f"[結果] 自對偶模統一: 鏈 n=22 同樹 c=17 (λ₁₇=μ²) 都 v_g=c/√2 (O140 v_22=c/√2 確認)")
print(f"[結果] K_Tree 樹狀譜: v_g(c)=cos(cπ/68)≤1, 唯一 c=0; Σλ=66=2K_tree")
print(f"[結果] 半整數 shift 層 (2N_ℓ) v_g≤1 照舊")
print(f"\n結果: {npass}/{len(checks)} PASS")
for name, c, note in checks:
    if not c:
        print(f"  FAIL {name}: {note}")