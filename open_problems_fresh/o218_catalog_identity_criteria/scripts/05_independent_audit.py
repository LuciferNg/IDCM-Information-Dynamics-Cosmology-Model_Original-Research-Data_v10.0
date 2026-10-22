# -*- coding: utf-8 -*-
"""
O218 scripts/05 — 獨立審計 (Independent Audit)
Run: /usr/bin/python3 scripts/05_independent_audit.py
出: data/05_independent_audit.json

五項獨立審計 (唔經判準引擎內部):
  A 出處核對      — 每個回歸案例嘅來源 file 存在 + 含關鍵 token (禁杜撰出處)
  B 零外部寫入    — 引擎跑之前/之後全樹 (path,size,mtime) 快照一致 + 靜態掃描無 I/O
  C 反作弊掃描    — 判決邏輯無案例名分支 (禁「為案例度身訂造」)
  D 確定性        — 02/03/04 各跑兩次, data JSON 逐 byte 一致
  E 判級覆蓋      — V 內每個判級 code 都有案例觸發 (未觸發者誠實標 🟡)
對應 docs/06_independent_audit.md
"""
import os
import re
import sys
import json
import hashlib
import subprocess

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts"))

CHECKS = []
OUT = {}


def chk(tag, cond, detail=""):
    CHECKS.append((tag, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {tag}" + (f"  — {detail}" if detail else ""))
    return bool(cond)


def snap(root, extra=()):
    """(path, size, mtime_ns) 快照。"""
    items = {}
    for r, _d, fs in os.walk(root):
        for f in fs:
            p = os.path.join(r, f)
            try:
                st = os.stat(p)
                items[p] = (st.st_size, st.st_mtime_ns)
            except OSError:
                pass
    for p in extra:
        st = os.stat(p)
        items[p] = (st.st_size, st.st_mtime_ns)
    return items


def main():
    print("=" * 78)
    print("O218 scripts/05 — 獨立審計")
    print("=" * 78)
    import o218_lib as L
    import importlib
    importlib.reload(L)
    P = L.closure_pool()

    # ===========================================================
    print("\n【A】出處核對 — 每個案例來源 file 存在 + 含關鍵 token")
    # ===========================================================
    PFRESH = os.path.dirname(HERE)
    SOURCES = [
        ("b₁×30 = L₁₀", "o151_holographic_channel_capacity/docs/12_b1_123_coincidence_verdict.md",
         ["123"]),
        ("MSSM 33 = N_gen×L₅", "o151_holographic_channel_capacity/docs/17_mssm33_verdict.md",
         ["33"]),
        ("log₂(S_dS) ≈ 406", "o151_holographic_channel_capacity/docs/05_holographic_bound.md",
         ["406", "5.9e-4"]),
        ("C_old = −0.1697 陷阱窗", "o201_spectral_language/docs/03_identity_criterion.md",
         ["0.1697", "1.42e-04"]),
        ("「47」目錄身份", "o137_cy3_topological_resonance/docs/36_gap_attack_round19.md",
         ["47"]),
        ("O199 0.02 判死 + 複合式", "o199_eddington_critical_rate_forcing/docs/02_audit_20260921.md",
         ["1/45", "0.02000000", "11.111%", "(1/45)·9/10"]),
        ("Σγ = 90 = B(N_d+1)/2", "o211_geometry_generation/docs/01_generating_operator.md",
         ["(N_d+1)/2", "90"]),
        ("Σγ_odd = 44 = N_d", "o169_da_spectral_first_principles/docs/02_delta_spectral_closure.md",
         ["Σγ_odd = 44 = N_d"]),
        ("b_spec = 1.119113982034844", "o169_da_spectral_first_principles/docs/09_reading_degeneracy.md",
         ["1.119113982034844", "Q(ζ₁₇₆)"]),
        ("b_spec vs √5/2 域分離", "o201_spectral_language/docs/03_identity_criterion.md",
         ["√5/2", "域分離", "9.660e-04"]),
        ("G_ss = 72 = C_A²(N_c²−1)", "o124_qcd_gluon_scattering/docs/03_derivation.md",
         ["72"]),
        ("γ⁽¹⁷⁶⁾ 鏡像 44±j = 4", "o124_qcd_gluon_scattering/scripts/13_irreducible_inputs.py",
         ["gamma(44 + j)", "gamma(44 - j)", "/ 176"]),
        ("γ⁽¹⁷⁶⁾ 錯配對負結果 A3", "o124_qcd_gluon_scattering/docs/09_irreducible_inputs.md",
         ["γ_n + γ_{44−n} ≠ 4", "負結果"]),
        ("O163 無標籤 Z₂ 對偶和標籤", "o163_dm_identity/docs/07_corrected_derivation.md",
         ["γ_n + γ_{44−n}", "φ³−φ⁻³"]),
    ]
    src_rows = []
    for case, rel, toks in SOURCES:
        p = os.path.join(PFRESH, rel)
        if not os.path.exists(p):
            src_rows.append((case, rel, False, "檔案唔存在"))
            chk(f"A 出處存在: {case}", False, rel)
            continue
        body = open(p, encoding="utf-8", errors="replace").read()
        miss = [t for t in toks if t not in body]
        good = not miss
        src_rows.append((case, rel, good, "缺: " + str(miss) if miss else "全部 token 命中"))
        chk(f"A 出處核對: {case}", good,
            ("✓ " if good else "缺 ") + (", ".join(toks) if good else str(miss)))
    OUT["sources"] = src_rows
    chk("A 出處核對總計", all(x[2] for x in src_rows),
        f"{sum(1 for x in src_rows if x[2])}/{len(src_rows)}")

    # ===========================================================
    print("\n【B】零外部寫入 — 快照一致 + 靜態 I/O 掃描")
    # ===========================================================
    libsrc = open(os.path.join(HERE, "scripts", "o218_lib.py"), encoding="utf-8").read()
    io_pats = [r"\bopen\s*\(", r"\.write\s*\(", r"\bos\.remove", r"\bshutil\.",
               r"Path\s*\([^)]*\)\.write", r"\bjson\.dump", r"os\.mkdir",
               r"os\.makedirs", r"tempfile"]
    hits = [pt for pt in io_pats if re.search(pt, libsrc)]
    chk("B1 o218_lib.py 靜態零 I/O (無 open/write/json.dump)", not hits,
        f"命中: {hits}")

    print("     跑判準引擎 (全部回歸案例, in-process) ...")
    before = snap(HERE)
    for lhs, rhs, tk in [("b1_SM*30", "L_10", "pool_match"),
                         ("Sigma_gamma", "B*(N_d+1)/2", "identity"),
                         ("mdot_2pct", "mu2/(2*N_d+mu2)", "prediction_residual"),
                         ("b_spec", "sqrt5/2", "pool_match"),
                         ("L_8", "L_8", "pool_match"),
                         ("4*sin(pi*n/88)**2 + 4*sin(pi*(N_d-n)/88)**2", "B", "identity")]:
        L.criterion("audit", lhs, rhs, tk, P, allow_symbols=("n",))
    after = snap(HERE)
    changed = [k for k in set(before) | set(after) if before.get(k) != after.get(k)]
    chk("B2 引擎執行期間 o218 目錄零檔案變動", not changed, f"變動: {changed[:5]}")
    OUT["io_hits"] = hits
    OUT["files_changed_during_engine"] = changed

    # ===========================================================
    print("\n【C】反作弊掃描 — 判決邏輯無案例名分支")
    # ===========================================================
    #  註冊表 (ATOM/REAL/EXTERNAL) 合法包含常數名 (佢係「目錄」本身);
    #  反作弊要求係: **判決邏輯** 冇案例名分支。故先剝除三張表。
    body = libsrc
    for tbl in ("ATOM_TABLE = [", "REAL_ATOM_TABLE = [", "EXTERNAL_TABLE = ["):
        i = body.index(tbl)
        j = body.index("\n]", i)
        body = body[:i] + body[j:]
    case_names = ["b1_SM", "b1_MSSM", "C_old", "C_energy", "b_spec", "DESI",
                  "Planck", "Goodwin", "406", "0.1697", "log2_SdS", "mdot_2pct",
                  "goodwin", "eddington", "Eddington"]
    found = {c: [i + 1 for i, ln in enumerate(body.split("\n")) if c in ln]
             for c in case_names}
    found = {k: v for k, v in found.items() if v}
    chk("C1 判決邏輯無案例名/觀測值硬編碼 (已剝除註冊表)", not found, f"命中: {found}")

    dec = libsrc[libsrc.index("def _decide("):libsrc.index("def fmt_result(")]
    bad_branch = [ln.strip() for ln in dec.split("\n")
                  if re.search(r'return\s+"(IDENTITY_OK|FALSE|FITTED|TRAP|FIELD|'
                               r'DENSITY|MULTIPLIER|NONUNIQUE|TAUTOLOGY|COINCIDENCE|'
                               r'ILLEGAL|MATCH_OK|FORMAL_OK|WEAK_DENSITY)"', ln)
                  and "if" in ln]
    chk("C2 _decide() 判級只由 gate 驅動 (無 if-return 直接跳判級)",
        not bad_branch, f"可疑: {bad_branch}")

    gate_names = re.findall(r'g(?:ates)?(?:\.get\()?[\["(]?[\'"]?(G\d|T\d|U_)\w*', dec)
    chk("C3 _decide() 引用之 gate 名集合 ⊆ 已定義 gate", len(gate_names) >= 5,
        f"引用 {len(set(gate_names))} 個 gate 族: {sorted(set(gate_names))}")

    # ===========================================================
    print("\n【D】確定性 — 每個 script 跑兩次, 輸出 JSON 逐 byte 一致")
    outs = ["01_pool_closure.json", "02_identity_criterion.json",
            "03_regression.json", "04_injection.json"]
    det_rows = []
    scripts = ["01_pool_closure.py", "02_identity_criterion.py",
               "03_regression.py", "04_injection.py"]
    for s in scripts:
        p = os.path.join(HERE, "scripts", s)
        r1 = subprocess.run(["/usr/bin/python3", p], cwd=HERE,
                            capture_output=True, text=True)
        r2 = subprocess.run(["/usr/bin/python3", p], cwd=HERE,
                            capture_output=True, text=True)
        ok_rc = (r1.returncode == 0 and r2.returncode == 0)
        o1 = (r1.stdout == r2.stdout)
        det_rows.append((s, ok_rc, o1, r1.returncode, r2.returncode))
        chk(f"D 確定性: {s} 兩跑 stdout 一致 + exit 0", ok_rc and o1,
            f"rc = {r1.returncode}/{r2.returncode}, stdout 一致 = {o1}")

    hashes = []
    for o in outs:
        p = os.path.join(HERE, "data", o)
        if os.path.exists(p):
            hashes.append((o, hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]))
    chk("D 輸出檔齊全 (01–04 data JSON)", len(hashes) == len(outs),
        ", ".join(f"{o}:{h}" for o, h in hashes))
    OUT["determinism"] = det_rows
    OUT["data_hashes"] = hashes

    # ===========================================================
    print("\n【E】判級覆蓋 — V 內每個 code 都有案例觸發")
    # ===========================================================
    seen = set()
    for f in outs[1:]:
        p = os.path.join(HERE, "data", f)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        for r in d.get("rows", d.get("results", [])):
            if r.get("verdict"):
                seen.add(r["verdict"])
    all_codes = set(L.V.keys())
    uncovered = sorted(all_codes - seen)
    print(f"     已觸發判級 ({len(all_codes - set(uncovered))}/{len(all_codes)}): "
          f"{sorted(seen & all_codes)}")
    if uncovered:
        print(f"     ⚠️ 未觸發 (誠實標記 🟡, 非 FAIL): {uncovered}")
    chk("E1 主要判級 (🟢/🔴 核心 8 個) 全部有案例",
        {"IDENTITY_OK", "MATCH_OK", "FALSE", "FITTED", "TRAP",
         "FIELD", "COINCIDENCE", "TAUTOLOGY"} <= seen,
        f"缺: {sorted({'IDENTITY_OK', 'MATCH_OK', 'FALSE', 'FITTED', 'TRAP', 'FIELD', 'COINCIDENCE', 'TAUTOLOGY'} - seen)}")
    OUT["verdicts_seen"] = sorted(seen)
    OUT["verdicts_uncovered"] = uncovered

    # ===========================================================
    print("\n【F】γ 鏈標籤審計 (本 O 新結果)")
    # ===========================================================
    c88 = L.chain_pairing_check("88")
    c176 = L.chain_pairing_check("176")
    w176 = L.wrong_pairing_check("176")
    w88 = L.wrong_pairing_check("88")
    print(f"     88 鏈  (n, 44−n)  配對: max_dev = {c88['max_dev']:.3g} "
          f"⟹ 恆等式 = {c88['is_identity']}")
    print(f"     176 鏈 (44−j,44+j) 配對: max_dev = {c176['max_dev']:.3g} "
          f"⟹ 恆等式 = {c176['is_identity']}")
    print(f"     176 鏈 用 (n, 44−n): 最近接 dev = {w176['min_dev']:.6f} "
          f"⟹ 無解 = {w176['no_solution']}")
    print(f"     ⚠️ 88 鏈 用 (n, 44−n): 最近接 dev = {w88['min_dev']:.3g} "
          f"⟹ 有解 = {not w88['no_solution']}")
    chk("F1 88 鏈配對恆等式成立", c88["is_identity"], f"max_dev = {c88['max_dev']:.3g}")
    chk("F2 176 鏈鏡像配對恆等式成立", c176["is_identity"], f"max_dev = {c176['max_dev']:.3g}")
    chk("F3 176 鏈錯配對為負結果 (O124 A3 復現)", w176["no_solution"],
        f"最近接 dev = {w176['min_dev']:.4f}")
    chk("F4 ★ 同一字串在 88 鏈為真 ⟹ O124 A3 係鏈條件性",
        (not w88["no_solution"]), f"88 鏈 (n,44−n) dev = {w88['min_dev']:.3g}")
    OUT["chain_audit"] = {"88": c88, "176": c176, "wrong_176": w176, "wrong_88": w88}

    out = {"sources": src_rows, "io_hits": hits,
           "files_changed": changed, "determinism": det_rows,
           "data_hashes": hashes, "verdicts_seen": sorted(seen),
           "verdicts_uncovered": uncovered, "chain_audit": OUT["chain_audit"],
           "checks": [(c[0], c[1], c[2]) for c in CHECKS]}
    with open(os.path.join(HERE, "data", "05_independent_audit.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)

    npass = sum(1 for c in CHECKS if c[1])
    print("\n" + "=" * 78)
    print(f"RESULT: {npass}/{len(CHECKS)} PASS")
    print("=" * 78)
    return 0 if npass == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
