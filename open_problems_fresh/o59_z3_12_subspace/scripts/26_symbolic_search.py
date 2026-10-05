#!/usr/bin/env python3
"""
O59 Clean v_geom factor (1482.84) and lambda_2nd (2.3474) —
Symbolic structural identity search.
"""
import os, math, itertools, numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
phi = (1 + math.sqrt(5)) / 2
eps = phi**(-1) / 4  # 0.1545...

# ============ IDCM CONSTANT LIBRARY ============
constants = {
    # Structural numbers
    "Nd": 44, "B": 4, "Ngen": 3, "Ktree": 33,
    # K_Chain eigenvalues
    "g1": 4*math.sin(math.pi/88)**2,
    "g7": 4*math.sin(7*math.pi/88)**2,
    "g8": 4*math.sin(8*math.pi/88)**2,
    "g20": 4*math.sin(20*math.pi/88)**2,
    "g22": 4*math.sin(22*math.pi/88)**2,  # = 2
    "g33": 4*math.sin(33*math.pi/88)**2,
    "g44": 4*math.sin(44*math.pi/88)**2,  # = 4
    # Lucas numbers
    "L4": 7, "L5": 11, "L6": 18, "L7": 29, "L10": 123,
    # Fibonacci numbers
    "F5": 5, "F6": 8, "F7": 13, "F8": 21, "F9": 34,
    # Special
    "phi": phi, "phi_inv": phi**(-1), "phi_sq": phi**2,
    "eps": eps,
    "pi": math.pi,
    "M0": 27.900915,  # MeV
    "v_ew": 246220,  # MeV
}

# Target values
targets = {
    "factor_1482.84": 1482.84,
    "lam2_2.3474": 2.34737,
    "lam_max_35.4178": 35.41776824,
}

# ============ GENERATE CANDIDATE EXPRESSIONS ============
def generate_expressions():
    """Generate candidate expressions from IDCM structural numbers."""
    candidates = []
    K = list(constants.items())
    
    # Level 1: Simple expressions
    for name, val in K:
        if val > 0:
            candidates.append((f"{name}", val))
            candidates.append((f"1/{name}", 1/val))
            candidates.append((f"{name}^2", val**2))
            candidates.append((f"sqrt({name})", math.sqrt(val)))
    
    # Level 2: Products of two
    for (n1, v1), (n2, v2) in itertools.combinations(K, 2):
        if v1 > 0 and v2 > 0:
            candidates.append((f"{n1}*{n2}", v1*v2))
            candidates.append((f"{n1}/{n2}", v1/v2))
            candidates.append((f"{n1}+{n2}", v1+v2))
            candidates.append((f"{n1}-{n2}", v1-v2))
    
    # Level 3: Products of gamma with structural numbers
    for g_name in ["g1", "g7", "g20", "g22", "g33"]:
        g = constants[g_name]
        for s_name, s_val in K:
            if s_val > 0 and s_val not in [0, 1]:
                candidates.append((f"{g_name}*{s_name}", g*s_val))
                candidates.append((f"{s_name}*{g_name}", s_val*g))
    
    # Level 4: Composite expressions
    c = constants
    # Nd + 2B = 52
    candidates.append(("Nd+2B", c["Nd"] + 2*c["B"]))
    # Nd - 2B = 36
    candidates.append(("Nd-2B", c["Nd"] - 2*c["B"]))
    # 88 = 2Nd
    candidates.append(("2Nd", 2*c["Nd"]))
    # 14 = 2L4
    candidates.append(("2L4", 2*c["L4"]))
    # 1232 = 88*14
    candidates.append(("2Nd*2L4", 2*c["Nd"] * 2*c["L4"]))
    # 2B^2 = 32
    candidates.append(("2B^2", 2*c["B"]**2))
    
    # Level 5: gamma_n * (Nd - k) expressions
    for g_name in ["g1", "g7", "g20", "g33"]:
        g = constants[g_name]
        for k in range(1, 45):
            expr = f"{g_name}*(Nd-{k})"
            val = g * (c["Nd"] - k)
            candidates.append((expr, val))
            expr2 = f"(Nd-{k})*{g_name}"
            candidates.append((expr2, val))
    
    # Level 6: 1232 * (1 + gamma_n) expressions
    for g_name in ["g1", "g7", "g20", "g33", "g22"]:
        g = constants[g_name]
        for k in [1, 2, 3, 4, 5, 7, 8, 11, 13, 21, 29, 33, 40, 44]:
            expr = f"1232*(1+{k}*{g_name})"
            val = 1232 * (1 + k * g)
            candidates.append((expr, val))
            expr2 = f"1232*(1+{g_name}*{k})"
            candidates.append((expr2, val))
    
    # Level 7: Nd - 2 - gamma_ratio
    for g_num in ["g1", "g7", "g20", "g33"]:
        for g_den in ["g1", "g7", "g20", "g33", "g22"]:
            if g_num != g_den:
                r = constants[g_num] / constants[g_den]
                for k in [0, 1, 2, 3, 4, 5, 7, 8]:
                    expr = f"Nd-{k}-{g_num}/{g_den}"
                    val = c["Nd"] - k - r
                    candidates.append((expr, val))
    
    # Level 8: lambda_max * (Nd - k - gamma_ratio)
    lam = targets["lam_max_35.4178"]
    for k in [0, 1, 2, 3, 4, 5]:
        for g_num in ["g1", "g7", "g20", "g33"]:
            for g_den in ["g1", "g7", "g20", "g33", "g22"]:
                if g_num != g_den:
                    r = constants[g_num] / constants[g_den]
                    expr = f"lam_max*(Nd-{k}-{g_num}/{g_den})"
                    val = lam * (c["Nd"] - k - r)
                    candidates.append((expr, val))
    
    return candidates

# ============ SEARCH ============
print("=" * 72)
print("STRUCTURAL IDENTITY SEARCH FOR 1482.84 AND 2.3474")
print("=" * 72)

all_candidates = generate_expressions()
print(f"Total candidates: {len(all_candidates)}")

for target_name, target_val in targets.items():
    print(f"\n{'='*72}")
    print(f"SEARCHING FOR: {target_name} = {target_val}")
    print(f"{'='*72}")
    
    best = []
    for expr, val in all_candidates:
        if val == 0:
            continue
        err = abs(val - target_val) / target_val * 100
        if err < 1.0:  # < 1% threshold
            best.append((err, expr, val))
    
    best.sort(key=lambda x: x[0])
    print(f"  Best matches (< 1% error):")
    for err, expr, val in best[:20]:
        star = "★" if err < 0.1 else " "
        print(f"  {star} {err:.4f}%  |  {expr} = {val:.10f}")

# ============ DEEP DIVE: v_geom factor ============
print("\n" + "=" * 72)
print("DEEP DIVE: v_geom factor 1482.84")
print("=" * 72)

c = constants
lam_max = targets["lam_max_35.4178"]
v_ew = c["v_ew"]
M0 = c["M0"]

# The formula: v_geom = sqrt(lambda_max) * M0 * factor
# factor = v_geom / (sqrt(lambda_max) * M0)
factor = v_ew / (math.sqrt(lam_max) * M0)
print(f"  v_geom = {v_ew} MeV")
print(f"  lambda_max = {lam_max}")
print(f"  sqrt(lambda_max) * M0 = {math.sqrt(lam_max) * M0:.4f} MeV")
print(f"  factor = {factor:.6f}")

# Check: 1232 = 2Nd * 2L4
print(f"\n  1232 = 2Nd * 2L4 = {2*c['Nd']} * {2*c['L4']} = {2*c['Nd']*2*c['L4']}")
print(f"  factor/1232 = {factor/1232:.6f}")

# Check factor decomposition
print(f"\n  Factor decomposition:")
print(f"  factor / 88 = {factor/88:.6f} = 2Nd")
print(f"  factor / 44 = {factor/44:.6f} = Nd")
print(f"  factor / 14 = {factor/14:.6f} = 2L4")
print(f"  factor / 7 = {factor/7:.6f} = L4")
print(f"  factor / 29 = {factor/29:.6f} = L7")
print(f"  factor / 33 = {factor/33:.6f} = Ktree")
print(f"  factor / 11 = {factor/11:.6f} = L5")
print(f"  factor / 4 = {factor/4:.6f} = B")

# Check: 1482.84 = 1232 * (1 + 40*g1)
g1 = c["g1"]
print(f"\n  1232*(1+40*g1) = 1232*(1+{40}*{g1:.6f}) = {1232*(1+40*g1):.4f}")
print(f"  Error: {abs(1232*(1+40*g1)-factor)/factor*100:.4f}%")
print(f"  40 = Nd - B = {c['Nd']} - {c['B']} = {c['Nd']-c['B']}")

# Check: 1482.84 = 1232 * (1 + (Nd-B) * g1)
print(f"\n  1232*(1+(Nd-B)*g1) = 1232*(1+{c['Nd']-c['B']}*{g1:.6f}) = {1232*(1+(c['Nd']-c['B'])*g1):.4f}")
print(f"  Error: {abs(1232*(1+(c['Nd']-c['B'])*g1)-factor)/factor*100:.4f}%")

# Try: 1482.84 = 88 * 44 / phi^2 * (1 + something)
print(f"\n  88*44/phi^2 = {88*44/phi**2:.4f}")
print(f"  factor - 88*44/phi^2 = {factor - 88*44/phi**2:.4f}")

# Try: 1482.84 = 44 * 33.70
# 33.70 = ?
print(f"\n  factor/44 = {factor/44:.4f}")
print(f"  factor/44 - 33 = {factor/44 - 33:.4f}")
print(f"  factor/44 - 29 = {factor/44 - 29:.4f}")
print(f"  factor/44 - 7 = {factor/44 - 7:.4f}")

# ============ DEEP DIVE: lambda_2nd = 2.3474 ============
print("\n" + "=" * 72)
print("DEEP DIVE: lambda_2nd = 2.34737")
print("=" * 72)

lam2 = targets["lam2_2.3474"]

# Check gamma_n relationships
print(f"  gamma_7 = {c['g7']:.6f}")
print(f"  gamma_20 = {c['g20']:.6f}")
print(f"  gamma_33 = {c['g33']:.6f}")
print(f"  gamma_22 = {c['g22']:.6f}")

# Check: 2.3474 = gamma_7 * 9.595? 
print(f"\n  lam2/g7 = {lam2/c['g7']:.6f}")
print(f"  lam2/g20 = {lam2/c['g20']:.6f}")
print(f"  lam2/g33 = {lam2/c['g33']:.6f}")

# Check special gamma ratios
print(f"\n  g7/g20 = {c['g7']/c['g20']:.6f}")
print(f"  g20/g7 = {c['g20']/c['g7']:.6f}")
print(f"  g33/g7 = {c['g33']/c['g7']:.6f}")
print(f"  g20/g33 = {c['g20']/c['g33']:.6f}")

# Check: lam2 = Nd - g20/g7? No
print(f"\n  Nd - g20/g7 = {c['Nd'] - c['g20']/c['g7']:.6f}")
print(f"  Nd - g7/g20 = {c['Nd'] - c['g7']/c['g20']:.6f}")
print(f"  Nd - g33/g7 = {c['Nd'] - c['g33']/c['g7']:.6f}")

# Check: lam2 = gamma_7 * 10 - something?
print(f"\n  10*g7 = {10*c['g7']:.6f}")
print(f"  10*g7 - lam2 = {10*c['g7'] - lam2:.6f}")
print(f"  g7*L5 = {c['g7']*c['L5']:.6f}")
print(f"  g7*L5 - lam2 = {c['g7']*c['L5'] - lam2:.6f}")

# Check: lam2 = gamma_20 * phi?
print(f"\n  g20*phi = {c['g20']*phi:.6f}")
print(f"  g20*phi_inv = {c['g20']*phi**(-1):.6f}")
print(f"  g20*phi - lam2 = {c['g20']*phi - lam2:.6f}")

# Check: lam2 = 2 + something?
print(f"\n  lam2 - 2 = {lam2 - 2:.6f}")
print(f"  lam2 - 1 = {lam2 - 1:.6f}")
print(f"  lam2 - g22 = {lam2 - c['g22']:.6f}")

# Check: lam2 = 1/gamma_1 * something?
print(f"\n  1/g1 = {1/c['g1']:.4f}")
print(f"  lam2 * 1/g1 = {lam2/c['g1']:.4f}")
print(f"  lam2 * 1/g1 / 84 = {lam2/c['g1']/84:.4f}")
print(f"  84 = ?")

# ============ SUMMARY ============
print("\n" + "=" * 72)
print("BEST CANDIDATES SUMMARY")
print("=" * 72)

print(f"""
  FACTOR 1482.84:
  ★ 1232 × (1 + (Nd-B)×g1) = 1232 × (1 + 40×{c['g1']:.6f})
    = {1232*(1+(c['Nd']-c['B'])*c['g1']):.4f}
    Error: {abs(1232*(1+(c['Nd']-c['B'])*c['g1'])-factor)/factor*100:.4f}%
    [40 = Nd - B = 44 - 4]
  
  LAMBDA_2ND 2.34737:
  Check: g7 × L5 = {c['g7']*c['L5']:.6f}
  Check: g7 × 10 - {10*c['g7'] - lam2:.4f}
  Check: g20 × phi_inv = {c['g20']*phi**(-1):.6f}
  Check: lam2 - 2 = {lam2-2:.6f}
  Check: 1/g1 = {1/c['g1']:.4f}
""")

print("=" * 72)
print("SEARCH COMPLETE")
print("=" * 72)