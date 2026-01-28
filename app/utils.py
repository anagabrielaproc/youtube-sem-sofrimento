import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from app import db
from app.models import Channel

def get_youtube_client(api_key):
    if not api_key:
        return None
    try:
        return build('youtube', 'v3', developerKey=api_key, cache_discovery=False)
    except Exception as e:
        print(f"Erro ao criar cliente YouTube: {e}")
        return None

def search_youtube_videos(api_key, query, max_results=50, published_after=None, min_views=0, max_views=None, min_subs=0, max_subs=None, deep_analysis=False):
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

    try:
        search_response = youtube.search().list(**search_params).execute()
        items = search_response.get('items', [])
        if not items:
            return []

        video_ids = [item['id']['videoId'] for item in items]
        
        # Obter estatísticas dos vídeos
        video_items = []
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            video_response = youtube.videos().list(
                part='statistics,snippet',
                id=','.join(batch_ids)
            ).execute()
            video_items.extend(video_response.get('items', []))
        
        # Obter IDs únicos de canais para buscar estatísticas
        channel_ids = list(set([v['snippet']['channelId'] for v in video_items if 'snippet' in v]))
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
            try:
                v_stats = v.get('statistics', {})
                v_snippet = v.get('snippet', {})
                c_id = v_snippet.get('channelId')
                c_data = channels_info.get(c_id)
                
                if not c_data: continue
                
                views = int(v_stats.get('viewCount', 0))
                subs = int(c_data.get('statistics', {}).get('subscriberCount', 0))
                v_count = int(c_data.get('statistics', {}).get('videoCount', 0))
                c_created = c_data.get('snippet', {}).get('publishedAt', '')
                
                # Filtros básicos
                if min_views > 0 and views < min_views: continue
                if max_views and views > max_views: continue
                if min_subs > 0 and subs < min_subs: continue
                if max_subs and subs > max_subs: continue

                # Lógica de Oportunidade
                opportunity = "Saturado"
                if c_created:
                    created_dt = datetime.strptime(c_created, '%Y-%m-%dT%H:%M:%SZ')
                    days_old = (datetime.utcnow() - created_dt).days
                    if days_old <= 30: opportunity = "Ótima Oportunidade"
                    elif days_old <= 90: opportunity = "Boa Oportunidade"
                
                score = round((views / subs * 100), 1) if subs > 0 else 0

                # SALVAR OU ATUALIZAR NO BANCO DE DADOS (A mágica acontece aqui)
                channel_db = Channel.query.filter_by(youtube_id=c_id).first()
                if not channel_db:
                    channel_db = Channel(youtube_id=c_id)
                
                channel_db.title = v_snippet.get('channelTitle')
                channel_db.thumbnail = c_data.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url')
                channel_db.subscribers = subs
                channel_db.video_count = v_count
                channel_db.created_at = created_dt if c_created else None
                channel_db.score = score
                channel_db.opportunity_label = opportunity
                channel_db.last_updated = datetime.utcnow()
                
                db.session.add(channel_db)

                res = {
                    'video_id': v['id'],
                    'title': v_snippet.get('title', ''),
                    'thumbnail': v_snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'channel_title': v_snippet.get('channelTitle', ''),
                    'channel_id': c_id,
                    'published_at': datetime.strptime(v_snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y'),
                    'views': views,
                    'formatted_views': format_number(views),
                    'subscribers': subs,
                    'formatted_subs': format_number(subs),
                    'channel_created_at': created_dt.strftime('%d/%m/%Y') if c_created else 'N/A',
                    'opportunity': opportunity,
                    'score': score
                }
                final_results.append(res)
            except:
                continue
        
        db.session.commit() # Salva tudo no banco
        return final_results
    except Exception as e:
        print(f"Erro na busca: {e}")
        return []

def format_number(num):
    try:
        num = int(num)
        if num >= 1000000: return f"{num/1000000:.1f}M"
        if num >= 1000: return f"{num/1000:.1f}K"
        return str(num)
    except:
        return "0"
