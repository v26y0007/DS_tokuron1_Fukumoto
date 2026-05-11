import pandas as pd
import isodate
from googleapiclient.discovery import build

# --- 設定 ---
API_KEY = 'AIzaSyB66NPca8zGHZImB6yqMun7XF6k5Ygfcg8'
CHANNEL_ID = 'UCoEIdZkDEZdrCDCJSqwifzw'

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_and_split_videos(channel_id):
    # 1. プレイリストID取得
    ch_response = youtube.channels().list(part='contentDetails', id=channel_id).execute()
    uploads_id = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    video_data = []
    next_page_token = None

    while True:
        playlist_res = youtube.playlistItems().list(
            part='contentDetails', playlistId=uploads_id, maxResults=50, pageToken=next_page_token
        ).execute()
        
        v_ids = [item['contentDetails']['videoId'] for item in playlist_res['items']]

        # 2. 動画詳細と長さを取得
        v_res = youtube.videos().list(
            part='snippet,statistics,contentDetails', id=','.join(v_ids)
        ).execute()

        for video in v_res['items']:
            duration_iso = video['contentDetails']['duration']
            duration_sec = isodate.parse_duration(duration_iso).total_seconds()
            
            # 判定（60秒以下をShortsとする）
            video_type = 'Shorts' if duration_sec <= 60 else 'Regular'

            video_data.append({
                'title': video['snippet']['title'],
                'video_type': video_type,
                'duration_sec': duration_sec,
                'view_count': int(video['statistics'].get('viewCount', 0)),
                'like_count': int(video['statistics'].get('likeCount', 0)),
                'comment_count': int(video['statistics'].get('commentCount', 0)),
                'published_at': video['snippet']['publishedAt'],
                'video_id': video['id']
            })

        next_page_token = playlist_res.get('nextPageToken')
        if not next_page_token: break

    # 全データを一度DataFrameにする
    df_all = pd.DataFrame(video_data)

    # 3. データを条件で切り分けて別々に保存
    df_shorts = df_all[df_all['video_type'] == 'Shorts']
    df_regular = df_all[df_all['video_type'] == 'Regular']

    df_shorts.to_csv('TJ_shorts_data.csv', index=False, encoding='utf-8-sig')
    df_regular.to_csv('TJ_regular_data.csv', index=False, encoding='utf-8-sig')

    print(f"保存完了！")
    print(f"ショート動画: {len(df_shorts)}件 -> idol_shorts_data.csv")
    print(f"通常動画: {len(df_regular)}件 -> idol_regular_data.csv")

# 実行
get_and_split_videos(CHANNEL_ID)