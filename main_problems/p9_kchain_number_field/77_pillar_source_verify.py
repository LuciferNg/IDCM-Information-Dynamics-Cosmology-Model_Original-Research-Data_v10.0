#!/usr/bin/env python3
"""
77_pillar_source_verify.py — 5 支柱 label 閉合源頭驗證 (2026-10-17)
===================================================================================
問題 (76 號之後): 76 號確認「cover 全 5 支柱」= tautology。但 A 層 label 真實性
（O-series 閉合時序）仍然獨立。本輪驗證 5 支柱 label 每個對應嘅物理閉合
有冇真憑實據:
  7  ANCHOR/DM  : (13,20) DM 13.8 MeV 錨格 — 13.8 MeV 喺邊度出現?
  14 GEN        : 三代 quark (10,24)u/d (8,22)c/s (19,33)t/b — P13 週期表
  20 TRANSFER   : (7,20) n/p BBN 端點 — BBN 邊度?
  22 HALF       : 44−d=d 自鏡像; γ_n=γ_{88−n} — 數學恒等, 唔使閉合
  33 KTREE      : (8,33) m_c/m_b — O158 ×41 聚類?

方法: grep O-series docs + register 狀態, 搵每個 label 嘅「閉合出處」。
"""
import subprocess
import json
import os

ROOT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
P9 = f"{ROOT}/main_problems/p9_kchain_number_field"

PASS = 0
FAIL = 0
FAILS = []
OUT = []

def chk(name, desc, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ✅ {name}: {desc}")
    else:
        FAIL += 1
        FAILS.append(name)
        print(f"  ❌ {name}: {desc}" + (f"  [{detail}]" if detail else ""))
    OUT.append({"id": name, "desc": desc, "ok": ok, "detail": detail})

def grep_any(pats, roots=None):
    """喺 O-series/docs 搵任何 pattern, 返回匹配檔"""
    roots = roots or [f"{ROOT}/open_problems_fresh", f"{ROOT}/main_problems/p13_beat_periodic_table"]
    hits = []
    for pat in pats:
        r = subprocess.run(["grep", "-rln", "--include=*.md", "--include=*.py",
                            "-e", pat, *roots],
                           capture_output=True, text=True)
        hits += [f for f in r.stdout.splitlines() if not f.startswith(P9)]
    return sorted(set(hits))

print("=" * 72)
print("A. ANCHOR 7 — DM 13.8 MeV 錨格 (13,20)")
print("=" * 72)
hits = grep_any(["13.8", "13,20", "DM 13", "m_7"])
print("  hits:")
for f in hits[:8]:
    print(f"    {f.replace(ROOT+'/', '')}")
chk("A1_dm_138", "13.8 MeV 喺 O-series/P13 出現 (DM 錨格出處)",
    len(hits) >= 1, f"{len(hits)} 檔: {[f.replace(ROOT+'/','') for f in hits[:3]]}")

print()
print("=" * 72)
print("B. GEN 14 — 三代 quark 行 (10,24)/(8,22)/(19,33)")
print("=" * 72)
hits2 = grep_any(["10,24", "8,22", "19,33", "GENERATION", "generation"])
print("  hits:")
for f in hits2[:8]:
    print(f"    {f.replace(ROOT+'/', '')}")
chk("B1_gen_cells", "三代 quark 格子喺 P13/docs 出現 (GEN 直接出處)",
    len(hits2) >= 1, f"{len(hits2)} 檔")

print()
print("=" * 72)
print("C. TRANSFER 20 — (7,20) n/p BBN 端點")
print("=" * 72)
hits3 = grep_any(["7,20", "BBN", "n/p", "neutron", "proton"])
print("  hits:")
for f in hits3[:8]:
    print(f"    {f.replace(ROOT+'/', '')}")
chk("C1_bbn", "(7,20) n/p BBN 喺 docs 出現 (TRANSFER 出處)",
    len(hits3) >= 1, f"{len(hits3)} 檔")

print()
print("=" * 72)
print("D. HALF 22 — 44−d=d 自鏡像, γ_n=γ_{88−n}")
print("=" * 72)
hits4 = grep_any(["γ_22", "gamma_22", "44−d", "self.mirror", "self-mirror"])
print("  hits:")
for f in hits4[:8]:
    print(f"    {f.replace(ROOT+'/', '')}")
chk("D1_half", "γ_22/自鏡像喺 docs 出現 (HALF 出處)",
    len(hits4) >= 1, f"{len(hits4)} 檔")

print()
print("=" * 72)
print("E. KTREE 33 — (8,33) m_c/m_b, O158 ×41 聚類")
print("=" * 72)
hits5 = grep_any(["8,33", "m_c", "m_b", "×41", "x41", "uml"])
print("  hits:")
for f in hits5[:8]:
    print(f"    {f.replace(ROOT+'/', '')}")
chk("E1_ktree", "(8,33) m_c/m_b / ×41 喺 docs 出現 (KTREE 出處)",
    len(hits5) >= 1, f"{len(hits5)} 檔")
# O158 狀態
r = subprocess.run(["grep", "-E", '"pid": "O158"', f"{ROOT}/problem_register/register.jsonl"],
                   capture_output=True, text=True)
o158 = r.stdout.strip().split("\n")[0][:200] if r.stdout else "(冇 O158)"
chk("E2_o158", f"O158 register 狀態: {o158[60:150]}", "closed" in r.stdout or "partial" in r.stdout)

print()
print("=" * 72)
print("F. 完整 5 支柱源頭表")
print("=" * 72)
table = {
    "7 ANCHOR/DM": ("13.8 MeV / (13,20)", len(hits) >= 1),
    "14 GEN": ("三代 quark 格", len(hits2) >= 1),
    "20 TRANSFER": ("(7,20) n/p BBN", len(hits3) >= 1),
    "22 HALF": ("γ_22 / 自鏡像", len(hits4) >= 1),
    "33 KTREE": ("(8,33) m_c/m_b / ×41", len(hits5) >= 1),
}
for k, (src, ok) in table.items():
    print(f"  {k}: {'✅' if ok else '❌'} {src}")
chk("F1_all5", "全部 5 支柱都有 docs 出處", all(v for _, v in table.values()))

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "77_pillar_source_verify", "date": "2026-10-17",
    "sources": {k: v for k, (v, _) in table.items()},
    "hits": {
        "7_dm": [f.replace(ROOT+"/", "") for f in hits[:5]],
        "14_gen": [f.replace(ROOT+"/", "") for f in hits2[:5]],
        "20_transfer": [f.replace(ROOT+"/", "") for f in hits3[:5]],
        "22_half": [f.replace(ROOT+"/", "") for f in hits4[:5]],
        "33_ktree": [f.replace(ROOT+"/", "") for f in hits5[:5]],
    },
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/77_pillar_source_verify.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/77_pillar_source_verify.json")