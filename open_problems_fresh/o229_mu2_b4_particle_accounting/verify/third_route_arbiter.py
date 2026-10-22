#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O229 / R5 第三路線仲裁（verify/；唔計入 scripts 01–25 名單）
目的: 以**獨立於 24 與 25 之演算法**重算 34 原子之 lock(v) 表，並與 scripts/24 逐項比對。
路線: (a) 多項式形式 → sympy `real_roots`（精確、完備）；(b) 含 2^B 形式 → sympy 精確代入掃描 [1,B0]，
      B0 由支配論證給出（見下），非任意上限。
項集: 直接 exec `scripts/24_r5_discrimination.py` 之前段取得同一凍結類 𝒞（不重寫類定義，避免走樣）。
"""
import json, os, sympy as sp
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(BASE, "scripts", "24_r5_discrimination.py")
src  = open(SRC, encoding="utf-8").read()
G    = {"__file__": SRC, "__name__": "arbiter"}
exec(src.split("nz=sum(1 for v in ATOMS")[0], G)          # 只取 24 之前段（項集/直方圖/lock 迴圈）
TERMS = G["TERMS"]; b = G["b"]; ATOMS = G["ATOMS"]; BDEP = G["BDEP"]; lock24 = G["lock"]
d24 = json.load(open(os.path.join(BASE, "data", "24_r5_discrimination.json"), encoding="utf-8"))
OUT = []
def p(s=""):
    print(s); OUT.append(s)
def ispow(e):
    return any(pp.base == 2 and pp.exp.free_symbols for pp in e.atoms(sp.Pow))
# ---- 支配界: |poly(B)| ≤ C·Σ_{k≤4}B^k ；2^B > C·Σ + |target|（B ≥ B0）⟹ 掃 [1,B0] 完備
MX = 1
for (c, k, val, ee) in TERMS:
    if ispow(ee):
        MX = max(MX, abs(c))
    else:
        for co in sp.Poly(ee, b).all_coeffs():
            MX = max(MX, abs(sp.Rational(co)))
C = 4 * MX; VMAX = 1000
B0 = 1
while 2**B0 <= C * (B0**4 + B0**3 + B0**2 + B0 + 1) + VMAX:
    B0 += 1
p("=" * 78)
p("O229 / R5 第三路線仲裁（verify/third_route_arbiter.py）")
p("=" * 78)
p(f"項集 = {len(TERMS)}（取自 24 前段）；單項係數上界 MX = {MX}；C = 4·MX = {C}")
p(f"支配界 B0 = {B0}：2^{B0} = {2**B0} > C·Σ B0^k + {VMAX} = {C*(B0**4+B0**3+B0**2+B0+1)+VMAX}")
p(f"比例 2·(B/(B+1))⁴ > 1（B ≥ 2）⟹ 對所有 B ≥ B0 成立 ⟹ 掃 [1,B0] 即完備")
rows = []; diffs = []; nid = 0; npowf = 0; ncmp = 0
for v in ATOMS:
    cnt = 0
    for comb in G["forms_by_val"].get(v, []):
        if not any(BDEP[TERMS[i][1]] for i in comb):
            continue                                        # 純常數式 ⟹ 唔鎖 B
        ex = sp.expand(sum(TERMS[i][3] for i in comb) - v)
        if ex == 0:
            nid += 1; continue                              # 恆等成立 ⟹ 零信息
        if ispow(ex):
            npowf += 1
            rs = [Bv for Bv in range(1, B0 + 1) if int(ex.subs(b, Bv)) == 0]
        else:
            try:
                rs = sorted(int(r) for r in sp.real_roots(sp.Poly(ex, b))
                            if r.is_positive and r.is_integer)
            except ZeroDivisionError:
                nid += 1; continue
        ncmp += 1
        if rs == [4]:
            cnt += 1
    rows.append((v, lock24[v], cnt))
    if cnt != lock24[v]:
        diffs.append((v, lock24[v], cnt))
p(f"\n比對形式數 = {ncmp:,}（恆等類 {nid}；含 2^B {npowf}）")
p(f"與 24 之 lock 表差異原子數 = {len(diffs)}")
for v, a_, c_ in diffs:
    p(f"  ✗ v={v}: 24={a_} 仲裁={c_}")
p("\nlock 表（v: 24 / 仲裁）")
for v, a_, c_ in rows:
    p(f"  {v:4d}: {a_:5d} / {c_:5d}" + ("" if a_ == c_ else "   ✗"))
same_json = all(lock24[v] == d24["lock"]["table"][str(v)] for v in ATOMS)
p(f"\n24 代碼內 lock == 24 JSON lock 表: {same_json}")
verdict = (len(diffs) == 0) and same_json
p(f"\nRESULT: {'PASS' if verdict else 'FAIL'} — 第三路線與 24 逐項一致")
os.makedirs(os.path.join(BASE, "verify"), exist_ok=True)
open(os.path.join(BASE, "verify", "third_route_arbiter.out"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
json.dump({"script": "verify/third_route_arbiter.py", "terms": len(TERMS), "MX": int(MX), "C": int(C), "B0": int(B0),
           "compared_forms": int(ncmp), "ident_forms": int(nid), "pow_forms": int(npowf),
           "diff_atoms": [[int(a) for a in d] for d in diffs],
           "lock_table_24": {str(v): int(lock24[v]) for v in ATOMS},
           "lock_table_arbiter": {str(v): int(c) for v, a_, c in rows},
           "json_consistent": same_json, "verdict": "PASS" if verdict else "FAIL"},
          open(os.path.join(BASE, "verify", "third_route_arbiter.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
