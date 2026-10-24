#!/usr/bin/env python3
"""
O216 scripts/03_nogo_barriers.py — 色荷結構 no-go 證明（多條獨立屏障）
=======================================================================
SESSION_START 驗證標準: 「色荷規則：零參數閉式 + 盲測」或「結構 no-go 證明
（多條獨立屏障）」。本檔提供後者 — 五條獨立屏障。

屏障 A（算術/譜側）: 鏈長冇 3 因子 ⟹ 鏈層冇 Z₃ 週期結構 ⟹ 色荷唔可能係鏈週期量
屏障 B（密度基準）: Δn_color ∈ 目錄 q_obs 🔴 ⟹ 任何「和/差屬目錄」論證無效
屏障 C（窮舉）:     O137 R19 事前 6 候選全 fail（只有無鑑別力 2ℤ/4ℤ）
屏障 D（嵌入層）:   色數 3 = B−1（O68）+ 4 = 3⊕1（O88）⟹ 色荷已有規範嵌入層結構
屏障 E（身份）:     18 = 6×3 = 2N_gen² = L₆ 只係 counting identity，唔當額外證據

裁決（SESSION_START §五）: 色荷唔可以由鏈層導出（no-go），
色數本身已由規範嵌入層導出（O68/O88 閉合, 引用）。
"""
import random, math, sys, os, json

PASS, FAIL = [], []
def _reg_closed(pids):
    """真查 register.jsonl 追閉合狀態（replay: closed→True, reopen/open→False）。
    路徑自動適配 register 搬遷（repo 內 / repo 上一層）。查唔到 → False（誠實 FAIL）。"""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    for cand in (os.path.join(root, "problem_register", "register.jsonl"),
                 os.path.join(os.path.dirname(root), "problem_register", "register.jsonl")):
        if not os.path.exists(cand):
            continue
        st = {}
        for ln in open(cand, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            try:
                d = json.loads(ln)
            except Exception:
                continue
            p = str(d.get("pid") or "").split("/")[0]
            if p not in pids:
                continue
            if d.get("kind") == "closed" or d.get("verdict") == "closed":
                st[p] = True
            elif d.get("kind") == "reopen" or d.get("verdict") == "open":
                st[p] = False
        return all(st.get(p) is True for p in pids)
    return False
def ck(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name}" + (f"  ({detail})" if detail else ""))

N_d, B, N_gen = 44, 4, 3
L = [2,1]
while len(L) < 7: L.append(L[-1]+L[-2])

print("="*84)
print("屏障 A — 鏈層冇 Z₃ 週期結構（算術）")
print("="*84)
# 88-site 鏈之週期結構: 88 = 2³·11; 44 = 2²·11; 176 = 16·11
for M, name in [(88,"88-site"), (44,"44-site"), (176,"176-site")]:
    fac3 = M % 3 == 0
    print(f"  {name} 鏈長 {M} = {M} (=2^a·11^b 家族)  mod 3 = {M%3}  ⟹ 3{'|' if fac3 else '∤'}{M}")
ck("88-site: 3 ∤ 88 (冇 Z₃ 週期)", 88 % 3 != 0, "88 = 2³·11")
ck("44-site: 3 ∤ 44 (冇 Z₃ 週期)", 44 % 3 != 0, "44 = 2²·11")
ck("176-site: 3 ∤ 176", 176 % 3 != 0, "176 = 16·11")
print("  ★ 鏈長家族 ℳ = 2^a·11^b (O229 R4: 3 ∤ M 係結構上不可能嘅必要條件)")
print("  ⟹ 鏈層冇模-3扇區 / 3 週期結構可承載「色」")
# 平移對稱 subgroup: Z_88 嘅 subgroup 階 = gcd(88, k) ∈ divisors(88) = {1,2,4,8,11,22,44,88}
divs = sorted(d for d in range(1,89) if 88 % d == 0)
ck("Z_88 subgroup 階 ∈ {1,2,4,8,11,22,44,88} 冇 3", 3 not in divs, str(divs))

print()
print("="*84)
print("屏障 B — 密度基準（O208 標準, 本 O scripts/01）")
print("="*84)
N_MC, SEED = 200_000, 216
rng = random.Random(SEED)
DN_OBS = {0, 12, 28}
STRICT = {1,2,3,4,5,6,7,8,9,10,11,13,15,16,18,21,28,33}
BROAD  = STRICT | {12,14,17,19,20,22,24,25,26,27,29,30,31,32,34,35,36,37,
                   40,41,42,44,45,46,49,55,60,64,66,70,75,77,88,90,92,98}
def frac(cat):
    xs = rng.sample(range(0,34), 3)
    return sum(1 for x in xs if x in cat)/3
q_s = sum(1 for _ in range(N_MC) if frac(STRICT) <= 1/3)/N_MC
q_b = sum(1 for _ in range(N_MC) if frac(BROAD) <= 2/3)/N_MC
print(f"  Δn = {sorted(DN_OBS)}; 嚴格命中 1/3, 寬鬆命中 2/3")
print(f"  q_obs(嚴格) = {q_s:.4%}  q_obs(寬鬆) = {q_b:.4%}  (N_mc={N_MC}, seed={SEED})")
ck("q_obs(嚴格) > 5% → 🔴 密度效應", q_s > 0.05, f"{q_s:.4%}")
ck("q_obs(寬鬆) > 5% → 🔴 密度效應", q_b > 0.05, f"{q_b:.4%}")
print("  ⟹ 觀測命中率唔高於隨機中位 ⟹ 「Δn_color 屬 IDCM 目錄」唔構成證據")

print()
print("="*84)
print("屏障 C — O137 R19 事前候選 6 條全部 fail（重現）")
print("="*84)
dn_obs = {0,12,28}
cands = {
    "{0,B²,2B²,3B²} = {0,16,32,48}": {0,16,32,48},
    "{0,L₄,2L₄,3L₄} = {0,7,14,21}": {0,7,14,21},
    "{0,N_gen²,2N_gen²,3N_gen²} = {0,9,18,27}": {0,9,18,27},
    "{0,N_d,2N_d} = {0,44,88}": {0,44,88},
    "2ℤ (偶數)": None,
    "4ℤ (B 倍數)": None,
}
fails = 0
for nm, S in cands.items():
    if S is None:
        if "2ℤ" in nm: ok = all(x % 2 == 0 for x in dn_obs)
        else: ok = all(x % 4 == 0 for x in dn_obs)
    else:
        ok = dn_obs <= S
    if not ok: fails += 1
    else: print(f"    ⚠️ {nm} 通過（但無鑑別力）")
print(f"  事前候選 6 條中: {fails} 條 fail; 通過者只有 2ℤ/4ℤ（無鑑別力）")
ck("0/{B,L₄,N_gen²,N_d} 家族 4 條全 fail", not (dn_obs <= cands["{0,B²,2B²,3B²} = {0,16,32,48}"] or
    dn_obs <= cands["{0,L₄,2L₄,3L₄} = {0,7,14,21}"] or
    dn_obs <= cands["{0,N_gen²,2N_gen²,3N_gen²} = {0,9,18,27}"] or
    dn_obs <= cands["{0,N_d,2N_d} = {0,44,88}"]))
print("  ⟹ Δn = [0,12,28] 非 N_gen/B/L₄/N_d 倍數族; O137 R19 已據此判「無單一結構規則」")

print()
print("="*84)
print("屏障 D — 嵌入層已導出色數（O68/O88 閉合, 引用）")
print("="*84)
print("""
  SU(4)_PS → SU(3)_C × U(1)_{B−L}:  4 = 3_{1/3} ⊕ 1_{−1}   (O68 docs/02, O88 docs/02)
    4 = B = L₃ (K_Tree 分支因子)    3 = B−1 = N_gen (色荷)  1 = B−(B−1) (B−L)
  12 = (4,3) = (3,3)_{1/3} ⊕ (1,3)_{−1}  = 9 夸克(3色×3代) + 3 輕子(3代)  (O88)
""")
ck("色數 3 = B−1 = N_gen（O68 閉合）", B-1 == N_gen == 3)
ck("4 = 3⊕1 分解結構（O88 閉合）", 4 == 3+1 and 1 == B-(B-1))
ck("O88 = closed, O68 = closed（register 真查）", _reg_closed({"O88","O68"}), "replay register.jsonl")
print("  ⟹ 色荷**存在性與計數**（3 色）已由規範嵌入層導出 — 唔係外部標籤")
print("  ⟹ 剩餘問題只有「Δn_color 繞數規則」— 屏障 A/B/C 已否證其鏈層結構")

print()
print("="*84)
print("屏障 E — 18 = 6×3 = 2N_gen² = L₆ 只係 counting identity")
print("="*84)
total = 6 * 3
print(f"  夸克模式 6 × 色 3 = {total} 夸克態")
print(f"  {total} = 2·N_gen² = 2·9 = L₆ = {L[6]}")
ck("18 = 2N_gen² = L₆ (算術恆等)", total == 2*N_gen**2 == L[6])
print("  ⚠️ 此身份唔係色荷規則: 佢只反映 6 = 2N_gen 與 3 = B−1 = N_gen 嘅組合;")
print("  色乘子 3 本身先有結構（屏障 D）。18 = L₆ 係 bonus identity 唔當證據。")

print()
print("="*84)
print("裁決（SESSION_START §五 標準）")
print("="*84)
print("""
  🔴 色荷唔可以由鏈層導出（結構 no-go）:
      A. 鏈長冇 3 因子（3 ∤ 88/44/176）⟹ 冇 Z₃ 扇區
      B. 密度基準 q_obs 🔴 ⟹ 「Δn ∈ 目錄」論證無效
      C. O137 R19 事前 6 候選全 fail / 無鑑別力
  🟢 色數 3 = B−1 = N_gen 已由規範嵌入層導出（O68/O88 閉合, 引用）:
      4 = 3_{1/3} ⊕ 1_{−1} ⟹ 3 色 = SU(3)_C 三重態
  🟡 結論: 色荷係「規範嵌入層標籤」（同角色 σ_g 一層, O209 docs/10 + O67 merged）,
      唔係鏈層譜量; Δn_color 繞數規則唔存在。色荷自由度 = 3 = B−1 結構強制,
      唔係「外部觀測輸入」— 已由 SU(4)_PS → SU(3)_C × U(1)_{B−L} 分解承接。
""")
print(f"PASS {len(PASS)} / FAIL {len(FAIL)}")
sys.exit(0 if not FAIL else 1)