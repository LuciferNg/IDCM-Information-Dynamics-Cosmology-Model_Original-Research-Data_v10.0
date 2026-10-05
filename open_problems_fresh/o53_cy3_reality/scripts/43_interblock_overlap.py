#!/usr/bin/env python3
"""
O53 攻堅目標一 (核心): Y 矩陣 inter-block 分析 + φ^(-k/3) 檢驗
===================================================================
發現:
  - 3×12 block {0-11, 12-23, 24-35} 係最佳分組 (κ ratio 2.41)
  - 5 高-degree fields: 0(-742), 8(733), 4(-194), 3(137), 7(34)

核心問題: 12 維機制嘅幾何身份
  1. Y 矩陣 3×12 block 嘅 overlap 矩陣 (3×3 塊之間)
  2. 每塊 12×12 嘅完整譜 — 有冇 φ^(-k/3) 結構?
  3. Schur 分解: 主 12×12 塊 vs 交疊
  4. 3 個 12×12 block 本徵值: 12+12+12 = 36 個本徵值
"""
import os, json, math, sys
import numpy as np
from scipy.linalg import schur

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53 攻堅 1d: Inter-block overlap + φ^(-k/3)")
print("=" * 70)

with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)

K = np.zeros((36, 36, 36))
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val
J0 = np.array(jstar['Jstar_36D'])
Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2

# --- [1] 3×12 block 結構 ---
print("\n[1] Y 矩陣 3×12 blocks:")
blocks = {}
for bi in range(3):
    for bj in range(3):
        blocks[(bi, bj)] = Y[bi*12:(bi+1)*12, bj*12:(bj+1)*12]

# 每塊嘅最大奇異值 (inter-block strength)
print("\n    Inter-block 主奇異值 (3×3):")
smat = np.zeros((3, 3))
for bi in range(3):
    for bj in range(3):
        s = np.linalg.svd(blocks[(bi, bj)], compute_uv=False)[0]
        smat[bi, bj] = s
print(f"    {np.array2string(smat, precision=3)}")
print(f"    對角: {np.diag(smat)}")
print(f"    非對角 mean: {np.mean(smat[np.eye(3)==0]):.3f}")
print(f"    對角/非對角 = {np.diag(smat).mean()/np.mean(smat[np.eye(3)==0]):.2f}")

# --- [2] Overlap matrix (normalized) ---
print("\n[2] Normalized overlap (Frobenius):")
fnorm = np.zeros((3, 3))
for bi in range(3):
    for bj in range(3):
        fnorm[bi, bj] = np.linalg.norm(blocks[(bi, bj)], 'fro')
print(f"    Frobenius norms:")
print(f"    {np.array2string(fnorm, precision=2)}")
diag_mean = np.mean([fnorm[i,i] for i in range(3)])
off_mean = np.mean([fnorm[i,j] for i in range(3) for j in range(3) if i != j])
print(f"    對角 mean = {diag_mean:.2f}, 非對角 mean = {off_mean:.2f}, ratio = {diag_mean/off_mean:.2f}")

# --- [3] 每塊 12×12 譜 ---
print("\n[3] 每塊 12×12 譜 (φ 指數):")
all_block_evals = []
for g in range(3):
    blk = blocks[(g, g)]
    ev = np.linalg.eigvalsh(blk)
    ev_nz = np.sort(np.abs(ev))[::-1]
    all_block_evals.append(ev_nz)
    print(f"    Block {g} 前 8 |λ|: {np.array2string(ev_nz[:8], precision=4)}")
    # φ 指數
    exps = [math.log(1/l)/math.log(phi) if l > 1e-10 else float('inf') for l in ev_nz[:6]]
    print(f"      φ 指數: {[f'{e:+.2f}' for e in exps]}")

# --- [4] 全部 36 個 block 本徵值 vs φ^(-k/3) ---
print("\n[4] 36 個 block 本徵值 (3×12) vs φ^(-k/3):")
all_ev = np.concatenate(all_block_evals)
all_ev = np.sort(all_ev)[::-1]
# φ^(-k/3) 序列
for k in range(8):
    target = phi ** (-k/3)
    # 最近嘅 block 本徵值
    diff = np.abs(all_ev - target)
    idx = np.argmin(diff)
    print(f"    φ^(-{k}/3) = {target:.5f}  vs  λ[{idx}] = {all_ev[idx]:.5f}  (誤差 {diff[idx]/target*100:.1f}%)")

# --- [5] Schur 分解 ---
print("\n[5] Schur 分解 (Y = QTQ*):")
T, Q = schur(Y, output='real')
# T 嘅對角 = 本徵值 (實), 2×2 塊 = 複本徵值
print(f"    T 對角: {np.array2string(np.diag(T)[:12], precision=4)}")
# 檢查 T 有冇 block 結構
T_abs = np.abs(T)
# 3×12 分組下嘅 T 結構
print(f"    T 嘅 3×12 塊 Frobenius:")
Tf = np.zeros((3, 3))
for bi in range(3):
    for bj in range(3):
        Tf[bi, bj] = np.linalg.norm(T_abs[bi*12:(bi+1)*12, bj*12:(bj+1)*12])
print(f"    {np.array2string(Tf, precision=2)}")

# --- [6] 3×12 = 3 個同構 block? ---
print("\n[6] 3 個 12×12 block 同構檢驗:")
# 比較 block 0,1,2 嘅本徵值譜
e0 = np.sort(np.abs(all_block_evals[0]))[::-1][:8]
e1 = np.sort(np.abs(all_block_evals[1]))[::-1][:8]
e2 = np.sort(np.abs(all_block_evals[2]))[::-1][:8]
print(f"    Block 0: {np.array2string(e0, precision=3)}")
print(f"    Block 1: {np.array2string(e1, precision=3)}")
print(f"    Block 2: {np.array2string(e2, precision=3)}")
# 相關性
c01 = np.corrcoef(e0, e1)[0, 1]
c02 = np.corrcoef(e0, e2)[0, 1]
c12 = np.corrcoef(e1, e2)[0, 1]
print(f"    corr: c01={c01:.3f}, c02={c02:.3f}, c12={c12:.3f}")
check("Block 譜相關 (>0.7)", min(c01, c02, c12) > 0.7, 
      f"(c01={c01:.3f}, c02={c02:.3f}, c12={c12:.3f})")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
