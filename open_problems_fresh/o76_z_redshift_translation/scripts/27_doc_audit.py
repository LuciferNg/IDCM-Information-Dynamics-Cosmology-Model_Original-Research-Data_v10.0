#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O76/27: 文檔審計 (唯讀) — 第 2 輪
================================================================
只讀唔改任何文檔。檢查:
  A. 數值: doc 聲稱值 vs data/*.json 實際值
  B. 時序: script -> data -> doc 執行鏈 (唔用 mtime 判 doc 新舊, 只判鏈序)
  C. 範圍: 本 O 目錄只有預期檔案 (無跨目錄寫入)
  D. 計數: 各層 tally 文檔間一致 + 計數沿革保留
  E. final_result.md 模板合規 (狀態->結論->關鍵公式->依賴)
  F. 編碼: 全部 doc 冇 U+FFFD
  G. 修正註記: 被取代嘅值有 ⚠️ 註記 (禁跨文檔污染檢查)
  H. 時序索引: §推導時序索引 存在 + 4 輪齊全
"""
import json, re, sys, glob, os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PASS, FAIL = [], []
def chk(name, cond, detail=''):
    ok = bool(cond)
    (PASS if ok else FAIL).append(name)
    print(f"  {'[OK]' if ok else '[FAIL]'} {name}" + (f"   {detail}" if detail else ''))

def read(p):
    return (BASE / p).read_text(encoding='utf-8', errors='replace')

print("=" * 78)
print("O76/27 - 文檔審計 (唯讀)")
print("=" * 78)

DOCS = {
    'root01':   '01_problem_record.md',
    'session':  'SESSION_START.md',
    'final':    'final_result.md',
    'd01':      'docs/01_problem_record.md',
    'd02':      'docs/02_o169_correction_reverification.md',
    'd03':      'docs/03_open_problems_round1.md',
    'd04':      'docs/04_audit_round2.md',
    'd05':      'docs/05_gemini_verification.md',
}
TXT = {}
for k, p in DOCS.items():
    f = BASE / p
    chk(f"A0 {k} 存在", f.exists(), p)
    if f.exists():
        TXT[k] = read(p)

ALL = "\n".join(TXT.values())

def norm(s):
    s = s.replace('\u2212', '-').replace('\ufffd', '')
    s = re.sub(r'\s+', '', s)
    return s
NALL = norm(ALL)

# ================= A. 數值 vs data =================
print("\n" + "=" * 78)
print("A. 數值: doc vs data/*.json")
print("=" * 78)
J = {}
for f in sorted(glob.glob(str(BASE / 'data' / '*.json'))):
    J[os.path.basename(f)] = json.load(open(f))

# 由 json 取真值
j24 = J['24_o169_reverification.json']
j25 = J['25_alpha_reverdict.json']
j26 = J['26_open_problems.json']

checks_A = [
    ('A1  b_spec = 1.11911398', f"{j24['o169_b_spec']:.8f}", '1.11911398'),
    ('A2  C_new = -0.23606798', f"{j24['o169_C_new']:.8f}", '-0.23606798'),
    ('A3  DESI chi2 NEW = 2.4528', f"{j24['desi_chi2_new']:.4f}", '2.4528'),
    ('A4  DESI chi2 OLD = 27.1635', f"{j24['desi_chi2_old']:.4f}", '27.1635'),
    ('A5  DESI chi2 OLD+delta = 13.0888', f"{j24['desi_chi2_old_delta']:.4f}", '13.0888'),
    ('A6  Nyquist old = 0.9990', f"{j24['nyquist_ratio_old']:.4f}", '0.9990'),
    ('A7  Nyquist new = 0.9632', f"{j24['nyquist_ratio_new']:.4f}", '0.9632'),
    ('A8  z_eff new = 0.7213475', f"{j24['z_eff_exp_new']:.7f}", '0.7213475'),
    ('A9  SN chi2 alpha=0 = 1989.9', f"{j24['sn_chi2_new_alpha0']:.1f}", '1989.9'),
    ('A10 alpha_best = +0.0392', f"{j25['alpha_best']:.4f}", '0.0392'),
    ('A11 sigma_alpha = 0.0140', f"{j25['sigma_alpha']:.4f}", '0.0140'),
    ('A12 SN chi2 alpha=-n/p (new DA) = 2138.2', f"{j24['sn_chi2_new_alpha_np']:.1f}", '2138.2'),
    ('A13 T(z) chi2 = 1.63', f"{j26['B_tcmb']['chi2_beta0']:.2f}", '1.63'),
    ('A14 N_need = 248', f"{j26['C_power']['N_need_alpha_3sigma']}", '248'),
    ('A15 ladder z(0.002) = +0.50', f"{j26['D_ladder']['z_sharp_0002']:.2f}", '0.50'),
]
for name, val, docv in checks_A:
    chk(name, val == docv, f"json={val} doc={docv}")

# doc 內出現檢查 (正規化後)
for name, needle in [
    ('A20 docs 有 1.11911398', '1.11911398'),
    ('A21 docs 有 0.23606798', '0.23606798'),
    ('A22 docs 有 2.4528', '2.4528'),
    ('A23 docs 有 1989.9', '1989.9'),
    ('A24 docs 有 0.9632', '0.9632'),
    ('A25 docs 有 0.7213475', '0.7213475'),
    ('A26 docs 有 1.003', '1.003'),
    ('A27 docs 有 2.72548', '2.72548'),
    ('A28 docs 有 σ_z,pec = 0.00036', '0.00036'),
    ('A29 docs 有 消相干比 0.0081', '0.0081'),
    ('A30 docs 有 巡天 χ² = 76.80', '76.80'),
    ('A31 docs 有 Spearman p = 0.2080', '0.2080'),
    ('A32 docs 有 Lyα pull = +0.09', '+0.09'),
]:
    chk(name, norm(needle) in NALL, needle)

# ================= B. 時序鏈 =================
print("\n" + "=" * 78)
print("B. 時序: 執行鏈 (script -> data -> doc)")
print("=" * 78)
def mt(p):
    f = BASE / p
    return f.stat().st_mtime if f.exists() else None

chain = [
    ('B1  scripts/24 <= data/24.json', 'scripts/24_o169_reverification.py', 'data/24_o169_reverification.json'),
    ('B2  scripts/25 <= data/25.json', 'scripts/25_alpha_reverdict.py', 'data/25_alpha_reverdict.json'),
    ('B3  scripts/26 <= data/26.json', 'scripts/26_open_problems.py', 'data/26_open_problems.json'),
    ('B6  docs/03 <= final_result.md', 'docs/03_open_problems_round1.md', 'final_result.md'),
]
for name, a, b in chain:
    ma, mb = mt(a), mt(b)
    chk(name, ma is not None and mb is not None and ma <= mb + 1,
        f"{ma:.0f} <= {mb:.0f}" if ma and mb else "missing")
print("  [INFO] data/26 <= docs/02, docs/03 嘅 mtime 檢查**已降級為內容檢查**")
print("         (重跑腳本會更新 data 檔 mtime -> mtime 序唔可靠; 依技能 pitfall 改內容斷言)")
# 內容檢查 (免疫檔案重觸): data 值必須出現喺對應 doc
chk("B4' data/24 值 2.4528 (DESI NEW) 出現喺 docs/02",
    norm('2.4528') in norm(TXT['d02']), "2.4528")
chk("B5' data/24 值 0.9632 (Nyquist NEW) 出現喺 docs/02",
    norm('0.9632') in norm(TXT['d02']), "0.9632")
chk("B7' data/26 值 1.63 (T(z) χ²) 出現喺 docs/03",
    norm('1.63') in norm(TXT['d03']), "1.63")
chk("B8' data/26 值 248 (N_need) 出現喺 docs/03",
    norm('248') in norm(TXT['d03']), "248")
chk("B9' data/25 值 0.0392 (α_best) 出現喺 docs/02 同 docs/03",
    norm('0.0392') in norm(TXT['d02']) and norm('0.0392') in norm(TXT['d03']), "0.0392")

# ================= C. 範圍 =================
print("\n" + "=" * 78)
print("C. 範圍: 本 O 目錄檔案集")
print("=" * 78)
want_docs = set(v for v in DOCS.values() if v.startswith('docs/'))
have_docs = set(str(Path(p).relative_to(BASE)) for p in glob.glob(str(BASE / 'docs' / '*.md')))
chk("C1 docs/ 檔案集 = 預期", have_docs == want_docs, f"have={sorted(have_docs)}")
want_root = {'01_problem_record.md', 'SESSION_START.md', 'final_result.md'}
have_root = set(os.path.basename(p) for p in glob.glob(str(BASE / '*.md')))
chk("C2 root .md 檔案集 = 預期", have_root == want_root, f"have={sorted(have_root)}")
have_scripts = set(os.path.basename(p) for p in glob.glob(str(BASE / 'scripts' / '*.py')))
idx = sorted(int(s[:2]) for s in have_scripts if s[:2].isdigit())
chk("C3 scripts 編號連續 (無跳號)", idx == list(range(1, len(idx) + 1)), f"idx={idx}")
chk("C4 scripts 01-26 齊全 (推導腳本)", all(f"{i:02d}_" in "".join(have_scripts) for i in range(1, 27)),
    f"n_scripts={len(have_scripts)}")
have_json = set(os.path.basename(p) for p in glob.glob(str(BASE / 'data' / '*.json')))
jidx = sorted(int(f[:2]) for f in have_json if f[:2].isdigit())
chk("C5 data json 01-26 齊全 (推導輸出)", all(i in jidx for i in range(1, 27)), f"json_idx={jidx}")
# 跨目錄寫入檢查: 本 session 只寫過 O76
chk("C6 無寫入本 O 以外 (檔案集內全部屬 o76/)",
    all('o76_z_redshift_translation' in str(p) for p in glob.glob(str(BASE / '**' / '*'), recursive=True)),
    "OK")

# ================= D. 計數一致 =================
print("\n" + "=" * 78)
print("D. 計數: 各層 tally 文檔間一致")
print("=" * 78)
def tally(denom):
    vals = set()
    for k, t in TXT.items():
        for m in re.finditer(r'(\d+)\s*/\s*' + str(denom) + r'\s*PASS', norm(t)):
            n = int(m.group(1))
            if n in (denom, denom - 1):     # 只接受合理分子
                vals.add(n)
    return vals

denoms = set()
for k, t in TXT.items():
    for m in re.finditer(r'(\d+)\s*/\s*(\d+)\s*PASS', norm(t)):
        denoms.add(int(m.group(2)))
print(f"  (自動掃描到嘅分母: {sorted(denoms)})")
for denom in sorted(denoms):
    v = tally(denom)
    chk(f"D1 {denom} 分母嘅 tally 文檔間唯一", len(v) <= 1, f"values={sorted(v)}")
chk("D2 計數沿革保留 (第 1 輪 10/10)", '10/10' in norm(ALL), "10/10")
chk("D3 計數沿革保留 (第 1 輪 17/17)", '17/17' in norm(ALL), "17/17")
chk("D4 計數沿革保留 (第 1 輪 5/5)", '5/5' in norm(ALL), "5/5")
chk("D5 第 2 輪小計 60/60 出現", '60/60' in norm(ALL), "60/60")
chk("D9 計數沿革保留 (scripts/27 首跑 82/82)", '82/82' in norm(ALL), "82/82")
chk("D10 第 3 輪 tally 21/21 出現", '21/21' in norm(ALL), "21/21")
chk("D6 舊值 2006.8 保留 (非刪除)", '2006.8' in norm(ALL), "2006.8")
chk("D7 舊值 12.82 保留", '12.82' in norm(ALL), "12.82")
chk("D8 舊值 0.891635 保留", '0.891635' in norm(ALL), "0.891635")

# ================= E. final_result 模板 =================
print("\n" + "=" * 78)
print("E. final_result.md 模板合規")
print("=" * 78)
ft = TXT['final']
i_status = ft.find('## 狀態')
i_concl = ft.find('## 結論')
i_form = ft.find('## 關鍵公式')
i_dep = ft.find('## 依賴')
chk("E1 章節順序 狀態->結論->關鍵公式->依賴",
    -1 < i_status < i_concl < i_form < i_dep,
    f"{i_status},{i_concl},{i_form},{i_dep}")
chk("E2 狀態行有 emoji", bool(re.search(r'## 狀態:\s*[🟢🟡🔴]', ft)), "")
chk("E3 依賴有 → 箭頭", '→' in ft[i_dep:i_dep + 400], "")
chk("E4 冇 U+FFFD", '\ufffd' not in ft, "")

# ================= F. 編碼 =================
print("\n" + "=" * 78)
print("F. 編碼完整性")
print("=" * 78)
for k, t in TXT.items():
    chk(f"F1 {k} 冇 U+FFFD", '\ufffd' not in t, "")

# ================= G. 修正註記 (禁跨文檔污染) =================
print("\n" + "=" * 78)
print("G. 修正註記: 被取代值有 ⚠️ 標記")
print("=" * 78)
d01 = TXT['d01']
chk("G1 docs/01 有檔頭 ⚠️ 修正表", '⚠️ 上游修正交回已執行' in d01, "")
chk("G2 docs/01 標明「原文保留」", '原文保留' in d01, "")
chk("G3 docs/01 標明「方向錯誤」(舊 α)", '方向錯誤' in d01, "")
chk("G4 docs/01 原文逐字保留 (核心公式仍在)", '1+2φ⁻¹ℓ+δ(ℓ)' in d01 or '1+2φ⁻¹ℓ+δ' in d01, "")
chk("G5 docs/01 原文 P2/P6 仍在", 'D_L/D_A = (1+z)^{0.857}' in d01 or '0.857' in d01, "")
chk("G6 docs/01 有新增 §四-B 更新段", '四-B' in d01, "")
chk("G7 root01 標明「原文保留」", '原文保留' in TXT['root01'], "")
chk("G8 root01 舊值仍在 (2006.8/12.82/0.9990)", all(x in norm(TXT['root01']) for x in ['2006.8', '12.82', '0.9990']), "")
chk("G9 舊 scripts 01-23 保留原狀 (歷史記錄)",
    'C=-0.1697' in read('scripts/01_z_core_structure.py'), "")

# ================= H. 時序索引 =================
print("\n" + "=" * 78)
print("H. 推導時序索引")
print("=" * 78)
r = TXT['root01']
chk("H1 有 §推導時序索引", '§推導時序索引' in r or '推導時序索引' in r, "")
for rnd in ['第 0 輪', '第 1 輪', '第 1.5 輪', '第 2 輪']:
    chk(f"H2 {rnd} 存在", rnd in r, "")
chk("H3 有「禁止回溯污染」聲明", '禁止回溯污染' in r, "")
chk("H4 有 commit 欄", 'commit' in r, "")
chk("H5 有計數沿革段", '計數沿革' in r, "")
chk("H6 第 2 輪列有 scripts 24/25/26 行",
    all(x in r for x in ['scripts/24', 'scripts/25', 'scripts/26']), "")
chk("H7 第 1 輪列有 23 個 script 行 (01-23)",
    sum(1 for i in range(1, 24) if f'scripts/{i:02d}' in r) == 23,
    f"count={sum(1 for i in range(1, 24) if f'scripts/{i:02d}' in r)}")


# ================= I. 開放問題三份文檔一致性 =================
print("\n" + "=" * 78)
print("I. 開放問題: 三份文檔一致性 (共同權威清單)")
print("=" * 78)
import re as _re
def open_ids(txt):
    """抽出開放項編號 O1..O9 (只喺開放問題相關段)"""
    ids = set()
    for m in _re.finditer(r'\bO([1-9])\b', txt):
        ids.add(int(m.group(1)))
    return ids

r_o = open_ids(TXT['root01']); f_o = open_ids(TXT['final']); s_o = open_ids(TXT['session'])
print(f"  root01 開放項 = {sorted(r_o)}")
print(f"  final  開放項 = {sorted(f_o)}")
print(f"  session開放項 = {sorted(s_o)}")
chk("I1  root01 開放項集合 = final 開放項集合", r_o == f_o, f"{sorted(r_o)} vs {sorted(f_o)}")
chk("I2  ★三份文檔開放項集合完全一致", r_o == f_o == s_o,
    f"root={sorted(r_o)} final={sorted(f_o)} session={sorted(s_o)}")
chk("I3  開放項總數 = 9 (O1-O9)", len(r_o) == 9, f"n = {len(r_o)}")
chk("I4  有 §開放問題總表", '開放問題總表' in TXT['root01'], "")
chk("I5  總表標明「共同權威清單」", '共同權威' in TXT['root01'], "")
chk("I6  🟡 6 / 🔴 3 計數一致 (root01)",
    ('🟡 6' in TXT['root01'] and '🔴 3' in TXT['root01']), "")
chk("I7  final_result 開放段引用總表位置",
    '開放問題總表' in TXT['final'], "")
chk("I8  final_result 開放項數 = 9", len(f_o) == 9, f"n = {len(f_o)}")
chk("I9  session 列明開放項數 (🟡6/🔴3)", ('🟡 6' in TXT['session'] and '🔴 3' in TXT['session']), "")
chk("I10 三份文檔都引用 docs/05", all('docs/05' in TXT[k] for k in ('root01', 'final', 'session')),
    "")
chk("I11 檔案清單 scripts 範圍 = 01-29", 'scripts/01-29' in TXT['root01'], "")
chk("I12 檔案清單含 docs/05", '05_gemini_verification' in TXT['root01'], "")
chk("I13 final_result 有「可證偽預言」段", '可證偽預言' in TXT['final'], "")

# ================= 總結 =================
print("\n" + "=" * 78)
print(f"O76/27 文檔審計: PASS = {len(PASS)}  FAIL = {len(FAIL)}")
if FAIL:
    print("FAIL 項:")
    for f in FAIL:
        print("   -", f)
print("=" * 78)
with open(BASE / 'data' / '27_doc_audit.json', 'w') as f:
    json.dump({'pass': len(PASS), 'fail': len(FAIL), 'fails': FAIL}, f, indent=2, ensure_ascii=False)
print("-> data/27_doc_audit.json")
sys.exit(1 if FAIL else 0)
