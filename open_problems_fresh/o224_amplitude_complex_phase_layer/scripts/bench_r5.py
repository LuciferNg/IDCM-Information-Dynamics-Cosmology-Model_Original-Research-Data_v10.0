import sys, time, numpy as np
sys.path.insert(0,'scripts')
import lib2i as L, importlib.util
spec = importlib.util.spec_from_file_location('w16','scripts/16_windows_global.py')
w16 = importlib.util.module_from_spec(spec); spec.loader.exec_module(w16)
G, idx, MUL, U, ids, types, hx, K = L.load_machine(); nax=len(ids)
KA=np.array(K,dtype=np.int32); NMUL=np.array(MUL,dtype=np.int32); hxa=np.array(hx,dtype=np.int32)
anti=np.array(L.antipodal(U,nax),dtype=np.int32).reshape(nax,nax).astype(bool)
adx=np.arange(nax)
X=w16.build_e4(nax,KA,NMUL,hxa)
A3=np.random.randint(-500,500,size=(nax,nax,nax)).astype(np.int32)
M=np.random.rand(nax,nax,nax)>0.5
def bench(f,rep=20):
    f(); t=time.time()
    for _ in range(rep): f()
    return (time.time()-t)/rep*1000
print('where 62^3        %.3f ms' % bench(lambda: np.where(M,A3,-w16.SENT)))
print('max   axis=-1     %.3f ms' % bench(lambda: A3.max(axis=-1)))
print('argmax axis=-1    %.3f ms' % bench(lambda: A3.argmax(axis=-1)))
print('argpartition K=2  %.3f ms' % bench(lambda: np.argpartition(A3,-2,axis=-1)[...,-2:]))
print('argpartition K=3  %.3f ms' % bench(lambda: np.argpartition(A3,-3,axis=-1)[...,-3:]))
print('argpartition K=6  %.3f ms' % bench(lambda: np.argpartition(A3,-6,axis=-1)[...,-6:]))
print('full sort 62^3    %.3f ms' % bench(lambda: np.sort(A3,axis=-1)))
i1=A3.argmax(-1)
print('put_along_axis    %.3f ms' % bench(lambda: np.put_along_axis(A3,i1[...,None],-w16.SENT,axis=-1)) if False else '')
fi=np.zeros(nax,bool); fi[[0,1,2,3]]=True
t=time.time()
for _ in range(50): w16.group_masks(nax,0,1,2,3,adx,anti,fi)
print('group_masks       %.3f ms' % ((time.time()-t)/50*1000))
t=time.time()
for _ in range(50): w16.fg_of_group(X,0,1,2,3,nax)
print('fg_of_group       %.3f ms' % ((time.time()-t)/50*1000))
# alternative top-2: argmax + take + put + argmax
def top2(A):
    i1=A.argmax(-1); v1=np.take_along_axis(A,i1[...,None],-1)[...,0]
    B=A.copy(); np.put_along_axis(B,i1[...,None],-w16.SENT,axis=-1)
    i2=B.argmax(-1); v2=np.take_along_axis(B,i2[...,None],-1)[...,0]
    return i1,i2,v1,v2
print('top2 via argmax   %.3f ms' % bench(lambda: top2(A3)))
# batched where on (8,62,62,62)
M8=np.broadcast_to(M,(8,)+M.shape); Ab=np.broadcast_to(A3,(8,)+A3.shape)
print('where 8x62^3      %.3f ms' % bench(lambda: np.where(M8,Ab,-w16.SENT),5))
print('argpartition K=2 on 8x62^3  %.3f ms' % bench(lambda: np.argpartition(Ab,-2,axis=-1)[...,-2:],5))
