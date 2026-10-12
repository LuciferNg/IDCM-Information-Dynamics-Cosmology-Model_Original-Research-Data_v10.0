#!/usr/bin/python3
"""O239 — Script 24: stair-β 全鏈閉合檢定（重寫版）
============================================================================
狀態: 2026-10-12 回滾後重寫（原 R17→R18 延伸內容已回滾, 本 script 重新落碟）
背景: scripts/23 確認 β = sin18° = 88-gon 每 20△ 面相位嘅半弦 (4.4 步)。
      本 script 檢定 stair 深度同 β 單位有冇結構連結:
        stair 深度: 33 (Up/K_Tree), 26 (Down), 19 (Lepton)
        β 分母:     10 = sin(π/10) 嘅「10」
        88 − (33+26+19) = ?  —— 會唔會啱好 = 10?

判據預註冊（唔 fit target）:
  S1: 33+26+19 = 78 = 6·F₇ (6×13)? 以及 88−78 = 10?
  S2: 10 嘅結構身份候選 (L₅−1, 20△/2) 檢定——但單點池太密禁律:
      10 係細數, 大量先驗結構式都會命中, 主身份只接受「由 88−Σstair 推出」,
      其他身份作為附註, 唔宣稱唯一.
  S3: stair k → k/20 圈: 33β=1.65 圈, 26β=1.30 圈, 19β=0.95 圈
      (β 單位 = 20△ 週期之一格), Lepton 19/20 = 差 1 完成 20△ 週期.
  S4: 後見發現聲明——此檢定由 scripts/23 結果自然衍生, 非預寫;
      任何「88−Σstair=10」嘅結構意義只作記錄, 唔推新預言.
產物: data/24_stair_beta_closure.json（重寫版）
"""
import json

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/24 — stair-β 全鏈閉合（重寫版, 回滾後重新落碟）")
print("=" * 78)

K_Tree, L4, B, N_gen = 33, 7, 4, 3
stair = [K_Tree, K_Tree - L4, K_Tree - 2*L4]   # 33, 26, 19
F7 = 13
L5 = 11
D20 = 20   # 20△ 挫阻面數

# ── S1: Σstair 同 88 餘數 ──
S = sum(stair)
rem = 88 - S
print(f"\n── S1: Σ(stair) 同 88 餘數 ──")
print(f"   33 + 26 + 19 = {S}")
print(f"   88 − {S} = {rem}")
print(f"   {S} = 6×F₇ = 6×{F7} = {6*F7}")
chk("S1a Σstair = 6·F₇ = 78", S == 6*F7, f"{S} = 6×{F7}")
chk("S1b 88 − Σstair = 10 (=β 分母)", rem == 10, f"{rem}")

# ── S2: 10 嘅身份候選 ──
print(f"\n── S2: 10 嘅結構身份候選（單點池太密禁律）──")
c10 = {
    "T1 88−Σstair (主身份, 由檢定推出)": 88 - S,
    "T2 L₅ − 1": L5 - 1,
    "T3 20△/2": D20 // 2,
    "T4 (88−32)/5 − 1.2? no": None,  # 唔砌新式
}
print(f"   T1 = {c10['T1 88−Σstair (主身份, 由檢定推出)']} (主)")
print(f"   T2 = L₅−1 = {L5}−1 = {L5-1} (附註, 池候選)")
print(f"   T3 = 20△/2 = {D20//2} (附註, 池候選)")
chk("S2 主身份 T1 成立, 其餘只作附註", c10["T1 88−Σstair (主身份, 由檢定推出)"] == 10,
    f"T1=10; T2={L5-1}, T3={D20//2} 只係池候選")

# ── S3: stair k → k/20 圈 ──
print(f"\n── S3: stair 深度喺 β 單位 (20△ 週期) ──")
beta_unit = 1/20   # 4.4 步 = 每 △ 面 4.4 步? no——88/20 = 4.4 步/△ 面, β=sin(4.4·π/44)
# 正確定義: β 單位週期 = 20△ 面 → 每個 stair 深度 n 對應 n/20 週期
for n in stair:
    print(f"   {n}β → {n}/20 = {n/20:.2f} 圈")
lept_turn = stair[2]/20
print(f"   Lepton 19/20 = {lept_turn:.2f} 圈 → 差 {1-lept_turn:.2f} 完成 20△ 週期")
chk("S3 Lepton 差 1/20 完成週期 (後見記錄)", abs((1 - lept_turn) - 1/20) < 1e-12,
    f"19/20, 餘 1/20")

json.dump({
    "S1_sum_stair": S, "S1_rem": rem, "S1_6F7": 6*F7,
    "S2_T1": 10, "S2_T2": L5-1, "S2_T3": D20//2,
    "S3_turns": [n/20 for n in stair],
    "S4_note": "後見發現—由 scripts/23 自然衍生, 唔推新預言; 10 嘅 T2/T3 係池候選唔宣稱",
}, open("data/24_stair_beta_closure.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")