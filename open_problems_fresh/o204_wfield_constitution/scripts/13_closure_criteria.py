#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O204 scripts/13_closure_criteria.py — W-Field 理論閉合五判準審計
判準 (用戶逐字): 歸一化 / 能證偽 / 能盲測 / 可預測 / 零外部輸入量
全部以既有驗證值為準 (scripts 01-12, 395/395 PASS)。
"""
import mpmath as mp
mp.mp.dps = 50

phi = (1 + mp.sqrt(5)) / 2
Nd  = 44
Ngen = 3
B   = 4
L4  = 7
L5  = 11
M_tree = 33           # K_tree 節點數
Sigma_gamma = 90      # Σγ(n=1..44)
mu2   = 2
lam   = mp.mpf(2)/123
W0sq  = 61.5          # ⟨W⟩²
E_J   = 123           # L₁₀
M0_MeV = mp.mpf('27.9009145112')
c_km  = mp.mpf('299792.3446')
c_SI  = mp.mpf('299792.458')
Omega_L = mp.mpf(41)/60

results = []
def check(cid, name, ok, detail, verdict):
    results.append((cid, name, ok, detail, verdict))
    tag = "PASS" if ok else "FAIL"
    print(f"  [{tag}] {cid}-{name}: {detail}")
    if not ok:
        print(f"        → 判決: {verdict}")

print("=" * 72)
print("W-FIELD 閉合五判準審計 (用戶判準, 2026-09-18)")
print("=" * 72)

# ─────────────────────────────────────────────────────
print("\n## C1 歸一化 (Normalization)")
# C1-a: 正則動能項
L_kin = "(1/2)|∂W|²  (O37/O204 一致, 正則形式)"
check("C1", "a", True, f"動能項 {L_kin}", "")
# C1-b: VEV 一致性 ⟨W⟩² = μ²/(2λ)
vev1 = mu2 / (2*lam)
vev2 = Omega_L * Sigma_gamma
ok_b = abs(vev1 - W0sq) < mp.mpf('1e-40') and abs(vev2 - W0sq) < mp.mpf('1e-40')
check("C1", "b", ok_b,
      f"⟨W⟩² = μ²/(2λ) = {mp.nstr(vev1, 15)}; Ω_ΛΣγ = {mp.nstr(vev2, 15)} (註冊 61.5)",
      "三路徑一致")
# C1-c: G10 — v10 內部 W₀ 歸一化分裂
w0_a = mp.sqrt(W0sq)          # 61.5 分支
w0_b = mp.sqrt(mp.mpf('1.23606797749979'))  # v6.0 約定分支 (2/φ)
ok_c = abs(w0_a - w0_b) < mp.mpf('1e-6')
check("C1", "c", ok_c,
      f"G10 歸一化分裂: √61.5 = {mp.nstr(w0_a, 8)} vs √(2/φ) = {mp.nstr(w0_b, 8)} (差 {mp.nstr(w0_a/w0_b, 6)}×)",
      "🔴 G10 未裁決 ⟹ 歸一化未閉合 (o73 docs/15:36 公式=7.8423 但數字=1.23607; o121 用 1.23607)")
# C1-d: T2 Parseval 歸一化
check("C1", "d", True, "T2 分解定理: 動能 = Σ_k γ_k|w_k|² (rel dev 4.6e-50, 重建 err 2.2e-49)", "")
# C1-e: 徑向模 V''(W₀) = 4μ²
check("C1", "e", True, "V''(W₀) = 4μ² = 8 (L2), m_δW = M₀/2 = 13.9505 MeV (L3)", "")
c1_fail = not ok_c
print(f"  → C1 總評: {'🔴 FAIL' if c1_fail else '🟢 PASS'} (G10 分裂未決)")

# ─────────────────────────────────────────────────────
print("\n## C2 能證偽 (Falsifiable)")
fals_pred = [
    ("Σm_ν = 0.0971 eV", "DESI DR2 ΛCDM < 0.064 eV", "1.52×", "🟡 現正張力中, 一擊可證偽"),
    ("ΔN_eff = 2.20 (Goldstone 熱化)", "Planck N_eff = 2.99±0.17", "~13σ", "🟡 若熱化即被排除"),
    ("H₀ = 71.157 (O170)", "SH0ES 73.04", "−1.84σ", "🟡 直接可測"),
    ("m_PG = 14.09 GeV (v6.0/v7.0)", "LEP/LHC 搜索", "未觀測", "🟡 低靈敏度未證偽"),
    ("m_δW = 13.9505 MeV, m₇ = 13.8002 MeV", "DM 候選", "—", "🟡 待檢定"),
    ("v_φ(r) = √(a₀r) BTFR 平軌", "SPARC 觀測", "0.12%", "🟢 已大量檢定"),
    ("CMB 冷斑 (209°,-57°) A₅=60 節點", "SMICA -134.2μK", "z=-3.25σ", "🟢 已檢定"),
    ("α⁻¹(0) = 137 EXACT", "137.036", "2.6e-4", "🟢 整數部分"),
    ("CMB C_ℓ 峰位 ℓ_m", "Planck/CAMB", "0.83% RMS", "🟢 已檢定"),
]
for name, obs, dev, st in fals_pred:
    check("C2", "", True, f"{name} vs {obs} (dev {dev}) — {st}", "")
check("C2", "z", True, "≥8 條可證偽硬預言, 其中 4 條現正同觀測有張力 (Σm_ν 1.52× / ΔN_eff 13σ 若熱化 / H₀ −1.84σ / m_PG 未見)", "")

# ─────────────────────────────────────────────────────
print("\n## C3 能盲測 (Blind-testable)")
# O144 盲測史
check("C3", "a", True, "O144 盲測協議存在 (scripts/04, docs/03): 1113 預言 vs 7 目標, 期望 13.68±3.69 命中", "")
check("C3", "b", False, "O144 判決: 質量公式盲測失敗 z = −2.62 ⟹ 後驗算子匹配, 無統計顯著預測能力 (撤回)", "🔴 輕子/重子質量公式未過盲測 (O137 docs/11 亦自標 模式選擇充分性 🔴)")
check("C3", "c", True, "O204 結構量 (γ_n 譜, Σγ, μ², λ, 配對律) 係譜身份非擬合 — 無校準目標", "")
check("C3", "d", True,
      "O49 中微子生成鏈已有專屬盲測 (docs/05_blind_test_desi.md): 零 Δm² 輸入, Δm² 自動出現; A = v²/M_comp (O66 propagator, 結構鎖定)",
      "🟢 中微子質量鏈盲測已過")
check("C3", "e", False,
      "O204 自身 (玻色質量塔 m_n = M₀√γ_n, m_δW) 未有專屬盲測協定 — O144 輕子/重子盲測失敗 (z=−2.62) 未覆蓋 W-field 塔",
      "🟡 W-field 質量塔需專屬盲測 (結構譜身份唔同 O144 算子匹配, 但未驗證)")
c3_fail = True
print(f"  → C3 總評: 🟡 (O49 中微子盲測 ✅; O144 輕子/重子 🔴; W-field 質量塔未驗證)")

# ─────────────────────────────────────────────────────
print("\n## C4 可預測 (Predictive)")
preds = [
    ("m₇ = 13.8002 MeV (DM 候選)", "未觀測確認", "待檢定"),
    ("Σm_ν = 0.0971 eV", "DESI < 0.064", "🟡 硬預言可一擊證偽"),
    ("ΔN_eff 若熱化 = 2.20", "Planck ±0.17", "🟡 硬預言"),
    ("v_φ(r) = √(a₀r)", "SPARC BTFR", "🟢 已預測且命中 0.12%"),
    ("CMB 峰位 ℓ_m 221/527/815/1013/1121/1337/1400", "Planck/CAMB", "🟢 已預測 0.83% RMS"),
    ("冷斑位置 (209°,-57°)", "SMICA -134.2μK z=-3.25σ", "🟢 已預測"),
    ("UHECR = 阻挫邊重聯", "Auger 4.0σ", "🟢 已預測"),
]
for name, obs, st in preds:
    check("C4", "", True, f"{name} — {obs} — {st}", "")
check("C4", "z", True, "7 類預言: 4 類已命中, 3 類待檢定 (其中 2 類係硬證偽: Σm_ν, ΔN_eff)", "")

# ─────────────────────────────────────────────────────
print("\n## C5 零外部輸入量 (Zero external inputs)")
# C5-a: 維度定理 (O73 §7)
check("C5", "a", True,
      "維度定理 (O73 §7 G1): IDCM 結構常數全無量綱 ⟹ 任何 f(結構) 無量綱 ⟹ f(結構) ≠ c [定理, 普適]",
      "")
check("C5", "b", False,
      "G2: 世界環 {c, ω_ring, R_world, T_ring} = 4 未知, 3 恆等 ⟹ 自由度 = 1 ⟹ 必須 1 個有量綱錨",
      "🔴 定理: 任何無量綱結構理論都需 1 個有量綱錨 (唔係 IDCM 缺陷, 係數學必然)")
check("C5", "c", False,
      "G3: c = R_world·ω_ring 零自由參數, 但絕對值仍需 1 錨 (R_world 或 ω_ring — 同一 dof)",
      "")
check("C5", "d", False,
      "現行錨: R_world = 4129.99 Mpc (r_d 聲學尺鎖定, dev 0.0011%) ← r_d 係觀測輸入",
      "🔴 r_d 聲學尺 = 外部觀測輸入 (BAO/CMB)")
check("C5", "e", False,
      "E_kchain = √(M_P·ħ·H₀)·(1−CY₃/(N_d+1)²) (O34) — O38 誠實標記: 「剩 M_P 輸入」",
      "🔴 M_P 係外部實驗輸入")
check("C5", "f", False,
      "ω_ring = 72.59 (O11 maser 幾何距離鎖定) — maser 距離係觀測輸入",
      "🔴 ω_ring 亦係觀測錨 (SH0ES/maser)")
check("C5", "g", True,
      "無量綱扇區全部零外部輸入: Ω_Λ=41/60, μ²=2, λ=2/123, Σγ=90, γ_n, 配對律, η_B 鏈 — 全由 0,1 導出",
      "🟢 無量綱扇區閉合")
c5_fail = True
print(f"  → C5 總評: 🔴 FAIL (維度定理要求 1 個有量綱錨; 現行錨 = r_d 聲學尺 / M_P / ω_ring, 全屬外部觀測輸入)")

# ─────────────────────────────────────────────────────
print("\n" + "=" * 72)
print("閉合五判準總表")
print("=" * 72)
table = [
    ("C1 歸一化",  "🟡/🔴", "G10 W₀ 分裂未決 (61.5 vs 1.23607); 其餘正則形式全 PASS"),
    ("C2 能證偽",  "🟢",   "≥8 條硬預言, 4 條現正有張力 (可一擊證偽)"),
    ("C3 能盲測",  "🟡",   "O49 中微子盲測 ✅ (零 Δm² 輸入); O144 輕子/重子質量公式 🔴 (z=−2.62); W-field 質量塔未驗"),
    ("C4 可預測",  "🟢",   "7 類預言: 4 類已命中 (BTFR/CMB峰/冷斑/UHECR), 2 類硬證偽待檢"),
    ("C5 零外部輸入", "🔴", "維度定理: 需 1 有量綱錨; 現行錨 = r_d 聲學尺/M_P/ω_ring (全外部) — 嚴格解讀未閉合"),
]
for cid, verdict, detail in table:
    print(f"  {cid}: {verdict} — {detail}")

n_pass = sum(1 for r in results if r[2])
n_fail = sum(1 for r in results if not r[2])
print(f"\n判準明細: {n_pass} PASS / {n_fail} FAIL")
print("總判: 5 判準中 2 🟢 (證偽/預測), 1 🟡-🔴 (歸一化, G10), 1 🟡 (盲測, 中微子過但 W-field 塔未驗), 1 🔴 (零外部輸入)")
print("⟹ W-Field 理論按用戶判準: **未閉合** — 阻塞點: C5 (1 個有量綱錨, 維度定理必然), C1 (G10), C3 (W-field 塔盲測)")
print("\n★ C5 解讀層 (必須誠實標明):")
print("  維度定理 (O73 §7) 係普適定理: 任何由無量綱結構常數出發之理論, 都要 1 個有量綱錨。")
print("  嚴格解讀 (零外部輸入量, 含單位錨): 🔴 未閉合 — 現行錨 = r_d 聲學尺 / M_P / ω_ring (全觀測)。")
print("  寬鬆解讀 (零自由參數, 錨只定單位): 🟢 已閉合 — 全部無量綱量由 0,1 導出, 錨只係單位選擇。")
print("  用戶判準字面 (『零外部輸入量』) 取嚴格解讀 ⟹ 判決: 🔴")
