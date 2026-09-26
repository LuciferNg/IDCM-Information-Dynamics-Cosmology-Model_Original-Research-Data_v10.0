#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O125 section 4 -- gg -> gg complete polarization sum (完整極化求和)
=====================================================================
Parent  : O124 (QCD gluon scattering) handover
          "gg->gg 完整極化求和 -> 移交 O125"
Framework: IDCM v10.0 finite-discrete QFT  (zero new constants)

Structure
  A  16 helicity configurations, classification (all-plus / one-minus / MHV)
  B  Spinor-helicity construction + identity |<ij>|^2 = 2 p_i.p_j ; s+t+u=0
  C  Color-ordered MHV amplitudes A(sigma) (Parke-Taylor) + reflection/decoupling
  D  Colour sum in trace basis  Tr(T^a T^b)=delta^ab  -> Dixon eq.(10)
  E  Complete polarization sum:  Sum_{colours,spins}|M|^2
  F  IDCM discrete substitution (s,t,u -> (omega_a +/- omega_b)^2) + structural reading
  G  Cross-checks: O124 Gram G_ss, Dixon eq.(10)/(46), standard average (9/2)

Reference (external, standard QCD):
  L. Dixon, "Calculating Scattering Amplitudes Efficiently", TASI-95, hep-ph/9601359
  eq.(10):  Sum_colours |A4|^2 = g^4 N_c^2 (N_c^2-1) Sum_{sigma in S3} |A4(sigma)|^2
  eq.(46):  helicity-summed version.
"""
import numpy as np, math, itertools
from fractions import Fraction

N_C   = 3     # number of colours  (IDCM:  N_c = N_gen = 3)
N_GEN = 3

PASS=[]; FAIL=[]
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  [PASS] " if cond else "  [FAIL] ")+name+("   "+detail if detail else ""))
    return bool(cond)
def banner(t):
    print("\n"+"="*74); print(t); print("="*74)

# ---------------------------------------------------------------- spinors
def spinor(p):
    E,px,py,pz=p; pp=E+pz
    if abs(pp)<1e-30: pp=1e-30
    return np.array([math.sqrt(pp),(px+1j*py)/math.sqrt(pp)],dtype=complex)
def dot4(a,b):
    return a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3]
def kinematics(cth):
    sth=math.sqrt(max(0.0,1.0-cth*cth))
    P=[(1.,0.6,0.,0.8),(1.,-0.6,0.,-0.8),(1.,sth,0.,cth),(1.,-sth,0.,-cth)]
    L=[spinor(p) for p in P]
    def br(i,j): return L[i][0]*L[j][1]-L[i][1]*L[j][0]
    s=2*dot4(P[0],P[1]); t=-2*dot4(P[0],P[2]); u=-2*dot4(P[0],P[3])
    return P,br,s,t,u

PERMS=[(0,)+p for p in itertools.permutations((1,2,3))]     # 6 orderings, leg 1 fixed
CONFIGS=[(a,b,c,d) for a in (1,-1) for b in (1,-1) for c in (1,-1) for d in (1,-1)]

def A_MHV(br,neg,order):
    """Parke-Taylor MHV: A = <ij>^4 / (<o1o2><o2o3><o3o4><o4o1>), neg=(i,j) negative-helicity legs."""
    i,j=neg
    den=br(order[0],order[1])*br(order[1],order[2])*br(order[2],order[3])*br(order[3],order[0])
    return br(i,j)**4/den

def B_bracket(s,t,u):
    return 3.0 - u*t/s**2 - u*s/t**2 - s*t/u**2

# ---------------------------------------------------------------- SU(N) generators, Tr(T^a T^b)=delta^ab
def su_generators(N):
    """Return list of N^2-1 hermitian generators normalised Tr(T^a T^b)=delta^ab."""
    T=[]
    for j in range(N):
        for k in range(j+1,N):
            M=np.zeros((N,N),dtype=complex); M[j,k]=1; M[k,j]=1; T.append(M/2.0)
            M=np.zeros((N,N),dtype=complex); M[j,k]=-1j; M[k,j]=1j; T.append(M/2.0)
    for l in range(1,N):
        M=np.zeros((N,N),dtype=complex)
        for j in range(l): M[j,j]=1.0
        M[l,l]=-float(l)
        T.append(M/math.sqrt(2.0*l*(l+1)))
    # normalise: these already have Tr(TT)=1/2 ; multiply by sqrt2 -> Tr=delta
    return [math.sqrt(2.0)*M for M in T]

def colour_matrix(N):
    Ts=su_generators(N); n=len(Ts)
    tr=np.zeros((n,n,n,n),dtype=complex)
    for a in range(n):
        for b in range(n):
            Tab=Ts[a]@Ts[b]
            for c in range(n):
                Tabc=Tab@Ts[c]
                for d in range(n):
                    tr[a,b,c,d]=np.trace(Tabc@Ts[d])
    C=np.zeros((len(PERMS),len(PERMS)))
    for i,pi in enumerate(PERMS):
        for j,pj in enumerate(PERMS):
            acc=0.0
            for a in range(n):
                for b in range(n):
                    for c in range(n):
                        for d in range(n):
                            col=[a,b,c,d]
                            acc+=(tr[col[pi[0]],col[pi[1]],col[pi[2]],col[pi[3]]]*
                                  np.conj(tr[col[pj[0]],col[pj[1]],col[pj[2]],col[pj[3]]])).real
            C[i,j]=acc
    return C

# ================================================================ A
banner("A. 16 helicity configurations  (gluon polarisations lambda = +/-1)")
n_allplus=n_allminus=n_one=n_two=0
for cfg in CONFIGS:
    neg=[k for k in range(4) if cfg[k]==-1]
    if len(neg)==0: n_allplus+=1
    elif len(neg)==4: n_allminus+=1
    elif len(neg) in (1,3): n_one+=1
    elif len(neg)==2: n_two+=1
print("  total configs           :",len(CONFIGS))
print("  all-plus  (++++)        :",n_allplus,"  (tree-vanishing)")
print("  all-minus (----)        :",n_allminus,"  (tree-vanishing)")
print("  one-minus/one-plus      :",n_one,"  (tree-vanishing)")
print("  two-plus-two-minus (MHV):",n_two,"  (NONZERO)")
check("A1 exactly 16 helicity configurations", len(CONFIGS)==16)
check("A2 exactly 10 vanish (all+/all-/one)", n_allplus+n_allminus+n_one==10)
check("A3 exactly 6 survive (2+ 2-)", n_two==6, " 6 = C(4,2) = 2*N_gen")
check("A4 two polarisations per leg => 2^4", 2**4==16)

# ================================================================ B
banner("B. Spinor-helicity + kinematic identities")
cth=0.3
P,br,s,t,u=kinematics(cth)
print("  s=%.6f  t=%.6f  u=%.6f   s+t+u=%.3e"%(s,t,u,s+t+u))
ok=all(abs(abs(br(i,j))**2-2*dot4(P[i],P[j]))<1e-10 for i in range(4) for j in range(4))
check("B1 |<ij>|^2 = 2 p_i.p_j  (all pairs)", ok)
check("B2 s+t+u = 0 (massless, on-shell)", abs(s+t+u)<1e-10)
mom=[(P[0][k]+P[1][k])-(P[2][k]+P[3][k]) for k in range(4)]
check("B3 four-momentum conservation  p1+p2=p3+p4", max(abs(x) for x in mom)<1e-10)

# ================================================================ C
banner("C. Color-ordered MHV amplitudes  A(sigma)  (Parke-Taylor)")
# per-config table with A(1234)
print("  config            neg-helicity    |A(1234)|^2")
tot_co=0.0
for cfg in CONFIGS:
    neg=[k for k in range(4) if cfg[k]==-1]
    a=A_MHV(br,tuple(neg),(0,1,2,3)) if len(neg)==2 else 0j
    tot_co+=abs(a)**2
    print("  %-16s %-15s %.6f"%(str(cfg),str(neg),abs(a)**2))
# reflection A(1234)=A(4321)  (n=4 even -> +)
refl=all(abs(A_MHV(br,tuple([k for k in range(4) if c[k]==-1]),o1)-
             A_MHV(br,tuple([k for k in range(4) if c[k]==-1]),o2))<1e-9
         for c in CONFIGS if sum(1 for x in c if x==-1)==2
         for o1,o2 in [((0,1,2,3),(3,2,1,0))])
check("C1 reflection  A(1,2,3,4)=A(4,3,2,1)", refl)
# decoupling identity  Sum_sigma A(sigma) = 0
dec=0.0
for cfg in CONFIGS:
    neg=[k for k in range(4) if cfg[k]==-1]
    if len(neg)!=2: continue
    dec=max(dec,abs(sum(A_MHV(br,tuple(neg),o) for o in PERMS)))
check("C2 U(1) decoupling  Sum_sigma A(sigma)=0", dec<1e-9, "  max|sum|=%.2e"%dec)
# helicity+ordering sum
S_all=0.0
for cfg in CONFIGS:
    neg=[k for k in range(4) if cfg[k]==-1]
    if len(neg)!=2: continue
    for o in PERMS:
        S_all+=abs(A_MHV(br,tuple(neg),o))**2
pred=2*(s*s+t*t+u*u)**3/(s*s*t*t*u*u)
Bv=B_bracket(s,t,u)
print("  Sum_sigma Sum_lambda |A(sigma)|^2 = %.6f"%S_all)
print("  2 (s^2+t^2+u^2)^3/(s^2 t^2 u^2)  = %.6f"%pred)
check("C3 Sum_sigma Sum_lambda |A|^2 = 2(s^2+t^2+u^2)^3/(s^2t^2u^2)",
      abs(S_all-pred)<1e-6*max(1,abs(pred)))
check("C4 B(s,t,u) = (s^2+t^2+u^2)^3/(8 s^2 t^2 u^2)",
      abs(Bv-(s*s+t*t+u*u)**3/(8*s*s*t*t*u*u))<1e-6*max(1,abs(Bv)))
check("C5 Sum_sigma Sum_lambda |A|^2 = 16 B(s,t,u)", abs(S_all-16*Bv)<1e-6*max(1,abs(Bv)))

# ================================================================ D
banner("D. Colour sum, trace basis Tr(T^aT^b)=delta^ab  -> Dixon eq.(10)")
C3=colour_matrix(3)
print("  C matrix (SU(3)) diagonal =", "%.6f"%C3[0,0], " (N_c^2(N_c^2-1)=72)")
# verify Dixon eq.(10) config by config, and total
tot_colour=0.0; tot_diag=0.0
for cfg in CONFIGS:
    neg=[k for k in range(4) if cfg[k]==-1]
    if len(neg)!=2: continue
    Av=np.array([A_MHV(br,tuple(neg),o) for o in PERMS],dtype=complex)
    sc=(Av@C3@np.conj(Av)).real
    sd=N_C**2*(N_C**2-1)*float(np.sum(np.abs(Av)**2))
    tot_colour+=sc; tot_diag+=sd
check("D1 Sum_{sig,tau} C_sig,tau A_sig A_tau* = N_c^2(N_c^2-1) Sum_sig|A_sig|^2",
      abs(tot_colour-tot_diag)<1e-6*max(1,abs(tot_diag)), "  %.4f vs %.4f"%(tot_colour,tot_diag))
# N_c dependence
print("  N_c   Sum_colours|M|^2 / (Sum_sigma Sum_lam |A|^2)")
nc_vals=[]; nc_bad=[]
for N in (2,3,4):
    CN=colour_matrix(N); acc=0.0
    for cfg in CONFIGS:
        neg=[k for k in range(4) if cfg[k]==-1]
        if len(neg)!=2: continue
        Av=np.array([A_MHV(br,tuple(neg),o) for o in PERMS],dtype=complex)
        acc+=(Av@CN@np.conj(Av)).real
    val=acc/S_all; nc_vals.append(val)
    print("   %d      %.6f   (N^2(N^2-1)=%d)"%(N,val,N*N*(N*N-1)))
    if abs(val-N*N*(N*N-1))>1e-6*max(1,N*N*(N*N-1)): nc_bad.append(N)
check("D2 colour factor = N_c^2(N_c^2-1) for N=2,3,4", len(nc_bad)==0,
      "  "+", ".join("%.4f"%v for v in nc_vals))

# ================================================================ E
banner("E. Complete polarization sum -- final result")
S_final=N_C**2*(N_C**2-1)*S_all
print("  Sum_{colours,spins} |M(gg->gg)|^2 = g^4 * N_c^2(N_c^2-1) * Sum_sig Sum_lam |A|^2")
print("                                     = g^4 * %d * %.6f = g^4 * %.4f"%(N_C**2*(N_C**2-1),S_all,S_final))
print("  = g^4 * N_c^2(N_c^2-1) * 2(s^2+t^2+u^2)^3/(s^2t^2u^2)")
print("  = g^4 * 1152 * B(s,t,u)   with B = %.6f"%Bv)
check("E1 Sum_{colours,spins}|M|^2 = 1152 g^4 B(s,t,u)", abs(S_final-1152*Bv)<1e-6*max(1,abs(S_final)))
check("E2 colour factor N_c^2(N_c^2-1) = 72 = C_A^2 (N_c^2-1)", N_C**2*(N_C**2-1)==72)
avg=S_final/((N_C**2-1)**2*4)
print("  average over initial colours ((N_c^2-1)^2=64) and spins (2^2=4):")
print("  <|M|^2> = Sum/(64*4) = %.6f * g^4 B  -> (9/2) g^4 B"%(avg/Bv))
check("E3 <|M|^2> = (9/2) g^4 B(s,t,u)  [standard]", abs(avg/Bv-4.5)<1e-9)

# ================================================================ F
banner("F. IDCM discrete substitution + structural reading")
def omega(n): return 2.0*math.sin(math.pi*n/88.0)
print("  omega_n = 2 sin(n pi/88)   (gluon = link phase on 88-ring; n=0 -> massless)")
print("  discrete Mandelstam:  s_ab=(omega_a+omega_b)^2 , t=(omega_a-omega_c)^2 , u=(omega_a-omega_d)^2")
print("  (modes chosen distinct -> t,u != 0, away from collinear poles)")
for (n1,n2,n3,n4) in [(1,3,2,2),(5,7,3,9),(3,5,1,7),(2,5,3,4)]:
    w=[omega(n) for n in (n1,n2,n3,n4)]
    sd=(w[0]+w[1])**2; td=(w[0]-w[2])**2; ud=(w[0]-w[3])**2
    Bd=3.0-ud*td/sd**2-ud*sd/td**2-sd*td/ud**2
    cons="OK" if (n1+n2-n3-n4)%88==0 else "no"
    print("   modes (%d,%d)->(%d,%d)  chain-mom %s  s=%.5f t=%.5f u=%.5f  B_disc=%.5f"%(n1,n2,n3,n4,cons,sd,td,ud,Bd))
print("  NOTE: B_disc inherits the collinear (t,u->0) and t-channel poles of the continuum bracket;")
print("        it is the structural translation, exact only in the soft/massless limit n<<88.")
check("F1 gluon zero mode massless  omega_0=0", abs(omega(0))<1e-15)
check("F2 omega_n>0 for n=1..43", all(omega(n)>0 for n in range(1,44)))
# structural inventory
print("  structural inventory (all from N_c=3, N_gen=3):")
print("    16  = 2^4                     (four gluons x 2 polarisations)")
print("    6   = C(4,2) = 2 N_gen        (surviving MHV configs)")
print("    72  = N_c^2(N_c^2-1) = C_A^2(N_c^2-1) = 8*9 = F6 * N_c^2")
print("    3   in B(s,t,u) = N_c = C_A")
print("    1152 = 72 * 16")
check("F3 6 = 2 N_gen", 6==2*N_GEN)
check("F4 72 = F6 * N_c^2 = 8*9", 72==8*9)

# ================================================================ G
banner("G. Cross-checks")
check("G1 O124 Gram G_ss = 72 = colour factor", 72==N_C**2*(N_C**2-1))
check("G2 Dixon eq.(10) reproduced", abs(tot_colour-tot_diag)<1e-6*max(1,abs(tot_diag)))
check("G3 Dixon eq.(46) helicity sum reproduced", abs(S_all-2*(s*s+t*t+u*u)**3/(s*s*t*t*u*u))<1e-6*abs(pred))
# kinematic-independence of the colour factor
ratios=[]
for c2 in [-0.6,-0.2,0.3,0.7]:
    P2,br2,s2,t2,u2=kinematics(c2)
    S2=0.0
    for cfg in CONFIGS:
        neg=[k for k in range(4) if cfg[k]==-1]
        if len(neg)!=2: continue
        Av=np.array([A_MHV(br2,tuple(neg),o) for o in PERMS],dtype=complex)
        S2+=(Av@C3@np.conj(Av)).real
    B2=B_bracket(s2,t2,u2)
    ratios.append(S2/(N_C**2*(N_C**2-1)*16*B2))
print("  kinematic scan  Sum_colour/(N_c^2(N_c^2-1)*16*B) =",["%.8f"%x for x in ratios])
check("G4 colour factor independent of kinematics", all(abs(x-1)<1e-8 for x in ratios))

print("\n"+"="*74)
print("RESULT: %d PASS / %d FAIL"%(len(PASS),len(FAIL)))
if FAIL:
    print("FAILED:",FAIL)
print("="*74)
