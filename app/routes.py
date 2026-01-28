from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import SearchHistory, User
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
    query = ""
    language = "all"
    region = "all"
    start_date = ""
    end_date = ""
    period_btn = ""
    min_views = 0
    min_likes = 0
    min_subs = 0
    max_subs = ""
    limit = 50

    if request.method == 'POST':
        query = request.form.get('query')
        language = request.form.get('language', 'all')
        region = request.form.get('region', 'all')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        period_btn = request.form.get('period_btn')
        min_views = int(request.form.get('min_views') or 0)
        min_likes = int(request.form.get('min_likes') or 0)
        min_subs = int(request.form.get('min_subs') or 0)
        max_subs = request.form.get('max_subs')
        limit = int(request.form.get('limit') or 50)

        published_after = None
        published_before = None
        now = datetime.utcnow()

        if period_btn:
            if period_btn == 'today':
                published_after = now.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
            elif period_btn == 'yesterday':
                yesterday = now - timedelta(days=1)
                published_after = yesterday.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
                published_before = yesterday.replace(hour=23, minute=59, second=59).isoformat() + 'Z'
            elif period_btn == 'week':
                published_after = (now - timedelta(days=7)).isoformat() + 'Z'
            elif period_btn == 'month':
                published_after = (now - timedelta(days=30)).isoformat() + 'Z'
            elif period_btn == 'year':
                published_after = (now - timedelta(days=365)).isoformat() + 'Z'
        
        if start_date:
            published_after = datetime.strptime(start_date, '%Y-%m-%d').isoformat() + 'Z'
        if end_date:
            published_before = datetime.strptime(end_date, '%Y-%m-%d').isoformat() + 'Z'

        max_subs_val = int(max_subs) if max_subs and max_subs.isdigit() else None
        api_key = current_app.config.get('YOUTUBE_API_KEY')

        if not api_key:
            flash('API Key do YouTube não configurada nas variáveis de ambiente.', 'warning')
        elif query:
            results = search_youtube_videos(
                api_key=api_key,
                query=query,
                max_results=limit,
                published_after=published_after,
                published_before=published_before,
                region_code=region,
                relevance_language=language,
                min_views=min_views,
                min_likes=min_likes,
                min_subs=min_subs,
                max_subs=max_subs_val
            )
            
            # Ordenar por Score decrescente
            results.sort(key=lambda x: x['score'], reverse=True)
            
            # Salvar histórico
            history = SearchHistory(query=query, user_id=current_user.id)
            db.session.add(history)
            db.session.commit()

    return render_template('garimpo.html', 
                           results=results, 
                           query=query,
                           language=language,
                           region=region,
                           start_date=start_date,
                           end_date=end_date,
                           period_btn=period_btn,
                           min_views=min_views,
                           min_likes=min_likes,
                           min_subs=min_subs,
                           max_subs=max_subs,
                           limit=limit)

@main.route('/promissores')
@login_required
def promissores():
    api_key = current_app.config.get('YOUTUBE_API_KEY')
    results = []
    if api_key:
        results = search_youtube_videos(
            api_key=api_key,
            query="estratégia youtube",
            max_results=50,
            max_subs=100000
        )
        results = [r for r in results if r['opportunity'] in ['Ótima Oportunidade', 'Boa Oportunidade']]
        results.sort(key=lambda x: x['score'], reverse=True)

    return render_template('promissores.html', results=results)

@main.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if request.method == 'POST':
        # Alterar senha do usuário atual
        new_password = request.form.get('new_password')
        if new_password:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
        else:
            flash('Configurações salvas!', 'success')
    return render_template('configuracoes.html')

@main.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
def admin_usuarios():
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = True if request.form.get('is_admin') else False
        
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe.', 'warning')
        else:
            new_user = User(username=username, is_admin=is_admin)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash(f'Usuário {username} criado com sucesso!', 'success')
            
    users = User.query.all()
    return render_template('admin_usuarios.html', users=users)

@main.route('/admin/usuarios/deletar/<int:id>')
@login_required
def deletar_usuario(id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(id)
    if user.username == 'admin':
        flash('Não é possível deletar o administrador principal.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Usuário removido.', 'success')
    
    return redirect(url_for('main.admin_usuarios'))
