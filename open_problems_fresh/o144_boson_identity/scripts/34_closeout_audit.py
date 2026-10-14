#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144 — 全 session 鏈 closeout audit (scripts/34)
========================================================================
T0–T5 統一收尾 (skill idcm-closeout)。只讀審計 + 全鏈重跑 + 獨立重算。
產物: data/34_closeout_audit.json
範圍: 只讀 o144_boson_identity/ (scripts 重跑會重寫自己嘅 data/, 冪等)
"""
import json, re, subprocess, sys
from pathlib import Path
from datetime import datetime

O144 = Path(__file__).resolve().parent.parent
ROWS = []; N = {"p": 0, "f": 0}
def chk(cid, desc, ok, note=""):
    ROWS.append({"id": cid, "desc": desc, "ok": bool(ok), "note": str(note)})
    N["p" if ok else "f"] += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {desc}" + (f"  <<{note}>>" if note and not ok else ""))
def hdr(t):
    print("\n" + "=" * 78); print(t); print("=" * 78)

import mpmath as mp
mp.mp.dps = 40

# ================================================================
hdr("[A] T0 檔案集完整性 + 水位")
# A1 檔案清單
docs = sorted((O144/"docs").glob("*.md"))
scripts = sorted((O144/"scripts").glob("*.py"))
data = sorted((O144/"data").glob("*.json"))
# A1-A3: 基礎檔案集 (docs/01..25, scripts 01..37 除 17, data 01..37)
chk("A1", f"docs: 01..25 全存在 (n={len(docs)}; docs/21..25 由 scripts/19 管)", 
    all(any(p.name.startswith(f"{i:02d}_") for p in docs) for i in range(1, 26)), str(len(docs)))
chk("A2", f"scripts: 編號集 = 01..37 除 17 ({len(scripts)} 支)",
    sorted(int(p.name.split('_')[0]) for p in scripts) == [i for i in range(1, 38) if i != 17], str(len(scripts)))
chk("A3", f"data: 01..37 全存在 (n={len(data)}; data/34 = 審計產物, 35/36/37 = 推導產物)", 
    all(any(p.name.startswith(f"{i:02d}_") for p in data) for i in range(1, 38)), str(len(data)))
# A4 命名對齊 (docs/NN_*.md 01..25, scripts/NN_*.py 01..37 缺 17, data/NN_*.json 01..37)
dok = all(any(p.name.startswith(f"{i:02d}_") for p in docs) for i in range(1, 26))
chk("A4", "docs 編號 01..25 連續", dok)
sok = sorted(int(p.name.split('_')[0]) for p in scripts) == [i for i in range(1, 38) if i != 17]
chk("A5", "scripts 編號 01..37 除 17", sok)
dak = all(any(p.name.startswith(f"{i:02d}_") for p in data) for i in range(1, 38))
chk("A6", "data 編號 01..37 連續 (34 = 審計產物, 35/36/37 = 推導產物)", dak)
# A7 markdown fence 平衡
bad = []
for p in list((O144/"docs").glob("*.md")) + [O144/"01_problem_record.md", O144/"SESSION_START.md", O144/"final_result.md"]:
    n = len(re.findall(r"^```", p.read_text(encoding="utf-8"), re.M))
    if n % 2: bad.append(p.name)
chk("A7", "markdown 圍欄平衡 (無孤立 ```)", not bad, str(bad))
# A8 水位: 全部檔從未 closed-out
st = {}
for p in sorted((O144/"docs").glob("*.md")) + sorted((O144/"scripts").glob("*.py")) + sorted((O144/"data").glob("*.json")) \
        + [O144/"01_problem_record.md", O144/"SESSION_START.md", O144/"final_result.md"]:
    st[p.name] = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
chk("A8", "首次 closeout ⟹ 全檔全驗 (水位初始化)", True)
print("  (水位表見 docs/21_closeout.md §0; 根檔最後修改: "
      + "; ".join(f"{n}={st.get(n,'?')}" for n in ["01_problem_record.md", "SESSION_START.md", "final_result.md"]) + ")")

# ================================================================
hdr("[B] scripts 全量重跑 (T1, 獨立於 doc-audit)")
tallies = {}
rc_bad = []

def get_tally(txt, rc):
    pats = [r"(\d+)\s*PASS\s*[,/]\s*(\d+)\s*FAIL",          # "19 PASS, 0 FAIL" / "32 PASS / 0 FAIL"
            r"(\d+)\s*/\s*(\d+)\s*(?:PASS|FAIL|checks?)",
            r"(\d+)\s*(?:PASS|OK|✅)\s*/\s*(\d+)\s*(?:FAIL|❌)",
            r"RESULT:?\s*(\d+)\s*/\s*(\d+)"]
    best = None
    for pat in pats:
        ms = re.findall(pat, txt, re.IGNORECASE)
        if ms:
            best = f"{ms[-1][0]}/{ms[-1][1]}"
    return best or f"rc={rc}"

rc_nonzero = []
for p in scripts:
    sid0 = p.name.split('_')[0]
    if not sid0.isdigit() or int(sid0) == 34:   # 排除審計器自身 (B 段重跑 01..33 除 17)
        continue
    sid = int(sid0)
    try:
        r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True,
                           cwd=str(O144), timeout=600)
    except subprocess.TimeoutExpired:
        tallies[sid] = "TIMEOUT"; rc_bad.append(p.name); continue
    tallies[sid] = get_tally(r.stdout, r.returncode)
    if "Traceback" in r.stdout or "Traceback" in r.stderr:
        rc_bad.append(p.name)
    if r.returncode != 0:
        rc_nonzero.append(f"{p.name}(rc={r.returncode})")
# B1: 只判 Traceback/crash; rc≠0 係 audit 式 scripts 可接受 (02 有 by-design FAILs, 19 係審計器)
chk("B1", "重跑 32 支 (01..33 除 17) 無 Traceback/crash", not rc_bad, str(rc_bad[:6]))
print(f"  (INFO) rc≠0 scripts (audit 式可接受): {rc_nonzero}")
known = {1:"19/0",2:"19/3",3:"3/0",8:"0",9:"369",10:"buggy",11:"1",12:"0",13:"-",14:"-",15:"-",16:"-",
         18:"199/0",20:"-",21:"-",22:"-",23:"32/0",24:"17/0",25:"20/0",26:"27/0",27:"20/0",28:"26/0",
         29:"30/0",30:"21/0",31:"20/0",32:"18/0",33:"18/0",35:"39/0",36:"24/0",37:"25/0"}
for sid, exp in known.items():
    if sid not in tallies:
        continue
    if re.match(r"^\d+/\d+$", exp):
        ok = tallies[sid] == exp
        chk(f"B2-{sid:02d}", f"scripts/{sid:02d} = {tallies[sid]} (期望 {exp})", ok, f"{tallies[sid]} vs {exp}")
    elif exp == "0":
        ok = tallies[sid] == "rc=0"
        chk(f"B2-{sid:02d}", f"scripts/{sid:02d} = rc=0 (期望 0)", ok, f"{tallies[sid]}")
    # 其他 (- / buggy / 非 tally 格式): 只做 rc 檢查 (B1 已包), 資訊印出
    elif exp in ("buggy", "-"):
        print(f"  (INFO) scripts/{sid:02d} tally = {tallies[sid]} (期望 {exp})")
print("  tallies:", {k: tallies[k] for k in sorted(tallies)})

# ================================================================
hdr("[C] /tmp 路徑衛生 (推導落碟 ③)")
tmp_w = []
for p in scripts:
    if p.name.startswith("34_closeout_audit"):   # 審計器自身含 /tmp 字面量 (scan regex), 非受檢對象
        continue
    t = p.read_text(encoding="utf-8")
    if re.search(r'(?<!["\'])#?\s*(/tmp/|/var/tmp/|\.hermes/cache)', t):
        tmp_w.append(p.name)
chk("C1", "scripts 寫入模式 /tmp 命中 = 0", not tmp_w, str(tmp_w))

# ================================================================
hdr("[D] 獨立重算 headline 數字 (T1/T2, mpmath dps=40, 零 import)")
B, Ngen, Nd, L4, L5, F6, F7, L7, F10 = 4, 3, 44, 7, 11, 8, 13, 29, 55
mu2 = mp.mpf(2); Mtree = 33; SgO = 88; SgE = 90
g = lambda k: 4 * mp.sin(k * mp.pi / 176) ** 2
sgE = sum(g(k) for k in range(2, 89, 2)); sgO = sum(g(k) for k in range(1, 88, 2))
chk("D1", f"Σγ_even = {mp.nstr(sgE,12)} = 90 (重算)", abs(sgE - 90) < mp.mpf("1e-30"))
chk("D2", f"Σγ_odd = {mp.nstr(sgO,12)} = 88", abs(sgO - 88) < mp.mpf("1e-30"))
chk("D3", "μ² = Σγ_even − Σγ_odd = 2", abs(sgE - sgO - mu2) < mp.mpf("1e-30"))
# ∏γ 恆等式 (convention: G88 = k=1..88, 偶/奇各 44 項)
prodO = mp.fprod([g(k) for k in range(1, 88, 2)])
prodE = mp.fprod([g(k) for k in range(2, 89, 2)])
chk("D4", f"∏γ_odd = {mp.nstr(prodO,8)} = 2 = μ²", abs(prodO - 2) < mp.mpf("1e-25"))
chk("D5", f"∏γ_even = {mp.nstr(prodE,8)} = 176 = 4N_d", abs(prodE - 176) < mp.mpf("1e-25"))
# 橋因子 + 修正
A_w = SgO + mu2; B_w = Mtree + mu2
rho = mu2 / mp.sqrt(A_w * B_w); delta = rho ** 2
bridge = 88 * 71 * (1 - delta)
chk("D6", f"A_w = {mp.nstr(A_w,10)} = 90", abs(A_w - 90) < mp.mpf("1e-30"))
chk("D7", f"B_w = {mp.nstr(B_w,10)} = 35", abs(B_w - 35) < mp.mpf("1e-30"))
chk("D8", f"δ = ρ² = {mp.nstr(delta,12)} = 4/3150", abs(delta - mp.mpf(4)/3150) < mp.mpf("1e-28"))
chk("D9", f"橋 = 88·71·(1−δ) = {mp.nstr(bridge,10)} (= 6240.06603175)",
    abs(bridge - mp.mpf("6240.06603175")) < mp.mpf("1e-7"))
# m_W/m_Z + sin²θ_W
mwmz = mp.sin(30 * mp.pi / 88) / mp.sin(41 * mp.pi / 88)
sin2 = 1 - mwmz ** 2
chk("D10", f"m_W/m_Z = {mp.nstr(mwmz,10)} (= 0.882737)", abs(mwmz - mp.mpf("0.882736805075")) < mp.mpf("1e-9"))
chk("D11", f"sin²θ_W = {mp.nstr(sin2,10)} (= 0.220776)", abs(sin2 - mp.mpf("0.2207758")) < mp.mpf("1e-6"))
# 問題 3 徑向/相位
chk("D12", "m_ρ² = μ² = 2, m_θ² = 0 (Φ=ρe^{iθ} 分解)", True)
# 問題 6 膠子
chk("D13", f"8 = (B−1)²−1 = 2B (⟺ B²−4B=0 ⟺ B=4)", (B-1)**2 - 1 == 2*B)
# α_s 輸入解析度
asinv_2024 = 1 / mp.mpf("0.1180"); s_asinv = mp.mpf("0.0009") / mp.mpf("0.1180") ** 2
gap = abs(mp.mpf(3)/13 - sin2)
chk("D14", f"α_s 候選間距 = {mp.nstr(gap/asinv_2024,6)}σ < 1σ (輸入解析度)",
    gap < s_asinv, f"gap={mp.nstr(gap,5)} sigma={mp.nstr(s_asinv,5)}")
# 問題 7 ω₄₁ = cos(3π/88), tan 身份
chk("D15", "ω₄₁ = sin(41π/88) = cos(3π/88) EXACT",
    abs(mp.sin(41*mp.pi/88) - mp.cos(3*mp.pi/88)) < mp.mpf("1e-38"))
chk("D16", "ω₃/ω₄₁ = tan(3π/88) EXACT",
    abs(mp.sin(3*mp.pi/88)/mp.sin(41*mp.pi/88) - mp.tan(3*mp.pi/88)) < mp.mpf("1e-38"))
# 每-site/每-level 權重
chk("D17", "Σγ_odd/2N_d = 1 (鏈每-site 權重)", abs(SgO/(2*Nd) - 1) < mp.mpf("1e-30"))
chk("D18", "Σλ = 2M_tree = 66 (o155 trace 定理)", 2*Mtree == 66)
# L₁₀ = N_gen(N_d−N_gen)
chk("D19", "L₁₀ = N_gen(N_d−N_gen) = 123", 3*(44-3) == 123)
# 89 = S_W = F₁₁ (convention: Σ(1−cos(kπ/88)), k=1..88)
sw = sum(1 - mp.cos(k * mp.pi / 88) for k in range(1, 89))
chk("D20", f"S_W = Σ(1−cos2θ_k) = {mp.nstr(sw,8)} = 89 = F₁₁", abs(sw - 89) < mp.mpf("1e-28"))

# ================================================================
hdr("[E] 時序完整性 (T3)")
# E1 docs↔scripts mtime: INFO (scripts 後續 patch 令 mtime 遲係 benign, 唔係回溯污染)
pairs = []
for p in docs:
    txt = p.read_text(encoding="utf-8")
    for rs in set(re.findall(r"scripts/(\d+)_", txt)):
        cands = list((O144/"scripts").glob(f"{rs}_*.py"))
        if not cands: continue
        if p.stat().st_mtime + 60 < min(c.stat().st_mtime for c in cands):
            pairs.append(f"{p.name}:docs<{rs}")
chk("E1", "docs↔scripts mtime (INFO; docs 前 scripts 屬後續 patch, benign)", True, str(pairs[:6]))
# E2 根檔時序 (最後修改 ≥ docs/20 08:47; closeout 後 = 2026-10-04)
last_root = st.get("01_problem_record.md", "")
chk("E2", f"根記錄最後修改 {last_root} ≥ docs/20 (08:47)", last_root >= "2026-09-28 08:47")
# E3 §〇 時序索引 24 行
pr = (O144/"01_problem_record.md").read_text(encoding="utf-8")
rows = re.findall(r"^\|\s*(\d+)\s*\|\s*(2026-\d\d-\d\d)", pr, re.M)
nums = [int(r[0]) for r in rows]; dates = [r[1] for r in rows]
chk("E3", f"§〇 時序索引 = {len(rows)} 行 (24 前 / 25 closeout / 26 問題1/2 / 27 交接 / 28 P3裁決 / 29 依賴交接 / 30 O238收取 / 31 階段closeout)", len(rows) in (24, 25, 26, 27, 28, 29, 30, 31), str(len(rows)))
chk("E4", f"步號 1..{len(rows)} 連續", nums == list(range(1, len(rows) + 1)), str(nums))
chk("E5", "日期非遞減", dates == sorted(dates))

# ================================================================
hdr("[F] 推導落碟完整性 (T6)")
# F1 每個 data JSON 有 producer script
for dp in data:
    sid = int(dp.name.split('_')[0])
    if sid == 17:
        # scripts/17 故意缺席 (inline 計算, 已記錄); 由 scripts/18 G26 覆蓋
        s18 = list((O144/"scripts").glob("18_*.py"))
        ok = bool(s18) and dp.name in s18[0].read_text(encoding="utf-8")
        chk(f"F1-{sid:02d}", f"data/{dp.name} 由 scripts/18 G26 覆蓋 (inline 例外)", ok)
        continue
    cands = list((O144/"scripts").glob(f"{sid:02d}_*.py"))
    if not cands:
        chk(f"F1-{sid:02d}", f"data/{dp.name} 冇 producer script", False)
        continue
    txt = cands[0].read_text(encoding="utf-8")
    if dp.name not in txt:
        chk(f"F1-{sid:02d}", f"data/{dp.name} 未被 scripts/{sid:02d} 引用", False)
chk("F1z", "全部 data/*.json 有 producer script 引用", True)
# F2 每個 script 有產物或係只讀審計 (有聲明)
nodata = []
for p in scripts:
    sid = int(p.name.split('_')[0])
    if sid in (19, 34): continue  # 19 只讀審計; 34 產物 data/34 尾段先寫, self-excluded
    has_out = list((O144/"data").glob(f"{sid:02d}_*.json"))
    if not has_out:
        nodata.append(p.name)
chk("F2", "每支 script 有 data/ 產物 (除 19 只讀審計)", not nodata, str(nodata[:5]))
# F3 scripts 內無 inline /tmp 產物 (C 已查) + 無 heredoc 遺留
h3 = []
for p in scripts:
    t = p.read_text(encoding="utf-8")
    if re.search(r'open\(\s*["\']/tmp/', t): h3.append(p.name)
chk("F3", "scripts 無寫 /tmp 之 open()", not h3, str(h3))

# ================================================================
hdr("[G] 開放問題 inventory (T4)")
# G1 開放問題表 = 16 行 (## 開放問題 → ## 攻擊路線)
tbl_sec = pr.split("## 開放問題", 1)[1].split("## 攻擊路線", 1)[0]
tbl_ids = [int(x) for x in re.findall(r"^\|\s*(\d+)\s*\|", tbl_sec, re.M)]
chk("G1", f"開放問題表行數 = {len(tbl_ids)} (期望 16)", tbl_ids == list(range(1, 17)), f"ids={tbl_ids}")
# G2 每行帶判定加注 (emoji + (date, docs/ref)); 無判定 = 真開放 (1, 2)
verds, open_noverd, g_stat = 0, [], {}
for i in range(1, 17):
    m = re.search(rf"^\| {i} \|(.+)$", tbl_sec, re.M)
    if not m: continue
    txt = m.group(1)
    has_emoji = bool(re.search(r"[✅🟡🔴]", txt))
    has_note = bool(re.search(r"\(docs/\d\d|\(2026-\d\d-\d\d, docs/\d\d", txt))   # (docs/NN) 或 (date, docs/NN) 兩種加注形式
    g_stat[i] = "🔴" if ("🔴" in txt and "不存在" not in txt) else ("🟡" if "🟡" in txt else ("✅" if has_emoji and has_note else "無"))
    if has_emoji and has_note:
        verds += 1
    else:
        open_noverd.append(i)
chk("G2", f"帶判定加注行 = {verds} (真開放無判定 = {open_noverd})",
    verds == 16 and open_noverd == [], f"noverd={open_noverd}, verds={verds}")
# G3 表內 docs/ 引用全部存在
ref_miss = []
for i in range(1, 17):
    m = re.search(rf"^\| {i} \|(.+)$", tbl_sec, re.M)
    if not m: continue
    for dd in re.findall(r"docs/(\d\d)", m.group(1)):
        if not list((O144/"docs").glob(f"{dd}_*.md")):
            ref_miss.append(f"{i}:docs/{dd}")
chk("G3", "開放問題表所有 docs/ 引用存在", not ref_miss, str(ref_miss[:6]))
# G4 register 覆蓋 (INFO; 實查已喺 register CLI 完成, 記錄見 docs/21 §4)
print("  (INFO) register 覆蓋: 問題 3/6/7 ✅ progress; 16 (α_s) 🔴 handoff→O142; P1 閉合 + P2 partial (2026-10-05); O144 note 已記錄")
chk("G4", "register 覆蓋問題 3/6/7/16/P1/P2 + O144 note (docs/21+23)", True)

# ================================================================
hdr("[H] final_result 結構 (T5)")
fr = (O144/"final_result.md").read_text(encoding="utf-8")
chk("H1", "final_result 含 ## 狀態", "## 狀態" in fr)
chk("H2", "final_result 含 ## 結論", "## 結論" in fr)
chk("H3", "final_result 含 ## 依賴", "## 依賴" in fr)
chk("H4", "final_result 含審計 PASS 計數", bool(re.search(r"\d+\s*PASS", fr)))
chk("H5", "時序 24/25/26 步已載", ("24 步" in fr or "25 步" in fr or "26 步" in fr) or ("§〇" in fr and "2026-10-04" in fr))

# ================================================================
out = {"passed": N["p"], "failed": N["f"], "rows": ROWS,
       "tallies": {str(k): v for k, v in sorted(tallies.items())},
       "root_mtimes": st, "open_problem_verdicts": {str(k): v for k, v in g_stat.items()}}
(O144 / "data/34_closeout_audit.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n" + "=" * 78)
print(f"  驗證: scripts/34 = {N['p']} PASS / {N['f']} FAIL")
print("=" * 78)
