import requests
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# ============================================
# JPX設定
# ============================================

BASE_URL = (
    "https://www.jpx.co.jp/markets/derivatives/"
    "trading-volume/tvdivq00000014nn-att/"
)

# ============================================
# 日本時間の日付を取得
# ============================================

now = datetime.now(ZoneInfo("Asia/Tokyo"))
date_str = now.strftime("%Y%m%d")
display_date = now.strftime("%Y-%m-%d")

# ============================================
# 建玉残高表のファイルURL
# ============================================

filename = f"{date_str}open_interest.xlsx"

file_url = BASE_URL + filename

print("========================================")
print("JPX デリバティブ建玉残高表")
print("========================================")
print("対象日:", display_date)
print("ファイル:", filename)
print("URL:", file_url)
print("")

# ============================================
# 保存先
# ============================================

save_dir = Path("data")

save_dir.mkdir(
    parents=True,
    exist_ok=True
)

save_path = save_dir / f"{display_date}_open_interest.xlsx"

# ============================================
# HTTP設定
# ============================================

headers = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}

# ============================================
# ダウンロード
# ============================================

print("JPXから建玉残高表を取得しています...")

response = requests.get(
    file_url,
    headers=headers,
    timeout=60
)

print("HTTPステータス:", response.status_code)

# ============================================
# ファイル存在確認
# ============================================

if response.status_code == 404:

    print("")
    print("本日の建玉残高表はまだ掲載されていません。")
    print("処理を終了します。")
    exit(0)

response.raise_for_status()

# ============================================
# Excelファイルとして保存
# ============================================

save_path.write_bytes(response.content)

print("")
print("========================================")
print("ダウンロード成功")
print("========================================")
print("保存先:", save_path)
print("ファイルサイズ:", len(response.content), "bytes")
