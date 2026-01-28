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

def search_youtube_videos(api_key, query, max_results=50, published_after=None, min_views=0, max_views=None, min_subs=0, max_subs=None, deep_analysis=False):
    """
    Busca vídeos no YouTube. 
    Se deep_analysis=False, foca em velocidade (Garimpo).
    Se deep_analysis=True, busca dados extras do canal (Promissores).
    """
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
        
        # Obter estatísticas dos vídeos em blocos para evitar erros
        video_items = []
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            video_response = youtube.videos().list(
                part='statistics,snippet',
                id=','.join(batch_ids)
            ).execute()
            video_items.extend(video_response.get('items', []))
        
        channels_info = {}
        if deep_analysis:
            # Obter IDs únicos de canais
            channel_ids = list(set([v['snippet']['channelId'] for v in video_items if 'snippet' in v]))
            # Buscar dados dos canais em blocos
            for i in range(0, len(channel_ids), 50):
                batch_ids = channel_ids[i:i+50]
                try:
                    channel_response = youtube.channels().list(
                        part='statistics,snippet',
                        id=','.join(batch_ids)
                    ).execute()
                    for c in channel_response.get('items', []):
                        channels_info[c['id']] = c
                except Exception as e:
                    print(f"Erro ao buscar canais: {e}")
                    continue

        final_results = []
        for v in video_items:
            try:
                v_stats = v.get('statistics', {})
                v_snippet = v.get('snippet', {})
                c_id = v_snippet.get('channelId')
                
                if not c_id: continue
                
                views = int(v_stats.get('viewCount', 0))
                
                # Filtros de views
                if min_views > 0 and views < min_views: continue
                if max_views and views > max_views: continue

                res = {
                    'video_id': v['id'],
                    'title': v_snippet.get('title', ''),
                    'thumbnail': v_snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'channel_title': v_snippet.get('channelTitle', ''),
                    'channel_id': c_id,
                    'published_at': datetime.strptime(v_snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y') if 'publishedAt' in v_snippet else 'N/A',
                    'views': views,
                    'formatted_views': format_number(views),
                }

                if deep_analysis:
                    c_data = channels_info.get(c_id)
                    if not c_data: continue
                    
                    c_stats = c_data.get('statistics', {})
                    c_snippet = c_data.get('snippet', {})
                    
                    subs = int(c_stats.get('subscriberCount', 0))
                    video_count = int(c_stats.get('videoCount', 0))
                    
                    # Filtros de inscritos
                    if min_subs > 0 and subs < min_subs: continue
                    if max_subs and subs > max_subs: continue

                    # Lógica de Oportunidade
                    channel_published_at = c_snippet.get('publishedAt', '')
                    opportunity = "Saturado"
                    opportunity_color = "#6c757d"
                    created_date_str = 'N/A'
                    
                    if channel_published_at:
                        try:
                            created_dt = datetime.strptime(channel_published_at, '%Y-%m-%dT%H:%M:%SZ')
                            created_date_str = created_dt.strftime('%d/%m/%Y')
                            days_old = (datetime.utcnow() - created_dt).days
                            if days_old <= 30:
                                opportunity = "Ótima Oportunidade"
                                opportunity_color = "#28a745"
                            elif days_old <= 90:
                                opportunity = "Boa Oportunidade"
                                opportunity_color = "#ffc107"
                        except:
                            pass

                    res.update({
                        'subscribers': subs,
                        'formatted_subs': format_number(subs),
                        'video_count': video_count,
                        'channel_created_at': created_date_str,
                        'opportunity': opportunity,
                        'opportunity_color': opportunity_color,
                        'score': round((views / subs * 100), 1) if subs > 0 else 0
                    })
                
                final_results.append(res)
            except Exception as e:
                print(f"Erro ao processar vídeo {v.get('id')}: {e}")
                continue

        return final_results
    except Exception as e:
        print(f"Erro geral na busca: {e}")
        return []

def format_number(num):
    try:
        num = int(num)
        if num >= 1000000: return f"{num/1000000:.1f}M"
        if num >= 1000: return f"{num/1000:.1f}K"
        return str(num)
    except:
        return "0"
