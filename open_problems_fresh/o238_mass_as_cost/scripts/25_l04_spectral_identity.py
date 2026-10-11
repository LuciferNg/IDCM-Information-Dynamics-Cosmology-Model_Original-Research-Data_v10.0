#!/usr/bin/python3
"""O238 — Script 25: LO4 剔除集譜身份 — 投影 operator = 譜離散度極值化?

O234/O144/O206/O209 回覆後按回覆繼續推。LO4 要推嘅係「點解 88-chain 譜論
會自然選出 A₅ = 質數∪平方 ≤13」。候選機制: A₅ = 譜平面 (log|dm|, logγ) 高離散
mode 集合 — 剔除集 {6,8,10,12} = log|dm| 集中區 (std 0.56 vs A₅ 1.26–1.58,
scripts/18 已見). 本 script 推導:

  P1 離散度統計: |dm| 譜離散度 top-9 mode 集 vs A₅ — 有幾多 overlap?
      (離散度 = |log|dm|_n − median| 或 local spacing)
  P2 剔除集身份: {6,8,10,12} = 偶合成數 = log|dm| 集中區 — 係咪剛好係
      '低離散' 前 4? 定係數論規則先於統計?
  P3 譜論生成規則: 有冇一個『純譜統計』規則 (零數論輸入) 自然生成 A₅?
      候選: top-9 |z-score(log|dm|)|; top-9 |log|dm| − 線性預期|;
            每象限 2+ 點; γ 間距 > threshold 等
  P4 互檢: 譜統計規則 vs 數論規則 喺『質量 fit 層』比較 (RMS) —
      如果譜規則同 A₅ 一樣, LO4 閉合 = 投影 operator 係離散度極值化 (數論係統計嘅實現)
"""
import numpy as np, math, json

N = 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, N + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
D = E[:, None] - E[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)
gam = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
lnD = np.log(admn)
lnG = np.log(gam)

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MS2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
       "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
       "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}
logm = np.array([math.log(MS2[p]) for p in names9])
logd9 = np.log([admn[n-1] for n in SEL9])

def rms_of(sel, logm_=logm, logd_=logd9, phi2=PHI2):
    C_ = math.exp(np.mean(logm_ - phi2*logd_))
    r_ = logm_ - (math.log(C_) + phi2*logd_)
    return math.sqrt(np.mean(r_**2))

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

print("═══ P1. 離散度統計 ═══")
# 離散度度量 1: |lnD − median| (絕對離中)
med = np.median(lnD)
disp = np.abs(lnD - med)
top9_disp = np.argsort(disp)[::-1][:9] + 1
print(f"  top-9 |lnD−median| mode: {sorted(top9_disp.tolist())}")
print(f"  overlap vs A₅: {len(set(top9_disp) & set(SEL9))}/9")
chk("P1 top9-|lnD−med| overlap ≥ 5/9", len(set(top9_disp) & set(SEL9)) >= 5,
    f"overlap={len(set(top9_disp) & set(SEL9))}")

# 離散度度量 2: 局部 spacing (|lnD_n − lnD_{n±1}| 平均)
spacing = np.abs(np.diff(lnD))
# 每點嘅最近鄰 spacing (循環)
lsp = np.zeros(N)
for i in range(N):
    lsp[i] = min(abs(lnD[i]-lnD[(i-1) % N]), abs(lnD[i]-lnD[(i+1) % N]))
top9_lsp = np.argsort(lsp)[::-1][:9] + 1
print(f"  top-9 最近鄰spacing mode: {sorted(top9_lsp.tolist())}")
print(f"  overlap vs A₅: {len(set(top9_lsp) & set(SEL9))}/9")
chk("P1b top9-spacing overlap ≥ 5/9", len(set(top9_lsp) & set(SEL9)) >= 5,
    f"overlap={len(set(top9_lsp) & set(SEL9))}")

print("\n═══ P2. 剔除集身份 ═══")
drop = [6, 8, 10, 12]
print(f"  剔除集 {drop}: lnD std = {lnD[[d-1 for d in drop]].std():.3f} (mean {lnD[[d-1 for d in drop]].mean():.2f})")
print(f"  A₅  集      : lnD std = {lnD[[d-1 for d in SEL9]].std():.3f} (mean {lnD[[d-1 for d in SEL9]].mean():.2f})")
print(f"  全譜        : lnD std = {lnD.std():.3f} (mean {lnD.mean():.2f})")
# 集中區定義: 最低离散 4 mode?
low4 = np.argsort(disp)[:4] + 1
print(f"  最低離散 4 mode: {sorted(low4.tolist())} vs 剔除集 {sorted(drop)}")
chk("P2 剔除集 = 低離散區 (top4 low-disp 包含 ≥2 個剔除)", len(set(low4) & set(drop)) >= 2,
    f"overlap={len(set(low4) & set(drop))}")
# 但注意底 4 唔一定等於剔除集 — 統計 vs 數論
chk("P2b 剔除集 = 剛好最低離散 4?", sorted(low4) == sorted(drop),
    f"{sorted(low4)} != {sorted(drop)}")

print("\n═══ P3. 譜論生成規則 (零數論輸入) ═══")
# 候選譜規則 — 全部純譜統計
cands = {}
# R1: top-9 |lnD − med| (絕對離中)
cands["top9-|lnD−med|"] = sorted(set(top9_disp.tolist()))[:9] if len(set(top9_disp)) >= 9 else sorted(set(top9_disp.tolist()))
# R2: top-9 spacing
cands["top9-spacing"] = sorted(set(top9_lsp.tolist()))
# R3: 極端值 (top 5 大 + top 4 細)
hi5 = np.argsort(lnD)[::-1][:5] + 1
lo4 = np.argsort(lnD)[:4] + 1
cands["extreme(5hi+4lo)"] = sorted(set(hi5.tolist() + lo4.tolist()))
# R4: 殘差 |lnD − OLS(lnD~n)|
A = np.vstack([np.ones(N), np.arange(1, N+1)]).T
c_ols, *_ = np.linalg.lstsq(A, lnD, rcond=None)
resid = lnD - A @ c_ols
top9_res = np.argsort(np.abs(resid))[::-1][:9] + 1
cands["top9-|OLSresid|"] = sorted(set(top9_res.tolist()))
# R5: |lnD| 最大 9 (原生 |dm| 大)
cands["top9-|dm|"] = sorted(set((np.argsort(admn)[::-1][:9] + 1).tolist()))
# R6: γ 極端 (大 γ 9)
cands["top9-γ"] = sorted(set((np.argsort(gam)[::-1][:9] + 1).tolist()))

print(f"{'規則':20s} {'mode集':32s} {'overlap':>8s} {'RMS':>8s}")
for nm, mods in cands.items():
    ov = len(set(mods) & set(SEL9))
    rms = rms_of(sorted(mods)) if len(mods) == 9 else float('nan')
    print(f"{nm:20s} {str(sorted(mods)):32s} {ov:8d} {rms:8.3f}")

# A₅ 自身對照 — 用 int 9 唔係 str
print(f"  {'A₅ (真)':20s} {str(SEL9):32s} {9:>8d} {rms_of(SEL9):8.3f}")

print("\n═══ P5. γ 方向: A₅ 喺 γ 譜嘅身份 ═══")
# γ 間距: A₅ 內相鄰 mode 嘅 γ spacing 有冇特別?
g_sel = gam[[n-1 for n in SEL9]]
g_all = gam
print(f"  γ(SEL9) = {np.array2string(g_sel, precision=4)}")
# 剔除集 γ 身份
print(f"  γ(剔除集 {drop}) = {np.array2string(gam[[d-1 for d in drop]], precision=4)}")
# γ spacing 比例
sp_sel = np.diff(np.sort(SEL9))
print(f"  A₅ n-間距: {sp_sel.tolist()}")
# γ_n 鏡像 γ_{88-n}: A₅ 有冇鏡像對?
mir = {88-n: n for n in SEL9 if 88-n != n}
print(f"  鏡像對喺 A₅ 內: {[(n, 88-n) for n in SEL9 if 88-n in SEL9 and 88-n != n]}")
# mod-8 / mod-11 分佈
print(f"  A₅ mod 8: {sorted(n % 8 for n in SEL9)}")
print(f"  A₅ mod 11: {sorted(n % 11 for n in SEL9)}")

print("\n═══ P6. 11-子格 (O246 呼應) ═══")
sub11 = [11, 22, 33, 44, 55, 66, 77, 88]
low4 = np.argsort(disp)[:4] + 1
print(f"  11-子格 {sub11} 離散度排位: {[(n, round(float(disp[n-1]),3)) for n in sub11]}")
print(f"  最低離散 4 = {sorted(low4.tolist())} — 全部 = 11×奇數: {all(n % 11 == 0 and (n//11) % 2 == 1 for n in low4)}")
# 子格 11×奇 對 11×偶: 離散度對比
odd11 = [11*k for k in (1,3,5,7)]
even11 = [11*k for k in (2,4,6,8)]
chk("P6 11×奇數 = 低離散 (mean 低過 11×偶)", disp[[n-1 for n in odd11]].mean() < disp[[n-1 for n in even11]].mean(),
    f"odd11 disp={disp[[n-1 for n in odd11]].mean():.3f} even11 disp={disp[[n-1 for n in even11]].mean():.3f}")

print("\n═══ P7. 剔除集精確身份 (數論 vs 統計最後對決) ═══")
def is_prime(k):
    if k < 2: return False
    for d in range(2, int(math.sqrt(k)) + 1):
        if k % d == 0: return False
    return True
def is_sq(k):
    r = int(round(math.sqrt(k)))
    return r * r == k
# 剔除 = {6,8,10,12}: 偶合成數 (2 嘅倍數但不是質數又不是平方)
evens13 = [n for n in range(1, 14) if n % 2 == 0]
nonprime_nonsq = [n for n in evens13 if not is_prime(n) and not is_sq(n)]
print(f"  [1,13] 偶數: {evens13} → 非質非平方: {nonprime_nonsq} vs 剔除集 {drop}")
chk("P7 剔除集 = 偶合成數 (非質非平方)", nonprime_nonsq == drop, str(nonprime_nonsq))
# 奇數合成 (9=平方 已經入; 15>13): 冇其他
odds9 = [n for n in range(1, 14) if n % 2 == 1 and not is_prime(n)]
print(f"  [1,13] 奇合成: {odds9} (9=平方已入 A₅)")
# 統計對照: 剔除集離散度 rank
disp_rank = np.argsort(np.argsort(disp)) + 1
print(f"  剔除集離散度 rank (1=最低): {[(d, int(disp_rank[d-1])) for d in drop]}")

print("\n═══ P4. 數論 vs 統計 互檢 ═══")
# 數論規則唯一性: 譜統計規則 overlap 有冇超過 A₅?
best_ov = max(len(set(cands[k]) & set(SEL9)) for k in cands)
chk("P4 A₅ 數論規則「唯一」vs 統計規則 (overlap ≤7 即冇統計規則全中)",
    best_ov <= 7, f"best_ov={best_ov}")
# 共線性: A₅ 嘅 9 點喺 (lnD, lnG) 共線 0.992; 統計規則如何?
print("  統計規則共線性 (SEL9 對照 R²=0.992):")
for nm, mods in cands.items():
    if len(mods) != 9:
        continue
    ids = [m-1 for m in sorted(mods)]
    cc = np.corrcoef(lnD[ids], lnG[ids])[0, 1]
    print(f"    {nm:20s} R²={cc**2:.4f}")

out = {
    "top9_disp_overlap": int(len(set(top9_disp) & set(SEL9))),
    "top9_lsp_overlap": int(len(set(top9_lsp) & set(SEL9))),
    "low4": [int(x) for x in low4], "drop": [int(x) for x in drop],
    "cand_overlaps": {k: int(len(set(v) & set(SEL9))) for k, v in cands.items()},
    "SEL9_rms": float(rms_of(SEL9)),
}
with open("data/25_l04_spectral_identity.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")