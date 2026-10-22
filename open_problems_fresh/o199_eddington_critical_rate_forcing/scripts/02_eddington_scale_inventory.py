#!/usr/bin/env python3
"""
O199 scripts/02 - Inventory of IDCM dimensionless quantities at the 2% scale

GOAL
  Before asking "is 0.02 geometrically forced?", establish what the framework
  ALREADY contains at the 0.5% - 25% scale. Everything here is recomputed from
  first principles (no hard-coded known values):

     44-site chain      : gamma_n = 4 sin^2(pi n / 88),  n = 1..44
     176-Laplacian half : G_k     = 4 sin^2(pi k / 176), k = 1..88
     (convention note: gamma_44 = 2 in the 44-chain, = 4 in the 176 half-set;
      every registered identity below is labelled with its convention)

  Registered identities recomputed and verified:
     sum_{n odd}  gamma_n = N_d = 44              (O169 B1, EXACT)
     sum_{n even} gamma_n = 46 = N_d + mu^2
     sum_n gamma_n        = 90 = 2 N_d + mu^2
     sum_{k odd}  G_k     = 88 = 2 N_d            (O201 176 half-set)
     sum_{k even} G_k     = 90
     sum_k G_k            = 178 = 2 F_11          (O192)
     C_energy = (sum_even - sum_odd)/sum = mu^2/(2N_d+mu^2) = 1/45 EXACT (O203)

ASCII only.
"""

import json
import os
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
O_DIR = os.path.dirname(SCRIPT_DIR)
DATA = os.path.join(O_DIR, "data")

results = []


def check(name, cond, detail=""):
    results.append({"name": name, "pass": bool(cond), "detail": detail})
    print(("  PASS " if cond else "  FAIL ") + name + (" | " + detail if detail else ""))


# --- framework integers -----------------------------------------------------
N_d, B, N_gen, mu2 = 44, 4, 3, 2
L4, L5, L6 = 7, 11, 18
F5, F6, F7, F11 = 5, 8, 13, 89
F_proj = L6 - 1              # 17
M_tree = 33                  # = F_9 - 1
K_tree = 30
L10 = 123
W2_mean = 61.5               # <W>^2 (O204)
A5_V, A5_E = 60, 120

print("=" * 78)
print("O199 / 02 - IDCM dimensionless quantities at the 2% scale (inventory)")
print("=" * 78)

# --- spectra from first principles -----------------------------------------
g44 = [4.0 * math.sin(math.pi * n / 88.0) ** 2 for n in range(1, 45)]        # n=1..44
G176 = [4.0 * math.sin(math.pi * k / 176.0) ** 2 for k in range(1, 89)]      # k=1..88

s_odd44 = sum(g44[n - 1] for n in range(1, 45) if n % 2 == 1)
s_even44 = sum(g44[n - 1] for n in range(1, 45) if n % 2 == 0)
s_tot44 = sum(g44)
s_odd176 = sum(G176[k - 1] for k in range(1, 89) if k % 2 == 1)
s_even176 = sum(G176[k - 1] for k in range(1, 89) if k % 2 == 0)
s_tot176 = sum(G176)

print("  44-chain      : sum_odd = %.10f  sum_even = %.10f  sum = %.10f"
      % (s_odd44, s_even44, s_tot44))
print("  176 half-set  : sum_odd = %.10f  sum_even = %.10f  sum = %.10f"
      % (s_odd176, s_even176, s_tot176))

check("S1 44-chain sum_odd = N_d = 44 EXACT", abs(s_odd44 - N_d) < 1e-9, "%.12f" % s_odd44)
check("S2 44-chain sum_even = N_d + mu^2 = 46", abs(s_even44 - (N_d + mu2)) < 1e-9, "%.12f" % s_even44)
check("S3 44-chain sum = 2 N_d + mu^2 = 90", abs(s_tot44 - (2 * N_d + mu2)) < 1e-9, "%.12f" % s_tot44)
check("S4 176 half-set sum_odd = 2 N_d = 88", abs(s_odd176 - 2 * N_d) < 1e-9, "%.12f" % s_odd176)
check("S5 176 half-set sum = 2 F_11 = 178", abs(s_tot176 - 2 * F11) < 1e-9, "%.12f" % s_tot176)
check("S6 gamma_22 = mu^2 = 2 (Z2 self-dual mode, 44-chain)",
      abs(g44[21] - mu2) < 1e-12, "gamma_22 = %.12f" % g44[21])
check("S7 convention: gamma_44 = 4 in 44-chain (= gamma_max) / = mu^2 = 2 in the 88-site ring",
      abs(g44[43] - 4.0) < 1e-12 and abs(4.0 * math.sin(math.pi * 44.0 / 176.0) ** 2 - mu2) < 1e-12,
      "gamma_44(44-chain) = %.6f ; gamma_44(88-site) = %.6f"
      % (g44[43], 4.0 * math.sin(math.pi * 44.0 / 176.0) ** 2))

# --- registered dimensionless quantities at the 2% scale --------------------
W2_mean = 61.5
# <phi^2> = sum_k 1/(gamma_k + 2) over the 176-Laplacian half-set (O159 T2):
# computed here from first principles, NOT hard-coded.
phi2_var = sum(1.0 / (G + mu2) for G in G176)
phi2_registered = 25.236745
print("  <phi^2> = sum_k 1/(gamma_k+mu^2) (176 half-set) = %.9f  [O159 T2 registered: %.6f, dev %.2e]"
      % (phi2_var, phi2_registered, abs(phi2_var - phi2_registered) / phi2_registered))
check("S8 <phi^2> reproduces the O159 T2 registered value",
      abs(phi2_var - phi2_registered) / phi2_registered < 1e-6,
      "computed %.9f vs registered %.6f" % (phi2_var, phi2_registered))

inv = [
    # (label, value, convention/source, form-class)
    ("C_energy = mu^2/(2N_d+mu^2) = 1/45", mu2 / (2 * N_d + mu2), "44-chain, O203 EXACT", "single spectral ratio"),
    ("mu^2/(2N_d) = 1/44", mu2 / (2 * N_d), "site-count normalisation, O7/O203", "single spectral ratio"),
    ("(sum_even-sum_odd)/sum (176)", (s_even176 - s_odd176) / s_tot176, "176 half-set, = mu^2/2F_11", "single spectral ratio"),
    ("mu^2/sum (176 half-set)", mu2 / s_tot176, "176 half-set", "single spectral ratio"),
    ("1/(2N_d) = 1/88", 1.0 / (2 * N_d), "Nyquist single mode", "single spectral ratio"),
    ("1/(N_d*B) = 1/176", 1.0 / (N_d * B), "full 176 cycle", "single spectral ratio"),
    ("lambda_self = mu^2/L_10 = 2/123", mu2 / L10, "O204 vacuum coupling", "single spectral ratio"),
    ("mu^2/<W>^2 = 4/123", 4.0 / L10, "O204", "single spectral ratio"),
    ("1/(2*<phi^2>) = 1/(2*25.236745)", 1.0 / (2 * phi2_var), "O159 propagator sum", "transcendental"),
    ("1/60 = 1/A5_V", 1.0 / A5_V, "A5 net vertices", "geometric"),
    ("1/(N_d+B+mu^2) = 1/50", 1.0 / (N_d + B + mu2), "integer sum", "integer ratio"),
    ("C_energy*(1-lambda_Edd) = 1/50", (mu2 / (2 * N_d + mu2)) * (1 - B / (N_d - B)),
     "composition of 2 registered identities", "composite"),
    ("lambda_Edd = B/(N_d-B) = 1/10", float(B) / (N_d - B), "O176 D10 candidate", "registered candidate"),
    ("r_LRD = N_gen/(N_d-B) = 3/40", float(N_gen) / (N_d - B), "O176 D8 candidate", "registered candidate"),
    ("1/(L4*N_gen) = 1/21", 1.0 / (L4 * N_gen), "K(0) window", "integer ratio"),
    ("1/(L4*B) = 1/28", 1.0 / (L4 * B), "K(F_proj) window", "integer ratio"),
    ("1/(2N_d+B+mu^2) = 1/94", 1.0 / (2 * N_d + B + mu2), "integer sum", "integer ratio"),
    ("1/(N_d+2N_gen) = 1/50", 1.0 / (N_d + 2 * N_gen), "integer sum", "integer ratio"),
    ("1/(2*F5^2) = 1/50", 1.0 / (2 * F5 * F5), "integer sum", "integer ratio"),
    ("1/(M+F_proj) = 1/50", 1.0 / (M_tree + F_proj), "integer sum", "integer ratio"),
    ("1/(L4^2+1) = 1/50", 1.0 / (L4 * L4 + 1), "integer sum", "integer ratio"),
    ("1/(A5_E-A5_V-2B) = 1/52", 1.0 / (A5_E - A5_V - 2 * B), "integer sum", "integer ratio"),
    ("f_proj^2/10 = (19/60)^2/10", (19.0 / 60.0) ** 2 / 10.0, "derived", "composite"),
    ("1/45 * 9/10 (N/(N+1), N=N_gen^2)", (1.0 / 45.0) * (9.0 / 10.0), "O171 truncation form", "composite"),
]

print("-" * 78)
print("  target = 0.02   (dev = |v-0.02|/0.02)")
print("  %-46s %12s %9s  %s" % ("quantity", "value", "dev", "class"))
rows = []
for label, val, src, cls in inv:
    dev = abs(val - 0.02) / 0.02
    rows.append({"label": label, "value": val, "dev": dev, "source": src, "class": cls})
rows.sort(key=lambda r: r["dev"])
for r in rows:
    print("  %-46s %12.8f %8.3f%%  %s" % (r["label"][:46], r["value"], r["dev"] * 100.0, r["class"]))

# --- how many land inside the windows? --------------------------------------
w1 = (0.010, 0.030)
w2 = (0.018, 0.022)
in_w1 = [r for r in rows if w1[0] <= r["value"] <= w1[1]]
in_w2 = [r for r in rows if w2[0] <= r["value"] <= w2[1]]
print("-" * 78)
print("  in W1 [0.010,0.030] : %d / %d" % (len(in_w1), len(rows)))
print("  in W2 [0.018,0.022] : %d / %d  -> %s"
      % (len(in_w2), len(rows), ", ".join(r["label"][:40] for r in in_w2)))

check("I1 at least one registered identity inside W1",
      len(in_w1) > 0, "%d inside" % len(in_w1))
check("I2 C_energy (1/45) and 1/44 both inside W1 but neither inside W2",
      all(w1[0] <= v <= w1[1] for v in (mu2 / (2 * N_d + mu2), mu2 / (2 * N_d))) and
      all(not (w2[0] <= v <= w2[1]) for v in (mu2 / (2 * N_d + mu2), mu2 / (2 * N_d))),
      "1/45 = %.6f ; 1/44 = %.6f" % (mu2 / (2 * N_d + mu2), mu2 / (2 * N_d)))
check("I3 every EXACT hit on 0.02 is an integer-ratio or composite form",
      len(in_w2) > 0 and all(r["class"] in ("integer ratio", "composite")
                             for r in in_w2 if r["dev"] < 1e-12),
      "exact hits: %d ; classes: %s"
      % (sum(1 for r in in_w2 if r["dev"] < 1e-12),
         sorted(set(r["class"] for r in in_w2 if r["dev"] < 1e-12))))
check("I4 the only non-integer-form near-hit is 1/(2<phi^2>) at 0.94%",
      len([r for r in in_w2 if r["class"] not in ("integer ratio", "composite")]) == 1,
      "non-integer near-hits: %s"
      % [r["label"] for r in in_w2 if r["class"] not in ("integer ratio", "composite")])

out = {
    "spectra": {
        "sum_odd_44chain": s_odd44, "sum_even_44chain": s_even44, "sum_44chain": s_tot44,
        "sum_odd_176half": s_odd176, "sum_even_176half": s_even176, "sum_176half": s_tot176,
    },
    "target": 0.02,
    "windows": {"W1": list(w1), "W2": list(w2)},
    "inventory": rows,
}
os.makedirs(DATA, exist_ok=True)
with open(os.path.join(DATA, "02_eddington_scale_inventory.json"), "w") as fh:
    json.dump(out, fh, indent=2)

n_pass = sum(1 for r in results if r["pass"])
print("=" * 78)
print("TOTAL: %d/%d PASS" % (n_pass, len(results)))
print("wrote data/02_eddington_scale_inventory.json")
