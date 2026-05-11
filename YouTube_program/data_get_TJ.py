import pandas as pd
from googleapiclient.discovery import build

# --- 設定 ---
API_KEY = 'AIzaSyB66NPca8zGHZImB6yqMun7XF6k5Ygfcg8'
CHANNEL_ID = 'UCoEIdZkDEZdrCDCJSqwifzw' # 例: 'UC7eafEb07L9_8S9Mscb_T2w'

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_channel_videos(channel_id):
    # 1. チャンネルの「全アップロード動画」が入っているプレイリストIDを取得
    ch_response = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    
    uploads_playlist_id = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    video_data = []
    next_page_token = None

    # 2. プレイリスト内の動画IDを順次取得
    while True:
        playlist_response = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        video_ids = [item['contentDetails']['videoId'] for item in playlist_response['items']]

        # 3. 各動画の詳細統計（再生数、高評価数など）を取得
        video_response = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids)
        ).execute()

        for video in video_response['items']:
            video_data.append({
                'title': video['snippet']['title'],
                'published_at': video['snippet']['publishedAt'],
                'view_count': int(video['statistics'].get('viewCount', 0)),
                'like_count': int(video['statistics'].get('likeCount', 0)),
                'comment_count': int(video['statistics'].get('commentCount', 0)),
                'video_id': video['id']
            })

        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    return pd.DataFrame(video_data)

# 実行と保存
df = get_channel_videos(CHANNEL_ID)
df.to_csv('TJ_youtube_data.csv', index=False, encoding='utf-8-sig')
print(f"収集完了！ {len(df)} 件の動画データを保存しました。")