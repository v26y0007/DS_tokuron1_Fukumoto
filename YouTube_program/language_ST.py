import pandas as pd
import isodate
from googleapiclient.discovery import build
from langdetect import detect
import re
import time

# --- 設定 ---
API_KEY = 'AIzaSyB66NPca8zGHZImB6yqMun7XF6k5Ygfcg8'
CHANNEL_ID = 'UCwjAKjycHHT1QzHrQN5Stww'

youtube = build('youtube', 'v3', developerKey=API_KEY)

def clean_text(text):
    """絵文字やURL、記号を除去して言語判定の精度を上げる"""
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def get_comment_languages_for_video(video_id):
    """動画から最新のコメントを最大100件取得し、言語比率を算出する"""
    langs = []
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,  # 1動画あたりの最大サンプリング数
            textFormat='plainText'
        ).execute()
        
        for item in response.get('items', []):
            text = item['snippet']['topLevelComment']['snippet']['textDisplay']
            cleaned = clean_text(text)
            if not cleaned:
                continue
            try:
                langs.append(detect(cleaned))
            except:
                pass
    except Exception as e:
        # コメントが非公開の動画などはスキップ
        return {}

    if not langs:
        return {}

    # 言語ごとの比率を計算
    total = len(langs)
    lang_counts = pd.Series(langs).value_counts()
    ratios = {lang: count / total for lang, count in lang_counts.items()}
    return ratios

def analyze_and_split_all_videos(channel_id):
    # 1. チャンネルの全動画リストを取得
    ch_response = youtube.channels().list(part='contentDetails', id=channel_id).execute()
    uploads_id = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    video_list = []
    next_page_token = None

    print("全動画のリストを取得中...")
    while True:
        playlist_res = youtube.playlistItems().list(
            part='contentDetails', playlistId=uploads_id, maxResults=50, pageToken=next_page_token
        ).execute()
        
        v_ids = [item['contentDetails']['videoId'] for item in playlist_res['items']]

        v_res = youtube.videos().list(
            part='snippet,statistics,contentDetails', id=','.join(v_ids)
        ).execute()

        for video in v_res['items']:
            duration_iso = video['contentDetails']['duration']
            duration_sec = isodate.parse_duration(duration_iso).total_seconds()
            
            # 再生時間が60秒以下ならショートと判定
            video_type = 'Shorts' if duration_sec <= 60 else 'Regular'

            video_list.append({
                'video_id': video['id'],
                'title': video['snippet']['title'],
                'video_type': video_type,
                'duration_sec': duration_sec,
                'view_count': int(video['statistics'].get('viewCount', 0)),
                'like_count': int(video['statistics'].get('likeCount', 0)),
                'comment_count': int(video['statistics'].get('commentCount', 0)),
                'published_at': video['snippet']['publishedAt']
            })

        next_page_token = playlist_res.get('nextPageToken')
        if not next_page_token: break

    df_videos = pd.DataFrame(video_list)
    print(f"全動画のリスト化が完了しました（合計: {len(df_videos)}件）")

    # 2. 各動画の言語分析を実行
    print("順次コメントの言語を解析します（これには数分かかります）...")
    ja_ratios = []
    en_ratios = []
    other_ratios = []

    for idx, row in df_videos.iterrows():
        ratios = get_comment_languages_for_video(row['video_id'])
        
        ja_ratios.append(ratios.get('ja', 0.0))
        en_ratios.append(ratios.get('en', 0.0))
        
        # 日本語・英語以外の合計を「その他」とする
        other_val = sum([val for key, val in ratios.items() if key not in ['ja', 'en']])
        other_ratios.append(other_val)
        
        # API制限（負荷）対策のウェイト
        time.sleep(0.1)

    # 分析結果をデータフレームに追加
    df_videos['jp_ratio'] = ja_ratios
    df_videos['en_ratio'] = en_ratios
    df_videos['other_ratio'] = other_ratios
    df_videos['overseas_total_ratio'] = df_videos['en_ratio'] + df_videos['other_ratio']

    # 3. ショートと通常動画でファイルを切り分けて保存
    df_shorts = df_videos[df_videos['video_type'] == 'Shorts']
    df_regular = df_videos[df_videos['video_type'] == 'Regular']

    df_shorts.to_csv('ST_shorts_language_analysis.csv', index=False, encoding='utf-8-sig')
    df_regular.to_csv('ST_regular_language_analysis.csv', index=False, encoding='utf-8-sig')

    print("\n==========================================")
    print("処理が正常に完了しました！")
    print(f"ショート動画データ: {len(df_shorts)}件 -> all_shorts_language_analysis.csv")
    print(f"通常動画データ: {len(df_regular)}件 -> all_regular_language_analysis.csv")
    print("==========================================")

# 実行
analyze_and_split_all_videos(CHANNEL_ID)