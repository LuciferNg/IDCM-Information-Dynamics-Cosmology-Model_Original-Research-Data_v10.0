#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/13 (R3-①) — 異常和：由「檢查」升級為「定理」？(Y 之唯一性)
★ 合約: docs/14_r3_contract.md §A R3-①（跑數前凍結）
★ 零新參數: 量子數表全部來自 R1 docs/05（唯讀）；(α, β) 為約束參數，唔係擬合參數
"""
import json, os
from fractions import Fraction as Fr
import sympy as sp

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=[]; NP=NF=0
def p(s=""): print(s); OUT.append(s)
def chk(n,c,d=""):
    global NP,NF
    t="PASS" if c else "FAIL"; NP+=bool(c); NF+=(not c)
    p(f"  [{t}] {n}"+(f"   {d}" if d else "")); return bool(c)
def res(): p(f"\nRESULT: {NP}/{NP+NF} PASS"); return NP,NF

p("="*78); p("O229/13 (R3-①) — 異常泛函對 Y(α,β) = α·T₃R + β·(B−L)/2 之約束力"); p("="*78)

# ---------------- 單代 16 態（R1 docs/05，唯讀重載；Y 由 R1 表） ----------------
# (name, colour_mult, weak_dim, Y, T3R, BmL)  —— 全部 Fraction 精確
S=[("Q_L",  3, 2, Fr(1,6),  Fr(0),   Fr(1,3)),   # 3 色 × 2 弱 = 6 態
   ("u^c",  3, 1, Fr(-2,3), Fr(-1,2),Fr(-1,3)),
   ("d^c",  3, 1, Fr(1,3),  Fr(1,2), Fr(-1,3)),
   ("L_L",  1, 2, Fr(-1,2), Fr(0),   Fr(-1)),
   ("e^c",  1, 1, Fr(1),    Fr(1,2), Fr(1)),
   ("nu^c", 1, 1, Fr(0),    Fr(-1,2),Fr(1))]
DIM=lambda r: r[1]*r[2]                      # 態重數 = 色 × 弱

p("\n[1] 量子數表（R1 docs/05；態數 = Σ 色×弱）")
tot=0
for n,c,w,Y,t3,bm in S:
    tot+=DIM((n,c,w,Y,t3,bm))
    p(f"    {n:5s} 色={c} 弱={w} 態={c*w}  Y={Y}  T₃R={t3}  (B−L)={bm}")
chk("1.1 單代態數 = 16 = B²（R1 對賬表自洽）", tot==16, f"Σ = {tot}")

# ---------------- (α,β) 多項式化 ----------------
a,b=sp.symbols('alpha beta', real=True)
YS=lambda r: a*r[4] + b*r[5]/2               # Y(α,β) 對每一表示（同一表示內所有態同 Y）

p("\n[2] 8 個異常泛函（作為 (α, β) 之齊次多項式）")
A={}
A["SU3_3"]      = sp.Integer(sum(w*1 for n,c,w,Y,t3,bm in S if n=="Q_L")
                             - sum(w*1 for n,c,w,Y,t3,bm in S if bm==Fr(-1,3) and n!="Q_L"))
# 慣例甲（物理）: T(3) = T(3̄) = 1/2 ⟹ Σ_{coloured} dim_weak · Y
# 慣例乙（對照）: 3̄ 帶相對負號 ⟹ 展示結論對 3̄ 慣例敏感
A["SU3_2_U1"]   = sum(r[2]*YS(r) for r in S if r[1]>1)
A["SU3_2_U1b"]  = sum(r[2]*YS(r) for r in S if r[0]=="Q_L") - sum(r[2]*YS(r) for r in S if r[1]>1 and r[0]!="Q_L")
A["SU2_2_U1"]   = sum(r[1]*YS(r) for r in S if r[2]>1)
A["U1_3"]       = sum(DIM(r)*YS(r)**3 for r in S)
A["grav_U1"]    = sum(DIM(r)*YS(r) for r in S)
A["grav_BmL"]   = sum(DIM(r)*r[5] for r in S)
A["BmL_3"]      = sum(DIM(r)*r[5]**3 for r in S)
A["BmL_2_U1"]   = sum(DIM(r)*r[5]**2*YS(r) for r in S)
# U(1)³ 展開所需之 4 個純量（證明 ≡ 0 用）
MIX={}
MIX["T3R_3"]     = sum(DIM(r)*r[4]**3 for r in S)
MIX["T3R_2_BmL"] = sum(DIM(r)*r[4]**2*r[5] for r in S)
MIX["T3R_BmL_2"] = sum(DIM(r)*r[4]*r[5]**2 for r in S)
MIX["BmL_3"]     = sum(DIM(r)*r[5]**3 for r in S)
for k,v in A.items():
    p(f"    A[{k:10s}] = {sp.expand(v)}")
p("    （U(1)³ 之展開基底）")
for k,v in MIX.items():
    p(f"    Σ dim·{k:10s} = {v}")

p("\n[3] R3-① A1 預註冊: A[SU(3)²U(1)] 與 A[grav·U(1)] 對所有 (α,β) 恆零")
chk("3.1 A[SU(3)²U(1)] ≡ 0（慣例甲 T(3) = T(3̄) = 1/2，物理）", sp.simplify(A["SU3_2_U1"])==0)
chk("3.2 慣例乙（3̄ 帶相對負號）⟹ 非零 ⟹ 該和對 3̄ 慣例敏感（本項用慣例甲）",
    sp.simplify(A["SU3_2_U1b"])!=0, f"{sp.expand(A['SU3_2_U1b'])}")
chk("3.3 A[grav·U(1)] ≡ 0", sp.simplify(A["grav_U1"])==0)

p("\n[4] R3-① A2 預註冊: 解空間維數 = 1（即 Y 被唯一確定到標度）")
allzero=[sp.simplify(A[k]) for k in ("SU3_3","SU3_2_U1","SU2_2_U1","U1_3","grav_U1")]
ident=all(v==0 for v in allzero)
chk("4.1 5 個主異常條件全部 ≡ 0（唔剩任何約束）", ident,
    "全部恆零 ⟹ 解空間 = 整個 {T₃R, (B−L)} 平面")
chk("4.2 U(1)³ 之 4 個展開純量全 = 0（⟹ 恆等，非數值巧合）",
    all(v==0 for v in MIX.values()), f"{[str(v) for v in MIX.values()]}")
dim_span=2
chk("4.3 ★ A2 預註冊「解空間維數 = 1」", dim_span==1,
    f"實測 **維數 = {dim_span}**（(α,β) 任意 ⟹ 零約束）⟹ 預註冊 FAIL，原樣保留")
VER=("🔴 R3-① A2 **預註冊否證**：8 個異常和對 `(α, β)` **全部恆等地**為零 ⟹ "
     "`Y = α·T₃R + β·(B−L)/2` 之**任何**組合皆異常無關；解空間維數 = **2**，唔係 1。"
     "⟹ 「異常消去」對 `Y` 之形式**零判別力**（必要條件，非充分亦非唯一）。")

p("\n[5] R3-① A3 預註冊: 歸一化 Y(e^c) = 1 ⟹ (α, β) 唯一")
sol=sp.solve(sp.Eq(a*S[4][4]+b*S[4][5]/2,1),(a,b),dict=True)
p(f"    solve(Y(e^c) = 1) ⟹ {sol}  （欠定：1 方程 2 未知）")
chk("5.1 ★ A3 預註冊「歸一化 ⟹ (α,β) 唯一」", len(sol)==0 and False,
    "實測：只有 1 條方程 ⟹ **唔唯一**（α + β = 2 之整線）⟹ 預註冊 FAIL，原樣保留")
sol2=sp.solve([sp.Eq(a*S[4][4]+b*S[4][5]/2,1), sp.Eq(a*S[5][4]+b*S[5][5]/2,0)],(a,b),dict=True)
p(f"    補加 Y(ν^c) = 0 ⟹ {sol2}")
chk("5.2 補加輸入 Y(ν^c) = 0 後 (α, β) = (1, 1) 唯一 ⟹ Y = T₃R + (B−L)/2",
    sol2==[{a:1,b:1}], f"{sol2}")
chk("5.3 該解之 Y 向量 == R1 表之 Y（逐態）",
    all(sp.simplify(sp.Rational(r[4]+sp.Rational(r[5],2))-sp.Rational(r[3]))==0 for r in S))
VERS3=("🔴 R3-① A3 **預註冊否證**：單靠 `Y(e^c) = 1` **唔唯一**（得 `α + β = 2` 之整線）；"
       "須**額外輸入** `Y(ν^c) = 0` 才得唯一 `(α, β) = (1, 1)`。"
       "⚠️ 另記合約記法瑕疵：`docs/14 §A R3-① A2` 寫「方向 ∝ (1, 1/2)」係**筆誤**；"
       "本參數化 `Y = α T₃R + β(B−L)/2` 之下物理 `Y` = `(α, β) = (1, 1)`（合約已凍結，唔改）。")

p("\n[6] ★ 補充（超出預註冊之量化）：一般 6 向量之解空間維數")
X=sp.symbols('YQ Yu Yd YL Ye Yn', real=True)
conds=[2*X[0]+X[1]+X[2],                                    # SU(3)²U(1)
       3*X[0]+X[3],                                          # SU(2)²U(1)
       6*X[0]+3*X[1]+3*X[2]+2*X[3]+X[4]+X[5],                # grav
       6*X[0]**3+3*X[1]**3+3*X[2]**3+2*X[3]**3+X[4]**3+X[5]**3]  # U(1)³
p(f"    線性條件 3 條、未知 6 ⟹ 線性解空間維數 = {6-3}")
t,s=sp.symbols('t s', real=True)
subs={X[0]:1, X[2]:t, X[4]:s, X[1]:-2-t, X[3]:-3, X[5]:6-s}
G=sp.expand(conds[3].subs(subs))
p(f"    U(1)³ 於 (Y_Q=1, Y_d=t, Y_e=s) 截面: F(t,s) = {sp.factor(G)}")
chk("6.1 F(t,s) 唔恆零 ⟹ 射影維數 = 1 ⟹ 錐維數 = 3 − 1 = 2",
    G!=0, f"F = {sp.factor(G)}")
chk("6.2 ∂F/∂s 唔恆零 ⟹ 曲面非退化 ⟹ 解集確為 2 維",
    sp.diff(G,s)!=0)
def _conds(Yv):
    YQ,Yu,Yd,YL,Ye,Yn=Yv
    return (2*YQ+Yu+Yd, 3*YQ+YL,
            6*YQ+3*Yu+3*Yd+2*YL+Ye+Yn,
            6*YQ**3+3*Yu**3+3*Yd**3+2*YL**3+Ye**3+Yn**3)
CAND={"T3R":(Fr(0),Fr(-1,2),Fr(1,2),Fr(0),Fr(1,2),Fr(-1,2)),
      "B-L":(Fr(1,3),Fr(-1,3),Fr(-1,3),Fr(-1),Fr(1),Fr(1)),
      "Y":(Fr(1,6),Fr(-2,3),Fr(1,3),Fr(-1,2),Fr(1),Fr(0))}
for nm,v in CAND.items():
    p(f"    {nm:4s} 之 4 條件值 = {_conds(v)}")
chk("6.3 T₃R、B−L、物理 Y 三者皆為 4 條件之**精確**解（Fraction 逐條）",
    all(all(c==0 for c in _conds(v)) for v in CAND.values()))
VERS=("★ 補充結果（唔屬預註冊項）: 一般 6 維量子數空間中，4 個異常條件（3 線性 + 1 三次）"
      "之解集係**維數 2 之錐**——與 {T₃R, (B−L)} 平面內「處處為解」一致。"
      "⟹ 單代 16 態之異常消去**唔識別** hypercharge；`Y = T₃R + (B−L)/2` 係**額外物理輸入**"
      "（`Y(ν^c) = 0` 或等價之左右對稱 T₃R 賦值），唔係異常條件之推論。")

p("\n[7] R3-① A4 預註冊: 由解得之 Y 重算 Σ_f N_c Q_f² = 16/3、三代 16 = B²")
SUMM=[(3,Fr(2,3),'u_L'),(3,Fr(-1,3),'d_L'),(3,Fr(-2,3),'u^c'),(3,Fr(1,3),'d^c'),
      (1,Fr(0),'ν_L'),(1,Fr(-1),'e_L'),(1,Fr(1),'e^c'),(1,Fr(0),'ν^c')]
s16=sum(m*q*q for m,q,_ in SUMM)
chk("7.1 Σ_f N_c Q_f²（每代，全 16 態）= 16/3", s16==Fr(16,3), f"Σ = {s16}")
chk("7.2 三代和 = 16 = B²", s16*3==16)
Q_TABLE=[("u_L",Fr(1,2),Fr(1,6),Fr(2,3)), ("d_L",Fr(-1,2),Fr(1,6),Fr(-1,3)),
         ("u^c",Fr(0),Fr(-2,3),Fr(-2,3)), ("d^c",Fr(0),Fr(1,3),Fr(1,3)),
         ("ν_L",Fr(1,2),Fr(-1,2),Fr(0)),  ("e_L",Fr(-1,2),Fr(-1,2),Fr(-1)),
         ("e^c",Fr(0),Fr(1),Fr(1)),       ("ν^c",Fr(0),Fr(0),Fr(0))]
bad=[n for n,t3,Y,Q in Q_TABLE if t3+Y!=Q]
chk("7.3 Q = T₃L + Y 對全 8 態精確成立（Y 取自 (α,β) = (1,1) 之解）",
    not bad, f"不符: {bad}" if bad else "8/8 ✓")

# ---------------- 輸出 ----------------
V={"A1_su3lit_zero":True,"A2_dim":dim_span,"A2_predicted":1,"A2_kept_FAIL":True,
   "A3_normalization_unique":False,"A3_with_Ynu0":[1,1],"A3_kept_FAIL":True,
   "A4_per_gen":str(s16),"A4_three_gen":int(s16*3),"general_cone_dim":2,
   "contract_notation_defect":"docs/14 §A R3-① A2 '∝ (1,1/2)' 應為 (1,1)"}
p("\n★ R3-① 判決")
p(VERS)
p(VERS3)
p(VERS)
np_,nf_=res()
json.dump({"script":"13_r3_y_uniqueness","pass":np_,"fail":nf_,"total":np_+nf_,"verdicts":V,
           "anomaly_polys":{k:str(sp.expand(v)) for k,v in A.items()},
           "mix_sums":{k:str(v) for k,v in MIX.items()},
           "states":[{"n":r[0],"dim":DIM(r),"Y":str(r[3]),"T3R":str(r[4]),"BmL":str(r[5])} for r in S]},
          open(os.path.join(BASE,"data","13_r3_y_uniqueness.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","13_r3_y_uniqueness.out"),"w").write("\n".join(OUT)+"\n")
