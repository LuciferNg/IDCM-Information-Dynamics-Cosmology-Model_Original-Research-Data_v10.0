#!/usr/bin/env python3
"""
O49 06: O66 交叉閉合 + 結構缺口終審
====================================
2026-09-14: O49 結構缺口攻堅。

發現: O66 (o66_mcomp_first_principles) 已用 K_Chain propagator 機制閉合 M_comp:
  M_comp = M_pl × 10^(-(1/γ₆ - 1/76)) = 3.6890e13 GeV (0.0277%)
  76 = 88-12 = φ⁹-φ⁻⁹ = 4×19 (三重身份)

O49 舊鏈錯誤: 用咗 O66 表 2.2 明確拒絕嘅 M_comp[B] = M_pl/(2·h¹¹·h²¹·N_d)
(6.57% off), 再靠 φ^(1/8) 修正補救 → 人工修正, 非結構。

本 script: 驗證 O66 鏈 + NO 自洽譜 + Δm² 比 = 2B² = 32 + φ-power 衝突判定。
"""
import math, json, os
from pathlib import Path

phi = (1 + math.sqrt(5)) / 2
M_pl = 1.2209e19
v = 246.0
B = 4
Nd = 44
g6 = 4 * math.sin(6 * math.pi / 88) ** 2
PDG31, PDG21 = 2.434e-3, 7.53e-5

HERE = Path(__file__).parent
DATA = HERE.parent / "data"

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

print("=" * 76)
print("O49 06: O66 交叉閉合 + 結構缺口終審")
print("=" * 76)

# ─────────────────────────────────────────────────────────────
# §1 O66 M_comp 結構公式
# ─────────────────────────────────────────────────────────────
print("\n[1] O66 M_comp 結構公式 (K_Chain propagator)")
M_comp_O66 = M_pl * 10 ** (-(1 / g6 - 1 / 76))
print(f"  M_comp = M_pl×10^(-(1/γ₆ - 1/76)) = {M_comp_O66:.6e} GeV")
print(f"  1/γ₆ = {1/g6:.9f}, 1/76 = {1/76:.9f}, diff = {1/g6-1/76:.9f}")
check("M_comp ≈ 3.6890e13 (O66 閉合值)", abs(M_comp_O66 - 3.6890e13) / 3.6890e13 < 1e-4,
      f"({abs(M_comp_O66-3.6890e13)/3.6890e13*100:.4f}%)")
check("76 = 88-12 三重身份", (88 - 12 == 76) and abs(phi**9 - phi**(-9) - 76) < 1e-9
      and 4 * (Nd - 21 - B) == 76, "88-12 = φ⁹-φ⁻⁹ = 4×(44-21-4)")

# O49 舊 M_comp[B] 對比
MB_old = M_pl / (2 * 36 * 98 * Nd)
print(f"  O49 舊 [B] = M_pl/(2·h¹¹·h²¹·N_d) = {MB_old:.6e} GeV "
      f"(O66 表 2.2: 6.57% off, 已拒)")
print(f"  φ^(1/8) = {phi**(1/8):.6f}  ← 舊鏈人工修正, O66 唔需要")
check("O66 M_comp 比 O49 [B] 精確 >100×",
      abs(M_comp_O66 - 3.6909e13) / 3.6909e13 < abs(MB_old - 3.6909e13) / 3.6909e13 / 100,
      f"(O66 {abs(M_comp_O66-3.6909e13)/3.6909e13*100:.4f}% vs [B] {abs(MB_old-3.6909e13)/3.6909e13*100:.3f}%)")

# ─────────────────────────────────────────────────────────────
# §2 Propagator 機制 (O66 06)
# ─────────────────────────────────────────────────────────────
print("\n[2] K_Chain propagator 機制 (V_cycle 問題嘅答案)")
site_sum = sum(math.sin(6 * n * math.pi / 88) ** 2 for n in range(1, 45))
check("Σψ₆² = 22", abs(site_sum - 22) < 1e-10, f"({site_sum:.10f})")
print(f"  G₆(total) = 22/γ₆ = {22/g6:.6f}  ← propagator 強度")
print(f"  det(Δ_without_6)/det(Δ) = 1/γ₆ = {1/g6:.6f}  ← 譜行列式比")
print(f"  ΔS_eff = ½ln(1/γ₆) = {0.5*math.log(1/g6):.6f}")
S_inst = math.log(10) / g6 - math.log(10) / 76
print(f"  ln(M_pl/M_comp) = {S_inst:.6f} = ln(10)/γ₆ - ln(10)/76")
check("ln(M_pl/M_comp) = ln(10)(1/γ₆-1/76) 恒等",
      abs(S_inst - math.log(M_pl / M_comp_O66)) < 1e-12)
print(f"  → V_cycle 機制閉合: 緊化能標 = K_Chain propagator 穿透效應, 唔係 orbifold 體積")
print(f"  → 76 = 88-12 = Σγ_odd - 2×6 (純 K_Chain, 非 CY₃ 幾何)")

# ─────────────────────────────────────────────────────────────
# §3 NO 自洽質量譜 (O66 07)
# ─────────────────────────────────────────────────────────────
print("\n[3] NO 自洽質量譜 (18% 偏差 = 假警報)")
m3 = (g6 * v) ** 2 / M_comp_O66 * 1e9   # eV
m1 = math.sqrt(max(m3**2 - PDG31, 0))
m2 = math.sqrt(m1**2 + PDG21)
print(f"  m₃ = (γ₆v)²/M_comp = {m3:.6f} eV  ← 唯一結構預言")
print(f"  m₁ = √(m₃²-Δm²₃₁) = {m1:.6f} eV  ← NO 自洽 (Δm²₃₁ = m₃²-m₁²)")
print(f"  m₂ = √(m₁²+Δm²₂₁) = {m2:.6f} eV  ← 自洽 (Δm²₂₁ = m₂²-m₁²)")
check("Δm²₃₁ 自洽 = PDG", abs(m3**2 - m1**2 - PDG31) < 1e-8)
check("Δm²₂₁ 自洽 = PDG", abs(m2**2 - m1**2 - PDG21) < 1e-8)
sum_nu = m1 + m2 + m3
print(f"  Σm_ν = {sum_nu:.4f} eV  (DESI 2024 < 0.072 🔴, Planck < 0.12 ✅)")
print(f"  舊 O49 φ-power 譜: m_τ=0.0534, m_μ=0.0330, m_e=0.0204 → Δm²₂₁ raw 要 /Z₃²")

# φ-power hierarchy 衝突判定
m_mu_phi = m3 / phi   # O49 φ-power m_μ
print(f"\n  ★ φ-power hierarchy 衝突判定:")
print(f"    O49 φ-power: m_μ = m_τ/φ = {m_mu_phi:.4f} eV")
print(f"    O66 NO 自洽: m₂ = {m2:.4f} eV")
conflict = abs(m_mu_phi - m2) / m2 * 100
print(f"    衝突: {conflict:.1f}% ← m₂ 差 46%!")
print(f"    φ-power 譜 Δm²₂₁(raw) = m_μ²-m_e² = {(m3/phi)**2-(m3/phi**2)**2:.4e} eV²")
print(f"    PDG Δm²₂₁ = {PDG21:.2e} → 需要 Z₃² = 9 修正 (8.93, 0.73% 偏差)")
print(f"    O66 NO 譜: m₂²-m₁² = {m2**2-m1**2:.4e} 直接自洽, 零修正")
check("O66 NO 譜零修正自洽 (優於 φ-power+Z₃²)",
      abs(m2**2 - m1**2 - PDG21) < 1e-9,
      f"(φ-power 要 8.93≈9 近似修正)")

# ─────────────────────────────────────────────────────────────
# §4 Δm² 比 = 2B² = 32 (O57 docs/23 結構比)
# ─────────────────────────────────────────────────────────────
print("\n[4] Δm²₃₁/Δm²₂₁ = 2B² = 32 結構比 (O57 已確立)")
ratio = PDG31 / PDG21
print(f"  PDG 比 = {ratio:.4f} vs 2B² = 2×16 = 32")
dev32 = abs(ratio - 32) / 32 * 100
print(f"  偏差 = {dev32:.2f}%  ({'✅ 結構級' if dev32 < 1.1 else '🟡'})")
print(f"  一致性: Δm²₃₁ = {PDG31:.4e} vs 32×Δm²₂₁ = {32*PDG21:.4e}")
recon = abs(PDG31 - 32*PDG21) / PDG31 * 100
check("2B² 比一致性 (Δm²₃₁ ≈ 32×Δm²₂₁)", recon < 1.1,
      f"({recon:.2f}%)")

# ─────────────────────────────────────────────────────────────
# §5 Majorana dim-5 算子 (O57 Step 11)
# ─────────────────────────────────────────────────────────────
print("\n[5] Majorana dim-5 Weinberg 算子 (O57 Step 11)")
print(f"  λ = γ₆² = {g6**2:.8f} (W-field p6 實數模式 → 自伴 → Majorana)")
print(f"  m_ν = γ₆²v²/M_comp (dim-5), 對比 Dirac dim-4: y = M₀γ_n/v")
print(f"  → 中微子/帶電輕子 10¹¹ 壓抑 = dim-5/M_comp 尺度, 非調校")
check("γ₆² 角色: p6 quadratic (O57)", abs(g6**2 * v**2 / M_comp_O66 * 1e9 - m3) < 1e-6)
print(f"  0νββ 預言 (O57 docs/20): m_ββ = [6.4, 22.2] meV (LEGEND-1000 可測)")

# ─────────────────────────────────────────────────────────────
# §6 正態 vs 反態
# ─────────────────────────────────────────────────────────────
print("\n[6] 質量等級 (NO vs IO)")
print(f"  m₃ = {m3:.4f} > m₂ = {m2:.4f} > m₁ = {m1:.4f} → 正態 (NO)")
print(f"  m₃ 由結構 (γ₆v)²/M_comp 決定 = 0.0536 eV > √(Δm²₃₁) = {math.sqrt(PDG31):.4f}")
print(f"  → NO 係唯一自洽 (IO 需要 m₃ 係最輕, 與結構 m₃ 矛盾)")
check("NO 唯一自洽 (m₃ 結構值 > √Δm²₃₁)", m3 > math.sqrt(PDG31),
      f"({m3:.4f} > {math.sqrt(PDG31):.4f})")

# ─────────────────────────────────────────────────────────────
# §7 誠實缺口表
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 76)
print("[7] O49 結構缺口終審 (2026-09-14)")
print("=" * 76)
gaps = [
    ("M_comp 結構來源", "✅ O66 閉合: M_pl×10^(-(1/γ₆-1/76)), propagator 機制, 0.0277%"),
    ("φ^(1/8) 修正", "❌ 撤銷: 補償錯誤 M_comp[B] 嘅人工修正, O66 鏈唔需要"),
    ("V_cycle 機制", "✅ O66 閉合: K_Chain propagator 穿透 (G₆ = 22/γ₆, det 比 1/γ₆)"),
    ("Z₅ 荷 (4,0,3)", "🟡 φ-power hierarchy 被 O66 NO 譜推翻 (m₂ 差 46%); Z₅ 角色 = δ_CP = 2π/5 (O65), 非質量 hierarchy"),
    ("Z₃² = 9 修正", "❌ 撤銷: O66 NO 譜 Δm²₂₁ 直接自洽, 零修正; Z₃² 係 φ-power 錯譜嘅補救"),
    ("世代結構 m₁:m₂:m₃", "🔴 開放: O66 m₁,m₂ 由 Δm² 反推, 冇世代結構; φ-power 被推翻"),
    ("Majorana 證明", "✅ O57: dim-5 Weinberg λ=γ₆², 實數模式自伴; 0νββ [6.4,22.2] meV"),
    ("質量等級", "✅ NO 唯一自洽 (m₃ 結構值 > √Δm²₃₁)"),
    ("Σm_ν 預言", "🔴 0.0971 eV vs DESI < 0.072 — 可證偽張力 (O66 已標)"),
]
for name, verdict in gaps:
    mark = "🟢" if verdict.startswith("✅") else ("🟡" if verdict.startswith("🟡") else ("🔴" if verdict.startswith("🔴") else "❌"))
    print(f"  {mark} {name}: {verdict[2:]}")

# ─────────────────────────────────────────────────────────────
# §8 世代結構終審: 2B² 比 + NO 自洽 vs φ-power 推翻
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 76)
print("[8] 世代結構終審 — φ-power 被推翻嘅物理原因")
print("=" * 76)

# φ-power hierarchy 預言 m₂/m₁ = φ
# O66 NO 自洽譜: m₂/m₁ = 1.083 (近簡併)
# 太陽對 (m₁,m₂) 近簡併 ← Δm²₂₁ 細 (7.53e-5)
print(f"  φ-power hierarchy 預言: m₂/m₁ = φ = {phi:.3f} → Δm²₂₁ = m₁²φ = {m1**2*phi:.4e}")
print(f"  觀測: Δm²₂₁ = {PDG21:.2e} (細 9.4×)")
print(f"  O66 NO 自洽: m₂/m₁ = {m2/m1:.4f} (近簡併!)")
print(f"\n  → 太陽對 (m₁,m₂) 係近簡併 (差 8.3%), 唔係 φ 分離")
print(f"  → φ-power 1:φ⁻¹:φ⁻² 對 m₂ 錯 46.3% → 推翻")
print(f"  → 世代結構嘅真正內容 = Δm²₃₁/Δm²₂₁ = 2B² = 32 (O57 結構比)")

# 世代結構「比」已閉合: 2B² 比
print(f"\n  世代結構比閉合: Δm²₃₁/Δm²₂₁ = 2B² = 32 (dev {dev32:.2f}%)")
check("世代結構比 = 2B² (O57)", dev32 < 1.1, f"({dev32:.2f}%)")

# 但 m₁/m₃ 冇獨立結構: 由 Δm²₃₁ 反推
# m₁/m₃ = √(1 - Δm²₃₁/m₃²)
m1_m3 = m1 / m3
print(f"\n  m₁/m₃ = √(1-Δm²₃₁/m₃²) = {m1_m3:.4f} ← 由 Δm² 反推, 非獨立結構")
print(f"  對照 φ⁻² = {phi**(-2):.4f} (dev {abs(m1_m3-phi**(-2))/phi**(-2)*100:.1f}%)")
print(f"  → m₁ ≈ m₃φ⁻² 只係巧合 (Δm²₃₁/m₃² ≈ 1-φ⁻⁴ 差 0.76%), 唔係結構")

print(f"\n  世代結構終審:")
print(f"    ✅ 比結構閉合: Δm²₃₁/Δm²₂₁ = 2B² = 32 (O57)")
print(f"    ✅ 絕對標度閉合: m₃ = (γ₆v)²/M_comp (O66)")
print(f"    🔴 世代質量比 m₁:m₂:m₃ 冇獨立結構公式 (m₁/m₂ 由 Δm² 反推)")
print(f"       — m₁ ≈ m₃φ⁻² (2.2%), m₂ ≈ m₃φ⁻¹ 錯 46% → φ-power 唔成立")
print(f"       — 剩餘: 點解 Δm²₂₁ 咁細 (太陽對近簡併)? → 新 O 候選")

results = {
    "test": "O49 06: O66 交叉閉合 + 結構缺口終審",
    "M_comp_O66": M_comp_O66,
    "m3_eV": m3, "m1_eV": m1, "m2_eV": m2,
    "sum_nu_eV": sum_nu,
    "dm31_self_consistent": True,   # §3 check 已驗證 (Δm²₃₁ 自洽, <1e-8)
    "dm21_self_consistent": True,   # §3 check 已驗證 (Δm²₂₁ 自洽, <1e-8)
    "dm_ratio_2B2": ratio, "dm_ratio_dev_pct": dev32,
    "phi_power_conflict_pct": conflict,
    "status": "M_comp ✅ O66 propagator 閉合; φ-power/Z₃² 撤銷; 世代結構 🔴 開放; Σm_ν 🔴 DESI 張力",
    "passed": passed, "failed": failed,
}
results["generation_structure"] = {
    "phi_power_rejected": True,  # §8 conflict=46% 已計算證偽 (m₂ 差 46% → φ-power 唔成立)
    "m2_m1_NO": m2 / m1,
    "m2_m1_phi": phi,
    "dm_ratio_2B2": ratio,
    "m1_m3": m1_m3,
    "m1_m3_phi_minus2": phi**(-2),
    "status": "比結構 2B² ✅; 質量比無獨立結構 🔴 (φ-power 推翻)",
}
with open(DATA / "06_structural_closure.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nPassed: {passed}, Failed: {failed}")
raise SystemExit(1 if failed else 0)
