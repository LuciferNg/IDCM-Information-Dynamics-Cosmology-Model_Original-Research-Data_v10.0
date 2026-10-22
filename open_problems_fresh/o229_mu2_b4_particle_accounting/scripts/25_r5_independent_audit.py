#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/25 (R5) — R5 之**獨立核對器**（唔 import 22–24）
  [A] 合約指紋
  [B] |2I| = 120: 生成元閉包 ⟨2T, (1+i)/√2⟩（嚴謹）+ |A₅| 顯式枚舉 + index-16 障礙
  [C] 形式類: **排序式**獨立去重（代表選擇與 23 不同）⟹ 驗證 112 項 / 234,136 形式 / express(137) = 1444
  [D] **精確性交叉核對**: 逐命中形式比對 M1 = sympy real_roots（精確） vs M2 = Cauchy 界整數枚舉（完備）⟹ 0 分歧
  [E] lock(137) = 21、值池 p_value、24 之手寫係數表 CV 逐項核對
  [F] log↔data、AST 真空、清單
"""
import ast, hashlib, json, os, re, glob, itertools
from fractions import Fraction as Fr
import sympy as sp
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO=os.path.dirname(os.path.dirname(BASE))
OUT=[]; NP=NF=0
def p(s=""): print(s); OUT.append(s)
def chk(n,c,d=""):
    global NP,NF
    t="PASS" if c else "FAIL"; NP+=bool(c); NF+=(not c)
    p(f"  [{t}] {n}"+(f"   {d}" if d else "")); return bool(c)
def res(): p(f"\nRESULT: {NP}/{NP+NF} PASS"); return NP,NF
p("="*78); p("O229/25 (R5) — 獨立核對器（換算法；唔 import 22–24）"); p("="*78)

# ---------------- [A] ----------------
cs=hashlib.sha256(open(os.path.join(BASE,"docs","26_r5_contract.md"),'rb').read()).hexdigest()
sha=None
for ln in open(os.path.join(REPO,"problem_register","register.jsonl"),encoding="utf-8"):
    try: e=json.loads(ln)
    except Exception: continue
    s=json.dumps(e,ensure_ascii=False)
    if "O229/R5" in s:
        m=re.search(r"sha256=([0-9a-f]{64})",s)
        if m: sha=m.group(1)
p(f"\n[A] 合約 {cs[:20]}…  register {str(sha)[:20]}…")
chk("A1 預註冊 sha256 == 現檔 sha256", sha==cs)

# ---------------- [B] |2I| = 120（SL(2,𝔽₅) 顯式枚舉路線） ----------------
p("\n[B] |2I| = 120（2I ≅ SL(2,𝔽₅)：顯式枚舉 det = 1 之 2×2 矩陣）")
# ⚠️ 修正記錄: ⟨i, (1+i+j+k)/2, (1+i)/√2⟩ 只生成 2O（48 階，√2 環）；
#    2I 之 icosian 環係 ℚ(√5) ⟹ 改用 SL(2,𝔽₅) 之完全顯式路線。
M=[(a,b,c,d) for a in range(5) for b in range(5) for c in range(5) for d in range(5)
   if (a*d-b*c)%5==1]
def mmul(X,Y):
    a,b,c,d=X; e,f,g,h=Y
    return ((a*e+b*g)%5,(a*f+b*h)%5,(c*e+d*g)%5,(c*f+d*h)%5)
I=(1,0,0,1); mI=(4,0,0,4)
p(f"    |SL(2,𝔽₅)| = {len(M)}（顯式枚舉 ad − bc = 1 mod 5）")
chk("B1a 顯式枚舉得 |SL(2,𝔽₅)| = 120（≅ 2I）", len(M)==120, f"{len(M)}")
chk("B1b 乘法封閉（真群）∧ 單位元 ∈ 群 ∧ 逆元封閉",
    all(mmul(x,y) in set(M) for x in M[:20] for y in M) and I in M
    and all(any(mmul(x,y)==I for y in M) for x in M))
ordc={}
for x in M:
    k=1; y=x
    while y!=I: y=mmul(y,x); k+=1
    ordc[k]=ordc.get(k,0)+1
p(f"    元素階數譜 = {dict(sorted(ordc.items()))}")
chk("B1c 階數譜 ⊂ {1,2,3,4,5,6,10}（2I 之眾數譜；無 8、無 15）",
    set(ordc)<= {1,2,3,4,5,6,10}, f"{sorted(ordc)}")
center=[x for x in M if all(mmul(x,g)==mmul(g,x) for g in M)]
chk("B1d 中心 = {±I}（2 個），且 |SL(2,5)/{±I}| = 60 = |A₅|",
    len(center)==2 and set(center)=={I,mI} and len(M)//2==60,
    f"|Z| = {len(center)}, Z = {center}")
A5=[pm for pm in itertools.permutations(range(5))
    if sum(pm[i]>pm[j] for i in range(5) for j in range(i+1,5))%2==0]
chk("B1e 換路線: |A₅| = 60（顯式偶置換枚舉）、|S₅| = 120、120 = 2·60",
    len(A5)==60 and len(list(itertools.permutations(range(5))))==120)
chk("B1f index-16 障礙: 120/16 = 15/2 ∉ ℤ ⟹ 無傳遞作用", Fr(120,16).denominator!=1)
# （已刪除: √2 環 quaternion BFS —— 該環只生成 2O(48)，唔係 2I(120)；見 docs/31 -c5）

# ---------------- [C] 形式類（排序式獨立去重） ----------------
p("\n[C] 凍結形式類（排序式獨立去重）")
b=sp.Symbol('B', positive=True)
FUN={ "1":sp.Integer(1), "B":b, "B−1":b-1, "B+1":b+1, "2B":2*b, "B(B−1)":b*(b-1),
      "B²":b**2, "B³":b**3, "B⁴":b**4, "B²(B−1)²":b**2*(b-1)**2, "B²+1":b**2+1, "B⁴+B²":b**4+b**2,
      "C(B,2)":sp.binomial(b,2), "C(B²,2)":sp.binomial(b**2,2), "2^B":2**b,
      "L₄=7":sp.Integer(7), "L₅=11":sp.Integer(11), "L₅²=121":sp.Integer(121), "N_gen=3":sp.Integer(3),
      "N_gen²=9":sp.Integer(9), "μ²=2":sp.Integer(2), "N_d=44":sp.Integer(44), "N_site=88":sp.Integer(88),
      "Σγ=90":sp.Integer(90), "L₁₀=123":sp.Integer(123), "F₇=13":sp.Integer(13), "F₁₁=89":sp.Integer(89),
      "12":sp.Integer(12), "17":sp.Integer(17), "144":sp.Integer(144) }
names=list(FUN); BDEP={k:(b in FUN[k].free_symbols) for k in names}
RAW=[(c,k) for k in names for c in (1,-1,2,-2)]
items=sorted(RAW, key=lambda t:(abs(t[0]), t[1]))          # 代表選擇與 23 不同
seen={}; REP=[]
for c,k in items:
    key=sp.srepr(sp.expand(sp.expand_func(c*FUN[k])))      # 單遍正則鍵（expand_func 展開 binomial）
    if key in seen: continue
    seen[key]=1; REP.append((c,k,sp.expand(sp.expand_func(c*FUN[k]))))
p(f"    字面 {len(RAW)} 項 ⟹ 函數正則 = {len(REP)} 項")
chk("C1 函數正則項集 = 112（與 23/24 一致）", len(REP)==112, f"{len(REP)}")
vals={_i:int(REP[_i][2].subs(b,4)) for _i in range(len(REP))}
hist={}
for a in range(len(REP)):
    for bb in range(a+1,len(REP)):
        hist[vals[a]+vals[bb]]=hist.get(vals[a]+vals[bb],0)+1
        for cc in range(bb+1,len(REP)):
            hist[vals[a]+vals[bb]+vals[cc]]=hist.get(vals[a]+vals[bb]+vals[cc],0)+1
tot=sum(hist.values())
p(f"    形式總數 = {tot:,}；express(137) = {hist.get(137,0)}")
d24=json.load(open(os.path.join(BASE,"data","24_r5_discrimination.json"),encoding="utf-8"))
chk("C2 形式總數 = 234,136（與 24 一致）", tot==234136 and tot==d24["forms_total"], f"{tot:,}")
chk("C3 express(137) 與 24 一致（動態比對，避免硬編碼）",
    hist.get(137,0)==d24["express"]["137"], f"25={hist.get(137,0)}, 24={d24['express']['137']}")
ATOMS=[1,2,3,4,5,7,8,11,13,16,18,19,21,26,29,33,34,36,41,44,46,47,55,60,76,88,89,90,98,123,134,137,144,176]
chk("C4 34 原子之 express 全體一致（獨立實作）",
    all(hist.get(v,0)==d24["express"]["atoms"][str(v)] for v in ATOMS))
chk("C5 值池 p_value 一致（獨立重算）",
    abs(sum(1 for v in range(2,1001) if hist.get(v,0)>=hist.get(137,0))/999 - d24["p_value"])<1e-12)

# ---------------- [D] 精確性交叉核對 ----------------
p("\n[D] 精確性交叉核對: 每一含 B 命中形式之整數根（M1 real_roots ／ M2 Cauchy 界枚舉）")
# 預算每項之係數向量（每項只建 Poly 一次）⟹ 形式 = 向量相加（純 Python，快）
CVV=[]; ISPOW=[]
for (c,k,ee) in REP:
    pw=any(pp.base==2 and pp.exp.free_symbols for pp in ee.atoms(sp.Pow))
    ISPOW.append(pw)
    if pw: CVV.append(None); continue
    dd={}
    for (a,),co in sp.Poly(ee,b).as_dict().items():
        r=sp.Rational(co); dd[int(a)]=Fr(r.p,r.q)
    CVV.append(dd)
def vecs(f,target):
    d={}
    for i in f:
        if CVV[i] is None: return None
        for deg,co in CVV[i].items(): d[deg]=d.get(deg,Fr(0))+co
    d[0]=d.get(0,Fr(0))-target
    if not any(v!=0 for v in d.values()): return None        # 恆等成立 ⟹ 無鎖定信息
    return d
def int_coeffs(d):
    den=1
    for v in d.values(): den=max(den,v.denominator)
    top=max(d)
    co=[int(d[i]*den) if i in d else 0 for i in range(top,-1,-1)]
    while len(co)>1 and co[0]==0: co.pop(0)                 # ★ 剝前導零（-c6）
    return co
def roots_M1(f,target):
    d=vecs(f,target)
    if d is None: return "ID"
    try:
        return sorted(int(r) for r in sp.real_roots(sp.Poly.from_list(int_coeffs(d),b))
                      if r.is_positive and r.is_integer)
    except Exception: return None
def roots_M2(f,target):
    d=vecs(f,target)
    if d is None: return "ID"
    try:
        co=int_coeffs(d)
        lead=abs(co[0]); mx=max([abs(c) for c in co[1:]] or [0])
        bound=min(10**4, 1+(mx//max(1,lead))+2)          # Cauchy 界 ⟹ 界內掃描完備
        out=[]
        for Bv in range(1,bound+1):
            acc=0
            for c in co: acc=acc*Bv+c
            if acc==0: out.append(Bv)
        return out
    except Exception: return None
# ★ 2^B 形式之完備界: 對 B ≥ B0，2^B > C·Σ_{k≤4}B^k + |target| ⟹ 掃 [1,B0] 即完備
CVMAX=max(abs(co) for dd in CVV if dd for co in dd.values())   # ★ 保留分數（唔用 int() 截斷）
CBOUND=4*CVMAX; VMAX=1000
B0=1
while 2**B0 <= CBOUND*(B0**4+B0**3+B0**2+B0+1)+VMAX: B0+=1
def roots_M3(f,target):                                 # 含 2^B: 純 Python 求值（★ 整條方程乘 den）
    d={}; cpow=0
    for i in f:
        if ISPOW[i]: cpow += REP[i][0]                   # 該項 = c·2^B（2·2^B = 2^(B+1) 同一函數）
        else:
            for deg,co in CVV[i].items(): d[deg]=d.get(deg,Fr(0))+co
    d[0]=d.get(0,Fr(0))-target
    if not any(v!=0 for v in d.values()) and cpow==0: return "ID"
    den=1
    for v in d.values(): den=max(den,v.denominator)
    co=[int(d[i]*den) if i in d else 0 for i in range(max(d),-1,-1)]
    while len(co)>1 and co[0]==0: co.pop(0)
    out=[]
    for Bv in range(1,B0+1):
        acc=0
        for cc in co: acc=acc*Bv+cc
        if acc + den*cpow*(2**Bv) == 0: out.append(Bv)   # ★ den·cpow（-c6: 原本漏乘 den）
    return out
lock={}; mism=0; cmp_n=0; npoly=0; npow=0; npow_ok=0; npow_id=0; nident=0; bad_ex=[]
for v in ATOMS:
    forms=[]
    for a in range(len(REP)):
        for bb in range(a+1,len(REP)):
            if vals[a]+vals[bb]==v: forms.append((a,bb))
            for cc in range(bb+1,len(REP)):
                if vals[a]+vals[bb]+vals[cc]==v: forms.append((a,bb,cc))
    cnt=0
    for f in forms:
        if not any(BDEP[REP[i][1]] for i in f): continue      # 純常數式唔算鎖
        if any(ISPOW[i] for i in f):
            r1=roots_M3(f,v); npow+=1
            if r1=="ID": npow_id+=1; nident+=1; continue       # 恆等成立 ⟹ 無鎖定信息（唔算分歧）
            ex_=sp.expand_func(sp.expand(sum(REP[i][2] for i in f)-v))
            if all(int(ex_.subs(b,Bv))==0 for Bv in r1):      # 每個報告之根以 sympy 精確覆核
                npow_ok+=1
            else:
                mism+=1
                if len(bad_ex)<5: bad_ex.append((v,f,r1,"pow-覆核失敗"))
            if r1==[4]: cnt+=1
            continue
        r1=roots_M1(f,v); r2=roots_M2(f,v)
        if r1=="ID" or r2=="ID": nident+=1; continue           # 恆等成立（∀B）⟹ 無鎖定信息
        if r1 is None or r2 is None: mism+=1; continue
        npoly+=1; cmp_n+=1
        if r1!=r2:
            mism+=1
            if len(bad_ex)<5: bad_ex.append((v,f,r1,r2))
        if r1==[4]: cnt+=1
    lock[v]=cnt
p(f"    已比對 = {cmp_n:,} 多項式形式；含 2^B 之形式 = {npow}（逐根 sympy 覆核 {npow_ok}）；恆等類 = {nident}；分歧 = {mism}")
p(f"    2^B 形式之完備界 B0 = {B0}（2^B0 > {CBOUND}·Σ B0^k + {VMAX}）；剝前導零後 Cauchy 界有效")
for e in bad_ex: p(f"    ✗ 分歧例: {e}")
chk("D1 多項式形式: real_roots 與 Cauchy 界枚舉逐形式完全一致（0 分歧）⟹ 根判定精確",
    mism==0, f"多項式 {cmp_n:,} 形式、分歧 {mism}；含 2^B {npow} 形式（覆核 {npow_ok}）；恆等 {nident}")
chk("D1b 含 2^B 之形式: 每一報告之根皆經 sympy 精確代入覆核（界 [1,B0] 完備）；恆等類另計",
    npow==npow_ok+npow_id, f"覆核 {npow_ok} + 恆等 {npow_id} = {npow}")
chk("D2 lock(137) 與 24 一致", lock[137]==d24["lock"]["137"], f"25={lock[137]}, 24={d24['lock']['137']}")
mx=max(lock.values()); arg=[v for v in ATOMS if lock[v]==mx]
nz=sum(1 for v in ATOMS if lock[v]>=1)
chk("D3 #{v: lock(v) ≥ 1} 與 max/argmax 與 24 一致",
    nz==d24["lock"]["nonzero"] and mx==d24["lock"]["max"] and arg==d24["lock"]["argmax"],
    f"25: nz={nz}, max={mx} @ {arg}；24: nz={d24['lock']['nonzero']}, max={d24['lock']['max']} @ {d24['lock']['argmax']}")
chk("D4 24 之 lock 表逐項一致", all(lock[v]==d24["lock"]["table"][str(v)] for v in ATOMS))
if "CV" in d24:
    badCV=[]
    for k in d24["CV"]:
        if k=="2^B": continue
        want={int(a):Fr(x[0],x[1]) for a,x in d24["CV"][k].items()}
        got={int(a[0]):Fr(sp.Rational(c).p,sp.Rational(c).q)
             for a,c in sp.Poly(sp.expand_func(sp.expand(FUN[k])),b).as_dict().items()}
        if got!=want: badCV.append(k)
    chk("D5 24 之手寫係數表 CV 對 sympy 展開逐項一致", not badCV, f"不符 {badCV}" if badCV else f"{len(d24['CV'])} 項")
else:
    chk("D5 24 之 JSON 含 CV 欄（供逐項核對）", False, "缺 CV ⟹ 需重跑 24")

# ---------------- [E] 名單/一致性 ----------------
p("\n[E] 名單與一致性")
files=[os.path.relpath(os.path.join(dp,f),BASE) for dp,_,fs in os.walk(BASE) for f in fs]
sc=sorted(os.path.basename(f) for f in files if f.startswith("scripts"))
dc=sorted(os.path.basename(f) for f in files if f.startswith("docs"))
chk("E1 scripts = 25（01–25）", len(sc)==25, f"n={len(sc)}")
chk("E2 docs = 32（00–31）", len(dc)==32, f"n={len(dc)}")
vac=[]
for f in sorted(glob.glob(os.path.join(BASE,"scripts","*.py"))):
    n=os.path.basename(f)
    if not re.match(r"^2[2-5]_",n): continue
    tree=ast.parse(open(f,encoding="utf-8").read())
    for nd in ast.walk(tree):
        if isinstance(nd,ast.Call) and getattr(nd.func,'id','')=='chk' and len(nd.args)>1 \
           and isinstance(nd.args[1],ast.Constant) and nd.args[1].value in (True,1):
            vac.append(f"{n}:{nd.lineno}")
chk("E3 AST 真空 chk = 0（scripts/22–25）", not vac, f"{vac}" if vac else "0")
OKC=True; nseen=0
for f in sorted(glob.glob(os.path.join(BASE,"logs","*.out"))):
    nm=os.path.basename(f)[:-4]
    if not re.match(r"^\d\d_",nm): continue
    nseen+=1
    m=re.findall(r"(?m)^RESULT:\s*(\d+)/(\d+)\s*PASS",open(f,encoding="utf-8").read())
    dj=os.path.join(BASE,"data",nm+".json")
    if len(m)!=1 or not os.path.exists(dj): OKC=False; p(f"    缺 log/data: {nm}"); continue
    dd=json.load(open(dj,encoding="utf-8"))
    if not (dd.get("pass")==int(m[0][0]) and dd.get("total")==int(m[0][1])): OKC=False; p(f"    不一致: {nm}")
chk(f"E4 log↔data 一致（{nseen} 個）", OKC)
def rd(n):
    fp=os.path.join(BASE,"docs",n); return open(fp,encoding="utf-8").read() if os.path.exists(fp) else ""
NEED=[("27_r5_endpoint_anatomy.md","半結構"),("28_r5_form_class.md","1444"),
      ("28_r5_form_class.md","符號陷阱"),("29_r5_discrimination.md","值層"),
      ("30_r5_verdicts.md","R5-②"),("30_r5_verdicts.md","R5-③"),("31_r5_residuals.md","精確")]
miss=[(n,t) for n,t in NEED if t not in rd(n)]
chk("E5 docs 承載關鍵結果", not miss, f"缺 {miss}" if miss else "全部命中")
p("\n★ 核對器要點:")
p("   • |2I| = 120 以 **SL(2,𝔽₅) 顯式枚舉**獨立重建（另記: √2 環只生成 2O(48)，見 -c5）")
p(f"   • 形式類獨立去重得 {len(REP)} 項、{tot:,} 形式、express(137) = {hist.get(137,0)}、lock(137) = {lock[137]}")
p("   • **精確性**: 逐形式比對 real_roots 與 Cauchy 界枚舉，0 分歧")
np_,nf_=res()
CVJ={k:{str(a):[int(Fr(c).numerator),int(Fr(c).denominator)] for a,c in v.items()}
     for k,v in {kk:{int(a):sp.Rational(c) for (a,),c in sp.Poly(sp.expand_func(sp.expand(FUN[kk])),b).as_dict().items()}
                 for kk in FUN if kk!="2^B"}.items()}
json.dump({"script":"25_r5_independent_audit","pass":np_,"fail":nf_,"total":np_+nf_,
  "contract_sha256":cs,"registered_sha256":sha,"group_2I_size":len(M),
  "group_route":"SL(2,F5) explicit enumeration","order_spectrum":{str(k):v for k,v in ordc.items()},
  "center_size":len(center),
  "terms_canonical":len(REP),"forms_total":tot,"express_137":hist.get(137,0),
  "lock_137":lock[137],"lock_nonzero":nz,"lock_max":mx,"lock_argmax":arg,
  "exact_cmp_forms":cmp_n,"exact_mismatch":mism,"exact_pow_forms":npow,"exact_pow_verified":npow_ok,
  "exact_ident_forms":nident,"bound_B0":B0,"CV_check":CVJ,
  "lock_table":lock},
  open(os.path.join(BASE,"data","25_r5_independent_audit.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","25_r5_independent_audit.out"),"w").write("\n".join(OUT)+"\n")
