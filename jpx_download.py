import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import re

JPX_URL = "https://www.jpx.co.jp/markets/derivatives/trading-volume/index.html"

BASE_DIR = Path("data")
BASE_DIR.mkdir(exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("JPXページを取得しています...")

response = requests.get(
    JPX_URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("ページ取得成功")

# ページ内のリンクを確認
links = soup.find_all("a")

target_link = None

for link in links:
    text = link.get_text(" ", strip=True)

    if "デリバティブ建玉残高表" in text:
        href = link.get("href")

        if href:
            target_link = href
            print("対象リンクを発見:")
            print(text)
            print(href)
            break

if not target_link:
    raise Exception(
        "デリバティブ建玉残高表のリンクが見つかりませんでした"
    )

# 相対URLの場合は絶対URLにする
from urllib.parse import urljoin

file_url = urljoin(JPX_URL, target_link)

print("ダウンロードURL:")
print(file_url)

# ファイル取得
file_response = requests.get(
    file_url,
    headers=headers,
    timeout=60
)

file_response.raise_for_status()

# 拡張子を取得
content_type = file_response.headers.get("Content-Type", "")

if "zip" in content_type.lower():
    extension = ".zip"
elif "excel" in content_type.lower():
    extension = ".xlsx"
else:
    extension = ".dat"

filename = BASE_DIR / f"{today}_derivatives_open_interest{extension}"

filename.write_bytes(file_response.content)

print("ダウンロード完了")
print(filename)
