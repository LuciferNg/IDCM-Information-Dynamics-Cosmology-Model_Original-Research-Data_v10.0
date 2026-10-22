#!/usr/bin/env python3
"""
O38/m0-scale — 用戶問題 (2026-10-18): 可否從其他同樣需要 M₀ 嘅公式推導 N 嘅閉合?
==========================================================================
M₀ 唔只喺質量譜; 佢出現喺 κ²、⟨W⟩、m_δW、η_B 鏈、v_SM、m_e 定標等。
本 script 系統回答 [A]公式庫 [B]同源分類 [C]N 嘅多 pin 表達式 [D]探索表 [E]判定。

★ 核心問題: N = M₀/(ħω_ring) 可唔可以靠「另一條需-M₀ 公式 + 觀測 + 結構」閉合?
   答: 需要 ∃ 獨立 pin (觀測×結構, 唔同源)。
    若 pin 唔存在 ⟹ 所有需-M₀ 公式只係 M₀ 嘅線性重述 (同源) ⟹ N 仍開。
"""
from mpmath import mp, mpf, sqrt, sin, pi, log, exp, cos, floor
mp.dps = 60

print("=" * 76)
print("  O38/m0-scale — 需-M₀ 公式網交叉約束分析 (scripts/21)")
print("=" * 76)

M0   = mpf("27.900915")           # MeV (O38 閉合值)
m_e  = mpf("0.51099895000")       # PDG 2022 MeV
m_mu = mpf("105.6583755")         # PDG 2022 MeV
m_tau= mpf("1776.86")             # PDG MeV
m_p  = mpf("938.27208816")        # PDG 2022 MeV
m_7  = mpf("13.8002")             # IDCM M₀√γ₇
v_SM = mpf("246.2196")            # GeV (obs; 246219.6 MeV)
hbar_w = mpf("1.548431574e-39")   # ħω_ring 喺 MeV 制 = 1.548431574e−33 eV 嘅 MeV 單位
N_cur = M0/hbar_w                 # 現行 N

g7 = mpf("4")*sin(mp.pi/mpf("88")*mpf("7"))**2   # γ₇
print(f"  M₀     = {M0} MeV")
print(f"  ħω_ring= {hbar_w} MeV")
print(f"  N      = {N_cur} (1.80188233461e40)")
print(f"  m_e/m_μ/m_τ/m_p/m_7 = {m_e}, {m_mu}, {m_tau}, {m_p}, {m_7}")
print(f"  v_SM   = {v_SM} GeV (OBSERVED; O142 標記 🔴 未推導)")
print()

# ═══ [A] 需-M₀ 公式庫 + 同源分類 ═══
print("─── [A] 需-M₀ 公式庫 (source 分類) ───")
inventory = [
("m_n = M₀√γ_n",          "O34/O36",     "mass tower (∝M₀)",  "M₀-origin"),
("m_7 = M₀√γ₇ = 13.8002", "O34/O36",     "DM mass mode 7",    "M₀-origin"),
("κ² = M₀ (MeV 制)",      "O38/O37",     "κ̃²=88 closure",     "M₀-origin"),
("κ² = M₀·ω_scale",       "O38",         "dimensionful κ",    "M₀-origin"),
("⟨W⟩ = M₀",              "O37/O39",     "physical VEV",      "M₀-origin"),
("m_δW = M₀/2 = 13.9505", "O37",         "W-field mass",      "M₀-origin"),
("κ_bare²⟨W⟩² = M₀",      "O37",         "bare coupling",     "M₀-origin"),
("M₀ = m_e × F_e",        "O136 docs/36", "m_e 定標 5.0e−08",  "CALIBRATION"),
("v_SM = M₀ × f_v",       "O142 (open)", "v K-Chain 跳躍 🔴", "OPEN-DERIV"),
("Λ_IDCM = ρ√λ_max·M₀",   "O142 v16",    "cosm. scale",       "OPEN-DERIV"),
("m_μ/m_e = φ^(11+7/88)", "O34",         "lepton ladder",     "RATIO-ONLY"),
("η_B 鏈 (→ω_ring)",      "O168/scripts19", "dimension anchor", "ANCHOR-USED"),
]
for name, src, note, kind in inventory:
    print(f"  {name:34s} [{src:14s}] {kind}")
print("  → M₀-origin 全部 ∝ M₀ (同一標度源) ⟹ 各自唔提供獨立約束")
print("  → CALIBRATION: m_e 定標 (F_e 唔受機制強迫)")
print("  → OPEN-DERIV: v_SM 觀測已定但 IDCM 推導未閉合 (O142 🔴)")
print("  → RATIO-ONLY: 比例閉合, 不含 M₀ 絕對值 ⟹ 對 N 零約束")
print("  → ANCHOR-USED: 已經用喺維度側 (scripts/19)")
print()

# ═══ [B] 同源一致性: 每個 M₀-origin 公式嘅 M₀ 估計 ═══
print("─── [B] 同源一致性 (每個公式嘅 M₀ 估計 — 應該全部 ≡ M₀, 因為同一鏈) ───")
ests = {
    "κ² (MeV 制)":    M0,
    "κ²/ω_scale":     M0,          # ω_scale = 88ω_ring 已被 M₀ 定義吸收
    "⟨W⟩ (物理 VEV)": M0,
    "m_δW×2":         mpf("2")*mpf("13.9505"),
    "m_7/√γ₇":        m_7/sqrt(g7),
}
for name, v in ests.items():
    dev = abs(v - M0)/M0
    print(f"  {name:20s} = {float(v):.6f} MeV  dev = {float(dev)*100:.4f}%  {'✅ 同源' if dev < mpf('0.001') else '🟡 張力'}")
print("  (m_δW: 1.09% 張力 = 2√γ₇ = 0.98898 vs 1 — 已知內部張力, O37 已記錄)")
print()

# ═══ [C] N 嘅多 pin 表達式: N = obs_i × f_i / ħω_ring ═══
print("─── [C] N 嘅多 pin 表達式 (若 obs_i 有獨立結構 f_i) ───")
pins = [
    ("m_e  (定標)", m_e,  "F_e  = M₀/m_e"),
    ("m_7  (預言)", m_7,  "F_7  = M₀/m_7 = 1/√γ₇"),
    ("m_μ  (觀測)", m_mu, "F_μ  = M₀/m_μ"),
    ("m_p  (觀測)", m_p,  "F_p  = M₀/m_p"),
    ("v_SM (觀測)", v_SM*1000, "F_v  = M₀/v_SM"),
]
N_values = {}
for name, obs, desc in pins:
    f = M0/obs
    Ni = obs*f/(hbar_w)   # 恒等: Ni = M₀/ħω_ring
    N_values[name] = Ni
    print(f"  {name:12s} obs = {float(obs):12.6f}  {desc:24s} = {float(f):.6f}  ⟹ N = {float(Ni):.6e} (≡ 恒等)")
print("  ★ 數學: 若 f_i 由機制強迫閉合 → N 閉合。故問題 ⟹ f_i 有冇機制強迫？")
print()

# ═══ [D] 探索表 (後驗, 零閉合主張 — docs/36 判準: 掃描命中≠閉合) ═══
print("─── [D] f_i 結構探索 (後驗 — 唔過盲測協議, 只示範『有冇候選』) ───")
phi = (1+sqrt(5))/2
targets = {
    "F_e = M₀/m_e":  M0/m_e,
    "F_μ = M₀/m_μ":  M0/m_mu,
    "F_p = M₀/m_p":  M0/m_p,
    "f_v = v_SM/M₀": v_SM*1000/M0,
    "f_v⁻¹ = M₀/v_SM": M0/(v_SM*1000),
    "r_7e = m_7/m_e": m_7/m_e,
}
def nearest_structured(x, label):
    """最近嘅『低推理成本』候選: 整數/半整數/Fₙ/Lₙ/φ^p/q/137^p/q"""
    rows = []
    # 整數
    k = int(mp.floor(x+mpf("0.5")))
    rows.append((abs(x-k), f"{k} (integer)"))
    # 半整數
    h = int(mp.floor(2*x+mpf("0.5")))/2
    rows.append((abs(x-h), f"{h} (half)"))
    # φ^p (p 整數)
    p = mp.floor(mp.log(x)/mp.log(phi)+mpf("0.5"))
    rows.append((abs(x-phi**p), f"φ^{int(p)}"))
    # φ^{p/2}
    p = mp.floor(2*mp.log(x)/mp.log(phi)+mpf("0.5"))
    rows.append((abs(x-phi**(p/2)), f"φ^{int(p)}/2"))
    # 137^{k/4}
    k = mp.floor(4*mp.log(x)/mp.log(137)+mpf("0.5"))
    rows.append((abs(x-137**(k/4)), f"137^{int(k)}/4"))
    # 小數字表
    for c, cn in [(27,"3³"), (31,"π³"), (32,"2⁵"), (33,"M_tree"), (34,"2·17"),
                  (55,"F₁₀"), (61.5,"⟨W⟩²"), (88,"2N_d"), (90,"Σγ_even"),
                  (123,"3·41"), (137,"α⁻¹"), (256,"B⁴"), (8824.6,"?"),
                  (8836,"94²=4L₈²"), (4096,"B⁶")]:
        rows.append((abs(x-c), f"{cn}"))
    rows.sort(key=lambda r: r[0])
    return rows[:3]

for name, val in targets.items():
    print(f"\n  ● {name} = {float(val):.6f}   (log_φ = {float(mp.log(val)/mp.log(phi)):.4f})")
    for dev, cand in nearest_structured(val, name):
        mark = "★" if dev/val < mpf("1e-3") else " "
        print(f"    {mark} {cand:16s} dev = {float(dev):.6f} ({float(dev/val*100):.4f}%)")
    print("    判: 冇一個『機制強迫』⟹ 全部係後驗掃描命中 ⟹ 唔構成閉合 (docs/36 判準)")

print()
print("─── [E] 判定 ───")
print("""  1. 原理: N 閉合 ⟺ ∃ 獨立 pin (觀測×機制強迫結構, 同源以外)。
  2. 公式網: 所有 M₀-origin 公式 (m_n, κ², ⟨W⟩, m_δW, κ_bare) ∝ M₀ = 同一蹤。
  3. 獨立觀測候選:  m_e (定標 — F_e 冇機制) / v_SM (O142 🔴 未推導) /
     m_μ, m_p (冇 IDCM 公式) / Λ (open) ⟹ 全部未提供獨立 pin。
  4. ★ 重寫: N = M₀/(ħω_ring) = F_e·[m_e/(ħω_ring)]
     ⟹ N 嘅缺口 ≡ F_e = M₀/m_e 嘅缺口 ≡ 「電子喺 88-鏈嘅邊格」
     (O34 scripts/19 開放問題: e 嘅模態指數未解!) — 同一個洞, 兩個睇法。
  5. 交叉一致性: 全部需-M₀ 公式自洽 (因為同源); ratio-only (m_μ/m_e) 對 N 零約束。
  6. ⟹ 由其他公式推 N: ⚠️ 原理可行, 現況【冇獨立 pin】⟹ 維持 🔴
     → 最近可行路線 = O142 嘅 v_SM K-Chain 跳躍 (🔴 未推導, 屬他 O, 只可 register 發還)
     → 或 e 模態 (F_e) 機制強迫 — 需結構推導, 唔係掃描
""")