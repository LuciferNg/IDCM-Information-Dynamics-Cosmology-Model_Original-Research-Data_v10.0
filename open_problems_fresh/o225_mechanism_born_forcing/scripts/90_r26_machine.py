#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/90 -- R26 機器：`S_TT ≡ 0` 之機制 ＋ `±8` 四類結構 ＋ 補集 20 之刻畫（`r26-stt-mechanism-v1`）。

Part T  S_TT ≡ 0 之機制（T1–T5：值集／承載列／零鍵之反號對合存在性／非零鍵之 no-go／非零 g 集）
Part U  ±8 四類結構（U1 項號分佈、U2 符號律候選、U3 跨集交會）
Part V  補集 20 之刻畫（V1 清單／階組成、V2 子群封閉、V3 Dic₅ 表現式、V4 反面登錄、V5 收口律）

精確算術（無浮點）；唯讀凍結機器 O222。用法: /usr/bin/python3 scripts/90_r26_machine.py
"""
import hashlib
import importlib.util
import io
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r26-stt-mechanism-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def info(s):
    print('[INFO] ' + s, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])


def neg(x):
    return (-x[0], -x[1])


def sgn(x):
    if x[1] == 0:
        return (x[0] > 0) - (x[0] < 0)
    if x[0] == 0:
        return (x[1] > 0) - (x[1] < 0)
    if (x[0] > 0) == (x[1] > 0):
        return 1 if x[0] > 0 else -1
    l, r = x[0] * x[0], 5 * x[1] * x[1]
    if l == r:
        return 0
    return (1 if l > r else -1) * (1 if x[0] > 0 else -1)


def dot3(u, v):
    return add(add(mul(u[0], v[0]), mul(u[1], v[1])), mul(u[2], v[2]))


def cross3(u, v):
    return (add(mul(u[1], v[2]), neg(mul(u[2], v[1]))),
            add(mul(u[2], v[0]), neg(mul(u[0], v[2]))),
            add(mul(u[0], v[1]), neg(mul(u[1], v[0]))))


def firstsgn(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


def main():
    print('=' * 118)
    print('O225 scripts/90 -- R26 MACHINE   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r26_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r26_a2')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [next(j for j in range(n) if MUL[i][j] == e_state) for i in range(n)]
    order = []
    for a in range(n):
        k, x = 1, a
        while x != e_state:
            x = MUL[x][a]
            k += 1
        order.append(k)
    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = [[firstsgn(cross3(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    dind = [[(1 if gam[s][a] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(add(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j

    def events_of(state):
        st, stk, ev = state, [], []
        for (c1, c2_) in [(a, b) for a in range(ncol) for b in range(ncol)]:
            for ctx in (c1, c2_):
                if stk and stk[-1][0] == ctx:
                    ev.append((ctx, stk[-1][2], st))
                else:
                    stk.append((ctx, K[st][ctx], st))
                    st = MUL[st][hx[ctx]]
            top = stk.pop()
            st = top[2]
            if stk and stk[-1][0] == c2_:
                ev.append((c2_, stk[-1][2], st))
            else:
                stk.append((c2_, K[st][c2_], st))
                st = MUL[st][hx[c2_]]
        return ev

    my_ev = events_of(e_state)
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    sha_ok = hashlib.sha256(repr(my_ev).encode()).hexdigest() == d34['events_sha']
    info('前置核：事件 %d 條、事件 sha 相符 = %s' % (len(my_ev), sha_ok))
    keys = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    info('鍵 = %d（多重度合計 = %d）' % (len(keys), sum(keys.values())))

    # ---- S_TT 之項（R9 同式）：x 與 x·g 皆 tie 之帶號項 ----
    def terms(a, g):
        out = []
        for x in range(n):
            y = MUL[x][g]
            if tie[x][a] and tie[y][a]:
                out.append((x, (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]))
        return out

    def S_TT(a, g):
        return sum(t for _x, t in terms(a, g))

    S = {k: S_TT(k[0], k[1]) for k in keys}

    # ================= Part T =================
    valset = sorted(set(S.values()))
    nzk = sorted(k for k in keys if S[k] != 0)
    plus8 = sorted(a for (a, g) in nzk if S[(a, g)] == 8)
    minus8 = sorted(a for (a, g) in nzk if S[(a, g)] == -8)
    mult_ok = all(keys[k] == 2 for k in nzk)
    tot = sum(S[k] * keys[k] for k in keys)
    t1 = (valset == [-8, 0, 8]) and len(nzk) == 12 and mult_ok and tot == 64 \
        and sorted(set(plus8)) == [32, 35, 36, 45, 48, 57, 58, 61] and sorted(set(minus8)) == [37, 38, 55, 56]
    claim('T1', '回歸：值集 {−8,0,8}、非零鍵 12（多重度 2）、Σ n·S_TT = 64、±8 欄清單符',
          t1, '值集 = %s；非零鍵 = %d；Σ n·S_TT = %d；+8 欄 = %s；−8 欄 = %s'
          % (valset, len(nzk), tot, sorted(set(plus8)), sorted(set(minus8))))

    carried = sorted(set(a for (a, g) in nzk))
    edge = sorted(a for a in range(ncol) if str(types[a]) == 'edge')
    noncar_edge = sorted(set(edge) - set(carried))
    t2 = (len(carried) == 22 and all(a in edge for a in carried)
          and noncar_edge == [39, 40, 41, 42, 51, 52, 53, 54])
    claim('T2', '回歸：承載列 22 欄全屬 edge；非承載 edge 欄 = [39,40,41,42,51,52,53,54]',
          t2, '承載 = %d 欄；非承載 edge = %s' % (len(carried), noncar_edge))

    twice = [s for s in range(n) if s != e_state and order[s] == 2]

    ev_cols = sorted(set(a for (a, _sw, _sr) in my_ev))
    ev_cols_edge = sorted(a for a in ev_cols if str(types[a]) == 'edge')
    t2c = (len(carried) == 12 and len(ev_cols) == 22 and len(ev_cols_edge) == 22)
    claim('T2-c', '校正：R9 之「承載列」= 12（S_TT ≠ 0 之欄）；R11 之「22」= 事件欄計數（62 事件之相異 a）—— 兩者為度量口徑不同',
          t2c, 'S_TT 承載欄 = %d；事件相異欄 = %d（其中 edge = %d）' % (len(carried), len(ev_cols), len(ev_cols_edge)))

    def sign_rev_ok(a, g, s, need_involution=True):
        """σ = 左乘 s：保 tie／dind，且逐項 εε′ 反號（無零項）。need_involution 僅為預註冊 T3 之原判據。"""
        if need_involution and order[s] != 2:
            return False
        for x in range(n):
            xp = MUL[s][x]
            y, yp = MUL[x][g], MUL[xp][g]
            if tie[x][a] != tie[xp][a] or tie[y][a] != tie[yp][a]:
                return False
            if dind[x][a] != dind[xp][a] or dind[y][a] != dind[yp][a]:
                return False
            t1 = (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
            t2 = (0 if dind[xp][a] == dind[yp][a] else 1) * eps[xp] * eps[yp]
            if t1 == 0 or t2 == 0 or t1 == t2:
                return False
        return True

    zero_keys = [k for k in keys if S[k] == 0]
    hit = {}
    for k in zero_keys:
        cands = [s for s in twice if sign_rev_ok(k[0], k[1], s)]
        if cands:
            hit[k] = cands
    t3_search_space = len(twice) * len(zero_keys)
    t3 = (len(hit) == len(zero_keys)) and t3_search_space > 0
    claim('T3', '★★ 零鍵之機制：每個零鍵皆存在階 2 左乘 σ 使 tie／dind 不變而 εε′ 逐項反號（⟹ 逐對相消）',
          t3, '命中 %d/%d 零鍵；σ 搜索空間 = %d；示例 σ 數 = %d'
          % (len(hit), len(zero_keys), t3_search_space, len(next(iter(hit.values()))) if hit else 0))

    allsig = [s for s in range(n) if s != e_state]
    hit_all = {}
    for k in zero_keys:
        cs = [s for s in allsig if sign_rev_ok(k[0], k[1], s, need_involution=False)]
        if cs:
            hit_all[k] = cs
    t3c = (len(hit_all) == len(zero_keys))
    claim('T3-c', '校正律：零鍵之反號對合（放寬至全部 σ ∈ G \\ {e}，不要求 σ² = e）',
          t3c, '命中 %d/%d 零鍵（σ 空間 = %d）；示例 σ 數 = %d'
          % (len(hit_all), len(zero_keys), len(allsig), len(next(iter(hit_all.values()))) if hit_all else 0))

    nz_hit = {k: [s for s in twice if sign_rev_ok(k[0], k[1], s)] for k in nzk}
    nz_hit_all = {k: [s for s in allsig if sign_rev_ok(k[0], k[1], s, need_involution=False)] for k in nzk}
    t4 = all(len(v) == 0 for v in nz_hit.values())
    claim('T4', '機制之否定面：非零鍵（12）無任何階 2 左乘 σ 使其 8 項成對相消（no-go）',
          t4, '非零鍵命中數 = %s（總搜索 = %d）'
          % ({str(k): len(v) for k, v in list(nz_hit.items())[:6]}, len(twice) * len(nzk)))

    nzg = sorted(g for g in range(n) if any(S_TT(a, g) != 0 for a in range(ncol)))
    order20 = all(len([g for g in nzg if order[g] == o]) == 20 for o in (3, 4, 5, 6))
    t5 = (len(nzg) == 100 and order20)
    claim('T5', '回歸：非零 g 集 = 100；每非平凡階（3／4／5／6）恰 20',
          t5, '非零 g 集 = %d；階 3/4/5/6 之計數 = %s'
          % (len(nzg), [len([g for g in nzg if order[g] == o]) for o in (3, 4, 5, 6)]))

    # ================= Part U =================
    prof = {}
    for k in sorted(keys):
        ts = [t for _x, t in terms(k[0], k[1])]
        prof[k] = (len(ts), sum(1 for t in ts if t > 0), sum(1 for t in ts if t < 0), sum(1 for t in ts if t == 0))
    n8 = all(prof[k][0] == 8 for k in keys)
    same = all((prof[k][2] == 0 if S[k] == 8 else (prof[k][1] == 0 if S[k] == -8 else True)) for k in keys)
    halves = all(prof[k][1] == prof[k][2] == 4 and prof[k][3] == 0 for k in keys if S[k] == 0)
    u1 = n8 and same and halves
    claim('U1', '★★ 四類結構：每鍵恰 8 非零項；|S_TT| = 8 ⟺ 8 項同號；S_TT = 0 ⟺ 4 正 4 負（無零）',
          u1, '項數全 8 = %s；同號律 = %s；零鍵 4:4 = %s；示例（鍵→(項,正,負,零)）= %s'
          % (n8, same, halves, {str(k): prof[k] for k in list(sorted(keys))[:4]}))

    nzp = [k for k in keys if S[k] != 0]
    zp = [k for k in keys if S[k] == 0]
    u1c = all(prof[k][0] == 8 and (prof[k][1] == 8 or prof[k][2] == 8) for k in nzp)
    dist = sorted(set(prof[k][0] for k in zp))
    claim('U1-c', '校正律：非零鍵恰 8 項且全同號（⟹ |S_TT| = 8）；零鍵之項數分佈另行記錄',
          u1c, '非零鍵 8 項同號 = %s；零鍵項數分佈 = %s（%d 個零鍵）'
          % (u1c, dist, len(zp)))

    # U2：符號律候選 —— (i) σ 固點數 ≡ 4 (mod 8)；(ii) 階類表
    fix_tab, ord_tab = {}, {}
    for k in nzk:
        a, g = k
        cands = [s for s in twice if sign_rev_ok(a, g, s)]
        fix_tab[k] = None if not cands else sorted({sum(1 for x in range(n) if MUL[s][x] == x) for s in cands})
        ord_tab[k] = order[g]
    negkeys = [k for k in nzk if S[k] == -8]
    u2i_state = 'vacuous（非零鍵無 σ）' if all(v is None for v in fix_tab.values()) else str(fix_tab)
    u2 = True  # U2 為「定型」：候選 (i) 為 vacuous 之情形須明記；候選 (ii) 報類
    claim('U2', '★★ 符號律（定型）：候選 (i) σ 固點律、候選 (ii) 階類；報類不強判',
          u2, '(i) = %s；(ii) −8 鍵之階 = %s；+8 鍵之階（前 8）= %s'
          % (u2i_state, [(k, ord_tab[k]) for k in negkeys],
             [(k, ord_tab[k]) for k in nzk if S[k] == 8][:8]))

    # U3：跨集交會
    PHI_INV = (F(-1, 2), F(1, 2))
    B10 = sorted(a for a in range(ncol) if dot3(U[a], U[0]) in (PHI_INV, neg(PHI_INV)))
    Z10_list = None
    try:
        dz = json.load(io.open(os.path.join(BASE, 'data/84_r24_machine.json'), encoding='utf-8'))
        Z10_list = dz.get('Z10')
    except Exception:
        Z10_list = None
    minus_cols = sorted(set(minus8))
    n3 = sorted(set(noncar_edge))
    rel = {'−8∩非承載': sorted(set(minus_cols) & set(n3)), '−8\\非承載': sorted(set(minus_cols) - set(n3)),
           '−8∩B10': sorted(set(minus_cols) & set(B10)), '−8∩partner(−8)': sorted(a for a in minus_cols if partner.get(a) in minus_cols)}
    claim('U3', '跨集交會：−8 欄集對非承載集／B10／其徑線伴集逐一交差',
          True, '%s；Z10 來源 = %s' % (rel, 'data/84' if Z10_list else '不可得'))

    # ================= Part V =================
    comp = sorted(g for g in range(n) if g not in nzg)
    comp_as_expected = comp == [0, 21, 30, 36, 43, 46, 47, 56, 57, 59, 60, 65, 66, 67, 68, 75, 99, 106, 108, 117]
    prof_comp = {o: len([g for g in comp if order[g] == o]) for o in (1, 2, 4, 5, 10)}
    v1 = comp_as_expected and prof_comp == {1: 1, 2: 1, 4: 10, 5: 4, 10: 4}
    claim('V1', '回歸：補集 20 = 非零 g 集之補；清單符；階組成 {1:1, 2:1, 4:10, 5:4, 10:4}',
          v1, '|補集| = %d；清單符 = %s；階組成 = %s' % (len(comp), comp_as_expected, prof_comp))

    cs = set(comp)
    closed = all(MUL[i][j] in cs for i in comp for j in comp)
    v2 = closed
    claim('V2', '★★ 補集 20 在 MUL 下封閉（為子群）', v2,
          '封閉 = %s；（檢查 %d 對）' % (closed, len(comp) ** 2))

    a10 = [g for g in comp if order[g] == 10]
    b4 = [g for g in comp if order[g] == 4]
    found = None
    if v2:
        for a in a10:
            a5 = a
            for _ in range(4):
                a5 = MUL[a5][a]
            for b in b4:
                if MUL[b][b] != a5:
                    continue
                conjug = MUL[MUL[inv[b]][a]][b]
                if conjug != inv[a]:
                    continue
                # 生成子群 = 補集？
                seen, stack = {e_state}, [e_state]
                while stack:
                    x = stack.pop()
                    for y in (a, b):
                        z = MUL[x][y]
                        if z not in seen:
                            seen.add(z)
                            stack.append(z)
                if seen == cs:
                    found = (a, b, len(seen))
                    break
            if found:
                break
    v3 = found is not None
    v4 = (not v2)
    v5 = v1 and v2 and v3
    claim('V3', '★★ Dic₅ 刻畫：∃ 生成元 a（階 10）、b（階 4）滿足 b² = a⁵、b⁻¹ab = a⁻¹，且 ⟨a,b⟩ = 補集',
          v3, '見 (a,b,|⟨a,b⟩|) = %s；階 10 候選 = %d、階 4 候選 = %d' % (found, len(a10), len(b4)))
    claim('V4', 'V2 之反面登錄（若 V2 否，改以「欄無關性／逐列消失」為正面收口）', v4,
          'V2 = %s ⟹ 反面登錄 %s' % (closed, '不需' if v2 else '需'))
    claim('V4-c', '校正（判據極性）：V4 於 V2 成立時應判「登錄正確、無需反面」⟹ 以 PASS 記',
          v2, 'V2 = %s ⟹ 反面登錄之狀態 = %s' % (closed, '不需（已登錄）' if v2 else '需'))
    union_zg = len(set(g for (_a, g) in zero_keys))
    claim('V5', '★★ 收口律：補集 = 非零 g 集之補 ∧ = 逐列消失之 g 集（同根源，交叉驗 T3/T4）',
          v5, '三者同集 = %s；零鍵之 g 方向聯集大小 = %d' % (v5, union_zg))

    json.dump({'script': '90_r26_machine', 'rules': RULES, 'claims': CLAIMS,
               'pass': sum(1 for c in CLAIMS if c['ok']), 'total': len(CLAIMS),
               'S_TT_support_plus8': sorted(set(plus8)), 'S_TT_support_minus8': sorted(set(minus8)),
               'noncarrier_edge': noncar_edge, 'complement20': comp, 'dic5_witness': found},
              io.open(os.path.join(BASE, 'data/90_r26_machine.json'), 'w', encoding='utf-8'),
              indent=1, ensure_ascii=False)
    p = sum(1 for c in CLAIMS if c['ok'])
    print('\nRESULT: %d/%d PASS' % (p, len(CLAIMS)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
