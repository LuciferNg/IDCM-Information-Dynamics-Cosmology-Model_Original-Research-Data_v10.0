#!/usr/bin/env python3
"""
O137 Phase 7 — CY₃ 拓撲分層上的 2-adic 共振
============================================
Project 2-adic K_Chain structure onto the 4 φ-subspaces (28/9/5/2).

The hypothesis: mode selection {1,7,33} vs {15,21,25,35}
comes from a 2-adic conservation law across the 4 φ-groups.
"""

import json, os
from math import exp, pi, sin, cos, gcd
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

print("=" * 72)
print("O137 Phase 7 — CY₃ × 2-adic Resonance")
print("=" * 72)

# === Load φ data ===
with open("data/dual_triangulation_data.json") as f:
    tri = json.load(f)
phi = tri["gkz_phi"]

# φ≤12 indices and values
phi_le12 = [(i, v) for i, v in enumerate(phi) if v <= 12]
phi_le12_sorted = sorted(phi_le12, key=lambda x: x[0])

# Group by φ value
phi_groups = {}
for i, v in phi_le12:
    phi_groups.setdefault(v, []).append(i)

print(f"\n★ 44 φ≤12 points = N_d = 44")
for v in sorted(phi_groups.keys(), reverse=True):
    pts = phi_groups[v]
    print(f"   φ={v}: {len(pts)} pts, labels={pts}")

# === K_Chain site properties ===
print("\n" + "=" * 72)
print("K_Chain site properties (a=1..44)")
print("=" * 72)

def v2(x):
    """2-adic valuation"""
    if x == 0:
        return float('inf')
    c = 0
    while x % 2 == 0:
        x //= 2
        c += 1
    return c

def gamma_a(a):
    return 4 * sin(a * pi / 88) ** 2

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# Lucas numbers up to 44
def lucas(n):
    if n == 0: return 2
    if n == 1: return 1
    a, b = 2, 1
    for _ in range(2, n+1):
        a, b = b, a + b
    return b

lucas_vals = set(lucas(i) for i in range(1, 20) if lucas(i) <= 44)
fib_vals = set()
a, b = 1, 1
while a <= 44:
    fib_vals.add(a)
    a, b = b, a + b

print(f"  Lucas ≤ 44: {sorted(lucas_vals)}")
print(f"  Fibonacci ≤ 44: {sorted(fib_vals)}")
print(f"  Prime ≤ 44: {sorted([a for a in range(1, 45) if is_prime(a)])}")

# === Candidate mappings from K_Chain sites to φ groups ===
print("\n" + "=" * 72)
print("Candidate mappings: K_Chain sites → φ groups")
print("=" * 72)

ALLOWED = {1, 7, 33}
EXCLUDED = {15, 21, 25, 35}

def compute_v2_sum_for_mapping(mapping, mode_set):
    """
    For a given mapping {site: φ_group}, compute 2-adic phase sums.
    """
    # Group sites by φ value
    groups = {6: [], 8: [], 9: [], 12: []}
    for site, phi_val in mapping.items():
        if phi_val in groups:
            groups[phi_val].append(site)
    
    results = {}
    for n in mode_set:
        totals = {}
        for phi_val, sites in groups.items():
            # 2-adic depth: v₂(88/gcd(n·a, 88))
            total_depth = 0
            for a in sites:
                g = gcd(n * a, 88)
                depth = v2(88 // g)
                total_depth += depth
            totals[phi_val] = total_depth
        results[n] = totals
    return results, groups

# Map 1: Sort φ≤12 labels, assign to K_Chain sites 1..44 in order
sorted_labels = sorted(phi_le12, key=lambda x: x[0])
mapping_sorted = {a+1: v for a, (idx, v) in enumerate(sorted_labels)}
print(f"\nMap 1: Labels sorted → K_Chain 1..44")
print(f"  φ=6: {sorted([a for a, v in mapping_sorted.items() if v == 6])}")
print(f"  φ=8: {sorted([a for a, v in mapping_sorted.items() if v == 8])}")
print(f"  φ=9: {sorted([a for a, v in mapping_sorted.items() if v == 9])}")
print(f"  φ=12: {sorted([a for a, v in mapping_sorted.items() if v == 12])}")

# Map 2: Sort φ≤12 labels by φ value, then by label — assign to K_Chain 1..44
sorted_by_phi = sorted(phi_le12, key=lambda x: (x[1], x[0]))
mapping_phi = {a+1: v for a, (idx, v) in enumerate(sorted_by_phi)}
print(f"\nMap 2: Sorted by φ value → K_Chain 1..44")
print(f"  φ=6: {sorted([a for a, v in mapping_phi.items() if v == 6])}")
print(f"  φ=8: {sorted([a for a, v in mapping_phi.items() if v == 8])}")
print(f"  φ=9: {sorted([a for a, v in mapping_phi.items() if v == 9])}")
print(f"  φ=12: {sorted([a for a, v in mapping_phi.items() if v == 12])}")

# Map 3: v₂-based natural mapping
# φ=8 → v₂≥3 (5 bosons), φ=6 → integer γ sites {22,44}, φ=9 → ? 
# Let's try: φ=9 → the 9 sites with v₂=0 and a≡1 mod 4? No that's 11.
# Let's try: the 9 smallest odd sites {1,3,5,7,9,11,13,15,17}
# φ=12 → the rest
mapping_v2 = {}
all_sites = list(range(1, 45))

# φ=8: v₂≥3
phi8_sites = [a for a in all_sites if v2(a) >= 3]
# φ=6: integer γ (a=22, 44)
phi6_sites = [22, 44]
# φ=9: try the 9 sites with smallest γ_a that are odd
# γ_a increases with a, so the smallest odd sites are 1,3,5,7,9,11,13,15,17
phi9_sites = list(range(1, 19, 2))  # 1,3,5,7,9,11,13,15,17
# φ=12: the rest
phi12_sites = [a for a in all_sites if a not in phi8_sites + phi6_sites + phi9_sites]

for a in all_sites:
    if a in phi8_sites: mapping_v2[a] = 8
    elif a in phi6_sites: mapping_v2[a] = 6
    elif a in phi9_sites: mapping_v2[a] = 9
    else: mapping_v2[a] = 12

print(f"\nMap 3: v₂-based natural mapping")
print(f"  φ=8 (v₂≥3, 5 bosons): {phi8_sites}")
print(f"  φ=6 (integer γ, 2 sites): {phi6_sites}")
print(f"  φ=9 (smallest odd, 9 sites): {phi9_sites}")
print(f"  φ=12 (rest, 28 sites): {phi12_sites}")

# Map 4: v₂-based alternative
# φ=8 → v₂≥3 (5 bosons)
# φ=6 → {22, 44} (integer γ)
# φ=9 → the 9 Lucas+Fibonacci sites (union)
# φ=12 → the rest
lucas_fib = lucas_vals | fib_vals
phi9_sites_v4 = sorted([a for a in lucas_fib if a <= 44 and a not in phi8_sites and a not in phi6_sites])
# Take first 9
phi9_sites_v4 = phi9_sites_v4[:9] if len(phi9_sites_v4) >= 9 else phi9_sites_v4 + sorted([a for a in range(1, 45) if a not in phi8_sites + phi6_sites + phi9_sites_v4])[:9-len(phi9_sites_v4)]
phi12_sites_v4 = [a for a in all_sites if a not in phi8_sites + phi6_sites + phi9_sites_v4]

mapping_v4 = {}
for a in all_sites:
    if a in phi8_sites: mapping_v4[a] = 8
    elif a in phi6_sites: mapping_v4[a] = 6
    elif a in phi9_sites_v4: mapping_v4[a] = 9
    else: mapping_v4[a] = 12

print(f"\nMap 4: Lucas+Fibonacci φ=9")
print(f"  φ=9 (Lucas+Fibonacci): {phi9_sites_v4}")
print(f"  φ=12 (rest): {phi12_sites_v4}")

# Map 5: The 9 sites with a ≡ 33..41 (high modes)
# φ=8 → v₂≥3 (5 bosons)
# φ=6 → {22, 44} (integer γ)
# φ=9 → a = 33..41 (high modes, 9 sites)
# φ=12 → the rest
phi9_sites_v5 = list(range(33, 42))  # 33,34,35,36,37,38,39,40,41
phi12_sites_v5 = [a for a in all_sites if a not in phi8_sites + phi6_sites + phi9_sites_v5]

mapping_v5 = {}
for a in all_sites:
    if a in phi8_sites: mapping_v5[a] = 8
    elif a in phi6_sites: mapping_v5[a] = 6
    elif a in phi9_sites_v5: mapping_v5[a] = 9
    else: mapping_v5[a] = 12

print(f"\nMap 5: High modes φ=9 (a=33..41)")
print(f"  φ=9: {phi9_sites_v5}")
print(f"  φ=12: {phi12_sites_v5}")

# Map 6: φ=9 = sites with a ≡ 1 mod 4 (the "odd-odd" sites, 11 sites)
# But we need exactly 9, so take first 9
# φ=8 → v₂≥3 (5 bosons)
# φ=6 → {22, 44} (integer γ)
# φ=9 → a ≡ 1 mod 4, first 9
odd_odd = [a for a in range(1, 45, 4)]  # 1,5,9,13,17,21,25,29,33,37,41 = 11
phi9_sites_v6 = odd_odd[:9]  # 1,5,9,13,17,21,25,29,33
phi12_sites_v6 = [a for a in all_sites if a not in phi8_sites + phi6_sites + phi9_sites_v6]

mapping_v6 = {}
for a in all_sites:
    if a in phi8_sites: mapping_v6[a] = 8
    elif a in phi6_sites: mapping_v6[a] = 6
    elif a in phi9_sites_v6: mapping_v6[a] = 9
    else: mapping_v6[a] = 12

print(f"\nMap 6: a≡1 mod 4 φ=9 (first 9)")
print(f"  φ=9: {phi9_sites_v6}")
print(f"  φ=12: {phi12_sites_v6}")

# === Compute 2-adic phase sums for each mapping ===
print("\n" + "=" * 72)
print("2-adic Phase Sums for each mapping")
print("=" * 72)

test_modes = [1, 7, 11, 15, 21, 25, 33, 35, 43]

mappings = {
    "Map1_sorted": mapping_sorted,
    "Map2_phi_sorted": mapping_phi,
    "Map3_v2_natural": mapping_v2,
    "Map4_lucas_fib": mapping_v4,
    "Map5_high": mapping_v5,
    "Map6_odd1mod4": mapping_v6,
}

for map_name, mapping in mappings.items():
    print(f"\n--- {map_name} ---")
    groups = {6: [], 8: [], 9: [], 12: []}
    for site, phi_val in mapping.items():
        if phi_val in groups:
            groups[phi_val].append(site)
    
    # Verify group sizes
    sizes = {k: len(v) for k, v in groups.items()}
    print(f"  Group sizes: {sizes} (total={sum(sizes.values())})")
    
    # Compute 2-adic depth sums
    print(f"  {'Mode':>4} | ", end="")
    for phi_val in [6, 8, 9, 12]:
        print(f"φ={phi_val}_sum | ", end="")
    print("Signature")
    print(f"  {'-'*4} | " + "-"*10*4 + "----------")
    
    for n in test_modes:
        totals = {}
        for phi_val in [6, 8, 9, 12]:
            total = 0
            for a in groups[phi_val]:
                g = gcd(n * a, 88)
                depth = v2(88 // g)
                total += depth
            totals[phi_val] = total
        
        sig = tuple(totals[v] for v in [6, 8, 9, 12])
        marker = " ◀" if n in ALLOWED else ""
        print(f"  {n:>4} | {totals[6]:>8} | {totals[8]:>8} | {totals[9]:>8} | {totals[12]:>8} | {sig}{marker}")

# === Alternative: 2-adic weighted sum with phase ===
print("\n" + "=" * 72)
print("Alternative: Complex 2-adic impedance Z(n)")
print("Z(n) = Σ_a exp(2πi·n·a/88) · v₂(a)")
print("=" * 72)

for map_name, mapping in mappings.items():
    print(f"\n--- {map_name} ---")
    groups = {6: [], 8: [], 9: [], 12: []}
    for site, phi_val in mapping.items():
        if phi_val in groups:
            groups[phi_val].append(site)
    
    print(f"  {'Mode':>4} | ", end="")
    for phi_val in [6, 8, 9, 12]:
        print(f"Re(φ={phi_val}) | Im(φ={phi_val}) | ", end="")
    print("Signature")
    print(f"  {'-'*4} | " + "-"*12*4 + "----")
    
    for n in test_modes:
        targets = {}
        for phi_val in [6, 8, 9, 12]:
            z_re = 0.0
            z_im = 0.0
            for a in groups[phi_val]:
                theta = 2 * pi * n * a / 88
                z_re += cos(theta) * v2(a)
                z_im += sin(theta) * v2(a)
            targets[phi_val] = (z_re, z_im)
        
        sig = tuple((round(targets[v][0], 4), round(targets[v][1], 4)) for v in [6, 8, 9, 12])
        marker = " ◀" if n in ALLOWED else ""
        print(f"  {n:>4} | ", end="")
        for phi_val in [6, 8, 9, 12]:
            re, im = targets[phi_val]
            print(f"{re:>+6.2f} | {im:>+6.2f} | ", end="")
        print(f"  {marker}")

# === Summary ===
print("\n" + "=" * 72)
print("PHASE 7 SUMMARY")
print("=" * 72)
print("""
Phase 7 tests the hypothesis that the 2-adic structure of the K_Chain,
when projected onto the 4 φ-subspaces (28/9/5/2), gives a unique
conservation law for {1,7,33} vs {15,21,25,35}.

The key question is the CORRECT mapping from K_Chain sites a=1..44
to the 4 φ-groups. Six candidate mappings are tested.

Critical insight: the 2-adic depth d(n,a) = v₂(88/gcd(n·a,88))
is independent of n for odd modes when v₂(a) ≤ 2. This suggests
the 2-adic resonance is not in the simple depth sum, but in the
complex phase-weighted impedance.
""")