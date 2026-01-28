import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate

def get_youtube_client(api_key):
    if not api_key:
        return None
    try:
        return build('youtube', 'v3', developerKey=api_key, cache_discovery=False)
    except Exception as e:
        print(f"Erro ao criar cliente YouTube: {e}")
        return None

def search_youtube_videos(api_key, query, max_results=50, published_after=None, published_before=None, min_views=0, max_views=None, min_subs=0, max_subs=None):
    youtube = get_youtube_client(api_key)
    if not youtube:
        return []

    # 1. Busca inicial de vídeos
    search_params = {
        'q': query,
        'part': 'snippet',
        'type': 'video',
        'maxResults': max_results,
        'order': 'relevance'
    }
    if published_after:
        search_params['publishedAfter'] = published_after
    if published_before:
        search_params['publishedBefore'] = published_before

    try:
        search_response = youtube.search().list(**search_params).execute()
        items = search_response.get('items', [])
        if not items:
            return []

        video_ids = [item['id']['videoId'] for item in items]
        
        # 2. Obter estatísticas dos vídeos em um único lote
        video_response = youtube.videos().list(
            part='statistics,snippet,contentDetails',
            id=','.join(video_ids)
        ).execute()
        video_items = video_response.get('items', [])
        
        channel_ids = list(set([v['snippet']['channelId'] for v in video_items]))
        
        # 3. Obter estatísticas dos canais em um único lote
        channels_info = {}
        for i in range(0, len(channel_ids), 50):
            batch_ids = channel_ids[i:i+50]
            channel_response = youtube.channels().list(
                part='statistics,snippet',
                id=','.join(batch_ids)
            ).execute()
            for c in channel_response.get('items', []):
                channels_info[c['id']] = c

        final_results = []
        for v in video_items:
            v_stats = v.get('statistics', {})
            v_snippet = v.get('snippet', {})
            c_id = v_snippet.get('channelId')
            c_data = channels_info.get(c_id, {})
            
            if not c_data: continue
            
            c_stats = c_data.get('statistics', {})
            c_snippet = c_data.get('snippet', {})
            
            views = int(v_stats.get('viewCount', 0))
            subs = int(c_stats.get('subscriberCount', 0))
            
            # Aplicar filtros de pós-processamento solicitados
            if min_views > 0 and views < min_views: continue
            if max_views and views > max_views: continue
            if min_subs > 0 and subs < min_subs: continue
            if max_subs and subs > max_subs: continue

            # Data de criação do canal
            channel_published_at = c_snippet.get('publishedAt', '')
            channel_created_date = 'N/A'
            if channel_published_at:
                channel_created_date = datetime.strptime(channel_published_at, '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y')

            final_results.append({
                'video_id': v['id'],
                'title': v_snippet.get('title', ''),
                'thumbnail': v_snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'channel_title': v_snippet.get('channelTitle', ''),
                'channel_id': c_id,
                'published_at': datetime.strptime(v_snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y'),
                'channel_created_at': channel_created_date,
                'views': views,
                'subscribers': subs,
                'formatted_views': format_number(views),
                'formatted_subs': format_number(subs)
            })

        return final_results
    except Exception as e:
        print(f"Erro na busca: {e}")
        return []

def format_number(num):
    if num >= 1000000: return f"{num/1000000:.1f}M"
    if num >= 1000: return f"{num/1000:.1f}K"
    return str(num)
