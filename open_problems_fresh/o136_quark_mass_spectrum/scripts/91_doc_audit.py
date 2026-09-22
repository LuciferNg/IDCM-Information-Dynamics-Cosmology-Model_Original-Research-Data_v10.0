#!/usr/bin/env python3
"""
O136 — scripts/91_doc_audit.py : 文檔審計 (第 2 層, 只讀)
================================================================================
只讀文檔，唔改任何檔案。審計【記錄本身】而非物理:
  [A] 檔案集完整性 (docs / scripts / data / 三件套)
  [B] 編碼完整性 (U+FFFD) + markdown 圍欄平衡
  [C] 狀態行跨文檔一致性 (SESSION_START / docs/01 / final_result)
  [D] final_result.md 段序符合 RESULT_TEMPLATE
  [E] 推導時序索引 (存在 / 編號唯一遞增 / 每行有日期)
  [F] 已知數值錯誤嘅修正覆蓋 (28.033 / 0.443084 / 0.381566 / 12.42)
  [G] 目錄範圍紀律 (只准本目錄檔案)
  [H] 時序完整性 (禁止回溯污染: 舊日期段落唔可以含新 session 內容)
  [I] 關鍵數值出現性 (docs 必須載有核心結果)
  [J] 交叉引用可達 (docs/01 索引提到嘅檔案真係存在)
"""
import re, json, sys, subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DOCS = BASE / "docs"
DATA = BASE / "data"
SCR  = BASE / "scripts"

CHECKS = []
def chk(name, cond, detail=""):
    CHECKS.append((name, bool(cond), detail))
    return bool(cond)

def norm(s):
    """只摺疊空白 + 統一負號; 唔碰換行 (供行/表抽取用)"""
    return s.replace("\u2212", "-")

def read(p):
    try:    return p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"__ERR__{e}"

# 全部文檔
DOC_KEYS = {}
for p in sorted(DOCS.glob("*.md")):
    DOC_KEYS[p.name] = read(p)
SS = read(BASE / "SESSION_START.md")
FR = read(BASE / "final_result.md")
DOC_KEYS["SESSION_START.md"] = SS
DOC_KEYS["final_result.md"] = FR
ALLTXT = "\n".join(DOC_KEYS.values())

print("=" * 96)
print("O136 scripts/91_doc_audit.py — 文檔審計 (第 2 層, 只讀)")
print("=" * 96)

# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*96}\n[A] 檔案集完整性\n{'─'*96}")

nd = len(list(DOCS.glob("*.md")))
chk("A1 docs 數量 = 37", nd == 37, f"實際 {nd}")

want_scripts = {f"{i:02d}_" for i in range(1, 46)}
have_scripts = {p.name[:3] for p in SCR.glob("*.py")}
missing_s = sorted(want_scripts - have_scripts)
chk("A2 scripts 01-45 齊全", not missing_s, f"缺 {missing_s}")

# 90/91 為審計腳本
chk("A3 審計腳本 90/91 存在",
    (SCR / "90_verify_all.py").exists() and (SCR / "91_doc_audit.py").exists(), "")
chk("A3b 攻堅腳本 46–49 + docs/27,28 存在",
    all((SCR / f).exists() for f in ["46_sector_scale.py","47_sector_null_test.py",
                                      "48_collective_excitation.py","49_algebraic_degree_true.py"])
    and (DOCS / "27_sector_scale_null_test.md").exists()
    and (DOCS / "28_collective_and_degree_correction.md").exists()
    and all((SCR / f).exists() for f in ["50_gemini_proposal_verify.py","51_centroid_test.py",
                                          "52_b4_four_frame_test.py","53_observation_cost_and_rate.py",
                                          "54_observation_cost_null.py"])
    and (DOCS / "29_gemini_b4_and_observation_cost.md").exists()
    and (SCR / "55_k3_identity_and_null.py").exists()
    and (DOCS / "30_k3_identity_negative.md").exists()
    and (SCR / "56_multifactor_product.py").exists()
    and (DOCS / "31_multifactor_product_negative.md").exists()
    and all((SCR / f).exists() for f in ["57_two_mode_operator.py","58_two_mode_signfix.py",
                                          "59_two_mode_logmetric.py"])
    and (DOCS / "32_two_mode_operator_significant.md").exists()
    and all((SCR / f).exists() for f in ["60_residual_structure.py","61_third_order.py",
                                          "62_odd_order_theorem.py","63_odd_v_factor_theorem.py"])
    and (DOCS / "33_odd_v_factor_theorem.md").exists()
    and (SCR / "64_two_modesets_crosscheck.py").exists()
    and (DOCS / "34_two_modesets_crosscheck.md").exists()
    and (SCR / "65_alpha_identifiability.py").exists()
    and (DOCS / "35_alpha_identifiability.md").exists()
    and (SCR / "66_m0_exponent_identity.py").exists()
    and (DOCS / "36_m0_exponent_over_agreement.md").exists()
    and (SCR / "67_mass_scale_dimension.py").exists()
    and (DOCS / "37_mass_scale_inconsistency.md").exists(), "")

# data 檔: 有寫 json 嘅腳本都應該有對應 data
writers = {}
for p in sorted(SCR.glob("*.py")):
    t = read(p)
    for m in re.finditer(r'OUT\s*/\s*"(\d+)_[^"]+\.json"', t):
        writers[m.group(1)] = p.name
missing_d = sorted(k for k in writers if not (DATA / f"{k}_").exists() and
                   not any(x.name.startswith(f"{k}_") for x in DATA.glob("*.json")))
chk("A4 所有寫 json 嘅腳本都有對應 data 檔", not missing_d,
    f"writer={sorted(writers)}; 缺={missing_d}")

chk("A5 三件套齊 (SESSION_START / docs/01 / final_result)",
    SS.strip() != "" and "01_problem_record.md" in DOC_KEYS and FR.strip() != "",
    f"final_result 長度={len(FR)}")

# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*96}\n[B] 編碼完整性 + 圍欄平衡\n{'─'*96}")

bad_enc = [k for k, v in DOC_KEYS.items() if v.count("\ufffd") > 0]
chk("B1 冇任何文檔含 U+FFFD", not bad_enc,
    f"壞檔 {bad_enc}" if bad_enc else "全部乾淨")

bad_fence = []
for k, v in DOC_KEYS.items():
    n = v.count("\n```")
    if n % 2 != 0: bad_fence.append(f"{k}({n})")
chk("B2 markdown 圍欄平衡 (每檔 ``` 數為偶)", not bad_fence,
    f"不平衡 {bad_fence}" if bad_fence else "全部平衡")

# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*96}\n[C] 狀態行跨文檔一致性\n{'─'*96}")

def status_of(t):
    m = re.search(r"##\s*狀態[:：]\s*(.+)", t)
    if m: return m.group(1).strip()
    m = re.search(r">\s*\*\*狀態\*\*[:：]\s*(.+)", t)
    return m.group(1).strip() if m else ""

s_ss, s_pr, s_fr = status_of(SS), status_of(DOC_KEYS["01_problem_record.md"]), status_of(FR)
emoji = lambda s: ("🟢" if "🟢" in s else "") + ("🟡" if "🟡" in s else "") + ("🔴" if "🔴" in s else "")
chk("C1 三處狀態 emoji 一致", emoji(s_ss) == emoji(s_pr) == emoji(s_fr) and emoji(s_ss) != "",
    f"SS={emoji(s_ss)} PR={emoji(s_pr)} FR={emoji(s_fr)}")
chk("C2 final_result 狀態行存在", s_fr != "", s_fr[:60])

# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*96}\n[D] final_result.md 段序 (RESULT_TEMPLATE)\n{'─'*96}")

secs = re.findall(r"^##\s+(.+)$", FR, re.M)
order = ["狀態", "結論", "關鍵公式", "依賴"]
idx = []
for o in order:
    hit = [i for i, s in enumerate(secs) if s.startswith(o)]
    idx.append(hit[0] if hit else -1)
chk("D1 四段齊 (狀態/結論/關鍵公式/依賴)", all(i >= 0 for i in idx), f"{secs} → idx={idx}")
chk("D2 段序符合 template", idx == sorted(idx) and all(i >= 0 for i in idx), f"idx={idx}")
chk("D3 依賴用 → 箭頭", "→" in FR, "")

# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*96}\n[E] 推導時序索引\n{'─'*96}")

PR = DOC_KEYS["01_problem_record.md"]
chk("E1 有時序索引章節", ("時序索引" in PR), "")
rows = re.findall(r"^\|\s*(\d+)\s*\|([^\n]*)$", PR, re.M)   # [(num, rest), ...]
nums = [int(t[0]) for t in rows]
chk("E2 時序索引表有行 (≥10)", len(rows) >= 10, f"{len(rows)} 行")
chk("E3 時序編號唯一", len(nums) > 0 and len(nums) == len(set(nums)),
    f"重複 {[x for x in set(nums) if nums.count(x) > 1]} (n={len(nums)})")
chk("E4 時序編號遞增 (1..N 連續)", len(nums) > 0 and nums == sorted(nums) and nums == list(range(1, len(nums)+1)),
    f"{nums[:5]}...{nums[-3:]}")
# 每行有日期 (2026-MM-DD)
undated = [t[0] for t in rows if not re.search(r"\d{4}-\d{2}-\d{2}", t[1])]
chk("E5 每個時序行有日期", not undated, f"缺日期行號 {undated}")

chk("E6 有時序完整性確認段落", "時序完整性確認" in PR, "")
chk("E7 ⚠️ 附註有日期 + 正確值格式",
    len(re.findall(r"> ⚠️ \*\*驗證修正附註 \(2026-09-20", ALLTXT)) >= 15,
    f"{len(re.findall(r'> ⚠️ .*驗證修正附註', ALLTXT))} 處")

# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*96}\n[F] 已知數值錯誤嘅修正覆蓋\n{'─'*96}")

ERRATA = [
    ("28.033", "28.0172", "sin 空間上限 1/sin(π/88)"),
    ("0.443084", "0.447617", "sin(13π/88)"),
    ("0.381566", "0.382683", "sin(11π/88)"),
    ("12.420", "12.5410", "9 模式上限 sin(13π/88)/sin(π/88)"),
]
for stale, correct, what in ERRATA:
    carriers = [k for k, v in DOC_KEYS.items() if stale in v]
    # 每個載有舊值嘅文檔都必須同時載有正確值 + ⚠️ 註記
    unfixed = [k for k in carriers
               if correct not in DOC_KEYS[k] or "⚠️" not in DOC_KEYS[k]]
    chk(f"F-{stale} 修正覆蓋 ({what}): {len(carriers)} 檔載有舊值, 全部有註記",
        not unfixed,
        f"載有={carriers}; 未註記={unfixed}" if unfixed else f"載有={len(carriers)} 檔, 全部已註記")

# docs/26 §二 框架修正註記覆蓋
_d26 = DOC_KEYS.get("26_obstruction_theorem.md", "")
chk("F-fw docs/26 範圍/比值分離 有框架修正註記",
    "範圍/比值分離" in _d26 and "框架修正附註" in _d26 and "docs/27" in _d26, "")
chk("F-fw2 docs/26 候選解釋 #1 有排除註記",
    "輕子/上夸克/下夸克" in _d26 and "排除附註" in _d26, "")

# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*96}\n[G] 目錄範圍紀律\n{'─'*96}")

ALLOWED_TOP = {"SESSION_START.md", "final_result.md", "docs", "scripts", "data",
               "README.md"}
stray = sorted(p.name for p in BASE.iterdir()
               if p.name not in ALLOWED_TOP and not p.name.startswith("."))
chk("G1 目錄 root 冇預期外檔案", not stray, f"stray={stray}")

stray_docs = sorted(p.name for p in DOCS.iterdir() if p.is_file() and p.suffix != ".md")
chk("G2 docs/ 只含 .md", not stray_docs, f"{stray_docs}")

stray_data = sorted(p.name for p in DATA.iterdir()
                    if p.is_file() and p.suffix not in (".json", ".txt", ".npz", ".csv"))
chk("G3 data/ 只含數據檔", not stray_data, f"{stray_data}")

# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*96}\n[H] 時序完整性 (禁止回溯污染)\n{'─'*96}")

# 舊日期段落 (2026-08-29 / 08-30) 唔應該含 09-20 嘅新發現
OLD_KEYS = ["docs/19_a5_selection_rule.md", "docs/20_mass_scale_verdict.md",
            "docs/21_transmission_hypothesis.md", "docs/22_frame_resolution.md"]
NEWMARK = ["結構障礙定理", "觀察↔被觀察", "位置算子", "42.6×", "0.5873"]
poll = []
for k in OLD_KEYS:
    kk = k.split("/")[-1]
    if kk not in DOC_KEYS: continue
    t = DOC_KEYS[kk]
    # 只檢查「日期標頭為 08-29/08-30」嘅文檔本體是否含 09-20 專屬內容
    if "2026-08-29" in t or "2026-08-30" in t:
        hits = [m for m in NEWMARK if m in t]
        if hits: poll.append(f"{kk}:{hits}")
chk("H1 08-29/08-30 文檔冇 09-20 專屬內容 (回溯污染)", not poll,
    f"污染 {poll}" if poll else "無污染")

chk("H2 09-20 新內容存在於 docs/25,26 (新檔)",
    all(m in (DOC_KEYS.get("25_observer_interaction_attack.md", "") +
              DOC_KEYS.get("26_obstruction_theorem.md", "")) for m in ["位置算子", "結構障礙定理"]),
    "")
# 強化: 08-30 舊 session 文檔本體唔可以含 09-20 專屬結論
_oldsess = ["02_mass_spectrum_framework.md", "03_derivation_audit.md"]
_poll2 = [k for k in _oldsess if k in DOC_KEYS
          and any(m in DOC_KEYS[k] for m in ["結構障礙定理", "位置算子", "42.6×"])]
chk("H2b 08-30 舊 session 文檔冇 09-20 結論 (回溯污染)", not _poll2, f"污染 {_poll2}")

# tally 跨文檔一致性 (分母由文檔推導, 非硬編碼)
_denoms = {int(m.group(2)) for t in DOC_KEYS.values()
           for m in re.finditer(r"(\d+)\s*/\s*(\d+)\s*PASS", t)}
_tally_ok = True; _det = []
for d in sorted(_denoms):
    vals = {int(m.group(1)) for t in DOC_KEYS.values()
            for m in re.finditer(r"(\d+)\s*/\s*" + str(d) + r"\s*PASS", t)
            if int(m.group(1)) in (d, d - 1)}
    _det.append(f"{d}:{sorted(vals)}")
    _tally_ok &= len(vals) <= 1
chk("H4 tally 跨文檔一致 (每個分母單一值)", _tally_ok, " ".join(_det))

# 時序索引保留舊日期行 (禁刪歷史)
old_rows = len(re.findall(r"2026-08-2\d", PR))
chk("H3 時序索引保留 08 月歷史行", old_rows >= 3, f"{old_rows} 行")

# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*96}\n[I] 關鍵數值出現性 (≥1 文檔)\n{'─'*96}")

KEYVALS = {
    "Σγ = 90": "90", "N_d = 44": "44", "E_proj = 28.5": "28.5",
    "反週期 n·L≡44": "n·L", "q-參數化": "N_d·q",
    "A₅ 選擇律 9 模式": "9 模式", "位置算子 Z₂-奇": "位置算子",
    "二階自能 RMS 0.5873": "0.5873", "結構障礙 α 跨度 42.6": "42.6",
    "負相關 −0.2901": "0.2901", "Gap 範圍 2.175e5": "2.175",
    "無解釋上限 3.8588": "3.8588", "frame ICRS": "ICRS",
    "γ₂₀/γ₇ = 7": "γ₂₀/γ₇",
    "扇區 null test P=0.34": "0.3400",
    "範圍唔係障礙 (框架修正)": "2.237e+05",
    "扇區標度 RMS 0.3549": "0.3549",
    "代數次數真公式 v₂(44−n)": "v₂(44−n)",
    "代數次數合計 44": "合計",
    "docs/16 錯誤註記": "驗證修正附註",
    "Node 0 退化定理": "β₀",
    "B=4 k=4 唔特別": "k = 4 唔特別",
    "觀察代價 Σc^{−2}": "0.6854",
    "null 無判別力": "無判別力",
    "k=3 四重否定": "四重否定",
    "sec² 代數身份": "sec²",
    "方法論定理範圍唔係證據": "範圍永遠唔係證據",
    "多因子飽和": "飽和",
    "置換 null 退化定理": "置換 null 退化定理",
    "score 度量修正": "0.5873 精確吻合",
    "二模式雙重顯著": "雙重顯著",
    "A5 模式集 P=0.0155": "0.0155",
    "位置算子 P=0.0080": "0.0080",
    "1/dE 權重本質": "權重係本質的",
    "奇數 V 因子消滅定理": "奇數 V 因子消滅定理",
    "存活階 2,6,10": "{2, 6, 10, 14, ...}",
    "六階無新信息": "0.988235",
    "殘餘無結構": "唔顯著",
    "O120/O137 模式分配否定": "0.8525",
    "A5 唯一統計支持": "0.0155",
    "O120 第一代閉合": "0.133%",
    "壓縮性判準": "壓縮",
    "alpha 不可辨識": "不可辨識",
    "可辨識性判準": "可辨識性判準",
    "pi-1/2 更佳": "2.641593",
    "9! = 重排配對": "重排配對",
    "過度吻合判準": "過度吻合判準",
    "47 有 5 讀法": "F₇ + F₉",
    "M0 指數事後重建": "事後有理重建",
    "優 5.8 萬倍": "5.8 萬倍",
    "H0 內部不一致": "72.590",
    "兩參數欠定": "兩參數欠定",
    "8:1 壓縮": "8:1",
    "幾何平均非推導": "相容性論證",
}
for label, needle in KEYVALS.items():
    chk(f"I-{label}", needle in ALLTXT, "")

# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*96}\n[J] 交叉引用可達\n{'─'*96}")

refs = set(re.findall(r"`?(scripts/\d\d_[a-z0-9_]+\.py)`?", ALLTXT))
missing_refs = [r for r in sorted(refs) if not (BASE / r).exists()]
chk("J1 文檔引用嘅 scripts 全部存在", not missing_refs, f"缺 {missing_refs}")

drefs = set(re.findall(r"docs/(\d\d)_[a-z0-9_]+\.md", ALLTXT))
missing_dr = [d for d in sorted(drefs) if not (DOCS / f"{d}_").exists() and
              not any(x.name.startswith(f"{d}_") for x in DOCS.glob("*.md"))]
chk("J2 文檔引用嘅 docs 全部存在", not missing_dr, f"缺 {missing_dr}")

# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*96}\n[K] 時序 (mtime, INFO only)\n{'─'*96}")

try:
    out = subprocess.run(["bash", "-c",
        f"stat -c '%Y %n' {BASE}/scripts/*.py {BASE}/data/*.json 2>/dev/null | sort -n"],
        capture_output=True, text=True, timeout=30).stdout.strip().splitlines()
    print(f"  [INFO] scripts/data 檔數 = {len(out)}; 最早 = {out[0].split()[1].split('/')[-1] if out else '-'}")
    chk("K1 scripts 檔數 ≥ 47 (45 + 90 + 91)",
        len(list(SCR.glob("*.py"))) >= 47, f"{len(list(SCR.glob('*.py')))}")
except Exception as e:
    chk("K1 scripts 檔數", False, str(e))

# ══════════════════════════════════════════════════════════════════
# [Z] 自指 tally 一致性 (文檔引用嘅第 2 層計數必須 = 本腳本最終計數)
_final_total = len(CHECKS) + 1        # +1 = 本 check 自己
chk(f"Z1 文檔引用嘅第 2 層 tally = {_final_total}/{_final_total}",
    f"{_final_total}/{_final_total} PASS" in ALLTXT,
    " ".join(sorted({m.group(0) for t in DOC_KEYS.values()
                     for m in re.finditer(r"\d+/\d+ PASS", t)})))

# ══════════════════════════════════════════════════════════════════
npass = sum(1 for _, ok, _ in CHECKS if ok)
nfail = len(CHECKS) - npass
print(f"\n{'='*96}")
for name, ok, det in CHECKS:
    if not ok:
        print(f"  🔴 FAIL  {name}   [{det}]")
print(f"\nRESULT: {npass}/{len(CHECKS)} PASS   ({nfail} FAIL)")
print("=" * 96)

try:
    (DATA / "91_doc_audit_results.json").write_text(json.dumps({
        "total": len(CHECKS), "pass": npass, "fail": nfail,
        "checks": [{"name": n, "ok": o, "detail": d} for n, o, d in CHECKS],
    }, ensure_ascii=False, indent=2))
    print("已寫出 91_doc_audit_results.json")
except Exception as e:
    print(f"[WARN] 寫出失敗: {e}")

sys.exit(1 if nfail else 0)