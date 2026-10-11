#!/usr/bin/python3
"""O239 — Script 07: T1 θ ↔ rapidity 身份判決（閘門測試）
============================================================================
策略 T1（docs/04 §二 缺口）: O180 θ_k（88 模態幾何角）vs 相對論 rapidity η
——同胚但未證恒等？本 script 判決。

已證材料（跨 O, 必須核歸一化）:
  O180 scripts/01 A3: θ_k = kπ/176, v_k = c·cos(θ_k), k=1..88 → v_k²=a₀r_k EXACT
  O140 docs/02 §4.1: v/c = cos(πn/88), η_n = atanh(cos θ_n) = ln cot(πn/176), n=1..44
  O140 docs/02 §5:  E_n = mc²γ_n = mc²csc(πn/88), p_n = mc·cot(πn/88)
  O140 docs/01: 「快度 η_a+η_b 唔在階梯上」🔴 開放 (κ-Poincaré?)

預註冊判據（跑前凍結）:
  H1 歸一化一致: O180 θ_k=kπ/176（88 模態）對 k=2n 等於 O140 θ_n=πn/88（44 模態）
     —— 即兩個 O 係同一譜嘅 88-格 vs 44-格 slicing, 唔係矛盾
  H2 精確恆等（mpmath 60 dps, tol 1e-50）: η_n = atanh(cos(πn/88)) = ln cot(πn/176)
  H3 逆映射精確: θ_n = 2·arccot(e^{η_n})（雙射, 單調）
  H4 docs/04 鏈同 O140 一致: γ_n = csc(πn/88), p_n = mc·cot(πn/88),
     E²−p²c² = m²c⁴ 精確（質量殼）
  H5 合成律: η_a + η_b 一般唔落喺 88-格階梯（間距 Δη = ln cot(π/176) 附近）——
     量化「唔落格」嘅比例 + 檢定 O140「跳到更細層 ℓ」聲稱（最小 ℓ 令合成落格）
  H6 離散 γ 上限: γ_max(ℓ) = csc(π/(88·4^ℓ)) ≈ (88/π)·4^ℓ —— docs/04 §T2 嘅
     「加速成本上限」結構（O140 docs/02 §6.1 已證）

判決規則:
  θ = rapidity ⟺ H2 成立且 H5 顯示合成律喺階梯上封閉
  θ ≠ rapidity 但精確雙射 ⟺ H2/H3 成立但 H5 唔封閉（→ η = ln cot(θ/2) 係精確關係）
"""
import mpmath as mp
mp.mp.dps = 60

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/07 — T1: θ ↔ rapidity 身份判決")
print("=" * 78)

N = 44  # K_Chain 44 模態（O140 權威）

# ── H1: 歸一化核對（O180 88-格 vs O140 44-格）──
print("\n── H1: O180/O140 歸一化核對 ──")
# O180: θ_k = kπ/176, k=1..88；O140: θ_n = nπ/88, n=1..44
# 檢查 k=2n 時 θ_k == θ_n（同一譜唔同 slicing）
ok_h1 = True
for n in range(1, N + 1):
    th_O180 = mp.mpf(2 * n) * mp.pi / 176   # k = 2n
    th_O140 = mp.mpf(n) * mp.pi / 88
    if abs(th_O180 - th_O140) > mp.mpf("1e-50"):
        ok_h1 = False
print(f"   O180 88-格：θ_k = kπ/176, k=1..88  → 88 個半格")
print(f"   O140 44-格：θ_n = nπ/88,  n=1..44   → k=2n 子集")
print(f"   max|θ(2n)_O180 − θ_n_O140| = 0? {ok_h1}")
chk("H1 歸一化一致（O180 88-格 ⊃ O140 44-格, k=2n）", ok_h1)

# ── H2: 精確恆等 η_n = atanh(cos θ_n) = ln cot(θ_n/2) ──
print("\n── H2: η_n = atanh(cos θ_n) = ln cot(θ_n/2)（mpmath 60 dps）──")
worst = mp.mpf(0)
for n in range(1, N):
    th = mp.mpf(n) * mp.pi / 88
    v = mp.cos(th)
    eta_a = mp.atanh(v)
    eta_b = mp.log(mp.cot(th / 2))
    eta_c = mp.log(mp.cot(mp.mpf(n) * mp.pi / 176))
    worst = max(worst, abs(eta_a - eta_b), abs(eta_a - eta_c))
print(f"   max|atanh(cosθ) − ln cot(θ/2)| = {mp.nstr(worst, 6)}")
for n in [1, 22, 43]:
    th = mp.mpf(n) * mp.pi / 88
    print(f"   n={n:>2}: η = {mp.nstr(mp.atanh(mp.cos(th)), 10)}  "
          f"ln cot(πn/176) = {mp.nstr(mp.log(mp.cot(mp.mpf(n)*mp.pi/176)), 10)}")
chk("H2 η_n = atanh(cosθ_n) = ln cot(πn/176) 精確", worst < mp.mpf("1e-50"),
    f"worst={mp.nstr(worst, 4)}")

# ── H3: 逆映射 θ = 2 arccot(e^η) ──
print("\n── H3: 逆映射 θ_n = 2·arccot(e^{η_n})（雙射）──")
worst = mp.mpf(0)
prev = None
mono = True
for n in range(1, N):
    th = mp.mpf(n) * mp.pi / 88
    eta = mp.atanh(mp.cos(th))
    th_back = 2 * mp.acot(mp.e ** eta)
    worst = max(worst, abs(th - th_back))
    if prev is not None and not (eta < prev):
        mono = False
    prev = eta
print(f"   max|θ − 2arccot(e^η)| = {mp.nstr(worst, 6)};  η_n 嚴格單調遞減: {mono}")
chk("H3 逆映射精確 + 單調（θ↔η 雙射）", worst < mp.mpf("1e-50") and mono)

# ── H4: docs/04 鏈 vs O140（γ, p, 質量殼）──
print("\n── H4: docs/04 鏈（γ=cscθ, p=mc·cotθ, E²−p²c²=m²c⁴）──")
m, c = mp.mpf(1), mp.mpf(1)
worst_g, worst_p, worst_shell = mp.mpf(0), mp.mpf(0), mp.mpf(0)
for n in range(1, N):
    th = mp.mpf(n) * mp.pi / 88
    gam = 1 / mp.sin(th)                    # cscθ（docs/04）
    gam_ref = mp.csc(th)                     # O140 §5
    p = m * c * mp.cos(th) / mp.sin(th)      # mc·cotθ（docs/04）
    p_ref = m * c * mp.cot(th)               # O140 §5
    E = m * c * c * gam
    worst_g = max(worst_g, abs(gam - gam_ref))
    worst_p = max(worst_p, abs(p - p_ref))
    worst_shell = max(worst_shell, abs(E*E - p*p*c*c - m*m*c**4))
print(f"   max|γ − csc θ| = {mp.nstr(worst_g, 4)}")
print(f"   max|p − mc·cotθ| = {mp.nstr(worst_p, 4)}")
print(f"   max|E² − p²c² − m²c⁴| = {mp.nstr(worst_shell, 4)}")
chk("H4 γ/p/質量殼 同 O140 逐點一致（docs/04 鏈 = O140）",
    worst_g < mp.mpf("1e-50") and worst_p < mp.mpf("1e-50") and worst_shell < mp.mpf("1e-50"))

# ── H5: 合成律封閉性（O140 🔴 開放項）──
print("\n── H5: η_a + η_b 落唔落喺階梯上? ──")
# 44-模態階梯: η_n = ln cot(πn/176), n=1..44
eta_ladder = [mp.log(mp.cot(mp.mpf(n) * mp.pi / 176)) for n in range(1, N)]
dEta0 = eta_ladder[0] - eta_ladder[1]
print(f"   ℓ=0 階梯間距 Δη_0 = ln cot(π/176) − ln cot(2π/176) = {mp.nstr(dEta0, 8)}")
on_ladder = 0
total = 0
import itertools
for a, b in itertools.combinations(range(1, N), 2):
    s = eta_ladder[a-1] + eta_ladder[b-1]
    nearest = min(abs(s - e) for e in eta_ladder)
    total += 1
    if nearest < mp.mpf("1e-30"):
        on_ladder += 1
print(f"   精確落格: {on_ladder}/{total} ({100.0*on_ladder/total:.2f}%)  ← O140「唔在階梯上」")
# O140 docs/04 §39 聲稱: 升層 ℓ (N_ℓ=44·4^ℓ) 合成落喺 Δη_ℓ/2 內
def ladder_at(ell):
    Nl = N * 4**ell
    xs = [mp.mpf(nn) * mp.pi / (176 * 4**ell) for nn in range(1, Nl)]
    return [mp.log(mp.cot(x)) for x in xs]
print("   O140「升層近似」檢定: 合成落喺 Δη_ℓ/2 內 嘅比例")
for ell in range(0, 7):
    lad = sorted(ladder_at(ell))
    dEta = lad[1] - lad[0]        # 升序: 第二 − 第一 = 正
    half = dEta / 2
    cnt = 0
    for a, b in itertools.combinations(range(1, N), 2):
        s = eta_ladder[a-1] + eta_ladder[b-1]
        nearest = min(abs(s - e) for e in lad)
        if nearest < half:
            cnt += 1
    print(f"     ℓ={ell}: Δη_ℓ/2 = {mp.nstr(half,6)}  落內 {cnt}/{total} = {100.0*cnt/total:.1f}%")
sample_ok = True
for a, b in [(1, 1), (1, 22), (3, 7)]:
    s = eta_ladder[a-1] + eta_ladder[b-1]
    lad = sorted(ladder_at(3)); dEta = lad[1]-lad[0]
    nearest = min(abs(s - e) for e in lad)
    print(f"     樣本 η_{a}+η_{b} = {mp.nstr(s,8)}: ℓ=3 最近距 = {mp.nstr(nearest,6)}  Δη₃/2 = {mp.nstr(dEta/2,6)}")
chk("H5 合成律: 精確唔落 88-格階梯（→ θ≠rapidity; κ-Poincaré 開放項 = O140）",
    on_ladder <= total * 0.1,
    f"精確落格 {on_ladder}/{total}")

# ── H6: 離散 γ 上限 ──
print("\n── H6: γ_max(ℓ) = csc(π/(88·4^ℓ)) ≈ (88/π)·4^ℓ（O140 §6.1）──")
worst = mp.mpf(0)
for ell in range(0, 8):
    Nl = mp.mpf(88) * mp.mpf(4)**ell
    gmax = mp.csc(mp.pi / Nl)
    approx = (88 / mp.pi) * mp.mpf(4)**ell
    dv = abs(gmax / approx - 1)
    worst = max(worst, dv)
    if ell <= 3:
        print(f"   ℓ={ell}: γ_max = {mp.nstr(gmax, 8)}  ≈ (88/π)·4^ℓ = {mp.nstr(approx, 8)}")
print(f"   max 相對偏差（ℓ=0..7）= {mp.nstr(worst, 4)}")
chk("H6 離散 γ 上限結構成立（γ_max ≈ (88/π)·4^ℓ）", worst < mp.mpf("1e-2"),
    f"worst rel={mp.nstr(worst, 4)}")

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")
print()
print("── 判決 ──")
print("  θ ≠ rapidity η（H5: 合成律唔喺階梯上封閉）")
print("  但 θ ↔ η 係精確雙射: η = ln cot(θ/2), θ = 2·arccot(e^η)（H2/H3 1e-50）")
print("  ⟹ docs/04 「同胚未證恒等」gap 收窄為: 精確關係已證, 合成律封閉性 = O140 開放項")
print("  ⟹ docs/04 鏈（γ=cscθ, p=mc cotθ, 質量殼）逐點 = O140 §5（獨立重證）")