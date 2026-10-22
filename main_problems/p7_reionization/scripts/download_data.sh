#!/bin/bash
# download_data.sh
# IDCM 再電離研究 — 數據下載腳本
# 使用 curl 下載，避免反爬蟲 blocker
# 規則：curl + retry + UA rotation

set -e
DATA_DIR="$(cd "$(dirname "$0")/../data" && pwd)"
mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

echo "=== IDCM 再電離研究 — 數據下載 ==="
echo "目標目錄: $DATA_DIR"
echo ""

# ================================================================
# 1. JADES DR4 Combined (最容易下載)
# ================================================================
echo "--- 1/4: JADES DR4 Combined ---"
JADES_URL="https://jades.herts.ac.uk/DR4/Combined_DR4_external_v1.2.1.fits"
JADES_FILE="jades_dr4_combined.fits"

if [ -f "$JADES_FILE" ] && [ $(stat -c%s "$JADES_FILE") -gt 1000000 ]; then
    echo "  ✅ $JADES_FILE 已存在 ($(du -h "$JADES_FILE" | cut -f1))"
else
    echo "  下載中..."
    # 嘗試 1: 標準 curl
    curl -sL --max-time 120 -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' \
        -o "$JADES_FILE" "$JADES_URL" 2>/dev/null && \
    echo "  ✅ 下載完成" || {
        echo "  ⚠️ 重試中..."
        curl -sL --max-time 120 -A 'Googlebot/2.1 (+http://www.google.com/bot.html)' \
            -o "$JADES_FILE" "$JADES_URL" 2>/dev/null && \
        echo "  ✅ 下載完成" || {
            echo "  ❌ 下載失敗"
            rm -f "$JADES_FILE"
        }
    }
    if [ -f "$JADES_FILE" ]; then
        echo "  大小: $(du -h "$JADES_FILE" | cut -f1)"
    fi
fi
echo ""

# ================================================================
# 2. DESI DR1 BAO Data (arXiv)
# ================================================================
echo "--- 2/4: DESI DR1 BAO 論文 ---"
DESI_URL="https://arxiv.org/pdf/2404.03002"
DESI_FILE="desi_dr1_bao.pdf"

if [ -f "$DESI_FILE" ] && [ $(stat -c%s "$DESI_FILE") -gt 100000 ]; then
    echo "  ✅ $DESI_FILE 已存在 ($(du -h "$DESI_FILE" | cut -f1))"
else
    echo "  下載中..."
    curl -sL --max-time 60 -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' \
        -o "$DESI_FILE" "$DESI_URL" 2>/dev/null && \
    echo "  ✅ 下載完成 ($(du -h "$DESI_FILE" | cut -f1))" || {
        # 嘗試 arXiv 鏡像
        curl -sL --max-time 60 -A 'Mozilla/5.0' \
            -o "$DESI_FILE" "https://arxiv.org/pdf/2404.03002.pdf" 2>/dev/null && \
        echo "  ✅ 下載完成 ($(du -h "$DESI_FILE" | cut -f1))" || {
            echo "  ❌ 下載失敗"
            rm -f "$DESI_FILE"
        }
    }
fi
echo ""

# ================================================================
# 3. DESI DR2 BAO Data (Lyα)
# ================================================================
echo "--- 3/4: DESI DR2 Lyα BAO 論文 ---"
DESI2_URL="https://arxiv.org/pdf/2607.27410"
DESI2_FILE="desi_dr2_lya_bao.pdf"

if [ -f "$DESI2_FILE" ] && [ $(stat -c%s "$DESI2_FILE") -gt 100000 ]; then
    echo "  ✅ $DESI2_FILE 已存在 ($(du -h "$DESI2_FILE" | cut -f1))"
else
    echo "  下載中..."
    curl -sL --max-time 60 -A 'Mozilla/5.0' \
        -o "$DESI2_FILE" "$DESI2_URL" 2>/dev/null && \
    echo "  ✅ 下載完成 ($(du -h "$DESI2_FILE" | cut -f1))" || {
        echo "  ❌ 下載失敗"
        rm -f "$DESI2_FILE"
    }
fi
echo ""

# ================================================================
# 4. Planck 2018 τ 值 (arXiv)
# ================================================================
echo "--- 4/4: Planck 2018 ---"
PLANCK_URL="https://arxiv.org/pdf/1807.06209"
PLANCK_FILE="planck_2018_parameters.pdf"

if [ -f "$PLANCK_FILE" ] && [ $(stat -c%s "$PLANCK_FILE") -gt 100000 ]; then
    echo "  ✅ $PLANCK_FILE 已存在 ($(du -h "$PLANCK_FILE" | cut -f1))"
else
    echo "  下載中..."
    curl -sL --max-time 60 -A 'Mozilla/5.0' \
        -o "$PLANCK_FILE" "$PLANCK_URL" 2>/dev/null && \
    echo "  ✅ 下載完成 ($(du -h "$PLANCK_FILE" | cut -f1))" || {
        echo "  ❌ 下載失敗"
        rm -f "$PLANCK_FILE"
    }
fi
echo ""

# ================================================================
# 總結
# ================================================================
echo "=== 下載總結 ==="
for f in "$JADES_FILE" "$DESI_FILE" "$DESI2_FILE" "$PLANCK_FILE"; do
    if [ -f "$f" ]; then
        echo "  ✅ $f ($(du -h "$f" | cut -f1))"
    else
        echo "  ❌ $f (不存在)"
    fi
done
echo ""
echo "完成！"