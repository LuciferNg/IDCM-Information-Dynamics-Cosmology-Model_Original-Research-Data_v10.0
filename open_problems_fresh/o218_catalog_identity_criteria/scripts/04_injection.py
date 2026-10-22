# -*- coding: utf-8 -*-
"""
O218 scripts/04 — 注入測試 (Injection / Falsifiability Test)
Run: /usr/bin/python3 scripts/04_injection.py
出: data/04_injection.json

★ 目的 (SESSION_START 鐵律「判準要可執行、有牙」):
  對**已閉合**嘅真案例故意注入一類缺陷, 判準必須 (a) 判級由 🟢 翻 🟡/🔴,
  且 (b) 由**正確嘅 gate** 判死 (可追溯 — 唔可以「亂槍打鳥」)。
  同時做**形式不變性**測試: 等價改寫 (別名/次序) 唔可以改變判級。

對應 docs/05_falsifiability.md
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import o218_lib as L   # noqa: E402

CHECKS = []
ROWS = []


def rec(tag, inj, res, want_verdict, want_gate=None, note=""):
    ok = (res["verdict"] == want_verdict) if isinstance(want_verdict, str) \
        else (res["verdict"] in want_verdict)
    gate_ok = True
    if want_gate:
        gate_ok = any(res["gates"].get(k) in ("FAIL", "MISSING", "WEAK")
                      for k in (want_gate if isinstance(want_gate, (list, tuple))
                                else [want_gate]))
        ok = ok and gate_ok
    CHECKS.append((tag, ok, f"{res['verdict']} / gate {want_gate}"))
    ROWS.append({"tag": tag, "injection": inj, "verdict": res["verdict"],
                 "want_verdict": want_verdict, "want_gate": want_gate,
                 "gate_fired": [k for k, v in res["gates"].items()
                                if v in ("FAIL", "MISSING", "WEAK")],
                 "dev": res["dev"], "note": note})
    print(f"  [{'PASS' if ok else 'FAIL'}] {tag} — 注入: {inj}")
    want_txt = want_verdict if isinstance(want_verdict, str) else sorted(want_verdict)
    print(f"         判級 {res['emoji']} {res['verdict']} (期望 {want_txt})"
          f" | dev = {'n/a' if res['dev'] is None else format(res['dev'], '.4g')}")
    print(f"         觸發 gate: {ROWS[-1]['gate_fired']}")
    return ok


def main():
    print("=" * 78)
    print("O218 scripts/04 — 注入測試 (判準 falsifiability)")
    print("=" * 78)
    P = L.closure_pool()
    A = 990
    reg = L.registered_values()
    n_green = 0

    # 基準 🟢 案例 (B1/B2 已閉合)
    cert90 = L.certify_exact_numeric(L.sum_gamma(1, 44), 90)
    base_ok = L.criterion("Σγ = 90", "Sigma_gamma", "B*(N_d+1)/2", "identity", P,
                          exact_cert=("numeric", cert90[1]))
    print(f"\n基準 🟢: Σγ = 90 → {base_ok['verdict']}")
    n_green += base_ok["verdict"] == "IDENTITY_OK"

    # =================================================================
    print("\n【I】注入 1 — 目標偏 1 (off-by-one): Σγ = 91")
    # =================================================================
    cert = L.certify_exact_numeric(L.sum_gamma(1, 44), 91)
    r = L.criterion("Σγ = 91", "Sigma_gamma", "N_d + Sigma_gamma_odd + 1", "identity", P,
                    exact_cert=("numeric", cert[1]))
    rec("I1 off-by-one (+1)", "目標 90 → 91", r, {"FALSE"}, "G0_equality_holds")

    # =================================================================
    print("\n【I】注入 2 — 擬合常數: Σγ = 90 × 1.000237")
    # =================================================================
    obs_fit = 1.119113982034844 * 1.000237
    r = L.criterion("b_spec × 1.000237 = 觀測", "obs_fit_b", "b_spec * 1.000237",
                    "prediction_residual", P, target_precision=1e-4,
                    allow_symbols=("obs_fit_b",))
    rec("I2 擬合常數", "加乘性擬合因子 1.000237 去命中觀測", r, {"FITTED"},
        "G3_zero_free_param", note=f"觀測 = {obs_fit:.9f}")

    # =================================================================
    print("\n【I】注入 3 — 閉包退化葉 397 (∈ P 但無結構身份)")
    print("     ⚠️ 對照: 24 有深度 1 表示 (3+21) ⟹ 仍屬合法 DEPTH1 葉 —")
    print("        資訊量工作落在 U (表示數) 與 G5 (密度), 唔在 G1 (見 docs/05 §限制)")
    # ⚠️ 必須用 evaluate=False: sp.sympify("397 - 307") 會即時化簡成 90 ⟹ 葉消失
    e397 = L.sp.Add(L.sp.Integer(397), L.sp.Integer(-307), evaluate=False)
    r = L.criterion("Σγ = 397 − 307", "Sigma_gamma", e397, "identity", P,
                    exact_cert=("numeric", 0))
    rec("I3 閉包退化葉 (397)", "葉 397 只係「落喺閉包區間」", r, {"ILLEGAL"},
        "G1_G2_leaf_audit")
    # 葉分類階梯 (直接單元檢查, 唔經字串解析)
    lad = {v: L.audit_numeric_literals(L.sp.Integer(v), P)[0][1]
           for v in (24, 397, 401, 946)}
    print(f"     葉分類階梯: {lad}")
    chk3 = (lad[24] == "DEPTH1" and lad[397] == "CLOSURE_TRIVIAL"
            and lad[401] == "BARELITERAL" and lad[946] == "REGISTERED")
    CHECKS.append(("I3b 葉分類階梯 (24 DEPTH1 / 397 CLOSURE_TRIVIAL / 401 BARELITERAL)",
                   chk3, str(lad)))
    print(f"  [{'PASS' if chk3 else 'FAIL'}] I3b 葉分類階梯 — {lad}")

    # =================================================================
    print("\n【I】注入 4 — 域分離: Σγ_odd = N_d (44) 偷換成 √5/2·(88/√5)/2")
    #             直接把目標換成域外數: N_d = b_spec/√5 → 域分離觸發
    # =================================================================
    r = L.criterion("N_d = b_spec/√5", "N_d", "b_spec/sqrt5", "pool_match", P,
                    d_obs=0.0023, tol_rel=1e-2, field_pair=(5, 176))
    rec("I4 數域偷換", "N_d → b_spec/√5", r, {"FIELD", "FALSE"}, "G6_field")

    # =================================================================
    print("\n【I】注入 5 — 陷阱窗: Σγ = 90 (dev 1.42e-4), 目標精度 1e-4")
    # =================================================================
    r = L.criterion("Σγ = 90 (窗口內近失)", "Sigma_gamma", "B*(N_d+1)/2",
                    "identity", P, d_obs=1.42e-4, tol_rel=1e-3,
                    target_precision=1e-4)
    rec("I5 陷阱窗", "把 EXACT 鬆成 dev 1.42e-4", r, {"TRAP"},
        "G4_trap_window")

    # =================================================================
    print("\n【I】注入 6 — 自由乘數: Σγ = 90 但偷偷 ×(9/10) 去命中外目標")
    # =================================================================
    fd = L.farey_density(81.0, 1e-9, L.q_max_for_form("quotient_product", A))
    r = L.criterion("Σγ × 9/10 = 81", "L_8_obs", "Sigma_gamma*(N_gen**2/(N_gen**2+1))",
                    "prediction_residual", P, d_obs=0.0, density=fd,
                    leading_dev=0.10, target_precision=1e-4,
                    allow_symbols=("L_8_obs",))
    rec("I6 自由乘數", "加乘性修正因子 9/10", r, {"MULTIPLIER", "DENSITY"},
        ["T5_two_level", "G5_density"])

    # =================================================================
    print("\n【I】注入 7 — 重言式: 用共有量 41 (SM 固有) 砌 Σγ_odd")
    # =================================================================
    r = L.criterion("Σγ_odd = x41·44/x41", "Sigma_gamma_odd", "x41*N_d/x41",
                    "pool_match", P, shared_symbol="x41", d_obs=0.0,
                    allow_symbols=("x41",))
    rec("I7 重言式", "等式對共有量 41 恆等", r, {"TAUTOLOGY"}, "T1_tautology")

    # =================================================================
    print("\n【I】注入 8 — 跨框架: Σγ_odd(44) 換成 MSSM b₁ 之倍數")
    # =================================================================
    r = L.criterion("b₁_MSSM × 20/3 = N_d", "b1_MSSM*20/3", "N_d",
                    "pool_match", P)
    rec("I8 跨框架巧合", "MSSM b₁ 重新包裝成 N_d", r, {"COINCIDENCE"},
        "T2_cross_framework")

    # =================================================================
    print("\n【I】注入 9 — 目錄非唯一: Σγ_odd = 44 = 41+3 報成目錄身份")
    # =================================================================
    r44 = len(L.depth1_reps(44, reg))
    r = L.criterion("Σγ_odd 當目錄值", "Sigma_gamma_odd", "N_d", "pool_match", P,
                    nonunique_target=r44)
    rec("I9 目錄非唯一", "把已閉合恆等式降級成「目錄值」", r, {"NONUNIQUE"},
        "U_nonunique", note=f"R(44) = {r44}")

    # =================================================================
    print("\n【I】注入 10 — 密度膨脹: 用 3 因子複合式命中任意目標")
    # =================================================================
    fd3 = L.farey_density(90.0, 1e-9, 990 ** 3)
    print(f"     3 因子 q_max = 990³ ⟹ {fd3['note']}")
    r = L.criterion("任意目標 = 3 因子複合", "target_arb", 
                    "B*(N_d+1)/2 * (N_gen**2/(N_gen**2+1)) * (F_5/F_5)",
                    "pool_match", P, d_obs=0.0, density=fd3,
                    allow_symbols=("target_arb",))
    rec("I10 密度膨脹 (3 因子)", "加第 3 個因子 ⟹ 池爆炸", r, {"DENSITY"},
        "G5_density")

    # =================================================================
    print("\n【I】注入 11 — 實數冒充: 葉換成未註冊實數 1.118033989 (=√5/2 小數)")
    # =================================================================
    r = L.criterion("N_d = 1.118033989 × 44/1.118033989", "N_d",
                    "1.118033989*(N_d/1.118033989)", "identity", P,
                    exact_cert=("numeric", 1.0))
    rec("I11 實數冒充", "√5/2 寫成十進小數", r, {"FITTED"}, "G3_zero_free_param")

    # =================================================================
    print("\n【I】注入 12 — 無出處符號: 葉用未註冊符號 y_z")
    # =================================================================
    r = L.criterion("Σγ = y_z", "Sigma_gamma", "y_z", "identity", P,
                    exact_cert=("numeric", 1.0))
    rec("I12 無出處符號", "引入未註冊符號 y_z", r, {"ILLEGAL"},
        "G1_G2_leaf_audit")

    # =================================================================
    print("\n【I】注入 13 — 裸數 401 (> cap ⟹ 唔喺閉包 ⟹ BARELITERAL)")
    # =================================================================
    e401 = L.sp.Add(L.sp.Integer(401), L.sp.Integer(-311), evaluate=False)
    r = L.criterion("Σγ = 401 − 311", "Sigma_gamma", e401, "identity", P,
                    exact_cert=("numeric", 0))
    rec("I13 裸數 401", "葉 401 超出閉包上限", r, {"ILLEGAL"}, "G1_G2_leaf_audit")

    print("\n【N】形式不變性 (等價改寫唔可以改變判級)")
    # =================================================================
    a = L.criterion("Σγ = 90", "Sigma_gamma", "B*(N_d+1)/2", "identity", P,
                    exact_cert=("numeric", cert90[1]))
    b = L.criterion("Σγ = 90 (次序換)", "Sigma_gamma", "(N_d+1)*B/2 + 0",
                    "identity", P, exact_cert=("numeric", cert90[1]))
    print(f"     原式 {a['verdict']} vs 等價改寫 {b['verdict']}")
    CHECKS.append(("N1 等價改寫判級不變", a["verdict"] == b["verdict"] == "IDENTITY_OK",
                   f"{a['verdict']} / {b['verdict']}"))
    print(f"  [{'PASS' if CHECKS[-1][1] else 'FAIL'}] N1 等價改寫判級不變")

    c = L.criterion("γ_n + γ_{44−n} = B", "4*sin(pi*n/88)**2 + 4*sin(pi*(N_d-n)/88)**2",
                    "B", "identity", P,
                    exact_cert=("symbolic", L.certify_exact_symbolic(
                        "4*sin(pi*n/88)**2 + 4*sin(pi*(N_d-n)/88)**2", "B")[1]),
                    allow_symbols=("n",))
    d = L.criterion("γ_n + γ_{44−n} = B (用 43)", 
                    "4*sin(pi*n/88)**2 + 4*sin(pi*(43+1-n)/88)**2", "B",
                    "identity", P, exact_cert=("symbolic", L.certify_exact_symbolic(
                        "4*sin(pi*n/88)**2 + 4*sin(pi*(43+1-n)/88)**2", "B")[1]),
                    allow_symbols=("n",))
    CHECKS.append(("N2 等價寫法 (43+1) 判級不變",
                   c["verdict"] == d["verdict"] == "IDENTITY_OK",
                   f"{c['verdict']} / {d['verdict']}"))
    print(f"  [{'PASS' if CHECKS[-1][1] else 'FAIL'}] N2 等價寫法 43+1 判級不變"
          f" ({c['verdict']} / {d['verdict']})")

    # =================================================================
    print("\n【N】敏感度: 🟢 案例對 1e-6 級目標擾動之反應")
    # =================================================================
    # 註: 冇精確證書時, identity 類只可判 🟡 FORMAL_OK (未閉合) — 唔可以白拿 🟢
    for eps, want in ((1e-12, "FORMAL_OK"), (1e-6, "FALSE"), (1e-3, "FALSE")):
        r = L.criterion(f"Σγ = 90×(1+{eps:g})", "Sigma_gamma", "B*(N_d+1)/2",
                        "identity", P, d_obs=eps)
        ok = r["verdict"] == want
        CHECKS.append((f"N3 敏感度 dev = {eps:g}", ok, f"{r['verdict']} (期望 {want})"))
        print(f"  [{'PASS' if ok else 'FAIL'}] N3 dev = {eps:g} ⟹ {r['verdict']}"
              f" (期望 {want})")

    out = {"rows": ROWS, "checks": [(c[0], c[1], c[2]) for c in CHECKS]}
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "data", "04_injection.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)

    npass = sum(1 for c in CHECKS if c[1])
    print("\n" + "=" * 78)
    print(f"RESULT: {npass}/{len(CHECKS)} PASS (12 類注入 + 5 形式/敏感度)")
    print("=" * 78)
    return 0 if npass == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
