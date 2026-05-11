import csv
import re
from pathlib import Path

import requests
from lxml import html


# =========================
# 設定
# =========================
URL = "https://www.billboard-japan.com/charts/detail?a=hot100"
OUTPUT_CSV = "billboard_japan_hot100.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}


# =========================
# 関数
# =========================
def clean_text(text):
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def get_text(element, xpath):
    result = element.xpath(xpath)
    if not result:
        return ""

    value = result[0]

    if isinstance(value, str):
        return clean_text(value)

    return clean_text(value.text_content())


def remove_label(text, label):
    text = clean_text(text)
    return text.replace(label, "").strip()


def parse_int_or_blank(text):
    text = clean_text(text).replace(",", "")

    if text == "" or text == "-":
        return ""

    try:
        return int(text)
    except ValueError:
        return text


def extract_points(tr):
    """
    総合ポイント数を取得する。
    取得できない順位もあるため、見つからなければ空文字を返す。
    """

    # ユーザー指定に近いXPathで取得
    point_text = get_text(tr, "./td[2]/div[2]/div/div/p[3]")
    if point_text:
        return point_text

    # 予備: 「総合ポイント数」の次にある数値を探す
    texts = [clean_text(t) for t in tr.xpath(".//text()")]
    texts = [t for t in texts if t]

    for i, t in enumerate(texts):
        if "総合ポイント数" in t:
            for next_text in texts[i + 1:]:
                if re.fullmatch(r"[0-9,]+", next_text):
                    return next_text

    return ""


# =========================
# HTML取得
# =========================
response = requests.get(URL, headers=HEADERS, timeout=20)
response.raise_for_status()

tree = html.fromstring(response.content)


# =========================
# 公開日取得
# =========================
page_text = clean_text(tree.text_content())
m = re.search(r"\[\s*(\d{4}/\d{2}/\d{2})\s*公開\s*\]", page_text)
chart_date = m.group(1) if m else ""


# =========================
# ランキング行を取得
# =========================
# 「前回：」を含むtrをランキング行として扱う
ranking_rows = tree.xpath('//tr[.//text()[contains(., "前回：")]]')

if not ranking_rows:
    raise RuntimeError("ランキング行が見つかりませんでした。ページ構造を確認してください。")


# =========================
# データ抽出
# =========================
rows = []

for tr in ranking_rows:
    rank_raw = get_text(tr, "./td[2]/div[1]/p[1]")
    previous_rank_raw = get_text(tr, "./td[2]/div[1]/p[3]/span[1]")
    chart_in_raw = get_text(tr, "./td[2]/div[1]/p[3]/span[2]")

    title = get_text(tr, "./td[2]/div[2]/p[1]")

    artist = get_text(tr, "./td[2]/div[2]/p[2]/a")
    if not artist:
        artist = get_text(tr, "./td[2]/div[2]/p[2]")

    total_points_raw = extract_points(tr)

    rank = parse_int_or_blank(rank_raw)
    previous_rank = remove_label(previous_rank_raw, "前回：")
    chart_in = remove_label(chart_in_raw, "チャートイン：")
    total_points = parse_int_or_blank(total_points_raw)

    # rankが取得できない行はスキップ
    if rank == "":
        continue

    # 1〜100位以外はスキップ
    if isinstance(rank, int) and not (1 <= rank <= 100):
        continue

    # タイトルもアーティストもない場合はスキップ
    if not title and not artist:
        print(f"{rank}位: データなしのためスキップ")
        continue

    rows.append({
        "chart_date": chart_date,
        "rank": rank,
        "previous_rank": previous_rank,
        "chart_in": chart_in,
        "title": title,
        "artist": artist,
        "total_points": total_points,
        "total_points_raw": total_points_raw,
    })

    print(f"{rank}位: {title} / {artist}")


# =========================
# 順位で並び替え
# =========================
rows.sort(key=lambda x: int(x["rank"]))


# =========================
# CSV出力
# =========================
fieldnames = [
    "chart_date",
    "rank",
    "previous_rank",
    "chart_in",
    "title",
    "artist",
    "total_points",
    "total_points_raw",
]

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("==============================")
print(f"取得件数: {len(rows)} 件")
print(f"CSV出力完了: {Path(OUTPUT_CSV).resolve()}")
print("==============================")