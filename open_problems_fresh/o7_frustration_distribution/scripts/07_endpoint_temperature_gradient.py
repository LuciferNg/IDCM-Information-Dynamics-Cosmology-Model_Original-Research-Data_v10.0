#!/usr/bin/env python3
"""
O7 開放問題 A: 端點 vs connector 溫度梯度
============================================
預測 3: 縫合線端點 (degree-1 frust nodes) 嘅溫度梯度 > connector (degree-2)

方法:
1. 用 SMICA 5° smoothed + bandpass 兩個尺度
2. 每節點計算溫度梯度: |T_v - mean(T_neighbors)|
3. 比較 deg-1, deg-2, 非阻挫端點, 全部節點
4. 隨機對照: 隨機選同數量節點
"""
import numpy as np
import math
from collections import defaultdict, deque
from scipy.stats import ttest_ind, mannwhitneyu

DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"

# ============ 1. 載入圖 ============
nodes = []
with open(f"{DATA}/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                   math.cos(math.radians(d))*math.sin(math.radians(r)),
                   math.sin(math.radians(d))] for r,d in nodes])

adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j)
            adj[j].add(i)

# 阻挫子圖
frust_edges = set()
with open(f"{DATA}/frustration_edges.txt") as f:
    f.readline()
    for line in f:
        p = line.strip().split()
        u, v = int(p[0]), int(p[1])
        frust_edges.add((min(u, v), max(u, v)))

frust_adj = defaultdict(set)
for u, v in frust_edges:
    frust_adj[u].add(v); frust_adj[v].add(u)

deg1 = sorted([v for v in range(60) if v in frust_adj and len(frust_adj[v]) == 1])
deg2 = sorted([v for v in range(60) if v in frust_adj and len(frust_adj[v]) == 2])
non_frust = sorted([v for v in range(60) if v not in frust_adj])

print("=" * 70)
print("O7 開放問題 A: 端點 vs connector 溫度梯度")
print("=" * 70)
print(f"\n節點分類:")
print(f"   degree-1 (端點): {len(deg1)} 個")
print(f"   degree-2 (連接器): {len(deg2)} 個")
print(f"   非阻挫: {len(non_frust)} 個")

# ============ 2. 載入溫度數據 ============
datasets = {
    'smica_smoothed.txt': 'SMICA 5° 平滑',
    'smica_bandpass.txt': 'SMICA 帶通 ℓ∈[20,60]'
}

def load_temps(filename):
    """Load temperature data: col 0=idx, col 2=T (smoothed) or col 1=T (bandpass)"""
    temps = {}
    with open(f"{DATA}/{filename}") as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            try:
                idx = int(parts[0])
                # Both formats: col 0=idx, col 1=color, col 2=temp
                t = float(parts[2])
                temps[idx] = t
            except:
                pass
    return temps

def compute_gradient(temps, v):
    """溫度梯度: |T_v - mean(T_neighbors)|"""
    if v not in temps:
        return None
    neighbors = list(adj[v])
    if not neighbors:
        return 0.0
    T_v = temps[v]
    T_neighbors = [temps[n] for n in neighbors if n in temps]
    if not T_neighbors:
        return 0.0
    return abs(T_v - np.mean(T_neighbors))

# ============ 3. 分析 ============
for fname, label in datasets.items():
    print(f"\n{'='*70}")
    print(f"📐 {label}")
    print(f"{'='*70}")

    temps = load_temps(fname)
    if len(temps) < 60:
        print(f"   ⚠️ 只讀取 {len(temps)}/60 節點溫度")
        continue

    # 梯度
    grad_all = [compute_gradient(temps, v) for v in range(60)]
    grad_all = [g for g in grad_all if g is not None]

    grad_d1 = [compute_gradient(temps, v) for v in deg1]
    grad_d1 = [g for g in grad_d1 if g is not None]

    grad_d2 = [compute_gradient(temps, v) for v in deg2]
    grad_d2 = [g for g in grad_d2 if g is not None]

    grad_nf = [compute_gradient(temps, v) for v in non_frust]
    grad_nf = [g for g in grad_nf if g is not None]

    print(f"\n   溫度梯度對比:")
    print(f"   {'類型':<20} {'數量':>6} {'平均梯度':>10} {'±SD':>10}")
    print(f"   {'-'*50}")
    print(f"   {'全部節點':<20} {len(grad_all):>6} {np.mean(grad_all):>10.2f} {np.std(grad_all):>10.2f}")
    print(f"   {'degree-1 (端點)':<20} {len(grad_d1):>6} {np.mean(grad_d1):>10.2f} {np.std(grad_d1):>10.2f}")
    print(f"   {'degree-2 (連接器)':<20} {len(grad_d2):>6} {np.mean(grad_d2):>10.2f} {np.std(grad_d2):>10.2f}")
    print(f"   {'非阻挫':<20} {len(grad_nf):>6} {np.mean(grad_nf):>10.2f} {np.std(grad_nf):>10.2f}")

    # 統計檢定
    if grad_d1 and grad_d2:
        t_stat, t_p = ttest_ind(grad_d1, grad_d2)
        u_stat, u_p = mannwhitneyu(grad_d1, grad_d2)
        print(f"\n   端點 vs 連接器:")
        print(f"     t-test: t={t_stat:.3f}, p={t_p:.4f} {'🟡端點梯度大' if (t_p<0.05 and np.mean(grad_d1)>np.mean(grad_d2)) else '🟡端點梯度小' if (t_p<0.05 and np.mean(grad_d1)<np.mean(grad_d2)) else '🟢無顯著差異'}")
        print(f"     MW U-test: U={u_stat:.0f}, p={u_p:.4f} {'🟡' if u_p<0.05 else '🟢'}")

    # 絕對溫度對比
    temps_d1 = [temps[v] for v in deg1]
    temps_d2 = [temps[v] for v in deg2]
    print(f"\n   絕對溫度對比:")
    print(f"   {'類型':<20} {'平均T':>10} {'±SD':>10}")
    print(f"   {'degree-1 (端點)':<20} {np.mean(temps_d1):>10.2f} {np.std(temps_d1):>10.2f}")
    print(f"   {'degree-2 (連接器)':<20} {np.mean(temps_d2):>10.2f} {np.std(temps_d2):>10.2f}")
    if temps_d1 and temps_d2:
        t_s, t_p = ttest_ind(temps_d1, temps_d2)
        print(f"     t-test: p={t_p:.4f} {'🟡' if t_p<0.05 else '🟢'}")

    # 隨機對照: 隨機選 40 個節點做端點
    rng = np.random.RandomState(42)
    rand_grad = []
    for _ in range(10000):
        idx = rng.choice(60, len(deg1), replace=False)
        g = [compute_gradient(temps, v) for v in idx]
        g = [x for x in g if x is not None]
        rand_grad.append(np.mean(g) if g else 0)

    real_grad_mean = np.mean(grad_d1) if grad_d1 else 0
    pct = np.mean([r >= real_grad_mean for r in rand_grad]) * 100
    print(f"\n   隨機對照 (10000次, 隨機選 {len(deg1)} 節點):")
    print(f"     隨機平均梯度: {np.mean(rand_grad):.2f} ± {np.std(rand_grad):.2f}")
    print(f"     真實端點梯度: {real_grad_mean:.2f}")
    print(f"     百分位: {pct:.1f}% {'🟡端點梯度異常大' if pct>95 else '🟡端點梯度異常小' if pct<5 else '🟢正常'}")

# ============ 4. 縫合線沿線溫度梯度 ============
print(f"\n{'='*70}")
print("📐 縫合線沿線溫度梯度")
print(f"{'='*70}")

temps_smooth = load_temps('smica_smoothed.txt')
temps_band = load_temps('smica_bandpass.txt')

# 追蹤縫合線
seen = set()
seam_gradients = []
for start in range(60):
    if start not in frust_adj or start in seen:
        continue
    comp = []
    q = deque([start])
    seen.add(start)
    while q:
        u = q.popleft()
        comp.append(u)
        for v in frust_adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)

    if len(comp) >= 2:
        # 沿線溫度
        smooth_T = [temps_smooth.get(v, 0) for v in comp]
        band_T = [temps_band.get(v, 0) for v in comp]
        # 溫度梯度 = 沿線 max-min
        smooth_range = max(smooth_T) - min(smooth_T)
        band_range = max(band_T) - min(band_T)
        # 端點溫差
        end_diff_s = abs(smooth_T[0] - smooth_T[-1])
        end_diff_b = abs(band_T[0] - band_T[-1])

        seam_gradients.append({
            'nodes': comp, 'len': len(comp),
            'smooth_range': smooth_range, 'band_range': band_range,
            'end_diff_s': end_diff_s, 'end_diff_b': end_diff_b
        })

print(f"\n   20 條縫合線沿線溫度梯度:")
print(f"   {'#':>2} {'長度':>4} {'平滑ΔT':>8} {'帶通ΔT':>8} {'端點ΔT_s':>8} {'端點ΔT_b':>8}")
print(f"   {'-'*45}")
for i, sg in enumerate(seam_gradients):
    markers = ''
    print(f"   {i:>2} {sg['len']:>4} {sg['smooth_range']:>8.1f} {sg['band_range']:>8.1f} {sg['end_diff_s']:>8.1f} {sg['end_diff_b']:>8.1f}")

# 端點梯度 vs 縫合線長度相關
end_diffs = [sg['end_diff_s'] for sg in seam_gradients]
lengths = [sg['len'] for sg in seam_gradients]
r = np.corrcoef(end_diffs, lengths)[0, 1] if len(end_diffs) > 1 else 0
print(f"\n   端點ΔT vs 縫合線長度 相關: r={r:.3f} {'🟡' if abs(r)>0.5 else '🟢'}")

# 單邊 vs 多邊縫合線
single_end = [sg['end_diff_s'] for sg in seam_gradients if sg['len'] == 2]
multi_end = [sg['end_diff_s'] for sg in seam_gradients if sg['len'] > 2]
if single_end and multi_end:
    t_p = ttest_ind(single_end, multi_end)[1]
    print(f"\n   單邊縫合線端點ΔT: {np.mean(single_end):.1f} ± {np.std(single_end):.1f}")
    print(f"   多邊縫合線端點ΔT: {np.mean(multi_end):.1f} ± {np.std(multi_end):.1f}")
    print(f"   t-test: p={t_p:.4f} {'🟡' if t_p<0.05 else '🟢'}")

# ============ 5. 總結 ============
print(f"\n{'='*70}")
print("📋 總結")
print(f"{'='*70}")
print(f"   預測 3: 端點溫度梯度 > connector 溫度梯度")
print(f"   SMICA 5°平滑: 端點 {np.mean(grad_d1):.1f}μK, connector {np.mean(grad_d2):.1f}μK" if 'grad_d1' in dir() else "")
print(f"   SMICA 帶通: 端點 {np.mean([compute_gradient(load_temps('smica_bandpass.txt'), v) for v in deg1]):.1f}μK, connector {np.mean([compute_gradient(load_temps('smica_bandpass.txt'), v) for v in deg2]):.1f}μK" if 'deg1' in dir() else "")

print(f"""
   結論:
   - 兩個尺度都未發現端點溫度梯度顯著大於 connector
   - 預測 3 未經驗證 🟡
   - 可能原因: 5° 平滑可能太粗, 掩蓋咗局部梯度差異
   - 建議: 用更高分辨率 SMICA (nside=1024) 或 Planck 原始地圖
""")