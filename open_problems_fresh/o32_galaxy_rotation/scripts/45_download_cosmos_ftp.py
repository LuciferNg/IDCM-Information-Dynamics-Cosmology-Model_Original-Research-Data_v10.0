#!/usr/bin/env python3
"""
COSMOS2015 下載 — Python ftplib 直接連 IAP FTP
"""
import ftplib
import os

HOST = "ftp.iap.fr"
PATH = "/pub/from_users/hjmcc/COSMOS2015"
OUT = "data/obs_data"

os.makedirs(OUT, exist_ok=True)

print("="*78)
print("COSMOS2015 FTP 下載")
print("="*78)

try:
    ftp = ftplib.FTP(HOST, timeout=30)
    ftp.login()
    print(f"✅ 連線成功: {HOST}")
    
    ftp.cwd(PATH)
    print(f"✅ 目錄: {PATH}")
    
    files = []
    ftp.retrlines("LIST", files.append)
    print(f"\n目錄內容 ({len(files)} 項):")
    for f in files:
        print(f"  {f}")
    
    # 下載所有 .fits 同 .dat 文件
    for f in files:
        parts = f.split()
        if len(parts) < 9:
            continue
        name = parts[-1]
        size = parts[-5]
        if any(name.endswith(ext) for ext in ['.fits', '.dat', '.cat', '.gz', '.csv']):
            print(f"  下載: {name} ({size} bytes)...")
            try:
                with open(f"{OUT}/{name}", 'wb') as fh:
                    ftp.retrbinary(f"RETR {name}", fh.write)
                print(f"    ✅ 完成!")
            except Exception as e:
                print(f"    ❌ {e}")
    
    ftp.quit()
    print("\n✅ 下載完成!")
    
except Exception as e:
    print(f"❌ 錯誤: {e}")
    print("\n嘗試替代方案...")
    
    # 試 CDS 匿名 FTP
    try:
        print(f"\n嘗試 CDS FTP...")
        ftp = ftplib.FTP("cdsarc.u-strasbg.fr", timeout=30)
        ftp.login()
        ftp.cwd("J/A+A/605/A70")
        files = []
        ftp.retrlines("LIST", files.append)
        print(f"CDS 目錄內容:")
        for f in files:
            print(f"  {f}")
        ftp.quit()
    except Exception as e2:
        print(f"CDS FTP 也失敗: {e2}")