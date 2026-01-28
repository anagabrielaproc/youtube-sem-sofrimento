import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate

def get_youtube_client(api_key):
    if not api_key:
        return None
    return build('youtube', 'v3', developerKey=api_key)

def search_youtube_videos(api_key, query, max_results=50, published_after=None, published_before=None, region_code=None, relevance_language=None, min_views=0, min_likes=0, min_subs=0, max_subs=None):
    youtube = get_youtube_client(api_key)
    if not youtube:
        return []

    search_params = {
        'q': query,
        'part': 'snippet',
        'type': 'video',
        'maxResults': max_results,
        'order': 'viewCount'
    }

    if published_after:
        search_params['publishedAfter'] = published_after
    if published_before:
        search_params['publishedBefore'] = published_before
    if region_code and region_code != 'all':
        search_params['regionCode'] = region_code
    if relevance_language and relevance_language != 'all':
        search_params['relevanceLanguage'] = relevance_language

    try:
        search_response = youtube.search().list(**search_params).execute()
        
        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        if not video_ids:
            return []

        # Obter detalhes dos vídeos (views, likes)
        video_response = youtube.videos().list(
            part='statistics,snippet,contentDetails',
            id=','.join(video_ids)
        ).execute()

        channels_data = {}
        for item in video_response.get('items', []):
            views = int(item['statistics'].get('viewCount', 0))
            likes = int(item['statistics'].get('likeCount', 0))
            
            # Aplicar filtros de vídeo (views e likes mínimos)
            if views < min_views or likes < min_likes:
                continue

            channel_id = item['snippet']['channelId']
            if channel_id not in channels_data:
                channels_data[channel_id] = {
                    'id': channel_id,
                    'title': item['snippet']['channelTitle'],
                    'videos': []
                }
            
            channels_data[channel_id]['videos'].append({
                'id': item['id'],
                'title': item['snippet']['title'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'views': views,
                'likes': likes,
                'published_at': item['snippet']['publishedAt']
            })

        if not channels_data:
            return []

        # Obter detalhes dos canais (inscritos, total de vídeos)
        channel_ids = list(channels_data.keys())
        # A API permite até 50 IDs por vez
        final_results = []
        
        for i in range(0, len(channel_ids), 50):
            batch_ids = channel_ids[i:i+50]
            channel_response = youtube.channels().list(
                part='statistics,snippet',
                id=','.join(batch_ids)
            ).execute()

            for item in channel_response.get('items', []):
                c_id = item['id']
                stats = item['statistics']
                subs = int(stats.get('subscriberCount', 0))
                
                # Aplicar filtros de canal (inscritos mín/máx)
                if subs < min_subs:
                    continue
                if max_subs is not None and subs > max_subs:
                    continue
                
                channel_info = channels_data[c_id]
                channel_info['subscribers'] = subs
                channel_info['total_views'] = int(stats.get('viewCount', 0))
                channel_info['total_videos'] = int(stats.get('videoCount', 0))
                channel_info['thumbnail'] = item['snippet']['thumbnails']['default']['url']
                channel_info['published_at'] = item['snippet']['publishedAt']
                
                # Calcular média de views dos vídeos encontrados
                video_views = [v['views'] for v in channel_info['videos']]
                channel_info['avg_views_found'] = sum(video_views) / len(video_views) if video_views else 0
                
                # Critério de Canal Promissor (ajustado)
                is_promising = False
                if channel_info['subscribers'] < 100000 and channel_info['avg_views_found'] > (channel_info['subscribers'] * 0.3):
                    is_promising = True
                
                channel_info['is_promising'] = is_promising
                final_results.append(channel_info)

        return final_results
    except Exception as e:
        print(f"Erro na API do YouTube: {e}")
        return []
