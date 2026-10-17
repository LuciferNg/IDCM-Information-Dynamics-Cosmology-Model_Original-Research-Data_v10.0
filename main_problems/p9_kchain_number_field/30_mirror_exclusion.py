#!/usr/bin/env python3
"""
30_mirror_exclusion.py — 對角線排除 + 兩邊鎖 7 (2026-10-17)
============================================================
調律者指示 (2026-10-17): 「4和16要對角線排除後，然後才在兩邊用結構鎖死7」

「對角線」= d ↔ 44−d 鏡像軸 (44-site 對稱軸; γ_n=γ_{88−n} 反粒子鏡像喺 row 層投影)

本輪做兩步:
  STEP 1 (對角線排除): 用 44−d 鏡像嘅「自封閉/出走」結構排除 gcd4/gcd16
  STEP 2 (兩邊鎖死 7): 排除後, 喺 gcd1 (20 候選) 用「鏡像伴侶身份」鎖死 7

預註冊盲測規則 (locked, 唔准事後改):
  R4a 排除規則: 冇 magic 嘅 gcd 類 = 44−d 鏡像下「元素全數出走嘅類」? (gcd4/gcd16 ✓?)
  R4b 代表規則: magic d 嘅鏡像伴侶 44−d 身份有規律 (filler/data/self/排除類)?
  R4c 鎖7規則:   gcd1 內 magic 代表 7 = 唯一「鏡像伴侶唔係 Lucas 鏈 L* 成員」嘅 Lucas 質數候選?

零 import 原推導; 純整數; MC 盲測固定 seed。
"""
import json, random
from math import gcd
from collections import Counter

MAGIC = [7, 14, 20, 22, 33]
DATA  = {11, 13, 17, 19, 21, 25}

def gcl(d):
    return gcd(abs(44 - d), 176)

# 鏡像
def mirror(d):
    return 44 - d

# Lucas 鏈 L* = {m·L_k: m∈{1,2,3}}
L = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29}
LSTAR = sorted({m * Lk for Lk in L.values() for m in (1, 2, 3) if 1 <= m * Lk <= 43})

res = {"step": "30_mirror_exclusion", "rules": {"R4a": "排除=鏡像出走類", "R4b": "代表=鏡像伴侶身份", "R4c": "鎖7=鏡像伴侶非L*"}}

# ---------- 基礎: 7 類 ----------
classes = {}
for d in range(1, 44):
    classes.setdefault(gcl(d), []).append(d)

# ---------- STEP 1: 44−d 鏡像下類別流向 ----------
flow = {}
for g in sorted(classes):
    targets = Counter(gcl(mirror(d)) for d in classes[g])
    flow[str(g)] = {f"gcd{t}": n for t, n in sorted(targets.items())}
    self_closed = (len(targets) == 1 and list(targets)[0] == g)
    # 全出走 = 所有元素鏡像後 gcd 類唔等於原類
    all_exit = all(gcl(mirror(d)) != g for d in classes[g])
    flow[str(g)]["self_closed"] = self_closed
    flow[str(g)]["all_exit"] = all_exit

res["STEP1_mirror_flow"] = flow

# R4a 檢驗: 冇 magic 類 = all_exit?
no_magic_g = [g for g in sorted(classes) if not any(d in MAGIC for d in classes[g])]
all_exit_g = [g for g in sorted(classes) if flow[str(g)]["all_exit"]]
has_magic_all_exit = [g for g in sorted(classes) if flow[str(g)]["all_exit"] and any(d in MAGIC for d in classes[g])]
res["R4a_check"] = {
    "no_magic_classes": no_magic_g,          # expect [4, 16]
    "all_exit_classes": all_exit_g,
    "all_exit_but_magic": has_magic_all_exit,  # gcd8 出走但有 magic — 反例
    "verdict": "PARTIAL — gcd4/gcd16 出走 ✓ 但 gcd8 都出走而有 magic ⟹ 出走唔係排除嘅充要條件"
}

# ---------- STEP 2a: magic 鏡像伴侶身份 ----------
partner = {d: mirror(d) for d in MAGIC}
def role(x):
    if x in MAGIC: return "magic"
    if x in DATA:  return "data"
    return "filler"
partner_roles = {f"d{d}": {"mirror": mirror(d), "mirror_gcd": gcl(mirror(d)),
                           "mirror_role": role(mirror(d)), "own_role": role(d)} for d in MAGIC}
res["STEP2_magic_partner"] = partner_roles

# R4b 檢驗: magic ↔ 伴侶性質
p_roles = [partner_roles[f"d{d}"]["mirror_role"] for d in MAGIC]
res["R4b_check"] = {
    "mirror_roles_of_magic": p_roles,   # 7→filler, 14→filler, 20→gcd4(排除類!), 22→self, 33→data(11!)
    "note": "每個 magic 嘅鏡像伴侶: 7↔37(filler), 14↔30(filler), 20↔24(gcd4 被排除類!), 22↔22(軸心), 33↔11(data 行!) —— 冇一條共同 pattern"
}

# ---------- STEP 2b: 鎖 7 — gcd1 內 Lucas 質數候選 {3,7,29} 嘅鏡像伴侶 ----------
g1 = classes[1]
cands = [d for d in g1 if d in (3, 7, 29)]
cand_info = []
for d in cands:
    m = mirror(d)
    cand_info.append({
        "d": d, "is_Lucas": d in {2, 3, 7, 11, 29}, "L_index_unique": d != 3 or True,
        "mirror": m, "mirror_in_LSTAR": m in LSTAR,
        "mirror_in_data": m in DATA, "mirror_in_magic": m in MAGIC,
    })
res["STEP2b_lock7"] = {
    "gcd1_lucas_primes": cands,   # [3, 7, 29]
    "detail": cand_info,
    "pattern": {
        "3":  "mirror 41: 非L* 非data 非magic",
        "7":  "mirror 37: 非L* 非data 非magic ← 同 3 一樣, 冇分別!",
        "29": "mirror 15: 非L* 非data 非magic",
    },
    "verdict": "R4c FAIL 候選 — 3/7/29 嘅鏡像伴侶全部都係 filler (唔係 L*/data/magic), 鏡像伴侶身份分唔開 7 同 3 ⟹ 鎖 7 唔可以靠『兩邊』鏡像身份"
}

# ---------- 盲測: 鏡像伴侶角色分佈有冇統計訊號 ----------
# 若每 gcd1 元素嘅「鏡像伴侶角色」係隨機, 7 嘅伴侶 37 係 filler 嘅概率?
random.seed(20261017)
N = 10**6
g1_filler_mirror = 0
for _ in range(N):
    d = random.choice(g1)
    m = mirror(d)
    if role(m) == "filler":
        g1_filler_mirror += 1
p_filler = g1_filler_mirror / N
res["blind_mirror_g1"] = {
    "P(隨機 gcd1 元素嘅鏡像伴侶係 filler)": round(p_filler, 5),
    "7 嘅伴侶 37": "filler",
    "verdict": "7 嘅伴侶係 filler 概率" + (f"{p_filler:.3f} — 唔特別" if p_filler > 0.1 else f"{p_filler:.3f} — 有訊號")
}

# ========== 總結 ==========
summary = []
summary.append("STEP1 (排除 4/16): gcd4/gcd16 喺 44−d 鏡像下全出走 ✓ — 但 gcd8 都出走而有 magic ⟹ 出走唔足以解釋排除")
summary.append("STEP2 (鎖 7): 3/7/29 嘅鏡像伴侶全部 filler, 鏡像身份分唔開 7 vs 3 ⟹ 「兩邊鎖7」用鏡像伴侶角色做唔到")
summary.append("★ 真正嘅鏡像結構: d=22 係唯一自鏡像 (對稱軸自己 = HALF magic); gcd2 嘅 14↔30 兩邊 filler; gcd11 嘅 33↔11 = magic↔data 唯一跨層對")
summary.append("★ 20↔24: magic 20 嘅鏡像落入被排除類 gcd4 — 「magic 鏡像落入缺類」可能先係 20 嘅特殊身份")

res["summary"] = summary

with open("data/30_mirror_exclusion.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)

print("=== STEP1: 44−d 鏡像類別流向 ===")
for g in sorted(classes):
    f = flow[str(g)]
    fl = " | ".join(f"{k}:{v}" for k, v in f.items() if k not in ("self_closed", "all_exit"))
    print(f"gcd={g:2d} {classes[g]}  → {fl}  self={f['self_closed']!s:5s} all_exit={f['all_exit']!s:5s}")
print()
print("冇 magic 類 =", no_magic_g, "| 全出走類 =", all_exit_g, "| 出走但有 magic =", has_magic_all_exit)
print()
print("=== STEP2b: gcd1 Lucas 質數候選鏡像配對 ===")
for c in cand_info:
    print(f"  {c['d']:2d} ↔ {c['mirror']:2d}  mirror L*? {c['mirror_in_LSTAR']}  data? {c['mirror_in_data']}  magic? {c['mirror_in_magic']}")
print()
print("=== 盲測: gcd1 隨機元素鏡像伴侶係 filler 概率 ===")
print(f"  P = {p_filler:.5f}")
print()
print("=== 總結 ===")
for s in summary:
    print(" ", s)
print()
print("輸出: data/30_mirror_exclusion.json")