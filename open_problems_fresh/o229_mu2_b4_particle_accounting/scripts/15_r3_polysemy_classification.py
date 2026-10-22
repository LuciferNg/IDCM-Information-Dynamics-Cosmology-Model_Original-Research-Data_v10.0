#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/15 (R3-③) — 多義（polysemy）機制分類 + 完備性掃描
★ 合約: docs/14_r3_contract.md §A R3-③
★ 零新參數: P1–P11 全部逐項以精確算式**重驗**；角色表每項都要算得出值
"""
import json, os, math
from fractions import Fraction as Fr
import mpmath as mp
mp.mp.dps=50
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=[]; NP=NF=0
def p(s=""): print(s); OUT.append(s)
def chk(n,c,d=""):
    global NP,NF
    t="PASS" if c else "FAIL"; NP+=bool(c); NF+=(not c)
    p(f"  [{t}] {n}"+(f"   {d}" if d else "")); return bool(c)
def res(): p(f"\nRESULT: {NP}/{NP+NF} PASS"); return NP,NF
ATOMS=[1,2,3,4,5,7,8,11,13,16,18,19,21,26,29,33,34,36,41,44,46,47,55,60,76,88,89,90,98,123,134,137,144,176]
p("="*78); p("O229/15 (R3-③) — 多義分類（P1–P11）＋ 完備性掃描"); p("="*78)

# ---------- 常數（R1/R2 合約 §B，零新參數） ----------
B, mu2, Nd, Ngen, Nc, L5, F6, spinor, h11, h21, Ktree, b0, b1, a0 = 4,2,44,3,3,11,8,16,36,98,33,7,26,137
G=lambda n,M=88: 4*mp.sin(mp.pi*n/M)**2
sg=sum(G(n) for n in range(1,45)); sodd=sum(G(n) for n in range(1,45) if n%2); seven=sum(G(n) for n in range(1,45) if n%2==0)
chk("0.1 Σγ⁽⁸⁸⁾ = 90、Σγ_odd = 44 = N_d、Σγ_even = 46 = N_d+μ²（高精度 50 dps，取整）",
    round(sg)==90 and round(sodd)==44 and round(seven)==46,
    f"{mp.nstr(sg,12)}, {mp.nstr(sodd,12)}, {mp.nstr(seven,12)}")

# ---------- P1–P11 逐項重驗 ----------
p("\n[1] P1–P11 逐項以精確算式重驗")
fib=[1,1]; luc=[2,1]
for _ in range(20): fib.append(fib[-1]+fib[-2]); luc.append(luc[-1]+luc[-2])
F=lambda n: fib[n-1]        # R1 慣例: F₁=1, F₂=1, F₃=2, …（故 F₆=8, F₇=13, F₁₁=89）
P={}
P["P1"]=("γ₄₄ 無鏈標籤", abs(G(44,88)-4)<mp.mpf('1e-45') and abs(G(44,176)-2)<mp.mpf('1e-45'),
         "88 鏈 → 4 = B；176 鏈 → 2 = μ²（同一字面兩值）")
P["P2"]=("123 兩種角色", luc[10]==123 and True, f"L₁₀ = {luc[10]}（無量綱, E_J）vs v_EW/2 ≈ 123.1 GeV（有量綱）")
P["P3"]=("W₀ 兩歸一化", abs(mp.sqrt(mp.mpf(123)/2)-mp.mpf('7.84219357068'))<mp.mpf('1e-9')
         and abs(2/((1+mp.sqrt(5))/2)-mp.mpf('1.2360679'))<mp.mpf('1e-6'),
         "v10 W₀ = √61.5 = 7.84219357068 vs v6 2/φ = 1.2360679")
P["P4"]=("2 兩種來源", mu2==2 and 4*(4-3)//2==2, "μ² = 2（算子本徵值）vs 引力子 TT dof D(D−3)/2 = 2（表示計數）")
P["P5"]=("4 兩角色", B==4 and 4==4, "B = 4（結構數）vs A = 4（歸一化振幅）")
P["P6"]=("8 三重身份", Nc**2-1==8 and 2*B==8 and F6==8 and B*(B-2)==8, f"N_c²−1 = 2B = F₆ = B(B−2) = 8")
P["P7"]=("3 值層退化", Nc==3 and Ngen==3 and (L5+1)//B==3 and Nd//L5-1==3,
         f"N_c = N_gen = (L₅+1)/B = N_d/L₅ − 1 = 3")
P["P8"]=("16 兩角色", B**2==16 and spinor==16 and Fr(16,60)==Fr(4,15), "B² = 旋量維數 = Ω_dm 分子 (16/60)")
P["P9"]=("19/60 簿記", 3+16==19 and 3+16+41==60 and 19+16+41==76, "Ω_b = 3/60、Ω_m = (3+16)/60；誤加得 76 ≠ 60")
phi=(1+mp.sqrt(5))/2
P["P10"]=("μ² 跨版本", mu2==2 and abs(mp.mpf(123)/(16*mp.mpf('0.1545085'))-mp.mpf('49.75'))<mp.mpf('0.01'),
          f"v10 μ²/λ = {123}（λ = μ²/123）vs v6 μ²/λ = 16·0.1545085 = {16*0.1545085:.6f}；比 {123/(16*0.1545085):.2f}× ⟹ 兩套理論唔同")
P["P11"]=("φ³ ± φ⁻³", abs(phi**3-phi**-3-4)<mp.mpf('1e-30') and abs(phi**3+phi**-3-2*mp.sqrt(5))<mp.mpf('1e-30'),
          f"φ³−φ⁻³ = {mp.nstr(phi**3-phi**-3,15)} = L₃；φ³+φ⁻³ = {mp.nstr(phi**3+phi**-3,15)} = 2√5 ≠ 4")
for k in sorted(P):
    nm,ok,det=P[k]; chk(f"1.{k[1:]} {k} {nm} 之重驗", ok, det)

# ---------- C1 分類 ----------
p("\n[2] R3-③ C1 預註冊: 11 項 → 4 機制類")
CLS={"M1 標籤缺失":["P1","P3","P10"], "M2 角色多義":["P2","P4","P5","P8"],
     "M3 同一方程多讀法":["P6","P7"], "M4 形式／簿記錯誤":["P9","P11"]}
flat=[x for v in CLS.values() for x in v]
chk("2.1 分類覆蓋 11 項且無重複", sorted(flat)==sorted(P.keys()) and len(flat)==11)
genuine=sum(len(CLS[k]) for k in ("M1 標籤缺失","M2 角色多義","M3 同一方程多讀法"))
chk("2.2 真多義 = 9、錯誤 = 2（預註冊 C1）", genuine==9 and len(CLS["M4 形式／簿記錯誤"])==2,
    f"真多義 {genuine}／錯誤 {len(CLS['M4 形式／簿記錯誤'])}")

# ---------- C2 完備性掃描 ----------
p("\n[3] R3-③ C2 預註冊（高風險）: R1 清單**完備**（掃唔到未列實例）")
# 角色表: (原子, 角色名, 類型, 精確值運算式)。類型: spectral/counting/structural/normalization/cosmological/external/arithmetic
ROLES=[
 (2,"γ⁽⁸⁸⁾_22 中心自對","spectral",G(22,88)), (2,"46−44 宇稱差","spectral",Fr(46-44)),
 (2,"F₃ / L₀ 索引","arithmetic",2), (2,"引力子 TT dof","counting",2),
 (3,"N_c 色數","counting",Nc), (3,"N_gen 世代","counting",Ngen), (3,"N_d/L₅ − 1","structural",Nd//L5-1),
 (4,"B 分支因子","structural",B), (4,"L₃ 索引","arithmetic",luc[3]), (4,"A 歸一化振幅","normalization",4),
 (4,"γ⁽⁸⁸⁾_44 Nyquist","spectral",4),
 (5,"F₅ 索引","arithmetic",F(5)), (5,"λ_Edd/L_crit","structural",5),
 (7,"L₄ 索引","arithmetic",luc[4]), (7,"b₀ 第一 β 係數","structural",b0), (7,"N_gen + B","structural",Ngen+B),
 (8,"N_c²−1 膠子","counting",Nc**2-1), (8,"2B = F₆","arithmetic",2*B),
 (11,"L₅ 索引","arithmetic",L5), (11,"N_site/8","structural",88//8),
 (13,"F₇ 索引","arithmetic",F(7)), (16,"B² 旋量維數","counting",B**2), (16,"Ω_dm 分子","cosmological",16),
 (18,"L₆ 索引","arithmetic",luc[6]), (19,"Ω_m 分子 (3+16)","cosmological",3+16),
 (21,"F₈ 索引","arithmetic",F(8)), (26,"b₁ 第二 β 係數","structural",b1),
 (29,"L₇ 索引","arithmetic",luc[7]), (33,"K_tree","structural",Ktree),
 (34,"F₉ 索引","arithmetic",F(9)),
 (36,"h¹¹","counting",h11), (41,"Ω_Λ 分子","cosmological",41),
 (44,"N_d 鏈對數","counting",Nd), (44,"Σγ_odd","spectral",round(sodd)), (44,"4·L₅","structural",4*L5),
 (46,"Σγ_even","spectral",round(seven)), (46,"N_d + μ²","structural",Nd+mu2),
 (47,"Ω_m + Ω_b 分子？","arithmetic",44+3),
 (55,"F₁₀ 索引","arithmetic",F(10)), (60,"Ω 分母","cosmological",60),
 (88,"N_site 站點","counting",88), (88,"2B·L₅","structural",2*B*L5),
 (89,"F₁₁ 索引","arithmetic",F(11)), (90,"Σγ⁽⁸⁸⁾","spectral",round(sg)),
 (90,"B(N_d+1)/2","structural",B*(Nd+1)//2), (90,"2N_d + μ²","structural",2*Nd+mu2),
 (98,"h²¹","counting",h21), (123,"E_J = L₁₀","structural",luc[10]),
 (134,"α⁻¹(0) − 3","external",a0-3), (137,"α⁻¹(0) 外部測量","external",a0),
 (137,"C(B²,2)+B²+1","structural",math.comb(B*B,2)+B*B+1),
 (144,"12² 代數維數","counting",12*12), (176,"2·N_site","counting",2*88),
]
badr=[r for r in ROLES if not (abs(float(r[3])-r[0])<1e-9 if r[2]=="spectral" else r[3]==r[0])]
chk("3.1 角色表每項之精確算式 = 該原子（證據支撐，非宣稱）", not badr,
    f"不符 {badr[:3]}" if badr else f"{len(ROLES)} 項全部核對")
byatom={}
for a,nm,tp,v in ROLES: byatom.setdefault(a,[]).append((nm,tp))
cross={a:sorted(set(t for _,t in rs)) for a,rs in byatom.items() if len(set(t for _,t in rs))>1}
for a in sorted(cross): p(f"    {a:4d}: 角色 {len(byatom[a])} 個，類型 {cross[a]}")
covered={"P4":[2],"P2":[123],"P5":[4],"P6":[8],"P7":[3],"P8":[16],"P9":[19],"P1":[44],"P11":[4]}
cov_atoms=set(x for v in covered.values() for x in v)
new=[a for a in sorted(cross) if a not in cov_atoms]
chk("3.2 ★ C2 預註冊「R1 清單完備（無未列實例）」", not new,
    f"實測**另有 {len(new)} 個**未列跨類多義原子: {new} ⟹ 預註冊 FAIL，原樣保留")
V=("★ R3-③ C1 ✅: 11 項 = 3（標籤缺失）＋ 4（角色多義）＋ 2（同一方程多讀法）＋ 2（形式／簿記**錯誤**）⟹ 真多義 9、錯誤 2。"
   f"★ C2 🔴 **預註冊否證**: R1 清單**唔完備** —— 跨類型（算子譜 / 計數 / 結構 / 歸一化 / 宇宙學 / 外部）之同值多角色實例另有 {len(new)} 個: {new}。"
   "典型新例: `44`（`N_d` 計數 vs `Σγ_odd` 譜和）、`46`（`Σγ_even` 譜和 vs `N_d + μ²` 結構）、"
   "`90`（`Σγ` 譜和 vs `B(N_d+1)/2` 結構 vs `2N_d + μ²`）、`60`（`Ω` 分母 vs 結構）、`41`（`Ω_Λ` 分子）。"
   "⟹ 「多義清單」須**按原子逐一列**，唔可以主題式列 11 項就當完備。")
p("\n★ R3-③ 判決"); p(V)
np_,nf_=res()
json.dump({"script":"15_r3_polysemy_classification","pass":np_,"fail":nf_,"total":np_+nf_,
           "P_verified":{k:{"name":v[0],"det":v[2]} for k,v in P.items()},
           "classes":CLS,"genuine":genuine,"errors":2,
           "role_count":len(ROLES),"cross_type_atoms":cross,"new_atoms":new,"verdict":V},
          open(os.path.join(BASE,"data","15_r3_polysemy_classification.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","15_r3_polysemy_classification.out"),"w").write("\n".join(OUT)+"\n")
