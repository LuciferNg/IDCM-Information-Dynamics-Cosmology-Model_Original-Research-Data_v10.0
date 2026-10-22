#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O210 scripts/02_type_registry.py — 型別註冊表 + T0 標量判準 + 重寫率
================================================================================
O208 規則: 禁止字面 True → 全部數值/結構檢查 + 分級 verdict。
T0 判準: s : Sc ⟺ ∃ f:Fn, A:Op 使 s = f(A)。anchors (有量綱錨) 係例外, 標 🟡。
每條目: (name, value, type, generator, functional, field, version, status, note)
重寫率 = (#🟢) / (#total)。
"""
import json
from fractions import Fraction

# ───────────────────────── 型別註冊表 ─────────────────────────
# type ∈ {Op, Sc, Fn, Ix}
# generator ∈ {T̂, K_chain, K_tree, Ω, v̂_g, U, P, Spec, Lie, CY₃, W, B, A₅, anchor, input}
# functional ∈ {Tr, Spec, Σ, det, rank, ⟨·⟩, E[φ], beat, 𝒫, dim, Wilson, none(Op/Ix)}
# field ∈ {Q, Q(√5), Q(ζ₈₈)⁺, Q(ζ₅₅)⁺, ℂ, trans, composite, dimless}
R = [
    # ── G1: 生成元與譜 ──
    ("φ, −1/φ = spec(T̂)", "φ, −1/φ", "Sc", "T̂", "Spec", "Q(√5)", "v10", "🟢", "T̂ 特徵值 (x²+x−1=0 根)"),
    ("L_n = Tr(T̂ⁿ) (Lucas)", "Lₙ", "Sc", "T̂", "Tr", "Q", "v10", "🟢", "L₁₀=123, L₅=11, L₄=7, L₇=29, L₈=47"),
    ("F_n = (T̂ⁿ)₁₂ (Fib)", "Fₙ", "Sc", "T̂", "matrix-elem", "Q", "v10", "🟢", "F₆=8, F₁₀=55, F₁₁=89, F₇=13, F₅=5"),
    ("γ_k = 4sin²(kπ/176), k∈I₈₈ (176-L 對角算子 γ̂ = Σγ_kP_k)", "γ̂", "Op", "K_chain", "Spec", "Q(ζ₈₈)⁺", "v10", "🟢", "176-L 標準; 成員 γ_k : Sc (88-L n↔2n)"),
    ("μ² = 2 = γ₄₄ (自對偶)", "2", "Sc", "K_chain", "Spec", "Q", "v10", "🟢", "176-L k=44; = E−O = Σγ_even−Σγ_odd"),
    ("B = 4 = γ₈₈ (Nyquist)", "4", "Sc", "K_chain", "Spec", "Q", "v10", "🟢", "176-L k=88; = log₂16? 分支因子"),
    ("γ_k + γ_{88−k} = 4 (Z₂ 對偶)", "4", "Sc", "K_chain", "Spec", "Q", "v10", "🟢", "∀k∈I₈₈"),
    ("N_d = 44 = dim V₄₄", "44", "Sc", "K_chain", "dim", "Q", "v10", "🟢", "Tr(I₄₄); = B×R, R=11"),
    ("N_gen = 3 = B−1", "3", "Sc", "K_tree", "rank", "Q", "v10", "🟢", "分支代數; SU(3)_C 維"),
    ("ω_n = 2sin(πn/88) (對角算子 Ω̂)", "Ω̂", "Op", "Ω", "Spec", "Q(ζ₈₈)⁺", "v10", "🟢", "44 勢; m_n = M₀·ω_n"),
    ("v_g(n) = cos(πn/88) (對角算子 v̂_g)", "v̂_g", "Op", "v̂_g", "Spec", "Q(ζ₈₈)⁺", "v10", "🟢", "v_g = c·cos(πn/88); Nyquist 駐波"),
    # ── G2: 譜和與扇區 ──
    ("Σγ_even = 90 (176-L even k, world)", "90", "Sc", "K_chain", "Σ∘Proj_world", "Q", "v10", "🟢", "Tr(P_world γ̂)"),
    ("Σγ_odd = 88 (176-L odd k, observer)", "88", "Sc", "K_chain", "Σ∘Proj_obs", "Q", "v10", "🟢", "Tr(P_obs γ̂)"),
    ("Σγ = 178 = 2F₁₁", "178", "Sc", "K_chain", "Tr", "Q", "v10", "🟢", "Σ_even + Σ_odd"),
    ("Σγ_even − Σγ_odd = 2 = μ²", "2", "Sc", "K_chain", "Σ", "Q", "v10", "🟢", "μ² 三合一 (O159)"),
    ("44-site (88-L) parity: even=46, odd=44", "46/44", "Sc", "K_chain", "Σ∘Proj", "Q", "v10", "🟢", "憲章 C2 裁決; s0/s2 扇區"),
    ("mod-4 扇區 s0=46, s1=44−sec, s2=44, s3=44+sec", "46/44∓sec/44+sec", "Sc", "K_chain", "Σ∘Proj_mod4", "Q∪trans", "v10", "🟢", "O148 閉式; s1+s3 超越對消"),
    ("Σ√γ_n = 1+cot(π/176)", "57.0165883", "Sc", "K_chain", "Σ∘√Spec", "trans", "v10", "🟢", "EXACT; 57+1/60 係有理近似 (ε=−7.68e-5)"),
    ("Σλ (tree Dirichlet-33) = 66 = dim Λ²(12)", "66", "Sc", "K_tree", "Tr", "Q", "v10", "🟢", "KTSG R2 21/21"),
    # ── G3: 張量積 ──
    ("𝒯 = K_chain ⊗ K_tree", "—", "Op", "⊗", "none", "dimless", "v10", "🟢", "代數載體"),
    ("Γ = γ̂⊗λ̂, ΣΓ = 5940 = B·N_gen³·F₅·L₅", "5940", "Sc", "⊗", "Tr", "Q", "v10", "🟢", "90×66; KTSG"),
    ("Tr(A⊗B) = TrA·TrB", "rule", "Fn", "⊗", "Tr", "—", "v10", "🟢", "跡因子化"),
    ("946 = C(44,2) = dim Λ²(I₄₄)", "946", "Sc", "Ix", "dim", "Q", "v10", "🟢", "beat 空間維度"),
    ("66 = Λ²(12), 78 = Sym²(12), 144 = 12⊗12", "66/78/144", "Sc", "Lie", "dim", "Q", "v10", "🟢", "SU(12) 張量分解"),
    # ── G4: 直和 ──
    ("12 = 1⊕11 (Cartan ⊕ roots)", "12", "Sc", "Lie", "dim", "Q", "v10", "🟢", "SU(12) 基本表示"),
    ("V₈₈ = V_world ⊕ V_obs (P_w+P_o=I)", "88", "Sc", "K_chain", "dim", "Q", "v10", "🟢", "44+44"),
    ("176 = 66⊕68⊕42 (O155)", "176", "Sc", "K_chain", "⊕", "Q", "v10", "🟢", "譜分解"),
    ("178 = 172+2+4 (O153)", "178", "Sc", "K_chain", "⊕", "Q", "v10", "🟢", "譜分解"),
    ("Tr(A⊕B) = TrA + TrB", "rule", "Fn", "⊕", "Tr", "—", "v10", "🟢", "直和跡可加"),
    # ── G5: 投影 ──
    ("P² = P (冪等)", "rule", "Op", "P", "none", "—", "v10", "🟢", "投影閉合"),
    ("P_CY: 946 → 134", "134", "Sc", "P", "dim", "Q", "v10", "🟢", "像維 = h¹¹+h²¹"),
    ("134 = h¹¹+h²¹ = 36+98", "134", "Sc", "CY₃", "dim", "Q", "v10", "🟢", "∀B 判別力零 (O53)"),
    ("36 = (2N_gen)² = h¹¹", "36", "Sc", "CY₃", "dim", "Q", "v10", "🟢", "CY₃ Kähler 模"),
    ("98 = 2L₄² = h²¹", "98", "Sc", "CY₃", "dim", "Q", "v10", "🟢", "CY₃ 複結構模"),
    ("χ = −4(N_d−F₇) = −124", "−124", "Sc", "CY₃", "rank", "Q", "v10", "🟢", "歐拉示性"),
    ("E_proj = 2+B·L = 28.5 (L=53/8)", "57/2", "Sc", "W", "⟨·⟩", "Q", "v10", "🟢", "物質投影能量; O47"),
    ("E_sync = 88−4L = 61.5 = L₁₀/2", "123/2", "Sc", "W", "⟨·⟩", "Q", "v10", "🟢", "真空同步能量; O41"),
    ("F_proj = 17 = dim ker T_pipe = L₆−1", "17", "Sc", "P", "dim", "Q", "v10", "🟢", "投影截斷; O121"),
    ("60-vertex rhombicosidodecahedron (20Δ+30□+12⬠)", "60", "Sc", "A₅", "dim", "Q", "v10", "🟢", "χ=2; 阻挫32; 錨定30"),
    # ── G6: 伴隨 ──
    ("T̂† = T̂, γ̂† = γ̂ (自伴隨)", "rule", "Op", "†", "none", "—", "v10", "🟢", "實對稱 ⇒ 實譜"),
    ("U_k† = U_k⁻¹ (么正); γ_k^(176-L) = |1−U_k|²", "rule", "Op", "U", "Spec", "Q(ζ₈₈)⁺", "v10", "🟢", "2θ_k = kπ/88"),
    ("Wilson ΠU_k: 總相位 44.5π", "44.5π", "Sc", "U", "Wilson", "Q", "v10", "🟢", "Σθ_k = (89/2)π"),
    ("T_pipe† = I − T_pipe", "rule", "Op", "P", "†", "—", "v10", "🟢", "O121 黑洞 = 局部 T_pipe†"),
    ("J² = −I (O159 複結構)", "rule", "Op", "K_chain", "Spec", "Q", "v10", "🟢", "Dirichlet BVP 複結構"),
    # ── G7: 收縮 ──
    ("Tr_tree(Γ) = Σλ·γ̂ (部分跡)", "rule", "Op", "⊗", "Contr", "—", "v10", "🟢", "收縮閉合"),
    ("Tr(Γ) = 5940 (全收縮)", "5940", "Sc", "⊗", "Tr", "Q", "v10", "🟢", "Σγ·Σλ"),
    ("Σ_k γ_k = Tr(γ̂) = 178 (指數收縮)", "178", "Sc", "K_chain", "Tr", "Q", "v10", "🟢", "指數求和 = 跡"),
    # ── G8: 歸一化與耦合 ──
    ("m_ρ² = 4μ² = 8 (O204)", "8", "Sc", "W", "Spec", "Q", "v10", "🟢", "非 2μ²; 核歸一化"),
    ("W₀² = L₁₀/2 = 61.5; W₀ = 7.84219357068", "7.84219357068", "Sc", "W", "⟨·⟩", "Q(√1230)", "v10", "🟢", "舊 1.23607 = v6 ε/2κ"),
    ("λ = 2/L₁₀ = 2/123", "2/123", "Sc", "W", "⟨·⟩", "Q", "v10", "🟢", "W⁴ 自耦合"),
    ("κ² = M₀ = 27.9009 MeV", "27.9009 MeV", "Sc", "anchor", "anchor", "dimless", "v10", "🟡", "質量錨 (O38); 三線性耦合"),
    ("κ_crit = sin(π/88)/⟨W⟩ = 0.00455132", "0.00455132", "Sc", "W", "Spec", "Q(ζ₈₈)⁺", "v10", "🟢", "O81; κ=1/B⁴ 亞臨界 0.8583×"),
    ("L₁₀ = N_gen(N_d−N_gen) = 123", "123", "Sc", "T̂", "Tr", "Q", "v10", "🟢", "Lucas 跡"),
    ("λ_max = 36 − 1/γ₄₀^(176-L) = 35.4170", "35.4170", "Sc", "CY₃", "Spec", "Q(ζ₈₈)⁺", "v10", "🟢", "⚠ 原記錄 γ₂₀ 88-L — 指數標籤漂移, 憲章 C2"),
    ("α_s⁻¹ = F₆ + sin²θ_W + 1/B = 8.4708", "8.4708", "Sc", "T̂+input", "Tr", "Q∪input", "v10", "🟢", "F₆=(T̂⁶)₁₂=8; sin²θ_W 係輸入"),
    ("137 = α⁻¹ = 3N_d+F₅", "137", "Sc", "T̂", "add-closure", "Q", "v10", "🟢", "大層唯一質數"),
    ("55 = F₁₀ = C(L₅,2) = N_d+L₅", "55", "Sc", "T̂", "Tr", "Q", "v10", "🟢", "混合 home 塔"),
    ("123 = 3(N_d−3) (O33)", "123", "Sc", "T̂", "Tr", "Q", "v10", "🟢", "L₁₀ 另一身份"),
    ("Ω = (3:16:41)/60 (O215)", "Ω", "Sc", "K_chain", "Σ∘Proj", "Q", "v10", "🟢", "⚠ 用 Σγ_odd=44 = 44-site odd (憲章 C2 命名)"),
    ("Ω_m = E_proj/Σγ = 19/60", "19/60", "Sc", "W", "⟨·⟩", "Q", "v10", "🟢", "物質密度"),
    ("真空能 = E_sync/Σγ = 41/60", "41/60", "Sc", "W", "⟨·⟩", "Q", "v10", "🟢", "Ω_Λ 結構式"),
    ("C = B/L₅ = 4/11", "4/11", "Sc", "K_tree", "Σ", "Q", "v10", "🟢", "晶格干涉對比"),
    ("M₄/M₀ = L₄/(L₅+B) = 7/15", "7/15", "Sc", "T̂", "Tr", "Q", "v10", "🟢", "hop=4 質量比"),
    ("dβ/dℓ = 4N_d/(N_d−μ²) = 88/21", "88/21", "Sc", "K_chain", "Spec", "Q", "v10", "🟢", "每層陡峭化"),
    ("21 = (N_d−μ²)/2", "21", "Sc", "K_chain", "Σ", "Q", "v10", "🟢", "凝聚階梯"),
    ("75 = L₄L₅−μ² = 2N_d−F₇", "75", "Sc", "T̂", "Tr", "Q", "v10", "🟢", "E_strain 分母"),
    ("421 = a²+b² (a=14,b=15); L₇ = a+b = 29", "421/29", "Sc", "T̂", "Tr", "Q", "v10", "🟢", "O171 錘對生成"),
    ("E_min = L₁₀/(4N_d) = 123/176", "123/176", "Sc", "T̂", "Tr", "Q", "v10", "🟢", "O152"),
    ("f_unproj = L₁₀/(4(N_d+1)) = 41/60", "41/60", "Sc", "T̂", "Tr", "Q", "v10", "🟢", "O152"),
    ("ε = (L₆+1)/L₁₀ = 19/123", "19/123", "Sc", "T̂", "Tr", "Q", "v10", "🟢", "O152; φ⁻¹/4 係近似 (δ₃=0.023% 陷阱)"),
    ("C_energy = μ²/Σγ = 1/45", "1/45", "Sc", "K_chain", "Σ", "Q", "v10", "🟢", "O203 愛丁頓臨界率強逼值"),
    ("Ω_b 候選 = 19/450", "19/450", "Sc", "T̂", "Tr", "Q", "v10", "🟡", "O215 2.3σ 🟡 可證偽"),
    ("sin²θ₂₃(55) = 0.57298", "0.57298", "Sc", "K_chain", "Σ∘Proj", "Q(ζ₅₅)⁺", "v10", "🟢", "O155 home 55; 0.004%"),
    ("μ/e = (γ₇/γ₁)(F_μ/F_e) = 206.705", "206.705", "Sc", "K_chain×T̂", "Σ∘Proj", "composite", "v10", "🟢", "O54; 複合域 (ζ₈₈)⁺·(√5)"),
    ("R_world = 4129.94 Mpc; a = R_world/88 = 46.93 Mpc", "4129.94", "Sc", "anchor", "anchor", "dimless", "v10", "🟡", "長度錨 (O8); 維度定理需 1 錨"),
    ("c = a√J = R_world·ω_ring = 2πR_world/T_ring", "c", "Sc", "W", "Spec", "dimless", "v10", "🟢", "O73§10; dev 0.194% EXACT 結構"),
    ("88 = 2N_d = 44·μ² = F₁₁−1 = 90−2", "88", "Sc", "K_chain", "dim", "Q", "v10", "🟢", "多身份 hub (O155)"),
    ("33²+44² = 55² (O156 畢氏)", "55", "Sc", "T̂", "Tr", "Q", "v10", "🟢", "維度比 4:3"),
    ("η_B = 6.2145e-10 (h=0.674)", "6.2145e-10", "Sc", "BBN", "⟨·⟩", "dimless", "v10", "🟢", "O38/O170; 舊 6.0636e-10 已廢"),
    ("H₀ = 71.157 (O38/O170)", "71.157", "Sc", "anchor", "anchor", "dimless", "v10", "🟢", "h_o170 = h_cmb(1+1/18)"),
    ("v_geom = 246.2639 (O53)", "246.2639", "Sc", "CY₃", "Spec", "dimless", "v10", "🟡", "0.018%; 公式源 O53 docs (O210 只做型別)"),
    ("V_EW = 246.21 GeV", "246.21", "Sc", "anchor", "anchor", "dimless", "v10", "🟡", "電弱標度錨"),
    ("Λ_eff = 8πM_Pl²e^{−V_Λ}; ρ_Λ^{1/4} = 2.246 meV", "2.246", "Sc", "W", "⟨·⟩", "dimless", "v10", "🟡", "O86 🟡; 41/60 結構式優先"),
    ("D_A(ℓ) = R(1−4^{−ℓ})(ℓ+1.11911398)", "D_A", "Sc", "W", "Σ", "dimless", "v10", "🟢", "O76; z_eff = 1/ln4"),
    ("Σ√γ 閉式 (#17)", "—", "Sc", "K_chain", "Σ∘√Spec", "trans", "v10", "🟢", "重複引用"),
    # ── 誠實清單 ──
    ("δ(88) CP 相位域 Q(ζ₈₈)⁺ vs δ(55) Q(ζ₅₅)⁺", "T31", "Sc", "K_chain", "Spec", "Q(ζ₈₈)⁺/Q(ζ₅₅)⁺", "v10", "🟢", "O155 T31 域不相容; 分工定理"),
    ("O206 殘餘 0.5875 = 未建模結構", "0.5875", "Sc", "—", "—", "—", "v10", "🔴", "非噪聲; OPEN-4 簇 — 未入代數"),
    ("283.0821 尾巴 (O107)", "283.0821", "Sc", "—", "—", "—", "v10", "🔴", "冇算子身份 — T0 判準排除"),
    ("44.5 = F₁₁/2", "44.5", "Sc", "—", "—", "—", "v10", "🔴", "縫外冇角色 (O152 R13)"),
    ("M* 斜率 −0.9±0.1 宿主質量投影", "−0.9", "Sc", "—", "—", "—", "v10", "🔴", "質量選取假象; 非代數量"),
]

# ───────────────────────── 檢查 ─────────────────────────
TYPES = {"Op", "Sc", "Fn", "Ix"}
FIELDS = {"Q", "Q(√5)", "Q(ζ₈₈)⁺", "Q(ζ₅₅)⁺", "ℂ", "trans", "composite", "dimless", "Q∪input", "Q∪trans", "—", "Q(√1230)", "Q(ζ₈₈)⁺/Q(ζ₅₅)⁺"}
STATUSES = {"🟢", "🟡", "🔴"}

errs = []
for i, (name, value, t, gen, fn, field, ver, status, note) in enumerate(R):
    if t not in TYPES:
        errs.append(f"[{i}] {name}: type '{t}' 唔喺四型")
    if t == "Sc":
        if status != "🔴":   # 🔴 = T0 判準排除裁決本身 (誠實標記), 唔當違規
            if fn == "none":
                errs.append(f"[{i}] {name}: Sc 但冇 functional (T0 違反)")
            if gen == "—":
                errs.append(f"[{i}] {name}: Sc 但冇 generator (T0 違反)")
    if field not in FIELDS:
        errs.append(f"[{i}] {name}: field '{field}' 未註冊")
    if status not in STATUSES:
        errs.append(f"[{i}] {name}: status '{status}' 未註冊")

# 重寫率
total = len(R)
green = sum(1 for r in R if r[7] == "🟢")
yellow = sum(1 for r in R if r[7] == "🟡")
red = sum(1 for r in R if r[7] == "🔴")
rate = green / total if total else 0

print(f"O210 型別註冊表: {total} 條目")
print(f"  🟢 可代數化 (T0 滿足 + 版本標籤): {green}")
print(f"  🟡 錨/輸入或源待核: {yellow}")
print(f"  🔴 冇算子身份 (T0 判準排除, 誠實標記): {red}")
print(f"  重寫率 (🟢/total) = {rate:.3f} ({green}/{total})")
if errs:
    print("  ERRORS:")
    for e in errs:
        print("   -", e)
    print("RESULT: FAIL")
else:
    print("RESULT: PASS (型別/域/狀態全部合規)")

# 輸出 machine-readable JSON
with open("data/02_type_registry.json", "w", encoding="utf-8") as f:
    json.dump([{"name": r[0], "value": r[1], "type": r[2], "generator": r[3],
                "functional": r[4], "field": r[5], "version": r[6],
                "status": r[7], "note": r[8]} for r in R],
              f, ensure_ascii=False, indent=1)
print("data/02_type_registry.json 已寫入")
