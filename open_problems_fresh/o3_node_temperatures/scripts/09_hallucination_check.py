#!/usr/bin/env python3
"""
hallucination_check_o3.py — O3 結果報告數字驗證
================================================
獨立重算 02_results.md 嘅所有關鍵數字 + 檔案存在檢查
任何 fail → exit 1
"""
import numpy as np
import os

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o3_node_temperatures"
DATA = os.path.join(BASE, "data")
fails = []
passes = []

def check(name, cond, detail=""):
    if cond:
        passes.append(name)
        print(f"  ✅ {name} {detail}")
    else:
        fails.append(name)
        print(f"  ❌ {name} {detail}")

# ============ 載入 ============
rows = []
with open(os.path.join(DATA, "node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), float(p[3]), float(p[4]), int(p[5])))
T = np.array([r[2] for r in rows])
color = np.array([r[1] for r in rows])
hop = np.array([r[5] for r in rows])

print("=" * 60)
print("O3 結果報告數字驗證")
print("=" * 60)

# ============ 基本統計 ============
check("mean=-1.25", abs(T.mean() - (-1.25)) < 0.05, f"got {T.mean():.3f}")
check("std=46.19", abs(T.std(ddof=1) - 46.19) < 0.05, f"got {T.std(ddof=1):.3f}")
check("min=-134.19 @node0", abs(T.min() - (-134.19)) < 0.01 and np.argmin(T) == 0, f"got {T.min():.3f} @{np.argmin(T)}")
check("max=+112.00 @node53", abs(T.max() - 112.00) < 0.01 and np.argmax(T) == 53, f"got {T.max():.3f} @{np.argmax(T)}")
check("median=+1.44", abs(np.median(T) - 1.44) < 0.05, f"got {np.median(T):.3f}")

# ============ 冷熱分離 ============
Tc = T[color == 1]
Th = T[color == 0]
check("冷色 mean=-12.41", abs(Tc.mean() - (-12.41)) < 0.05, f"got {Tc.mean():.3f}")
check("熱色 mean=+9.91", abs(Th.mean() - 9.91) < 0.05, f"got {Th.mean():.3f}")
check("冷熱差=-22.31", abs((Tc.mean() - Th.mean()) - (-22.31)) < 0.05, f"got {Tc.mean()-Th.mean():.3f}")
check("冷30/熱30", len(Tc) == 30 and len(Th) == 30, f"got {len(Tc)}/{len(Th)}")

# ============ 極端百分位 ============
# 由 03 記錄: 冷斑 98.2%, 冷熱差 3.4% — 呢啲係隨機對照結果, 唔重算 (需 2000 組)
# 但可以檢查已知節點值
check("節點47=-123.40", abs(T[47] - (-123.40)) < 0.05, f"got {T[47]:.3f}")
check("節點57=+8.21", abs(T[57] - 8.21) < 0.05, f"got {T[57]:.3f}")
check("節點9=-106.99", abs(T[9] - (-106.99)) < 0.05, f"got {T[9]:.3f}")

# ============ BFS ============
check("BFS 分佈 1+4+8+11+12+11+8+4+1",
      all(np.bincount(hop, minlength=9)[:9] == [1,4,8,11,12,11,8,4,1]),
      f"got {list(np.bincount(hop, minlength=9)[:9])}")
check("直徑=8", hop.max() == 8)
check("對徑=節點57", list(np.where(hop == 8)[0]) == [57], f"got {list(np.where(hop==8)[0])}")

# ============ 著色 parity ============
check("著色 = BFS parity", np.all(color == (1 - (hop % 2))))

# ============ ΔE=0 節點 ============
ZERO_E = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
zm = np.array([i in ZERO_E for i in range(60)])
Tz = T[zm]
To = T[~zm]
check("ΔE=0 mean|T|=19.05", abs(np.abs(Tz).mean() - 19.05) < 0.05, f"got {np.abs(Tz).mean():.3f}")
check("其他48 mean|T|=36.18", abs(np.abs(To).mean() - 36.18) < 0.05, f"got {np.abs(To).mean():.3f}")
check("比例=0.526", abs(np.abs(Tz).mean()/np.abs(To).mean() - 0.526) < 0.01, f"got {np.abs(Tz).mean()/np.abs(To).mean():.3f}")
check("node45=+1.57", abs(T[45] - 1.57) < 0.05, f"got {T[45]:.3f}")
check("|T|<15: 7/12", (np.abs(Tz) < 15).sum() == 7, f"got {(np.abs(Tz)<15).sum()}")

# ============ 匹配率 ============
match = ((color == 1) & (T < 0)) | ((color == 0) & (T > 0))
check("匹配率 61.7%", abs(match.mean() - 0.617) < 0.01, f"got {match.mean():.3f}")
check("23/60 唔匹配", (~match).sum() == 23, f"got {(~match).sum()}")
check("冷色正溫 12 個", ((color==1)&(T>0)).sum() == 12, f"got {((color==1)&(T>0)).sum()}")
check("熱色負溫 11 個", ((color==0)&(T<0)).sum() == 11, f"got {((color==0)&(T<0)).sum()}")

# ============ 檔案存在 ============
for f in ["node_temps.txt", "bfs_distances.txt"]:
    check(f"檔案 {f} 存在", os.path.exists(os.path.join(DATA, f)))
for f in ["01_temp_hist.png", "02_coldhot_box.png", "03_temp_vs_bfs.png"]:
    check(f"圖 {f} 存在", os.path.exists(os.path.join(BASE, "figs", f)))
for f in ["01_node_temps.py", "02_stats_tests.py", "03_extreme_test.py",
          "04_ladder_corr.py", "05_verify.py", "06_node57_puzzle.py",
          "07_plots.py", "08_zero_energy_nodes.py"]:
    check(f"script {f} 存在", os.path.exists(os.path.join(BASE, "scripts", f)))

print(f"\n{'='*60}")
print(f"結果: {len(passes)} 通過, {len(fails)} 失敗")
if fails:
    print("❌ 有失敗!")
    exit(1)
print("✅ 全部通過 — 報告數字無幻覺")
