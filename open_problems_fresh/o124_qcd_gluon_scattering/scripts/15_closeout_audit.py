#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O124 — Script 15: Closeout 獨立審計 (2026-10-06)
========================================================================
由零重算 + 全鏈完整性審計。唔 import scripts/01–14。

§A  全部 14 script 重跑 (subprocess /usr/bin/python3, 用絕對解譯器)
§B  全鏈 session 取證 (state.db read-only, session_key chain)
§C  文檔完整性 (docs/01–09 存在 + final_result + SESSION_START; φ³−φ⁻³ 修正)
§D  Δα⁻¹ = 9 排除核對 (13.2σ 重算)
§E  登記面核對 (register O124 事件存在: registered + 2 notes + hired handoff)
"""
import os, sqlite3, subprocess, json, glob, math, sys

PASS = FAIL = TOTAL = 0
def chk(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    ok = bool(cond)
    if ok: PASS += 1
    else:  FAIL += 1
    print(f"  {'✅' if ok else '❌'} {name} {detail}")

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
ODIR = os.path.join(BASE, "open_problems_fresh/o124_qcd_gluon_scattering")
REPO = os.path.join(BASE, "problem_register")
PY = "/usr/bin/python3"

print("=" * 78)
print("  O124 Script 15: Closeout 獨立審計")
print("=" * 78)

# ── [A] 全 14 script 重跑 ───────────────────────────────────────
print("\n─── [A] 14 scripts 重跑 (絶對解譯器) ───")
scripts = [s for s in sorted(glob.glob(os.path.join(ODIR, "scripts", "*.py")))
           if not os.path.basename(s).startswith("15_")]
chk("A1 scripts 數 = 16 (01–14,16,17; 排除自身)", len(scripts) == 16, f"({len(scripts)})")
for s in scripts:
    nm = os.path.basename(s)
    r = subprocess.run([PY, s], cwd=ODIR, capture_output=True, text=True, timeout=900)
    chk(f"A2 {nm} exit=0", r.returncode == 0, f"(rc={r.returncode})")
print("      (逐支時間消耗, 唔逐行印出)")

# ── [B] session 鏈取證 ──────────────────────────────────────────
print("\n─── [B] session 鏈 (state.db read-only) ───")
sk = "agent:main:telegram:dm:7500748185:39951"
conn = sqlite3.connect("file:" + os.path.expanduser("~/.hermes/state.db") + "?mode=ro", uri=True)
ids = [r[0] for r in conn.execute(
    "SELECT id FROM sessions WHERE session_key=? ORDER BY started_at", (sk,)).fetchall()]
known = {"20260926_171759_3f594672","20260926_174749_7ff639","20260926_201424_f65d2b",
         "20260926_211116_28a397","20260926_231227_88f73b"}
chk("B1 對話框 session_key 鏈含已知 5 個 09-26 session",
    known.issubset(set(ids)) and len(ids) >= 5,
    f"({len(ids)} sessions, 最後: {ids[-1]})")
nmsg = conn.execute("SELECT COUNT(*) FROM messages WHERE session_id IN (%s)"
                    % ",".join("?" * len(ids)), ids).fetchone()[0]
chk("B2 全鏈訊息數 ≥ 450 (含壓縮保留內容)", nmsg >= 450, f"({nmsg})")
# 今日新 session (20261006_*) 存在或唔存在 (closeout 當日)
today = [sid for sid in ids if sid.startswith("20261006_")]
chk("B2b closeout session (2026-10-06) 喺鏈上", len(today) >= 1, f"({today})")
# o124 寫入範圍
wpath = set()
for sid in ids:
    for (tc,) in conn.execute("SELECT tool_calls FROM messages WHERE session_id=?", (sid,)).fetchall():
        if not tc: continue
        try: tcs = json.loads(tc)
        except Exception: continue
        if isinstance(tcs, dict): tcs = [tcs]
        for t in tcs:
            fn = (t.get("function") or {}).get("name")
            if fn in ("write_file", "patch"):
                try: args = json.loads((t.get("function") or {}).get("arguments") or "{}")
                except Exception: args = {}
                p = args.get("path")
                if p and "o124_qcd_gluon_scattering" in p: wpath.add(p)
chk("B3 本鏈寫入 o124 檔案 ≥ 20", len(wpath) >= 20, f"({len(wpath)})")
chk("B4 本鏈寫入範圍: 只有 o124 + README (唔含其他 O)",
    all("o124_qcd_gluon_scattering" in p or p.endswith("open_problems_fresh/README.md") or
        p.startswith("/home/wsl/.hermes/cache/scratch/") for p in wpath))

# ── [C] 文檔完整性 ──────────────────────────────────────────────
print("\n─── [C] 文檔完整性 ───")
docs = sorted(glob.glob(os.path.join(ODIR, "docs", "*.md")))
chk("C1 docs 10 份存在 (01–10)", len(docs) == 10, f"({len(docs)})")
for f in ("SESSION_START.md", "final_result.md"):
    chk(f"C2 {f} 存在", os.path.exists(os.path.join(ODIR, f)))
d9 = open(os.path.join(ODIR, "docs/09_irreducible_inputs.md"), encoding="utf-8").read()
chk("C3 docs/09 已修正 φ³−φ⁻³ (ψ 註記)", "φ³ + ψ³ = φ³ − φ⁻³ = L₃ = 4" in d9 or "φ³ − φ⁻³ = L₃" in d9)
chk("C4 docs/09 §7 closeout 修正存在",
    "Closeout 修正 (2026-10-06)" in d9 and "13.2σ" in d9 and "排除" in d9)
chk("C5 docs/09 無壓縮標記",
    "HERMES-CONTEXT-COMPRESSION" not in d9 and "omitted here" not in d9)
for sd in ("SESSION_START.md", "docs/01_problem_record.md"):
    t = open(os.path.join(ODIR, sd), encoding="utf-8").read()
    # C6: 只禁「錯式等號」φ³+φ⁻³ = L₃（=4）。docs/01 §十八/廿一 兩處 φ³+φ⁻³
    #     係「描述筆誤本身」（O229 handoff 指正記錄），唔係錯式——允許存在。
    chk(f"C6 {sd} 無 φ³+φ^{{−3}} 錯式等號 (已修正)",
        "φ³+φ^{−3} = L₃" not in t and "φ³+φ⁻³ = L₃ = 4" not in t)
fr = open(os.path.join(ODIR, "final_result.md"), encoding="utf-8").read()
chk("C7 final_result 無 φ³+φ^{−3} 錯式", "φ³+φ^{−3} = L₃" not in fr)

# ── [D] Δα⁻¹ = 9 排除重算 ───────────────────────────────────────
print("\n─── [D] Δα⁻¹ = 9 排除 (12/10-03 note 重算) ───")
a0, aMZ, sa = 137.035999074, 127.930, 0.008
d = a0 - aMZ
chk("D1 Δα⁻¹ 實測 = 9.1060 ± 0.008", abs(d - 9.1060) < 0.0002, f"({d:.4f})")
chk("D2 偏差 = 13.2σ (13.25 重算)", abs((d - 9)/sa - 13.25) < 0.05, f"({(d-9)/sa:.2f}σ)")
chk("D3 結構整數端點僅 137−128 = 9 (純代數)", 137 - 128 == 9)
chk("D4 整數端點 137 亦偏 +0.78%", abs((137 - aMZ - 9)/9*100 - 0.778) < 0.02,
    f"({(137-aMZ-9)/9*100:+.3f}%)")

# ── [E] 登記面 ──────────────────────────────────────────────────
print("\n─── [E] register 覆蓋 (read-only) ───")
reg = os.path.join(REPO, "register.jsonl")
ev = []
with open(reg, encoding="utf-8") as f:
    for line in f:
        try: j = json.loads(line)
        except Exception: continue
        if j.get("pid") == "O124" or j.get("target_pid") == "O124": ev.append(j)
kinds = [e["kind"] for e in ev]
chk("E1 O124 註冊事件存在 (registered @09-26)",
    any(k == "registered" and e.get("ts", "").startswith("2026-09-26") for k, e in zip(kinds, ev)))
chk("E2 O229→O124 handoff 存在 (pid=O229, target=O124, 10-02)",
    any(e.get("pid") == "O229" and e.get("kind") == "handed_off"
        and e.get("target_pid") == "O124" for e in ev))
chk("E3 10-03 note (Δα⁻¹=9 排除) 存在",
    any(e.get("kind") == "note" and "13.2σ" in (e.get("note") or "") for e in ev))
chk("E4 O85 note (10-05, 不引 Δα⁻¹=9) 存在",
    any(e.get("kind") == "note" and "O85" in (e.get("note") or "") for e in ev))

conn.close()

print("\n" + "=" * 78)
print(f"  結果: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"  結論: {'✅ closeout 前置審計通過' if FAIL == 0 else '❌ 有項失敗'}")
print("=" * 78)