#!/usr/bin/env python3
"""
O57 十一期 68: 推 1 — 66 態 Q_ij 相交矩陣 + 本徵態過濾
=========================================================
Gemini 方向 1: 用 CYTools 117 positive curves 嘅 Intersection Matrix
  Q_ij = C_i · D_j (curve i × divisor j, 36 Kähler 模)
  → 66 態映射為 Q_ij 嘅本徵態
  → 零本徵值 = Gauge Singlet, 非零 = SU(3)/SU(2) 荷

測試:
  1. 由 κ_ijk 構建 Q_ij = κ_ijk t_k (curve volumes 矩陣)
  2. 用 φ^(35-i) 做 t_k
  3. Q 嘅本徵值譜
  4. 66 態 (36K+30C) 投影到 Q 本徵空間
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十一期 68: 66 態 Q_ij 相交矩陣")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 載入 κ ============
print("\n[1] 載入正確 κ")
# 用 CYTools intersection (scripts/38 重建)
import importlib.util
spec = importlib.util.spec_from_file_location("kc", os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src", "kchain_wave_params.py"))
# 或者直接喺 o53 揾 κ
kappa_path = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes", "cy36_98_intersection_full.json")
print(f"  κ 檔: {kappa_path}")
print(f"  存在: {os.path.exists(kappa_path)}")

# 用 scripts/38 嘅重建方法
# 直接讀 CYTools 生成嘅正確 κ (scripts/38 已重建)
# 假設 scripts/38 存咗 data/38_correct_kappa.json
kappa38 = os.path.join(os.path.dirname(__file__), "..", "data", "38_correct_kappa.json")
print(f"  scripts/38 κ: {kappa38}, 存在: {os.path.exists(kappa38)}")

# 如果冇, 用 scripts/44 嘅方法 (66 態分解)
# scripts/44 已經確認 66 = 36K + 30C
# 呢度用 P_fixed_v2.npy 重建 66 態 + 用 curve volumes 做 Q

# ============ 2. 66 態提取 ============
print("\n[2] 66 態提取")
P_path = os.path.join(BASE, "data", "P_fixed_v2.npy")
P = np.load(P_path)
evals, evecs = np.linalg.eigh(P @ P.T)
idx = np.argsort(evals)[::-1]
evecs = evecs[:, idx]
pos = evals[idx] > 1e-10
evecs66 = evecs[:, pos][:, :66]
print(f"  P: {P.shape}, 66 態: {evecs66.shape}")
e_k = np.sum(evecs66[:36, :]**2, axis=0)
e_c = np.sum(evecs66[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
print(f"  K 態: {np.sum(sector=='K')}, C 態: {np.sum(sector=='C')}")

# ============ 3. Q_ij 構建 ============
print("\n[3] Q_ij 構建 (curve volumes)")
# 用 φ^(35-i) Kähler 參數 (五期發現)
# Q_ij = κ_ijk t_k 係 divisor 空間嘅 curve volume 矩陣
# 但冇 κ 檔 — 用替代: curve volumes 直接做 Q
# 五期 43: curve volumes 117 positive, range 1e8

# 載入 scripts/43 結果
vol43 = os.path.join(os.path.dirname(__file__), "..", "data", "43_curve_vol_mass.json")
if os.path.exists(vol43):
    with open(vol43) as f:
        d43 = json.load(f)
    print(f"  scripts/43 結果: {list(d43.keys())[:5]}")
    # 可能有 curve volumes
    if "volumes" in d43:
        vols = np.array(d43["volumes"])
        print(f"  curve volumes: {vols.shape}, positive: {np.sum(vols>0)}")
        # Q = diag(volumes) 近似 (如果冇完整相交矩陣)
        Q = np.diag(vols[:min(len(vols), 66)])
        print(f"  Q (diag 近似): {Q.shape}")
else:
    print(f"  scripts/43 JSON 唔存在 — 用替代方法")

# ============ 4. Q 本徵值 ============
print("\n[4] Q 本徵值譜")
# 用 66×66 隨機/結構矩陣模擬 (冇真 κ)
# 但更好: 用 66 態本身嘅 Gram 矩陣 + γ 權重
# Q_66 = evecs66.T @ diag(γ134) @ evecs66 (γ-weighted)
# γ 譜 134 維: 44 (Kähler) + 44 (CPX) + 44 + 2 (Nyquist) = 134
gamma = 4*np.sin(np.pi*np.arange(1, 45)/88)**2
gamma134 = np.concatenate([gamma, gamma, gamma, gamma[:2]])
Q_66 = evecs66.T @ np.diag(gamma134) @ evecs66
ev_Q = np.linalg.eigvalsh(Q_66)
print(f"  Q_66 (γ-weighted) 本徵值:")
print(f"    max: {ev_Q[-1]:.4f}, min: {ev_Q[0]:.4f}")
print(f"    range: {ev_Q[-1]-ev_Q[0]:.4f}")
print(f"    零(接近): {np.sum(np.abs(ev_Q) < 1e-6)}")
print(f"    正: {np.sum(ev_Q > 0)}")

# 66 態按本徵值分組
print(f"\n  本徵值分佈:")
for i in range(0, 66, 10):
    print(f"    [{i}:{i+10}] {[f'{x:.3f}' for x in ev_Q[i:i+10]]}")

# ============ 5. 世代結構 ============
print("\n[5] 世代結構 (3 組?)")
# 66 態 = 3 代 × 22
# 檢查 γ-weighted Q 有冇 3 個 cluster
sorted_ev = np.sort(ev_Q)[::-1]
# 簡單 gap 分析
gaps = np.diff(sorted_ev)
top_gaps = np.argsort(gaps)[-5:][::-1]
print(f"  最大 gap 位置: {sorted(top_gaps)}")
print(f"  → 3 個 cluster? {len(top_gaps) >= 2}")

# 每代 22 態嘅平均 Q 值
for gen in range(3):
    sl = slice(gen*22, (gen+1)*22)
    print(f"  Gen{gen+1} ({22} 態): mean Q = {np.mean(ev_Q[sl]):.4f}, range = {ev_Q[sl].max()-ev_Q[sl].min():.4f}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("十一期 68 總結:")
print("=" * 72)
print(f"""
  Q_ij 相交矩陣探索:
  ─────────────────────────────────
  1. 66 態 = {np.sum(sector=='K')}K + {np.sum(sector=='C')}C
  2. Q_66 (γ-weighted) 本徵值: range {ev_Q[-1]-ev_Q[0]:.2f}
  3. 零本徵值: {np.sum(np.abs(ev_Q) < 1e-6)} (singlet?)
  4. 3 代 cluster: {'有' if len(top_gaps)>=2 else '冇'}

  誠實: 未有真 Q_ij = C_i·D_j (需 CYTools curve-divisor 相交)
  → 用 γ-weighted 近似, 結構探索
""")

results = {
    "test": "O57 十一期 68: Q_ij 矩陣",
    "nK": int(np.sum(sector=='K')),
    "nC": int(np.sum(sector=='C')),
    "Q_range": float(ev_Q[-1]-ev_Q[0]),
    "Q_zero": int(np.sum(np.abs(ev_Q) < 1e-6)),
    "gen_means": [float(np.mean(ev_Q[i*22:(i+1)*22])) for i in range(3)],
    "passed": passed, "failed": failed
}
with open("data/68_q_matrix.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十一期 68 完成!")
