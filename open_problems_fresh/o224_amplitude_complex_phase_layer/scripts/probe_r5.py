import sys, time, numpy as np
sys.path.insert(0, 'scripts')
import lib2i as L
import importlib.util
spec = importlib.util.spec_from_file_location('w16', 'scripts/16_windows_global.py')
w16 = importlib.util.module_from_spec(spec); spec.loader.exec_module(w16)

G, idx, MUL, U, ids, types, hx, K = L.load_machine()
nax = len(ids)
KA = np.array(K, dtype=np.int32); NMUL = np.array(MUL, dtype=np.int32); hxa = np.array(hx, dtype=np.int32)
anti = np.array(L.antipodal(U, nax), dtype=np.int32).reshape(nax, nax).astype(bool)
adx = np.arange(nax); terms4 = w16.mermin_terms(4)
X = w16.build_e4(nax, KA, NMUL, hxa)
print('|E4|max =', int(np.abs(X).max()), ' terms4 =', len(terms4))

def prep(a, ap, b, bb):
    fi = np.zeros(nax, bool); fi[[a, ap, b, bb]] = True
    gate, masks, plane_cc = w16.group_masks(nax, a, ap, b, bb, adx, anti, fi)
    F3, G3 = w16.fg_of_group(X, a, ap, b, bb, nax)
    return gate, masks, plane_cc, F3, G3

# (a) timing on one group, all five windows
t0 = time.time()
for _ in range(10):
    for (a,ap,b,bb) in [(0,1,2,3),(0,1,7,3),(5,5,9,9)]:
        g,m,p,F,G = prep(a,ap,b,bb)
        for w in w16.WINDOWS:
            if g[w]: w16.reduced_group(F,G,w,m,p,nax)
print('reduced path: %.1f ms per group (5 windows)' % ((time.time()-t0)/30*1000))

# (b) reduced vs FULL on several groups, all windows
bad = 0
for (a,ap,b,bb) in [(0,1,2,3),(0,1,2,4),(0,1,8,6),(0,60,0,53),(5,5,9,9),(31,31,31,31),(0,31,1,30),(13,28,22,43)]:
    g,m,p,F,G = prep(a,ap,b,bb)
    fg = w16.full_group(F,G,m,p,nax)
    for w in w16.WINDOWS:
        if not g[w]: continue
        rp,rap,rn,ran = w16.reduced_group(F,G,w,m,p,nax)
        fp,fap,fn,fan = fg[w]
        okv = (rp==fp and rn==fn)
        # direct 8-term checks on both reduced extremes
        t8p = (a,ap,b,bb)+tuple(rap); t8n = (a,ap,b,bb)+tuple(ran)
        d8p = w16.direct8(X,t8p,terms4); d8n = w16.direct8(X,t8n,terms4)
        memp = w16.window_member(w,t8p,anti); memn = w16.window_member(w,t8n,anti)
        ok = okv and d8p==rp and d8n==rn and memp and memn
        if not ok:
            bad += 1
            print('BAD', (a,ap,b,bb), w, 'red',(rp,rn),'full',(fp,fn),'d8',(d8p,d8n),'mem',(memp,memn))
print('reduced-vs-full+direct8+member checks: %s' % ('ALL OK' if bad==0 else '%d BAD' % bad))
