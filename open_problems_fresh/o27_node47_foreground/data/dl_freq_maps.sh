#!/bin/bash
# 下載 Planck HFI 頻率 maps (100/143/217/353 GHz) — R3.01 full nside2048
# 用於 node47 多頻譜前景檢查 (O27)
cd /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o27_node47_foreground/data
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
for id in "HFI_SkyMap_100_2048_R3.01_full.fits" "HFI_SkyMap_143_2048_R3.01_full.fits" "HFI_SkyMap_217_2048_R3.01_full.fits" "HFI_SkyMap_353_2048_R3.01_full.fits"; do
  if [ -s "$id" ]; then echo "SKIP $id (exists)"; continue; fi
  echo ">>> $id"
  curl -C - --retry 3 --retry-delay 5 -A "$UA" -o "$id" "https://pla.esac.esa.int/pla/aio/product-action?MAP.MAP_ID=${id}"
  RC=$?
  echo ">>> $id done RC=$RC size=$(stat -c%s "$id" 2>/dev/null)"
done
echo "ALL FREQ MAPS DONE"
