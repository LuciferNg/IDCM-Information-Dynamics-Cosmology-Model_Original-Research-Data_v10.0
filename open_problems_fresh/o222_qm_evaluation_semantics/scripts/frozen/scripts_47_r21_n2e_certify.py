#!/usr/bin/env python3
"""O222 R21/N2e -- EXACT certification of the N2a/N2b/N2d identifications (no floats anywhere).

  U side (144 pairs): sign(u_a.u_b) == sign(r_a.r_b)          [u from certified r=3 candidate: ints;
                                                              r from the frozen machine: exact Q(sqrt5)]
  V side (3844 pairs): sign(VM_j.VM_jp) == sign(v_j.v_jp)      [VM := Uc^T Kc, all integers;
                                                              v from the certified r=3 candidate: ints]
  reproduction: sign(Uc_i . VM_j) == Kc[i][j] on all 12x62 = 744 pairs                        [integers]
Contract: docs/33_r21_n2d_contract.md  (+ docs/30, docs/31).  Usage: /usr/bin/python3 -u scripts/47_r21_n2e_certify.py
"""
import importlib.util, json, os

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("a2_cert", os.path.join(HERE, "09_a2_rollback.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
axes, Uax, ids, types, hvec = m.load_inputs(); G, idx, MUL = m.build_group()
add, mul, S = m.add, m.mul, m.sgn
dot3 = lambda a, b: add(add(mul(a[0], b[0]), mul(a[1], b[1])), mul(a[2], b[2]))
R = [m.rot_ref(q, Uax[0]) for q in G]

spec2 = importlib.util.spec_from_file_location("b5_cert", os.path.join(HERE, "12_b5_budget.py"))
m2 = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(m2)
_mm, K, _M, _h, _i, _t = m2.load_machine()

J = json.load(open(os.path.join(ROOT, "data", "40_candidates.json"), encoding="utf-8"))
cand = J.get("candidates", J)
c3 = [c for c in cand if len(c["U"][0]) == 3][0]
Uc_all, V = c3["U"], c3["V"]           # integers on a 1e-4 grid
sgn = lambda x: 1 if x > 0 else (-1 if x < 0 else 0)
NAX = len(K[0]); NR = len(K)

# class representatives by K row pattern (frozen rows of the machine)
patt = {}
for i in range(NR):
    patt.setdefault(tuple(K[i]), i)
rep = sorted(patt.values())
assert len(rep) == 12, len(rep)
Kc = [[K[i][j] for j in range(NAX)] for i in rep]

# --- U side, exact Q(sqrt5) on the frozen side, integers on the candidate side
u_side_bad = 0
for a in range(12):
    for b in range(12):
        if S(dot3(R[rep[a]], R[rep[b]])) != sgn(sum(Uc_all[rep[a]][k] * Uc_all[rep[b]][k] for k in range(3))):
            u_side_bad += 1

# --- V side: VM = Uc^T Kc  (pure integers)
Uc = [Uc_all[i] for i in rep]
VM = [[sum(Kc[i][j] * Uc[i][k] for i in range(12)) for k in range(3)] for j in range(NAX)]
v_side_bad = sum(1 for a in range(NAX) for b in range(NAX)
                 if sgn(sum(VM[a][k] * VM[b][k] for k in range(3))) != sgn(sum(V[a][k] * V[b][k] for k in range(3))))
# --- reproduction of K on the 12 classes
repro_bad = sum(1 for i in range(12) for j in range(NAX)
                if sgn(sum(Uc[i][k] * VM[j][k] for k in range(3))) != Kc[i][j])
# --- degeneracy check
zero_vm = sum(1 for j in range(NAX) if all(x == 0 for x in VM[j]))
out = {"U_side_pairs": 144, "U_side_bad": u_side_bad, "V_side_pairs": NAX * NAX, "V_side_bad": v_side_bad,
       "reproduction_pairs": 12 * NAX, "reproduction_bad": repro_bad, "zero_VM_rows": zero_vm,
       "arithmetic": "no floats: integers for U/V/K; exact Q(sqrt5) (Fraction) for the frozen vectors",
       "verdict": "CERTIFIED" if (u_side_bad == 0 and v_side_bad == 0 and repro_bad == 0 and zero_vm == 0) else "NOT CERTIFIED"}
print(json.dumps(out, ensure_ascii=False))
json.dump(out, open(os.path.join(ROOT, "data", "47_r21_n2e_certify.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
