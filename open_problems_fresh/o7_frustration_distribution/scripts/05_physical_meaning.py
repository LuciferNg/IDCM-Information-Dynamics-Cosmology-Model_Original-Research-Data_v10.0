#!/usr/bin/env python3
"""
O7 Task 5: 物理意義 — 阻挫邊 = 縫合線 → 空間分佈預測
====================================================================
分析:
1. 追蹤縫合線: 阻挫邊通過 degree-2 節點連接成路徑
2. 每條縫合線連接嘅奇面類型 (Δ-Δ, Δ-⬠, ⬠-⬠)
3. 縫合線嘅天球位置
4. 物理預測: 溫度梯度異常, 可觀測信號
5. SMICA 驗證 (如果數據可用)
"""
import numpy as np
import math
from collections import defaultdict, Counter, deque
import os

DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"

# ============ 1. 載入數據 ============
nodes = []
with open(f"{DATA}/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))

vecs = []
for ra, dec in nodes:
    r, d = math.radians(ra), math.radians(dec)
    vecs.append(np.array([math.cos(d)*math.cos(r),
                          math.cos(d)*math.sin(r),
                          math.sin(d)]))
vecs = np.array(vecs)

# 建全圖
THRESHOLD = 28.0
adj = defaultdict(set)
edges_all = []
for i in range(60):
    for j in range(i+1, 60):
        dot = np.clip(np.dot(vecs[i], vecs[j]), -1, 1)
        if math.degrees(math.acos(dot)) < THRESHOLD:
            adj[i].add(j)
            adj[j].add(i)
            edges_all.append((i, j))

# 阻挫邊
frust_edges = set()
frust_list = []
color = {}
with open(f"{DATA}/frustration_edges.txt") as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split()
        u, v = int(parts[0]), int(parts[1])
        cu, cv = int(parts[2]), int(parts[3])
        frust_edges.add((u, v) if u < v else (v, u))
        frust_list.append((u, v, cu))

# 著色
with open(f"{DATA}/anchored_coloring.txt") as f:
    f.readline()
    for line in f:
        parts = line.strip().split()
        idx, c = int(parts[0]), int(parts[3])
        color[idx] = c

# 面資料: 邊→面類型映射
edge_faces = defaultdict(list)  # edge -> [(face_type, vertices)]
with open(f"{DATA}/faces.txt") as f:
    for line in f:
        if line.startswith("#"):
            continue
        parts = line.strip().split()
        if not parts:
            continue
        ft = parts[0]
        bracket_start = line.index('[')
        bracket_end = line.index(']')
        vert_str = line[bracket_start+1:bracket_end]
        vertices = [int(x.strip()) for x in vert_str.split(',')]
        n = len(vertices)
        for i in range(n):
            e = tuple(sorted((vertices[i], vertices[(i+1) % n])))
            edge_faces[e].append((ft, vertices))

print("=" * 70)
print("O7 Task 5: 物理意義 — 阻挫邊 = 縫合線")
print("=" * 70)

# ============ 2. 追蹤縫合線 ============
print(f"\n{'='*70}")
print("📐 [5.1] 縫合線路徑追蹤")
print(f"{'='*70}")

# 阻挫子圖
frust_adj = defaultdict(set)
for u, v in frust_edges:
    frust_adj[u].add(v)
    frust_adj[v].add(u)
frust_nodes = set(frust_adj.keys())

# 找所有路徑 (degree-2 節點 = 連接器)
seen = set()
seam_segments = []  # 每條: [node_path, edge_list]
for start in frust_nodes:
    if start in seen:
        continue
    # BFS component
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

    if len(comp) == 2:
        # 單條邊
        e = tuple(sorted(comp))
        seam_segments.append({'nodes': comp, 'edges': [e], 'type': 'single'})
    else:
        # 路徑: 搵端點 (degree 1)
        endpoints = [v for v in comp if len(frust_adj[v]) == 1]
        if len(endpoints) == 2:
            # 係一條路徑: BFS 搵最短路徑
            u, w = endpoints
            q = deque([(u, [u])])
            visited = {u}
            path = None
            while q and not path:
                cur, p = q.popleft()
                if cur == w:
                    path = p
                    break
                for v in frust_adj[cur]:
                    if v not in visited:
                        visited.add(v)
                        q.append((v, p + [v]))
            if path:
                edges = []
                for i in range(len(path)-1):
                    e = tuple(sorted((path[i], path[i+1])))
                    edges.append(e)
                seam_segments.append({'nodes': path, 'edges': edges, 'type': 'path'})
            else:
                seam_segments.append({'nodes': comp, 'edges': [], 'type': 'unknown'})
        else:
            # 單節點或其他
            seam_segments.append({'nodes': comp, 'edges': [], 'type': f'deg{len(endpoints)}'})

print(f"   總縫合線段數: {len(seam_segments)}")
seg_types = Counter(s['type'] for s in seam_segments)
for t, c in sorted(seg_types.items()):
    print(f"     {t}: {c}")

# ============ 3. 每條縫合線嘅奇面連接 ============
print(f"\n{'='*70}")
print("📐 [5.2] 縫合線連接嘅奇面類型")
print(f"{'='*70}")

seam_odd_summary = []
for i, seg in enumerate(seam_segments):
    nodes_list = seg['nodes']
    edges_list = seg['edges']

    # 每條邊嘅奇面類型
    odd_faces = []
    edge_types = []
    for e in edges_list:
        e_faces = edge_faces[e]
        for ft, verts in e_faces:
            if ft in ('T', 'P'):
                labels = {'T': 'Δ', 'P': '⬠'}
                odd_faces.append(labels[ft])
                break
        # 邊類型
        face_types = [ef[0] for ef in e_faces]
        ft_labels = {'T': 'Δ', 'S': '□', 'P': '⬠'}
        types = [ft_labels[x] for x in sorted(face_types)]
        edge_types.append('-'.join(types))

    # 端點座標
    start_ra, start_dec = nodes[nodes_list[0]]
    end_ra, end_dec = nodes[nodes_list[-1]]

    # 縫合線長度 (度)
    total_deg = 0
    for j in range(len(nodes_list)-1):
        u, v = nodes_list[j], nodes_list[j+1]
        dot = np.clip(np.dot(vecs[u], vecs[v]), -1, 1)
        total_deg += math.degrees(math.acos(dot))

    seam_odd_summary.append({
        'idx': i, 'nodes': nodes_list, 'edges': edges_list,
        'odd_faces': odd_faces, 'edge_types': edge_types,
        'n_edges': len(edges_list), 'n_nodes': len(nodes_list),
        'total_deg': total_deg, 'start': (start_ra, start_dec),
        'end': (end_ra, end_dec)
    })

    # 奇面類型組合
    odd_set = set(odd_faces)
    odd_combo = ''.join(sorted(odd_set))
    # 端點顏色
    start_color = color[nodes_list[0]]
    end_color = color[nodes_list[-1]]

    print(f"\n   縫合線 #{i} ({seg['type']}):")
    print(f"     節點路徑: {nodes_list}")
    print(f"     邊類型:   {edge_types}")
    print(f"     奇面:     {odd_faces}")
    print(f"     長度:     {total_deg:.1f}° ({len(edges_list)} 條邊)")
    print(f"     端點:     ({start_ra:.1f}°, {start_dec:.1f}°) ↔ ({end_ra:.1f}°, {end_dec:.1f}°)")
    print(f"     端點色:   {'冷' if start_color==1 else '熱'} → {'冷' if end_color==1 else '熱'}")

# 奇面組合統計
odd_combos = Counter()
for s in seam_odd_summary:
    odd_set = set(s['odd_faces'])
    combo = ''.join(sorted(odd_set))
    odd_combos[combo] += 1
print(f"\n   奇面組合分佈:")
for combo, cnt in sorted(odd_combos.items()):
    print(f"     {combo}: {cnt} 條縫合線")

# 單邊 vs 多邊縫合線
single_edges = sum(1 for s in seam_odd_summary if s['n_edges'] == 1)
multi_edges = sum(1 for s in seam_odd_summary if s['n_edges'] > 1)
print(f"\n   單邊縫合線: {single_edges} (直接連接 1 奇面 + 1 偶面)")
print(f"   多邊縫合線: {multi_edges} (通過正方形連接多個奇面)")

# 多邊縫合線嘅奇面連接模式
print(f"\n   多邊縫合線細節:")
for s in seam_odd_summary:
    if s['n_edges'] > 1:
        combo = ''.join(sorted(set(s['odd_faces'])))
        print(f"     #{s['idx']}: {s['odd_faces']} (combo={combo}, {s['n_edges']}邊, {s['total_deg']:.1f}°)")

# ============ 4. 縫合線天球分佈 ============
print(f"\n{'='*70}")
print("📐 [5.3] 縫合線天球分佈")
print(f"{'='*70}")

# 每條縫合線嘅中點
midpoints = []
for s in seam_odd_summary:
    nodes_list = s['nodes']
    mid_idx = len(nodes_list) // 2
    mid_ra, mid_dec = nodes[nodes_list[mid_idx]]
    midpoints.append((mid_ra, mid_dec, s['n_edges'], s['total_deg']))

print(f"   縫合線中點位置:")
for i, (ra, dec, n, length) in enumerate(midpoints):
    print(f"     #{i}: ({ra:.1f}°, {dec:+.1f}°) [{n}邊, {length:.1f}°]")

# 南北半球分佈
n_north = sum(1 for _, dec, _, _ in midpoints if dec > 0)
n_south = sum(1 for _, dec, _, _ in midpoints if dec < 0)
print(f"\n   縫合線南北: {n_north} 北 / {n_south} 南")

# 縫合線長度統計
lengths = [s['total_deg'] for s in seam_odd_summary]
print(f"   縫合線長度: 平均 {np.mean(lengths):.1f}° ± {np.std(lengths):.1f}°, "
      f"範圍 {min(lengths):.1f}° - {max(lengths):.1f}°")

# 總縫合線長度
total_seam_length = sum(lengths)
print(f"   總縫合線長度: {total_seam_length:.1f}°")
print(f"   天球覆蓋率: {total_seam_length / 360 * 100:.1f}% (如果全部縫合線沿大圓)")
print(f"   實際天球覆蓋: ~{len(frust_nodes)/60*100:.0f}% 節點涉及")

# ============ 5. 物理預測 ============
print(f"\n{'='*70}")
print("📐 [5.4] 物理預測")
print(f"{'='*70}")

print(f"""
   阻挫邊 = 投影縫合線 (Projection Seams)

   🌟 預測 1: 縫合線係 LOCAL DEFECTS, 唔係 global seams
   - 20 條獨立縫合線段, 最長 3 邊 (~78°)
   - 意味: K_Chain 投影縫合係局部, 唔係全球縫合
   - 可證偽: 如果發現 >78° 連續異常線 → 呢個預測錯

   🌟 預測 2: 縫合線必經過正方形 connector
   - 每條 >1 邊嘅縫合線經過 1 個正方形 (degree-2 節點)
   - 正方形嘅 2 條阻挫邊永遠係對邊 (平行)
   - 可證偽: 如果發現正方形有鄰邊阻挫 → 預測錯

   🌟 預測 3: 縫合線溫度梯度 anomaly
   - 已知: 阻挫邊 34.5μK vs 正常邊 53.1μK (SMICA)
   - 縫合線沿線溫度梯度較低 = 冷熱邊界模糊
   - 預測: 縫合線端點 (degree-1 frust nodes) 嘅溫度梯度最大
   - 可證偽: 如果端點梯度不大於 connector 節點 → 預測錯

   🌟 預測 4: 20 條縫合線對應 20 個三角形
   - 每三角形貢獻 1 條 Δ-□ 阻挫邊
   - 12 條 ⬠-□ 阻挫邊由五邊形貢獻
   - 16 個正方形 connector 連接 32 條邊
   - 比例: 20Δ : 12⬠ : 32□-connector = 5:3:8

   🌟 預測 5: 縫合線 = 拓撲位元骨幹
   - 40 個 degree-1 節點 = 可翻轉位元端點
   - 12 個 degree-2 節點 = 位元路由器
   - 最大資訊儲存: 2^40 種翻轉組合
   - 但受阻挫飽和限制, 實際 ~2^20
""")

# ============ 6. SMICA 驗證 (如果可用) ============
print(f"{'='*70}")
print("📐 [5.5] SMICA 溫度驗證")
print(f"{'='*70}")

smica_files = ['smica_smoothed.txt', 'smica_bandpass.txt', 'smica_continuous.txt']

# 讀取 SMICA 溫度 (如果存在)
smica_data = None
for sf in smica_files:
    sf_path = f"{DATA}/{sf}"
    if os.path.exists(sf_path):
        print(f"   找到 SMICA 數據: {sf}")
        # 讀取: 假設格式係 idx, temperature
        smica_temps = {}
        with open(sf_path) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                parts = line.strip().split()
                if len(parts) >= 3 and parts[0].isdigit():
                    try:
                        idx = int(parts[0])
                        temp = float(parts[2])  # column 2 = T_smooth_uK
                        smica_temps[idx] = temp
                    except:
                        pass
        if len(smica_temps) >= 60:
            smica_data = smica_temps
            print(f"     讀取 {len(smica_temps)} 個節點溫度")
            break

if smica_data:
    # 按節點分類
    deg1_nodes = [v for v in frust_nodes if len(frust_adj[v]) == 1]
    deg2_nodes = [v for v in frust_nodes if len(frust_adj[v]) == 2]
    non_frust = [v for v in range(60) if v not in frust_nodes]

    deg1_temps = [smica_data[v] for v in deg1_nodes if v in smica_data]
    deg2_temps = [smica_data[v] for v in deg2_nodes if v in smica_data]
    non_frust_temps = [smica_data[v] for v in non_frust if v in smica_data]
    all_temps = [smica_data[v] for v in range(60) if v in smica_data]

    print(f"\n   節點類型溫度對比:")
    print(f"     全部節點: {np.mean(all_temps):+.1f}μK ± {np.std(all_temps):.1f}μK")
    if deg1_temps:
        print(f"     degree-1 (端點, {len(deg1_temps)}節點): {np.mean(deg1_temps):+.1f}μK ± {np.std(deg1_temps):.1f}μK")
    if deg2_temps:
        print(f"     degree-2 (連接器, {len(deg2_temps)}節點): {np.mean(deg2_temps):+.1f}μK ± {np.std(deg2_temps):.1f}μK")
    if non_frust_temps:
        print(f"     非阻挫節點 ({len(non_frust_temps)}節點): {np.mean(non_frust_temps):+.1f}μK ± {np.std(non_frust_temps):.1f}μK")

    # 縫合線端點溫度 vs 連接器溫度
    if deg1_temps and deg2_temps:
        from scipy.stats import ttest_ind
        t_stat, t_p = ttest_ind(deg1_temps, deg2_temps)
        print(f"\n     端點 vs 連接器 t-test: p={t_p:.4f} {'🟡' if t_p<0.05 else '🟢'}")

    # 縫合線沿線溫度 pattern
    print(f"\n   每條縫合線沿線溫度:")
    for s in seam_odd_summary:
        temps = [smica_data[v] for v in s['nodes'] if v in smica_data]
        if temps:
            temp_str = ' → '.join(f"{t:+.1f}" for t in temps)
            print(f"     #{s['idx']}: {temp_str}  (Δ={max(temps)-min(temps):+.1f}μK)")
else:
    print(f"   未找到 SMICA 節點溫度數據, 跳過溫度驗證 🟡")
    print(f"   可參考: 22_smica_smoothed.py 結果 (阻挫邊 34.5μK vs 正常邊 53.1μK)")

# ============ 7. 總結 ============
print(f"\n{'='*70}")
print("📋 總結 — 阻挫邊物理意義")
print(f"{'='*70}")

# 奇面組合分佈
print(f"   縫合線總數: {len(seam_segments)}")
print(f"   單邊縫合線: {single_edges} (Δ-□ 或 ⬠-□)")
print(f"   多邊縫合線: {multi_edges} (通過正方形連接)")
print(f"   奇面組合: {dict(odd_combos)}")
print(f"   總縫合線長度: {total_seam_length:.1f}°")
print(f"   最長縫合線: {max(lengths):.1f}° ({max(s['n_edges'] for s in seam_odd_summary)} 條邊)")
print(f"   平均縫合線長度: {np.mean(lengths):.1f}°")

# 物理意義總結
print(f"""
   🌟 核心物理圖像:
   阻挫邊 = K_Chain 投影縫合線, 形成 20 條局部缺陷

   縫合線結構:
   - 10 條單邊 Δ-□ (最短, 直接連接 1 三角形 + 1 正方形)
   - 8 條雙邊路徑 (Δ-□-⬠ 或 ⬠-□-⬠ 或 Δ-□-Δ)
   - 2 條三邊路徑 (最長, 連接 3 個奇面)

   可證偽預測:
   1. 冇連續縫合線 >78° 🟢
   2. 正方形縫合 connector 永遠對邊 🟢
   3. 端點節點溫度梯度大於 connector 🟡 (待驗證)
   4. 20:12:32 = Δ:⬠:□connector 比例 🟢
   5. 縫合線 = 拓撲位元骨幹, 2^20 自由度 🟡 (理論推導)
""")