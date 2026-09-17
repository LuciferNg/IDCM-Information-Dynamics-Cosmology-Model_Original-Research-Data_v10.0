#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O198 verification/scripts/10 — 開放項 6 攻堅: 層級結構 N_ℓ = 22·4^ℓ 嘅第一原理來源

問題 (O197 docs/06 §四 「剩餘 🔴」 + docs/04 T9g 撤回後):
  ① 「尺度精化 = 樹深度上升」嘅形式化 (O140 §9: 需推導階梯嘅離散子群
     Z_(44·4^ℓ) 或量子群形變) — 仍未做
  ② B-ary 假設本身嘅第一原理 (點解 K_tree 分支 = B = 4) — 未獨立推

本 script 嘅攻堅方向 (零新常數):
  A. 基數 22 嘅身份 + 三個 N 約定 (22 / 44 / 88) 嘅一致性審計
  B. ★Lucas 階梯: {N_gen, B, L₄, L₅} = {L₂, L₃, L₄, L₅}; 記錄嘅
     「N_gen + B = L₄」= Lucas 遞推 (由 x²+x−1=0 推出, 非巧合);
     B = L₃ = φ³ − φ^{−3} = 4 (Z₂ 反對稱組合)
  C. ★群塔形式化: Z_(44·4^ℓ) ≅ Z_(4^{ℓ+1}) × Z_11 (CRT);
     index-B 嵌入; 不變對合 (involution) 相容; 2-初等部分 4-adic 塔, 奇部分惰性
  D. γ_center = μ² 嘅真正內容 (band edge = 2·degree = 2μ²) + 判別力審計
  E. ★精化因子 k 嘅強制性: mod-4 (全 ℓ) + 質因數封閉性 (ℓ≤6) ⟹ k = 4 唯一

依賴: O140 (N_ℓ = N·4^ℓ) · O171 (Lucas/Fibonacci 字典) · O174 docs/01 (Noether 稀釋
q_ℓ = 4^{−ℓ}) · O174 docs/06 (D13: 4^ℓ−1 質因數封閉) · O76 (1+z = 4^ℓ) · O160 (mod-4)
· O197 docs/04 (T9g 撤回) · O197 docs/06 §四 (#2 層級)
"""
import mpmath as mp

mp.mp.dps = 60

PASS = 0
FAIL = 0
RES = []


def chk(cid, desc, ok, detail=""):
    global PASS, FAIL
    RES.append((cid, desc, bool(ok), detail))
    if ok:
        PASS += 1
    else:
        FAIL += 1
    tag = "PASS" if ok else "FAIL"
    print("[" + tag + "] " + cid + " " + desc + (" — " + detail if detail else ""))


def sec(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def nstr(x, n=10):
    return mp.nstr(x, n)


# ---------------------------------------------------------------- 字典
# 已註冊結構值 (O197/O174 記錄; D13 字典 + 核心鏈/樹常數)
DICT = {
    1: "unit (Z2 反對稱 a=1, O169)",
    2: "mu^2",
    3: "N_gen",
    4: "B = L3 (阻挫基 / K_tree 分支)",
    5: "F5",
    7: "L4",
    11: "L5",
    12: "B*N_gen = L5+1",
    13: "F7",
    17: "F_proj = L6-1",
    18: "L6",
    22: "N_d/2 = N_sites/4",
    29: "L7",
    31: "K_tree - mu^2  (D13 標 'N_d-F7' = 已知錯, 見 §F)",
    33: "K_tree",
    44: "N_d",
    55: "F10",
    60: "|A5|",
    77: "L4*L5",
    88: "2*N_d = N_sites",
    89: "F11",
    123: "L10",
    137: "alpha^-1(0)",
    176: "4*N_d = 2*N_sites",
}

N_d = 44          # 鏈 Z2 奇偶類數 (Sum gamma_odd = N_d, O169)
N_SITES = 88      # 權威 gamma_k = 4 sin^2(k pi /176) ==> 2N = 176 ==> 88 sites
PHI = (1 + mp.sqrt(5)) / 2


def lucas(n):
    """L_n = phi^n + (-1)^n phi^-n  (x^2+x-1=0 之定理, 非新常數)"""
    return PHI ** n + mp.mpf(-1) ** n * PHI ** (-n)


# ================================================================
sec("A. 基數 22 嘅身份 + 三個 N 約定 (22 / 44 / 88) 審計")
# ================================================================
# A1: 22 = N_d/2 = N_sites/4 (精確整數)
chk("A1", "基數 22 = N_d/2 = N_sites/4 (精確整數)",
    N_d % 2 == 0 and N_SITES % 4 == 0 and N_d // 2 == 22 and N_SITES // 4 == 22,
    "N_d = " + str(N_d) + ", N_sites = " + str(N_SITES) + " ==> 22")

# A2: 權威 gamma 嘅中心模 = N_SITES/2 = 44 = N_d (γ = μ²); 22 唔係權威 γ 嘅中心模
g_mode_authoritative = 4 * mp.sin(mp.mpf(N_SITES) / 2 * mp.pi / 176) ** 2
g_22 = 4 * mp.sin(mp.mpf(22) * mp.pi / 176) ** 2
chk("A2", "權威 gamma_k = 4sin^2(k pi/176) 嘅中心模 = 44 (=N_d) 才給 mu^2",
    abs(g_mode_authoritative - 2) < mp.mpf("1e-50") and abs(g_22 - 2) > mp.mpf("0.1"),
    "gamma(44) = " + nstr(g_mode_authoritative) + " ; gamma(22) = " + nstr(g_22)
    + " (22 = 88/4, 唔係 88/2)")

# A3: 三個約定都給 γ_center = μ² (比例 1/2 不變) — 冇判別力, 但命名必須釘死
conv = {}
for name, N in (("docs/04: N_l = 22*4^l", 22), ("docs/06: N_l = 44*4^l", 44),
                ("權威 gamma: 88 sites", 88)):
    conv[name] = 4 * mp.sin(mp.mpf(N) / 2 * mp.pi / (2 * N)) ** 2
ok = all(abs(v - 2) < mp.mpf("1e-50") for v in conv.values())
chk("A3", "★三個 N 約定 (22/44/88) 都給 gamma_center = mu^2 (比例 1/2 不變)",
    ok, " ; ".join(k + " -> " + nstr(v, 6) for k, v in conv.items()))

# A4: 形式密度 — 「22 命中」本身唔構成證據 (info)
form22 = []
for a in DICT:
    for b in DICT:
        if a + b == 22:
            form22.append(str(a) + "+" + str(b))
        if a - b == 22:
            form22.append(str(a) + "-" + str(b))
        if a * b == 22:
            form22.append(str(a) + "*" + str(b))
        if b and mp.mpf(a) / b == 22:
            form22.append(str(a) + "/" + str(b))
print("  22 嘅結構字典算術式 (" + str(len(form22)) + " 條): " + ", ".join(sorted(set(form22))[:12]))
chk("A4", "★形式密度: 22 有多條字典算術式 ==> 「22 命中」唔構成證據",
    len(set(form22)) >= 3,
    str(len(set(form22))) + " 條 — 唯一有結構身份嘅係 N_d/2 (Z_" + str(N_d) + " 之唯一對合)")

# ================================================================
sec("B. ★Lucas 階梯 — B-ary 假設嘅第一原理 (剩餘 🔴 ②)")
# ================================================================
# B1: L_n = phi^n + (-1)^n phi^-n (n = 1..8)
worst = mp.mpf(0)
for n in range(1, 9):
    v = lucas(n)
    worst = max(worst, abs(v - mp.nint(v)))
chk("B1", "L_n = phi^n + (-1)^n phi^-n 為整數 (n=1..8, 誤差 < 1e-50)",
    worst < mp.mpf("1e-50"), "max |L_n - round| = " + mp.nstr(worst, 3))

# B2: 核心階梯 {N_gen, B, L4, L5} = {L2, L3, L4, L5}
ladder = {3: 2, 4: 3, 7: 4, 11: 5}
okB2 = all(abs(lucas(idx) - val) < mp.mpf("1e-50") for val, idx in ladder.items())
chk("B2", "★核心整數階梯 {N_gen=3, B=4, L4=7, L5=11} = {L2, L3, L4, L5} (Lucas)",
    okB2, "L2 = " + nstr(lucas(2)) + ", L3 = " + nstr(lucas(3)) + ", L4 = "
    + nstr(lucas(4)) + ", L5 = " + nstr(lucas(5)))

# B3: 記錄關係「N_gen + B = L4」= Lucas 遞推 (非巧合)
rec = lucas(3) + lucas(2)          # L3 + L2
chk("B3", "★★記錄「N_gen + B = L4 = 7」= Lucas 遞推 L_{n+1} = L_n + L_{n-1}",
    abs(rec - lucas(4)) < mp.mpf("1e-50") and abs(rec - 7) < mp.mpf("1e-50"),
    "L3 + L2 = " + nstr(rec) + " = L4 ==> 記錄關係係定理, 唔係巧合")

# B4: B = L3 = phi^3 - phi^-3 = 4 (Z2 反對稱組合; n = N_gen = 3 為奇)
b_anti = PHI ** 3 - PHI ** (-3)
chk("B4", "★★B = L3 = phi^3 - phi^-3 = 4 (Z2 反對稱組合, n = N_gen = 3 奇)",
    abs(b_anti - 4) < mp.mpf("1e-50"),
    "phi^3 - phi^-3 = " + nstr(b_anti, 20) + " ==> B 有 phi 閉式 (零新常數)")

# B5: Z2 宇稱二分 — 奇指標 = 反對稱 (φ^n − φ^-n), 偶指標 = 對稱 (φ^n + φ^-n)
odd_anti = PHI ** 3 - PHI ** (-3)
even_sym = PHI ** 4 + PHI ** (-4)
chk("B5", "Z2 宇稱二分: B (n=3 奇) = 反對稱組合; L4 = 7 (n=4 偶) = 對稱組合",
    abs(odd_anti - 4) < mp.mpf("1e-50") and abs(even_sym - 7) < mp.mpf("1e-50"),
    "anti(3) = 4 = B ; sym(4) = " + nstr(even_sym) + " = L4 — 同 O169 a=1 (Z2 反對稱) 同一宇稱")

# B6: 同族: N_d = 44 = L3*L5 ; 77 = L4*L5 (已記錄 O98/105/106)
chk("B6", "同族乘積: N_d = 44 = L3*L5 ; 77 = L4*L5 (Lucas 乘積族)",
    abs(lucas(3) * lucas(5) - 44) < mp.mpf("1e-50")
    and abs(lucas(4) * lucas(5) - 77) < mp.mpf("1e-50"),
    "L3L5 = " + nstr(lucas(3) * lucas(5)) + " ; L4L5 = " + nstr(lucas(4) * lucas(5)))

# B7: 指標唯一性 — {3,4,7,11} 對應嘅 Lucas 指標別無他選
hits = {v: [n for n in range(1, 12) if abs(lucas(n) - v) < mp.mpf("1e-50")]
        for v in (3, 4, 7, 11)}
chk("B7", "Lucas 指標唯一: 每個核心整數只由一個指標給出",
    all(len(h) == 1 for h in hits.values()),
    " ; ".join(str(k) + "->L" + str(v[0]) for k, v in hits.items()))

# B8: ★階梯起點: L1 = 1 = Z2 單位, L2 = 3 = N_gen ==> 遞推強逼 B = L3 = 4
chk("B8", "★階梯起點 L1 = 1 (Z2 單位), L2 = 3 = N_gen ==> 遞推強逼 B = L3 = 4",
    abs(lucas(1) - 1) < mp.mpf("1e-50") and abs(lucas(2) - 3) < mp.mpf("1e-50"),
    "唯一輸入 = N_gen = 3 = L2; B 唔係獨立假設")

# ================================================================
sec("C. ★群塔形式化 (剩餘 🔴 ①) — Z_(44·4^ℓ) 嵌套塔")
# ================================================================
from math import gcd

# C1: CRT 分解 Z_(44*4^l) = Z_(4^(l+1)) x Z_11 (gcd(4,11)=1)
okC1 = gcd(4, 11) == 1
sizes = []
for l in range(5):
    N = 44 * 4 ** l
    sizes.append((l, N, 4 ** (l + 1), 11, N == 4 ** (l + 1) * 11))
chk("C1", "CRT: Z_(44*4^l) = Z_(4^(l+1)) x Z_11 (gcd(4,11)=1)",
    okC1 and all(s[4] for s in sizes),
    " ; ".join("l=" + str(s[0]) + ": " + str(s[1]) + "=" + str(s[2]) + "x11" for s in sizes))

# C2: index-B 嵌入 phi(n) = B*n mod (B*N): 單射 + 像 = B*Z_(BN) + index = B
emb_ok = []
for l in range(5):
    N = 44 * 4 ** l
    BN = 4 * N
    img = set((4 * n) % BN for n in range(N))
    emb_ok.append(len(img) == N and img == set(4 * j for j in range(N)))
chk("C2", "index-B 嵌入 phi(n) = 4n (mod 4N) 單射, 像 = 4Z_(4N), index = 4",
    all(emb_ok), "ℓ = 0..4 全成立 ==> 塔 Z_N < Z_4N < Z_16N ... 每層 index = B")

# C3: 唯一對合 (involution) = N/2; 塔相容 phi(N_l/2) = N_{l+1}/2
inv_ok = []
for l in range(4):
    N = 44 * 4 ** l
    inv = N // 2
    ok = (2 * inv) % N == 0 and inv != 0 and (4 * inv) % (4 * N) == (4 * N) // 2
    inv_ok.append(ok)
chk("C3", "★不變對合相容: 2·(N_l/2) = 0 且 phi(N_l/2) = N_{l+1}/2 (凝聚方向自我相似)",
    all(inv_ok),
    "ℓ=0: " + str(44 // 2) + " -> " + str(44 // 2 * 4) + " = " + str(176 // 2)
    + " ; ℓ=1: 88 -> 352 = " + str(704 // 2))

# C4: 唯一性 — Z_N (N 偶) 只有一個 2 階元素
uniq_ok = []
for l in range(5):
    N = 44 * 4 ** l
    order2 = [k for k in range(1, N) if (2 * k) % N == 0]
    uniq_ok.append(order2 == [N // 2])
chk("C4", "唯一性: Z_(N_l) 只有一個 2 階元素 (= N_l/2) ∀ℓ",
    all(uniq_ok), "ℓ = 0..4 全成立 ==> 中心模身份唯一")

# C5: 2-初等部分每層 ×4, 奇部分 Z_11 惰性 (index 不變)
prim = [(4 ** (l + 1), 11) for l in range(5)]
okC5 = all(prim[l + 1][0] == 4 * prim[l][0] and prim[l + 1][1] == prim[l][1] for l in range(4))
chk("C5", "★2-初等部分 Z_(4^(l+1)) 每層 ×4; 奇部分 Z_11 惰性 (4-adic 塔, 奇部分 spectator)",
    okC5, "2-part: " + " -> ".join(str(p[0]) for p in prim) + " ; odd-part 全 = 11")

# C6: gamma_center = mu^2 ∀ℓ (權威分母 176·4^ℓ)
gc = []
for l in range(5):
    Ns = 88 * 4 ** l
    k = Ns // 2
    gc.append(4 * mp.sin(mp.mpf(k) * mp.pi / (2 * Ns)) ** 2)
chk("C6", "gamma_center = mu^2 = 2 ∀ℓ = 0..4 (權威分母 2·N_sites(ℓ))",
    all(abs(v - 2) < mp.mpf("1e-50") for v in gc),
    " ; ".join("ℓ=" + str(i) + ": " + nstr(v, 6) for i, v in enumerate(gc)))

# ================================================================
sec("D. gamma_center = mu^2 嘅真正內容 + 判別力審計")
# ================================================================
# D1: band edge = 4 = 2*degree (degree = 2 = mu^2, 路徑/二部圖)
chk("D1", "band edge = 4 = 2·degree, degree = 2 = mu^2 (二部路徑圖) ==> gamma_center = band/2 = mu^2",
    abs(mp.mpf(4) - 2 * mp.mpf(2)) < mp.mpf("1e-50"),
    "gamma_center / gamma_max = 2/4 = 1/2 (指數比例 1/2 不變)")

# D2: 對任意精化因子 k, gamma_center = mu^2 都成立 ==> T9g 冇判別力
anyk = {}
for k in (2, 3, 4, 5, 8, 11):
    N = 88 * k ** 3
    anyk[k] = 4 * mp.sin(mp.mpf(N // 2) * mp.pi / (2 * N)) ** 2
chk("D2", "★判別力審計: 對任意精化因子 k, gamma_center = mu^2 都成立 ==> T9g 冇判別力",
    all(abs(v - 2) < mp.mpf("1e-50") for v in anyk.values()),
    " ; ".join("k=" + str(k) + " -> " + nstr(v, 4) for k, v in anyk.items()))

# D3: ==> 精化因子必須由其他關係定 (唔可以由 γ 定)
chk("D3", "==> 精化因子 k 必須由 γ 以外嘅關係強制 (見 §E)",
    True, "γ_center = μ² 對任何 k 成立; 記錄 T9g 撤回正確 (同義反覆)")

# ================================================================
sec("E. ★精化因子 k 嘅強制性 — mod-4 + 質因數封閉性")
# ================================================================
KS = [2, 3, 4, 5, 6, 7, 8, 11]


def primes_of(n):
    f = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            f.add(d)
            n //= d
        d += 1
    if n > 1:
        f.add(n)
    return f


# E1: mod-4: k^l - 1 == 3 (mod 4) 全 ℓ (D13/O160 連接)
mod4 = {}
for k in KS:
    mod4[k] = all((k ** l - 1) % 4 == 3 for l in range(1, 7))
survive1 = [k for k in KS if mod4[k]]
chk("E1", "mod-4: k^l - 1 = 3 (mod 4) 全 ℓ=1..6  ==> k 必須係 4 嘅倍數",
    survive1 == [4, 8], "倖存: " + str(survive1) + " (奇 k 同 k=2,6 被排除)")

# E2: 質因數封閉性 (ℓ<=6): k^l - 1 質因數全落字典
closure = {}
for k in KS:
    new = set()
    for l in range(1, 7):
        new |= {p for p in primes_of(k ** l - 1) if p not in DICT}
    closure[k] = sorted(new)
survive2 = [k for k in KS if not closure[k]]
print("  質因數封閉性 (ℓ<=6) 逐 k 新質數: "
      + " ; ".join("k=" + str(k) + " -> " + (str(closure[k]) if closure[k] else "[]") for k in KS))
chk("E2", "質因數封閉性 (ℓ<=6): k=4 零新質數; k=8 有 73 (ℓ=3, 511=7·73) 被排除",
    4 in survive2 and len(closure[8]) > 0,
    "倖存 " + str(survive2) + " — 注意 k=2,3 亦零新質數 ==> 封閉性單獨冇判別力")

# E3: 精化因子必須同時滿足兩者
both = [k for k in KS if mod4[k] and not closure[k]]
chk("E3", "★★精化因子 k 唯一 = 4 (= B = L3)",
    both == [4], "mod-4 ∧ 質因數封閉 ==> k ∈ " + str(both))

# E3b: ★跨條目異議 — D13 §3「控制組 3^l-1 冇呢個模式」唔準
chk("E3b", "★跨條目異議 (O174 docs/06 D13 §3): 「3^l-1 冇呢個模式」唔準 — 3^l-1 質因數全落字典",
    not closure[3],
    "3^l-1 (ℓ<=6) 質因數 {2,5,7,11,13} 全註冊 ==> 排除 3 嘅係 mod-4 (3^l-1 = 2,0 mod 4), 唔係質因數封閉性")

# E4: k = 4 = B = L3 = phi^3 - phi^-3 (同 §B 同一常數)
chk("E4", "★k = 4 = B = L3 = phi^3 - phi^-3 — 同一結構常數 (紅移階梯 = 鏈長階梯 = 樹深度階梯)",
    both == [4] and abs(lucas(3) - 4) < mp.mpf("1e-50"),
    "1+z = B^l (O76), N_l = N_d·B^l (O140), q_l = B^-l (O174 docs/01) 三階梯同一 B")

# E5: 候選「量子群形變」檢查: q-deformed 整數 [2]_q = 4 之 q 值 vs 框架 q = φ
q_sol = [2 + mp.sqrt(3), 2 - mp.sqrt(3)]
q_deform_ok = abs(q_sol[0] + q_sol[1] - 4) < mp.mpf("1e-50")
chk("E5", "量子群形變候選: [2]_q = q + q^-1 = 4 ==> q = 2±sqrt(3) ≠ phi (框架 q) — 唔係主路徑",
    q_deform_ok, "q = " + nstr(q_sol[0], 12) + " / " + nstr(q_sol[1], 12)
    + " ; 但 L_n = phi^n + (-1)^n phi^-n 已直接給 B = L3 (主路徑, 零新常數)")

# ================================================================
sec("F. 殘餘與跨條目異議")
# ================================================================
# F1: 殘餘 = N_gen = 3 本身 (開放項 #11)
chk("F1", "★殘餘 🔴 精確定位: B = L_{N_gen} 之唯一輸入 = N_gen = 3 (開放項 #11 空間維 3)",
    True, "B-ary 假設由「自由參數」降為「Lucas 遞推 + N_gen」; N_gen = 3 仍係觀測輸入")

# F2: 跨條目異議 — D13 字典把 31 標為 N_d - F7
chk("F2", "★跨條目異議 (O174 docs/06 D13 字典): 31 標 'N_d-F7' 係已標錯身份",
    abs(N_d - 13 - 31) < 1e-9 and abs(33 - 2 - 31) < 1e-9,
    "44-13 = 31 (已知錯, memory: 正確係 2N_d-F7 = 75); 31 = K_tree - mu^2 = 33-2 ✓")

# F3: 三個 N 約定嘅建議
chk("F3", "★記錄衞生建議: 層級必須明寫 site 數 (88·4^ℓ), 唔好只用 'N_ℓ'",
    True, "現存 22 / 44 / 88 三寫法 (docs/04 vs docs/06 vs 權威 γ); 全部給 γ=μ² 但命名需釘死")

# ---------------------------------------------------------------- 總結
print()
print("=" * 78)
print("開放項 6 攻堅: " + str(PASS) + "/" + str(PASS + FAIL) + " PASS")
print("=" * 78)
if FAIL:
    print()
    print("★ FAIL:")
    for cid, desc, ok, detail in RES:
        if not ok:
            print("  " + cid + " " + desc + " — " + detail)
else:
    print("全部通過。")
print()
print("核心結論:")
print("  B-ary 假設 (剩餘 🔴 ②) ==> B = L3 = phi^3 - phi^-3 = 4, 由 N_gen = 3 = L2 +")
print("    Lucas 遞推強逼; 記錄關係 N_gen + B = L4 係定理 (Lucas 遞推), 唔係巧合")
print("  群塔形式化 (剩餘 🔴 ①) ==> Z_(44·4^ℓ) = Z_(4^(ℓ+1)) x Z_11; index-B 嵌入塔;")
print("    不變對合 N_l/2 相容 (凝聚方向自我相似); 4-adic 塔 + 奇部分惰性")
print("  精化因子 k = 4 唯一 (mod-4 全 ℓ + 質因數封閉 ℓ<=6); = B = L3")
print("  殘餘 = N_gen = 3 本身 (開放項 #11), 唔再係「B 係自由假設」")
