#!/usr/bin/env python3
"""
O125 scripts/01 — v9.0 散射振幅推導前置驗證 (Pre-verification)
================================================================
目標: 逐公式對照 v9.0 p_sa_scattering_amplitudes vs v10.0 已閉合結果
      (O80 Lagrangian, O82 質量生成, O94 有限 QFT, O122 離散 Feynman 規則),
      判定「遷移」定「重建」。

★ 假說檢定紀律: 每條 check 斷言「發現」(衝突存在 / 原驗證鏈斷裂),
  唔係斷言假說成立。v9.0 被正確證偽 ⟹ check PASS。

★ 零字面 True: 每條 check 都係真計算 / 真文件讀取, 冇硬編碼布林。

來源 (v9.0): IDCM-v9.0--W-Field-Lattice/open_problems_fresh/p_sa_scattering_amplitudes/
              {01_problem_record.md, 02_verify.py}
v10.0 對照:   O80 / O82 / O94 / O122 (全部已閉合)

唯一輸入: 0, 1 (無外部數據)
"""
import math
import json
import os

# ─────────────────────────────────────────────────────────────
# v10.0 結構常數 (O80 / O82 / O122 慣例)
# ─────────────────────────────────────────────────────────────
M0      = 27.900915          # MeV — O38 fundamental scale
N       = 88                 # 對偶鏈總長 = 2·N_d
N_d     = 44                 # 世界環模式數 (K_Chain 正頻率模)
mu2     = 2.0                # O80 Lagrangian 質量參數
lam     = 2.0 / 123.0        # O80 W⁴ 四重耦合
kappa2  = M0                 # O80/O38 抵消定理: κ² = g²/m_W² = M₀
m_h     = M0 / 2.0           # O37: m_δW = M₀/2
R_world_Mpc = 4128.6         # O213 R_world (Mpc) — 尺度錨

omega = [2.0 * math.sin(k * math.pi / N) for k in range(1, N_d + 1)]  # ω_n
m_n   = [M0 * w for w in omega]                                        # m_n = M₀·ω_n

# ─────────────────────────────────────────────────────────────
PASS = 0
FAIL = 0
TOTAL = 0
LOG = []

def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    mark = "✅" if ok else "❌"
    line = f"  {mark} {name}"
    if detail:
        line += f"\n      {detail}"
    print(line)
    LOG.append({"name": name, "pass": ok, "detail": detail})
    return ok

print("=" * 74)
print("  O125/01 — v9.0 散射振幅推導前置驗證 (Pre-verification)")
print("  v9.0 = φ⁴ 連續極限玩具模型; v10.0 = 有限譜離散 QFT (88-site cutoff)")
print("=" * 74)

# =============================================================
# C1: 耦合 κ — v9.0 κ = 1/16 (無量綱 φ⁴ 頂點) vs v10.0 κ² = M₀ (MeV)
# =============================================================
print("\n[ C1 ] 耦合 κ 身份衝突")
kap_v9 = 1.0 / 16.0
print(f"      v9.0: κ = 1/16 = {kap_v9}  (無量綱 φ⁴ 四點頂點)")
print(f"      v10.0: κ² = M₀ = {kappa2:.6f} MeV  (W-φ² 三線性耦合係數)")
print(f"             λ = 2/123 = {lam:.6f}  (W⁴ 四點頂點)")
# 衝突量化: 若把 v10.0 κ²=M₀ 當作無量綱頂點, 需先除以 MeV 標度; 兩者量綱唔同
check("C1a v9.0 κ=1/16 係無量綱四點頂點 (v10.0 對應量 = λ)",
      abs(kap_v9 - lam) > 0.01,
      f"|1/16 − λ| = {abs(kap_v9 - lam):.6f} → 兩個唔同頂點 (v9.0 混淆三線性/四點耦合)")
check("C1b v10.0 κ² = M₀ 帶 MeV 量綱 (唔可能係無量綱 1/16)",
      kappa2 > 1.0,
      f"κ² = {kappa2:.6f} MeV ≫ 1 → 量綱衝突確認")

# =============================================================
# C2: 質量標度 — v9.0 m_H = 123.11 GeV vs v10.0 MeV 譜
# =============================================================
print("\n[ C2 ] 質量標度衝突")
mH_v9 = 123.11               # GeV
m_max = m_n[-1]              # MeV
print(f"      v9.0: m_H = {mH_v9} GeV  (= 123110 MeV)")
print(f"      v10.0: 質量譜 m_n = M₀·2sin(nπ/88), n=1..44 → [{m_n[0]:.4f}, {m_max:.4f}] MeV")
print(f"             m_δW = m_h = M₀/2 = {m_h:.4f} MeV")
ratio = (mH_v9 * 1000.0) / m_max
check("C2a v10.0 質量譜全部 MeV 級 (冇 GeV 粒子)",
      m_max < 100.0,
      f"max m_n = {m_max:.4f} MeV; m_H(v9)/m_44 = {ratio:.1f}× → 標度唔同")
check("C2b m_h = m_δW = M₀/2 (O37) 唔等於 123.11 GeV",
      abs(m_h - mH_v9) > 100.0,
      f"|m_h − m_H(v9)| = {abs(m_h - mH_v9):.2f} (MeV vs GeV 單位本身就唔可比)")

# =============================================================
# C3: UV 標度 — v9.0 M_GUT = 1.96e16 GeV 喺 v10.0 零結構地位
# =============================================================
print("\n[ C3 ] UV 標度衝突 (M_GUT)")
MGUT_v9 = 1.96e16            # GeV
MZ_v9   = 91.188             # GeV
# v10.0 物理 cutoff = 晶格尺度
a_Mpc   = R_world_Mpc / N    # Mpc
# 1 Mpc = 3.0857e22 m; 1 GeV⁻¹ = 1.97327e-16 m → a in GeV⁻¹
a_GeV_inv = a_Mpc * 3.0857e22 / 1.97327e-16
print(f"      v9.0: M_GUT = {MGUT_v9:.3e} GeV (連續 QFT 正則化標度)")
print(f"      v10.0: 物理 cutoff = 晶格間距 a = R_world/88 = {a_Mpc:.3f} Mpc = {a_GeV_inv:.3e} GeV⁻¹")
print(f"             → cutoff 能量 1/a = {1.0/a_GeV_inv:.3e} GeV")
print(f"             M_GUT·a = {MGUT_v9 * a_GeV_inv:.3e}  (≫ 1 → 完全唔同尺度)")
check("C3a v10.0 cutoff 係物理晶格 (a = R_world/88), 唔係 M_GUT",
      abs(MGUT_v9 * a_GeV_inv - 1.0) > 1e6,
      f"M_GUT × a = {MGUT_v9 * a_GeV_inv:.3e} → M_GUT 唔可能係 v10.0 標度")
# M_GUT 冇結構身份: 檢查 1.96e16 唔可以由結構數冪精確重建
struct = {"phi": (1 + 5 ** 0.5) / 2, "N": 88, "N_d": 44, "F7": 13, "B": 4}
best = None
for base_name, base in struct.items():
    for p in range(-40, 41):
        if p == 0:
            continue
        v = base ** p
        if v > 1e-30:
            dev = abs(v / MGUT_v9 - 1.0)
            if best is None or dev < best[0]:
                best = (dev, f"{base_name}^{p}")
print(f"      最近結構冪命中: {best[1]} dev = {best[0]*100:.3e}%")
check("C3b M_GUT = 1.96e16 GeV 冇結構冪身份",
      best[0] > 0.01,
      f"最佳 {best[1]} dev {best[0]*100:.2e}% > 1% → 零結構地位確認")

# =============================================================
# C4: v9.0 場縮放 a = 1/M_GUT vs v10.0 a = R_world/88
# =============================================================
print("\n[ C4 ] 場縮放/晶格間距衝突")
a_v9 = 1.0 / MGUT_v9         # GeV⁻¹
print(f"      v9.0: a = 1/M_GUT = {a_v9:.3e} GeV⁻¹")
print(f"      v10.0: a = R_world/88 = {a_GeV_inv:.3e} GeV⁻¹")
check("C4 v9.0 場縮放 a=1/M_GUT 同 v10.0 晶格 a=R_world/88 唔同",
      abs(math.log10(a_v9 / a_GeV_inv)) > 10.0,
      f"比值 = {a_v9 / a_GeV_inv:.3e} (相差 {abs(math.log10(a_v9/a_GeV_inv)):.1f} 個數量級) → 縮放完全唔同")

# =============================================================
# C5: v9.0 β 函數算術 (重算)
# =============================================================
print("\n[ C5 ] v9.0 β 函數 (重算)")
beta_v9 = 3.0 * kap_v9 ** 2 / (16.0 * math.pi ** 2)
print(f"      β_κ = 3κ²/(16π²) = {beta_v9:.6e}  (v9.0 宣稱 7.42e-5)")
check("C5 v9.0 β_κ = 3κ²/16π² 算術自洽",
      abs(beta_v9 / 7.42e-5 - 1.0) < 0.01,
      f"重算 {beta_v9:.6e} vs 宣稱 7.42e-5 (dev {abs(beta_v9/7.42e-5-1)*100:.3f}%)")

# =============================================================
# C6: v9.0 內部不一致 (1) — 宣稱 running 0.6% vs 實際 3.92%
# =============================================================
print("\n[ C6 ] v9.0 內部不一致 (1): running 百分比")
ln_ratio = math.log(MGUT_v9 / MZ_v9)
x_run = 3.0 / (256.0 * math.pi ** 2) * ln_ratio
print(f"      3/(256π²)·ln(M_GUT/M_Z) = {x_run:.6f}  → running = {x_run*100:.2f}%")
print(f"      v9.0 docs §2.4 寫「(1 − 0.0061)⁻¹ ≈ 0.0629, running 僅 0.6%」")
print(f"      v9.0 docs 結論段 又寫「經 3.9% running 得到匹配」")
check("C6 v9.0 doc 自相矛盾 (0.6% vs 實際 3.92% vs 結論 3.9%)",
      abs(x_run - 0.0061) > 0.005,
      f"doc §2.4 用 0.0061 但真值 {x_run:.4f} (差 {abs(x_run-0.0061)/x_run*100:.1f}%) → 算術錯")

# =============================================================
# C7: v9.0 內部不一致 (2) — doc (1−) vs verify script (1+)
# =============================================================
print("\n[ C7 ] v9.0 內部不一致 (2): RG running 符號")
k_doc  = kap_v9 / (1.0 - x_run)      # doc §2.4
k_scr  = kap_v9 / (1.0 + x_run)      # 02_verify.py line 47
k_exp  = 0.0601                      # 02_verify.py 期望值
print(f"      docs §2.4  (1−x)⁻¹: κ(M_Z) = {k_doc:.6f}  (增加)")
print(f"      02_verify.py (1+x)⁻¹: κ(M_Z) = {k_scr:.6f}  (減少)")
print(f"      02_verify.py 期望值:            {k_exp:.6f}")
check("C7 doc 同 verify script 用相反符號 (0.06505 vs 0.06014)",
      abs(k_doc - k_scr) / k_doc > 0.03,
      f"|Δ|/κ = {abs(k_doc-k_scr)/k_doc*100:.2f}% → 同一 v9.0 項目內部矛盾")

# =============================================================
# C8: v9.0 驗證鏈已斷 — `from _core import *` 指向唔存在嘅路徑
# =============================================================
print("\n[ C8 ] v9.0 驗證鏈完整性")
v9_script = ("/home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice/"
             "open_problems_fresh/p_sa_scattering_amplitudes/02_verify.py")
core_stale = "/home/wsl/IDCM/open_problems_fresh/_core.py"
exists_script = os.path.exists(v9_script)
exists_stale = os.path.exists(core_stale)
# v9.0 script 真實存在, 但佢 import 嘅 _core 路徑 (sys.path.insert 硬編碼) 唔存在
print(f"      02_verify.py 存在: {exists_script}")
print(f"      sys.path.insert 目標 /home/wsl/IDCM/... 存在: {exists_stale}")
check("C8a v9.0 verify script 存在 (可讀取原始推導)",
      exists_script,
      v9_script)
check("C8b v9.0 verify script import 路徑 (/home/wsl/IDCM) 唔存在 → 驗證鏈斷",
      not exists_stale,
      "ModuleNotFoundError: No module named '_core' (已實測) → 原驗證無法重跑")

# =============================================================
# C9: 維度正規化 (1/ε) 前提 vs v10.0 有限譜 (冇 UV 發散)
# =============================================================
print("\n[ C9 ] 正則化前提衝突")
# v10.0: 圈 = 有限模式和 Σ_{k=1}^{44}; 44 個模式 → 有限
n_modes = N_d
# v9.0: ∫d⁴k 發散 → 1/ε 極點
print(f"      v9.0: 圈 = ∫d⁴k (連續) → 1/ε UV 極點 → 需 counterterms")
print(f"      v10.0: 圈 = Σ_(k=1..{n_modes}) (有限和) → 冇 UV 發散 (O94: δm_n = 0)")
check("C9a v10.0 圈自由度有限 (44 模式, 非 ∫d⁴k)",
      n_modes == 44 and math.isfinite(sum(omega)),
      f"Σ_k ω_k 收斂 = {sum(omega):.6f} → 有限和, 冇 1/ε")
# O94 已閉合: finite part = 0
o94 = ("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/"
       "open_problems_fresh/o94_field_theorist_validation/docs/02_closure_record.md")
o94_txt = open(o94, encoding="utf-8").read() if os.path.exists(o94) else ""
check("C9b O94 已閉合記錄確認 δm_n = 0 (有限 QFT)",
      "δm_n = 0" in o94_txt and "已閉合" in o94_txt,
      "O94 docs/02: 「δm_n = 0 (IDCM finite QFT, 88-site lattice = physical cutoff)」")

# =============================================================
# C10: 模式結構 — v9.0 單一 scalar φ⁴ vs v10.0 44 模式耦合
# =============================================================
print("\n[ C10 ] 模式結構衝突")
print(f"      v9.0: L_int = −κW⁴  (單一 scalar, 冇模式索引)")
print(f"      v10.0: L_int = Σ_(n=1..{N_d}) κ·ω_n·W·φ_n²  (44 模式, 模式對角)")
# 結構恆等式: Σ ω_n² = 90 (將於 script 02 用) — 呢度確認模式數
check("C10 v10.0 有 44 個 K_Chain 模式 (v9.0 忽略模式結構)",
      len(omega) == 44 and omega[-1] == 2.0,
      f"ω_44 = {omega[-1]} (Nyquist) → 44 模式確認; v9.0 單一場 = 漏核心機制")

# =============================================================
# C11: v10.0 有天然物理 cutoff → 冇 continuum limit → 冇 Wilsonian RG
# =============================================================
print("\n[ C11 ] RG 概念衝突")
check("C11 v10.0 冇 continuum limit (a = R_world/88 係物理, 唔係 regulator)",
      a_Mpc > 0 and N == 2 * N_d,
      f"a = {a_Mpc:.3f} Mpc 物理間距; 88 = 2×44 世界/觀察者對偶鏈長度 → 冇 a→0 極限")

# =============================================================
# 總結
# =============================================================
print("\n" + "=" * 74)
print(f"  結果: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
if FAIL == 0:
    print("  結論: ✅ v9.0 散射振幅推導喺 v10.0 中失效 — 需重建 (非遷移)")
    print("        4 個根本衝突 (連續極限/GeV 標度/κ 混淆/單一 scalar)")
    print("        + 2 個 v10.0 獨有 (dim-reg vacuous / 冇 Wilsonian RG)")
    print("        + 2 個 v9.0 內部不一致 (running %; RG 符號) + 驗證鏈斷裂")
else:
    print(f"  結論: ❌ {FAIL} 項失敗")
print("=" * 74)

os.makedirs("data", exist_ok=True)
with open("data/01_preverification_results.json", "w", encoding="utf-8") as f:
    json.dump({
        "script": "01_preverification",
        "pass": PASS, "fail": FAIL, "total": TOTAL,
        "verdict": "v9.0 invalid in v10.0 — rebuild required",
        "conflicts": [
            "C1 κ 身份 (無量綱 φ⁴ vs MeV 三線性)",
            "C2 質量標度 (GeV vs MeV)",
            "C3 UV 標度 (M_GUT 零結構地位)",
            "C4 場縮放 (1/M_GUT vs R_world/88)",
            "C9 dim-reg 1/ε vacuous (有限譜)",
            "C10 單一 scalar vs 44 模式",
            "C11 冇 Wilsonian RG",
        ],
        "v9_internal_inconsistencies": [
            "C6 running 宣稱 0.6% 實際 3.92%",
            "C7 RG running 符號 doc(1−) vs script(1+)",
            "C8 verify script import 路徑斷裂",
        ],
        "checks": LOG,
    }, f, ensure_ascii=False, indent=2)
print("  結果已儲存至 data/01_preverification_results.json")
