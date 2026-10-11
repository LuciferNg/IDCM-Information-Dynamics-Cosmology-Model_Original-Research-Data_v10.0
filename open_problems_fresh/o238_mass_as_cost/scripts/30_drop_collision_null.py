#!/usr/bin/python3
"""O238 — Script 30: 剔除集重合 MC null — 「偶合成數 {6,8,10,12} 啱好係 log|dm| 低離散區」係巧合定結構?

docs/10 P4 觀察: 剔除集 {6,8,10,12} 係 log|dm| 集中區 (mean 5.94, std 0.56),
A₅ 選嘅係大離散 mode (std 1.26–1.58). 但呢個「數論剔除集 ↔ 譜結構集中區」重合
從來冇做 MC null — 呢個係 O238 最後一個未推盡位 (調律者: 「是否已推盡」).

設計 (盲測):
  P1 剔除集 4 點 {6,8,10,12} 嘅 log|dm| std = 0.56 — 喺「隨機 4 點(88 選 4, 無放回) log|dm| std」分佈嘅 percentile?
  P2 A₅ 9 點 log|dm| std (1.26–1.58 區間) vs 隨機 9 點 std 分佈 — A₅ 係咪異常「散」?
  P3 (額外) 「4 個偶合成數」同「最低離散 4 {11,33,55,77} (scripts/25 P6)」嘅重合度 — 唔係同一組?
  P4 判準: 剔除集 std percentile <0.05 (顯著集中) 或 >0.95 (顯著散) = 有結構; 否則巧合坐實

來源: docs/10 §一 P4 (scripts/18 output), docs/14 §一 (LO4)
"""
import numpy as np, math, json, random

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
logd = np.log(admn)  # 88 個 mode 嘅 log|dm|

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
DROP = [6, 8, 10, 12]  # 剔除集 = 偶合成數
names_sel = {1:'t',2:'b',3:'τ',4:'c',5:'μ',7:'s',9:'d',11:'u',13:'e'}

def std_of(idx):
    return float(np.std(logd[np.array(idx) - 1], ddof=1)) if len(idx) > 1 else 0.0

# P1
std_drop = std_of(DROP)
print(f"═══ P1. 剔除集 log|dm| std ═══")
print(f"  剔除集 {DROP} (偶合成數): log|dm| std = {std_drop:.4f}")
print(f"  (docs/10 記錄 0.56 — 對照: mean {np.mean(logd[np.array(DROP)-1]):.2f})")

random.seed(20261012)
n_mc = 200000
L = logd
# 隨機 4 點 std 分佈
stds4 = np.empty(n_mc)
for i in range(n_mc):
    idx = random.sample(range(N), 4)
    stds4[i] = np.std(L[idx], ddof=1)
pct_drop = np.mean(stds4 <= std_drop)
print(f"  隨機 4 點 std (N={n_mc}, ddof=1): median={np.median(stds4):.4f}, 5%={np.percentile(stds4,5):.4f}, 95%={np.percentile(stds4,95):.4f}")
print(f"  剔除集 std {std_drop:.4f} → percentile {pct_drop*100:.2f}%")
print(f"  ⟹ {'🔴 顯著集中 (<5%) — 數論剔除集啱好切中譜結構集中區' if pct_drop < 0.05 else '🟢 巧合 — 喺隨機範圍內, 唔係結構'}")

# P2
std_a5 = std_of(SEL9)
stds9 = np.empty(n_mc)
for i in range(n_mc):
    idx = random.sample(range(N), 9)
    stds9[i] = np.std(L[idx], ddof=1)
pct_a5 = np.mean(stds9 >= std_a5)
print(f"\n═══ P2. A₅ 9 點 log|dm| std ═══")
print(f"  A₅ {SEL9}: std = {std_a5:.4f}")
print(f"  隨機 9 點 std: median={np.median(stds9):.4f}, 95%={np.percentile(stds9,95):.4f}")
print(f"  A₅ std → percentile (≥) {pct_a5*100:.2f}%")
print(f"  ⟹ {'🔴 顯著散 — A₅ 選大離散 mode 有結構' if pct_a5 > 0.95 else '🟢 巧合'}")

# P3: 最低離散 4 係咪 {11,33,55,77}? 同剔除集重合?
stds = []
for k in range(1, N+1):
    # 每個 mode 附近離散度: |log|dm|_k − median| (scripts/25 用過嘅定義)
    pass
# scripts/25 P6 定義: 最低離散 4 mode = {11,33,55,77} (離散 0.008 vs 偶 6.36)
# 重新算: 離散度 = mode 附近 log|dm| 嘅局部集中? 用簡單定義: |logd − median(logd)|
med = np.median(logd)
disp = np.abs(logd - med)
order = np.argsort(disp)
low4 = sorted((order[:4] + 1).tolist())
print(f"\n═══ P3. 最低離散 4 mode ═══")
print(f"  最低離散 4 (|logd−median|): {low4}")
print(f"  vs scripts/25 P6 記錄 {[11,33,55,77]}")
print(f"  同剔除集 {DROP} 重合: {sorted(set(low4) & set(DROP))}")
print(f"  重合度: {len(set(low4) & set(DROP))}/4")
# 剔除集 4 點喺低離散區比例 vs 隨機
drop_disp = disp[np.array(DROP)-1]
print(f"  剔除集離散: {[round(float(x),2) for x in drop_disp]}")
print(f"  剔除集離散 vs 全部 median {np.median(disp):.2f}: 有 {sum(drop_disp < np.median(disp))}/4 喺下半")

out = {
    "P1_drop_std": std_drop, "P1_drop_pct": float(pct_drop),
    "P2_a5_std": float(std_a5), "P2_a5_pct": float(pct_a5),
    "P3_low4": low4, "P3_drop_overlap": sorted(set(low4) & set(DROP)),
    "n_mc": n_mc,
}
with open("data/30_drop_collision_null.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: P1 {'結構' if pct_drop < 0.05 else '巧合'} / P2 {'結構' if pct_a5 > 0.95 else '巧合'} / P3 overlap {len(set(low4) & set(DROP))}/4")