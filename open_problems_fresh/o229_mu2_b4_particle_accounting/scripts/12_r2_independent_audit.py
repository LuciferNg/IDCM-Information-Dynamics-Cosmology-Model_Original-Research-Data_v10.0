#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/12 (R2) — R2 之**獨立核對器**
★ 唔 import scripts/09、10、11，亦唔 import o218_lib；逐項**換算法**獨立重算
證: A 合約指紋(對 register 預註冊) / B 獨立重算 / C log↔data / D AST 真空 / E docs↔證據 / F 寫入範圍
"""
import ast, hashlib, json, os, re, glob
from fractions import Fraction as Fr
import mpmath as mp
mp.mp.dps=60
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO=os.path.dirname(os.path.dirname(BASE))
OUT=[];NP=NF=0
def p(s=""): print(s); OUT.append(s)
def chk(n,c,d=""):
    global NP,NF
    t="PASS" if c else "FAIL"; NP+=bool(c); NF+=(not c)
    p(f"  [{t}] {n}"+(f"   {d}" if d else "")); return bool(c)
def res(): p(f"\nRESULT: {NP}/{NP+NF} PASS"); return NP,NF

p("="*78); p("O229/12 (R2) — 獨立核對器（換算法、唔 import 受核腳本）"); p("="*78)

# ---------------- A 合約指紋 ----------------
p("\n[A] 凍結合約指紋 vs register 預註冊")
cs=hashlib.sha256(open(os.path.join(BASE,"docs","08_r2_contract.md"),'rb').read()).hexdigest()
reg=os.path.join(REPO,"problem_register","register.jsonl")
sha_in_reg=None
if os.path.exists(reg):
    for ln in open(reg,encoding="utf-8"):
        try: e=json.loads(ln)
        except Exception: continue
        blob=json.dumps(e,ensure_ascii=False)
        if "O229/R2" in blob and "sha256=" in blob:
            m=re.search(r"sha256=([0-9a-f]{64})",blob)
            if m: sha_in_reg=m.group(1)
p(f"    檔案 sha256 = {cs[:24]}…")
p(f"    register 註冊 = {(sha_in_reg or '(未找到)')[:24]}…")
chk("A1 docs/08_r2_contract.md 存在且 register 有預註冊 sha256", sha_in_reg is not None)
chk("A2 預註冊 sha256 == 現檔 sha256（跑數後未改合約）", sha_in_reg==cs)

# ---------------- B 獨立重算 (換算法) ----------------
p("\n[B] 獨立重算（逐項換算法）")
phi=(1+mp.sqrt(5))/2; psi=(1-mp.sqrt(5))/2; rt5=mp.sqrt(5)
def Lb(n): return phi**n+psi**n          # Binet: 對比 09 之遞迴
def Fb(n): return (phi**n-psi**n)/rt5
chk("B1 Binet Lucas: L₃ = 4, L₀ = 2, L₅ = 11 (對比 09 之遞迴表)",
    abs(Lb(3)-4)<mp.mpf('1e-45') and abs(Lb(0)-2)<mp.mpf('1e-45') and abs(Lb(5)-11)<mp.mpf('1e-45'),
    f"L₃={mp.nstr(Lb(3),12)}")
chk("B2 Binet Fib: F₃ = 2，且 4 ∉ Fibonacci（掃 n = 0..40, tol 1e-40）",
    abs(Fb(3)-2)<mp.mpf('1e-45') and not any(abs(Fb(n)-4)<mp.mpf('1e-40') for n in range(0,41)),
    f"F₃={mp.nstr(Fb(3),12)}")
r2=sum(1 for n in range(0,41) if abs(Lb(n)-2)<mp.mpf('1e-40') or abs(Fb(n)-2)<mp.mpf('1e-40'))
r4=sum(1 for n in range(0,41) if abs(Lb(n)-4)<mp.mpf('1e-40') or abs(Fb(n)-4)<mp.mpf('1e-40'))
p(f"    實現計數（0..40）: |R(2)| = {r2}   |R(4)| = {r4}")
chk("B3 |R(2)| = 2 且 |R(4)| = 1（與 09 結論獨立一致）", r2==2 and r4==1)

# V_min: 數值獨立重算 — (i) 黃金分割搜尋 (ii) 三點拋物線頂點 (對二次式精確) (iii) findroot 於導數
def Vnum(x): return -2*x + mp.mpf(2)/123*x*x
gr=(mp.sqrt(5)-1)/2
a,b=mp.mpf(0),mp.mpf(1000); c=b-gr*(b-a); d=a+gr*(b-a)
for _ in range(400):
    if Vnum(c)<Vnum(d): b=d
    else: a=c
    c=b-gr*(b-a); d=a+gr*(b-a)
xnum=(a+b)/2
p(f"    (i) 黃金分割 400 步: x* = {mp.nstr(xnum,20)}   註: 二次比較退化 ⟹ 精度上限 ~1e-30")
chk("B4 區間收縮法 x* = 61.5（精度受二次比較退化所限，容差 1e-25）",
    abs(xnum-mp.mpf('61.5'))<mp.mpf('1e-25'), f"|Δ| = {mp.nstr(abs(xnum-mp.mpf('61.5')),3)}")
x0,x1,x2=mp.mpf(0),mp.mpf(100),mp.mpf(500)          # 三點二次擬合頂點 (對二次式**精確**)
v0,v1,v2=Vnum(x0),Vnum(x1),Vnum(x2)
h1,h2=x1-x0,x2-x1
aa=((v2-v1)/h2-(v1-v0)/h1)/(h2+h1)
bb=(v1-v0)/h1-aa*h1
xv=-bb/(2*aa)
chk("B5 三點二次擬合頂點（對二次式精確）= 61.5", abs(xv-mp.mpf('61.5'))<mp.mpf('1e-45'),
    f"x* = {mp.nstr(xv,25)}")
xr=mp.findroot(lambda x: -2+mp.mpf(4)/123*x, mp.mpf(200))
chk("B6 findroot 於 dV/dx = 0 → x* = 61.5", abs(xr-mp.mpf('61.5'))<mp.mpf('1e-45'),
    f"x* = {mp.nstr(xr,25)}")
chk("B7 V_min 數值 = −61.5（由 B5 之頂點）", abs(Vnum(xv)+mp.mpf('61.5'))<mp.mpf('1e-45'),
    f"V_min = {mp.nstr(Vnum(xv),25)}")

# 全 16 態 QED 和 (獨立枚舉)
SUMM=[(3,Fr(2,3)),(3,Fr(-1,3)),(3,Fr(-2,3)),(3,Fr(1,3)),(1,Fr(0)),(1,Fr(-1)),(1,Fr(1)),(1,Fr(0))]
st=sum(m for m,_ in SUMM); s16=sum(m*q*q for m,q in SUMM)
chk("B8 全 16 態求和 = 16/3（獨立，對比 10 之 -c4）", st==16 and s16==Fr(16,3), f"態數={st}, Σ={s16}")
chk("B9 三代和 = 16 = B²", s16*3==16)

# 剛性: 端點鎖用**多項式形式**重算 (對比 11 之 binomial)
poly=lambda B: B**4+B**2-272
chk("B10 端點鎖多項式形式 B⁴+B²−272 = 0 ⟺ B = 4 (正根唯一)", poly(4)==0 and poly(5)!=0)
import sympy as sp
Bs=sp.Symbol('Bs',positive=True)
chk("B10b B⁴+B²−272 = 0 之正根 = 4", [r for r in sp.solve(Bs**4+Bs**2-272,Bs) if r.is_real and r>0]==[sp.Integer(4)])
# K16 / K17 於兩慣例
for lbl,A,Bv,mu2 in (("凍結 A=4", mp.mpf(4), mp.mpf(4)*(1+mp.mpf('1e-3')), mp.mpf(2)),
                     ("選單 A:=B", mp.mpf(4)*(1+mp.mpf('1e-3')), mp.mpf(4)*(1+mp.mpf('1e-3')), mp.mpf(2))):
    gmax=A*mp.sin(mp.pi/2)**2; gcen=A*mp.sin(mp.pi/4)**2
    p(f"    {lbl}: γ_max={mp.nstr(gmax,10)} B={mp.nstr(Bv,10)} | K16={'生存' if abs(Bv-gmax)<1e-25 else '斷'}"
      f" ; γ_(M/4)={mp.nstr(gcen,10)} μ²={mu2} | K17={'生存' if abs(mu2-gcen)<1e-25 else '斷'}")
d11=json.load(open(os.path.join(BASE,"data","11_r2_two_param_rigidity.json")))
g=d11["grid"]
regI  =sorted(set(k for (a,b),k in ((tuple(map(float,kk.split(','))),vv) for kk,vv in g.items()) if a==0.0 and b!=0.0))
regII =sorted(set(k for (a,b),k in ((tuple(map(float,kk.split(','))),vv) for kk,vv in g.items()) if b==0.0 and a!=0.0))
regIII=sorted(set(k for (a,b),k in ((tuple(map(float,kk.split(','))),vv) for kk,vv in g.items()) if a!=0.0 and b!=0.0 and a!=b))
regIV =sorted(set(k for (a,b),k in ((tuple(map(float,kk.split(','))),vv) for kk,vv in g.items()) if a!=0.0 and b!=0.0 and a==b))
chk("B11 data/11 之四區存活數 = 軸I 20 / 軸II 6 / 內點 5 / 橋線 6",
    regI==[20] and regII==[6] and regIII==[5] and regIV==[6], f"{regI} {regII} {regIII} {regIV}")
chk("B12 data/11 原點 = 22 且網格點數 = 25", g.get("0.0,0.0")==22 and len(g)==25)

# ---------------- C log↔data ----------------
p("\n[C] log ↔ data 逐腳本一致（01–12）")
EXP=[]
OKC=True
for f in sorted(glob.glob(os.path.join(BASE,"logs","*.out"))):
    nm=os.path.basename(f)[:-4]
    if not re.match(r"^\d\d_",nm): continue
    EXP.append(nm)
    txt=open(f,encoding="utf-8").read()
    m=re.findall(r"(?m)^RESULT:\s*(\d+)/(\d+)\s*PASS",txt)
    dj=os.path.join(BASE,"data",nm+".json")
    if len(m)!=1 or not os.path.exists(dj):
        chk(f"C {nm}: log 有唯一 RESULT 且有 data json", False); OKC=False; continue
    ps,tt=int(m[0][0]),int(m[0][1])
    d=json.load(open(dj,encoding="utf-8"))
    good=(d.get("pass")==ps and d.get("total")==tt and d.get("fail")==tt-ps)
    if not good: p(f"    不一致: {nm} log={ps}/{tt} data={d.get('pass')}/{d.get('total')}")
    OKC&=good
chk(f"C 全部 {len(EXP)} 個腳本 log↔data 一致", OKC, f"腳本數={len(EXP)}")

# ---------------- D AST 真空掃描 ----------------
p("\n[D] AST 真空斷言掃描（scripts/09–12；chk 第二參數為字面 True/1）")
vac=[]
for f in sorted(glob.glob(os.path.join(BASE,"scripts","*.py"))):
    n=os.path.basename(f)
    if not re.match(r"^(09|10|11|12)_",n): continue
    try: tree=ast.parse(open(f,encoding="utf-8").read())
    except SyntaxError as e: vac.append(f"{n}:SYNTAX {e}"); continue
    for nd in ast.walk(tree):
        if isinstance(nd,ast.Call) and getattr(nd.func,'id','')=='chk' and len(nd.args)>1 \
           and isinstance(nd.args[1],ast.Constant) and nd.args[1].value in (True,1):
            vac.append(f"{n}:{nd.lineno}")
chk("D 真空 chk = 0", not vac, f"{vac}" if vac else "0 ✓")

# ---------------- E docs ↔ 證據 ----------------
p("\n[E] docs ↔ 證據綁定")
def rd(n): 
    fp=os.path.join(BASE,"docs",n)
    return open(fp,encoding="utf-8").read() if os.path.exists(fp) else ""
NEED=[("09_r2_gap2b_index_identity.md","14/15"),
      ("10_r2_vmin_closed_form.md","13/13"),
      ("11_r2_two_param_rigidity.md","15/16"),
      ("12_r2_verdicts.md","42/44"),
      ("12_r2_verdicts.md","16/3"),
      ("10_r2_vmin_closed_form.md","−61.5"),
      ("09_r2_gap2b_index_identity.md","R(2)")]
miss=[(n,t) for n,t in NEED if t not in rd(n)]
chk("E docs 承載各腳本 RESULT 與關鍵數字", not miss, f"缺: {miss}" if miss else "全部命中")

# ---------------- F 寫入範圍 / 清單 ----------------
p("\n[F] 寫入範圍與清單")
files=[os.path.relpath(os.path.join(dp,f),BASE) for dp,_,fs in os.walk(BASE) for f in fs]
sc=sorted(os.path.basename(f) for f in files if f.startswith("scripts"))
dc=sorted(os.path.basename(f) for f in files if f.startswith("docs"))
chk("F1 scripts = 25 個，編號 01–25 完備（全鏈 closeout 2026-10-03 擴充）",
    len(sc)==25 and all(re.match(rf"^{i:02d}_",s) for i,s in zip(range(1,26),sc)), f"n={len(sc)}")
chk("F2 docs = 32 個（00–31）", len(dc)==32, f"n={len(dc)}: {dc}")
dd=sorted(os.path.basename(f) for f in files if f.startswith("data"))
ll=sorted(os.path.basename(f) for f in files if f.startswith("logs"))
PRE={re.match(r"^(\d\d)_",s).group(1) for s in sc}
dpre={x[:2] for x in dd if re.match(r"^\d\d_",x)}; lpre={x[:2] for x in ll if re.match(r"^\d\d_",x)}
orphan=sorted(x for x in dd+ll if (re.match(r"^\d\d_",x) and x[:2] not in PRE)
              or (not re.match(r"^\d\d_",x) and not re.match(r"^(chain_|legacy_|closeout_)",x)))
missd=sorted(PRE-dpre); missl=sorted(PRE-lpre)
chk("F3 data/logs 前綴 ⊆ 腳本前綴（無孤兒）；唯一允許未寫者 = 本核對器自身輸出 12",
    not orphan and set(missd)<={"12"} and set(missl)<={"12"},
    f"data={len(dd)} logs={len(ll)}; 缺={missd}/{missl}; 孤兒={orphan}")

p("\n★ 核對器發現（非 PASS/FAIL，記錄用）:")
p("   • R2-⑤ 之『8 = 2B』係 **naive 約定**（只計 u,d,e）之產物；標準 QED 約定計全 16 態")
p("     ⟹ 每代 16/3、三代 16 = **B²**（已於 scripts/10 §[3] 加 -c4 校正，B8 獨立重算一致）")
p("   • R2-④ 兩條預註冊（存活數 +1、橋線外恆 5）被否證，已原樣保留 FAIL 並各加 -c 校正")
np_,nf_=res()
json.dump({"script":"12_r2_independent_audit","pass":np_,"fail":nf_,"total":np_+nf_,
           "contract_sha256":cs,"registered_sha256":sha_in_reg,
           "independent":{"L3":mp.nstr(Lb(3),30),"F3":mp.nstr(Fb(3),30),
                          "xstar":mp.nstr(xnum,30),"Vmin":mp.nstr(Vnum(xnum),30),
                          "qed_std_per_gen":str(s16),"regimes":[regI,regII,regIII,regIV]},
           "scripts_seen":EXP},
          open(os.path.join(BASE,"data","12_r2_independent_audit.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","12_r2_independent_audit.out"),"w").write("\n".join(OUT)+"\n")
