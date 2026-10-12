#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""O247 Q2 攻堅 07 — 投影算符層: A₅ = 質數∪平方≤13 嘅 operator 出處 (判據預註冊)

調律者 2026-10-12: 「直接在 o247 要攻投影算符層」。

背景 (O238 已閉合):
- A₅ = {1,2,3,4,5,7,9,11,13} = 質數∪平方≤13; p=1.75e-12 (selection rule)
- scripts/25: A₅ 唔係 |dm|/γ 譜統計極值化 (top-9 規則 overlap 1/9) — 統計生成否證
- scripts/26: A₅ 唯一質量 fit 特權 (RMS 0.546 vs 次佳 1.102, ratio 2.02)
- scripts/28: A₅ 群論撞名否證 (0/173 命吥)
- docs/09 §五 2 剩餘: 「operator 本身 (點由 88-chain 自然選出 A₅ 9 點) 未推導」
- O238 只記上界「13 = F₇ 觀察級」— 未試 13 = 88 質因數和 (2+11)!!

本 script 攻四條未試路線 (全部預註冊):
  C1 ★ 上界 13 出處: 88 = 2³×11 → 相異質因數 {2,11} 和 = 13 EXACT?
     vs F₇ (O238 觀察級) vs 其他候選 (σ(88), φ(88), 8+11=19, 2⁴+11...)
     MC null: 隨機 n∈[50,150] 質因數和做上界 → 「質數∪平方≤上界」9元素/10元素
     隨機命中率 — 證明 13 係 88 特有而唔係普通合成數
  C2 ★ τ(n)≤3 算子: A₅ = {n ≤ 13 : τ(n) ≤ 3} (除數計數 τ)?
     τ(1)=1, τ(p)=2, τ(p²)=3, τ(pq)=4... ⟹ τ≤3 ⟺ {1}∪質數∪質數平方
     = 質數∪平方 嘅第二表達 (唔同集合: 質數平方 {4,9} vs 平方 {1,4,9} — 1 由 τ(1)≤3 入)
     檢定等號 + 呢個表達有冇 operator 意義 (τ 係算術函數 = 數論算子)
  C3 ★ rank-9 projector: P_A₅ = Σ_{n∈A₅}|ψ_n⟩⟨ψ_n| (88×88 譜投影子)
     Tr(P) = 9 = N_gen² ✓; P²=P; P 同 L_88 交換 (譜投影子自然交換 — 平凡?)
     「投影算子 = 譜投影子 support A₅」— 檢定量度 P_A₅ 對 連續層 |dm| 嘅作用:
     |dm|_proj = P_A₅ |dm| → 9 點保留, 79 點歸零 — 與「lazy projection」框架對照
  C4 ★ 9 = N_gen² 計數出處: A₅ 9 點 = 9 基本費米子 = N_gen²;
     「質數∪平方 ≤ 13」係 1..15 內唯一 9-元素自然規則 (O238 scripts/22 已證 7 個 9-元素規則,
     A₅ 唯一質量特權) — 本 script 只做計數: 9 = N_gen² 檢定 + 上界掃描 13~15 集不變性
  C5 整合判決: C1-C4 各自 PASS/FAIL, 然後總結「投影算符層」下一步

數據: O238 正典 S2 freeze v2 質量集 + 88-chain |dm|/γ 譜 (重現 scripts/26 基礎)
"""
import math
import numpy as np

N = 88
A5 = [1, 2, 3, 4, 5, 7, 9, 11, 13]

# ---------- 88-chain 譜 (重現 O238 基礎) ----------
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, N + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
Eee = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
D = Eee[:, None] - Eee[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)
gam = Eee

def is_prime(k):
    if k < 2: return False
    for d in range(2, int(math.sqrt(k)) + 1):
        if k % d == 0: return False
    return True

def is_sq(k):
    r = int(round(math.sqrt(k)))
    return r * r == k

def prime_factors(n):
    fs = []
    d = 2
    m = n
    while d * d <= m:
        if m % d == 0:
            fs.append(d)
            while m % d == 0:
                m //= d
        d += 1
    if m > 1:
        fs.append(m)
    return fs

def tau(n):
    if n == 1: return 1
    ans = 1
    d = 2
    m = n
    while d * d <= m:
        if m % d == 0:
            e = 0
            while m % d == 0:
                m //= d
                e += 1
            ans *= (e + 1)
        d += 1
    if m > 1:
        ans *= 2
    return ans

def psq_rule(ub):
    return sorted([k for k in range(1, ub + 1) if is_prime(k) or is_sq(k)])

print("=" * 78)
print("C1  ★ 上界 13 出處: 88 質因數和 (2+11=13) vs F₇ vs 其他")
print("=" * 78)
pf = prime_factors(88)
print("88 = 2³ × 11; 相異質因數 = %s; 和 = %d" % (pf, sum(pf)))
print("13 = F₇ (O238 觀察級) + 新候選: 質因數和 %d = %d+%d" % (sum(pf), pf[0], pf[1]))
cands = {"sigma(88)": None, "phi(88)": None, "8+11": 19, "2+11 (質因數和)": 13,
         "F₇": 13, "11+3": 14, "sqrt(88)*2": round(2 * math.sqrt(88))}
print("候選上界: %s" % {k: (v if v is not None else "—") for k, v in cands.items()})
# MC null: 隨機 n∈[50,150], 質因數和做上界, 集大小
rng = np.random.default_rng(20261012)
sizes = []
for _ in range(10000):
    n = int(rng.integers(50, 151))
    ub = sum(prime_factors(n))
    sizes.append(len(psq_rule(ub)) if ub >= 1 else 0)
sizes = np.array(sizes)
# 88 嘅集: psq_rule(13) = A₅ (9 元素)
sz88 = len(psq_rule(13))
p9 = float(np.mean(sizes == 9))
p_ge9 = float(np.mean(sizes >= 9))
print("psq_rule(13) = %s (%d 元素)" % (psq_rule(13), sz88))
print("MC null (n∈[50,150] 質因數和上界): 集=9 概率 %.4f; 集≥9 概率 %.4f" % (p9, p_ge9))
print("→ 13 = 質因數和 命中 9 元素 (9 = N_gen²) 嘅概率: %.1f%%" % (p9 * 100))
c1 = sz88 == 9
print("C1 判定: %s (13 質因數和 → 9 元素集; MC 稀有度 %.2f%%)" % ("PASS" if c1 and p9 < 0.05 else "FAIL", p9 * 100))

print()
print("=" * 78)
print("C2  τ(n)≤3 算子: A₅ = {n≤13: τ(n)≤3}? (除數計數函數)")
print("=" * 78)
set_tau = sorted([k for k in range(1, 14) if tau(k) <= 3])
print("τ(n)≤3, n≤13: %s" % set_tau)
print("A₅         : %s" % A5)
c2 = set_tau == A5
print("τ(1..13): %s" % [tau(k) for k in range(1, 14)])
print("τ≤3 ⟺ {1}∪質數∪質數²; 質數²≤13 = {4,9}; 同 質數∪平方 嘅差 = {1} (τ(1)=1≤3)")
print("C2 判定: %s (τ 算子等價表達; 但含 1 = 質數²∪{1}, 唔同 質數∪平方)" % ("PASS" if c2 else "FAIL"))
# 補充: 質數∪平方 同 τ≤3 集合異同
set_psq = psq_rule(13)
not_in = sorted(set(set_tau) ^ set(set_psq))
print("τ≤3 XOR 質數∪平方 (≤13) = %s" % not_in)

print()
print("=" * 78)
print("C3  rank-9 譜投影子 P_A₅: Tr=9=N_gen², P²=P, 對 L_88 交換")
print("=" * 78)
# 88×88 譜投影子: P = Σ_{n∈A₅} |ψ_n⟩⟨ψ_n| — ψ_n = psii[n-1]
PA5 = np.zeros((N, N))
for n in A5:
    v = psii[n - 1]
    PA5 += np.outer(v, v)
tr = np.trace(PA5)
p2 = PA5 @ PA5
ok_idem = np.allclose(p2, PA5, atol=1e-12)
# 同 L_88 交換: L_88 = 88-cycle Laplacian? 用            譜 ψ_n 係 Dirichlet 特徵函數 (sin), 唔係 cycle
# K_chain L cycle 特徵向量 = 平面波, 唔係 sin — 所以用「88-cycle Laplace L_c」會唔交換
Lc = np.zeros((N, N))
for i in range(N):
    Lc[i, i] = 2.0
    Lc[i, (i + 1) % N] = -1.0
    Lc[i, (i - 1) % N] = -1.0
comm = np.linalg.norm(Lc @ PA5 - PA5 @ Lc)
print("Tr(P_A₅) = %.6f (9 = N_gen²: %s)" % (tr, "✓" if abs(tr - 9) < 1e-9 else "✗"))
print("P² = P: %s" % ok_idem)
print("‖[L_88cycle, P_A₅]‖ = %.3e (唔交換 — 因為 sin 基底唔係 cycle 平面波)" % comm)
# 對 |dm| 作用: (I−P)|dm| 殘餘
dm_proj = PA5 @ admn
resid = np.linalg.norm((np.eye(N) - PA5) @ admn) / np.linalg.norm(admn)
print("投影後保留 ‖P|dm|‖/‖|dm|‖ = %.4f; 補空間殘餘 = %.4f" % (
    np.linalg.norm(dm_proj) / np.linalg.norm(admn), resid))
c3 = abs(tr - 9) < 1e-9 and ok_idem
print("C3 判定: %s (rank-9 譜投影子身份成立; lazy projection 對照: P|dm| 保留 9 mode)" % ("PASS" if c3 else "FAIL"))

print()
print("=" * 78)
print("C4  9 = N_gen² 計數出處 + 上界 13~15 集不變性")
print("=" * 78)
print("A₅ 9 點 = 9 基本費米子 = N_gen² = 3² ✓ (O238 已證 7 個 9-元素規則, A₅ 唯一質量特權)")
for ub in (11, 12, 13, 14, 15, 16):
    s = psq_rule(ub)
    same = "=" if s == A5 else ("≠" if len(s) == 9 else "≠(*)")
    print("psq_rule(%2d) = %-28s len=%d %s" % (ub, s, len(s), same))
c4 = (psq_rule(13) == psq_rule(14) == psq_rule(15) == A5) and psq_rule(16) != A5
print("上界 13/14/15 集不變; 16 (4²) 開始變 → 上界範圍 [13,15] 都給 A₅; 13 係「最小自然上界」")
print("C4 判定: %s (13 係質數∪平方 9-元素集嘅最小不變上界; 9 = N_gen²)" % ("PASS" if c4 else "FAIL"))

print()
print("=" * 78)
print("C5  整合判決")
print("=" * 78)
print("C1 (13=質因數和2+11): %s — 新出處候選, MC 稀有度 %.2f%%" % (
    "PASS" if c1 and p9 < 0.05 else "FAIL", p9 * 100))
print("C2 (τ(n)≤3 表達): %s — 等價但含 1 差異, τ 係數論算子" % ("PASS" if c2 else "FAIL"))
print("C3 (rank-9 譜投影子): %s — Tr=9=N_gen², P²=P, 對 cycle 唔交換" % ("PASS" if c3 else "FAIL"))
print("C4 (9=N_gen² + 上界不變): %s — [13,15] 不變, 16 變" % ("PASS" if c4 else "FAIL"))
npass = sum([c1 and p9 < 0.05, c2, c3, c4])
print("==> %d/4 PASS; PROJECTOR-LAYER 開放項: C1-C4 全部通過嘅話, 投影 operator 形式化 = "
      "rank-9 譜投影子 + 數論 selection (13 = 88 質因數和), 下一步 = 盲測預言 79 點歸零" % npass)