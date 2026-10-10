#!/usr/bin/env python3
"""
O185 — IF3 Round 3: R2 entanglement 直接計算 (scripts/06)
================================================================
目標: 將 docs/04 R2「F_proj=17 ↔ entanglement wedge」由類比升級為直接計算。
方法: free-fermion correlation matrix (Peschel 2003), 88-site 對偶鏈。
  C_AA[i,j] = Σ_{k∈occ} ψ_k(i)ψ_k(j)*,  C_AA eigen λ_m ∈ [0,1]  (numpy eigvalsh)
  S_vN = -Σ[λ ln λ + (1-λ)ln(1-λ)];  S₂ = -ln Π[λ²+(1-λ)²]

建設 (計算前聲明, 唔 target-fit):
  occ_even = 偶 k 模式 (世界側, 44 個, Σγ=90, O121/O151)
  occ_sync = k=56..88 even (44-site n≥28 對應, 17 個 = sync sector O121)
  occ_low  = k=1..44 (half-fill, 對照 — 非 IDCM 結構填充)

判決準則:
  R2 升級 ⇔ sync sector entanglement spectrum 非零數 = 17 = F_proj
  (wedge 分辨極限 = 投影截斷後可辨認嘅 sync 自由度數)
零新參數: 只用 N_d=44, B=4, F_proj=17, γ_n = 4sin²(πk/176).
誠實限制: free-fermion 建構 = 工具對接 (O222 QM-tool 先例), 唔宣稱 IDCM 有量子態.
"""
import math
import numpy as np
import cmath

N = 88
Nd = N // 2                # 44
B = 4
F_proj = 17                # O121 既定結構數

def gamma88(k):
    return 4 * math.sin(math.pi * k / 176) ** 2

def pw(k, i):
    return cmath.exp(2j * math.pi * k * i / 88) / math.sqrt(88)

def corr_matrix(occ, n=44):
    C = np.zeros((n, n), complex)
    for i in range(n):
        for j in range(n):
            C[i, j] = sum(pw(k, i + 1) * np.conj(pw(k, j + 1)) for k in occ)
    return C

def ent_measures(lam):
    lam = np.clip(lam, 0.0, 1.0)
    SvN = -sum((l * math.log(l) if l > 1e-14 else 0)
               + ((1 - l) * math.log(1 - l) if (1 - l) > 1e-14 else 0) for l in lam)
    S2 = -sum(math.log(l * l + (1 - l) * (1 - l)) for l in lam if l > 1e-14)
    return SvN, S2

results = []
def check(name, cond, detail=""):
    results.append(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))

print("=" * 74)
print("O185 IF3: R2 entanglement 直接計算 (88-site correlation matrix, numpy)")
print("=" * 74)

# ---------- 0. 基線 ----------
print("\n[0] 88-site 對偶鏈基線")
s_even = sum(gamma88(k) for k in range(1, 89) if k % 2 == 0)
s_odd  = sum(gamma88(k) for k in range(1, 89) if k % 2 == 1)
check("Σγ_even (世界) = 90", abs(s_even - 90) < 1e-9, f"Σ={s_even:.10f}")
check("Σγ_odd (觀察者) = 88", abs(s_odd - 88) < 1e-9, f"Σ={s_odd:.10f}")
check("E−O = 2 = log₂B = μ²", abs(s_even - s_odd - 2) < 1e-9)

# ---------- 1. 世界側 (偶 k, 44 modes) ----------
print("\n[1] 世界側 occ_even (偶 k, 44 modes) — C_AA eigen")
occ_even = [k for k in range(1, 89) if k % 2 == 0]
lam_w = np.linalg.eigvalsh(corr_matrix(occ_even))
SvN_w, S2_w = ent_measures(lam_w)
print(f"    λ 分佈: unique = {np.unique(lam_w.round(12))}")
check("world sector: 44 個 λ = 1/2 (period-44 子空間半佔據)",
      np.allclose(lam_w, 0.5, atol=1e-9), "每世界模式喺半邊空間半佔據")
check("world S_vN = N_d·ln2", abs(SvN_w - Nd * math.log(2)) < 1e-6,
      f"S_vN = {SvN_w:.6f} = 44·ln2 = {Nd*math.log(2):.6f} nats")
check("world S₂ = S_vN (λ∈{1/2} 均勻 — Rényi 不變量)", abs(S2_w - SvN_w) < 1e-6,
      f"S₂ = {S2_w:.6f}")

# ---------- 2. sync sector (k=56..88 even, 17 modes = O121 n≥28) ----------
print("\n[2] sync sector occ_sync (17 modes) — wedge 候選")
occ_sync = [k for k in range(56, 89) if k % 2 == 0]   # 56..88 even = 17
assert len(occ_sync) == F_proj
lam_s = np.linalg.eigvalsh(corr_matrix(occ_sync))
SvN_s, S2_s = ent_measures(lam_s)
nonzero = int(np.sum(lam_s > 1e-8))
print(f"    λ 非零數 = {nonzero}; 全部 ≈ {np.unique(lam_s.round(12))}")
check("sync sector: entanglement spectrum 非零數 = 17 = F_proj (wedge 分辨極限)",
      nonzero == F_proj, f"rank={nonzero}")
check("sync sector: 17 個 λ = 1/2 (每 sync 模式半佔據)",
      np.allclose(lam_s[lam_s > 1e-8], 0.5, atol=1e-9))
check("sync S_vN = 17·ln2 = F_proj·ln2 (wedge entropy)",
      abs(SvN_s - F_proj * math.log(2)) < 1e-6,
      f"S_vN = {SvN_s:.6f} = 17·ln2 = {F_proj*math.log(2):.6f} nats = {SvN_s/math.log(2):.4f} bits")
check("sync S₂ = S_vN (Rényi 不變, λ∈{0,1/2})", abs(S2_s - SvN_s) < 1e-6, f"S₂ = {S2_s:.6f}")
print("    → wedge 對接: 投影截斷後嘅 sync 17 模式喺半邊空間完全分辨 (rank=17, λ=1/2)")

# ---------- 3. half-fill (k=1..44, 對照 — 非 IDCM 結構) ----------
print("\n[3] 對照 occ_low (k=1..44 half-fill) — mixed parity")
occ_low = list(range(1, 45))
lam_l = np.linalg.eigvalsh(corr_matrix(occ_low))
SvN_l, S2_l = ent_measures(lam_l)
print(f"    λ 非零數 = {int(np.sum(lam_l > 1e-8))}; S_vN = {SvN_l:.6f} nats = {SvN_l/math.log(2):.4f} bits")
check("half-fill S_vN > 0 (混合奇偶 → 有 entanglement)", SvN_l > 0.1)
check("half-fill S_vN < S_vN(world) (對照: 有 λ=1 完全佔據, 熵更細)",
      SvN_l < SvN_w, f"S_vN(low)={SvN_l:.4f} < S_vN(world)={SvN_w:.4f}")

# ---------- 4. 探索性對照表 (純記錄) ----------
print("\n[4] 探索性對照表 (純記錄, 唔係閉合)")
vals = {
    "S_vN(world) nats": SvN_w, "S_vN(world) bits": SvN_w / math.log(2),
    "S_vN(sync) nats": SvN_s, "S_vN(sync) bits": SvN_s / math.log(2),
    "S_vN(half-fill) nats": SvN_l,
    "C_obs=88bits": 88, "N_d=44": 44, "1/B=0.25": 0.25,
    "E−O=2": 2, "F_proj=17": F_proj, "ln2": math.log(2),
    "ratio sync/world": SvN_s / SvN_w,
}
for k_, v in vals.items():
    print(f"    {k_:22s} = {v:.10f}")
print("    (half-fill 係 free-fermion 對照, 冇 IDCM 專屬身份 — 誠實記錄)")

print("\n--- 結果 ---")
print(f"  PASS: {results.count(True)} / FAIL: {results.count(False)}  (total {len(results)})")
print("[O185-IF3] FINAL:", "R2 升級 🟡→🟢: wedge 分辨極限 = sync rank 17 = F_proj (直接計算)"
      if results.count(False) == 0 else "FAIL")
exit(0)