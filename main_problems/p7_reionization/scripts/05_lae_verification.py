#!/usr/bin/env python3
"""
05_lae_verification.py
=========================
IDCM 驗證：Lyα 發射線星系計數 N(z) ∝ 1/(1+z)

假設：LAE 密度下降係投影選擇效應，唔係 IGM 中性化
IDCM 預測：N(z) ∝ 1/(1+z) （純幾何，K_Tree projection 收窄）

驗證：先用公開嘅 JADES/CEERS 數據做初步比較
如果吻合，就係強力證據支持 IDCM 解釋

IDCM v10.0 — 共震點宇宙學
"""

import sys
import math
import json
import urllib.request
import os

# ================================================================
# IDCM Core Constants
# ================================================================
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4
N_d = 44
M = 33
B = 4

# ================================================================
# IDCM 預測：N(z) ∝ 1/(1+z)
# ================================================================
print("=" * 72)
print("IDCM 再電離問題 — 路徑 4：LAE 計數驗證")
print("=" * 72)

def idcm_lae_prediction(z, norm=1000):
    """
    IDCM 預測：LAE 計數 ∝ 投影面積 ∝ 1/(1+z)
    ℓ = log₄(1+z), K_Tree 投影面積 ∝ B^{-ℓ} = 4^{-log₄(1+z)} = 1/(1+z)
    """
    return norm / (1 + z)

# 預測曲線
print(f"\nIDCM 預測：N(z) ∝ 1/(1+z)")
print(f"  物理機制：K_Tree projection 面積隨 ℓ 收窄")
print(f"  ℓ = log₄(1+z), 投影面積 ∝ B^(-ℓ) = 1/(1+z)")
print(f"\n  z    | ℓ = log₄(1+z) | N_pred (歸一化)")
print(f"  {'─'*4}|{'─'*16}|{'─'*20}")
for z in [3, 4, 5, 6, 7, 8, 9, 10]:
    ell = math.log(1 + z) / math.log(4)
    N = idcm_lae_prediction(z, norm=100)
    print(f"  {z:3d} | {ell:14.3f} | {N:18.1f}")

# 與 ΛCDM 比較
print(f"\n\nIDCM vs ΛCDM 預測比較：")
print(f"  z    | N_IDCM (1/(1+z)) | N_ΛCDM (典型模型)")
print(f"  {'─'*4}|{'─'*18}|{'─'*22}")
for z in [3, 4, 5, 6, 7, 8, 9, 10]:
    N_idcm = idcm_lae_prediction(z, norm=100)
    # ΛCDM 典型預測（近似）：LAF 模型，喺 z≈6-7 急降
    # 簡單模型：exp(-(z-6)²/2) 嘅形式
    N_lcdm = 100 * math.exp(-((z - 6) / 3)**2) if z >= 4 else 100
    print(f"  {z:3d} | {N_idcm:17.1f} | {N_lcdm:21.1f}")

# ================================================================
# 嘗試下載 JADES DR4 數據
# ================================================================
print(f"\n{'=' * 72}")
print("下載 JADES DR4 數據")
print("=" * 72)

data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)

# JADES DR4 光譜數據
jades_urls = [
    ("https://jades.herts.ac.uk/DR4/Combined_DR4_external_v1.2.1.fits",
     "jades_dr4_combined.fits"),
]

for url, fname in jades_urls:
    fpath = os.path.join(data_dir, fname)
    if os.path.exists(fpath) and os.path.getsize(fpath) > 1000:
        print(f"  ✅ {fname} 已存在 ({os.path.getsize(fpath)/1e6:.1f} MB)")
        continue
    
    print(f"  下載 {fname}...")
    try:
        # Use curl via terminal for anti-bot compliance
        # (will be called from terminal)
        pass
    except Exception as e:
        print(f"  ❌ 下載失敗: {e}")

print(f"\nJADES DR4 數據需要經 curl 下載（見 download_data.sh）")

# ================================================================
# 儲存預測
# ================================================================
predictions = {}
for z in range(3, 16):
    ell = math.log(1 + z) / math.log(4)
    N_idcm = idcm_lae_prediction(z, norm=100)
    N_lcdm = 100 * math.exp(-((z - 6) / 3)**2) if z >= 4 else 100
    predictions[f'z_{z}'] = {
        'ell': ell,
        'N_idcm': N_idcm,
        'N_lcdm': N_lcdm,
        'ratio_idcm_lcdm': N_idcm / N_lcdm if N_lcdm > 0 else float('inf')
    }

with open('data/lae_predictions.json', 'w') as f:
    json.dump(predictions, f, indent=2)

print(f"\n預測已儲存至 data/lae_predictions.json")
print(f"{'=' * 72}")