import sys, time, numpy as np, importlib.util
sys.path.insert(0,'scripts')
import lib2i as L
spec = importlib.util.spec_from_file_location('w16','scripts/16_windows_global.py')
w16 = importlib.util.module_from_spec(spec); spec.loader.exec_module(w16)
G_,idx,MUL,U,ids,types,hx,K = L.load_machine(); nax=len(ids)
KA=np.array(K,dtype=np.int32); NMUL=np.array(MUL,dtype=np.int32); hxa=np.array(hx,dtype=np.int32)
anti=np.array(L.antipodal(U,nax),dtype=np.int32).reshape(nax,nax).astype(bool)
adx=np.arange(nax); X=w16.build_e4(nax,KA,NMUL,hxa)
part = anti.argmax(axis=1)
# 1) exact symmetry tests on E4
E= X.astype(np.int64)
Ep = E[np.ix_(part,part,part,part)]
print('antipodal relabelling of E4: identical =', bool((Ep==E).all()), ' sign-flip =', bool((Ep==-E).all()),
      ' max|Ep-E| =', int(np.abs(Ep-E).max()))
E1 = E[np.ix_(part,adx,adx,adx)]
print('single-axis antipodal: identical =', bool((E1==E).all()), ' max|diff| =', int(np.abs(E1-E).max()))
# 2) section profile
def prep(a,a2,b,b2):
    fi=np.zeros(nax,bool); fi[[a,a2,b,b2]]=True
    return fi
fi=prep(0,1,2,3)
N=20
def bench(f,n=N):
    f(); t=time.time()
    for _ in range(n): f()
    return (time.time()-t)/n*1000
F3,G3 = w16.fg_of_group(X,0,1,2,3,nax)
print('fg_of_group        %.3f ms' % bench(lambda: w16.fg_of_group(X,0,1,2,3,nax)))
print('group_gate         %.3f ms' % bench(lambda: w16.group_gate(0,1,2,3,anti)))
print('window_setup       %.3f ms' % bench(lambda: w16.window_setup(nax,0,1,2,3,adx,anti,fi)))
setup = w16.window_setup(nax,0,1,2,3,adx,anti,fi)
print('group_masks        %.3f ms' % bench(lambda: w16.group_masks(nax,0,1,2,3,adx,anti,fi)))
for w in w16.WINDOWS:
    print('  reduced %-9s %.3f ms' % (w, bench(lambda w=w: w16.reduced_group(F3,G3,w,setup,nax))))
print('reduced ALL        %.3f ms' % bench(lambda: [w16.reduced_group(F3,G3,w,setup,nax) for w in w16.WINDOWS], 10))
# 3) where/stakes
B,pm,cc,ex = setup['anti_v3']
A0 = F3[:,:,B]
print('slice copy         %.3f ms' % bench(lambda: F3[:,:,B]))
print('  n_excl triples =', len(ex), 'sizes', [len(e[0]) for e in ex])
def scattertest():
    Z=A0.copy()
    for (ii,jj,kk) in ex: Z[ii,jj,kk]=w16.NEG_SENT
    return Z
print('excl scatter(4)    %.3f ms' % bench(scattertest))
print('topK K=2           %.3f ms' % bench(lambda: w16.top_k(A0.copy(),2)))
print('topK K=3           %.3f ms' % bench(lambda: w16.top_k(A0.copy(),3)))
