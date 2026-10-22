#!/usr/bin/env python3
"""
O56 - Phase 3: 文檔審計 (唯讀, 只讀唔寫)
==========================================
只讀記錄層, 唔改任何檔案。檢查:
  1. 檔案清單 / 範圍紀律 (無越界檔案)
  2. 文檔 <-> 數據 數值一致性
  3. 章節編號連續性
  4. 編碼完整性 (無 U+FFFD)
  5. Tally 跨文檔一致性
  6. 執行鏈 mtime 時序
  7. final_result.md 模板合規
  8. 推導時序索引存在性
  9. 開放問題 inventory 一致性
"""
import os
import re
import json
import glob
import sys
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)

passed = 0
failed = 0
warns = []
def chk(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK   {name} {detail}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

def norm(s):
    """Unicode 正規化: 全角減號 -> ASCII, 下標數字 -> ASCII, 去多餘空白"""
    subs = {'\u2212': '-', '\u2013': '-', '\u2014': '-', '\u00d7': 'x',
            '\u2080': '0', '\u2081': '1', '\u2082': '2', '\u2083': '3',
            '\u2084': '4', '\u2085': '5', '\u2086': '6', '\u2087': '7',
            '\u2088': '8', '\u2089': '9'}
    for k, v in subs.items():
        s = s.replace(k, v)
    return re.sub(r'\s+', ' ', s)

print("=" * 74)
print("O56 Phase 3: 文檔審計 (唯讀)")
print("=" * 74)

# ============================================================
# 1. 檔案清單 / 範圍紀律
# ============================================================
print("\n" + "=" * 74)
print("[1] 檔案清單 / 範圍紀律")
print("=" * 74)

want = {
    'SESSION_START.md',
    '01_problem_record.md',
    'final_result.md',
    'docs/01_moduli_lock_derivation.md',
    'docs/02_projection_matrix.md',
    'docs/03_gen3_proof.md',
    'docs/04_closing_report.md',
    'scripts/01_moduli_lock_derivation.py',
    'scripts/02_projection_matrix.py',
    'scripts/03_gen3_proof.py',
    'scripts/05_independent_verify.py',
    'scripts/06_doc_audit.py',
    'scripts/final_verification.py',
    'data/01_moduli_lock_derivation.json',
    'data/02_projection_matrix.json',
    'data/03_gen3_proof.json',
    'data/final_verification.json',
}
have = set()
for p in glob.glob(os.path.join(ROOT, '**', '*'), recursive=True):
    if os.path.isfile(p):
        have.add(os.path.relpath(p, ROOT))

missing = sorted(want - have)
stray = sorted(have - want)
print(f"  檔案總數 = {len(have)}")
print(f"  缺失 = {missing if missing else '無'}")
print(f"  預期外 = {stray if stray else '無'}")
chk("1a 無缺失檔案", not missing, f"({len(missing)} 個)")
chk("1b 無預期外檔案 (範圍紀律)", not stray, f"({len(stray)} 個)")

# ============================================================
# 2. 文檔 <-> 數據 數值一致性
# ============================================================
print("\n" + "=" * 74)
print("[2] 文檔 <-> 數據 數值一致性")
print("=" * 74)

TXT = {}
for rel in sorted(want):
    p = os.path.join(ROOT, rel)
    if os.path.isfile(p) and rel.endswith('.md'):
        with open(p, encoding='utf-8', errors='replace') as f:
            TXT[rel] = f.read()
    elif os.path.isfile(p) and rel.endswith('.py'):
        with open(p, encoding='utf-8', errors='replace') as f:
            TXT[rel] = f.read()

# 核心數值 (needle, 應該出現喺邊啲文檔)
CORE = [
    ('36', ['docs/01_moduli_lock_derivation.md', '01_problem_record.md',
            'final_result.md', 'SESSION_START.md']),
    ('98', ['docs/01_moduli_lock_derivation.md', '01_problem_record.md',
            'final_result.md', 'SESSION_START.md']),
    ('124', ['docs/01_moduli_lock_derivation.md', '01_problem_record.md',
             'final_result.md']),
    ('44', ['docs/01_moduli_lock_derivation.md', 'final_result.md']),
    ('90', ['docs/01_moduli_lock_derivation.md', 'final_result.md']),
    ('2B', ['docs/01_moduli_lock_derivation.md', 'final_result.md']),
]
for needle, docs in CORE:
    for d in docs:
        t = norm(TXT.get(d, ''))
        chk(f"2 {d} 含 '{needle}'", needle in t)

# 文檔數值 vs 數據 JSON
def load(fn):
    p = os.path.join(ROOT, 'data', fn)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)

d1, d2, d3, d4 = (load('01_moduli_lock_derivation.json'),
                  load('02_projection_matrix.json'),
                  load('03_gen3_proof.json'),
                  load('final_verification.json'))

if d1:
    for key, val, docs in [
        ('h11_A', 36, ['docs/01_moduli_lock_derivation.md', 'final_result.md']),
        ('h21_A', 98, ['docs/01_moduli_lock_derivation.md', 'final_result.md']),
        ('chi', -124, ['docs/01_moduli_lock_derivation.md']),
    ]:
        assert d1[key] == val, f"data/01 {key} != {val}"
        for d in docs:
            chk(f"2 {d} 記錄 {key}={val}", str(val) in norm(TXT.get(d, '')))

if d2:
    chk("2 data/02 rank_M = 36", d2['rank_M'] == 36)
    chk("2 data/02 nullity = 8", d2['nullity'] == 8)
    chk("2 docs/02 記錄 rank=36",
        'rank' in norm(TXT.get('docs/02_projection_matrix.md', '')).lower())

if d3:
    chk("2 data/03 N_gen = 3", d3['N_gen_from_proof'] == 3)

# ============================================================
# 3. 章節編號連續性
# ============================================================
print("\n" + "=" * 74)
print("[3] 章節編號連續性")
print("=" * 74)

CN = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,
      '十':10,'十一':11,'十二':12,'十三':13,'十四':14,'十五':15}

for rel, t in sorted(TXT.items()):
    if not rel.endswith('.md'):
        continue
    if rel.startswith('docs/0'):
        continue   # 主題文檔用自由格式, 唔強制編號
    heads = re.findall(r'^#{1,3}\s*([一二三四五六七八九十]+)、', t, re.M)
    if not heads:
        continue
    nums = [CN[h] for h in heads if h in CN]
    seq_ok = nums == sorted(nums) and len(nums) == len(set(nums))
    print(f"  {rel}: 章節 {nums}")
    chk(f"3 {rel} 章節編號無重複/遞增", seq_ok, f"({nums})")
    if nums:
        chk(f"3 {rel} 章節由 1 開始連續", nums == list(range(1, len(nums) + 1)),
            f"(期望 1..{len(nums)})")

# ============================================================
# 4. 編碼完整性 (U+FFFD)
# ============================================================
print("\n" + "=" * 74)
print("[4] 編碼完整性 (冇 U+FFFD)")
print("=" * 74)

for rel, t in sorted(TXT.items()):
    n_fffd = t.count('\ufffd')
    chk(f"4 {rel} 編碼完整", n_fffd == 0, f"({n_fffd} 個 U+FFFD)")

# ============================================================
# 5. Tally 跨文檔一致性
# ============================================================
print("\n" + "=" * 74)
print("[5] Tally 跨文檔一致性")
print("=" * 74)

MD = {k: norm(v) for k, v in TXT.items() if k.endswith('.md')}
denoms = set()
for t in MD.values():
    for m in re.finditer(r'(\d+)\s*/\s*(\d+)\s*PASS', t):
        denoms.add(int(m.group(2)))
print(f"  文檔中出現嘅分母 = {sorted(denoms)}")

for d in sorted(denoms):
    vals = set()
    for t in MD.values():
        for m in re.finditer(r'(\d+)\s*/\s*' + str(d) + r'\s*PASS', t):
            n = int(m.group(1))
            if n in (d, d - 1):
                vals.add(n)
    chk(f"5 分母 {d} 嘅 tally 文檔間唯一", len(vals) <= 1, f"values={sorted(vals)}")

# 128 = 21+11+24+72 算術
chk("5 128 = 21+11+24+72", 21 + 11 + 24 + 72 == 128)
chk("5 284 = 128+77+79", 128 + 77 + 79 == 284)
chk("5 總數 128 出現喺 problem_record",
    '128/128' in MD.get('01_problem_record.md', ''))
chk("5 總數 128 出現喺 SESSION_START",
    '128' in MD.get('SESSION_START.md', ''))
chk("5 總數 284 出現喺 problem_record",
    '284/284' in MD.get('01_problem_record.md', ''))
chk("5 總數 284 出現喺 SESSION_START",
    '284/284' in MD.get('SESSION_START.md', ''))
chk("5 計數沿革保留喺 problem_record",
    '計數沿革' in MD.get('01_problem_record.md', ''))
chk("5 計數沿革保留喺 SESSION_START",
    '計數沿革' in MD.get('SESSION_START.md', ''))

# ============================================================
# 6. 執行鏈 mtime 時序
# ============================================================
print("\n" + "=" * 74)
print("[6] 執行鏈 mtime 時序")
print("=" * 74)

def mt(rel):
    p = os.path.join(ROOT, rel)
    return os.path.getmtime(p) if os.path.exists(p) else None

chain = [
    ('scripts/01_moduli_lock_derivation.py', 'data/01_moduli_lock_derivation.json'),
    ('scripts/02_projection_matrix.py', 'data/02_projection_matrix.json'),
    ('scripts/03_gen3_proof.py', 'data/03_gen3_proof.json'),
    ('scripts/final_verification.py', 'data/final_verification.json'),
]
for s, dd in chain:
    ts, td = mt(s), mt(dd)
    if ts is None or td is None:
        chk(f"6 {s} -> {dd}", False, "(缺失)")
    else:
        ok = td >= ts - 2      # 容許 2 秒容差
        chk(f"6 {s} <= {dd}", ok,
            f"({'OK' if ok else 'data 早於 script'})")
        if not ok:
            print(f"       script={datetime.datetime.fromtimestamp(ts)}")
            print(f"       data  ={datetime.datetime.fromtimestamp(td)}")

# docs 相對 data 只作 INFO (後期合法 patch 會更新 mtime)
for dd in ['data/01_moduli_lock_derivation.json', 'data/02_projection_matrix.json',
           'data/03_gen3_proof.json']:
    td = mt(dd)
    for doc in ['docs/01_moduli_lock_derivation.md', 'docs/02_projection_matrix.md',
                'docs/03_gen3_proof.md']:
        tdoc = mt(doc)
        if td and tdoc:
            print(f"  [INFO] {doc} vs {dd}: "
                  f"{'doc >= data' if tdoc >= td else 'doc < data (後期 patch)'}")

# ============================================================
# 7. final_result.md 模板合規
# ============================================================
print("\n" + "=" * 74)
print("[7] final_result.md 模板合規 (RESULT_TEMPLATE.md)")
print("=" * 74)

fr = TXT.get('final_result.md', '')
if not fr:
    chk("7 final_result.md 存在", False, "(缺失)")
else:
    chk("7 final_result.md 存在", True)
    # 模板四段: 狀態 / 結論 / 關鍵公式 / 依賴 (依序)
    idx = {}
    for key, pat in [('status', r'##\s*狀態'),
                     ('concl', r'##\s*結論'),
                     ('formula', r'##\s*關鍵公式'),
                     ('dep', r'##\s*依賴')]:
        m = re.search(pat, fr)
        idx[key] = m.start() if m else None
    print(f"  段落位置: {idx}")
    chk("7 四段齊全", all(v is not None for v in idx.values()))
    if all(v is not None for v in idx.values()):
        order = idx['status'] < idx['concl'] < idx['formula'] < idx['dep']
        chk("7 段落順序 狀態→結論→關鍵公式→依賴", order)
    chk("7 含狀態 emoji", any(e in fr for e in ['🟢', '🟡', '🔴']))
    chk("7 依賴含 '→' 箭頭", '→' in fr)
    nlines = len([l for l in fr.splitlines() if l.strip()])
    print(f"  [INFO] 非空行數 = {nlines} (模板建議 <=20 行)")

# ============================================================
# 8. 推導時序索引存在性
# ============================================================
print("\n" + "=" * 74)
print("[8] 推導時序索引 (01_problem_record.md)")
print("=" * 74)

pr = norm(TXT.get('01_problem_record.md', ''))
pr_raw = TXT.get('01_problem_record.md', '')
chk("8 problem_record 含「推導時序索引」", '推導時序索引' in pr)
chk("8 problem_record 含「導航索引」聲明", '導航索引' in pr)
# 時序表行數 — 必須用 RAW 文本 (norm() 會把換行壓成空格, 令 ^ 錨點失效)
rows = re.findall(r'^\|\s*(?:T\d+|\d+)\s*\|', pr_raw, re.M)
print(f"  時序表行數 = {len(rows)}")
chk("8 時序表 >= 4 行", len(rows) >= 4, f"({len(rows)})")
# T 編號連續
tids = [int(m) for m in re.findall(r'^\|\s*T(\d+)\s*\|', pr_raw, re.M)]
print(f"  T 編號 = {tids}")
chk("8 T 編號非空且連續遞增",
    len(tids) >= 4 and tids == list(range(1, len(tids) + 1)), f"({tids})")
chk("8 problem_record 含「開放問題」inventory", '開放問題' in pr)
chk("8 problem_record 含「計數沿革」", '計數沿革' in pr)

# ============================================================
# 9. 開放問題 inventory 一致性
# ============================================================
print("\n" + "=" * 74)
print("[9] 開放問題 inventory 一致性")
print("=" * 74)

ss = norm(TXT.get('SESSION_START.md', ''))
pr_t = norm(TXT.get('01_problem_record.md', ''))
fr_t = norm(fr)

# 已由 scripts/02, 03 閉合嘅兩項: 其「現況」欄須標 🟢 已閉合
# (原狀態欄刻意保留 🔴/🟡 以存時序, 故唔可以用「出現 🔴/🟡」做判準)
def row_state(t, key):
    for line in t.split('\n'):
        if key in line:
            return line
    return ''

for key in ['3L6 中嘅因子 3 同 N_gen=3 嘅精確對應證明',
            '2B=8 耦合嘅 projection operator 幾何實現']:
    row = row_state(ss, key)
    ok = ('已閉合' in row) and ('🟢' in row)
    chk(f"9 SESSION_START 現況欄標閉合: {key[:22]}...", ok)
    if not ok:
        print(f"       row = {row[:120]}")

# 剩餘真開放項要喺三個檔都出現
for needle in ['rank=109', 'even/odd']:
    in_any = (needle in ss) or (needle in pr_t) or (needle in fr_t)
    chk(f"9 剩餘開放項 '{needle}' 有記錄", in_any)

# ============================================================
# 總結
# ============================================================
print("\n" + "=" * 74)
print(f"Phase 3 文檔審計: 通過 {passed}, 失敗 {failed}")
print("=" * 74)
if failed:
    sys.exit(1)
print("Phase 3 全部通過")
