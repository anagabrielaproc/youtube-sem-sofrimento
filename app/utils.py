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
        'order': 'relevance'
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

        # Obter detalhes dos vídeos (views, likes, comments, duration)
        video_response = youtube.videos().list(
            part='statistics,snippet,contentDetails',
            id=','.join(video_ids)
        ).execute()

        video_items = video_response.get('items', [])
        channel_ids = list(set([v['snippet']['channelId'] for v in video_items]))

        # Obter detalhes dos canais (inscritos, data de criação)
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
            v_stats = v['statistics']
            v_snippet = v['snippet']
            v_details = v['contentDetails']
            c_id = v_snippet['channelId']
            c_data = channels_info.get(c_id, {})
            
            if not c_data: continue
            
            c_stats = c_data.get('statistics', {})
            c_snippet = c_data.get('snippet', {})
            
            views = int(v_stats.get('viewCount', 0))
            likes = int(v_stats.get('likeCount', 0))
            comments = int(v_stats.get('commentCount', 0))
            subs = int(c_stats.get('subscriberCount', 0))
            total_videos = int(c_stats.get('videoCount', 0))
            
            # Aplicar filtros
            if views < min_views: continue
            if likes < min_likes: continue
            if subs < min_subs: continue
            if max_subs is not None and subs > max_subs: continue

            # Calcular Score (Views / Subs ratio)
            score = round((views / subs * 100), 1) if subs > 0 else 0
            
            # Lógica de Oportunidade
            channel_created_at = c_snippet.get('publishedAt', '')
            opportunity = "Saturado"
            opportunity_color = "#6c757d" # Cinza
            
            if channel_created_at:
                created_dt = datetime.strptime(channel_created_at, '%Y-%m-%dT%H:%M:%SZ')
                now = datetime.utcnow()
                months_old = (now.year - created_dt.year) * 12 + now.month - created_dt.month
                
                if months_old <= 1:
                    opportunity = "Ótima Oportunidade"
                    opportunity_color = "#28a745" # Verde
                elif 1 < months_old <= 3:
                    opportunity = "Boa Oportunidade"
                    opportunity_color = "#ffc107" # Amarelo
                else:
                    opportunity = "Saturado"
                    opportunity_color = "#dc3545" # Vermelho/Cinza

            final_results.append({
                'video_id': v['id'],
                'title': v_snippet['title'],
                'thumbnail': v_snippet['thumbnails']['high']['url'],
                'channel_title': v_snippet['channelTitle'],
                'channel_id': c_id,
                'published_at': datetime.strptime(v_snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y'),
                'channel_created_at': datetime.strptime(channel_created_at, '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y') if channel_created_at else 'N/A',
                'views': views,
                'likes': likes,
                'comments': comments,
                'subscribers': subs,
                'total_videos': total_videos,
                'duration': format_duration(v_details.get('duration', '')),
                'score': score,
                'opportunity': opportunity,
                'opportunity_color': opportunity_color,
                'formatted_views': format_number(views),
                'formatted_likes': format_number(likes),
                'formatted_comments': format_number(comments),
                'formatted_subs': format_number(subs)
            })

        return final_results
    except Exception as e:
        print(f"Erro na API do YouTube: {e}")
        return []

def format_duration(duration_str):
    if not duration_str: return "00:00"
    try:
        duration = isodate.parse_duration(duration_str)
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
    except:
        return "00:00"

def format_number(num):
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    if num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)
