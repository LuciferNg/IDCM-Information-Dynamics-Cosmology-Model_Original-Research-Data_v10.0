#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""O247 Q2 攻堅 04 — K_Tree 過渡池盲測: 原子層 = 複合投影 or 單質投影 (判據預註冊)

調律者 2026-10-12: 「原子層不是複合投影就是單質投影，連續過渡公式應該在k-tree找」

結構根據:
- O157 R2: Γ = γ⊗λ (ΣΓ=5940), μ = metric 層 (φ-ladder 唔入譜因子)
- K_Tree λ_k = 4sin²(kπ/68), k=1..33 (Dirichlet chain, Σ=66=2K_tree) [O155/O157]
- O238 docs/11: 強子唔喺冪律層 (6<8.6) ⟹ 複合態投影要 O144 連結層
- scripts/01 池只有 K_chain 結構數, 冇 K_Tree 譜域 ⟹ 本 script 換池重測

兩個投影路 (調律者二選一):
- 單質投影: m_atom = M₀ × (K_Tree 譜/結構數) — 原子視為單一粒子直接投影
- 複合投影: 結合能 E_bind 有 K_Tree 結構身份 — 原子 = Σ核子 − E_bind

判據 (預註冊, 凍結):
  G1 K_Tree 池掃描: 目標 = {m_p/M₀, m_n/M₀, m_H/M₀, amu/M₀, m_He4/M₀,
     E_bind(He4)/M₀, E_bind(Fe56)/A/M₀} — 池 = K_Tree 專屬結構數 + 譜
  G2 MC null: 同池 log-uniform r∈[0.1,400] × 10000, 3% 窗 (譜數值跨度大)
     z = (h−mean)/std; z≥5 升候選, 3≤z<5 線索, z<3 否決
  G3 三點檢定: 過閘公式 (單質: 原子質量/M₀ 或 複合: E_bind/M₀) 必須喺 ≥2 個
     樣本外原子層量 (He4/Fe56/D2) 命中先升正式候選
  G4 連續過渡候選: Σ_{k=1}^{A} λ_k (A=1..33) 部分和 = 質量數 A 嘅過渡公式?
     對 E_bind 每核子曲線形狀 (7.07→8.79→7.57)

池定義 (K_Tree 專屬, 凍結):
  P_tree = {λ_k = 4sin²(kπ/68), k=1..33} ∪ {Σ_{k=1}^{A} λ_k, A=1..33}
         ∪ {66, 68, 176, 134, 42, 88, 55, 34, 17, 33, 22, 4, 16, 90, 61.5, 5940/90}
         ∪ {μ-ladder 對數標籤: 291.5−m, m=0..33}
         ∪ {B^p = 4^p, p=-5..5} ∪ {φ^q, q=-10..10}
         ∪ {λ_k/λ_j, k≠j} ∪ {λ_k × 33/66 等尺度} (唔加 — 保持池細, 密度可量度)
  P_tree 池規模記入 log (密度判定一部份)

觀測值 (PDG 2024 / NIST):
  M₀ = 27.900915 MeV
  m_p = 938.27208816, m_n = 939.5654205 MeV
  m_e = 0.51099895 MeV
  amu = 931.49410242 MeV (CODATA)
  m_H (氫原子) = 938.7830745 MeV (m_p + m_e − 13.598 eV)
  m_He4 (α粒子核) = 3727.3794066 MeV
  E_bind(He4) = 2m_p + 2m_n − m_He4 = 28.2957 MeV; 每核子 = 7.0739
  E_bind(Fe56)/A = 8.7903 MeV (鋫-56, 峰值), E_bind(D2)/A = 1.1123 MeV
"""
import math
import numpy as np

DELTA = 0.03
MC_N = 10000
Z_GATE = 5.0
Z_LINE = 3.0
logmin, logmax = 0.1, 400.0

# ---------- K_Tree 池 (凍結) ----------
lam = [4 * math.sin(k * math.pi / 68) ** 2 for k in range(1, 34)]
psums = []
s = 0.0
for v in lam:
    s += v
    psums.append(s)
phi = (1 + math.sqrt(5)) / 2
pool = set(lam) | set(psums)
pool |= {66, 68, 176, 134, 42, 88, 55, 34, 17, 33, 22, 4, 16, 90, 61.5, 5940 / 90}
pool |= {291.5 - m for m in range(34)}
pool |= {4 ** p for p in range(-5, 6)}
pool |= {phi ** q for q in range(-10, 11)}
# λ_k/λ_j (j≠k)
for k in range(33):
    for j in range(33):
        if j != k:
            pool.add(lam[k] / lam[j])
pool.discard(0.0)
pool_arr = np.array(sorted(pool))

# ---------- 觀測 ----------
M0, mp, mn, me = 27.900915, 938.27208816, 939.5654205, 0.51099895
amu = 931.49410242
mH = 938.7830745
mHe4 = 3727.3794066
Eb_He4 = 2 * mp + 2 * mn - mHe4
Eb_Fe56_A = 8.7903
Eb_D2_A = 1.1123
obs = {
    "m_p/M0 (單質)":       mp / M0,
    "m_n/M0 (單質)":       mn / M0,
    "m_H/M0 (單質)":       mH / M0,
    "amu/M0 (錨)":         amu / M0,
    "m_He4/M0 (單質)":     mHe4 / M0,
    "E_bind(He4)/M0":      Eb_He4 / M0,
    "E_bind(Fe56)/A/M0":   Eb_Fe56_A / M0,
    "E_bind(D2)/A/M0":     Eb_D2_A / M0,
}

def hits(r, arr=pool_arr, rel=DELTA):
    return int(np.sum(np.abs(arr / r - 1.0) < rel))

print("=" * 78)
print("G1+G2  K_Tree 過渡池盲測 (池=%d, 窗=%.0f%%, MC=%d)" % (len(pool_arr), DELTA * 100, MC_N))
print("=" * 78)
rng = np.random.default_rng(20261012)
null_r = np.exp(rng.uniform(math.log(logmin), math.log(logmax), size=MC_N))
null_hits = np.array([hits(r) for r in null_r])
print("null: mean=%.3f std=%.3f max=%d" % (null_hits.mean(), null_hits.std(), null_hits.max()))
results = []
for name, r in obs.items():
    h = hits(r)
    z = (h - null_hits.mean()) / null_hits.std()
    tag = "升候選" if z >= Z_GATE else ("線索" if z >= Z_LINE else "否決")
    print("%-22s r=%11.6f  命中=%d  z=%7.2f  ⟹ %s" % (name, r, h, z, tag))
    results.append((name, r, h, z, tag))

# ---------- G3 三點檢定 (只對 z≥3 目標) ----------
print()
print("=" * 78)
print("G3  三點檢定 (z≥3 目標嘅最近候選 → 樣本外兄弟值)")
print("=" * 78)
for name, r, h, z, tag in results:
    if z < Z_LINE:
        continue
    dev = np.abs(pool_arr / r - 1.0)
    i = int(np.argmin(dev))
    cand = pool_arr[i]
    dev_best = dev[i]
    print("★ %s: r=%.6f 最近候選=%g dev=%.4f%%" % (name, r, cand, dev_best * 100))
    # 樣本外: 同一候選套其餘原子層量
    others = [("He4", mHe4 / M0), ("amu", amu / M0), ("H", mH / M0),
              ("E_bind(He4)", Eb_He4 / M0), ("E_bind(Fe56)/A", Eb_Fe56_A / M0)]
    for oname, ov in others:
        if abs(ov / cand - 1.0) < DELTA:
            print("    ✅ 套 %-16s r=%8.5f  命中 (dev=%.3f%%)" % (oname, ov, abs(ov / cand - 1.0) * 100))
        else:
            print("    ✗ 套 %-16s r=%8.5f  (dev=%.2f%%)" % (oname, ov, abs(ov / cand - 1.0) * 100))

# ---------- G4 連續過渡候選: Σλ 部分和 vs 結合能曲線 ----------
print()
print("=" * 78)
print("G4  連續過渡: Σ_{k=1..A} λ_k 部分和 對 E_bind/A 曲線形狀")
print("=" * 78)
print("A  | Σλ(A)     | Σλ(A)/M0 (MeV)| obs E_bind/A (MeV) | dev")
print("---|-----------|----------------|--------------------|------")
Eb_curve = {2: 1.1123, 4: 7.0739, 12: 7.6801, 16: 7.9762, 56: 8.7903,
            100: 8.4700, 208: 7.8500, 238: 7.5700}
for A in (2, 4, 12, 16):
    p = psums[A - 1] if A <= 33 else None
    if p is None:
        continue
    pred = p * M0
    if A in Eb_curve:
        devA = abs(pred / Eb_curve[A] - 1.0) * 100
        print("%-3d | %10.5f | %14.3f | %18.4f | %.2f%%" % (A, p, pred, Eb_curve[A], devA))
print("(注意: A>33 唔喺 Σλ 範圍 — 過渡只覆蓋 A∈[1,33] = K_Tree levels; Fe56/U238 喺範圍外)")

print()
print("=" * 78)
print("RESULT")
print("=" * 78)
n_pass = sum(1 for _, _, _, z, _ in results if z >= Z_GATE)
n_line = sum(1 for _, _, _, z, _ in results if Z_LINE <= z < Z_GATE)
n_fail = sum(1 for _, _, _, z, _ in results if z < Z_LINE)
print("%d 檢查: %d 升候選 + %d 線索 + %d 否決" % (len(results), n_pass, n_line, n_fail))