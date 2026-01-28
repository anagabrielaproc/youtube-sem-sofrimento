from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Channel, SearchHistory, User
from app.utils import search_youtube_videos
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/garimpo', methods=['GET', 'POST'])
@login_required
def garimpo():
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        language = request.form.get('language')
        region = request.form.get('region')
        
        # Datas
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        period = request.form.get('period_btn') # Botões rápidos
        
        published_after = None
        published_before = None
        now = datetime.utcnow()

        if period:
            if period == 'today':
                published_after = (now - timedelta(days=1)).isoformat() + 'Z'
            elif period == 'yesterday':
                published_after = (now - timedelta(days=2)).isoformat() + 'Z'
                published_before = (now - timedelta(days=1)).isoformat() + 'Z'
            elif period == 'week':
                published_after = (now - timedelta(days=7)).isoformat() + 'Z'
            elif period == 'month':
                published_after = (now - timedelta(days=30)).isoformat() + 'Z'
            elif period == 'year':
                published_after = (now - timedelta(days=365)).isoformat() + 'Z'
        elif start_date:
            published_after = datetime.strptime(start_date, '%Y-%m-%d').isoformat() + 'Z'
            if end_date:
                published_before = datetime.strptime(end_date, '%Y-%m-%d').isoformat() + 'Z'

        # Filtros numéricos
        min_views = int(request.form.get('min_views') or 0)
        min_likes = int(request.form.get('min_likes') or 0)
        min_subs = int(request.form.get('min_subs') or 0)
        max_subs_val = request.form.get('max_subs')
        max_subs = int(max_subs_val) if max_subs_val and max_subs_val.isdigit() else None
        limit = int(request.form.get('limit') or 50)

        api_key = current_app.config.get('YOUTUBE_API_KEY')

        if not api_key:
            flash('API Key do YouTube não configurada.', 'warning')
        else:
            results = search_youtube_videos(
                api_key, 
                query, 
                max_results=limit, 
                published_after=published_after,
                published_before=published_before,
                relevance_language=language,
                region_code=region,
                min_views=min_views,
                min_likes=min_likes,
                min_subs=min_subs,
                max_subs=max_subs
            )
            
            # Salvar histórico
            history = SearchHistory(query=query, user_id=current_user.id)
            db.session.add(history)
            
            # Salvar/Atualizar canais promissores no DB
            for res in results:
                if res['is_promising']:
                    channel = Channel.query.filter_by(youtube_id=res['id']).first()
                    if not channel:
                        channel = Channel(
                            youtube_id=res['id'],
                            title=res['title'],
                            thumbnail=res['thumbnail'],
                            subscribers=res['subscribers'],
                            video_count=res['total_videos'],
                            view_count=res['total_views'],
                            created_at=datetime.fromisoformat(res['published_at'].replace('Z', '')),
                            is_promising=True
                        )
                        db.session.add(channel)
                    else:
                        channel.subscribers = res['subscribers']
                        channel.view_count = res['total_views']
                        channel.video_count = res['total_videos']
                        channel.last_updated = datetime.utcnow()
            
            db.session.commit()

    return render_template('garimpo.html', results=results)

@main.route('/promissores')
@login_required
def promissores():
    channels = Channel.query.filter_by(is_promising=True).order_by(Channel.last_updated.desc()).all()
    return render_template('promissores.html', channels=channels)

@main.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if request.method == 'POST':
        flash('Configurações salvas com sucesso!', 'success')
    return render_template('configuracoes.html')
