#!/usr/bin/env python3
"""
O143 #26 — 修正節點匹配 + Gemini Part I [C] 重做 + Part II (圖路徑積分)
=====================================================================
#25 [C] 無效: T_obs 係 a5_nodes.txt 次序, V 係生成次序 → 索引錯配。
本輪: 0) 用 nearest-neighbour 匹配兩個座標集 (驗證 bijection)
      1) 重做 [C]: 移除 ℓ≤2 後 ℓ=3 是否存活
      2) 混疊洩漏量化: ℓ'=5 → ℓ=3 嘅實際貢獻
      3) Part II: 圖路徑積分 (60-node Laplacian) 測試 Gemini 嘅動力學提案

      ⚠️ 有效性附註 (09-19 後續, 見 docs/07 §1.3/§4):
      本腳本 [1]/[2] 嘅「精確座標」行**無效** — 匹配最大角距 18.52° (a5_nodes 唔係標準
      rhombicosidodecahedron), 次序對應錯。
      有效部分: [0] 匹配失敗發現 / [1]「a5 座標」行 (真採樣) / [3] Part II 證偽。
      混疊洩漏正確值 = 0.46% (用 a5 真座標) — 見 scripts/27 [B]。
      [1]「只留 ℓ=3」對 a5 座標退化 (W2 有 74 欄 > 60 節點 → 張滿全空間, 恆 0)。
      """
import numpy as np, math, json, itertools
from scipy.special import lpmv
from scipy.optimize import linear_sum_assignment

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'
G = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data'
rng = np.random.default_rng(2026)
phi = (1+5**0.5)/2

base = [(1,1,phi**3), (phi**2, phi, 2*phi), (2+phi, 0, phi**2)]
verts = []
for b in base:
    for perm in [b, (b[1],b[2],b[0]), (b[2],b[0],b[1])]:
        for sg in itertools.product([1,-1], repeat=3):
            v = tuple(s*x for s,x in zip(sg, perm))
            if v not in verts: verts.append(v)
Vex = np.array(verts, float); Vex /= np.linalg.norm(Vex, axis=1, keepdims=True)

a5 = np.loadtxt(f'{D}/a5_nodes.txt')
Va5 = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                 math.cos(math.radians(d))*math.sin(math.radians(r)),
                 math.sin(math.radians(d))] for r, d in a5])
T_obs = np.array(json.load(open(f'{G}/temps2_SMICA_4.17deg.json'))['A5_60'][:60])
ac = np.loadtxt(f'{D}/anchored_coloring.txt'); color = ac[:,3].astype(int)

print("="*80); print("  O143 #26 — 節點匹配 + [C] 重做 + Part II"); print("="*80)

# ── 0. 匹配 ──
Cst = Va5 @ Vex.T
ri, ci = linear_sum_assignment(-Cst)
print(f"\n[0] 匹配 a5_nodes ↔ 精確 Vex")
print(f"    最大角距 = {math.degrees(math.acos(np.clip(Cst[ri,ci].min(),-1,1))):.4f}°")
print(f"    係 bijection? {len(set(ci.tolist()))==60 and len(set(ri.tolist()))==60}")
# T_obs 在 a5 次序 → 重排到 Vex 次序
T_ex = np.zeros(60)
for i, j in zip(ri, ci):
    T_ex[j] = T_obs[i]
# 驗證: 兩邊算 ℓ=3 功率應一致
def real_sph(l, m, v):
    theta = np.arccos(np.clip(v[:,2],-1,1)); ph = np.arctan2(v[:,1], v[:,0])
    am = abs(m)
    norm = math.sqrt((2*l+1)/(4*math.pi) * math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am, l, np.cos(theta))
    if m == 0: return norm*P
    if m > 0: return math.sqrt(2)*norm*P*np.cos(am*ph)
    return math.sqrt(2)*norm*P*np.sin(am*ph)
def blocks(V, lmax=8):
    return {l: np.column_stack([real_sph(l,m,V) for m in range(-l,l+1)]) for l in range(lmax+1)}
BA5 = blocks(Va5); BEX = blocks(Vex)
def p3(V, T, B):
    x = T - T.mean()
    c, *_ = np.linalg.lstsq(B[3], x, rcond=None)
    return float((c**2).sum())
print(f"    ℓ=3 功率: a5 座標 = {p3(Va5,T_obs,BA5):.0f}, 精確座標(重排) = {p3(Vex,T_ex,BEX):.0f}")

# ── 1. [C] 重做: 移除 ℓ≤2 ──
print(f"\n[1] [C] 重做 (精確座標 + 正確匹配)")
for tag, V, T, B in [('a5 座標', Va5, T_obs, BA5), ('精確座標', Vex, T_ex, BEX)]:
    x = T - T.mean()
    W = np.column_stack([B[l] for l in range(3)])
    rest = x - W @ np.linalg.lstsq(W, x, rcond=None)[0]
    W2 = np.column_stack([B[l] for l in range(9) if l != 3])
    only3 = x - W2 @ np.linalg.lstsq(W2, x, rcond=None)[0]
    p_raw, p_rest, p_only = p3(V,T,B), p3(V,rest,B), p3(V,only3,B)
    def nullp(y, n=1500):
        v = [np.linalg.lstsq(B[3], rng.permutation(y), rcond=None)[0] for _ in range(n)]
        return np.array([(c**2).sum() for c in v])
    nr, no = nullp(x), nullp(only3)
    print(f"  {tag}:")
    print(f"    raw = {p_raw:.0f} (null {nr.mean():.0f}±{nr.std():.0f}, p={(1+(nr>=p_raw).sum())/(1+len(nr)):.4f})")
    print(f"    移除 ℓ≤2 後 = {p_rest:.0f} ({100*p_rest/p_raw:.1f}% 保留)")
    print(f"    只留 ℓ=3 (移除 ℓ≤2 及 ℓ≥4) = {p_only:.0f} (null {no.mean():.0f}±{no.std():.0f}, p={(1+(no>=p_only).sum())/(1+len(no)):.4f})")

# ── 2. ℓ'=5 → ℓ=3 洩漏量化 ──
print(f"\n[2] 混疊洩漏量化 (精確座標)")
B = BEX
x = T_ex - T_ex.mean()
c5, *_ = np.linalg.lstsq(B[5], x, rcond=None)
p5 = float((c5**2).sum())
# 用純 ℓ=5 場 (擬合值) 睇佢喺 ℓ=3 投影幾多
syn5 = B[5] @ c5
print(f"    場嘅 ℓ=5 功率 = {p5:.0f}")
print(f"    純 ℓ=5 擬合場喺 ℓ=3 投影 = {p3(Vex, syn5, B):.0f}")
print(f"    → 佔觀測 ℓ=3 功率 {100*p3(Vex,syn5,B)/p3(Vex,x,B):.2f}%")
# 對照: 純 ℓ=3 場喺 ℓ=5 投影
c3, *_ = np.linalg.lstsq(B[3], x, rcond=None); syn3 = B[3] @ c3
print(f"    對照: 純 ℓ=3 擬合場喺 ℓ=5 投影 = {float((np.linalg.lstsq(B[5], syn3, rcond=None)[0]**2).sum()):.0f}")

# ── 3. Part II: 圖路徑積分 ──
print(f"\n[3] Gemini Part II: 圖路徑積分測試")
print(f"  ⚠️ Gemini 用 176-Laplacian (88×88 鏈) 驅動 60-node 態 — 維度唔匹配")
print(f"     (O182 裁決: 冇逐點鏈索引) → 本輪用 60-node A5 圖 Laplacian 代替")
adj = np.zeros((60,60))
for i in range(60):
    for j in range(i+1,60):
        if math.degrees(math.acos(np.clip(np.dot(Va5[i],Va5[j]),-1,1))) < 28.0:
            adj[i,j] = adj[j,i] = 1
L60 = np.diag(adj.sum(1)) - adj
lam, U = np.linalg.eigh(L60)
kd = np.array([sum(1 for j in range(60) if adj[i,j] and color[i]==color[j]) for i in range(60)])
k2nodes = np.where(kd==2)[0]
print(f"    L60 譜範圍 [{lam.min():.3f}, {lam.max():.3f}]; k=2 節點 = {sorted(k2nodes.tolist())}")
psi0 = np.zeros(60); psi0[k2nodes] = 1/math.sqrt(len(k2nodes))
coef0 = U.T @ psi0
Tx = T_obs - T_obs.mean()
best = None
for tau in np.linspace(0, 20, 2001):
    Tt = U @ (np.exp(-1j*lam*tau) * coef0)
    for lab, sig in [('Re', Tt.real), ('Im', Tt.imag), ('|.|', np.abs(Tt))]:
        r = abs(np.corrcoef(sig, Tx)[0,1])
        if best is None or r > best[0]: best = (r, tau, lab, sig.copy())
print(f"    最佳: r = {best[0]:.4f} (τ = {best[1]:.2f}, {best[2]})")
print(f"    但 τ 係自由參數 (2001×3 = 6003 次掃描) → 需 null 校正")
# null: 隨機 ψ0 (12 個隨機節點) 嘅最佳 r 分佈
null_r = []
for _ in range(300):
    p0 = np.zeros(60); p0[rng.choice(60,12,replace=False)] = 1/math.sqrt(12)
    c0 = U.T @ p0
    bb = 0
    for tau in np.linspace(0, 20, 401):
        Tt = U @ (np.exp(-1j*lam*tau)*c0)
        for sig in [Tt.real, Tt.imag, np.abs(Tt)]:
            bb = max(bb, abs(np.corrcoef(sig, Tx)[0,1]))
    null_r.append(bb)
null_r = np.array(null_r)
print(f"    null (隨機 12 節點初始態): best r = {null_r.mean():.3f} ± {null_r.std():.3f}, 95% = {np.percentile(null_r,95):.3f}")
print(f"    觀測 best r = {best[0]:.4f} → p = {(1+(null_r>=best[0]).sum())/(1+len(null_r)):.4f}")
# node9 vs node20
Tt = best[3]
print(f"    node9 vs node20 (|T|): 觀測 {abs(T_obs[9]):.1f} vs {abs(T_obs[20]):.1f} (3.0×)")
print(f"      路徑積分預測: {abs(Tt[9]):.3f} vs {abs(Tt[20]):.3f} ({abs(Tt[9])/max(abs(Tt[20]),1e-12):.2f}×)")

res = {'match_max_deg': float(math.degrees(math.acos(np.clip(Cst[ri,ci].min(),-1,1)))),
       'p3_a5': p3(Va5,T_obs,BA5), 'p3_exact': p3(Vex,T_ex,BEX),
       'path_integral_best_r': best[0], 'path_tau': float(best[1]), 'path_label': best[2],
       'null_mean': float(null_r.mean()), 'null_std': float(null_r.std()),
       'path_p': float((1+(null_r>=best[0]).sum())/(1+len(null_r)))}
with open(f'{O143}/data/step23_gemini_part2.json','w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step23_gemini_part2.json")
