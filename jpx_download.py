import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin

JPX_URL = "https://www.jpx.co.jp/markets/derivatives/trading-volume/index.html"

BASE_DIR = Path("data")
BASE_DIR.mkdir(exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}

print("JPXページを取得しています...")

response = requests.get(
    JPX_URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()

print("ページ取得成功")

soup = BeautifulSoup(response.text, "html.parser")

# --------------------------------------------------
# ページ内のExcel / ZIP / CSV等のリンクを調査
# --------------------------------------------------

candidates = []

for a in soup.find_all("a", href=True):

    text = a.get_text(" ", strip=True)
    href = a["href"]

    full_url = urljoin(JPX_URL, href)

    # 建玉関連と思われるリンクを抽出
    if any(keyword in text for keyword in [
        "建玉",
        "Open Interest",
        "open interest",
        "OI"
    ]):
        candidates.append((text, full_url))

# --------------------------------------------------
# 候補を表示
# --------------------------------------------------

print("")
print("=== 建玉関連リンク候補 ===")

for text, url in candidates:
    print("TEXT:", text)
    print("URL :", url)
    print("")

# --------------------------------------------------
# 建玉残高表のリンクを特定
# --------------------------------------------------

target = None

for text, url in candidates:

    if "建玉残高表" in text:
        target = url
        break

# --------------------------------------------------
# 見つからなかった場合
# --------------------------------------------------

if target is None:

    print("")
    print("建玉残高表を自動特定できませんでした。")
    print("ページ内のリンク一覧を確認します。")
    print("")

    for a in soup.find_all("a", href=True):

        text = a.get_text(" ", strip=True)
        href = a["href"]

        if href.lower().endswith(
            (".xlsx", ".xls", ".zip", ".csv")
        ):
            print(text)
            print(urljoin(JPX_URL, href))
            print("")

    raise Exception(
        "デリバティブ建玉残高表のリンクを特定できませんでした"
    )

# --------------------------------------------------
# ダウンロード
# --------------------------------------------------

print("対象ファイル:")
print(target)

file_response = requests.get(
    target,
    headers=headers,
    timeout=60
)

file_response.raise_for_status()

# URLから拡張子を取得
path = target.lower()

if ".xlsx" in path:
    extension = ".xlsx"
elif ".xls" in path:
    extension = ".xls"
elif ".zip" in path:
    extension = ".zip"
elif ".csv" in path:
    extension = ".csv"
else:
    extension = ".dat"

filename = (
    BASE_DIR /
    f"{today}_derivatives_open_interest{extension}"
)

filename.write_bytes(file_response.content)

print("")
print("====================================")
print("ダウンロード成功")
print("保存先:", filename)
print("====================================")
