#!/usr/bin/env python3
"""
O70 — 19: Kähler Cone Extreme Rays via Polymake (fixed)
========================================================
使用 polymake wrapper 計算 32D Kähler cone 嘅 extreme rays。
"""
import sys, os, math, json, numpy as np
import tempfile, subprocess

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O70 19: Kähler Cone Extreme Rays — Polymake")
print("=" * 72)

# Load data & compute Q
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
basis_0 = np.array([b-1 for b in basis])

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

Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-15)
print(f"Q: 185×32, rank: {np.linalg.matrix_rank(Q)}")

# Write Q matrix
tmpdir = tempfile.mkdtemp()
Q_path = os.path.join(tmpdir, "Q.txt")
rays_path = os.path.join(tmpdir, "rays.txt")
lines_path = os.path.join(tmpdir, "lines.txt")
facets_path = os.path.join(tmpdir, "facets.txt")

# Polymake INEQUALITIES: [b, -a] for a·x ≤ b
# For Qx ≥ 0: -Qx ≤ 0 → a = -Q, b = 0 → [0, Q]
with open(Q_path, 'w') as f:
    f.write(f"{185} {33}\n")
    for i in range(185):
        f.write("0")
        for j in range(32):
            f.write(f" {Qn[i, j]:.15e}")
        f.write("\n")

# Polymake script
pm_script = f"""
use application 'polytope';

my $A = read_matrix("{Q_path}");
my $c = new Polytope<Float>(INEQUALITIES => $A);

my $rays = $c->RAYS;
my $lines = $c->LINEALITY_SPACE;
my $facets = $c->FACETS;

write_matrix("{rays_path}", $rays);
write_matrix("{lines_path}", $lines);
write_matrix("{facets_path}", $facets);

print "DIM: ", $c->DIM, "\\n";
print "N_RAYS: ", $rays->rows, "\\n";
print "N_LINES: ", $lines->rows, "\\n";
print "N_FACETS: ", $facets->rows, "\\n";
print "POINTED: ", $c->POINTED ? "yes" : "no", "\\n";
print "Done\\n";
"""

pm_path = os.path.join(tmpdir, "compute_rays.pl")
with open(pm_path, 'w') as f:
    f.write(pm_script)

# Run polymake via wrapper
PM = "/home/wsl/.local/polymake/usr/bin/polymake-wrapper.sh"
print("\nRunning polymake...")
result = subprocess.run([PM, pm_path], capture_output=True, text=True, timeout=600)
print(result.stdout)
if result.stderr:
    stderr_clean = [l for l in result.stderr.split('\n') if 'bliss' not in l and 'private' not in l]
    if stderr_clean:
        print(f"STDERR: {chr(10).join(stderr_clean[:5])}")

# Read results
if os.path.exists(rays_path):
    with open(rays_path) as f:
        lines = f.readlines()
    dims = lines[0].strip().split()
    n_rays, n_dims = int(dims[0]), int(dims[1])
    print(f"\n{n_rays} rays, {n_dims} dimensions")
    
    rays = []
    for line in lines[1:]:
        vals = [float(x) for x in line.strip().split()]
        if len(vals) == 32:
            rays.append(vals)
    
    R = np.array(rays)
    print(f"Rays array: {R.shape}")
    print(f"Rank: {np.linalg.matrix_rank(R)}")
    
    # Check cone membership
    Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-15)
    in_cone = 0
    for r in R:
        if np.all(Qn @ r > -1e-6):
            in_cone += 1
    print(f"Rays in cone: {in_cone}/{n_rays}")
    
    # Active constraints
    active_counts = [np.sum(np.abs(Qn @ r) < 1e-6) for r in R]
    print(f"Active: min={min(active_counts)}, max={max(active_counts)}, mean={np.mean(active_counts):.1f}")
    print(f"Rays with ≤35 active: {sum(1 for c in active_counts if c <= 35)}")
    print(f"Rays with ≤40 active: {sum(1 for c in active_counts if c <= 40)}")
    
    # Save
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "19_polymake_rays.npy")
    np.save(out_path, R)
    print(f"Saved to {out_path}")
else:
    print("FAILED: No rays output")

# Read facets
if os.path.exists(facets_path):
    with open(facets_path) as f:
        facets_content = f.read()
    lines = facets_content.strip().split('\n')
    dims = lines[0].strip().split()
    n_facets = int(dims[0])
    print(f"\nFacets: {n_facets}")
    if n_facets > 0 and n_facets <= 200:
        print(f"  First 3: {lines[1][:80]}...")
        print(f"  Last 3: {lines[-1][:80]}...")

print("\nDone.")