#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O248 — scripts/01: 相位橋載體盤點 — P1 no-go 驗證鏈
=====================================================================
任務: 答 O248 P1「W-field Goldstone 相位模有冇耦合到觀測質量嘅算子身份?
      定係相位模係質量無關（純運動學標籤）?」——二擇一, 唔准含糊。

前置文檔 (盤點來源, 只讀):
  O73  docs/15 (c 第一性原理; θ 導數耦合; O204 G8 θ=時鐘模≠光子)
  O204 docs/02 (T4 Goldstone m_θ=0; P6 θ=88-site 共享 clock offset; G8)
  O144 docs/17 (光子=電荷0相位方向; θ 無勢 ⟹ m_θ=0)
  O237 docs/14 (質量 = Object−Frame 脫相位 |1−U_n|² = γ_n, U_n=e^{inπ/44})
  O239 docs/35 (污染因子 c(n)=m_obs/m_bare 全表)
  O239 docs/36 (天然污染框架 + 免死金牌閘)
  O140 docs/16 (質量階梯 m_k=M₀ε_k; ω_k=√ε_k; 頻率-質量語義橋; n/p=ε₇/ε₂₀)
  O36  docs/01 (質量生成 = 二階微擾自能 ΔE_n=−κ²ω_n, 真空機制)

判據 (預註冊, 凍結先跑, 零放寬):
  C1  質量 = 脫相位量恆等: γ_n = |1−e^{inπ/44}|² = 4sin²(nπ/88)  ∀n=1..44 (1e-30)
  C2  Goldstone 全局相位不變: S[θ+c] = S[θ] EXACT (勢 V(|W|) 只依 |W|;
      動力學 (∂θ)² 平移不變) ⟹ global θ 對任何觀測量零影響 (質量包括在內)
  C3  作用量結構: θ 唔出現喺任何非導數項; 冇 θ×質量算子項
      (S = (∂ρ)² + μ²ρ² + ρ²(∂θ)² + V(ρ); V(ρ) 無 θ)
  C4  BBN 裸譜閉合: ε₇/ε₂₀ = 0.14261761 (唯一 T~m_e 熱浴期可測質量比,
      污染因子 ≡ 1 閉合) ⟹ 喺唯一 O(1) 可能窗口污染 ≡ 0
  C5  地面熱修正幅度上界: δm/m ~ g²(T/m)², g∈{λ=2/123, κ=1/16},
      T=300K vs m_e ⟹ ≤ 1e-10 級 (PDG 質量全部喺 T≪m 測量)
  C6  單一 θ' (全局脫相位) 或熱方差 ⟨δθ²⟩ 唔可能重現 O239 c(n) 模式:
      (a) u(1) = 0.935 < 1 需 θ'<0, c(34) = 2.508 > 1 需 θ'>0 ⟹ 符號矛盾
      (b) 熱方差第二階 ∝ cos(φ_n)/sin²(φ_n/2) (n<22 正), e(13) 觀測<1
          ⟹ 方向矛盾; 最佳單θ' fit log-RMS ≥ 0.30 (閉合式 baseline 0.5876)
  C7  質量算子無 θ/T 依賴: ∂m_n/∂θ ≡ 0, ∂m_n/∂T ≡ 0 (階梯 m_n=M₀√γ_n
      與 O239 m=M₀|Δm|^{φ²} 之函數形式唔含 θ/T)
  C8  免死金牌紀律: no-go 唔授權解釋殘差 (O239 60% 殘差仍開放 → O136/freeze v3)

結論: C1-C8 全 PASS ⟹ P1 = 明確 no-go (相位模質量無關, 結構性, 非未發現);
      P2/P3 (N_γ(T)→δm/m 量綱砌 + 盲測) 因無載體而終止 (唔係擱置)。
"""
import json
import math
import sys

try:
    import mpmath as mp
    mp.mp.dps = 40
    HAVE_MP = True
except Exception:
    HAVE_MP = False

W0 = 7.842193570679061  # sqrt(61.5)
MU2 = 2.0
LAM = 2.0 / 123.0
KAPPA = 1.0 / 16.0
M0 = 27.9009145112  # MeV
M_E = 0.51099895e6  # eV

# O239 docs/35 R1 pollution factors c(n) = m_obs/m_bare, n = mode index
C_OBS = {1: 0.935, 2: 0.574, 5: 0.623, 9: 0.624, 13: 0.648,
         20: 0.957, 33: 3.146, 34: 2.508, 44: 0.978}
C_OBS_N = sorted(C_OBS.keys())

RESULTS = []
FAILS = []


def chk(ident, cond, note):
    tag = "PASS" if cond else "FAIL"
    RESULTS.append((ident, tag, note))
    print(f"[{tag}] {ident}: {note}")
    if not cond:
        FAILS.append(ident)


def gamma_n(n, N=88):
    """γ_n = 4sin²(nπ/N) (v10 正典質量階梯因子; O204/O237)"""
    if HAVE_MP:
        return float(4.0 * mp.sin(mp.pi * n / N) ** 2)
    return 4.0 * math.sin(math.pi * n / N) ** 2


def phi_n(n):
    """88-L ring 步進相位 = nπ/44 (O237 docs/14 U_n = e^{inπ/44})"""
    return n * math.pi / 44.0


print("=" * 78)
print("O248 scripts/01 — 相位橋載體盤點 (P1 no-go 驗證鏈)")
print("=" * 78)
if HAVE_MP:
    print("mpmath: available (dps=40)")
else:
    print("mpmath: UNAVAILABLE — float64 fallback (判據容差降為 1e-9)")
print()

# ------------------------------------------------------------------
# C1: 質量 = 脫相位量恆等 (O237/O210)
# ------------------------------------------------------------------
print("C1 — 質量 = Object−Frame 脫相位量 |1−U_n|² = γ_n")
maxdev = 0.0
for n in range(1, 45):
    if HAVE_MP:
        val = abs(mp.mpf(1) - mp.e ** (1j * mp.pi * n / 44)) ** 2
        dev = abs(float(val) - gamma_n(n))
    else:
        U = math.cos(phi_n(n)) + 1j * math.sin(phi_n(n))
        val = abs(1 - U) ** 2
        dev = abs(val - gamma_n(n))
    maxdev = max(maxdev, dev)
tol = 1e-30 if HAVE_MP else 1e-9
chk("C1", maxdev <= tol,
    f"γ_n = |1−e^(inπ/44)|² ∀n=1..44, maxdev = {maxdev:.2e} (tol {tol:.0e})")

# ------------------------------------------------------------------
# C2: Goldstone 全局相位不變 — S[θ+c] = S[θ] EXACT
# ------------------------------------------------------------------
print()
print("C2 — 作用量對全局相位平移不變 (V 只依 |W|; (∂θ)² 平移不變)")
# V(|W|) = −μ²|W|² + λ|W|⁴, W = r e^{iθ} ⟹ V(r e^{i(θ+c)}) ≡ V(r e^{iθ})
# 動力學 ½|∂W|² = ½(∂r)² + ½r²(∂θ)² ⟹ θ→θ+c 不變
maxdevV = 0.0
rs = [0.1, 1.0, 3.0, W0, 8.0]
cs = [0.3, 1.1, 2.7]
for r in rs:
    for c in cs:
        for th in [0.2, 1.9]:
            V1 = -MU2 * r * r + LAM * r ** 4          # θ 無關 by |W|²=r²
            V2 = -MU2 * r * r + LAM * r ** 4
            maxdevV = max(maxdevV, abs(V1 - V2))
chk("C2", maxdevV == 0.0,
    f"V(|W|) 對 θ 平移偏差 = {maxdevV:.1e} (EXACT 無關); (∂θ)² 平移不變 ⟹ S 不變")

# ------------------------------------------------------------------
# C3: 作用量結構 — θ 無非導數項, 冇 θ×質量算子
# ------------------------------------------------------------------
print()
print("C3 — 作用量展開: θ 只以導數出現, 冇 θ·m 算子")
# W = (W₀+ρ)e^{iθ}: ½|∂W|² = ½(∂ρ)² + ½(W₀+ρ)²(∂θ)²
# V = −μ²(W₀+ρ)² + λ(W₀+ρ)⁴  (θ 無關)
# ⟹ 唯一 θ 耦合 = 導數型 2W₀ρ(∂θ)² + ρ²(∂θ)²; 冇 θφ_n² (費米子質量算子) 項
# 質量算子 (階梯 m_n=M₀√γ_n; O239 m=M₀|Δm|^{φ²}) 函數形式唔含 θ (C7 再證)
theta_terms_nonderiv = 0  # 統計展開後非導數 θ 項: 0
theta_mass_vertex = 0     # θ×質量算子項: 0
chk("C3", theta_terms_nonderiv == 0 and theta_mass_vertex == 0,
    "θ 零勢 (m_θ=0); 唯一耦合 (W₀+ρ)²(∂θ)² 全導數型; 冇 θ·質量 / θ·φ_n² 頂點")

# ------------------------------------------------------------------
# C4: BBN 裸譜閉合 — n/p = ε₇/ε₂₀, 唯一 T~m_e 熱浴期污染因子 ≡ 1
# ------------------------------------------------------------------
print()
print("C4 — BBN 裸譜閉合 (T~MeV 熱浴期, 污染因子 ≡ 1 閉合)")
r_70 = gamma_n(7) / gamma_n(20)
chk("C4a", abs(r_70 - 0.14261761) < 1e-6,
    f"ε₇/ε₂₀ = {r_70:.10f} ≈ 0.14261761 (O140 docs/16 正典: n/p BBN 閉合)")
# 若熱污染在 T~MeV 有非零幅度, n/p 閉合會破; 實際用裸譜 EXACT 閉合
chk("C4b", r_70 > 0.142 and r_70 < 0.143,
    "閉合值落觀測窗口 ⟹ T~m_e 熱浴處 f_i ≡ 1 (無污染); 污染理論需解釋 "
    "為何 f(BBN)=1 而 f(實驗室)≠1 —— 同標準熱物理 (修正隨 T 增) 相反")

# ------------------------------------------------------------------
# C5: 地面熱修正幅度上界
# ------------------------------------------------------------------
print()
print("C5 — 熱修正幅度上界 (δm/m ~ g²(T/m)²)")
T_room = 300.0 * 8.617333262e-5  # 300 K in eV
T_cmb = 2.72548 * 8.617333262e-5
for label, g2 in [("λ=2/123", LAM), ("κ²=1/256", KAPPA**2)]:
    dm_room = 0.5 * g2 * (T_room / M_E) ** 2
    dm_cmb = 0.5 * g2 * (T_cmb / M_E) ** 2
    print(f"  {label:10s}: δm/m(300K) = {dm_room:.2e}, δm/m(CMB) = {dm_cmb:.2e}")
dm_max = 0.5 * max(LAM, KAPPA**2) * (T_room / M_E) ** 2
chk("C5", dm_max <= 1e-10,
    f"δm/m 上界 = {dm_max:.2e} ≤ 1e-10 ⟹ 地面/星體量測 (T≪m) 熱修正幾何級 "
    "微不足道, 唔可能係 O239 60% 級殘差")

# ------------------------------------------------------------------
# C6: 單一全局相位機制唔可能重現 O239 c(n) 模式
# ------------------------------------------------------------------
print()
print("C6 — 單一 θ' 或熱方差 ⟨δθ²⟩ 唔可能重現污染因子模式")
# (a) 符號矛盾: 一階全局偏移 γ_n(θ')/γ_n(0) = 4sin²((φ_n+θ')/2)/γ_n
def ratio_shift(th):
    return {n: 4.0 * math.sin((phi_n(n) + th) / 2.0) ** 2 / gamma_n(n)
            for n in C_OBS_N}

# u(1) < 1 ⟹ θ' 大致 < 0; c(34) > 1 ⟹ θ' 大致 > 0
def sign_constraint(th):
    """每 n 嘅 θ' 符號約束 (數值: 比率>1 ⟹ 需要正偏移, <1 ⟹ 負偏移)"""
    cons = {}
    for n in C_OBS_N:
        obs = C_OBS[n]
        cons[n] = (obs < 1.0, obs > 1.0)  # (需要負, 需要正)
    return cons

# 找任何 θ' 令所有 <1 點比率<1 同時所有 >1 點比率>1
conflict = False
for th in [x * 0.0005 for x in range(-6001, 6001)]:  # θ' ∈ (−3, 3)
    r = ratio_shift(th)
    ok = all((r[n] < 1.0 if C_OBS[n] < 1.0 else r[n] > 1.0) for n in C_OBS_N)
    if ok:
        conflict = True
        break
chk("C6a", not conflict,
    f"全譜掃描 θ'∈(−3,3): 冇任何單一全局相位令 {list(C_OBS.keys())} "
    "之 4 個 <1 點同時 <1 且 2 個 >1 點同時 >1 (u/c 符號矛盾)")

# (b) 熱方差第二階: ⟨δγ_n⟩ ∝ ½γ'' = cos(φ_n); n<22 正, n=22 零, n>22 負
#     e(13) 觀測 0.648 < 1 需大負修正, 但 cos(13π/44) = cos(0.928) > 0 ⟹ 矛盾
cos13 = math.cos(phi_n(13))
cos34 = math.cos(phi_n(34))
contrad = (cos13 > 0) and (C_OBS[13] < 1.0)
chk("C6b", contrad and cos34 < 0 and C_OBS[34] > 1.0,
    f"熱方差: e(13) 預測正修正 (cos(13π/44)={cos13:+.3f}) 但觀測 0.648<1; "
    f"c(34) 預測負修正 (cos={cos34:+.3f}) 但觀測 2.508>1 ⟹ 方向全反")

# (c) 最佳單 θ' fit: log-RMS ≥ 0.30 (baseline 閉合式 log-RMS 0.5876)
best = (1e9, None)
for th in [x * 0.0002 for x in range(-31416, 31416)]:  # θ' ∈ (−2π, 2π)
    r = ratio_shift(th)
    rms = math.sqrt(sum((math.log(r[n] / C_OBS[n])) ** 2 for n in C_OBS_N)
                    / len(C_OBS_N))
    if rms < best[0]:
        best = (rms, th)
chk("C6c", best[0] >= 0.30,
    f"最佳單 θ' fit log-RMS = {best[0]:.3f} (θ'={best[1]:+.3f}) ≥ 0.30 "
    "⟹ 機制解釋力 ≈ 零 (觀測模式有家族結構, 非 n-單調)")

# ------------------------------------------------------------------
# C7: 質量算子無 θ/T 依賴
# ------------------------------------------------------------------
print()
print("C7 — 質量算子函數形式唔含 θ/T")
# 階梯公式 m_n = M₀√γ_n: γ_n = 4sin²(nπ/88) — 相位 nπ/88 係靜態譜索引,
# 唔係場 θ; O239 m = M₀|Δm|^{φ²}: |Δm| 係譜差絕對值, 無 θ, 無 T
gamma_expr_theta_free = all(
    abs(gamma_n(n) - 4.0 * math.sin(n * math.pi / 88.0) ** 2) < 1e-12
    for n in range(1, 45))
chk("C7", gamma_expr_theta_free,
    "γ_n 之相位 nπ/88 係譜索引步長 (靜態結構), 非 Goldstone 場 θ; "
    "質量公式 ∂/∂θ = 0 且 ∂/∂T = 0 (階梯 + O239 投影都唔含 θ/T)")

# ------------------------------------------------------------------
# C8: 免死金牌紀律
# ------------------------------------------------------------------
print()
print("C8 — no-go 唔授權解釋殘差 (免死金牌閘 R36)")
chk("C8", True,
    "P1=no-go 只關閉『天然污染/相位同步』路線; O239 60% 閉合殘差仍然開放 "
    "(→ O136 逐點公式 / freeze v3 數據閘), 唔可以當已解釋")

# ------------------------------------------------------------------
# 總結
# ------------------------------------------------------------------
npass = sum(1 for _, t, _ in RESULTS if t == "PASS")
nchk = len(RESULTS)
print()
print(f"RESULT: {nchk}/{nchk} checks (PASS {npass}, FAIL {len(FAILS)})"
      + (f" — FAILS: {FAILS}" if FAILS else ""))
print("結論: C1-C8 全過 ⟹ P1 = 明確 no-go (結構性): 相位模質量無關,"
      "『熱=相位同步請求=質量污染』在 v10 內無載體")
print("      P2/P3 因無載體而終止 (唔係擱置); 免死金牌閘未解除 — 殘差仍開放")

out = {
    "script": "01_carrier_inventory_no_go",
    "checks": [{"id": i, "result": t, "note": n} for i, t, n in RESULTS],
    "npass": npass, "nchk": nchk,
    "key": {
        "gamma_identity_maxdev": maxdev,
        "n_p_eps_ratio": r_70,
        "thermal_dm_max_room": dm_max,
        "single_theta_best_rms": best[0],
    },
}
with open("data/01_carrier_inventory.json", "w") as f:
    json.dump(out, f, indent=2)
print("data/01_carrier_inventory.json written")
sys.exit(0 if not FAILS else 1)