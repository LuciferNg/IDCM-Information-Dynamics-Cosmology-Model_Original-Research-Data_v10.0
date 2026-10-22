import sys, time, numpy as np, importlib.util, os
sys.path.insert(0,'scripts')
spec = importlib.util.spec_from_file_location('g17','scripts/17_windows_global_gpu.py')
g17 = importlib.util.module_from_spec(spec); spec.loader.exec_module(g17)
import lib2i as L, cupy as cp
cpu = g17.load_cpu_module()
G_,idx,MUL,U,ids,types,hx,K = L.load_machine(); nax=len(ids)
KA=np.array(K,dtype=np.int32); NMUL=np.array(MUL,dtype=np.int32); hxa=np.array(hx,dtype=np.int32)
anti=np.array(L.antipodal(U,nax),dtype=np.int32).reshape(nax,nax).astype(bool)
X=cpu.build_e4(nax,KA,NMUL,hxa)
chunk,_,_ = g17.make_gpu(None)
dX=cp.asarray(X); danti=cp.asarray(anti)
# timing: one chunk of 128 groups
gi=cp.asarray(np.arange(128,dtype=np.int64))
t=time.time()
r=chunk(dX,danti,0,1,gi,nax,128); cp.cuda.Stream.null.synchronize()
print('chunk(128 groups) = %.1f ms  -> per group %.3f ms ; full run est %.1f h' %
      ((time.time()-t)*1000, (time.time()-t)*1000/128, (time.time()-t)/128*62**4/3600))
for B in (256,384):
    gi=cp.asarray(np.arange(B,dtype=np.int64))
    t=time.time(); r=chunk(dX,danti,0,1,gi,nax,B); cp.cuda.Stream.null.synchronize()
    print('chunk(%d) = %.1f ms -> per group %.3f ms ; full run est %.2f h' % (B,(time.time()-t)*1000,(time.time()-t)*1000/B,(time.time()-t)/B*62**4/3600))
print('free VRAM GB = %.2f / %.2f' % (cp.cuda.Device(0).mem_info[0]/1e9, cp.cuda.Device(0).mem_info[0]/1e9+cp.cuda.Device(0).mem_info[1]/1e9))
