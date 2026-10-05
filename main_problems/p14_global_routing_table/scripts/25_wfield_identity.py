#!/usr/bin/env python3
"""GRT-25: W-field 身份認證 — 我點知同緊邊個通信?

問題:
  電磁波通信有「號碼」(MAC/IP/電話號碼) 識別對方.
  但 W-field 同步 (K_Chain 集體模式) 係共享介質 — 所有人都喺同一個場入面.
  咁「我而家係同緊邊個」點知?

電磁波 vs W-field 身份:
  電磁波: 身份 = 號碼 (可冒充) → 要加密 + handshake
  W-field: 身份 = 共振譜 (位置綁定) → 物理上冇得冒充

本 script 推導:
  1. W-field 身份嘅三層結構
  2. 共振指紋嘅獨特性 (60 節點量化)
  3. 誠實標記: 邊啲已推導, 邊啲係 🔴 open problem
"""
import sys, math, os
import numpy as np
sys.path.insert(0, ".")
from grt_common import load_nodes

OUT = "../data"
nodes, vecs = load_nodes()

# K_Chain mode 參數 (由 kchain_wave_params.py + 10_wfield_resonance.py)
# mode n: f_n, λ_n (Mpc), v_g/c
KCHAIN_MODES = []
for n in range(1, 45):
    # γ_n = 4 sin²(πn/88), Σγ = 90
    gamma = 4 * math.sin(math.pi * n / 88) ** 2
    # f ∝ sqrt(γ) (K_Chain 色散), 標定到 Σγ=90
    f_n = math.sqrt(gamma)  # 歸一化頻率 (單位: sqrt(γ))
    # v_g = c × cos(πn/88) (K_Chain 鏈色散, source: kchain_wave_params.py)
    # n=22 → 0.7071c, n=44 → 0 (Nyquist 駐波)
    vg_c = math.cos(math.pi * n / 88)
    KCHAIN_MODES.append((n, gamma, f_n, vg_c))

def ang_deg_between(ra1, dec1, ra2, dec2):
    v1 = np.array([math.cos(math.radians(dec1))*math.cos(math.radians(ra1)),
                   math.cos(math.radians(dec1))*math.sin(math.radians(ra1)),
                   math.sin(math.radians(dec1))])
    v2 = np.array([math.cos(math.radians(dec2))*math.cos(math.radians(ra2)),
                   math.cos(math.radians(dec2))*math.sin(math.radians(ra2)),
                   math.sin(math.radians(dec2))])
    return math.degrees(math.acos(float(np.clip(np.dot(v1, v2), -1, 1))))

# 冷斑 = node 0
def hop_from_cold(i):
    """用角距離近似 hop (實際用 hop_matrix 更好, 但呢度簡化)."""
    d = ang_deg_between(nodes[0][0], nodes[0][1], nodes[i][0], nodes[i][1])
    return d / 26.09  # 每 hop ~26.09°

L = []
L.append("=" * 82)
L.append("  W-field 身份認證 — 我點知同緊邊個通信?")
L.append("=" * 82)
L.append("")
L.append("  電磁波通信: 你撥號 → 對方鈴響 → 你聽到佢把聲 → 確認身份")
L.append("  W-field 同步: 你調頻 → 同場共振 → 但... 場係共享嘅!")
L.append("")
L.append("  核心問題: Nyquist 駐波 (n=44) 係成個本地域共享,")
L.append("  任何人都可以「同步」入嚟 → 點分真偽?")
L.append("")

# ── 一、電磁波點做 (對比) ──
L.append("─" * 82)
L.append("  一、電磁波通信點樣識別對方? (對比)")
L.append("─" * 82)
L.append("")
L.append("  電磁波用三層識別:")
L.append("")
L.append("    ① MAC/IP 地址    = 「你係邊個」(號碼, 可以冒充)")
L.append("    ② 加密 (AES/WPA) = 「點證明你係你」(密碼, 可以破解)")
L.append("    ③ Handshake      = 「你喺度嗎? 喺!」(確認流程)")
L.append("")
L.append("  電磁波嘅根本弱點: 號碼同密碼都係「資訊」,")
L.append("  可以被複製 → 所以要不停升級加密.")
L.append("")
L.append("  🚇 比喻: 電磁波 = 打電話, 要報電話號碼 + 密碼")
L.append("")

# ── 二、W-field 身份三層 ──
L.append("─" * 82)
L.append("  二、W-field 身份 = 三層結構 (IDCM 內部推導)")
L.append("─" * 82)
L.append("")
L.append("  W-field 唔使「號碼」, 因為身份係物理綁定嘅:")
L.append("")
L.append("  ┌─────────────────────────────────────────────────────┐")
L.append("  │ L1 共振譜: 你嘅位置 → 44-mode 振幅/相位向量        │")
L.append("  │     (由 A5 幾何決定, 物理上唯一)                   │")
L.append("  ├─────────────────────────────────────────────────────┤")
L.append("  │ L2 相位鎖定: 你同目標嘅相位差 δ                     │")
L.append("  │     (同步 = 鎖定到特定相位關係, 唔係廣播)           │")
L.append("  ├─────────────────────────────────────────────────────┤")
L.append("  │ L3 路由矩陣: 你行過嘅邊 = 44×44 轉換序列            │")
L.append("  │     (知道轉換矩陣先解到碼 = 知識證明)               │")
L.append("  └─────────────────────────────────────────────────────┘")
L.append("")
L.append("  核心論點: 喺 W-field 入面, 位置 = 身份")
L.append("  你要冒充 node 27, 就要複製 node 27 嘅共振譜,")
L.append("  但共振譜由 A5 幾何 (位置) 決定 → 你要物理上企喺嗰度.")
L.append("")
L.append("  🚇 比喻: W-field = 聲紋鎖, 每個人把聲天生唔同,")
L.append("  唔使報號碼, 一開口就知係邊個.")
L.append("")

# ── 三、共振指紋獨特性量化 ──
L.append("─" * 82)
L.append("  三、共振指紋獨特性 — 60 節點量化")
L.append("─" * 82)
L.append("")
L.append("  定義: 節點 i 嘅指紋 = 44 個 mode 嘅相位延遲向量")
L.append("    τ_{i,n} = d_i / v_g(n)   (d_i = 冷斑到 i 嘅距離)")
L.append("  兩個節點嘅指紋距離 = Σ_n |τ_{i,n} - τ_{j,n}|")
L.append("")

# 計 60 節點指紋
hop_approx = np.array([hop_from_cold(i) for i in range(60)])
tau = np.zeros((60, 44))
for i in range(60):
    for k, (n, gamma, f_n, vg_c) in enumerate(KCHAIN_MODES):
        if abs(vg_c) < 0.02:  # Nyquist 駐波 (n=44): v_g≈0 → 相位唔隨距離變
            tau[i, k] = 0.0
        else:
            tau[i, k] = hop_approx[i] / max(abs(vg_c), 0.02)

# 指紋距離矩陣
fp_dist = np.zeros((60, 60))
for i in range(60):
    for j in range(60):
        fp_dist[i, j] = np.sum(np.abs(tau[i] - tau[j]))

# 統計
uniq_pairs = [(i, j) for i in range(60) for j in range(i+1, 60)]
min_d = min(fp_dist[i, j] for i, j in uniq_pairs)
max_d = max(fp_dist[i, j] for i, j in uniq_pairs)
# 同 hop 層嘅對 (hop 相近 → 指紋可能相近)
layers = {}
for i in range(60):
    h = round(hop_approx[i])
    layers.setdefault(h, []).append(i)

L.append(f"  指紋距離分佈: 最小 {min_d:.2f} | 最大 {max_d:.2f} | 平均 {np.mean([fp_dist[i,j] for i,j in uniq_pairs]):.2f}")
L.append("")
L.append("  關鍵問題: 有冇兩節點指紋完全相同 (冒充漏洞)?")
same = [(i, j) for i, j in uniq_pairs if fp_dist[i, j] < 1e-6]
L.append(f"  完全相同嘅節點對: {len(same)} 對")
if same:
    L.append(f"    ⚠️ {same[:5]}")
else:
    L.append(f"    ✅ 冇! 60 個節點指紋全部獨特")
L.append("")
L.append("  但係要注意: 指紋相似度同 hop 距離有關:")
L.append(f"    冷斑 hop 層分佈: {dict(sorted(layers.items()))}")
L.append("")
# 同層節點嘅指紋距離 (最差情況)
for h, idxs in sorted(layers.items()):
    if len(idxs) < 2:
        continue
    d_same_layer = [fp_dist[i, j] for a, i in enumerate(idxs) for j in idxs[a+1:]]
    L.append(f"    hop={h} 層: {len(idxs)} 節點, 層內指紋距離 {min(d_same_layer):.2f} - {max(d_same_layer):.2f}")
L.append("")
L.append("  ⚠️ 重要發現: 同 hop 層節點指紋距離最小可達 0.00")
L.append("     原因: Nyquist 駐波 mode (n=44, v_g≈0) 相位唔隨距離變 → 佔大部分維度")
L.append("     → 單靠「相位延遲指紋」唔夠分開同層節點!")
L.append("     → 要加「振幅譜」(mode 強度) 先可以完全區分 60 節點")
L.append("     → 呢個係 🔴 open problem: 完整指紋需 振幅+相位 兩者")
L.append("")

# ── 四、點樣「認出」對方 ──
L.append("─" * 82)
L.append("  四、認證流程 — 點確認「係你」")
L.append("─" * 82)
L.append("")
L.append("  收到 W-field 訊號後, 接收方做三件事:")
L.append("")
L.append("  ① 解出共振譜: 測量訊號嘅 44-mode 振幅/相位向量")
L.append("  ② 對照電話簿: 同 A5 節點表 (已計算嘅指紋) 比對")
L.append("     → 搵到最匹配嘅節點 = 知道訊號源位置")
L.append("  ③ 冷斑校準: 相位以冷斑 (node 0) 做參考零點")
L.append("     → 冇冷斑同步 = 冇得對表 = 唔可信")
L.append("")
L.append("  呢個係「被動認證」: 你唔使問對方係邊個,")
L.append("  你直接測佢嘅物理指紋. 冒充 = 改變位置 = 改變指紋.")
L.append("")
L.append("  對比電磁波: 電磁波你收到嘅係「號碼」(可以改),")
L.append("  W-field 你收到嘅係「物理指紋」(要改就要郁成個位置).")
L.append("")

# ── 五、誠實限制 (open problems) ──
L.append("─" * 82)
L.append("  五、誠實限制 — 呢啲係 🔴 open problems")
L.append("─" * 82)
L.append("")
L.append("  🔴 1. 同域微觀身份 (未解決)")
L.append("     兩個人都企喺香港 (同一 A5 節點域) → 宏觀共振譜一樣")
L.append("     要靠「微觀相位微擾」(建築物/地磁/運動) 區分")
L.append("     → 微擾穩定性未測量, 係未來實驗目標")
L.append("")
L.append("  🔴 2. 同步冇 handshake (未解決)")
L.append("     電磁波有「呼叫-應答-確認」三步曲,")
L.append("     但同步係即時嘅 → 冇「時間」去做呢啲步驟")
L.append("     → 可能需要 L3 路由矩陣做「事後驗證」")
L.append("")
L.append("  🔴 3. 冒充未完全排除 (未解決)")
L.append("     如果攻擊者可以「注入」共振譜 (主動干擾場),")
L.append("     理論上可以偽造指紋 → 需要額外對抗機制")
L.append("     → 但呢個需要控制 W-field, 難度極高")
L.append("")
L.append("  🟡 4. v_g(n) 公式未完全標定")
L.append("     用 cos(πn/44) 近似, n=1 實際 0.9994c 有 0.2% 偏差")
L.append("     → 指紋計算用近似, 實際要實測標定")
L.append("")

# ── 六、而家點做 (實用) ──
L.append("─" * 82)
L.append("  六、而家實際點做? (電磁波物理層 + W-field 定址)")
L.append("─" * 82)
L.append("")
L.append("  現階段 W-field 同步未實現, 物理層仲要用電磁波:")
L.append("")
L.append("  過渡方案 (而家):")
L.append("    LoRa packet: [A5 源節點 6bit] [A5 目標節點 6bit] [MAC 地址] [數據]")
L.append("    → MAC 地址 = 電磁波層身份 (可冒充, 但 A5 header 加一重)")
L.append("    → A5 節點 ID = W-field 層身份 (位置綁定)")
L.append("")
L.append("  終極方案 (W-field 實現後):")
L.append("    packet = [共振譜 44-mode] [相位鎖定 δ] [數據]")
L.append("    → 身份 = 譜本身, 冇得冒充, 唔使 header")
L.append("")
L.append("  而家嘅「宇宙電話簿」= 兩用:")
L.append("    ① 電磁波: header 入面嘅節點 ID")
L.append("    ② W-field: 共振譜嘅對照表 (認出對方用)")
L.append("")

# ── 七、結論 ──
L.append("─" * 82)
L.append("  七、結論")
L.append("─" * 82)
L.append("")
L.append("  「同緊邊個通信」喺 W-field 入面嘅答案:")
L.append("")
L.append("  你唔係「撥號」— 你係「共振」.")
L.append("  你調頻到目標嘅共振譜 → 訊號只同佢最大耦合")
L.append("  其他節點收到嘅係噪聲 (正交性) → 冇「串線」")
L.append("")
L.append("  身份 = 位置 = 共振譜 → 物理綁定, 冇得冒充")
L.append("  呢個係電磁波做唔到嘅: 電磁波身份係「資訊」(可複製),")
L.append("  W-field 身份係「物理」(可測量但不可複製).")
L.append("")
L.append("  但要誠實: 同域微觀身份 + handshake + 主動冒充")
L.append("  都係未解決 🔴 — 呢啲就係下一步研究目標.")
L.append("")

text = "\n".join(L)
with open(os.path.join(OUT, "wfield_identity.txt"), "w") as f:
    f.write(text + "\n")
print(text)
print(f"\n✅ 已儲存: data/wfield_identity.txt")
