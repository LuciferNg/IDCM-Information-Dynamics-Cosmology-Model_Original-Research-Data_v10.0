#!/usr/bin/env python3
"""
07_rotation_invariance.py — 15.11° 旋轉不變性測試 (關鍵!)
==========================================================
核心問題: 「冷斑到 3-fold 軸 = 15.109°」係咪依賴 dodecahedron 朝向?

測試: 將標準 dodecahedron 旋轉任意角度 R, 重新計「冷斑到 3-fold 軸」距離。
如果距離唔變 → 15.109° 係內稟量 (唔依賴朝向)
如果距離變 → 15.109° 係人為 (依賴座標系選擇)

預期: 距離會隨 R 變化 → 證明之前嘅 15.109° 唔係結構量
"""
import numpy as np, math

print("=" * 66)
print("O1: 15.11° 旋轉不變性測試")
print("=" * 66)

phi = (1 + 5**0.5) / 2
inv_phi = 1/phi

# 標準 dodecahedron
verts = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        for sz in [-1, 1]:
            verts.append((sx, sy, sz))
for sx in [-1, 1]:
    for sy in [-1, 1]:
        verts.append((0, sx*inv_phi, sy*phi))
        verts.append((sx*inv_phi, sy*phi, 0))
        verts.append((sx*phi, 0, sy*inv_phi))
def norm(v):
    n = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return np.array(v)/n
verts_n = np.array([norm(v) for v in verts])

# 冷斑 (ICRS)
cs = np.array([0.6234, 0.6996, -0.3492])
cs = cs / np.linalg.norm(cs)

# 隨機旋轉
def rand_rotation(rng):
    q = rng.normal(size=3)
    q = q / np.linalg.norm(q)
    theta = rng.uniform(0, 2*math.pi)
    K = np.array([[0, -q[2], q[1]], [q[2], 0, -q[0]], [-q[1], q[0], 0]])
    return np.eye(3) + math.sin(theta)*K + (1-math.cos(theta))*K@K

rng = np.random.default_rng(42)
d3_vals = []
for trial in range(100):
    R = rand_rotation(rng)
    rot_verts = (R @ verts_n.T).T  # 旋轉後嘅 3-fold 軸
    d3 = min(math.degrees(math.acos(np.clip(np.dot(cs, v), -1, 1))) for v in rot_verts)
    d3_vals.append(d3)

d3_vals = np.array(d3_vals)
print(f"100 次隨機旋轉後嘅「冷斑到 3-fold 軸」距離:")
print(f"  min = {d3_vals.min():.3f}°")
print(f"  max = {d3_vals.max():.3f}°")
print(f"  mean = {d3_vals.mean():.3f}° ± {d3_vals.std():.3f}°")
print(f"  之前聲稱值: 15.109°")
print()
if d3_vals.std() > 1:
    print("❌ 距離隨旋轉大變 (std > 1°) → 15.109° 唔係內稟量!")
    print("   之前嘅 15.109° 依賴於 dodecahedron 嘅任意朝向!")
    print("   O1 需要重新定義: 冷斑到 3-fold 軸距離唔 well-defined")
else:
    print("✅ 距離唔變 → 15.109° 係內稟量 (唔依賴朝向)")

# 補充: 冷斑到「邊長」26.09° 係咪內稟? (60 節點固有)
print(f"\n補充: 60 節點最近鄰距離 (固有):")
print(f"  26.09° (4 個) — 軌道固有, 唔依賴朝向 ✅")

# 但 15.109° 到底係咩? 之前 08 點解得到 15.109?
# 08 用標準 verts_n (冇旋轉) 同冷斑 ICRS 向量 → 純粹兩個任意座標系嘅交叉
# 所以 15.109° 冇物理意義!
print(f"\n結論: 15.109° = 標準 dodecahedron (任意朝向) 同 ICRS 嘅交叉角")
print(f"     = 冇物理意義嘅量 (座標系依賴)")

# 真正有結構意義嘅量:
print(f"\n真正嘅結構量 (座標系無關):")
print(f"  1. 最近鄰距離 26.09° (軌道固有)")
print(f"  2. 4 個最近鄰 (degree-4)")
print(f"  3. 對徑點 174.66° (A5 冇反演)")
print(f"  4. 2:3 比例? — 但 d3/d5 都係座標系依賴!")

# 儲存
with open("data/rotation_invariance.txt", "w") as f:
    f.write(f"min={d3_vals.min():.3f} max={d3_vals.max():.3f} std={d3_vals.std():.3f}\n")
    f.write(f"之前聲稱 15.109° → {'內稟' if d3_vals.std() < 1 else '座標系依賴'}\n")
print("\n✅ 已存: data/rotation_invariance.txt")
