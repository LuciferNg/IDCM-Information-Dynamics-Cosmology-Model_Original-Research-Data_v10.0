
import importlib.util, os, sys, time
H=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location("m", os.path.join(H,"02_o226_ledger_machine.py"))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
t0=time.time()
axes,U,ids,types,hv=m.load_inputs(); G,idx,MUL=m.build_group(); hx=[idx[m.qkey(h)] for h in hv]
print("n2I",len(G),"axis",len(U),"h",len(hx))
K=m.build_K(G,U)
t1=time.time()
# time 2000 pair runs
st=time.time()
for i in range(2000):
    a=i%62; b=(i*7)%62
    m.run_pair(K,MUL,hx,a,b,i%120,-1,mode="cap4")
el=time.time()-st
print("build %.1fs  2000 pairs %.3fs -> %.1f us/pair" % (t1-t0, el, el/2000*1e6))
print("full-pass estimate for 120 states: %.0f s" % (461280*el/2000))
print("redundancy estimate (923k pairs): %.0f s" % (921600*el/2000))
