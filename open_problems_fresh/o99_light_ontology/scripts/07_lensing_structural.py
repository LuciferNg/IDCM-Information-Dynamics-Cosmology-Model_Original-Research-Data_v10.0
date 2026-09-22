#!/usr/bin/env python3
"""
O99 — scripts/07: 殺招2 攻堅 — CMB lens C_ℓ^φ^φ 局域代數復現挑戰

誠實宣布: 純局域 G(0) 4點頂點 operator 能否復現 Planck/ACT 透鏡?

實測 anchor (唔捏): SPT+Planck A_φφ = 1.01 ± 0.08; ACT DR6 + Planck PR4 lensing
吻合 ΛCDM line-of-sight 模型。平均 lens 偏角 ~2-3 arcmin。

結構解剖: 標準透鏡 = ∫δχ (LOS 投影) => C_L^φ^φ 有 LOS 累積峰 (L~50-200)。
純 local 4pt (C1「無傳輸 kernel」字面意) => flat spectrum, 冇 LOS 累積。
呢個係結構性 mismatch, 唔係 fit 數。→ 需「local-in-layer」橋(借用 R4 嘅 P_layer 投影層)。
"""

import math
import os
import json
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__)) + "/../data/"
log = print
res = []
def fc(label, ok, detail=""):
    res.append((label, ok))
    log(("PASS" if ok else "FAIL") + " | " + label + (("  " + detail) if detail else ""))

A_obs = 1.01  # SPT+Planck A_φφ = 1.01 ± 0.08

def los_lensing_shape(L):
    """standard line-of-sight 投影之透鏡 power 形狀 (有 LOS 累積峰)"""
    return L ** 2 / (1 + (L / 150.0) ** 2.5)

def local_4pt_shape(L):
    """local G(0) 4pt: flat, 無 LOS 長程結構"""
    return np.ones_like(L) * 100.0

L = np.logspace(1.5, 3, 50)
lens_shape = los_lensing_shape(L)
local_shape = local_4pt_shape(L)

shape_lens = np.std(np.log(lens_shape))
shape_local = np.std(np.log(local_shape))

print(f"  A_φφ 實測 (SPT+Planck) = {A_obs} ± 0.08")
print(f"  LOS lensing shape std(log) = {shape_lens:.3f}  (有 LOS 結構/峰)")
print(f"  local 4pt shape  std(log)  = {shape_local:.5f}  (flat)")

fc("實測透鏡配 ΛCDM line-of-sight 模型 (A_φφ ~ 1)", abs(A_obs - 1.0) < 0.1)
fc("標準 lensing C_ℓ 有 LOS 特徵結構 (非 flat)",
   shape_lens > 2 * shape_local)
fc("IDCM 純 local G(0) 4pt 係 flat — 無 lensing 之 LOS 峰",
   shape_local < 1e-3)

print("""
  ★★ 誠實判決:
    - CMB 透鏡 (Planck/ACT C_ℓ^φφ, A_φφ~1) 在標準 = line-of-sight 投影嘅直接證據。
    - 純 local 4pt (C1「無傳輸 kernel」字面) 只能產 flat spectrum, 無 LOS 累積峰。
      => 若 IDCM**唔**加「等效 LOS 投影層」, 就無法以字面 local G(0) 復現透鏡形狀.
    - 呢個係結構性 mismatch, 唔係某數 fit 唔到 — 係「形狀/拓撲層」唔同.

  ★ 但有後路 (R4 已開): 若把 lensing 寫成「P_layer(ℓ) 折射調製」= 等效把 LOS 積分
     平移為 ℓ-層呢. 呢個係 🔴 未閉合嘅橋 — C1「純 local」一句唔夠, 要「local-in-layer」.
""")

fail = sum(1 for _, o in res if not o)
log(f"==== {len(res)-fail}/{len(res)} PASS ====")
jp = OUT + "07_lensing.json"
data = {"note": "C1 lensing: local flat 4pt vs LOS shape — structural mismatch, need layer-projection bridge",
        "A_phiphi_obs": A_obs, "lensing_structural": "mismatch_requires_layer_bridge",
        "n_pass": len(res) - fail, "n_tot": len(res)}
with open(jp, "w") as f:
    json.dump(data, f, indent=2)
exit(0 if fail == 0 else 1)