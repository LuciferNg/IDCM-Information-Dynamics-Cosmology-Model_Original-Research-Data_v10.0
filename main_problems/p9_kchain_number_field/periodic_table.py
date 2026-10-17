#!/usr/bin/env python3
"""
拍頻週期表雛形 — 已知元素 + 新候選
=====================================
形式: 以 d (opcode) 為行, 以 s (workflow) 為列
      標示每格嘅 beat 值、角色、同族關係
"""
from math import pi, sin
import csv
from collections import defaultdict

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))

# 讀 atlas
rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']),
                     's': int(r['s']), 'label': r['label'].strip()})
pairs = [r for r in rows if r['n'] < r['m']]

# 物理格
phys = {
    (1,18): "m_μ/m_τ", (1,22): "m_s/m_d", (7,20): "n/p",
    (8,22): "c/s", (8,33): "m_c/m_b", (10,24): "u/d",
    (19,33): "t/b", (19,38): "m_H/m_W", (30,41): "m_W/m_Z"
}
phys_set = set(phys.keys())

# 新候選: 對偶點
candidates = {}
for (i,j), pname in phys.items():
    di, dj = 44-j, 44-i
    if di >= dj: continue
    candidates[(di,dj)] = f"dual({pname})"

# 近值點 (diff<0.001)
for (p_i,p_j), pname in phys.items():
    pv = beat(p_i,p_j)
    for (i,j) in [(i,j) for i in range(1,N) for j in range(i+1,N+1)]:
        if (i,j) in phys_set or (i,j) in candidates: continue
        bv = beat(i,j)
        if abs(bv-pv) < 0.001:
            # 檢查 atlas label
            label = ""
            for r in rows:
                if r['n'] == i and r['m'] == j and r['label']:
                    label = r['label']
                    break
            candidates[(i,j)] = f"near({pname})" + (f" [{label}]" if label else "")

print("="*72)
print("拍頻週期表雛形 — 元素分類")
print("="*72)

# 按 d 分組
by_d = defaultdict(list)
for (i,j), pname in phys.items():
    pv = beat(i,j)
    by_d[j-i].append((i,j,pv,"物理",pname))
for (i,j), desc in candidates.items():
    bv = beat(i,j)
    by_d[j-i].append((i,j,bv,desc.split("(")[0],desc))

# 輸出週期表
magic_d = [7,14,20,22,33]
data_d = [11,13,14,17,19,21,25]

print(f"\n{'d':>3s} | {'s 值':20s} | {'beat 值':20s} | {'角色':20s}")
print("-"*72)
for d in sorted(by_d.keys()):
    items = sorted(by_d[d], key=lambda x: x[1])  # 按 s 排序
    for i,j,bv,role,desc in items:
        # 標示
        if d in magic_d:
            role_flag = "★MAG" if d in magic_d and d != 14 else ""
        if d == 14 and any("物理" in r for _,_,_,r,_ in items):
            role_flag = "★GEN"
        if d == 14:
            row_type = "★GEN"
        elif d in magic_d:
            row_type = "★MAG"
        elif d in data_d:
            row_type = " DATA"
        else:
            row_type = " FILL"
        short_desc = desc[:20]
        print(f"{d:3d} | ({i:2d},{j:2d}) s={i+j:3d} | {bv:.8f} | {row_type} {short_desc}")
    if d < 43:
        print("-"*72)

print("\n" + "="*72)
print("週期表結構總結")
print("="*72)
print(f"""
  ★ MAG (操作行): d=7(ANCHOR), d=14(GEN), d=20(TRANSFER), d=22(HALF), d=33(KTREE)
  ★ DATA (物理行): d=11,13,14,17,19,21,25
  
  已知元素: 9 物理格
  新候選:   {len(candidates)} 個 (對偶 + 近值)
  
  d=14 (GEN 行) 特別密集:
    - 3 已知 quark: (8,22) c/s, (10,24) u/d, (19,33) t/b
    - 3 對偶 quark: (22,36), (20,34), (11,25)
    - 1 近 Higgs:  (15,29)
    → GEN 行有 7 個「活躍格」!
""")

# 將 GEN 行 6 個 quark 格排序
gen_quarks = [(8,22,"c/s","0.85074845"),
              (10,24,"u/d","0.81257079"),
              (19,33,"t/b","0.59282105"),
              (22,36,"dual(c/s)","0.50477238"),
              (20,34,"dual(u/d)","0.56417798"),
              (11,25,"dual(t/b)","0.79191621")]
gen_quarks.sort(key=lambda x: x[2])
print("\n" + "="*72)
print("★ GEN 行 6 格 quark 族 — 按 beat 值排序")
print("="*72)
for i,j,name,bv_str in sorted(gen_quarks, key=lambda x: float(x[3])):
    bv = float(bv_str)
    print(f"  ({i:2d},{j:2d}) s={i+j:3d} beat={bv:.8f}  {name:15s}")

# 檢查: 6 格嘅 beat 值有冇數學關係?
print("\n  beat 值比例:")
vals = [float(v) for _,_,_,v in gen_quarks]
vals.sort()
for k in range(len(vals)):
    for l in range(k+1, len(vals)):
        ratio = vals[l]/vals[k]
        print(f"    {vals[l]:.8f} / {vals[k]:.8f} = {ratio:.6f}")