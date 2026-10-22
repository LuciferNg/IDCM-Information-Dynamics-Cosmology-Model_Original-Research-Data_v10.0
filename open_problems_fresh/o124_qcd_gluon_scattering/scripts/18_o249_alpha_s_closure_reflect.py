#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O124 scripts/18 — O249 審計: α_s⁻¹ = F₆+sin²θ_W+1/B 閉合宣稱撤銷 (2026-10-14)
========================================================================================
■ 角色: O249 審計修正重跑 —— 獨立於 scripts/02 E5 + scripts/03 判決表 L141 嘅
  歷史輸出（該兩 script 原文保留）。本 script 輸出 O249 後之修正判定。
■ 原則: 零外部數據錨（唯一外部輸入 alpha_s_MZ = 0.1179, v9.0 遺留）。
  O144 docs/20 六判據為文檔層證據（docs/01 §廿五 已引），本 script 只做
  算術重算 + 對照,O249 判決以 docs 為準。
■ 記錄: tee → data/18_o249_alpha_s_closure_reflect_results.txt
■ 舊 scripts/02 (E5 ★ 三路徑收斂) + scripts/03 (L141 E α_s 🟢) 歷史保留,
  唔改 —— 佢哋嘅「★/🟢」輸出係 O249 之前嘅歷史狀態, 由本 script 同
  docs/01 §廿五/§廿六 承接修正。
"""
import math

PASS = FAIL = TOTAL = 0

def chk(name, cond, extra=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  ✅ {name} {extra}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {extra}")

N_d = 88      # 88-site ring (O124 核心)
B   = 4       # 色扇區秩 (L₃)
N_gen = 3     # SU(3) 色
F7 = 13       # Fibonacci
L4 = 7        # Lucas
L5 = 11
alpha_s_MZ = 0.1179   # v9.0 遺留唯一外部輸入
MZ_GeV   = 91.1876    # Z 質量 (標準值, 由 O142 共享)
Lam_IDCM_MeV = 45.2849  # O142 v16 Λ_IDCM (docs/16)

# ─────────────────────────────────────────────────────────────
print("=" * 78)
print("  O249 審計修正: α_s⁻¹ = F₆ + sin²θ_W + 1/B — 算術重算 + 修正判定")
print("  保留歷史: scripts/02 E5 + scripts/03 L141 原文不動; 本 script = O249 後路")
print("=" * 78)

# ── [A] 算術重算 (mpmath 級精度) ──────────────────────────────
print("\n─── [A] 算術重算 (高精度) ───")
sin2W = 1 - (math.cos(math.pi/8) - math.tan(3*math.pi/88)*math.sin(math.pi/8))**2
alpha_s_inv = 8 + sin2W + 1/B
print(f"  sin²θ_W        = {sin2W!r}")
print(f"  α_s⁻¹ (譜跡)   = {alpha_s_inv!r}")
print(f"  α_s   (譜跡)   = {1/alpha_s_inv!r}")

# O124 記錄值 (docs/03 §E + scripts/02 E1/E2)
chk("A1 譜跡 α_s⁻¹ = 8.47077573296567 (O124 記錄值複現)",
    abs(alpha_s_inv - 8.47077573296567) < 1e-13, f"({alpha_s_inv!r})")
chk("A2 α_s = 0.11805294 (O124 記錄值複現)",
    abs(1/alpha_s_inv - 0.11805294) < 1e-8, f"({1/alpha_s_inv:.10f})")

# ── [B] 對 SM 對照 (唯一外部輸入 0.1179) ───────────────────────
print("\n─── [B] SM 對照 ───")
sm_inv_2022 = 1/alpha_s_MZ
dev_2022 = (alpha_s_inv - sm_inv_2022)/sm_inv_2022 * 100
chk("B1 dev vs SM 2022 (1/0.1179 = 8.48176) ≈ 0.130% (O124 記錄值)",
    abs(dev_2022 - 0.1296) < 0.002, f"(dev {dev_2022:.4f}%)")
print(f"  ★ 註: SM 2024 中心 8.47458 → dev {abs(alpha_s_inv-8.47458)/8.47458*100:.6f}%")

# ── [C] O142 v14 邊界法重算 (替代路) ──────────────────────────
print("\n─── [C] O142 v14 邊界法 (替代路, 非譜跡) ───")
Lam_IDCM_GeV = Lam_IDCM_MeV/1000.0
alpha_s_inv_v14 = (L4/(2*math.pi)) * math.log(MZ_GeV/Lam_IDCM_GeV)
print(f"  α_s⁻¹(邊界法) = (L₄/2π)·ln(M_Z/Λ_IDCM) = {alpha_s_inv_v1:.10f}".replace("v1", "v14"))
chk("C1 邊界法 α_s⁻¹ = 8.47562 (O142 v14 docs/13 記錄值)",
    abs(alpha_s_inv_v14 - 8.47562) < 1e-4, f"({alpha_s_inv_v14:.6f}, dev vs SM2024 {abs(alpha_s_inv_v14-8.47458)/8.47458*100:.4f}%)")
print(f"  └─ 譜跡 8.4708 vs 邊界法 8.47562: 差 {abs(alpha_s_inv-alpha_s_inv_v14)*1000:.2f}e-3 (0.057%)")

# ── [D] O85 敏感度 (用真值 8.4818 替代 → 結論穩定性) ──────────
print("\n─── [D] O85 g₃/g₂ 敏感度 (docs/09 L237 引用) ───")
alpha2_inv = 30.0
g2 = math.sqrt(4*math.pi/alpha2_inv)
def g3(ai):
    return math.sqrt(4*math.pi/ai)
r_old = g3(alpha_s_inv)/g2
r_true = g3(sm_inv_2022)/g2
chk("D1 O85 用真值 8.4818 替代 8.4708 → g₃/g₂ 偏差變化 < 0.1% (結論穩)",
    abs(r_old - r_true)/r_old < 0.001,
    f"(曲用譜跡 {r_old:.5f} → 用SM真值 {r_true:.5f}, 變化 {abs(r_old-r_true)/r_old*100:.4f}%)")
print(f"  └─ O85 結論破壞性判據為結構性 (SU(12) 嵌入強制 g₃=g₂), 非數值 → 不受 O249 影響")

# ── [E] O249 修正判定 ─────────────────────────────────────────
print("\n─── [E] O249 修正判定 (取代 scripts/03 判決表 L141 之 🟢) ───")
print("  E α_s 譜跡形式:")
print("    • 算術複現: ✅ 8.47077573296567 = 8 + 0.2207757330 + 0.25")
print("    • 閉合宣稱: 🔴 已否證 —— O144 docs/20 §7 六判據全 🔴")
print("      (①v1用已否證3/13砌出 ②機制僅加法律 ③σ_rel 0.763%≫0.118%零判別力")
print("       ④±0.5σ 287命中 ⑤≤2項5條命中 ⑥原理路由全敗)")
print("    • 替代路:  🟡 O142 v14 邊界法 α_s⁻¹ = (L₄/2π)ln(M_Z/Λ_IDCM) = 8.47562")
print("    • 影響面:  b₀=L₄=7 不變; Δα⁻¹=9排除不變; α₂⁻¹=30 不涉本條公式")

# ── 結果 ──
print(f"\n{'='*78}")
print(f"  結果: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"  判決: 算術複現正確 (PASS 保持); 閉合宣稱 🔴 (O144 docs/20 六判據);")
print(f"        O142 v14 邊界法 8.47562 為現行替代路。")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)