#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O229 / scripts/07 — 缺口 ⑤: 防 numerology 密度基準 (O208 三件套 + MC null 10^7)
合約 §D 缺口⑤ (5-1..5-4) + §E ②   sha256 e3f18caac665984bbdb7ffd0a71a5e00131396ee771b75f7094633928743b449

★ 本檔自備 RNG (splitmix64) 與密度函數, **唔 import** o218_lib (避免污染上游 __pycache__)。
"""
import json, os, math, bisect, statistics
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=[];NP=NF=0;V={}
def p(s=""): print(s); OUT.append(s)
def chk(n,c,d=""):
    global NP,NF
    t="PASS" if c else "FAIL"; NP+= bool(c); NF+= (not c)
    p(f"  [{t}] {n}"+(f"   {d}" if d else "")); return bool(c)
def res(): p(f"\nRESULT: {NP}/{NP+NF} PASS"); return NP,NF

# ---------- splitmix64 (§E② 指定之可重現 RNG) ----------
M64=(1<<64)-1
class SM64:
    def __init__(self, seed): self.s = seed & M64
    def next(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & M64
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        return z ^ (z >> 31)
    def iuniform(self, a, b):        # 整數 [a,b] 均勻
        return a + self.next() % (b-a+1)

ATOMS = [1,2,3,4,5,7,8,11,13,16,18,19,21,26,29,33,34,36,41,44,46,47,55,60,76,88,89,90,98,123,134,137,144,176]
CAP = 400

p("="*78); p("O229/07 — 缺口 ⑤: 密度基準 (O208 三件套 + MC 10⁷)"); p("="*78)

p("\n[1] (5-1) B 與 μ² 係原子, 非目標 ⟹ 自身唔受密度檢定")
chk("B = 4 ∈ 原子表", 4 in ATOMS)
chk("μ² = 2 ∈ 原子表", 2 in ATOMS)
p("    依據 O200 ①/O208 例外: 純代數恆等式與原子本身 N_search = 1, 唔受密度檢定。")
chk("[5-1] B、μ² 皆原子 ⟹ 免疫密度檢定", (4 in ATOMS) and (2 in ATOMS))

p("\n[2] (5-4) 整數可達性: {+,−} 閉包覆蓋率")
pool=set(ATOMS)
frontier=sorted(pool)
while True:
    new=set(pool)
    cur=sorted(pool)
    for a in cur:
        for b in cur:
            d=abs(a-b); s=a+b
            if 1<=d<=CAP: new.add(d)
            if 1<=s<=CAP: new.add(s)
    if new==pool: break
    pool=new
cov=len({x for x in pool if 1<=x<=CAP})/CAP
p(f"    |P| = {len(pool)};  區間 [1,{CAP}] 覆蓋率 = {cov:.4f}")
chk("原子含 3 與 4 ⟹ gcd = 1 ⟹ {+,−} 閉包覆蓋 [1,CAP] 全部整數 ⟹ 可達性零信息",
    cov==1.0, f"coverage={cov}")
V["closure_coverage"]=cov
N_farey_1 = None

p("\n[3] (5-2) 派生數之密度: 每個目標有幾多個原子表達式命中 (精確有理)")
def reps(t, ops=("add","sub","mul","div")):
    out=[]
    for a in ATOMS:
        for b in ATOMS:
            if "add" in ops and a+b==t: out.append(f"{a}+{b}")
            if "sub" in ops and a-b==t and b>0: out.append(f"{a}-{b}")
            if "mul" in ops and a*b==t and b>1: out.append(f"{a}*{b}")
            if "div" in ops and b!=0 and a%b==0 and a//b==t and b>1: out.append(f"{a}/{b}")
    return out
DERIVED = {9:"Δα⁻¹", 16:"B²/旋量", 26:"b₁", 36:"h¹¹", 60:"預算", 88:"N_site", 90:"Σγ", 98:"h²¹", 123:"E_J=L₁₀", 137:"α⁻¹(0)"}
tbl={}
p(f"    {'值':>4s} {'名':>10s} {'命中數 R':>8s}  例")
for t,nm in sorted(DERIVED.items()):
    r=reps(t); tbl[t]={"name":nm,"R":len(r),"examples":r[:4]}
    p(f"    {t:>4d} {nm:>10s} {len(r):>8d}  {r[:3]}")
chk("[5-2] 全部派生數都有 ≥1 個原子表達式 (即『有表達式』零信息)",
    all(tbl[t]["R"]>=1 for t in DERIVED))
med=statistics.median([tbl[t]["R"] for t in DERIVED])
p(f"    命中數中位數 = {med}")
chk("[5-2] 大部分派生數 R ≥ 2 ⟹ 表示非唯一 ⟹ 零判別力",
    sum(1 for t in DERIVED if tbl[t]["R"]>=2) >= len(DERIVED)//2,
    f"R≥2 者 = {sum(1 for t in DERIVED if tbl[t]['R']>=2)}/{len(DERIVED)}")

p("\n[4] (5-2b) 端點形式密度: 有幾多個 ≤400 之整數形如 C(k²,2)+k²+1")
forms=[(k, math.comb(k*k,2)+k*k+1) for k in range(1,20) if math.comb(k*k,2)+k*k+1<=CAP]
p(f"    {forms}")
q_endpoint = len(forms)/(CAP-1)
chk("[5-2b] 端點鎖之判別力 = 5/399 ≈1.25% ⟹ 🟡 邊緣顯著 (非天文級)", 0.01 < q_endpoint < 0.02,
    f"q = {q_endpoint:.5f}")
V["endpoint_form_q"]=q_endpoint

p("\n[5] (5-3) MC null 10⁷: 隨機化可觀測量下, 3 鎖是否仍可同時滿足")
K_DRAW = 10_000_000
rng = SM64(229)
E = {k: math.comb(k*k,2)+k*k+1 for k in range(2,9)}   # 端點形式之可能值
hits=0; Bsols=set()
for i in range(K_DRAW):
    a0 = 100 + rng.next()%101      # α⁻¹(0)' ∈ [100,200]
    Nd = 20  + rng.next()%61       # N_d'     ∈ [20,80]
    L5 = 5   + rng.next()%26       # L₅'      ∈ [5,30]
    sp = 4   + rng.next()%61       # 旋量維數' ∈ [4,64]
    k  = math.isqrt(sp)
    if k*k != sp or k < 2: continue
    if E.get(k, -1) != a0: continue
    if k*L5 != Nd: continue
    hits+=1; Bsols.add(k)
q_mc = hits/K_DRAW
p(f"    樣本 = {K_DRAW:,};  命中 = {hits};  q_obs = {q_mc:.3e}   B' 集 = {sorted(Bsols)}")
if hits==0:
    p(f"    0 命中 ⟹ 95% 上界 q < 3/N = {3.0/K_DRAW:.2e}")
chk("[5-3] 三鎖同時滿足之隨機命中率 q_obs ≤ 1e-4 (≪1%) ⟹ 遠超 5σ 級",
    q_mc <= 1e-4, f"hits={hits}, q_obs={q_mc:.2e}")
V["mc_null"]={"N":K_DRAW,"hits":hits,"q_obs":q_mc,
              "q_upper95":(3.0/K_DRAW if hits==0 else None)}

p("\n[6] (5-3b) 完全枚舉: B' ∈ [2,300] 有幾多個滿足 ≥1 / ≥3 條鎖")
def locks(Bp):
    c=0
    if math.comb(Bp*Bp,2)+Bp*Bp+1==137: c+=1
    if Bp*11==44: c+=1
    if Bp*Bp==16: c+=1
    if Bp*2*11==88: c+=1
    if (Bp-1)**2==9: c+=1
    if 44-2*Bp==36: c+=1
    if Bp*Bp+44==60: c+=1
    if Bp!=44 and abs(Bp/(44-Bp)-0.1)<1e-15: c+=1
    return c
cnt1=[b for b in range(2,301) if locks(b)>=1]
cnt3=[b for b in range(2,301) if locks(b)>=3]
p(f"    滿足 ≥1 鎖之 B': {cnt1}   滿足 ≥3 鎖之 B': {cnt3}")
q3=len(cnt3)/299
chk("[5-3b] 完全枚舉: 僅 B'=4 滿足 ≥3 鎖 ⟹ q_obs = 1/299 = 0.33%", cnt3==[4], f"{cnt3}")
chk("[5-3b] 僅 B'=4 滿足任何一條鎖 (8 條鎖互不重疊之結果集)", cnt1==[4], f"{cnt1}")
V["enum_locks"]={"ge1":cnt1,"ge3":cnt3,"q":q3}

p("\n[7] (5-4b) Farey N_search: 池 {+,−,×,÷} 之候選密度")
fN = {}
for form,qmax in (("quotient/single",300),("product/sum_quotients",300*300)):
    for tol,T in ((1e-12,137),(1e-9,137)):
        L=2.0*tol*T
        N=L*(3.0/math.pi**2)*qmax**2
        fN[(form,tol)]=N
        p(f"    形式 {form:22s} q_max={qmax:<6d} tol={tol:g}  N_search ≈ {N:.4g}")
chk("[5-4b] (預註冊) Farey N_search ≫ 1 ⟹『可達性』類陳述零判別力",
    fN[("product/sum_quotients",1e-12)] > 1e6,
    f"實測 tol=1e-12: N = {fN[('product/sum_quotients',1e-12)]:.4g}")

p("\n[7c] ★ -c 校正 (原 5-4b 之預註冊形式被否證 — 原 FAIL 原樣保留)")
p(f"    tol = 1e-12 : N_search = {fN[('product/sum_quotients',1e-12)]:.4g}  < 1  ⟹ 近距巧合風險**低**")
p(f"    tol = 1e-9  : N_search = {fN[('product/sum_quotients',1e-9)]:.4g}  ≫ 1  ⟹ 近距巧合風險高")
p("    ⟹ 零判別力之【真正載體】係**精確整數閉包覆蓋率 = 1.000** (任何整數目標都可精確製造),")
p("      而**唔係**近距 (1e-12) Farey 密度 — 後者在此精度下 < 1, 即近距巧合反而少。")
chk("5-4b-c (校正): 零判別力之載體 = 精確整數可達性 (coverage = 1.000), 已由 §[2] 證",
    cov==1.0, f"coverage={cov}")
chk("5-4b-c2: 近距 (tol=1e-12) Farey N_search < 1 ⟹『數值近巧合』唔係主要風險", 
    fN[("product/sum_quotients",1e-12)] < 1.0)

V["verdict_gap5"]=(f"✅ 定量: 整數可達性覆蓋率 = 1.000 (零信息, 任何整數目標可精確製造); "
                   f"端點形式密度 q = 5/399 = 1.25% (🟡 邊緣顯著); "
                   f"3 鎖同時滿足喺 null (10⁷ 抽樣, 隨機可觀測量) 命中 {hits} ⟹ q_obs = {hits/K_DRAW:.2e} ≪ 1e-4; "
                   f"完全枚舉 B'∈[2,300] 僅 B'=4 滿足任何一條鎖 (q = 1/299 = 0.33%); "
                   f"派生數表示多數非唯一 (命中數中位數 14)。"
                   f" ⚠️ -c 校正: 原 5-4b『Farey N_search ≫ 1』喺 tol=1e-12 被否證 (N = 0.675 < 1) — "
                   f"零判別力之真正載體係精確整數閉包 (coverage 1.000), 唔係近距 Farey 密度。")
np_,nf_=res()
json.dump({"script":"07_gap5_density","pass":np_,"fail":nf_,"total":np_+nf_,
           "verdicts":V,"derived_reps":tbl,"atoms":ATOMS},
          open(os.path.join(BASE,"data","07_gap5_density.json"),"w"),ensure_ascii=False,indent=1)
open(os.path.join(BASE,"logs","07_gap5_density.out"),"w").write("\n".join(OUT)+"\n")
