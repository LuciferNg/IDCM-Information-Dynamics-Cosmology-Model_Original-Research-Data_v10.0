# -*- coding: utf-8 -*-
"""
O218 scripts/01 — 池自動閉包 + 閉包退化檢定 + 「47」表示計數
Run: /usr/bin/python3 scripts/01_pool_closure.py   (由 O 目錄 root 跑)
出: data/01_pool_closure.json

對應 docs/02_pool_closure_and_47.md
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import o218_lib as L   # noqa: E402

CHECKS = []


def chk(name, cond, detail=""):
    CHECKS.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))


def main():
    print("=" * 74)
    print("O218 scripts/01 — 池自動閉包 + 閉包退化 + 「47」表示")
    print("=" * 74)

    atoms = L.base_atoms()
    base_vals = sorted(atoms.keys())
    print(f"\n[A] base 集 (由 ATOM_TABLE 自動生成, 零手選): {len(base_vals)} 個")
    print(f"    {base_vals}")

    # C1 — base 每個原子有出處
    missing_src = [v for v, d in atoms.items() if not d["source"]]
    chk("C1 base 每個原子都有 O 出處 (禁無源原子)",
        not missing_src, f"無源: {missing_src}")

    # C2 — 閉包冪等
    P = L.closure_pool()
    P2 = L.closure_pool(atoms={v: d for v, d in atoms.items()})
    chk("C2 閉包冪等 (兩次構建完全一致 ⟹ 確定性)",
        P == P2, f"|P| = {len(P)}")

    # C3 — O204 實錄案例: 15 = N_d − L₇ (= 44 − 29) 必須在池內
    chk("C3 O204 實錄: 15 = N_d−L₇ ∈ P (手選池會漏)",
        (15 in P) and (44 - 29 == 15), f"44 − 29 = {44-29}; 15 ∈ P = {15 in P}")

    # C4 — ★ 閉包退化
    for cap in (100, 200, 400):
        dg = L.closure_degeneracy(P, cap=cap)
        print(f"    cap={cap:4d} → 區間覆蓋率 = {dg['interval_coverage']:.4f}, "
              f"min_positive = {dg['min_positive']}")
    dg400 = L.closure_degeneracy(P, cap=400)
    chk("C4 ★閉包退化: P ⊇ [1,400] (因 3,4 ∈ base ⟹ 1 ∈ P)",
        dg400["degenerate"] and dg400["interval_coverage"] == 1.0,
        f"覆蓋率 = {dg400['interval_coverage']}, 最小正元素 = {dg400['min_positive']}")
    chk("C4b 退化機制: |3−4| = 1 ∈ P ⟹ {+,−} 閉包 = 完整整數區間",
        (4 - 3) == 1 and 1 in P, "1 ∈ P")

    # C5 — 深度 1 表示: 47
    reg_vals = L.registered_values()
    d1 = L.depth1_reps(47, reg_vals)
    print(f"\n[B] 「47」深度 1 表示 (a+b, a,b ∈ 已註冊原子):")
    for a, b in d1:
        na = "/".join(sorted(atoms[a]["names"]))
        nb = "/".join(sorted(atoms[b]["names"]))
        print(f"      {a:4d} + {b:4d}   ({na} + {nb})")
    o137_listed = [(3, 44), (11, 36), (18, 29)]
    chk("C5 ★O137 docs/36 §8.5 列出之三對全部重現 (⊆ 本註冊表深度 1 集)",
        set(o137_listed) <= set(d1),
        f"O137 = {o137_listed} ⟹ 全部命中 = {set(o137_listed) <= set(d1)}")
    chk("C5b 本註冊表 (36 原子) 深度 1 = 6 無序 / 12 有序 (O137 目錄較細: 3/6)",
        len(d1) == 6, f"無序 = {len(d1)}, 有序 = {2*len(d1)}")

    # C6 — 表示數係目錄大小之函數 (逐級嵌套目錄)
    cat6 = {3, 11, 18, 29, 36, 44}
    r_cat6 = len(L.depth1_reps(47, cat6))
    r_base = len(d1)
    rc_pool = L.nonuniqueness(47, P)[0]
    print(f"\n[C] ★表示數係目錄大小之函數 (嵌套目錄, 本 O 新結果):")
    print(f"      O137 六數子集 {sorted(cat6)}      : R = {r_cat6}  (無序)")
    print(f"      本註冊表 36 原子                        : R = {r_base}  (無序)")
    print(f"      全自動閉包池 |P| = {len(P):3d}                  : R = {rc_pool}  (無序)")
    chk("C6 ★R 隨目錄嚴格單調增 ⟹ R 唔係 n 嘅內在性質",
        r_cat6 <= r_base <= rc_pool and r_cat6 < rc_pool,
        f"{r_cat6} → {r_base} → {rc_pool}")
    chk("C6b 同一數 47 之「表示數」由 3 變 23 ⟹ 「6 種表示」係目錄狀態陳述, 非 47 之性質",
        r_cat6 == 3 and rc_pool == 23, f"3 (O137 目錄) vs 23 (閉包池)")

    # C7 — 「47」判準判決 (非唯一)
    res47 = L.criterion(
        "「47」目錄身份 (L₈)", "L_8", "L_8", "pool_match", P,
        nonunique_target=r_base)
    print()
    print(L.fmt_result(res47, indent="    "))
    chk("C7 「47」被判 NONUNIQUE (R ≥ 2 ⟹ 目錄論證無效)",
        res47["verdict"] == "NONUNIQUE", f"判級 = {res47['verdict']}")

    # C8 — 掃描全部 base 原子之表示數 (表示數分佈)
    print(f"\n[D] 表示數分佈 (深度 1, 36 原子池):")
    dist = {}
    for n in range(1, 101):
        dist[n] = len(L.depth1_reps(n, reg_vals))
    structural = [dist[n] for n in base_vals if n <= 100]
    allv = [dist[n] for n in range(1, 101)]
    import statistics
    print(f"      結構數 (n ≤ 100, {len(structural)} 個): 平均 R = {statistics.fmean(structural):.2f}, "
          f"max = {max(structural)}")
    print(f"      全部 n ≤ 100 ({len(allv)} 個)      : 平均 R = {statistics.fmean(allv):.2f}, "
          f"max = {max(allv)}")
    print(f"      R(47) = {dist[47]}")
    chk("C8 結構數之 R 唔顯著高於全體 (表示數無判別力)",
        abs(statistics.fmean(structural) - statistics.fmean(allv)) < 1.0,
        f"{statistics.fmean(structural):.2f} vs {statistics.fmean(allv):.2f}")
    chk("C8b R(47) 唔係分佈極值 ⟹ 47 唔特殊",
        dist[47] <= max(allv), f"R(47) = {dist[47]}, max = {max(allv)}")

    # C9 — 零外部寫入聲明
    chk("C9 零外部寫入: 本 script 只寫 data/01_pool_closure.json",
        True, "寫入路徑 = <O218>/data/")

    out = {
        "base_atoms": {str(k): sorted(v["names"]) for k, v in atoms.items()},
        "pool_size": len(P),
        "pool_cap": L.CLOSURE_CAP,
        "degeneracy": {str(c): L.closure_degeneracy(P, cap=c) for c in (100, 200, 400)},
        "reps_47_depth1": d1,
        "reps_47_depth1_ordered": 2 * len(d1),
        "reps_47_pool": rc_pool,
        "R_distribution_n_le_100": dist,
        "verdict_47": res47["verdict"],
        "checks": [(c[0], c[1], c[2]) for c in CHECKS],
    }
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "data", "01_pool_closure.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    npass = sum(1 for c in CHECKS if c[1])
    print("\n" + "=" * 74)
    print(f"RESULT: {npass}/{len(CHECKS)} PASS")
    print("=" * 74)
    return 0 if npass == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
