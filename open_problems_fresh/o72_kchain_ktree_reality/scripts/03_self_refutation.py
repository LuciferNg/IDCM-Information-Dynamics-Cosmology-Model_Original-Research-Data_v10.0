"""
O72 自我質疑 01: K_Chain 核心數字係咪平凡恆等式? (唔係 44 特有)
=====================================================================
動機: 用戶指示 — 「呢個 session 重點係自我質疑, 唔係自我解釋。
      無需要搵路自圓其說, 可以用任何方向質疑 IDCM 及驗證其存在性。」

質疑假說 (要測試嘅):
  H1: 「Σγ(44-site) = 90」對任何 N-site 鏈都成立 (半譜和 = 2N+2)?
  H2: 「Σγ_odd = 88, Σγ_even = 90」對任何 N-site 鏈都成立 (Σ_odd=N, Σ_even=N+2)?
  H3: 946 拍頻「可分離性」= sin² 譜嘅恆等式 (差頻自動 = sin×sin)?
  H4: 946 = C(44,2) 只係平凡組合數?
  H5: λ_sync 定義有 circularity (44 = πR_H/λ_sync 係恆等式)?

如果 H1-H5 全中 → K_Chain 核心數字唔係「結構發現」,
   而係任何 ring Laplacian 都有嘅平凡數學 → 44 冇特殊性 → 存在性受重大質疑

驗證方法: 對 N = 30..60 掃描, 睇恆等式係咪對所有 N 成立 (N=44 冇特殊性)
"""
import numpy as np

print("=" * 72)
print("H1: 半譜和 Σ_{k=1..N} 4sin²(πk/2N) = 2N+2 對所有 N?")
print("=" * 72)
violations = 0
for N in range(30, 61):
    k = np.arange(1, N + 1)
    gamma = 4.0 * np.sin(np.pi * k / (2 * N)) ** 2
    S = gamma.sum()
    pred = 2 * N + 2
    if abs(S - pred) > 1e-9:
        violations += 1
        print(f"  N={N}: Σ={S:.6f} ≠ 2N+2={pred}  ❌")
print(f"  結果: N=30..60, {60-30+1-violations}/{60-30+1} 符合 2N+2")
print(f"  → N=44 冇特殊性: Σγ=90 只係 2×44+2 嘅必然結果")
print(f"  → 「90」唔係結構發現, 係 Laplacian 半譜恆等式\n")

print("=" * 72)
print("H2: Σγ_odd = N, Σγ_even = N+2 對所有偶數 N?")
print("=" * 72)
violations = 0
for N in range(30, 61, 2):
    k = np.arange(1, N + 1)
    gamma = 4.0 * np.sin(np.pi * k / (2 * N)) ** 2
    S_odd = gamma[0::2].sum()   # k=1,3,...,N-1
    S_even = gamma[1::2].sum()  # k=2,4,...,N
    if abs(S_odd - N) > 1e-9 or abs(S_even - (N + 2)) > 1e-9:
        violations += 1
        print(f"  N={N}: odd={S_odd:.6f}(≠N) even={S_even:.6f}(≠N+2)  ❌")
print(f"  結果: 所有偶數 N ∈ [30,60] 都係 Σγ_odd=N, Σγ_even=N+2")
print(f"  → 「88=觀察者, 90=世界」只係 N=88 時嘅 88=N, 90=N+2 — 平凡!")
print(f"  → 世界/觀察者分裂冇 44/88 特殊性\n")

print("=" * 72)
print("H3: 拍頻可分離性 = sin² 譜恆等式 (任何 M)")
print("=" * 72)
# 恆等式: sin²A - sin²B = sin(A+B)·sin(A-B)
# γ_a - γ_b = 4sin²(πa/2N) - 4sin²(πb/2N) = 4sin((a+b)π/2N)·sin((a-b)π/2N)
# → 自動係 1D×1D 可分離 (a+b, a-b 各自 1D)!
N = 44
ok = True
for a in range(1, N):
    for b in range(a + 1, N + 1):
        lhs = 4*np.sin(np.pi*a/(2*N))**2 - 4*np.sin(np.pi*b/(2*N))**2
        rhs = 4*np.sin((a+b)*np.pi/(2*N)) * np.sin((a-b)*np.pi/(2*N))
        if abs(lhs - rhs) > 1e-12:
            ok = False
print(f"  sin²A - sin²B = sin(A+B)sin(A-B) 對全部 {N*(N-1)//2} 對成立: {ok}")
print(f"  → 「946 可分離三角表」係 sin² 譜嘅代數恆等式, 唔係發現")
print(f"  → B(d,s) = 4sin(dπ/176)cos(sπ/176) 形式係必然 (和差化積)\n")

print("=" * 72)
print("H4: 946 = C(44,2) 平凡組合數")
print("=" * 72)
print(f"  C(44,2) = {44*43//2} — 任何 44 元素集合都有 946 個 pair")
print(f"  → 「946 個拍頻」只係「44 個模式嘅差頻數」— 平凡\n")

print("=" * 72)
print("H5: λ_sync / 44 circularity")
print("=" * 72)
H0 = 72.59
c = 299792.458
R_H = c / H0          # Mpc
T_sync = 2*np.pi / H0 * 3.085677581e19 / 3.15576e16  # Gyr (2π/H₀)
lam_sync = c * (T_sync * 3.15576e16) / (88 * 3.085677581e19)  # Mpc
print(f"  R_H = {R_H:.2f} Mpc (輸入: H₀)")
print(f"  λ_sync = c·T_sync/88 = {lam_sync:.2f} Mpc (定義: 用 88)")
print(f"  πR_H/λ_sync = {np.pi*R_H/lam_sync:.4f} (應該 = 44 = 88/2)")
print(f"  → 44 = πR_H/λ_sync 係 λ_sync 定義嘅恆等式, 唔係推導")
print(f"  → 44 同 88 係輸入選擇, 冇獨立推導\n")

print("=" * 72)
print("總結: 自我質疑發現")
print("=" * 72)
print("""
🔴 重大發現: K_Chain 嘅「結構閉合數字」全部係平凡數學:
   [1] Σγ = 2N+2 對任何 N (90 只係 2×44+2)
   [2] Σγ_odd = N, Σγ_even = N+2 對任何偶數 N (88/90 冇特殊性)
   [3] 拍頻可分離性 = sin²A - sin²B = sin(A+B)sin(A-B) 恆等式
   [4] 946 = C(44,2) 平凡組合數
   [5] 44 = πR_H/λ_sync 係定義恆等式 (44/88 係輸入, 唔係推導)

→ K_Chain 存在性受重大質疑: 核心數字冇一個證明 44/88 係必要
→ 「世界/觀察者 90/88 分裂」係任何偶數 N-ring 都有嘅性質

🟡 仍然未質疑倒嘅 (K_Chain 可能仍然有特殊性):
   - 點解宇宙要係 44-site (N=44) 而唔係 N=43 或 N=45?
     → 呢個先係真正嘅開放問題 (但 90/88/946 唔係證據)
   - R_H = c/H₀ 作為環周長: 點解係 Hubble 半徑?
   - 88-site 對偶鏈 (N=88) 嘅觀測對應 (λ_sync, BAO)?
""")
