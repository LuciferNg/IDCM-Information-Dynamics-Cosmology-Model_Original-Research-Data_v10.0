#!/usr/bin/env python3
"""
O70 — 17: Kähler Cone Extreme Rays via Polymake
=================================================
將 Q 矩陣匯出 → polymake 計算極端射線 → 匯入 Python
"""
import sys, os, math, json, numpy as np
import tempfile, subprocess

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O70 17: Kähler Cone Extreme Rays via Polymake")
print("=" * 72)

# Load data
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])

import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
basis_0 = np.array([b-1 for b in basis])

# Compute Q_ij
t_test = phi ** (-np.arange(36))
t32 = np.array([t_test[b-1] for b in basis])
eps = 1e-5
Q = np.zeros((185, 32))
for j in range(32):
    tp = t32.copy(); tm = t32.copy()
    tp[j] += eps; tm[j] -= eps
    cvp = np.array(cy.compute_curve_volumes(tp))
    cvm = np.array(cy.compute_curve_volumes(tm))
    Q[:, j] = (cvp - cvm) / (2*eps)

print(f"Q: 185×32, rank: {np.linalg.matrix_rank(Q)}")

# Normalize rows for stability
Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-15)

# Write Q matrix to temp file for polymake
tmpdir = tempfile.mkdtemp()
Q_path = os.path.join(tmpdir, "Q.txt")
rays_path = os.path.join(tmpdir, "rays.txt")
lines_path = os.path.join(tmpdir, "lines.txt")

# Write Q as a matrix (185 rows × 33 cols: first col = RHS, rest = coefficients)
# Polymake INEQUALITIES: [b, -a] for a·x ≤ b
# For Qx ≥ 0: -Qx ≤ 0 → a = -Q, b = 0 → [0, -(-Q)] = [0, Q]
# So each row is [0, Q_i1, Q_i2, ..., Q_i32]
with open(Q_path, 'w') as f:
    f.write(f"{185} {33}\n")  # 185 rows, 33 cols (32 + RHS)
    for i in range(185):
        f.write("0")  # RHS = 0
        for j in range(32):
            f.write(f" {Qn[i, j]:.15e}")
        f.write("\n")

print(f"Wrote Q matrix to {Q_path}")

# Polymake script
pm_script = f"""
use application 'polytope';

# Read the inequality matrix
my $A = read_matrix("{Q_path}");

# Create the cone from H-representation
# H-representation: [b, -A] for Ax ≥ b
# Since b = 0 and A = Q, we have: Qx ≥ 0
my $c = new Polytope<Rational>(INEQUALITIES => $A);

# Compute the rays (extreme rays of the cone)
my $rays = $c->RAYS;
my $lines = $c->LINEALITY_SPACE;

# Write to file
write_matrix("{rays_path}", $rays);
write_matrix("{lines_path}", $lines);

print "Done: ", $rays->rows, " rays, ", $c->DIM, " dimensions\\n";
print "Lineality: ", $lines->rows, "\\n";
"""

pm_path = os.path.join(tmpdir, "compute_rays.pl")
with open(pm_path, 'w') as f:
    f.write(pm_script)

# Run polymake
PM_BIN = "/home/wsl/.local/polymake/usr/bin/polymake"
PERL5LIB = "/home/wsl/perl5/lib/perl5:/home/wsl/.local/polymake/usr/share/polymake/perllib:/home/wsl/.local/polymake/usr/lib/polymake/perlx/5.40.0:/home/wsl/.local/polymake/usr/lib/polymake/perlx/5.40.0/x86_64-linux-gnu-thread-multi"

env = os.environ.copy()
env["PERL5LIB"] = PERL5LIB

print("\nRunning polymake...")
result = subprocess.run([PM_BIN, pm_path], env=env, capture_output=True, text=True, timeout=300)
print(result.stdout)
if result.stderr:
    print(f"STDERR: {result.stderr[:500]}")

# Read results
if os.path.exists(rays_path):
    with open(rays_path) as f:
        lines = f.readlines()
    
    # First line: dimensions
    dims = lines[0].strip().split()
    n_rays, n_dims = int(dims[0]), int(dims[1])
    print(f"\n{n_rays} rays, {n_dims} dimensions")
    
    # Parse rays
    rays = []
    for line in lines[1:]:
        vals = [float(x) for x in line.strip().split()]
        if len(vals) == 32:
            rays.append(vals)
    
    R = np.array(rays)
    print(f"Rays array: {R.shape}")
    print(f"Rank: {np.linalg.matrix_rank(R)}")
    
    # Save
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "17_polymake_rays.npy")
    np.save(out_path, R)
    print(f"Saved to {out_path}")
    
    # Check: are all rays in the cone?
    in_cone = 0
    for r in R:
        if np.all(Qn @ r > -1e-6):
            in_cone += 1
    print(f"Rays in cone: {in_cone}/{n_rays}")
    
    # Active constraints per ray
    active_counts = [np.sum(np.abs(Qn @ r) < 1e-6) for r in R]
    print(f"Active: min={min(active_counts)}, max={max(active_counts)}, mean={np.mean(active_counts):.1f}")
else:
    print("FAILED: No rays output")

# Read lineality space
if os.path.exists(lines_path):
    with open(lines_path) as f:
        lines_content = f.read()
    print(f"Lineality space: {lines_content[:200]}")
else:
    print("No lineality space")

print("\nDone.")