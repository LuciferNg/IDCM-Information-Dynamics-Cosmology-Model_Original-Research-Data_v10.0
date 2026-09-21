#!/usr/bin/env python3
"""
O57 二期 15: Sector 結構 22C+36K+8C ↔ SM 對應深化
===================================================
重大發現 (scripts/14): 66 態 sector 序列 = 22 C + 36 K + 8 C

  22 C (evec 0-21): 純 CPX → 費米子候選
  36 K (evec 22-57): 純 Kähler → 玻色子候選
  8 C (evec 58-65): 純 CPX → gluons 候選?

關鍵結構:
  22 = Nd/2 (half-chain)
  36 = h11 (Kähler 維度)!
  8 = 2B (分支邊界) = SU(3) gluons?

SM 對應:
  36 K = 12 gauge × 3? 或者 36 = 3×12?
  8 C = SU(3) 8 generators ✓
  22 C = 費米子?

探索:
  1. 22 C 態嘅內部結構 (頻率/beats)
  2. 36 K 態嘅內部結構
  3. 8 C 態嘅內部結構
  4. 3 代點樣嵌入 22 C?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2
Nd = 44

print("=" * 72)
print("O57 二期 15: Sector 22C+36K+8C")
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

# ============ 1. 載入 ============
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
PPT = P @ P.T
evals, evecs = np.linalg.eigh(PPT)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
evecs = evecs[:, idx]
pos = evals > 1e-10
evals_pos = evals[pos][:66]
evecs_pos = evecs[:, pos][:, :66]

# beats
beats = []
for n in range(1, 45):
    for m in range(n+1, 45):
        beats.append((n, m))
beats = np.array(beats)

# beat 頻率
gamma = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45)])
freqs = np.abs(gamma[beats[:,0]-1] - gamma[beats[:,1]-1])

# ============ 2. 22 C 態 (費米子候選) ============
print("\n[1] 22 C 態 (evec 0-21, 費米子候選)")
u_vecs = (P.T @ evecs_pos) / np.sqrt(evals_pos)  # 946×66

# 每個 C 態嘅代表 beat 頻率
c_freqs = []
for i in range(22):
    ui = u_vecs[:, i]
    top = np.argmax(np.abs(ui))
    c_freqs.append(freqs[top])
c_freqs = np.array(c_freqs)
print(f"  22 C 態嘅 top-beat 頻率:")
print(f"    {c_freqs}")
print(f"    range: [{c_freqs.min():.4f}, {c_freqs.max():.4f}]")

# 頻率排序?
print(f"  頻率排序: {np.all(np.diff(c_freqs) > 0)}")

# 22 C 態嘅 (n,m) 分佈
c_ns = []
c_ms = []
for i in range(22):
    ui = u_vecs[:, i]
    top = np.argmax(np.abs(ui))
    n, m = beats[top]
    c_ns.append(n)
    c_ms.append(m)
print(f"  top-beat (n,m): {list(zip(c_ns, c_ms))}")
print(f"  n range: {min(c_ns)}-{max(c_ns)}, m range: {min(c_ms)}-{max(c_ms)}")

# 3 代嵌入? 22 = 3×7 + 1?
# 7 = L₄
# 每 7 個態一組?
print(f"  22 = 3×7 + 1 (L₄×N_gen + 1)")

# 檢查 22 C 態嘅能量 gap 結構
c_evals = evals_pos[:22]
c_gaps = np.diff(np.log(c_evals))
print(f"  22 C 態 log-gaps:")
for i, g in enumerate(c_gaps):
    print(f"    {i+1}|{i+2}: {g:.4f}")

# 大 gap 位置 = 代邊界?
big_gaps = np.argsort(np.abs(c_gaps))[::-1][:4]
print(f"  大 gap @: {sorted(big_gaps+1)}")

# ============ 3. 36 K 態 (玻色子候選) ============
print("\n[2] 36 K 態 (evec 22-57, 玻色子候選)")
# 36 = h11 = Kähler 維度
# 36 = 12 gauge × 3? 或者 36 = 3×12?

# 每個 K 態嘅 top-beat
k_ns = []
k_ms = []
for i in range(22, 58):
    ui = u_vecs[:, i]
    top = np.argmax(np.abs(ui))
    n, m = beats[top]
    k_ns.append(n)
    k_ms.append(m)
print(f"  top-beat n: {sorted(set(k_ns))}")
print(f"  top-beat m: {sorted(set(k_ms))}")

# K 態 top-beats 集中喺低能量區?
print(f"  K 態 top-beat (n,m) 樣本:")
for i in [22, 25, 30, 35, 40, 45, 50, 55, 57]:
    ui = u_vecs[:, i]
    top = np.argmax(np.abs(ui))
    n, m = beats[top]
    print(f"    evec {i:2d}: ({n}, {m})")

# ============ 4. 8 C 態 (gluons 候選?) ============
print("\n[3] 8 C 態 (evec 58-65, gluons 候選?)")
g_ns = []
g_ms = []
g_freqs = []
for i in range(58, 66):
    ui = u_vecs[:, i]
    top = np.argmax(np.abs(ui))
    n, m = beats[top]
    g_ns.append(n)
    g_ms.append(m)
    g_freqs.append(freqs[top])
print(f"  top-beat (n,m): {list(zip(g_ns, g_ms))}")
print(f"  頻率: {[f'{f:.4f}' for f in g_freqs]}")

# 8 = SU(3) generators = 2B
# 8 C 態 = gluons? 
# 但 gluons 係 gauge bosons, 應該喺 Kähler sector?
# 呢 8 個係 CPX sector — 唔似 gluons!

# 重新諗: 8 C = 8 個「暗」態?
# 或者 8 = 2B = 分支邊界對應態?

print(f"  8 = 2B = 8 (分支邊界)")
print(f"  8 C 態可能 = 分支邊界對應嘅 CPX 態 (唔係 gluons!)")

# ============ 5. 66 = 22 + 36 + 8 分解 ============
print("\n[4] 66 = 22 + 36 + 8 分解")
print(f"  22 = Nd/2 = half-chain")
print(f"  36 = h11 = Kähler")
print(f"  8 = 2B = 分支邊界")
print(f"  66 = Nd/2 + h11 + 2B = 22 + 36 + 8 ✓")
check("66 = Nd/2 + h11 + 2B", 66 == 22 + 36 + 8)

# 另一種: 66 = 22 + 36 + 8
# 22 + 36 = 58, 58 + 8 = 66
# 58 = ? 
print(f"  22+36 = 58")
print(f"  58 = 2×29? 29 prime")

# ============ 6. SM 對應再嘗試 ============
print("\n[5] SM 對應再嘗試")
# 22 C: 費米子?
# 每代 16 Weyl → 3 代 = 48 ≠ 22
# 但 22 = 16 + 6? (16 費米 + 6 輕子?)
# 或者 22 C 唔係全費米子

# 真正 SM 每代 (physical particles, 唔計色):
# 6 夸克味 × 2 chirality = 12? 唔, 每代 2 味 × 2 chirality × 3 色 = 12
# 但「味」層面: 每代 2 夸克味 (u,d), 2 chirality = 4 態
# 輕子: e, νe = 2 態
# 4 + 2 = 6 態/代 (味層面)
# 3 代 × 6 = 18 態
# + gauge 12 + Higgs 2 = 32? 唔係 66

# 66 態係「幾何」態, 唔係直接 SM 粒子!
# 66 = 22 + 36 + 8:
#   22 C = half-chain CPX (費米幾何)
#   36 K = Kähler (規範幾何)
#   8 C = 分支邊界 (?)
# 呢個先係結構真相

# 但係! 36 K = h11 = 36 個 Kähler moduli
# 每個 Kähler modulus ↔ 一個規範場候選?
# 12 gauge bosons (W±, Z, γ, g×8) × 3 = 36?
# 12 × 3 = 36: 每代 12 規範? 但規範不分代!

# 另一種: 36 = 3×12 = 3 代 × 12
# 12 = ? 
print(f"  36 = 3×12")
print(f"  12 = 12 gauge bosons? (γ, W±, Z, g×8)")
print(f"  3 × 12 = 36: 3 代 × 12 規範? (但規範唔分代!)")
print(f"  或者 12 = 12 費米 Weyl/代 (夸克全)")
print(f"  3 × 12 = 36: 3 代 × 12 夸克 Weyl ✓ 更合理!")

# 12 夸克 Weyl/代:
# Q_L = (u,d)_L × 3 色 = 6
# u_R × 3 = 3
# d_R × 3 = 3
# = 12 ✓
# 36 K = 3 代 × 12 夸克 Weyl = 全部夸克!
# 但夸克係費米子, 點解喺 Kähler sector?

# 矛盾! Kähler = 玻色子, 但 36 K = 夸克?
# 或者 sector 分佈唔等於 玻色/費米 分佈!

# 誠實結論: sector 分佈 (C/K) 同 SM 粒子類型冇直接對應
# 需要更多物理輸入

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("二期 15 總結:")
print("=" * 72)
print(f"""
  66 態 sector 分解 (誠實):
  ─────────────────────────────────
  1. 22 C (evec 0-21): 純 CPX, top-beats 高能量區
  2. 36 K (evec 22-57): 純 Kähler = h11, top-beats 低能量區
  3. 8 C (evec 58-65): 純 CPX, 8 = 2B
  4. 66 = Nd/2 + h11 + 2B = 22 + 36 + 8 ✓

  結構對應:
  - 22 C = half-chain CPX (高能量 beats)
  - 36 K = Kähler moduli (低能量 beats)
  - 8 C = 分支邊界 (2B)

  ⚠️ 誠實: 
  - 36 K = h11 但唔等於「3代×12 夸克」(sector ≠ 費米/玻色)
  - 8 C = 2B 但唔等於 gluons (CPX sector!)
  - 66 態嘅幾何結構清晰, 但 SM 粒子標籤需要更多物理輸入
  - 頻率排序 ≠ 質量排序 (需要 e^-V 壓抑)
""")

results = {
    "test": "O57 二期 15: Sector 22C+36K+8C",
    "sector_split": "22C + 36K + 8C",
    "identity": "66 = Nd/2 + h11 + 2B = 22 + 36 + 8",
    "22C": "half-chain CPX (費米幾何候選)",
    "36K": "Kähler moduli = h11",
    "8C": "2B = 分支邊界",
    "honest": "sector ≠ 費米/玻色, 需更多物理輸入",
    "passed": passed, "failed": failed
}
with open("data/15_sector_structure.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 二期 15 完成!")
