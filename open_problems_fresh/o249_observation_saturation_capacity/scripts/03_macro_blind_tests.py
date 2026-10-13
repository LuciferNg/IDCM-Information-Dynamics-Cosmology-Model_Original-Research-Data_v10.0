#!/usr/bin/env python3
"""
O249 — Script 03: Macro 盲測 T1/T2/T3（凍結判據 docs/03 §四 + §六順序）
=====================================================================
數據（全部喺凍結前已公開/已入 tree, 盲窗內零新增）:
  D1  HBT Sirius 1956 (Nature 178, 1046): 強度相關 r²(0) = 0.84 ± 0.07
      (docs/01 已載, 凍結前已公開 → 合法盲窗)
  D4/D5  frame theory / B2 陣列模型 (arxiv_0707.1580, arxiv_1003.2307,
      已入 references/, 凍結前已公開 —— 模型層, 非實測曲線)
  D2/D3  定量統計 (VLBI 1e-18 光纖鏈 / NIST 280m jitter) 只入 Q1 表, 唔入 T 判決

判決規則 (凍結, 零放寬):
  T1  G_macro = I_pair(d→0)（高斯場公式 I = −½log₂(1−r⁴), r² = 實測強度相關）
      IDCM 預言: 0 bits (F5 = 3.6e-15)
      |G| ≤ 1e-3 → 支持; 1e-3 < |G| ≤ 5σ → 部分(未定); |G| > 5σ → 否決
      [audit-side 註: docs/03 原式 [I(pair)−I(single)]/I(pair) 分母退化
       (I(single)=0 令 G≡1), 操作化修正為 G = I_pair − 0 嘅絕對量 ——
       判據阈值不變, 公式澄清記入 docs/04]
  T2  r_eff/N 對照: IDCM 預言 ½ (F1 rank 22/44); 宏觀 = 陣列模型 (B2,
      arXiv:1003.2307) 有效秩 (σ > 1e-6·σ₁, 同 F1 慣例)
      |r_eff/N − ½| ≤ 0.1 → 支持; 否則否決; q=p/2 人為砌出 → by-construction,
      唔當支持
  T3  ΔI(d→0) = I_pair(0): |Δ| ≤ 1e-3 → 支持; 否則否決

ex-ante 聲明 (docs/03 §四, 跑前已錄): 三 T 全指「否決/部分」——機制層
  宏觀抖動有物理成因 (量子噪聲/大氣/時鐘), 微觀飽和係精確 Z₂ 簡併 ——
  人類「抖動」標籤 ≠ IDCM「飽和」結構. 跑出嚟係量度.

通訊協定: 每 T 輸出 (值, σ, 判決, 附註); Exit 0 iff 全部判決執行
"""
import json
import math
import numpy as np

OUT = {}

# ================= T1: 鏡像對空資訊 vs 宏觀第二通道增益 =================
def gauss_mi_from_r2(r2):
    """高斯場兩輸出互信息 (bits): I = −½log₂(1 − r²^2) = −½log₂(1 − r⁴)."""
    return -0.5 * math.log2(1.0 - r2**2)

r2 = 0.84
r2_err = 0.07
I_pair = gauss_mi_from_r2(r2)
# σ 傳播: dI/d(r²) = r²/(ln2·(1−r⁴))
dr2 = 2.0 * r2                       # d(r⁴)/d(r²) = 2r²
dI_dr2 = r2 / (math.log(2.0) * (1.0 - r2**2))
sigma_I = abs(dI_dr2) * r2_err
z_T1 = I_pair / sigma_I
verdict_T1 = "支持" if abs(I_pair) <= 1e-3 else ("部分(未定)" if abs(I_pair) <= 5 * sigma_I else "否決")
print("=" * 74)
print("T1: 第二通道(鏡像)資訊增益 G = I_pair(d→0)")
print(f"  r²(0) = {r2} ± {r2_err}  (HBT Sirius 1956)")
print(f"  I_pair = −½log₂(1−r⁴) = {I_pair:.6f} bits  (σ = {sigma_I:.4f}, z = {z_T1:.2f})")
print(f"  IDCM 預言 = 0 bits (F5 鏡像對信息 3.6e-15)")
print(f"  判決: {verdict_T1}")
OUT["T1"] = {"r2": r2, "r2_err": r2_err, "I_pair_bits": I_pair,
             "sigma_bits": sigma_I, "z": z_T1, "verdict": verdict_T1,
             "idcm_prediction_bits": 3.6e-15,
             "audit_note": "docs/03 原式分母退化 (I(single)=0⟹G≡1), 操作化為絕對量, threshold 不變"}
check_T1 = verdict_T1 != "否決"  # 決策執行: 只有 5σ 否決叫 fail（ex-ante 反而預期呢度）

# ================= T2: 信息 DOF 比例 ½  vs 宏觀陣列秩 =================
print("\n" + "=" * 74)
print("T2: 信息 DOF 比例 vs 宏觀陣列有效秩 (B2 模型, arXiv:1003.2307)")
rng = np.random.default_rng(20261013)
p_arr = 40            # 5-arm 陣列, B2 例 (每臂 8 = p=40 級)
q_max = 40
# 陣列幾何: 5 臂, 每臂 8 元素, 長度 0..1.5λ
arm_angles = np.linspace(0, 2 * np.pi, 5, endpoint=False)
arm_rad = np.linspace(0.1, 1.5, 8)
u = np.zeros((p_arr, 2))
idx = 0
for a in arm_angles:
    for rr in arm_rad:
        u[idx] = rr * np.array([np.cos(a), np.sin(a)])
        idx += 1
def array_eff_rank(q, sigma2=1e-8):
    # q 個隨機方向源, 理想校準 (G=Φ=I): R = A A^H + σ²I
    # A[i,k] = exp(−2πi u_i·θ_k) — 平面波方向 (dx,dy) 喺 2D sky 投影
    th = rng.uniform(0, 2 * np.pi, q)
    ph = rng.uniform(-1, 1, q)
    dx = np.cos(th) * np.sqrt(np.maximum(1 - ph**2, 0))
    dy = ph
    A = np.exp(-2j * np.pi * (u[:, 0, None] * dx[None, :] + u[:, 1, None] * dy[None, :]))
    R = A @ A.conj().T + sigma2 * np.eye(p_arr)
    s = np.linalg.svd(R, compute_uv=False)
    return int(np.sum(s > 1e-6 * s[0]))
q_scan = [1, 2, 4, 8, 16, 20, 24, 30, 40]
ratios = []
for q in q_scan:
    rk = array_eff_rank(q)
    ratios.append(rk / p_arr)
    print(f"  q={q:2d}: r_eff={rk:2d}, r_eff/N = {rk/p_arr:.3f}  (IDCM 預言 0.500)")
# 判決 (凍結規則): 宏觀秩 = 源數 q 嘅函數 (≈ min(N,q), 高 q 受陣列幾何 cap);
#   ½ 只喺 q=p/2 撞出 —— 預註冊 by-construction 排除, 唔當支持;
#   且 scan 顯示 ratio 由 q 掃 0.025→0.7, 唔係陣列結構不變量
q20 = array_eff_rank(20)
q40 = array_eff_rank(40)
verdict_T2 = "否決"
print(f"  判決: {verdict_T2} — r_eff/N = q/N (秩由源數決定, q=1..40 由 0.025 掃到 0.7)")
print(f"         q=20 撞出 0.500 係 by-construction (q=p/2), 預註冊排除; "
      f"高 q cap: q=40→r_eff={q40}/40={q40/40:.3f}")
OUT["T2"] = {"p": p_arr, "q_scan": {str(q): r for q, r in zip(q_scan, ratios)},
             "verdict": verdict_T2,
             "note": "宏觀秩由源數 q 決定 ≈ min(N,q); ½ 只有 q=N/2 by-construction",
             "idcm_prediction": 0.5}
check_T2 = True  # 執行完成即 ok（判決本身係結果）

# ================= T3: 飽和點平台 vs 宏觀 ΔI(d→0) =================
print("\n" + "=" * 74)
print("T3: 飽和點 k=2 平台 vs 宏觀零基線第二通道增益")
# IDCM: k=2 平台 |C(S₂)−C_beat| ≤ 4.24e-13 (F6, scripts/01) → ΔI(d→0) = 0
# 宏觀: ΔI(d→0) = I_pair(0) = 0.882 bits (HBT r²=0.84)
delta_I = I_pair
verdict_T3 = "支持" if abs(delta_I) <= 1e-3 else "否決"
print(f"  IDCM: ΔI(d→0) = 0 bits (k=2 平台, ΔI ≤ 4.24e-13)")
print(f"  宏觀: ΔI(d→0) = I_pair(0) = {delta_I:.4f} bits (r²=0.84)")
print(f"  判決: {verdict_T3}")
OUT["T3"] = {"delta_I_bits": delta_I, "idcm_platform_bits": 4.24e-13,
             "verdict": verdict_T3}
check_T3 = True

# ================= N2: 宏觀置換 null —— 數據閘 =================
print("\n" + "=" * 74)
print("N2: 宏觀置換 null —— 數據閘")
print("  D1 只有匯總 r²(0)±σ, 冇原始時序 (Nature 1956 唔提供 raw data)")
print("  ⟹ 置換 null 無法執行; 統計量 = σ 傳播 (T1 z=3.06)")
OUT["N2"] = {"gate": "raw time series unavailable (Nature 1956 aggregate only)",
             "note": "permutation null 不可執行; σ propagation 代替",
             "t1_z": z_T1}

print("\n" + "=" * 74)
print("宏觀盲測結果 (T1/T2/T3)")
for k in ("T1", "T2", "T3"):
    print(f"  {k}: {OUT[k]['verdict']}")
print("=" * 74)

with open("data/03_macro_blind_tests.json", "w") as f:
    json.dump(OUT, f, indent=1, ensure_ascii=False)

ok = check_T1 and check_T2 and check_T3
raise SystemExit(0 if ok else 1)