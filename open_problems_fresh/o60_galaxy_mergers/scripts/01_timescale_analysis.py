#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60 星系合併 vs IDCM 自洽性 — 時標對照分析
=================================================
Massari+2026 (arXiv:2601.18896): LKH 合併 ~12.3 Gyr ago (ΛCDM 詮釋)
問題: IDCM 無膨脹/無 Big Bang/無宇宙年齡, 呢啲恆星年齡點解讀?

框架: IDCM v10.0 非膨脹宇宙
- z = 結構座標 ℓ = log₄(1+z), 唔係 lookback time
- τ = R_H/c = 13.470 Gyr = 渲染深度 (光行時間, 固定距離度量)
- T_sync = 84.635 Gyr = K_Chain SYNC 週期
- t_true = N·T_sync + τ = 11,100.64 Gyr (N=131, O51)
- 冇「宇宙年齡」— 只有結構週期 + 觀察窗

目的: 檢查「恆星年齡/合併時間線」喺 IDCM 框架下嘅自洽性
"""
import numpy as np

print("=" * 72)
print("O60: 星系合併歷史 vs IDCM 時標 — 結構自洽性分析")
print("=" * 72)

# ── IDCM 結構常數 ──────────────────────────────────────────
phi = (1 + 5**0.5) / 2
c = 299792.458          # km/s
R_H = 4129.94           # Mpc, K_Chain 環周長
H0_idcm = c / R_H       # km/s/Mpc = 72.59
tau = R_H / c * 1e3     # Gyr? R_H[Mpc]/c[km/s] → 需轉換
# R_H[Mpc] × 3.0857e19 km/Mpc / c[km/s] = 秒 → Gyr
# 1 Mpc = 3.085677581e19 km; 1 yr = 3.15576e7 s
tau_gyr = R_H * 3.085677581e19 / c / 3.15576e7 / 1e9
T_sync = 84.6349        # Gyr (O51)
N_true = 131
t_true = N_true * T_sync + tau_gyr

print(f"\nIDCM 時標:")
print(f"  τ = R_H/c           = {tau_gyr:.4f} Gyr  (渲染深度/光行時間)")
print(f"  T_sync              = {T_sync:.4f} Gyr  (K_Chain SYNC 週期)")
print(f"  t_true = {N_true}·T_sync + τ = {t_true:.2f} Gyr")

# ── Massari+2026 觀測數字 ──────────────────────────────────
print(f"\nMassari+2026 (arXiv:2601.18896) 觀測:")
print(f"  樣本: 39 GCs (17 新 CARMA + 22 文獻), HST F606W+F814W")
print(f"  族群: MW in-situ (黑) + GSE (青) + LKH (紅, 12 GCs)")
print(f"  LKH: ~5e8 M☉ 恆星, 內 6 kpc, [M/H]~-1.4")
print(f"  合併時間: t_accr(LKH) ≈ 12.3 Gyr ago, z>4")
print(f"  GSE: t_accr ≈ 10.5 Gyr ago")
print(f"  Sgr: ~6 Gyr ago (進行中)")
print(f"  最老 GC isochrone: t_iso = 14.48 Gyr")

# ── 關鍵: 恆星年齡 vs IDCM 週期宇宙 ─────────────────────────
print(f"\n{'='*72}")
print(f"核心問題: IDCM 無膨脹宇宙中, 恆星年齡 12-14 Gyr 點解讀?")
print(f"{'='*72}")

# 1. 年齡測量係框架無關
print(f"""
[1] 觀測事實 (框架無關):
    GC isochrone 年齡 ~10.5-14.5 Gyr 係「相對年齡」精密測量
    (CARMA 方法: 誤差 0.26 Gyr, 比文獻好 3.5×)
    呢啲係恆星演化物理, 唔依賴宇宙學模型 — 兩邊框架都要解釋

[2] ΛCDM 詮釋:
    宇宙年齡 13.8 Gyr = 大爆炸後時間
    LKH 合併 = 大爆炸後 1.5 Gyr (z>4)
    GC 年齡 14.48 Gyr ≈ 宇宙年齡 → 最早形成

[3] IDCM 詮釋 (結構座標):
    z 唔係時間, 係 K_Tree 結構座標 ℓ = log₄(1+z)
    LKH 合併喺 z>4 → ℓ > log₄(5) = 1.16 (K_Tree level 1-2)
    即合併發生喺「結構深度」~1.2 級, 對應尺度 ~1000 Mpc 級
    ⚠️ 但「發生喺幾時」喺 IDCM 冇唯一答案 — 只有週期相位
""")

# 2. 週期宇宙 vs 單調時間線: 恆星年齡作為相位
print(f"[4] 週期宇宙嘅「年齡」問題:")
print(f"    IDCM: 宇宙冇起始(只有種子)冇結尾, 週期 T_sync=84.6 Gyr")
print(f"    GC 年齡 12-14 Gyr ≈ 0.15 × T_sync")
print(f"    比率: 12.3/84.635 = {12.3/T_sync:.4f}  ≈ 1/6.88")
print(f"    比率: 10.5/84.635 = {10.5/T_sync:.4f}  ≈ 1/8.06")
print(f"    比率: 14.48/84.635 = {14.48/T_sync:.4f} ≈ 1/5.85")
print(f"    6.88 ≈ F₇-6.12? 8.06 ≈ F₆? 5.85 ≈ 2F₅-4.15?")
print(f"    → 冇明顯 Fibonacci/Lucas 整數結構 (偏差 >10%)")
print(f"    → 「恆星年齡 = 週期分數」無結構閉合 🔴")

# 3. 觀察窗解釋
print(f"""
[5] 觀察窗解釋 (IDCM 自然讀法):
    τ = 13.470 Gyr = 渲染深度 = 觀察者可見嘅最大光行時間
    GC 年齡 ≤ 14.48 Gyr ≈ τ (偏差 7.5%)
    → 所有可見恆星嘅年齡都被觀察窗限制: 冇恆星可以比 τ 老
    → 呢個係「結構必然」: 觀察窗內嘅嘢最多睇到 τ 咁老
    ⚠️ 但 14.48 > 13.470 (偏差 7.5%) — 需要解釋!
    t_iso = 14.48 Gyr vs τ = 13.470 Gyr:
    偏差 = (14.48-13.47)/13.47 = 7.5%
    候選結構: t_iso = τ/(1-φ⁻⁵/2) = 14.11 (偏差 -2.6%) 🟡
    候選結構: t_iso = τ·φ⁻¹·(1+1/44) = ? 待查
    ⚠️ 唔好聲稱 0.07% 閉合 — 實際係 -2.6% (已修正 2026-08-24)
""")

# 檢查 14.48 結構
t_iso = 14.48
pred = tau_gyr / (1 - phi**-5 / 2)
print(f"    檢查: t_iso = τ/(1-φ⁻⁵/2) = {pred:.4f} vs 14.48 → 偏差 {(pred-t_iso)/t_iso*100:.3f}%")
pred2 = tau_gyr * (1 + phi**-5/2)
print(f"    檢查2: t_iso = τ(1+φ⁻⁵/2) = {pred2:.4f} vs 14.48 → 偏差 {(pred2-t_iso)/t_iso*100:.3f}%")
print(f"    φ⁻⁵ = {phi**-5:.5f}, φ⁻⁵/2 = {phi**-5/2:.5f}")

# 4. 合併時間間隔 (相對, 框架無關)
print(f"""
[6] 合併時間線 (相對間隔 — 框架無關!):
    LKH - GSE = 1.8 Gyr
    GSE - Sgr = 4.5 Gyr
    Sgr - now = 6 Gyr
    序列: 12.3 → 10.5 → 6 → 0 (Gyr ago)
    間隔: 1.8, 4.5, 6.0
    比率: 4.5/1.8 = 2.5, 6.0/4.5 = 1.333
    2.5 = 5/2 = F₅/2 (Lucas L₃=4? no)
    1.333 = 4/3 (B/F₄? B=4, F₄=3 → 4/3!)
    1.8 = 1.8, 4.5 = 4.5, 6.0 = 6.0
    L₄=7, L₅=11, L₆=18: 1.8×10 = 18 = L₆! 
    4.5×2 = 9 = F₆+1? 6.0 = L₃+2?
    ⚠️ 數字太少 (3 個間隔), 不能斷言結構
""")

# 5. 本星系群質量階梯 (O32 M_d 階梯)
print(f"[7] 本星系群質量階梯 (O32 M_d 階梯, 框架無關 vs IDCM):")
M0 = 1.187e18  # M_sun, ρ_m·λ_sync³
for d in [3, 4, 5]:
    Md = M0 / 64**d
    print(f"    d={d}: M_d = {Md:.2e} M☉ ({Md/1e12:.1f} e12 或 {Md/1e9:.1f} e9)")
print(f"    d=4 對應銀河系尺度 7.1e10 M☉")
print(f"    LKH 5e8 M☉ ≈ d=5 嘅矮星系階梯 (1.1e9)")
print(f"    比率: 1.1e9/5e8 = 2.2 ≈ φ²=2.618? 偏差 16% 🟡")

# 6. 星系合併頻率 — 結構預測
print(f"""
[8] IDCM 對合併歷史嘅結構預測 (可證偽):
    K_Tree 33 級, B=4 分支 → 質量階梯 M_d = M₀/64^d
    每級合併「應該」發生喺特定結構深度 ℓ
    LKH (5e8) → d≈5, GSE (5e8) → d≈5, MW (5e10) → d≈4
    ⚠️ LKH 同 GSE 質量一樣 (都 5e8) 但「時間」差 1.8 Gyr
    → 質量階梯唔預測「時間順序」, 只預測質量等級
    → IDCM 需要一個「合併時鐘」機制先可以預測時間線 🔴 未推導

[9] 自洽性結論 (初步):
    ✅ 恆星年齡 ≤ τ 觀察窗附近 (12-14.5 Gyr vs 13.47 Gyr 渲染深度)
    🟡 14.48 Gyr isochrone 上限 vs τ = 7.5% 偏差
       (候選 t_iso = τ/(1-φ⁻⁵/2) = 14.11, 偏差 -2.6% — 未閉合)
    🟡 合併質量階梯 vs O32 M_d 階梯一致 (5e8 ≈ d=5)
    🔴 合併「時間順序」冇結構機制 — IDCM 冇合併時鐘
    🔴 12.3/10.5/6.0 Gyr 數字冇直接 Fibonacci/Lucas 結構
""")

# 7. 數字檢查: 12.3, 10.5, 6.0 vs 結構常數
print(f"[10] 合併時間點 vs IDCM 結構常數:")
vals = {"LKH": 12.3, "GSE": 10.5, "Sgr": 6.0, "t_iso": 14.48}
consts = {
    "τ": tau_gyr, "T_sync": T_sync, "τ/φ": tau_gyr/phi, "τ/φ²": tau_gyr/phi**2,
    "τ·φ⁻³": tau_gyr*phi**-3, "τ·φ⁻⁴": tau_gyr*phi**-4, "τ·φ⁻⁵": tau_gyr*phi**-5,
    "L₁₀·τ/44": 123*tau_gyr/44, "2τ/φ": 2*tau_gyr/phi
}
for name, v in vals.items():
    best = min(consts.items(), key=lambda kv: abs(kv[1]-v)/v)
    dev = abs(best[1]-v)/v*100
    print(f"    {name:6s} {v:6.2f} Gyr → 最近結構常數 {best[0]} = {best[1]:6.2f} (偏差 {dev:.1f}%)")

# 8. 關鍵: z>4 對應結構深度
z_lkh = 4.0
ell = np.log(1+z_lkh)/np.log(4)
print(f"\n[11] LKH z>4 → ℓ = log₄(1+z) = {ell:.3f}")
print(f"    K_Tree level 1 (4.03 Mpc 星系群) 同 level 2 (16.1 Mpc 星系團)")
print(f"    → LKH 合併喺結構深度 ℓ≈1.16, 即「星系群形成層」")

# 9. 預言: 本星系群結構檢查
print(f"""
[12] 本星系群 IDCM 自洽性檢查 (中小尺度!):
    O32 已閉合: 銀河系旋轉曲線 RAR/BTFR/SHMR (7 支柱)
    未檢查: 本星系群 (Local Group) 結構
      - M31 + MW + 衛星系 (~100 個)
      - 質量階梯: M31 ~1e12, MW ~1e12, LMC ~2e10, SMC ~7e9
      - O32 d=3: 4.5e12 (團), d=4: 7.1e10 (銀河系), d=5: 1.1e9 (矮)
      - M31+MW ~2e12 vs d=3 4.5e12 (偏差 56%) 🟡
      - LMC 2e10 vs d=4 7.1e10 (偏差 72%) 🟡
      - 但「本星系群係特殊環境」(雙大星系 + 潮汐) — 可能偏離平均階梯
    ⚠️ 需要更多本星系群質量數據先可以閉合
""")

print("=" * 72)
print("初步結論: 星系合併歷史係 IDCM 新嘅自洽性測試面")
print(" - 靜態結構 (旋轉曲線) 已閉合 (O32)")
print(" - 時間演化 (合併歷史) 未閉合 — 需要「合併時鐘」機制 🔴")
print(" - 恆星年齡 ≤ τ 觀察窗 ✅ 但 14.48>τ 偏差 7.5% 待解釋")
print("=" * 72)
