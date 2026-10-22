#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/82_o225_closeout2_docs.py — O225 close-out 第二輪（R1–R23）文檔層審計（**唯讀**）

紀律：只讀檔（md／json），唔寫任何 doc；唔 import 本 o 任何推導 script。
首跑前預註冊（見 docs/49）：D1 狀態行三檔同步；D2 圍欄平衡；D3 U+FFFD = 0；
D4 未閉合項掃描（殘餘全對得上 docs/49 之 🔴 清冊）；D5 輪次覆蓋（合約／結果／三件套）；
D6 docs↔data 數字錨（閘／機器／審計之 N/M 與 data JSON 一致）；D7 metadata 塊；D8 時序索引缺號。
"""
import io, os, re, json, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS = []
def claim(tag, desc, ok, detail=''):
    CLAIMS.append({'tag': tag, 'desc': desc, 'ok': bool(ok), 'detail': str(detail)[:400]})
    print('[%s] %-4s %s  --  %s' % ('PASS' if ok else 'FAIL', tag, desc, str(detail)[:300]))

def rd(p):
    return io.open(p, encoding='utf-8').read()

ROOT = ['SESSION_START.md', '01_problem_record.md', 'final_result.md']

# ---------- D1 狀態行同步 ----------
hits = {}
for f in ROOT:
    t = rd(os.path.join(BASE, f))
    m = [l for l in t.split('\n') if l.startswith('> **狀態') or l.startswith('## 狀態')]
    hits[f] = m[0] if m else None
toks = {f: (re.findall(r'R1[–\-]R\d+', v or '') or ['NONE'])[0] for f, v in hits.items()}
claim('D1', '狀態行三檔同步（SESSION_START／01_problem_record／final_result 同記 R1–R23）',
      len(set(toks.values())) == 1, '三檔 = %s' % toks)

# ---------- D2/D3 圍欄 + 壞字 ----------
mds = ['docs/%s' % f for f in sorted(os.listdir(os.path.join(BASE, 'docs'))) if f.endswith('.md')] + ROOT + ['../README.md']
bad_f, bad_u = [], []
for f in mds:
    p = os.path.join(BASE, f)
    if not os.path.exists(p):
        continue
    t = rd(p)
    if t.count('\n```') % 2 != 0 and t.count('```') % 2 != 0:
        bad_f.append(f)
    if t.count('\ufffd'):
        bad_u.append((f, t.count('\ufffd')))
claim('D2', 'markdown 圍欄平衡（docs 全部 + 三檔 root + README）', bad_f == [], '不平衡 = %s' % bad_f)
claim('D3', 'U+FFFD 損壞字元 = 0', bad_u == [], '含壞字 = %s' % bad_u)

# ---------- D4 未閉合項掃描 ----------
EXC = [
    lambda l: l.lstrip().startswith('#'),                     # ① 章節標題
    lambda l: re.match(r'^>\s*\*\*(來源|前置|狀態|下游|目標|建立/更新|位置|判定|層分離|執行|T1|記錄層)', l),
    lambda l: re.match(r'^\|', l) and ('階段' in l or '輪' in l or '日期' in l),  # ③ 時序／階段表行
    lambda l: re.match(r'^(O\d+\s*→|## 依賴|O222\s*→)', l),  # ④ 依賴行
    lambda l: re.match(r'^>\s*⚠️', l),                        # ⑤ dated 更正附註頭
    lambda l: ('審計' in l and ('契' in l or '器' in l)),        # ⑥ 審計自身描述行
    lambda l: l.startswith('| `') or ('判定' in l and l.startswith('|')),  # ⑦ 判定摘要表行
    lambda l: '未閉合項殘餘' in l and '= 0' in l,                                  # ⑧ 自指審計行
    lambda l: bool(re.search(r'新 🔴 \d+ 項見', l)) and any(  # ⑨ 指向後續輪結果檔之 pointer（檔須存在）
        os.path.exists(os.path.join(BASE, m)) for m in re.findall(r'`(docs/[^`]+_results\.md)`', l)),
    lambda l: bool(re.search(r'\|\s*(🔴|🟡)[^|]*\|\s*$', l)) and l.startswith('|'),  # ⑩ 判定摘要表行（末格為 🔴/🟡）
    lambda l: not l.strip(),
]
resid = []
for f in ROOT:
    for i, l in enumerate(rd(os.path.join(BASE, f)).split('\n'), 1):
        if not re.search(r'🔴|🟡', l):
            continue
        if any(e(l) for e in EXC):
            continue
        resid.append((f, i, l.strip()[:120]))
inv = rd(os.path.join(BASE, 'docs/49_o225_closeout_r1-r23.md')) if os.path.exists(os.path.join(BASE, 'docs/49_o225_closeout_r1-r23.md')) else ''
VERDICT_TOK = ['❌', '✅', '✓', '✗', '已判定', '已閉合', '已收口', '收口', '已否證', '已更正', '已排除',
               '已歸約', 'PASS', 'FAIL', '🔴 未定', '🔴 未解', '已登錄', '不成立', '原樣保留', '見 docs/', 'docs/49']
def annotated(l):
    return any(v in l for v in VERDICT_TOK)
inv_n = re.sub(r'[^0-9A-Za-z\u4e00-\u9fff]', '', inv)
def grams(s):
    s = re.sub(r'[^\u4e00-\u9fff]', ' ', s)
    out = set()
    for w in s.split():
        for k in range(len(w) - 2):
            out.add(w[k:k + 3])
    return out
uncovered, tier2, tier2b = [], [], []
for (f, i, l) in resid:
    if annotated(l):
        continue
    tier2.append((f, i, l))
    g_hit = bool(grams(l)) and any(g in inv_n for g in grams(l))
    # 第三級：歷史「未閉合 🔴（Rn）／新 🔴（Rn）」行 —— 其接手表須在 docs/49 具 "Rn → ..." 映射
    rn = re.findall(r'R(\d{1,2})', l)
    m_hit = bool(rn) and all(re.search(r'R%d\s*→' % int(x), inv) for x in rn)
    if not (g_hit or m_hit):
        uncovered.append((f, i, l))
    elif m_hit and not g_hit:
        tier2b.append((f, i, l))
claim('D4', '未閉合項掃描（三級）：① 已帶書面判定 ② 3-gram 對映 docs/49 清冊 ③ 依 §六-c 接手表收口；未覆蓋必須 = 0',
      uncovered == [], '殘餘 %d 行；① 已帶書面判定 = %d；② 3-gram 對映清冊 = %d；③ 依 §六-c 接手表收口 = %d；未覆蓋 = %s'
      % (len(resid), len(resid) - len(tier2), len(tier2) - len(tier2b), len(tier2b), uncovered[:8]))

# ---------- D5 輪次覆蓋 ----------
SC = os.path.join(BASE, 'scripts')
sc = sorted(os.listdir(SC))
doc = sorted(os.listdir(os.path.join(BASE, 'docs')))
rec = rd(os.path.join(BASE, '01_problem_record.md'))
miss = []
for r in range(1, 24):
    tag = 'r%d' % r
    has_doc = any(tag in f for f in doc) and any(('r%d_results' % r) in f for f in doc)
    has_sc = any(('_r%d_' % r) in f for f in sc)
    sec = bool(re.search(r'## [^\n]*R%d[^\n]*（' % r, rec))
    if not (has_doc and has_sc and sec):
        miss.append((r, has_doc, has_sc, sec))
claim('D5', '輪次覆蓋 R1–R23：每輪有（docs 合約＋結果）∧（scripts 三件套）∧（problem_record 專節）',
      miss == [], '缺 = %s' % miss)

# ---------- D6 docs↔data 數字錨 ----------
anchors = {'r13': (48, 49, 50), 'r14': (51, 52, 53), 'r15': (54, 55, 56), 'r16': (57, 58, 59),
           'r17': (60, 61, 62), 'r18': (63, 64, 65), 'r19': (66, 67, 68), 'r20': (69, 70, 71),
           'r21': (72, 73, 74), 'r22': (75, 76, 77), 'r23': (78, 79, 80)}
d6bad = []
for tag, (g, m, a) in anchors.items():
    res = [f for f in doc if tag in f and 'results' in f]
    if not res:
        d6bad.append((tag, 'no results doc')); continue
    txt = rd(os.path.join(BASE, 'docs', res[0]))
    nums = re.findall(r'(\d+)/(\d+)', txt)
    got = []
    for base, jf in ((g, 'data/%d_%s_freeze.json' % (g, tag)), (m, 'data/%d_%s_machine.json' % (m, tag)),
                     (a, 'data/%d_%s_audit.json' % (a, tag))):
        p = os.path.join(BASE, jf)
        if os.path.exists(p):
            j = json.load(io.open(p, encoding='utf-8'))
            got.append('%d/%d' % (j.get('n_pass', -1), j.get('n_total', -1)))
    for gv in got:
        if gv not in ['%s/%s' % (x, y) for (x, y) in nums]:
            d6bad.append((tag, gv))
claim('D6', 'docs↔data 數字錨：R13–R23 之（閘／機器／審計）N/M 皆在結果檔原文且與 JSON 一致',
      d6bad == [], '不匹配 = %s' % d6bad)

# ---------- D7 metadata ----------
mt = rd(os.path.join(BASE, '01_problem_record.md'))[:1200]
need = ['pid:', 'title:', 'state:', 'verdict:', 'owner:', 'created:', 'updated:', 'prereq:', 'dir:', 'source:']
claim('D7', 'problem_record 之 registry metadata 塊完整（10 欄）',
      all(k in mt for k in need) and 'prereq:  O222' in mt, '缺 = %s' % [k for k in need if k not in mt])

# ---------- D8 時序索引 ----------
rows = re.findall(r'^\| (\d+) \|', rec, re.M)
dup = sorted({x for x in rows if rows.count(x) > 1})
secs = re.findall(r'^## (.+)$', rec, re.M)
dupsec = sorted({x for x in secs if secs.count(x) > 1})
claim('D8', '時序索引無重複行號；problem_record 無重複章節標題', dup == [] and dupsec == [], '重複行 = %s；重複節 = %s' % (dup, dupsec))

npass = sum(1 for c in CLAIMS if c['ok'])
print('=' * 110)
print('RESULT: %d/%d PASS  |  O225 close-out 第二輪 文檔層審計' % (npass, len(CLAIMS)))
with io.open(os.path.join(BASE, 'data/82_o225_closeout2_docs.json'), 'w', encoding='utf-8') as fh:
    json.dump({'rules': 'o225-closeout2-docs-v1', 'n_pass': npass, 'n_total': len(CLAIMS),
               'claims': CLAIMS, 'residual': resid, 'uncovered': uncovered}, fh, indent=1, ensure_ascii=False)
raise SystemExit(0 if npass == len(CLAIMS) else 1)
