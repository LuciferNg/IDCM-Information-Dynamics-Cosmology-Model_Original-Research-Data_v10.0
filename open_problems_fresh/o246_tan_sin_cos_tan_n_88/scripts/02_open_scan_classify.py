#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O246 scripts/02_open_scan_classify.py — 全開放問題 tan 適用性分類

調律者指示 (2026-10-10): 開新O掃全部開放問題, tan 分析做示範, 驗證後交接, 開完不推。

分類判準:
  A = tan 可能直接適用 (含相位/位元/二元/摺疊/對稱/譜相/時間處理)
  B = 需進一步測試 (含譜和/閉式/質量公式/算子身份)
  C = 唔適用 (純觀測/工具/命名/數據源/形而上学框架)

用法: /usr/bin/python3 scripts/02_open_scan_classify.py
輸出: docs/03_open_scan_table.md (分類表)
"""
import sqlite3, os, re, json

REPO = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
CON = sqlite3.connect(f"{REPO}/problem_register/register.sqlite")
rows = CON.execute(
    "SELECT pid, state, verdict, title FROM o_problem "
    "WHERE state IN ('open','partial','registered') AND pid NOT LIKE '%/%' "
    "ORDER BY CASE WHEN pid LIKE 'O%' THEN CAST(substr(pid,2) AS INT) ELSE 999 END"
).fetchall()
subrows = CON.execute(
    "SELECT pid, state, verdict, title FROM o_problem "
    "WHERE state IN ('open','partial','registered') AND pid LIKE '%/%' "
    "ORDER BY pid"
).fetchall()
CON.close()

# A 類 keyword: 相位/位元/二元/摺疊/對稱/時間/譜相/晶格/因果
A_KW = ["相位", "phase", "位元", "bit", "二元", "binary", "摺疊", "fold",
        "對稱", "symmetry", "時間", "tick", "宇稱", "parity", "對合",
        "晶格", "lattice", "cellular", "自旋", "spin", "Bell", "求值",
        "lazy", "rollback", "回滾", "阻挫", "frustration", "繞數", "winding",
        "Z₂", "Z2", "checkerboard", "對映", "mapping", "無信號", "no-signal",
        "糾纏", "entangl", "量子態", "Born", "機制層", "光錐", "Lorentz",
        "低能極限", "連續化", "Cauchy", "複相位", "amplitude", "phase-amplitude",
        "delta", "δ", "混合角", "mixing", "方向", "orient", "sign_rank",
        "beat", "拍頻", "數域", "periodic", "周期", "迴路", "閉合鏈",
        "資源幾何", "resource", "序", "次序", "頻率", "frequency", "波",
        "wave", "FSR", "相對論", "relativit", "紐結", "knot", "能量",
        "黑洞", "entropy", "熵", "debris", "返池", "作動", "動作電位"]
# B 類 keyword: 質量/譜和/閉式/算子/數值身份
B_KW = ["質量", "mass", "譜", "spectr", "閉式", "closed form", "算子", "operator",
        "數值", "value", "標度", "scale", "尺度", "G", "常數", "constant",
        "色散", "dispersion", "γ", "gamma", "頻譜", "eigen", "本徵",
        "重心", "baryon", "質子", "中子", "n/p", "η_B", "豐度", "abundance",
        "旋轉曲線", "rotation", "BTFR", "距離", "distance", "紅移", "redshift",
        "紅移演化", "H_eff", "H(z)", "D_L", "D_A", "Cepheid", "SN", "Maser",
        "級數", "和", "sum", "積", "product", "根", "root", "Galois", "數域",
        "kchain", "K_Chain", "K_Tree", "樹", "tree", "維度", "dimension",
        "破缺", "breaking", "旋量", "spinor", "費米子", "fermion", "玻色子",
        "boson", "Higgs", "EW", "弱電", "真空", "vacuum", "密度", "density",
        "暗物質", "dark matter", "張力", "tension", "h0", "Hubble", "H₀"]
# C 類 keyword: 觀測/工具/命名/數據/方法論
C_KW = ["冷斑", "熱斑", "節點", "node", "SMICA", "WMAP", "Planck", "小波",
        "wavelet", "工具箱", "工具", "命名", "naming", "數據源", "data source",
        "疊加", "stack", "對徑", "antipodal", "溫差", "溫度", "Catalogue",
        "目錄", "Lensing", "lensing", "mask", "前景", "foreground", "統計",
        "Occam", "形而上學", "命名規範", "verification", "驗證"]

def classify(title, pid):
    t = (title or "") + " " + pid
    tl = t.lower()
    a_score = sum(1 for kw in A_KW if kw.lower() in tl)
    b_score = sum(1 for kw in B_KW if kw.lower() in tl)
    c_score = sum(1 for kw in C_KW if kw.lower() in tl)
    if a_score >= 2 and a_score >= b_score:
        return "A"
    if c_score >= 2 and c_score > a_score and c_score > b_score:
        return "C"
    if b_score >= 1 or a_score >= 1:
        return "B"
    return "C"

results = []
for pid, state, verdict, title in rows:
    cls = classify(title, pid)
    results.append((cls, pid, state, title))

subresults = []
for pid, state, verdict, title in subrows:
    cls = classify(title, pid)
    subresults.append((cls, pid, state, title))

# 排序: A → B → C
order = {"A": 0, "B": 1, "C": 2}
results.sort(key=lambda r: (order[r[0]], r[1]))
subresults.sort(key=lambda r: (order[r[0]], r[1]))

out = ["# O246 docs/03 — 全開放問題 tan 適用性掃描分類表",
       "",
       "> 日期：2026-10-10（主 O）/ 2026-10-11（子問題補掃）· 方法：scripts/02_open_scan_classify.py（keyword 規則）· 狀態：🟢 掃描完成",
       "> 調律者指示：「所有開放問題掃一遍」—— open-family 主 O + 子問題（state ∈ {open,partial,registered}，register.sqlite 2026-10-11 快照）。",
       "> 判準：**A** = tan 可能直接適用（相位/位元/二元/摺疊/對稱/時間/譜相）｜**B** = 需進一步測試（譜和/閉式/質量/算子）｜**C** = 唔適用（純觀測/工具/命名/方法論）",
       "",
       f"## 統計（主 O）：A={sum(1 for r in results if r[0]=='A')} · B={sum(1 for r in results if r[0]=='B')} · C={sum(1 for r in results if r[0]=='C')} · 總={len(results)}",
       "",
       "| 類 | pid | state | title |",
       "|:--|:--|:--|:--|"]
for cls, pid, state, title in results:
    t = (title or "")[:60].replace("|", "\\|")
    out.append(f"| {cls} | {pid} | {state} | {t} |")

out += ["",
        f"## 統計（子問題）：A={sum(1 for r in subresults if r[0]=='A')} · B={sum(1 for r in subresults if r[0]=='B')} · C={sum(1 for r in subresults if r[0]=='C')} · 總={len(subresults)}",
        "",
        "| 類 | pid | state | title |",
        "|:--|:--|:--|:--|"]
for cls, pid, state, title in subresults:
    t = (title or "")[:60].replace("|", "\\|")
    out.append(f"| {cls} | {pid} | {state} | {t} |")

out += ["",
        "## 交接策略",
        "",
        "- **A 類**：tan 三角波/摺疊身份最有可能適用 → register handoff 去對應歸屬 O（見 docs/02 §四）",
        "- **B 類**：需進一步盲測（tan 閉式類比、格點對照）—— 記錄但唔推",
        "- **C 類**：無關，唔開",
        "",
        "> ⚠️ 「開完不推」：本表只分類＋記錄；後續 tan 攻擊由歸屬 O 決定，唔喺本 O 推導。"]

with open(f"{REPO}/open_problems_fresh/o246_tan_sin_cos_tan_n_88/docs/03_open_scan_table.md", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

# stdout 摘要
from collections import Counter
cnt = Counter(r[0] for r in results)
print(f"A={cnt['A']} B={cnt['B']} C={cnt['C']}  總={len(results)}")
print("A 類清單（tan 最可能適用）:")
for r in results:
    if r[0] == "A":
        print(f"  {r[1]:8s} {(r[3] or '')[:58]}")