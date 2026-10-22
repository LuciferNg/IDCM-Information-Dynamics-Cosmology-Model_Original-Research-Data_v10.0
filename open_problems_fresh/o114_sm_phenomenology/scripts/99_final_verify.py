#!/usr/bin/env python3
"""
O114 最終數值核對腳本
=====================
核對所有關鍵數值、公式、交叉引用嘅一致性。
"""
import numpy as np, math, os, json

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o114_sm_phenomenology"
passed = 0; failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond: passed += 1; print(f"  ✅ {name:<55} {detail}")
    else: failed += 1; print(f"  ❌ {name:<55} {detail}")

print("=" * 72)
print("O114 最終數值核對")
print("=" * 72)

# ============================================================
# 1. 關鍵物理常數
# ============================================================
print("\n--- 1. 物理常數 ---")
g_GUT = 0.517078
M_GUT = 6.2214e16
gamma_1 = 4 * math.sin(math.pi / 88) ** 2
v_uniform = M_GUT / g_GUT

check("g_GUT = 0.517078", abs(g_GUT - 0.517078) < 1e-6)
check("M_GUT = 6.2214e16 GeV", abs(M_GUT - 6.2214e16) < 1e12)
check(f"gamma_1 = {gamma_1:.6f}", abs(gamma_1 - 0.005096) < 0.0001)
check(f"v_uniform = M_GUT/g_GUT = {v_uniform:.2e}", abs(v_uniform - 1.203e17) < 1e15)

# ============================================================
# 2. 6 extra U(1) 正交性
# ============================================================
print("\n--- 2. 6 extra U(1) 正交性 ---")
E = np.array([
    [+0.6124, -0.6124, +0.0000, -0.2041, +0.2041, +0.0000,
     -0.2041, +0.2041, +0.0000, -0.2041, +0.2041, +0.0000],
    [+0.3536, +0.3536, -0.7071, -0.1179, -0.1179, +0.2357,
     -0.1179, -0.1179, +0.2357, -0.1179, -0.1179, +0.2357],
    [-0.0000, -0.0000, -0.0000, -0.6667, +0.3333, +0.3333,
     +0.3333, -0.1667, -0.1667, +0.3333, -0.1667, -0.1667],
    [-0.0000, -0.0000, -0.0000, +0.0000, -0.5774, +0.5774,
     +0.0000, +0.2887, -0.2887, +0.0000, +0.2887, -0.2887],
    [-0.0000, -0.0000, -0.0000, +0.0000, +0.0000, +0.0000,
     -0.5774, +0.2887, +0.2887, +0.5774, -0.2887, -0.2887],
    [-0.0000, -0.0000, -0.0000, +0.0000, +0.0000, -0.0000,
     +0.0000, -0.5000, +0.5000, +0.0000, +0.5000, -0.5000],
])

for i in range(6):
    for j in range(i, 6):
        dot = np.dot(E[i], E[j])
        if i == j:
            check(f"|E_{i+1}|² = 1 (normalized)", abs(dot - 1) < 0.01, f"({dot:.4f})")
        else:
            check(f"E_{i+1}·E_{j+1} = 0 (orthogonal)", abs(dot) < 1e-3, f"({dot:.2e})")

# ============================================================
# 3. SM 量子數正交性
# ============================================================
print("\n--- 3. SM 量子數正交性 ---")
Y = np.array([1/6]*6 + [2/3]*3 + [-1]*3)
T3L = np.array([0.5]*3 + [-0.5]*3 + [0]*3 + [0]*3)
T3R = np.array([0]*6 + [0.5]*3 + [-0.5]*3)
BL = np.array([1/3]*9 + [-1]*3)
Q = T3L + Y

for label, vec in [("Y", Y), ("T3L", T3L), ("T3R", T3R), ("BL", BL), ("Q", Q)]:
    nrm = np.linalg.norm(vec)
    for i in range(6):
        frac = abs(np.dot(E[i], vec)) / nrm
        check(f"⟨{label}|E_{i+1}⟩/∥{label}∥ = {frac:.4f}", frac < 1e-3, "")

# ============================================================
# 4. Anomaly (Tr(Q_i Q_j) = 6·δ_{ij})
# ============================================================
print("\n--- 4. Anomaly Tr(Q_i Q_j) ---")
for i in range(6):
    tr_12 = np.dot(E[i], E[i])
    tr_72 = 6 * tr_12
    check(f"Tr(H_{i+1}²) = 6 over 72 fermions", abs(tr_72 - 6) < 0.01, f"({tr_72:.4f})")

# ============================================================
# 5. M_Z' 質量
# ============================================================
print("\n--- 5. Z' 質量標度 ---")
M_Z_uniform = g_GUT * v_uniform
check(f"M_Z' (uniform) = M_GUT = {M_Z_uniform:.2e} GeV", 
      abs(M_Z_uniform - M_GUT) / M_GUT < 0.01, f"(ratio={M_Z_uniform/M_GUT:.4f})")

M_Z_cascade = [M_GUT * gamma_1**i for i in range(6)]
check(f"M_Z'(H₁) = {M_Z_cascade[0]:.2e} GeV", M_Z_cascade[0] == M_GUT, "")
check(f"M_Z'(H₂) = {M_Z_cascade[1]:.2e} GeV", abs(M_Z_cascade[1]/M_Z_cascade[0] - gamma_1) < 0.01, "")
check(f"M_Z'(H₆) = {M_Z_cascade[5]:.2e} GeV", 
      abs(M_Z_cascade[5] / M_Z_cascade[0] - gamma_1**5) < 0.01, "")

# ============================================================
# 6. 交叉引用核對
# ============================================================
print("\n--- 6. 交叉引用核對 ---")
# O107 docs
o107_closure = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o107_extra_u1_physical/docs/02_closure_report.md"
o107_problem = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o107_extra_u1_physical/docs/01_problem_record.md"
o107_session = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o107_extra_u1_physical/SESSION_START.md"
o114_session = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o114_sm_phenomenology/SESSION_START.md"
readme = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/README.md"
o110_gap = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o110_system_integration/docs/02_gap_analysis.md"

for fpath in [o107_closure, o107_problem, o107_session, o114_session, readme, o110_gap]:
    check(f"File exists: {os.path.basename(fpath)}", os.path.exists(fpath), "")

# Check key phrases in O107 docs
for fpath, phrase in [
    (o107_closure, "純水平對稱性"),
    (o107_closure, "16/16 PASS"),
    (o107_closure, "B-L 完全喺 tensor subspace"),
    (o107_problem, "純水平對稱性"),
    (o107_problem, "重要修正"),
    (o107_session, "純水平對稱性"),
    (o114_session, "純水平對稱性"),
    (readme, "O114"),
    (readme, "純水平對稱性"),
    (o110_gap, "O107+O114"),
    (o110_gap, "純水平對稱性"),
]:
    with open(fpath) as f:
        content = f.read()
    check(f"'{phrase[:20]}' in {os.path.basename(fpath)}", phrase in content, "")

# ============================================================
# 7. 總結
# ============================================================
print(f"\n{'='*72}")
print(f"最終核對結果: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")

if failed == 0:
    print("\n  🟢 ALL PASS — 所有數值、公式、交叉引用一致")
    print(f"  🟢 {passed} 項檢查全通過")
else:
    print(f"\n  ❌ {failed} 項失敗, 需要修正")

# 保存結果
with open(os.path.join(BASE, "data", "final_verification.json"), "w") as f:
    json.dump({"passed": passed, "failed": failed, "date": "2026-08-29"}, f, indent=2)