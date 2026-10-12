#!/usr/bin/python3
"""O239 — Script 13: 模擬重整化合成數據（freeze v2 全套 = 偽 lattice ensemble）
============================================================================
調律者問題: 「即使沒有 lattice, 是否可以模擬類似重整化技術來合成數據?」

IDCM 現成「模擬 RG」組件（O140 已證）:
  1. 尺度精化 N_ℓ = 44·4^ℓ（SR = ℓ→∞ 極限）——層間密度×4
  2. 鏈乘法律 ε_a·ε_{44−a} = ε_{2a}（22/22 EXACT）⟹ m_{2a}=m_a·m_{44−a}/M₀
      ⚠ O140 已裁決「乘法律係鏈內結構, 唔係 SM 質量譜選取規則」→ 唔用作 SM 合成, 禁重推
  3. 質量-速度階梯共享: m ∝ γ_n, v = c·cos, γ_FSR = csc（同一 n）

本 script 用「偽 lattice ensemble」方法:
  freeze v2 提供 dŵ種 scheme 值（PDG pole / FLAG RGI / FLAG 3GeV·Nf4 ratio）
  —— 唔同 scheme = 唔同「renormalization 方案」= 偽 lattice ensembles
  做法: 用 freeze v2 全套 RGI/3GeV 值重建 9 質量組, 重跑 T3 冪律 γ/β/α,
         睇「scheme 全替換」下冪律穩唔穩。

預註冊判據:
  R1 基線重現: O206 組 γ = −4.7503 ± 0.37（重現 T3）
  R2 freeze v2 全替換組: u/d/s/c/b 用 freeze v2 RGI/3GeV 一致值
      γ_RGI vs γ₀ dev < 15% = 冪律對 scheme 全替換穩健
  R3 freeze v2 全替換組 R² > 0.95（冪律仍然成立, 唔係「換 scheme 就散」）
  R4 α_RGI/β_RGI 同 O206 版一致（< 15%）
  R5 鏈乘法律不重推: 只用於「確認唔可以用」——marker

合成數據注意:
  - freeze v2 冇 t 嘅 RGI 值 → t 保持 PDG pole 172.69（QCD 跑動對 t 影響小: pole-msbar ~9GeV）;
    誠實標注: t 係混合 scheme 唯一殘留
  - freeze v2 冇 e/mu/tau RGI → pole 保持（輕子冇強耦合跑動, pole 即物理質量）
  - freeze v2 有 u/d RGI + md/mu ratio + ms/mud? → 需由 freeze v2 值反重建:
    M_RGI_u = 2.97 +0.11/−0.03, M_RGI_d = 6.53 ±0.07/0.08
    mb_mc_3GeV = 4.586 ±0.012;  mc_ms_Nf4 = 11.652 ±0.065
    要組齊 9 質量: c 由 mc/ms×s 得, s 由?? freeze v2 冇直接 RGI_s ——
    用 PDG RGI_s = 130.0 ± 0.8（FLAG/PDG2024 同一來源）
"""
import json, math
import numpy as np
from scipy import stats

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/13 — 模擬重整化合成數據（freeze v2 偽 lattice ensemble）")
print("=" * 78)

labels = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
n_modes = [1, 2, 3, 4, 5, 7, 9, 11, 13]
theta = np.array([n * np.pi / 88 for n in n_modes])
lt = np.log(theta)

# 基線（O206/PDG2024 = freeze v1.0）
M0 = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])

# ── R1: 基線重現 ──
r0 = stats.linregress(lt, np.log(M0))
g0 = r0.slope
print("\n── R1: 基線（O206/PDG2024, freeze v1.0）──")
print(f"   γ₀ = {g0:.4f} ± {r0.stderr:.4f}  R² = {r0.rvalue**2:.4f}")
chk("R1 基線重現 (γ ≈ −4.75)", abs(g0 + 4.75) < 0.5, f"γ₀={g0:.4f}")

# ── R2/R3: freeze v2 全替換組 ──
# u=2.97(RGI), d=6.53(RGI), s=130.0(RGI, PDG/FLAG), c = mc/ms×s = 11.652×130.0
# b = mb/mc×c = 4.586×c; t 保持 pole（冇 RGI）; 輕子保持 pole
print("\n── R2: freeze v2 全替換組（u/d/s RGI + c/b 由 freeze v2 ratio + t pole）──")
u_v2, d_v2, s_v2 = 2.97, 6.53, 130.0
mc_v2 = 11.652 * s_v2
mb_v2 = 4.586 * mc_v2
M_v2 = np.array([172690.0, mb_v2, 1776.86, mc_v2, 105.6584, s_v2, d_v2, u_v2, 0.510999])
print(f"   重建: u={u_v2}, d={d_v2}, s={s_v2}, c={mc_v2:.1f} (11.652×{s_v2}), "
      f"b={mb_v2:.1f} (4.586×{mc_v2:.1f})")
r_rgi = stats.linregress(lt, np.log(M_v2))
g_rgi = r_rgi.slope
dev_rgi = abs(g_rgi - g0) / abs(g0)
print(f"   γ_RGI = {g_rgi:.4f} ± {r_rgi.stderr:.4f}  R² = {r_rgi.rvalue**2:.4f}")
print(f"   vs γ₀ dev = {dev_rgi*100:.1f}%")
chk("R2 scheme 全替換 dev < 15%", dev_rgi < 0.15, f"dev={dev_rgi*100:.1f}%")
chk("R3 全替換組 R² > 0.95", r_rgi.rvalue**2 > 0.95, f"R²={r_rgi.rvalue**2:.4f}")

# ── R4: α/β 一致性（|dm| 冪律唔變）──
# 用 O206 9 模態 dm（data/09）做 β, 質量換組後 α = γ/β 唔變?
O9 = json.load(open("data/09_o206_inputs.json"))
dm9 = np.abs(np.array(O9["dm9"]))
r_beta = stats.linregress(lt, np.log(dm9))
beta0 = r_beta.slope
alpha0 = g0 / beta0
alpha_v2 = g_rgi / beta0
print("\n── R4: α = γ/β scheme 全替換──")
print(f"   β = {beta0:.4f}（|dm| 冪律, 唔受質量 scheme 影響——係譜量）")
print(f"   α₀ = {alpha0:.4f}（O206 版）, α_RGI = {alpha_v2:.4f}  dev = {abs(alpha_v2-alpha0)/abs(alpha0)*100:.1f}%")
chk("R4 α scheme 全替換 dev < 15%", abs(alpha_v2 - alpha0) / abs(alpha0) < 0.15,
    f"dev={abs(alpha_v2-alpha0)/abs(alpha0)*100:.1f}%")

# ── R5: 鏈乘法律 marker（禁重推）──
print("\n── R5: 鏈乘法律──")
print("   ⚠ O140 已裁決: ε_a·ε_{44−a}=ε_{2a} 係鏈內結構 (22/22),")
print("     但「SM 質量譜選取規則」唔存在於乘積方向（946 網格 null 26.1%）")
print("     ⟹ 唔用作 SM 質量合成——本 script 只用「scheme ensemble」方法")
chk("R5 不重推已否證路線", True, "marker: 鏈乘法律只記唔用")

json.dump({
    "R1_gamma0": g0, "R1_R2": r0.rvalue**2,
    "R2_gamma_v2": g_rgi, "R2_dev": float(dev_rgi), "R2_R2": r_rgi.rvalue**2,
    "R2_rebuilt": {"u": u_v2, "d": d_v2, "s": s_v2, "c": mc_v2, "b": mb_v2},
    "R4_alpha0": alpha0, "R4_alpha_v2": alpha_v2,
    "R5_note": "鏈乘法律係鏈內結構唔係SM選取規則 (O140), 禁重推",
    "note": "freeze v2 偽 lattice ensemble: u/d/s RGI + c/b freeze v2 ratio + t/輕子 pole",
}, open("data/13_synthetic_rg.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")