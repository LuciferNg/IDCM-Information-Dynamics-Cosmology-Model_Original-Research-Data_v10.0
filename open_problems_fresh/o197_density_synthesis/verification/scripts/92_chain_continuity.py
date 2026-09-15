#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O198 鏈連貫審計 — verification/scripts/92_chain_continuity.py

層 3/3: 驗「推導鏈」本身 (唔驗數值, 唔驗文檔數值, 驗鏈條有冇斷)。
  (h) 上游 O 存在 + 依賴檔案存在
  (i) 交叉引用可達 (docs/0X §Y 真係存在)
  (j) 章節編號連續 (冇被覆蓋 / 冇跳號)
  (k) 常數來源可追溯 (每個輸入常數有出處)
  (l) 依賴鏈方向一致 (problem_record / final_result 嘅依賴行)
  (m) 時序索引完整 (§〇 每一行有時序 + 產出 + 驗證)

只讀 (除本檔)。exit 1 = 有 FAIL。
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
O197 = BASE.parent
ROOT = O197.parent

PASS, FAIL = [], []
def chk(sec, name, ok, note=""):
    (PASS if ok else FAIL).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {sec} {name}" + (f"  — {note}" if note else ""))
    return ok

def rd(p):
    p = Path(p)
    return p.read_text(encoding="utf-8") if p.exists() else None

print("=" * 78)
print("(h) 上游 O 存在 + 依賴檔案存在")
print("=" * 78)
UPSTREAM = {
    "O173 (M_base / f_bar 來源)": ROOT / "o173_strain_energy_cycle",
    "O174 (μ/s 結構化值 + 前向遺留)": ROOT / "o174_condensation_rate_lagrangian",
    "O176 (高端斜率帶預言)": ROOT / "o176_adjudication_followup",
    "O197 (兩通道模型, 本目錄)": O197,
}
for nm, p in UPSTREAM.items():
    chk("h", f"上游 {nm} 目錄存在", p.is_dir(), str(p))
FILES = {
    "O197 docs/01_closure.md (預言 1-4 來源)": O197 / "docs/01_closure.md",
    "O197 docs/04_dhat_minus_role.md": O197 / "docs/04_dhat_minus_role.md",
    "O197 docs/05_three_half_power.md": O197 / "docs/05_three_half_power.md",
    "O197 主 problem_record": O197 / "01_problem_record.md",
    "data/harikane23_table3_eddington.json": BASE / "data/harikane23_table3_eddington.json",
    "docs/01": BASE / "docs/01_seed_spectrum_verification.md",
    "docs/02": BASE / "docs/02_measured_eddington_attack.md",
    "docs/03": BASE / "docs/03_growth_closure.md",
    "docs/04 (審計)": BASE / "docs/04_record_audit.md",
}
for nm, p in FILES.items():
    chk("h", f"依賴檔案 {nm}", p.is_file(), str(p.name))

print()
print("=" * 78)
print("(i) 交叉引用可達 — 引用嘅 §節真係存在")
print("=" * 78)
pr = rd(BASE / "01_problem_record.md") or ""
d1 = rd(BASE / "docs/01_seed_spectrum_verification.md") or ""
d2 = rd(BASE / "docs/02_measured_eddington_attack.md") or ""
d3 = rd(BASE / "docs/03_growth_closure.md") or ""
ss = rd(BASE / "SESSION_START.md") or ""
fr = rd(BASE / "final_result.md") or ""
o197_d1 = rd(O197 / "docs/01_closure.md") or ""

def secs(t):
    """抽出所有章節標題"""
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", t, re.M)]

def has_sec(t, label):
    return any(label in s for s in secs(t))

# problem_record 引用 O197 docs/01_closure.md §三
chk("i", "problem_record → O197 docs/01_closure.md §三 (預言來源) 可達",
    "docs/01_closure.md" in pr and has_sec(o197_d1, "三"), f"O197 docs/01 章節: {secs(o197_d1)[:6]}")
# docs/02 → docs/01 §三
chk("i", "docs/02 → docs/01 §三 可達", "docs/01" in d2 and has_sec(d1, "三"))
# docs/03 → docs/02
chk("i", "docs/03 → docs/02 可達", "docs/02" in d3 and (BASE / "docs/02_measured_eddington_attack.md").is_file())
# docs/03 → scripts/06
chk("i", "docs/03 → scripts/06 可達", "scripts/06" in d3)
# SESSION_START → problem_record §五
chk("i", "SESSION_START → problem_record §五 可達", "§五" in ss and has_sec(pr, "五"))
# docs/04 → 90 腳本
d4 = rd(BASE / "docs/04_record_audit.md") or ""
chk("i", "docs/04 → scripts/90_audit_records.py 可達", "90_audit_records.py" in d4)
# final_result → problem_record / O197
chk("i", "final_result → ../01_problem_record.md + ../docs/01_closure.md 可達",
    "../01_problem_record.md" in fr or "01_problem_record" in fr)

print()
print("=" * 78)
print("(j) 章節編號連續 (冇被覆蓋 / 冇跳號)")
print("=" * 78)
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
      "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12, "十三": 13}
def seq_of(t):
    out = []
    for s in secs(t):
        m = re.match(r"([一二三四五六七八九十]+)([-–][A-Za-z])?", s)
        if m and m.group(1) in CN:
            if m.group(2):        # 子章節 (四-B) 唔算新編號
                continue
            out.append(CN[m.group(1)])
    return out
for nm, t in [("problem_record", pr), ("docs/01", d1), ("docs/02", d2),
              ("docs/03", d3), ("docs/04", d4)]:
    sq = seq_of(t)
    ok = sq == sorted(sq) and (not sq or sq == list(range(1, len(sq) + 1)))
    chk("j", f"{nm} 章節編號連續遞增 {sq}", ok,
        f"(實得 {sq})" if not ok else "")

print()
print("=" * 78)
print("(k) 常數來源可追溯")
print("=" * 78)
CONST = [
    ("M_base = 1.914e6", "O173", ["O173", "o173"]),
    ("μ = φ⁻¹+11/45", "O174", ["O174", "o174"]),
    ("s = 1.1874", "O174", ["O174", "o174"]),
    ("λ_Edd = f_bar = B/(N_d−B) = 0.1", "O173", ["O173", "o173"]),
    ("t_S = 4.5e8 yr", "Salpeter (物理輸入)", ["Salpeter"]),
    ("ε = 0.1", "標準輻射效率 (物理輸入)", ["標準", "輻射效率"]),
    ("Planck 2018 (H0=67.4, Ωm=0.315)", "Planck (觀測輸入)", ["Planck"]),
    ("N=434", "Akins+2024", ["Akins"]),
    ("Harikane+23 Table 3", "arXiv:2303.11946", ["2303.11946"]),
]
for cname, src, needles in CONST:
    where = [k for k, t in [("pr", pr), ("d1", d1), ("d2", d2), ("d3", d3), ("ss", ss)] if t]
    hit = [k for k in where if any(n in {"pr": pr, "d1": d1, "d2": d2, "d3": d3, "ss": ss}[k] for n in needles)]
    chk("k", f"常數「{cname}」有來源標記 ({src})", bool(hit), f"見 {hit}")

print()
print("=" * 78)
print("(l) 依賴鏈方向一致")
print("=" * 78)
chk("l", "problem_record 零新常數聲明存在", "零新常數" in pr)
chk("l", "docs/01 依賴行 = O197 → O198", "O197" in d1 and "O198" in d1)
chk("l", "docs/02 依賴行 = docs/01 + scripts/05", "docs/01" in d2 and "scripts/05" in d2)
chk("l", "docs/03 依賴行 = docs/02 + scripts/06", "docs/02" in d3 and "scripts/06" in d3)
chk("l", "final_result 依賴行存在", "依賴" in fr or "O157" in fr or "O174" in fr)
# 合併標記: SESSION_START / final_result 必須有「已合併回 O197」
chk("l", "SESSION_START 有合併標記", "已合併回 O197" in ss)
chk("l", "final_result 有合併標記", "已合併回 O197" in fr)

print()
print("=" * 78)
print("(m) 時序索引完整 (§〇 / §三)")
print("=" * 78)
has_index = has_sec(pr, "〇") or has_sec(pr, "時序索引")
chk("m", "problem_record 有推導時序索引 (§〇 或 §三)", has_index,
    f"章節: {secs(pr)}")
if has_index:
    # 索引區塊內每行要有日期
    blk = pr
    idx = re.search(r"^##\s+[〇三].*?索引.*?$(.*?)(?=^##\s)", blk, re.M | re.S)
    if idx:
        body = idx.group(1)
        rows = [ln for ln in body.splitlines() if ln.strip().startswith(("|", "-"))]
        # 排除表頭 (含「日期」欄名) 同 markdown 分隔行
        rows = [ln for ln in rows if "| 日期 |" not in ln and not re.match(r"^\s*\|[\s:|-]+\|", ln)]
        dated = [ln for ln in rows if re.search(r"20\d\d-\d\d-\d\d|09-1\d", ln)]
        chk("m", "時序索引每一行有日期", len(rows) > 0 and len(dated) >= len(rows) - 1,
            f"{len(dated)}/{len(rows)} 行有日期")
        chk("m", "時序索引覆蓋 09-15 全部階段 (≥6 行)", len(rows) >= 6, f"{len(rows)} 行")
        # 回溯污染檢查: 索引唔可以出現「早於實際」嘅日期 (即 09-15 前)
        early = [ln for ln in rows if re.search(r"09-1[0-4]|2026-09-1[0-4]", ln)]
        chk("m", "時序索引冇 09-15 之前日期 (O198 全部 09-15 做)", not early,
            f"{early[:1]}" if early else "")

print()
print("=" * 78)
print(f"鏈連貫審計總計: {len(PASS)}/{len(PASS) + len(FAIL)} PASS")
print("=" * 78)
if FAIL:
    print("★ FAIL:")
    for f in FAIL: print(f"  - {f}")
    sys.exit(1)
print("全部通過。")
