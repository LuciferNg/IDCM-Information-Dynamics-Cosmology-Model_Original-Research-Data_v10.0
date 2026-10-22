#!/usr/bin/env python3
"""O225 R26 合約閘（scripts/89）— 見數前凍結 docs/55 並檢預註冊完備性。

C1 合約存在並凍結（sha256）｜C2 預註冊 tag 齊（T1–T5／U1–U3／V1–V5）
C3 極性宣告齊（★★ 者）｜C4 陰陽對照（真形式在場、錯形式不在場）
C5 GATE OPEN ＋ 落 data/89_r26_freeze.json
唯讀 O222；無浮點；無擬合。
"""
import io, os, re, sys, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
O = os.path.dirname(HERE)
DOC = os.path.join(O, 'docs', '55_r26_contract.md')
DATA = os.path.join(O, 'data', '89_r26_freeze.json')

TAGS = ['T1', 'T2', 'T3', 'T4', 'T5', 'U1', 'U2', 'U3', 'V1', 'V2', 'V3', 'V4', 'V5']
# 極性須出現之詞（★ 者）
POLARITY = ['極性：存在性', '極性：**存在性**', '極性：同號', '極性：定型', '極性：是/否', '極性：同構',
            '極性：併/差', '**極性：存在性**', '**極性：是/否**', '**極性：同構**']
# 陰性對照（真形式，必在）／陽性對照（錯形式，必不在）
NEG_CTRL = ['`S_TT ∈ {−8,0,8}`', 'Dic₅', 'b⁻¹ab = a⁻¹', 'Σ_{x: 兩者皆 tie}']
POS_CTRL = ['S_TT ∈ {−8,8}', 'S_TT ≡ 8', '補集 20 ≅ A₅']


def sha256(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()


def main():
    res, ok = [], True
    if not os.path.exists(DOC):
        print('[FAIL] C1   合約不存在：%s' % DOC); return 1
    txt = io.open(DOC, encoding='utf-8').read()
    h = sha256(DOC)
    res.append(('C1', True, '合約凍結 sha256=%s bytes=%d' % (h[:16], len(txt.encode()))))

    missing = [t for t in TAGS if not re.search(r'\*\*%s\*\*' % t, txt) and ('%s（' % t) not in txt and (t + '（') not in txt]
    ok &= not missing
    res.append(('C2', not missing, '預註冊 tag %d/%d；缺 = %s' % (len(TAGS) - len(missing), len(TAGS), missing or '無')))

    star = len(re.findall(r'★★', txt))
    pol = len([m for m in re.finditer(r'極性[:：]', txt)])
    ok &= pol >= 5 and star >= 6
    res.append(('C3', pol >= 5 and star >= 6, '★★ = %d；極性宣告 = %d（需 ≥5）' % (star, pol)))

    ng = [c for c in NEG_CTRL if c in txt]
    pg = [c for c in POS_CTRL if c.replace('`', '') in txt.replace('`', '')]
    ok &= (len(ng) == len(NEG_CTRL)) and (not pg)
    res.append(('C4', (len(ng) == len(NEG_CTRL)) and (not pg),
                '陰性（真形式在場）= %d/%d；陽性（錯形式誤入）= %s' % (len(ng), len(NEG_CTRL), pg or '無')))

    gate = ok
    res.append(('C5', gate, 'GATE ' + ('OPEN' if gate else 'CLOSED')))
    print('=' * 96)
    print('O225 scripts/89 -- R26 合約閘（r26-stt-mechanism-v1）')
    print('=' * 96)
    for k, good, msg in res:
        print('[%s] %-4s %s' % ('PASS' if good else 'FAIL', k, msg))
    n = sum(1 for _, g, _ in res if g)
    io.open(DATA, 'w', encoding='utf-8').write(json.dumps(
        {'script': '89_r26_contract', 'tag': 'r26-stt-mechanism-v1', 'contract': 'docs/55_r26_contract.md',
         'sha256': h, 'checks': [{'id': k, 'ok': g, 'msg': m} for k, g, m in res],
         'gate': 'OPEN' if gate else 'CLOSED', 'pass': n, 'total': len(res)}, indent=1, ensure_ascii=False))
    print('\nRESULT: %d/%d PASS' % (n, len(res)))
    return 0 if gate else 1


if __name__ == '__main__':
    raise SystemExit(main())
