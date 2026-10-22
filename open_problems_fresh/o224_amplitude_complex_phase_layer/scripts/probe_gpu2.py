import sys, time, numpy as np, importlib.util
sys.path.insert(0,'scripts')
spec = importlib.util.spec_from_file_location('g17','scripts/17_windows_global_gpu.py')
g17 = importlib.util.module_from_spec(spec); spec.loader.exec_module(g17)
import lib2i as L
import cupy as cp
cpu = g17.load_cpu_module()
G_,idx,MUL,U,ids,types,hx,K = L.load_machine(); nax=len(ids)
KA=np.array(K,dtype=np.int32); NMUL=np.array(MUL,dtype=np.int32); hxa=np.array(hx,dtype=np.int32)
anti=np.array(L.antipodal(U,nax),dtype=np.int32).reshape(nax,nax).astype(bool)
pool = cp.get_default_memory_pool()
X=cpu.build_e4(nax,KA,NMUL,hxa)
chunk,_,_ = g17.make_gpu(None)
dX=cp.asarray(X); danti=cp.asarray(anti)
for B in (64,128,256):
    pool.free_all_blocks()
    try:
        times=[]; 
        for rep in range(6):
            gi=cp.asarray(np.arange(B,dtype=np.int64))
            t=time.time(); r=chunk(dX,danti,0,1,gi,nax,B); cp.cuda.Stream.null.synchronize()
            dt=time.time()-t
            if rep>=2: times.append(dt)   # skip warmup
        med=float(np.median(times))
        print('B=%3d: median %.1f ms/chunk -> %.3f ms/group -> full-run %5.2f h (single stream)' % (B, med*1000, med*1000/B, med/B*62**4/3600))
        pool.free_all_blocks()
    except Exception as e:
        print('B=%d failed: %s' % (B, e)); pool.free_all_blocks()
print('VRAM free/total GB: %.2f / %.2f' % (cp.cuda.Device(0).mem_info[0]/1e9,(cp.cuda.Device(0).mem_info[0]+cp.cuda.Device(0).mem_info[1])/1e9))
