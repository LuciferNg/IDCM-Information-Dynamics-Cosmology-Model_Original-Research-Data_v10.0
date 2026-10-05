#!/usr/bin/env python3
"""
盲測批量 v1: 8 條隨機拍頻嘅 COMMAND/WORKFLOW 功能鑑定
=====================================================
框架: 946 拍頻 = 946 條微碼指令
- d = j−i = 差頻 = opcode 行
- s = j+i = 和頻 = workflow 列
- 每條指令: (d,s) 座標 → command 語義 + workflow 位置
"""
import random, json, math
from math import pi, sin

Nd = 44
w = lambda n: 2*sin(pi*n/88)
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47, 9:76, 10:123}
L_inv = {v:k for k,v in L.items()}
F = [0,1,1,2,3,5,8,13,21,34,55,89]

# magic rows (d 值) — 已指派 opcode 行
magic_rows = {
    7: "m7 anchor (DM 13.8 MeV)",
    14: "GEN d=14 (世代規則 Δn=B²−2)",
    20: "T(s->d) (轉移矩陣 2n_u)",
    22: "half-node (44/2)",
    33: "K_tree (33)",
}
# 已知物理參數 label (from master_atlas)
phys_labels = {
    (10,24): "u/d Quark (O34)", (8,22): "c/s Quark (O34)", (19,33): "t/b Quark (O34)",
    (8,33): "m_c/m_b (O34)", (1,22): "m_s/m_d (O35)", (30,41): "m_W/m_Z (O34)",
    (19,38): "m_H/m_W (O34)", (1,18): "m_mu/m_tau (O34)", (7,20): "n/p BBN (O13)",
}

def lucas_comp(n):
    """將 n 分解為 Lucas 數組合 (greedy)"""
    comp = []
    rem = n
    for idx in sorted(L.keys(), reverse=True):
        while rem >= L[idx] and L[idx] > 0:
            comp.append(L[idx])
            rem -= L[idx]
    return comp, rem

def classify(i, j):
    d = j - i
    s = j + i
    beat = abs(w(j) - w(i))
    info = {"pair": (i,j), "d": d, "s": s, "beat": round(beat, 8),
            "s-d": s-d, "s+d": s+d}
    # 1. d 行語義
    if d in magic_rows:
        info["d_role"] = f"🧙 magic: {magic_rows[d]}"
    elif d in L_inv:
        info["d_role"] = f"Lucas L{L_inv[d]} (={d})"
    else:
        fib_hit = [f for f in F if f == d]
        info["d_role"] = f"plain d={d}"
    # 2. s 列語義
    if s in L_inv:
        info["s_role"] = f"Lucas L{L_inv[s]} (={s})"
    elif s == 33:
        info["s_role"] = "M-pipeline (33)"
    elif s == 44:
        info["s_role"] = "N_d causal domain (44)"
    else:
        info["s_role"] = f"plain s={s}"
    # 3. 物理 label?
    key = (min(i,j), max(i,j))
    info["phys_label"] = phys_labels.get(key, None)
    # 4. i, j 嘅 Lucas 解讀
    info["i_comp"] = lucas_comp(i)
    info["j_comp"] = lucas_comp(j)
    # 5. degree (master atlas 方法)
    def phi(n):
        r = n; p = 2
        while p*p <= n:
            if n % p == 0:
                while n % p == 0: n //= p
                r -= r // p
            p += 1
        if n > 1: r -= r // n
        return r
    def sin_deg(k):
        k = abs(k) % 176
        if k == 88: return 1
        m = (88 - k) % 176
        g = math.gcd(352, m)
        return phi(352 // g) // 2
    def beat_degree(d, s):
        k1 = abs(d+s) % 352; k2 = abs(d-s) % 352
        return math.lcm(sin_deg(k1), sin_deg(k2))
    info["deg_diff"] = beat_degree(abs(d), s)
    info["deg_sum"] = beat_degree(s, abs(d))
    # 6. workflow 語義
    wf = []
    if s == 33: wf.append("M-pipeline")
    if s == 44: wf.append("N_d-domain")
    if d == 7: wf.append("m7-anchor")
    if d == 14: wf.append("GEN")
    if d == 22: wf.append("half-node")
    if d == 33: wf.append("K_tree")
    if d == 29: wf.append("V_EW(L₇)")
    if d == 20: wf.append("T(s->d)")
    info["workflow"] = wf if wf else ["一般填充"]
    # 7. SYNC 家族? (i=2 即 s−d=4=B)
    if i == 2: info["sync_family"] = True
    elif j == 2: info["sync_family"] = True
    else: info["sync_family"] = False
    return info

# ===== 抽籤 (seed 固定, 唔同上次) =====
random.seed(20260825)  # 同一日但用唔同 sampling: 抽 8 條
pairs = [(i,j) for i in range(1,Nd) for j in range(i+1,Nd+1)]
drawn = random.sample(pairs, 8)
# 確保同上次 (2,31) 唔重複
drawn = [p for p in drawn if p != (2,31)][:8]

results = [classify(i,j) for i,j in drawn]
print(json.dumps(results, indent=1, ensure_ascii=False))
