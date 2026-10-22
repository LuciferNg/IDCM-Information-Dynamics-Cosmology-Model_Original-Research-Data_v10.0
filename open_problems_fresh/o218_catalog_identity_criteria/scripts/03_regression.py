# -*- coding: utf-8 -*-
"""
O218 scripts/03 — 回歸測試 (Regression Suite)
Run: /usr/bin/python3 scripts/03_regression.py
出: data/03_regression.json

用 IDCM 全庫**已判死** (O151/O199/O201/O137) 同**已閉合** (O169/O211/O213) 之真實案例
做回歸測試集 — 判準必須「已知判死全判死 + 已知閉合全放行」。

★ 測試集自身審計 (O201 §7/§8): 每個案例附出處 file:line; 先標性質再算統計。
對應 docs/04_regression.md
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import o218_lib as L   # noqa: E402

CHECKS = []
ROWS = []


def row(case, src, kind, res, expect, note="", group=None):
    """group: "dead" (已知判死) | "alive" (已知閉合) — 顯式聲明, 唔靠 nature 字串推斷。"""
    ok = res["verdict"] == expect
    ROWS.append({"case": case, "source": src, "nature": kind, "group": group,
                 "verdict": res["verdict"], "expect": expect, "group": group,
                 "dev": res["dev"], "note": note,
                 "gates": res["gates"]})
    CHECKS.append((case, ok, f"{res['verdict']} (期望 {expect})"))
    print(f"  [{'PASS' if ok else 'FAIL'}] {case}")
    print(f"         出處 {src} | {kind}")
    print(f"         判級 {res['emoji']} {res['verdict']} (期望 {expect})"
          f" | dev = {'n/a' if res['dev'] is None else format(res['dev'], '.4g')}")
    if res["notes"]:
        for n in res["notes"][:3]:
            print(f"         · {n}")


def main():
    print("=" * 78)
    print("O218 scripts/03 — 回歸測試 (已知判死 / 已知閉合)")
    print("=" * 78)
    P = L.closure_pool()
    A = 990

    # =============================================================
    print("\n【A】已知判死案例 — 判準必須判 🔴")
    # =============================================================

    print("\nA1. O151 docs/12 §4 — b₁×30 = 123 = L₁₀")
    r = L.criterion("b₁×30 = L₁₀", "b1_SM*30", "L_10", "pool_match", P)
    row("b₁×30 = 123 = L₁₀", "o151/docs/12_b1_123_coincidence_verdict.md §4",
        "跨框架巧合", r, "COINCIDENCE", group="dead")

    print("\nA2. O151 docs/12 §3 — b₁ = 2N_gen×f_unproj")
    r = L.criterion("b₁ = 2N_gen·f_unproj", "x41/10", "2*N_gen*(x41/60)",
                    "pool_match", P, shared_symbol="x41", d_obs=0.0,
                    allow_symbols=("x41",))
    row("b₁ = 2N_gen×f_unproj", "o151/docs/12 §3", "重言式", r, "TAUTOLOGY", group="dead")

    print("\nA3. O151 docs/12 §5 — MSSM 33 = N_gen×L₅")
    r = L.criterion("MSSM b₁×5 = K_tree", "b1_MSSM*5", "K_tree", "pool_match", P)
    row("MSSM 33 = N_gen×L₅", "o151/docs/12 §5", "跨框架巧合", r, "COINCIDENCE",
        group="dead")

    print("\nA4. O199 docs/02 — 框架強逼值 C_energy = 1/45 vs 觀測 2.000%")
    dev_lead = abs(1 / 45 - 0.02) / 0.02
    r = L.criterion("C_energy = 1/45 = 2.222% vs 觀測 2.000%",
                    "mdot_2pct", "mu2/(2*N_d+mu2)", "prediction_residual", P,
                    target_precision=0.01)
    row("C_energy 1/45 (2.222%) vs 觀測 2.000%",
        "o199/docs/02_audit_20260921.md", "預言殘差 (11.1% 偏差)", r, "FALSE", group="dead",
        note=f"dev = {dev_lead:.4f}")

    print("\nA5. O199 docs/02 — 複合式救援 (1/45)·(9/10) = 0.02000000")
    fd = L.farey_density(0.02, 1e-9, L.q_max_for_form("quotient_product", A))
    r = L.criterion("(1/45)·(9/10) = 2.000%", "mdot_2pct",
                    "mu2/(2*N_d+mu2) * N_gen**2/(N_gen**2+1)",
                    "prediction_residual", P, density=fd, leading_dev=dev_lead,
                    target_precision=1e-4)
    row("(1/45)·(9/10) = 0.02 (複合救援式)", "o199/docs/02 §3 表",
        "兩級測試 (乘性修正承載)", r, "MULTIPLIER", group="dead",
        note=f"主體偏差 {dev_lead:.4f}")

    print("\nA6. O151 docs/05 §4 — log₂(S_dS) vs 406 = C(29,2)")
    r = L.criterion("log₂(S_dS) = 406 = C(29,2)", "log2_SdS", "L_8",
                    "pool_match", P, d_obs=5.9e-4, tol_rel=1e-3,
                    target_precision=1e-4, allow_symbols=("log2_SdS",))
    row("log₂(S_dS) ≈ 406", "o151/docs/05_holographic_bound.md §4",
        "陷阱窗", r, "TRAP", group="dead")

    print("\nA7. O201 docs/03 §二 — C_old = −0.1697 (最近池命中 dev 1.42e-4)")
    r = L.criterion("C_old = −0.1697", "C_old_sym", "C_old_sym", "pool_match", P,
                    d_obs=1.42e-4, tol_rel=1e-3, target_precision=1e-4,
                    allow_symbols=("C_old_sym",))
    row("C_old = −0.1697", "o201/docs/03_identity_criterion.md §二",
        "陷阱窗 (已證偽係數)", r, "TRAP", group="dead")

    print("\nA8. O201 docs/03 §二 — b_spec = √5/2 (域分離)")
    r = L.criterion("b_spec = √5/2", "b_spec", "sqrt5/2", "pool_match", P,
                    d_obs=9.660e-4, tol_rel=1e-3, field_pair=(5, 176))
    row("b_spec vs √5/2", "o201/docs/03 §二 + docs/04",
        "數域分離", r, "FIELD", group="dead")

    print("\nA9. O137 docs/36 §8.5 — 「47」目錄身份 (6 種表示)")
    r_base = len(L.depth1_reps(47, L.registered_values()))
    r = L.criterion("「47」目錄身份 (L₈)", "L_8", "L_8", "pool_match", P,
                    nonunique_target=r_base)
    row("「47」目錄身份", "o137/docs/36_gap_attack_round19.md §8.5",
        "目錄表示非唯一", r, "NONUNIQUE", note=f"R = {r_base}", group="dead")

    # =============================================================
    print("\n【B】已知閉合案例 — 判準必須放行 🟢")
    # =============================================================

    print("\nB1. O211 — Σγ = B(N_d+1)/2 = 90 EXACT")
    cert = L.certify_exact_numeric(L.sum_gamma(1, 44), 90)
    r = L.criterion("Σγ = B(N_d+1)/2", "Sigma_gamma", "B*(N_d+1)/2", "identity", P,
                    exact_cert=("numeric", cert[1]))
    row("Σγ = 90 = B(N_d+1)/2", "o211_geometry_generation (Σγ 閉式)",
        "代數恆等式", r, "IDENTITY_OK", group="alive", note=f"|差| = {cert[1]}")

    print("\nB2a. O169/O211 — γ⁽⁸⁸⁾_n + γ⁽⁸⁸⁾_{44−n} = 4 = B ∀n (88 鏈配對)")
    sym88 = L.certify_exact_symbolic(
        "4*sin(pi*n/88)**2 + 4*sin(pi*(N_d-n)/88)**2", "B")
    print(f"      sympy 化簡差 = {sym88[1]}")
    r = L.criterion("γ⁽⁸⁸⁾_n + γ⁽⁸⁸⁾_{44−n} = B",
                    "4*sin(pi*n/88)**2 + 4*sin(pi*(N_d-n)/88)**2", "B",
                    "identity", P, exact_cert=("symbolic", sym88[1]),
                    allow_symbols=("n",))
    row("γ⁽⁸⁸⁾_n + γ⁽⁸⁸⁾_{44−n} = 4 = B", "o169 docs/02:21 + o211 docs/01 C7",
        "符號恆等式", r, "IDENTITY_OK", group="alive", note=f"sympy 差 = {sym88[1]}")

    print("\nB2b. O124 A1 — γ⁽¹⁷⁶⁾_{44−j} + γ⁽¹⁷⁶⁾_{44+j} = 4 = B ∀j (176 鏈鏡像)")
    sym176 = L.certify_exact_symbolic(
        "4*sin(pi*(N_d-j)/176)**2 + 4*sin(pi*(N_d+j)/176)**2", "B")
    print(f"      sympy 化簡差 = {sym176[1]}")
    r = L.criterion("γ⁽¹⁷⁶⁾_{44−j} + γ⁽¹⁷⁶⁾_{44+j} = B",
                    "4*sin(pi*(N_d-j)/176)**2 + 4*sin(pi*(N_d+j)/176)**2", "B",
                    "identity", P, exact_cert=("symbolic", sym176[1]),
                    allow_symbols=("j",))
    row("γ⁽¹⁷⁶⁾_{44±j} = 4 = B", "o124 scripts/13 A1 (o160 docs/06 §4)",
        "符號恆等式", r, "IDENTITY_OK", group="alive", note=f"sympy 差 = {sym176[1]}")

    print("\nB2c. O124 A3 負結果 — γ⁽¹⁷⁶⁾_n + γ⁽¹⁷⁶⁾_{44−n} ≠ 4 (冇任何 n, 鏈條件性)")
    sym_neg = L.certify_exact_symbolic(
        "4*sin(pi*n/176)**2 + 4*sin(pi*(N_d-n)/176)**2", "B")
    wp = L.wrong_pairing_check("176")
    print(f"      sympy 化簡差 ≠ 0: {not sym_neg[0]} | 最近接偏差 = {wp['min_dev']:.6f}")
    r = L.criterion("γ⁽¹⁷⁶⁾_n + γ⁽¹⁷⁶⁾_{44−n} = B (錯配對)",
                    "4*sin(pi*n/176)**2 + 4*sin(pi*(N_d-n)/176)**2", "B",
                    "identity", P, exact_cert=("symbolic", sym_neg[1]),
                    allow_symbols=("n",))
    row("γ⁽¹⁷⁶⁾_n + γ⁽¹⁷⁶⁾_{44−n} ≠ 4 (錯配對)", "o124 docs/09 §A3 (負結果)",
        "負結果 (鏈條件性)", r, "FALSE", note=f"最近接 dev = {wp['min_dev']:.4f}", group="dead")

    print("\nB3. O169 B1 — Σ_{odd} γ = N_d = 44 EXACT")
    s_odd = L.sum_gamma_odd(43)
    cert = L.certify_exact_numeric(s_odd, 44)
    print(f"     Σ_{{奇 n ≤ 43}} γ_n = {L.sp.N(s_odd, 20)}")
    r = L.criterion("Σ_{odd} γ = N_d", "Sigma_gamma_odd", "N_d", "identity", P,
                    exact_cert=("numeric", cert[1]))
    row("Σγ_odd = 44 = N_d", "o169 B1 (Z₂ 反對稱)",
        "代數恆等式", r, "IDENTITY_OK", group="alive", note=f"|差| = {cert[1]}")

    print("\nB4. O213 R5 — 946 = C(N_d,2) EXACT")
    cert = L.certify_exact_numeric(44 * 43 / 2, 946)
    r = L.criterion("946 = C(N_d,2)", "C_Nd_2", "N_d*(N_d-1)/2", "identity", P,
                    exact_cert=("numeric", cert[1]))
    row("946 = C(44,2)", "o213 world_dynamics R5",
        "組合恆等式", r, "IDENTITY_OK", group="alive", note=f"|差| = {cert[1]}")

    print("\nB5. O124/O81 — 123 = L₁₀ = Tr(T̂¹⁰) = E_J")
    r = L.criterion("123 = Tr(T̂¹⁰) = L₁₀", "E_J", "L_10", "identity", P,
                    exact_cert=("numeric", 0))
    row("123 = L₁₀ = E_J", "o124 §b₀ / o81 U3",
        "算子恆等式", r, "IDENTITY_OK", group="alive")

    print("\nB6. O169/O213 R3 — b_spec vs DESI 自由擬合 b = 1.12157 ± 0.02458")
    b_fit, sig = 1.12157, 0.02458
    pull = abs(1.119113982034844 - b_fit) / sig
    r = L.criterion("b_spec vs DESI fit", "b_spec", "b_spec_fit",
                    "prediction_residual", P, d_obs=abs(1.119113982034844 - b_fit) / b_fit,
                    target_precision=sig / b_fit, allow_symbols=("b_spec_fit",))
    row("b_spec vs DESI free fit", "o169 docs/02 + docs/09",
        "預言殘差 (σ 內)", r, "MATCH_OK", group="alive", note=f"pull = {pull:.3f}σ")

    print("\nB7. O124 — 4g 頂點色代數 G_ss = 72 = C_A²(N_c²−1) EXACT")
    cert = L.certify_exact_numeric(3 ** 2 * (3 ** 2 - 1), 72)
    r = L.criterion("G_ss = 72", "G_ss", "N_gen**2*(N_gen**2-1)", "identity", P,
                    exact_cert=("numeric", cert[1]), allow_symbols=("G_ss",))
    row("G_ss = 72 (4g 色代數)", "o124/QCD 扇區",
        "色代數恆等式", r, "IDENTITY_OK", group="alive", note=f"|差| = {cert[1]}")

    # =============================================================
    print("\n【C】分佈統計 (O208 密度基準以身作則)")
    # =============================================================
    dead = [r for r in ROWS if r["group"] == "dead"]
    alive = [r for r in ROWS if r["group"] == "alive"]
    assert len(dead) + len(alive) == len(ROWS), "每行必須聲明 group"
    n_dead_ok = sum(1 for r in dead if r["verdict"] == r["expect"])
    n_alive_ok = sum(1 for r in alive if r["verdict"] == r["expect"])
    print(f"     判死案例 {len(dead)}: {n_dead_ok} 判死正確")
    print(f"     閉合案例 {len(alive)}: {n_alive_ok} 放行正確")
    n_all = sum(1 for r in ROWS if r["verdict"] == r["expect"])

    out = {"rows": ROWS, "n_dead": len(dead), "n_dead_ok": n_dead_ok,
           "n_alive": len(alive), "n_alive_ok": n_alive_ok,
           "checks": [(c[0], c[1], c[2]) for c in CHECKS]}
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "data", "03_regression.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)

    npass = sum(1 for c in CHECKS if c[1])
    print("\n" + "=" * 78)
    print(f"RESULT: {npass}/{len(CHECKS)} PASS  (判死 {n_dead_ok}/{len(dead)} + "
          f"放行 {n_alive_ok}/{len(alive)})")
    print("=" * 78)
    return 0 if npass == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
