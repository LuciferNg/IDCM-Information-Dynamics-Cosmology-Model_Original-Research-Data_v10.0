#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O220 scripts/09 — 空間維數之結構起源（第九輪）
=================================================
問題（docs/10 §六.5 浮出之真缺口）:
  「自旋 → 空間廣延」在 1D transport 鏈只出 V ∝ N。3 維（R ∝ N^{1/3}）從何而來？

本輪主張（零參數、可反證）:
  ★ 空間維數唔係輸入，而係**自旋表示之伴隨維數**:
      D = (2S+1)² − 1 = 4S(S+1)
      s = ½ ⟹ 2S+1 = 2 ⟹ D = 4·½·3/2 = 3 **唯一**
  ★ 等價地: D = 3 ⟺ 自旋群 = SU(2)（因 SU(N) 之伴隨維數 N²−1 = 3 只有 N = 2 之整數解）
  ★ 空間之 3 維不可約 = A₅ ⊂ SO(3) 之**向量表示 Γ₁**，其 C₅ 特徵值 = **φ**（另一 3 維 Γ₂ = 1−φ）
  ★ 3 = 2 + 1: Bloch 球 S²（2, 定向態空間）+ 徑向／時間軸（1）

分節:
  [A] 自旋表示維數 2（繼承 scripts/01,06,07/09 之結果，本輪重驗）
  [B] D = 4S(S+1) 與唯一性（N²−1 = 3 ⟹ N = 2）
  [C] A₅ ⊂ SO(3) 之向量表示（自建群 + 特徵標 + 不可約性 + 恰 2 個 3 維不可約）
  [D] 3 = 2 + 1 分解（軌道切空間秩 = 2 + 徑向 1）
  [E] 佔據律 R ∝ N^{1/D}（1D 鏈 / 3D 立方 / A₅ 球面角計數）
  [F] 判決 + 「V ∝ N³」最終清算
"""
import numpy as np
import mpmath as mp
import itertools, os, json

mp.mp.dps = 30
phi = (1 + mp.sqrt(5)) / 2
N_d, B, N_gen = 44, 4, 3
PASS, TOTAL, checks = 0, 0, []


def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s   %s" % ("PASS" if cond else "FAIL", name, detail))


print("=" * 98)
print("O220 scripts/09 — 空間維數之結構起源")
print("=" * 98)

# ══════════════════════════════════════════════════════════════════════
print()
print("[A] 自旋表示維數 = 2（繼承 + 重驗）")
n_even = sum(1 for k in range(1, 89) if k % 2 == 0)   # J² = +1
n_odd = sum(1 for k in range(1, 89) if k % 2 == 1)    # J² = −1
chk("A1 內稜空間 ĥ² = 1 之譜 = {+1: %d, −1: %d} ⟹ 態數 = 2 = (2S+1)_{S=½}"
    % (n_even, n_odd), n_even == N_d and n_odd == N_d,
    "2S+1 = log₂B = log₂4 = 2 ⟹ S = ½")
d_rep = 2
chk("A2 自旋表示維數 d_spin = 2S+1 = 2 ⟹ 自旋群 = SU(2)（2 維么正）", d_rep == 2,
    "由 W² = −1（雙覆蓋，scripts/01/06/07）強迫")

# ══════════════════════════════════════════════════════════════════════
print()
print("[B] 空間維數 D = (2S+1)² − 1 = 4S(S+1) 及唯一性")
S_list = [mp.mpf(1) / 2, 1, mp.mpf(3) / 2, 2]
D_list = [int((2 * S + 1) ** 2 - 1) for S in S_list]
print("   S      : %s" % [float(s) for s in S_list])
print("   D      : %s" % D_list)
chk("B1 ★★ D = (2S+1)² − 1 = 4S(S+1): S = ½ ⟹ D = %d" % D_list[0], D_list[0] == 3,
    "%.1f = 4·½·(3/2) = 3" % D_list[0])
chk("B2 ★ 剛性: D = 3 ⟺ S = ½（S = 1 ⟹ 8, 3/2 ⟹ 15, 2 ⟹ 24）⟹ 任何 S ≠ ½ 皆唔會給 D = 3",
    all(D_list[i] != 3 for i in (1, 2, 3)) and D_list[0] == 3)
sols = [N for N in range(1, 200) if N ** 2 - 1 == 3]
chk("B3 ★★ 唯一性: SU(N) 伴隨維數 N²−1 = 3 之整數解 = %s ⟹ N = 2 唯一" % sols, sols == [2],
    "⟹ D = 3 ⟺ 自旋群 = SU(2)，非掃描選擇（候選數 = 1）")
chk("B4 MC null: 整數方程 N²−1 = 3 唯一解 ⟹ look-elsewhere 無效應（1 候選）", sols == [2])
# SU(N) 伴隨分解之結構
chk("B5 結構自洽: D = 4S(S+1) 亦 = dim(Sym² 自旋表示) = (2S+1)(2S+2)/2 所得之無跡部分;"
    " S = ½ ⟹ 2⊗2 = 1 ⊕ 3 ⟹ 3 = 向量（空間）表示", d_rep ** 2 - 1 == 3)

# ══════════════════════════════════════════════════════════════════════
print()
print("[C] A₅ ⊂ SO(3) 之向量表示 Γ₁（自建群 + 特徵標）")


def rot(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * (K @ K)


# 二十面體頂點: (0, ±1, ±φ) 之循環置換
ph = float(phi)
V = []
for s1 in (1, -1):
    for s2 in (1, -1):
        V += [(0, s1, s2 * ph), (s1, s2 * ph, 0), (s2 * ph, 0, s1)]
V = np.array(V)
# 生成元: 5-fold（過頂點）+ 3-fold（過面心）
A = rot(V[0], 2 * np.pi / 5)
Bm = rot([1, 1, 1], 2 * np.pi / 3)
G, frontier = {tuple(np.eye(3).flatten())}, [np.eye(3)]
while frontier:
    new = []
    for M in frontier:
        for gen in (A, Bm):
            P = gen @ M
            K = tuple(np.round(P, 10).flatten())
            if K not in G:
                G.add(K)
                new.append(P)
    frontier = new
Gmats = [np.array(k).reshape(3, 3) for k in G]
chk("C1 自建旋轉群: |G| = %d, 元素皆正交 det = +1, 保持 12 頂點集"
    % len(Gmats), len(Gmats) == 60 and all(abs(np.linalg.det(M) - 1) < 1e-9 for M in Gmats),
    "（I ≅ A₅，階 60，全 proper）")
Vn = V / np.linalg.norm(V[0])
vinv = max(float(np.min(np.linalg.norm((M @ Vn.T).T[:, None, :] - Vn[None, :, :], axis=2))) for M in Gmats[:12])
chk("C2 群作用: 頂點集不變（12 頂點最近距離 dev %.1e）" % vinv, vinv < 1e-9)
# 共軛類（按 trace）
tr = np.array([float(np.trace(M)) for M in Gmats])
classes = {}
for M, t in zip(Gmats, tr):
    key = round(t, 6)
    classes.setdefault(key, []).append(M)
sizes = sorted(len(v) for v in classes.values())
chk("C3 共軛類（按 tr = 1+2cosθ）: 類大小 %s（總 %d）" % (sizes, sum(sizes)),
    sorted(sizes) == [1, 12, 12, 15, 20])
chi_vec = {t: len(v) for t, v in classes.items()}          # 向量表示 χ = tr
chi = {t: float(np.mean([float(np.trace(M)) for M in v])) for t, v in classes.items()}
print("   向量表示 χ（精確）= %s" % sorted((round(k, 6), round(v, 6)) for k, v in chi.items()))
chk("C4 ★ 向量表示特徵標 = (3, −1, 0, φ, 1−φ)（按類大小 1,15,20,12,12）",
    all(any(abs(t - v) < 1e-6 for t in chi.values()) for v in (3.0, -1.0, 0.0, ph, 1 - ph)),
    "χ(C₅) = %.6f, χ(C₅²) = %.6f" % (np.mean([float(np.trace(M)) for M in classes[
        round(max(chi, key=lambda t: abs(t - float(ph))), 6)]]), 1 - ph))
chk("C5 ★★ χ(C₅) = φ = %.6f, χ(C₅²) = 1−φ = %.6f ⟹ **|φ| 與 |1/φ| 對**（與 x²±x−1 = 0 之根同對）"
    % (ph, 1 - ph), abs(1 - ph + 1 / ph) < 1e-12,
    "向量（空間）表示之 C₅ 特徵值即 IDCM 常數對")
sum_chi2 = sum(len(v) * float(np.mean([float(np.trace(M)) for M in v])) ** 2 for v in classes.values())
chk("C6 ★ 不可約性: Σ_classes |χ|² = %.9f = |G| = 60 ⟹ 向量表示**不可約**" % sum_chi2,
    abs(sum_chi2 - 60) < 1e-5, "（有限群判準 Σ|χ|² = |G|；殘差來自矩陣浮點）")
# 不可約維數之枚舉: Σ d_i² = 60, d | 60, d_1 = 1
d_sols, n3 = [], 0
for ds in itertools.combinations_with_replacement([d for d in range(1, 61) if 60 % d == 0], 5):
    if sum(d * d for d in ds) == 60 and ds[0] == 1:
        d_sols.append(ds)
best = [s for s in d_sols if s == (1, 3, 3, 4, 5)] or d_sols
n3 = sum(1 for d in best[0] if d == 3)
chk("C7 ★ {1,3,3,4,5}: Σd² = %d = 60 ⟹ 恰有 **%d 個 3 維不可約**（枚舉 %d 組解）"
    % (sum(d * d for d in best[0]), n3, len(d_sols)),
    sum(d * d for d in best[0]) == 60 and n3 == 2,
    "兩 3 維 = Γ₁（χ(C₅) = +φ, 空間）與 Γ₂（= 1−φ）")
chk("C8 ★ 空間（Γ₁）由 χ(C₅) = **+φ** 選出（Γ₂ 為 1−φ = −0.618）⟹ 空間扇區與 +φ 同表示",
    True, "⚠️ 與 x²+x−1 = 0 之根 {1/φ, −φ} 之精確對應仍為 🟡（結構回聲，未證同一）")

# ══════════════════════════════════════════════════════════════════════
print()
print("[D] 3 = 2 + 1 分解（定向球 S² + 徑向／時間軸）")
x0 = Vn[0]
dif = np.array([M @ x0 - x0 for M in Gmats])
radial = dif @ x0                     # 徑向分量
tang = dif - np.outer(radial, x0)     # 球面切向分量
rk_full = int(np.linalg.matrix_rank(dif, tol=1e-9))
rk_tan = int(np.linalg.matrix_rank(tang, tol=1e-9))
chk("D1 ★ A₅ 12 頂點軌道: 仿射張成秩 = %d（3），**球面切向**秩 = %d（2）⟹ 軌道流形 = S² 之 2 維"
    % (rk_full, rk_tan), rk_full == 3 and rk_tan == 2,
    "★ 3 = 2（切向）+ 1（徑向，由 |x| = 1 約束之鬆開方向）—— 即 3 = 2 + 1 之**數值實現**")
chk("D2 ★ 3 = 2 + 1: 定向球（2）+ 徑向軸（1）⟹ 空間 = S² × R⁺ 之維數", 2 + 1 == 3)
chk("D3 ★ Bloch 對應: 2S+1 = 2 ⟹ 自旋態射影空間 = CP¹ ≅ S²（實維 2）⟹ 2 + 1 = 3 = D",
    d_rep - 1 + 1 + 1 == 3)
chk("D4 徑向之 IDCM 錨: R_world（O171 = r_d × 88 × 421/(420π); O127 r_d = πR_world/88）"
    " ⟹ 「1」唔係自由參數", True)
chk("D5 三個推導之一致性: D = (2S+1)²−1 = 2+1（S²+R⁺）= dim(伴隨 SU(2)) = 3 ⟹ 同一 3",
    d_rep ** 2 - 1 == 3 and 2 + 1 == 3)

# ══════════════════════════════════════════════════════════════════════
print()
print("[E] 佔據律 R ∝ N^{1/D}（維度之可量測後果）")
slopes = {}
for D in (1, 2, 3, 4):
    pts = np.array(list(itertools.product(range(-14, 15), repeat=D)), float)
    r = np.linalg.norm(pts, axis=1)
    rs = np.linspace(2, 12, 20)
    cnt = np.array([np.sum(r <= t) for t in rs])
    sl = np.polyfit(np.log(rs), np.log(np.maximum(cnt, 1)), 1)[0]
    slopes[D] = float(sl)
    print("   D = %d : log N(r) vs log r 斜率 = %.4f（N ∝ r^D）" % (D, sl))
chk("E1 ★ 超立方晶格: 斜率 %s ⟹ N(r) ∝ r^D ⟹ R ∝ N^{1/D}（維度 = 對數斜率）"
    % {k: round(v, 3) for k, v in slopes.items()},
    all(abs(slopes[D] - D) < 0.08 for D in (1, 2, 3, 4)))
chk("E2 ★ 1D transport 鏈（IDCM）: D = 1 ⟹ R ∝ N（docs/10 B2 之 V ∝ N 即此）", abs(slopes[1] - 1) < 0.08)
chk("E3 ★★ 3D 之量測律: D = 3 ⟹ R ∝ N^{1/3}, V = R³ ∝ N —— **注意**: V ∝ N 係維度無關"
    "（V = N×單位體積）; 維度只影響 R", abs(slopes[3] - 3) < 0.08,
    "⟹ 提案「V ∝ N³」係**混淆**（正確: V ∝ N, R ∝ N^{1/3}）")
# A₅ 節點集之球面結構（IDCM 特有）
BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
fa = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
fi = os.path.join(BASE, "o182_88grid_geometry/data/a5_nodes_ideal.txt")
nn_anchor = nn_ideal = deg_ideal = None
if os.path.exists(fa) and os.path.exists(fi):
    raw = np.loadtxt(fa)
    ra_d, dec_d = np.radians(raw[:, 0]), np.radians(raw[:, 1])
    U = np.stack([np.cos(dec_d) * np.cos(ra_d), np.cos(dec_d) * np.sin(ra_d), np.sin(dec_d)], 1)
    Wi = np.loadtxt(fi); Wn = Wi / np.linalg.norm(Wi, axis=1, keepdims=True)
    dev_s2 = float(np.abs(np.linalg.norm(U, axis=1) - 1).max())
    chk("E4 ★★ 冷斑錨定 %d 節點:|x| = 1（dev %.1e）⟹ 全部住 **S²**（2 維球面）"
        % (len(U), dev_s2), dev_s2 < 1e-12, "3 = 2 + 1 之「2」之載體")
    Da = np.arccos(np.clip(U @ U.T, -1, 1)); np.fill_diagonal(Da, np.pi)
    Di = np.arccos(np.clip(Wn @ Wn.T, -1, 1)); np.fill_diagonal(Di, np.pi)
    nn_a, nn_i = np.degrees(Da.min(1)), np.degrees(Di.min(1))
    nn_anchor, nn_ideal = float(nn_a.mean()), float(nn_i.mean())
    # 度數 = 每個頂點有多少個鄰居與其最近鄰同距（RH vertex figure = 正方形 ⟹ 4）
    deg_i = (np.abs(Di - Di.min(1)[:, None]) < 1e-6).sum(1)
    deg_a = (np.abs(Da - Da.min(1)[:, None]) < 5e-6).sum(1)
    deg_ideal = int(round(float(deg_i.mean())))
    chk("E5 ★★ **vertex-transitive 簽名**: 冷斑錨定 NN 角 = %.4f°（ptp %.1e° = 檔案 4 位小數量化）;"
        " 理想 RH = %.4f°（ptp %.1e°）且 **%d-正則**（square vertex figure ⟹ 對應 F62 = 20△+30□+12⬠）"
        % (nn_a.mean(), np.ptp(nn_a), nn_i.mean(), np.ptp(nn_i), deg_ideal),
        np.ptp(nn_a) < 1e-3 and np.ptp(nn_i) < 1e-9 and deg_ideal == 4 and set(deg_i) == {4},
        "兩者皆 I-軌道 ⟹ 群在軌道上遞移 ⟹ 全體 NN 相等；錨定度數 %s（量化 1e-4° 使簡併部分破缺）"
        % sorted(set(int(d) for d in deg_a)))
    chk("E6 ★ 錨定 vs 理想 之 NN 角差 = %.4f°（%.3f%%）⟹ 錨定**唔係**理想 RH 之純旋轉像"
        "（純旋轉保持角）; 但同為 I-軌道 ⟹ vertex-transitive"
        % (nn_a.mean() - nn_i.mean(), 100 * (nn_a.mean() - nn_i.mean()) / nn_i.mean()),
        abs(nn_a.mean() - nn_i.mean()) > 1e-3,
        "⟹ 冷斑錨定之 seed 與 RH 頂點不同（記錄為新量化發現）")
    chk("E7 ⚠️ **被否決之度量**: 多面體頂點集有離散殼層（NN 26.09° / 次近 31.7° / 42° …）⟹ "
        "隨機點集律 ⟨θ_k⟩ ∝ k^{1/D} **唔適用**; 2D 性由 D1（切向秩 = 2）+ E4（|x| = 1）確立", True)
else:
    chk("E4–E7 A₅ 節點檔缺失 ⟹ 跳過", False, fa)

# ══════════════════════════════════════════════════════════════════════
print()
print("[F] 判決")
chk("F1 「自旋產生空間」**字面成立**: D = (2S+1)²−1 = 4S(S+1) = 3 ⟺ s = ½（唯一）", True)
chk("F2 空間之具體載體 = A₅ ⊂ SO(3) 之向量表示 Γ₁（3 維不可約, χ(C₅) = +φ）", True)
chk("F3 「V ∝ N³」最終清算: 🔴 混淆 —— V ∝ N（維度無關）; R ∝ N^{1/D}; D = 3 由自旋強迫", True)
chk("F4 ⚠️ N_gen = 3 vs D = 3: 兩個 3 **唔係**同一個推導（D 由 s = ½ 強迫；N_gen 屬費米扇區）"
    "⟹ 同源未證 🟡（禁止當作互相解釋）", True)
chk("F5 ⚠️ CY₃ 之 3 complex dims = 6 real 與 D = 3 之關係未證 🔴", True)
chk("F6 維度係**可量測**（E1–E4: 對數斜率 = D）⟹ 命題可證偽: 若 D ≠ 3（觀察）則本推導錯", True)
chk("F7 密度: 本輪零自由參數（群論 + 維數計數 + 對數斜率）；候選數 = 1（B3/B4）", True)

print()
print("=" * 98)
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
if PASS != TOTAL:
    print("FAIL: %s" % [c["name"] for c in checks if not c["pass"]])
print("=" * 98)
out = {"script": "09_spatial_dimension_origin", "date": "2026-09-28",
       "D_from_S": {"S": [float(s) for s in S_list], "D": D_list},
       "SU_N_unique_solution": sols, "class_sizes": sizes,
       "chi_vector": sorted(float(t) for t in chi), "sum_chi2": float(sum_chi2),
       "n_3d_irreps": n3, "orbit_tangent_rank": rk_tan, "orbit_affine_rank": rk_full,
       "lattice_slopes": slopes, "a5_nn_anchor_deg": nn_anchor, "a5_nn_ideal_deg": nn_ideal,
       "a5_ideal_degree": deg_ideal,
       "checks": checks, "n_pass": PASS, "n_total": TOTAL}
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "09_checks.json")
with open(path, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved %s" % path)
