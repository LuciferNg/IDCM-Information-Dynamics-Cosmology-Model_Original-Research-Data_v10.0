#!/usr/bin/env python3
"""O222 R22/QM part 3 -- A5 quotient verification (QV4') + exact CHSH from the frozen correlation record (QV5)."""
import importlib.util, json, os, collections
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("a2qm3", os.path.join(HERE,"09_a2_rollback.py")); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
G,idx,MUL=m.build_group(); n=len(G); out={}
e=[a for a in range(n) if all(MUL[a][b]==b for b in range(n))][0]
cen=[a for a in range(n) if all(MUL[a][b]==MUL[b][a] for b in range(n))]
z=[a for a in cen if a!=e][0]
def mul(a,b): return MUL[a][b]
# quotient 2I/{+-1}
cos={}
for a in range(n):
    key=min(a,mul(a,z))
    cos.setdefault(key,[]).append(a)
keys=sorted(cos); ki={k:i for i,k in enumerate(keys)}; qn=len(keys)
QM=[[ki[min(mul(a,b), mul(mul(a,b),z))] for b in keys] for a in keys]
qe=ki[min(e, mul(e,z))]
def pw(tab,a,k):
    r=a
    for _ in range(k-1): r=tab[r][a]
    return r
qord=[min(k for k in range(1,31) if pw(QM,a,k)==qe) for a in range(qn)]
qseen=set(); qcl=[]
for a in range(qn):
    if a in qseen: continue
    cl=set()
    for g in range(qn):
        gi=[b for b in range(qn) if QM[g][b]==qe][0]
        cl.add(QM[QM[g][a]][gi])
    qcl.append(len(cl)); qseen|=cl
out["QV4p"]={"group":"2I/{+-1}","order":qn,"conjugacy_classes":len(qcl),"class_sizes":sorted(qcl),
            "order_distribution":dict(sorted(collections.Counter(qord).items())),
            "expected_A5":{"order":60,"classes":5,"class_sizes":[1,12,12,15,20],"orders":{"1":1,"2":15,"3":20,"5":24}},
            "matches_A5": (qn==60 and len(qcl)==5 and sorted(qcl)==[1,12,12,15,20])}
# ---- QV5: exact CHSH from data/09
p=os.path.join(ROOT,"data","09_a2_correlation.json")
d=json.load(open(p,encoding="utf-8"))
shape={k:(type(v).__name__+(("[%d]"%len(v)) if isinstance(v,list) else "")) for k,v in d.items()}
def flat(v):
    if isinstance(v,list):
        if v and isinstance(v[0],list): return "nested"
        return v
    return [v]
print("data/09 shape:",shape)
res={"shape":shape}
for key in ("C1_num","C1rev_num","C2"):
    v=flat(d.get(key))
    if v=="nested" or v is None: res[key]="nested/None"; continue
    try:
        res[key]=[str(x)[:18] for x in v[:4]]
    except Exception as ex: res[key]="err:"+type(ex).__name__
res["denominator"]=str(d.get("denominator"))[:24]
# try exact CHSH: S = C1 + C1rev + C2 - C2rev , computed entrywise then max |S|
try:
    den=F(d["denominator"]) if not isinstance(d["denominator"],list) else F(d["denominator"][0])
    a=[F(str(x)) for x in d["C1_num"]]; b=[F(str(x)) for x in d["C1rev_num"]]; c=[F(str(x)) for x in d["C2"]]
    L=min(len(a),len(b),len(c))
    S1=[a[i]+b[i]+c[i]-c[i] for i in range(L)]
    S2=[a[i]+b[i]+c[i] for i in range(L)]
    res["S_plus_max"]=str(max(abs(x) for x in S1)); res["S_allmax"]=str(max(abs(x) for x in S2))
    res["classical_bound"]=2; res["tsirelson_2sqrt2_squared"]=8
except Exception as ex:
    res["chsh_error"]=type(ex).__name__+":"+str(ex)[:80]
out["QV5"]=res
print(json.dumps(out,ensure_ascii=False,indent=1)[:1500])
json.dump(out,open(os.path.join(ROOT,"data","50_r22_qm_verify3.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
