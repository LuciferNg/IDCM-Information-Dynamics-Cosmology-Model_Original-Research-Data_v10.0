#!/usr/bin/env python3
"""38b — D6/S6/C6 perfect matching 枚舉 + (S∓D)/2 生成形式驗證
T1: 完美匹配 (3 對 disjoint, 每對 sum&diff 都結構) 有幾多個?
T2: 每個匹配嘅 (S,D) = (sum, diff) 序列
T3: (S∓D)/2 形式重構檢查
"""
import itertools

STRUCT = {1,2,3,4,5,6,7,8,9,11,12,13,16,17,18,19,20,21,22,25,27,29,32,33,34,36,38,40,41,42,44,47,55,64,66,68,76,77,85,88,90,98,123,137,143,153,176,178}
LABEL = {1:"1",2:"2=log2B",3:"3=N_gen",4:"4=B",5:"5=F5",6:"6=2N_gen",7:"7=L4",8:"8=F6",9:"9=K_tree",
11:"11=L5",12:"12=L5+1",13:"13=F7",16:"16=B²",17:"17=F_proj",18:"18=L6",19:"19=L6+1",20:"20=N_d−B",
21:"21=F8",22:"22=44/2",25:"25=F5²",27:"27=3³",29:"29=L7",32:"32=2B²",33:"33=K_tree",34:"34=F9",
36:"36=(2N_gen)²",38:"38",40:"40=N_d−B",41:"41=44−3",42:"42=N_d⁻",44:"44=N_d",47:"47=L8",
55:"55=F10",64:"64=2⁶",66:"66=2K_tree",68:"68",76:"76=L9",77:"77=L4L5",85:"85=88−3",88:"88",
90:"90",98:"98=h21",123:"123=L10",137:"137",143:"143=dimSU12",153:"153=9·17",176:"176",178:"178=2F11"}

def perfect_matchings(S):
    """全部 3 對 disjoint pairing 且每對 sum,diff ∈ STRUCT"""
    res = []
    for perm in itertools.permutations(S):
        m = []
        ok = True
        for i in range(0, 6, 2):
            a, b = perm[i], perm[i+1]
            if a > b: a, b = b, a
            if (a+b in STRUCT) and (b-a in STRUCT):
                m.append((a,b))
            else:
                ok = False; break
        if ok:
            key = tuple(sorted(m))
            if key not in res:
                res.append(key)
    return res

for name, S in [("D6", [1,2,6,9,19,21]), ("S6", [11,25,41,44,68,85]), ("C6", [3,11,20,25,41,44])]:
    ms = perfect_matchings(S)
    print(f"\n=== {name} perfect matchings: {len(ms)} ===")
    for m in ms:
        info = " | ".join(f"({a},{b}): S={a+b}({LABEL.get(a+b,'?')}) D={b-a}({LABEL.get(b-a,'?')})" for a,b in m)
        print(f"  {info}")

# (S∓D)/2 重構
print("\n=== (S∓D)/2 重構檢查 ===")
def half_sum_diff(S, D):
    return sorted({(S-D)//2, (S+D)//2})
sets = {
    "D6": [((7,5),(11,7),(40,2))],   # (L4,F5),(L5,L4),(N_d−B,log2B)
    "S6": [((55,33),(66,16),(153,17))], # (F10,K_tree),(2K_tree,B²),(9·17,F_proj)
}
for name, S0 in [("D6",[1,2,6,9,19,21]),("S6",[11,25,41,44,68,85])]:
    for sd_list in sets[name]:
        got = sorted(sum((half_sum_diff(S,D) for S,D in sd_list), start=[]))
        print(f"  {name}: {got} == {S0}? {got==sorted(S0)}")

# 額外: (41,44) 嘅身份
print("\n(41,44): S=85(88−3), D=3(N_gen) — 85 = 88−3 = N_d−N_gen")

print("\nRESULT: matching 枚舉完成")
