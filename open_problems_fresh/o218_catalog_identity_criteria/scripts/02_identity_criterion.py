# -*- coding: utf-8 -*-
"""
O218 scripts/02 — 統一判準引擎自檢 (Criterion Engine Self-Test)
Run: /usr/bin/python3 scripts/02_identity_criterion.py
出: data/02_identity_criterion.json

每個 gate 用一個最小規範案例驗證會唔會正確觸發 (O148「check 簽名坑」教訓:
判準唔識 FAIL 就等於冇判準)。對應 docs/03_unified_criterion.md
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import o218_lib as L   # noqa: E402

CHECKS = []
RESULTS = []


def chk(name, cond, detail=""):
    CHECKS.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))


def dv(r):
    return "n/a" if r.get("dev") is None else f"{r['dev']:.4g}"


def show(res):
    RESULTS.append(res)
    print(L.fmt_result(res, indent="     "))


def main():
    print("=" * 74)
    print("O218 scripts/02 — 統一判準引擎自檢")
    print("=" * 74)
    P = L.closure_pool()
    A = 990          # 池上限 (q_max 用)

    # ---------------------------------------------------------------
    print("\n[C1] 判準輸出格式穩定 (gate 鍵齊全 + 判級 code ∈ V)")
    r_probe = L.criterion("probe", "N_d", "N_d", "identity", P,
                          exact_cert=("numeric", 0))
    need = {"G0_equality_holds", "G1_G2_leaf_audit", "G3_zero_free_param",
            "T1_tautology", "T2_cross_framework", "T3_free_multiplier",
            "T5_two_level", "U_nonunique", "G4_trap_window", "G5_exact_cert",
            "G5_density", "G6_field"}
    chk("C1 gate 鍵齊全 (12 個)", need <= set(r_probe["gates"].keys()),
        f"缺: {sorted(need - set(r_probe['gates'].keys()))}")
    chk("C1b 判級 code ∈ V", r_probe["verdict"] in L.V, r_probe["verdict"])

    # ---------------------------------------------------------------
    print("\n[C2] 已知閉合 (identity 類): Σγ = B(N_d+1)/2 = 90 EXACT")
    cert = L.certify_exact_numeric(L.sum_gamma(1, 44), 90)
    print(f"     Σ_{{n=1}}^{{44}} 4sin²(πn/88) = {L.sum_gamma(1,44)}")
    print(f"     標稱 B(N_d+1)/2 = {4*45/2};  精確證書 |差| = {cert[1]}")
    r = L.criterion("Σγ = B(N_d+1)/2", "Sigma_gamma", "B*(N_d+1)/2",
                    "identity", P, exact_cert=("numeric", cert[1]))
    show(r)
    chk("C2 判 🟢 IDENTITY_OK (N_search = 1, 唔受密度檢定)",
        r["verdict"] == "IDENTITY_OK" and r["emoji"] == "🟢",
        f"{r['verdict']}, N_search = {r['density'].get('N_search')}")

    # ---------------------------------------------------------------
    print("\n[C3] G0 等式真偽: 44 = 45 (必然錯)")
    r = L.criterion("44 = 45", "N_d", "Omega_Lambda_num + B", "pool_match", P)
    show(r)
    chk("C3 判 🔴 FALSE (等式唔成立)", r["verdict"] == "FALSE",
        f"dev = {dv(r)}")

    # ---------------------------------------------------------------
    print("\n[C4] G3 自由參數: b_spec × 1.000237 (擬合常數)")
    r = L.criterion("b_spec × 1.000237", "b_spec * 1.000237",
                    "b_spec * 1.000237", "pool_match", P, d_obs=0.0)
    show(r)
    chk("C4 判 🔴 FITTED (含擬合常數)", r["verdict"] == "FITTED",
        f"{r['verdict']}")

    # ---------------------------------------------------------------
    print("\n[C5] T1 重言式: b₁ = 2·N_gen·f_unproj (共有量 41 為 SM 固有)")
    r = L.criterion("b₁ = 2·N_gen·f_unproj [41 共有]", "x41/10",
                    "2*N_gen*(x41/60)", "pool_match", P,
                    shared_symbol="x41", d_obs=0.0, allow_symbols=("x41",))
    show(r)
    chk("C5 判 🔴 TAUTOLOGY (等式對共有量 x41 恆等)",
        r["verdict"] == "TAUTOLOGY", f"{r['verdict']}")
    # 對照: 若共有量自己有 IDCM 推導 ⟹ 唔觸發
    d = L.t1_tautology("x41/10", "2*N_gen*(x41/60)", L.sp.Symbol("x41"))[1]
    chk("C5b T1 測試本身正確: 化簡 (x/10 − 6x/60) = 0", d == 0, f"差 = {d}")

    # ---------------------------------------------------------------
    print("\n[C6] T2 跨框架巧合: b₁_SM × 30 = 123 = L₁₀")
    r = L.criterion("b₁_SM × 30 = L₁₀", "b1_SM*30", "L_10", "pool_match", P)
    show(r)
    chk("C6 判 🔴 COINCIDENCE (IDCM ↔ EXTERNAL 無共同推導)",
        r["verdict"] == "COINCIDENCE", f"{r['verdict']}")
    print("\n     對照: 123 = L₁₀ = Tr(T̂¹⁰) (同一算子家族, 唔觸發 T2)")
    r2 = L.criterion("123 = Tr(T̂¹⁰) = L₁₀", "E_J", "L_10", "identity", P,
                     exact_cert=("numeric", 0))
    show(r2)
    chk("C6b 對照組判 🟢 (同一框架 ⟹ T2 唔觸發)",
        r2["verdict"] == "IDENTITY_OK", f"{r2['verdict']}")

    # ---------------------------------------------------------------
    print("\n[C7] U 非唯一表示: 「47」目錄身份")
    r_base = len(L.depth1_reps(47, L.registered_values()))
    r = L.criterion("「47」目錄身份 (L₈)", "L_8", "L_8", "pool_match", P,
                    nonunique_target=r_base)
    show(r)
    chk("C7 判 🔴 NONUNIQUE (R = 6 ≥ 2)", r["verdict"] == "NONUNIQUE",
        f"R = {r_base}")

    # ---------------------------------------------------------------
    print("\n[C8] G4 陷阱窗: C_old = −0.1697 (最近命中 dev = 1.42e-4)")
    r = L.criterion("C_old = −0.1697 (最近池命中)", "C_old_candidate",
                    "C_old_candidate", "pool_match", P,
                    d_obs=1.42e-4, target_precision=1e-4, tol_rel=1e-3,
                    allow_symbols=("C_old_candidate",))
    show(r)
    chk("C8 判 🔴 TRAP (目標精度 1e-4 優於窗寬 ⟹ 窗律綁定)",
        r["verdict"] == "TRAP", f"{r['verdict']}")
    print("\n     對照 (O201 §2 前置條件): 目標精度 0.63% ≫ 窗寬 ⟹ 窗律 n/a")
    inw, reason = L.trap_window(1.42e-4, target_precision=6.3e-3)
    r2 = L.criterion("C_old (0.63% 擬合值)", "C_old_candidate", "C_old_candidate",
                     "prediction_residual", P, d_obs=1.42e-4,
                     target_precision=6.3e-3,
                     allow_symbols=("C_old_candidate",))
    show(r2)
    chk("C8b 窗律前置條件正確 (精度差過窗寬 ⟹ 唔誤殺)",
        (not inw) and r2["gates"]["G4_trap_window"] == "PASS", reason)

    # ---------------------------------------------------------------
    print("\n[C9] G6 數域分離: b_spec (Q(ζ₁₇₆)⁺) vs √5/2 (Q(√5))")
    r = L.criterion("b_spec = √5/2", "b_spec", "sqrt5/2", "pool_match", P,
                    d_obs=9.660e-4, tol_rel=1e-3, field_pair=(5, 176))
    show(r)
    chk("C9 判 🔴 FIELD (gcd(5,176) = 1 ⟹ 結構上唔可能相等)",
        r["verdict"] == "FIELD", f"{r['verdict']}")

    # ---------------------------------------------------------------
    print("\n[C10] G5 Farey 密度: (1/45)·(9/10) = 0.02 (O199 複合式)")
    fd = L.farey_density(0.02, 1e-9, L.q_max_for_form("quotient_product", A))
    print(f"     {fd['note']}")
    r = L.criterion("(1/45)·(9/10) = 0.02", "mdot_2pct",
                    "mu2/(2*N_d+mu2) * N_gen**2/(N_gen**2+1)",
                    "prediction_residual", P,
                    density=fd, leading_dev=0.1111, target_precision=1e-4)
    show(r)
    chk("C10 判 🔴 MULTIPLIER (T5 兩級測試: 主體 11.1% 偏差, 乘性修正承載匹配)",
        r["verdict"] == "MULTIPLIER", f"{r['verdict']}")
    print("\n     對照 (同一複合式但無兩級資訊): 只餘 Farey 密度 🔴")
    r2 = L.criterion("(1/45)·(9/10) = 0.02 [只報密度]", "mdot_2pct",
                     "mu2/(2*N_d+mu2) * N_gen**2/(N_gen**2+1)",
                     "prediction_residual", P, density=fd)
    show(r2)
    chk("C10b 無兩級資訊時由 Farey 密度判 🔴 DENSITY",
        r2["verdict"] == "DENSITY", f"{r2['verdict']}")
    chk("C10c Farey N_search ≫ 1 (2 因子商積, q_max = 990²)",
        fd["N_search_farey"] > 1.0, f"N = {fd['N_search_farey']:.4g}")

    # ---------------------------------------------------------------
    print("\n[C11] O200 三分類: 同一式三類給出唔同判級")
    a = L.criterion("identity 類", "Sigma_gamma", "B*(N_d+1)/2", "identity", P,
                    exact_cert=("numeric", cert[1]))
    b = L.criterion("pool_match 類 (無密度)", "L_8", "L_8", "pool_match", P)
    c = L.criterion("prediction 類 (觀測 σ 內)", "b_spec", "b_spec_obs",
                    "prediction_residual", P, d_obs=3.7e-4, target_precision=1e-2,
                    allow_symbols=("b_spec_obs",))
    show(a); show(b); show(c)
    chk("C11 identity → 🟢 (N_search = 1)", a["verdict"] == "IDENTITY_OK")
    chk("C11b pool_match 無密度基準 → 🟡 (未閉合, 缺密度)",
        b["verdict"] in ("FORMAL_OK", "WEAK_DENSITY"), f"{b['verdict']}")
    chk("C11c prediction_residual 用 σ 判 (唔用密度)",
        c["gates"]["G5_density"].startswith("MISSING")
        or c["verdict"] in ("FORMAL_OK", "MATCH_OK"), f"{c['verdict']}")

    # ---------------------------------------------------------------
    print("\n[C12] 判準確定性 + 無全域狀態 (call-order independent)")
    r_a = L.criterion("det", "L_8", "L_8", "pool_match", P, nonunique_target=6)
    r_b = L.criterion("det", "L_8", "L_8", "pool_match", P, nonunique_target=6)
    chk("C12 兩次判決完全一致",
        json.dumps(r_a, sort_keys=True, default=str)
        == json.dumps(r_b, sort_keys=True, default=str))
    r_c = L.criterion("det", "L_8", "L_8", "pool_match", P, nonunique_target=1)
    chk("C12b 只改非唯一參數 ⟹ 判級由 NONUNIQUE 變 (判準有牙)",
        r_a["verdict"] == "NONUNIQUE" and r_c["verdict"] != "NONUNIQUE",
        f"{r_a['verdict']} → {r_c['verdict']}")

    # ---------------------------------------------------------------
    print("\n[C13] 交換 lhs/rhs 判級不變 (方向無關)")
    x = L.criterion("swap", "b1_SM*30", "L_10", "pool_match", P)
    y = L.criterion("swap", "L_10", "b1_SM*30", "pool_match", P)
    chk("C13 交換後判級相同", x["verdict"] == y["verdict"],
        f"{x['verdict']} vs {y['verdict']}")

    out = {"results": [{"name": r["name"], "class": r["class"], "verdict": r["verdict"],
                        "gates": r["gates"], "dev": r["dev"],
                        "density": {k: (float(v) if isinstance(v, (int, float)) else v)
                                    for k, v in (r.get("density") or {}).items()},
                        "notes": r["notes"]}
                       for r in RESULTS],
           "checks": [(c[0], c[1], c[2]) for c in CHECKS]}
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "data", "02_identity_criterion.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)

    npass = sum(1 for c in CHECKS if c[1])
    print("\n" + "=" * 74)
    print(f"RESULT: {npass}/{len(CHECKS)} PASS")
    print("=" * 74)
    return 0 if npass == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
