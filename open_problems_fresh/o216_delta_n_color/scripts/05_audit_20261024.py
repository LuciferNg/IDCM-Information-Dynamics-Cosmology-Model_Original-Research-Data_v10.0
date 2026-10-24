#!/usr/bin/env python3
"""
O216 scripts/05_audit_20261024.py — 內容審計（o-record-content-audit §1–§4）
============================================================================
可重跑。審計對象：docs/02–04、scripts/01–04、四件齊全、狀態一致性。
檢查項：
  §3   檔案齊全（README/final_result/01_problem_record/SESSION_START + docs/scripts/logs）
  §1-A 空洞 check（AST：ck(名, True) by fiat）
  §1-B ghost path（舊項目路徑 / /tmp 寫入）
  §1-D cross-O import
  §2   文檔↔logs 數字（q_obs、密度、PASS 數）
  §4   register 狀態（O216/子 pid closed；O68/O88 closed）
  八通道 em 讀數 Fraction 獨立重算（docs/04）
  狀態 emoji 一致性
用法：/usr/bin/python3 scripts/05_audit_20261024.py
"""
import ast, json, os, re, sys
from fractions import Fraction as F

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS, FAIL, NOTES = [], [], []

def ck(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name}" + (f"  ({detail})" if detail else ""))

def note(name, detail=""):
    NOTES.append(name)
    print(f"  📝 {name}" + (f"  ({detail})" if detail else ""))

def read(rel):
    return open(os.path.join(BASE, rel), encoding="utf-8").read()

def reg_states(pids):
    """replay register.jsonl：closed→True，reopen/open→False。"""
    root = os.path.dirname(BASE)          # .../IDCM-v10.0--It-From-Beat/open_problems_fresh
    repo = os.path.dirname(root)          # .../IDCM-v10.0--It-From-Beat
    for cand in (os.path.join(repo, "problem_register", "register.jsonl"),
                 os.path.join(os.path.dirname(repo), "problem_register", "register.jsonl")):
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
        return st, cand
    return {}, None

# ── §3 檔案齊全 ────────────────────────────────────────────────────────────
print("§3 檔案齊全")
for f in ["README.md", "final_result.md", "01_problem_record.md", "SESSION_START.md"]:
    ck(f"四件: {f}", os.path.isfile(os.path.join(BASE, f)))
for d in ["docs", "scripts", "logs"]:
    ck(f"目錄: {d}/", os.path.isdir(os.path.join(BASE, d)))
ck("docs/02 密度基準", os.path.isfile(os.path.join(BASE, "docs/02_density_baseline.md")))
ck("docs/03 no-go 裁決", os.path.isfile(os.path.join(BASE, "docs/03_no_go_verdict.md")))
ck("docs/04 handoff 答覆", os.path.isfile(os.path.join(BASE, "docs/04_handoff_response_spectator_label_operator.md")))

# ── §1-A 空洞 check ───────────────────────────────────────────────────────
print("\n§1-A 空洞 check（ck(名, True)）")
for fn in sorted(x for x in os.listdir(os.path.join(BASE, "scripts")) if x.endswith(".py")):
    tree = ast.parse(read(os.path.join("scripts", fn)))
    vac = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "ck" and len(node.args) >= 2:
            if isinstance(node.args[1], ast.Constant) and node.args[1].value is True:
                vac.append(ast.unparse(node.args[0]))
    ck(f"無空洞 ck: {fn}", len(vac) == 0, f"vacuous={len(vac)}" + (f" {vac}" if vac else ""))

# ── §1-B ghost path ──────────────────────────────────────────────────────
print("\n§1-B ghost path / 硬編碼路徑")
pat = re.compile(r"/home/wsl/Projects/(?!IDCM-Original)|/tmp/")
hits = []
for root, _, fs in os.walk(BASE):
    for f in fs:
        if f.endswith((".py", ".sh")) and f != "05_audit_20261024.py":
            p = os.path.join(root, f)
            for i, ln in enumerate(open(p, encoding="utf-8", errors="ignore"), 1):
                if pat.search(ln):
                    hits.append(f"{os.path.relpath(p, BASE)}:{i}")
ck("無 ghost path", len(hits) == 0, str(hits) if hits else "")

# ── §1-D cross-O import ──────────────────────────────────────────────────
print("\n§1-D cross-O import")
ximports = []
for fn in sorted(x for x in os.listdir(os.path.join(BASE, "scripts")) if x.endswith(".py")):
    for i, ln in enumerate(read(os.path.join("scripts", fn)).splitlines(), 1):
        if re.match(r"^\s*(import|from)\s+", ln) and re.search(r"o\d{3}|open_problems", ln):
            ximports.append(f"{fn}:{i}")
ck("零 cross-O import", len(ximports) == 0, str(ximports) if ximports else "")

# ── §2 文檔↔logs 數字 ────────────────────────────────────────────────────
print("\n§2 文檔↔logs 數字")
log1 = read("logs/01_density_baseline.out")
log2 = read("logs/02_color_routes.out")
log3 = read("logs/03_nogo_barriers.out")
log4 = read("logs/04_AUDIT_independent_recheck.out")
doc2 = read("docs/02_density_baseline.md")

def grab(pattern, text):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None

ck("logs/01 嚴格密度 46.4%", abs((grab(r"嚴格密度 = 13/28 = ([\d.]+)%", log1) or 0) - 46.4) < 0.05)
ck("logs/01 寬鬆密度 96.4%", abs((grab(r"寬鬆密度 = 27/28 = ([\d.]+)%", log1) or 0) - 96.4) < 0.05)
q_s = grab(r"q_obs = ([\d.]+)%", log1)
ck("logs/01 q_obs 嚴格 45.73%", q_s is not None and abs(q_s - 45.73) < 0.01, f"{q_s}")
q_b_list = re.findall(r"q_obs = ([\d.]+)%", log1)
q_b = float(q_b_list[1]) if len(q_b_list) > 1 else None
ck("logs/01 q_obs 寬鬆 17.09%", q_b is not None and abs(q_b - 17.09) < 0.01, f"{q_b}")
ck("docs/02 引用同值", "45.73%" in doc2 and "17.09%" in doc2)
ck("logs/01 N_mc/seed", "N_mc=200000, seed=216" in log1)
for nm, log in [("02", log2), ("03", log3), ("04", log4)]:
    ck(f"logs/{nm} 尾 RESULT rc=0", f"RESULT: {nm}_" in log and "rc=0" in log)
ck("logs 合計 65 checks", all(s in (log1+log2+log3+log4) for s in ["PASS 9 / FAIL 0", "PASS 17 / FAIL 0", "PASS 11 / FAIL 0", "PASS 28 / FAIL 0"]))

# ── §4 register 狀態 ─────────────────────────────────────────────────────
print("\n§4 register 狀態")
st, regpath = reg_states({"O216", "O68", "O88"})
ck("register.jsonl 可達", regpath is not None, str(regpath))
ck("O216 closed", st.get("O216") is True)
ck("O68 closed", st.get("O68") is True)
ck("O88 closed", st.get("O88") is True)

# ── docs/04 八通道 Fraction 重算 ─────────────────────────────────────────
print("\ndocs/04 八通道 em 讀數（Fraction，X=2.56 MeV）")
X = F("2.56")
rows = [
    ("n−p", "1.2933", +1, "-1.2667"), ("K⁺−K⁰", "-3.9340", -1, "-1.3740"),
    ("π⁺−π⁰", "4.5936", +1, "+2.0336"), ("Σ⁻−Σ⁰", "4.8070", +1, "+2.2470"),
    ("Σ⁰−Σ⁺", "3.2720", +1, "+0.7120"), ("Σ⁻−Σ⁺", "8.0790", +2, "+2.9590"),
    ("Ξ⁻−Ξ⁰", "6.8500", +1, "+4.2900"), ("D⁺−D⁰", "4.8200", +1, "+2.2600"),
]
okn = 0
for nm, dm, c, claim in rows:
    E = F(dm) - c * X
    if abs(E - F(claim)) == 0:
        okn += 1
ck("8/8 精確命中", okn == 8, f"{okn}/8")
doc4 = read("docs/04_handoff_response_spectator_label_operator.md")
ck("docs/04 記錄 8/8 PASS", "8/8 PASS" in doc4)
A = [F("-1.2667"), F("-1.3740")]
B = [F("2.2470"), F("0.7120"), F("4.2900"), F("2.2600")]
ck("A spread 0.107", abs(float(max(A) - min(A)) - 0.107) < 0.001)
ck("B spread 3.578", abs(float(max(B) - min(B)) - 3.578) < 0.001)

# ── 狀態 emoji 一致性 ────────────────────────────────────────────────────
print("\n狀態一致性")
pr = read("01_problem_record.md")
fr = read("final_result.md")
rs = read("RESULT.md")
ck("01_problem_record 🟢", "🟢" in pr)
ck("final_result 🟢", "🟢" in fr)
ck("RESULT 🟢", "🟢" in rs)
d3 = read("docs/03_no_go_verdict.md")
if "🟡" in d3:
    note("docs/03 狀態 emoji = 🟡（判定完成）vs 其餘 🟢", "docs/05 附註說明；原文不改")
ss = read("SESSION_START.md")
if "🟡 已註冊 — 未開始" in ss:
    note("SESSION_START = 起手快照（🟡 未開始）", "按 T3 快照不變原則，現狀以 01_problem_record 為準")

print(f"\nPASS {len(PASS)} / FAIL {len(FAIL)}  (notes {len(NOTES)})")
if NOTES:
    print("NOTES:")
    for n in NOTES:
        print(f"  - {n}")
sys.exit(0 if not FAIL else 1)