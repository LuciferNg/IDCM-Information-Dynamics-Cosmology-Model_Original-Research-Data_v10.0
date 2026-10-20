#!/usr/bin/env python3
"""
O254 scripts/01 — 能量數量級圍堵 (Energy Enclosure)
========================================================================
問題: P14 docs/29 Q2「改變拓撲態需要嘅能量係幾多? 晶體級 (mJ) 定天文級 (10⁴⁰ J)?」

預註冊判據 (跑前凍結, 禁後改):
  E1 = 1 mJ 脈衝喺 10 MHz 下嘅聲子數          → 判: 'mJ 含 ≫ 1 個聲子' (數量問題)
  E2 = 宇宙 K_Chain 單模量子 ℏω_ring           → 判: 報告數量級 (單量子從不禁止任何事)
  E3 = 相干全晶格翻轉下限 = N_IDCM·ℏω_ring = 2πE_Pl   → 判: E3/E_mJ > 1e10 (mJ 唔夠 10 個數量級)
  E4 = 觀測錨 UHECR (阻挫邊重聯 = 拓撲事件) 10^19-10^20 eV → 判: E4/E_mJ > 1e3
  E5 = 全宇宙真空凝聚能 ρ_vac·V_world            → 判: 報告 (真正「天文級」端)
  E6 = 10⁴⁰ J 佔位數: corpus grep 有冇結構推導   → 判: 報告 (docs/32 已標「未推導」)
  E7 = 能量槓桿 Λ₀ = ρ_vac·V_int/(ℏ·Δω) 重算     → 判: Λ₀ ∈ [8e11, 1e12] (docs/32: 9.06e11)
       plus 臨界發散後 1mJ 等效響應 vs E3        → 判: 報告「等效響應 ≠ 耦合/提取」

常量來源 (均 P14 docs/29/30/32 + register):
  ω_ring = 72.59 km/s/Mpc (P14 用), c=R·ω_ring 錨定 H₀=67.4071 差 ~7.7% 對數量級無關
  R_world = 4129.94 Mpc; ρ_vac = 6e-10 J/m³ (P14 scripts/56)
  N_IDCM = τ/t_Pl = 7.88e60 (register O86/O213 錨)
  聲子能量 10 MHz: E = h·f ≈ 6.6e-27 J (docs/29: ~10⁻²⁶ J)

輸出: data/01_energy_enclosure.json + logs/01.txt
執行: /usr/bin/python3 (background shell python3 係 miniforge 缺 numpy)
"""
import json
import math
import os

OUT_D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUT_L = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(OUT_D, exist_ok=True)
os.makedirs(OUT_L, exist_ok=True)

L = []
def p(s=""):
    L.append(str(s))
    print(s)

rows = []
checks = []
def chk(name, cond, desc):
    checks.append((name, bool(cond)))
    p(f"[{'PASS' if cond else 'FAIL'}] {name}: {desc}")

N_PASS = lambda: sum(1 for _, c in checks if c)
N_TOT = lambda: len(checks)

# ---------- 常量 ----------
h = 6.62607015e-34          # J·s
hbar = 1.054571817e-34      # J·s
c = 2.99792458e8            # m/s
G = 6.67430e-11             # m³/kg/s²
e_charge = 1.602176634e-19  # C (eV→J)
Mpc_m = 3.0856775814913673e22  # m per Mpc

omega_ring_permile = 72.59           # (km/s)/Mpc, P14 用
omega_ring_rad = omega_ring_permile * 1e3 / Mpc_m   # rad/s
E_Pl = math.sqrt(hbar * c**5 / G)    # J

# 宇宙 K_Chain 單模量子 E2
E_q_ring = hbar * omega_ring_rad

# ⿻ 審計修正 (2026-10-20): N_IDCM 用結構定義 N_exact=1/(ω_ring·t_Pl), dev E3a→0; 空 check 修正
N_reg = 7.88e60          # register O86/O213 (3 sig, 僅對照)
N_IDCM = 1.0 / (omega_ring_rad * math.sqrt(hbar * G / c**5))  # = τ/t_Pl ≡ 7.884689e60, dev 0
E_coherent = N_IDCM * E_q_ring       # 直接乘 (N 由 ω_ring,t_Pl 導出)
E_Pl_ref = hbar / math.sqrt(hbar * G / c**5)  # ℏ/t_Pl = E_Pl (= sqrt(ℏc⁵/G) 同值)
E_mJ = 1e-3               # J

# 晶體聲子 (10 MHz = P14 BOM 晶振級; docs/30 用 10 MHz)
f_phonon = 10e6
E_ph = h * f_phonon
N_ph_mJ = E_mJ / E_ph

# 觀測錨 UHECR E4
E_uhecr_1 = 1e19 * e_charge   # J
E_uhecr_2 = 1e20 * e_charge

# 全宇宙真空凝聚能 E5
rho_vac = 6e-10               # J/m³ (P14 scripts/56)
R_world_m = 4129.94 * Mpc_m
V_world = (4/3) * math.pi * R_world_m**3
E_vac_world = rho_vac * V_world

# 能量槓桿 E7 (P14 scripts/56 重算)
V_int = 1e-6                  # 1 cm³
delta_w = 2 * math.pi * 1e6   # 1 MHz 拍頻
Lambda0 = rho_vac * V_int / (hbar * delta_w)

p("=" * 84)
p("  O254 scripts/01: 能量數量級圍堵 — mJ vs 10⁴⁰ J 圍堵")
p("=" * 84)

p("\n[常量]")
p(f"  ω_ring   = {omega_ring_permile} (km/s)/Mpc = {omega_ring_rad:.4e} rad/s")
p(f"  E_Pl     = {E_Pl:.4e} J")
p(f"  N_IDCM   = {N_IDCM:.3e} (register O86/O213)")
p(f"  R_world  = {R_world_m:.4e} m = {R_world_m/Mpc_m:.2f} Mpc")

p("\n[E1] 晶體側: 1 mJ @ 10 MHz")
p(f"  聲子能量 E_ph        = {E_ph:.4e} J (~10⁻²⁶ J, docs/29 一致)")
p(f"  1 mJ 聲子數 N_ph     = {N_ph_mJ:.4e}")
chk("E1", N_ph_mJ > 1e20, f"mJ 含 ≫1 個聲子 (N_ph={N_ph_mJ:.2e}) — 能量額度唔係樽頸")

p("\n[E2] 宇宙 K_Chain 單模量子")
p(f"  ℏω_ring             = {E_q_ring:.4e} J")
p(f"  N_IDCM(結構)        = {N_IDCM:.6e} (≡ τ/t_Pl; 對照 register 7.88e60)")
p(f"  對比聲子: E_ph/E_q  = {E_ph/E_q_ring:.4e} (~{math.log10(E_ph/E_q_ring):.1f} 數量級, docs/29 23 數量級係頻率比)")
chk("E2", E_q_ring < E_ph, f"單量子 ℏω_ring={E_q_ring:.2e} J < 聲子 {E_ph:.2e} J — 單量子極細 (唔係限制端, 但真比較)")

p("\n[E3] 相干全晶格翻轉下限")
p(f"  E_coherent = N_IDCM·ℏω_ring = {E_coherent:.4e} J")
p(f"  E_Pl 閉式           = {E_Pl_ref:.4e} J")
chk("E3a", abs(E_coherent - E_Pl_ref) / E_Pl_ref < 0.001,
    f"N_IDCM·ℏω_ring = E_Pl 恆等 (N_IDCM 定義 τ=1/ω_ring; dev {abs(E_coherent-E_Pl_ref)/E_Pl_ref*100:.3f}%)")
chk("E3b", E_coherent / E_mJ > 1e10,
    f"E3/E_mJ = {E_coherent/E_mJ:.3e} > 1e10 ⟹ 相干全晶格翻轉至少高 mJ 10 個數量級以上")

p("\n[E4] 觀測錨: UHECR = 阻挫邊重聯 = 拓撲事件釋能 (P14 O7)")
p(f"  10^19 eV = {E_uhecr_1:.4e} J ; 10^20 eV = {E_uhecr_2:.4e} J")
chk("E4", E_uhecr_2 / E_mJ > 1e3,
    f"E4/E_mJ = {E_uhecr_2/E_mJ:.3e} > 1e3 ⟹ 一個宇宙拓撲事件 (UHECR 級) 能量高 mJ ≥4 個數量級")
p("  註: 但 graph-Ising ΔE=0 節點 (P14 docs/09) 圖模型翻轉成本 = 0 — 能量唔係唯一殺手,")
p("      實體相位滑移觸發能量喺 P14 未錨定 🔴 (人造調制器不存在)")

p("\n[E5] 全球真空凝聚能 (真正「天文級」端)")
p(f"  V_world    = {V_world:.4e} m³")
p(f"  E_vac_world = ρ_vac·V_world = {E_vac_world:.4e} J")
p(f"  log10 = {math.log10(E_vac_world):.2f} ⟹ ~10⁶⁹ J (遠超 10⁴⁰ J 佔位數)")

p("\n[E6] 10⁴⁰ J 佔位數狀態")
p("  corpus 考古 (P14 docs/29/32 + scripts/55-58):")
p("    docs/29:52  「天文級 (10⁴⁰ J)?」 — 首次出現, 純問題形式")
p("    docs/32:651  「Q2 能量 mJ vs 10⁴⁰ J — 呢個數量級估算未推導 (只係問題), 唔係答案」")
p("    scripts/55:326 問題重述; scripts/58 結論係「1-10 mJ 可改變全域陳數」(docs/32 評過樂觀)")
chk("E6", (E_uhecr_2 < 1e40 < E_vac_world),
    f"1e40 J 落喺事件錨 {E_uhecr_2:.0f} J 與全球凝聚 {E_vac_world:.3e} J 之間 — 冇對應已推導宇宙能量階, 佔位數 (真比較)")

p("\n[E7] 能量槓桿 Λ₀ 重算 (P14 scripts/56 對照)")
p(f"  Λ₀ = ρ_vac·V_int/(ℏ·Δω) = {Lambda0:.4e}")
chk("E7a", 8e11 <= Lambda0 <= 1e12, f"Λ₀ ∈ [8e11,1e12] 對上 docs/32 重算值 9.06e11")
# 臨界發散檔 (scripts/56: ν=1.5 @ δ-δ_c=1e-6 → ×1e9)
Lambda_crit = Lambda0 / (1e-6 ** 1.5)
# scripts/56 表格 audit: δ-δ_c=0.001, ν=1.5 行 — scripts/56 打印 10¹⁵, 實應 (1e-3)^-1.5 = 3.1623e4
div_001_15 = (1e-3) ** -1.5
chk("E7b", abs(div_001_15 - 3.1623e4) / 3.1623e4 < 1e-3,
    f"scripts/56 臨界表 audit: (1e-3)^-1.5 = {div_001_15:.4e} ≠ 其打印 1e15 — scripts/56 表格算術出錯")
p(f"  ⚠️ 即 scripts/56 之「Λ≈10²⁷ → 1 mJ → 10²⁴ J」(δ=0.001, ν=1.5) 應為 ~2.9e16 → 2.9e13 J")
p(f"     即使照佢最寬鬆讀法, 1 mJ → ~1e13 J 等效響應, 仍 ≪ E5 全球凝聚 5.2e69 J; 且係響應唔係提取")
resp_mJ_nominal = E_mJ * Lambda0
resp_mJ_crit = E_mJ * Lambda_crit
p(f"  Λ₀ 下 1 mJ「等效響應」 = {resp_mJ_nominal:.4e} J")
p(f"  臨界發散 (ν=1.5, δ-δ_c=1e-6) 下 = {resp_mJ_crit:.4e} J")
p(f"  對比 E3 相干下限 {E_coherent:.3e} J: 名義 Λ₀ 唔夠 ({resp_mJ_nominal/E_coherent:.2e}×),")
p(f"    臨界發散檔名義上夠 ({resp_mJ_crit/E_coherent:.2e}×) — 但 Λ₀ 係「等效響應」唔係「可提取/可耦合能量」,")
p(f"    且 |δ-δ_c|=1e-6 調諧同耦合算子都係 unanchored 🔴 (scripts/56 footnote 自己講明)")

# ---------- 圍堵總結 ----------
lo, hi = E_uhecr_2 / E_mJ, E_vac_world / E_mJ
p("\n" + "=" * 84)
p("  圍堵總結 (log10 對 mJ):")
p(f"    1 mJ  --------------------- 0")
p(f"    UHECR 單事件 (10^20 eV) --- {math.log10(E_uhecr_2/E_mJ):+.1f}   ← 觀測事件錨")
p(f"    相干全晶格翻轉 (E_Pl) ----- {math.log10(E_coherent/E_mJ):+.1f}  ← 結構下限 (恆等 = ℏ/t_Pl)")
p(f"    10⁴⁰ J 佔位數 ------------ {math.log10(1e40/E_mJ):+.1f}   ← 無推導")
p(f"    全宇宙真空凝聚 ----------- {math.log10(E_vac_world/E_mJ):+.1f}   ← 真正天文端")
p("=" * 84)
p(f"  Q2 初步裁決: 「mJ vs 10⁴⁰ J」係假二分。")
p(f"  圍堵: 任何實體宇宙拓撲事件 (E4) ≥ ~10 J ≫ 1 mJ (差 ≥4 數量級);")
p(f"  相干全晶格翻轉 (E3) ~10⁹ J (恆等 E_Pl, 差 12 數量級); 全球凝聚 ~10⁶⁹ J。")
p(f"  10⁴⁰ J 唔係答案 — 係未推導佔位數。mJ 端在能量意義上否證;")
p(f"  但 ΔE=0 圖模型 + 無耦合算子意味 Q1/Q3 先係真正殺手 (docs/29 🔴)。")

p(f"\n  RESULT: {N_PASS()}/{N_TOT()} PASS")

rows = {
    "title": "O254 scripts/01 能量數量級圍堵",
    "E_mJ_J": E_mJ,
    "E_ph_10MHz_J": E_ph,
    "N_ph_per_mJ": N_ph_mJ,
    "E_q_ring_J": E_q_ring,
    "N_IDCM": N_IDCM,
    "E_coherent_J": E_coherent,
    "E_Pl_ref_J": E_Pl_ref,
    "E_uhecr_1e19eV_J": E_uhecr_1,
    "E_uhecr_1e20eV_J": E_uhecr_2,
    "E_vac_world_J": E_vac_world,
    "E10_40_J": 1e40,
    "Lambda0": Lambda0,
    "resp_mJ_nominal_J": resp_mJ_nominal,
    "resp_mJ_critical_J": resp_mJ_crit,
    "checks": {n: bool(c) for n, c in checks},
    "conclusion": "mJ vs 1e40 J 假二分; 圍堵 = 事件錨~10J / 相干下限~1.96e9J (=E_Pl, N_IDCM·ℏω_ring 恆等) / 全球凝聚~1e69J; mJ 端能量否證, Q1/Q3 耦合算子先係真殺手",
}

with open(os.path.join(OUT_D, "01_energy_enclosure.json"), "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)
with open(os.path.join(OUT_L, "01.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
p(f"\n✅ 已寫入: data/01_energy_enclosure.json + logs/01.txt")