from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User
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
    min_subs = 0
    max_subs = ""
    min_views = 0
    max_views = ""
    period_btn = ""

    if request.method == 'POST':
        query = request.form.get('query')
        min_subs = int(request.form.get('min_subs') or 0)
        max_subs = request.form.get('max_subs')
        min_views = int(request.form.get('min_views') or 0)
        max_views = request.form.get('max_views')
        period_btn = request.form.get('period_btn')

        published_after = None
        now = datetime.utcnow()

        if period_btn == 'today':
            published_after = now.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
        elif period_btn == 'week':
            published_after = (now - timedelta(days=7)).isoformat() + 'Z'
        elif period_btn == 'month':
            published_after = (now - timedelta(days=30)).isoformat() + 'Z'
        elif period_btn == 'year':
            published_after = (now - timedelta(days=365)).isoformat() + 'Z'

        max_subs_val = int(max_subs) if max_subs and max_subs.isdigit() else None
        max_views_val = int(max_views) if max_views and max_views.isdigit() else None
        
        # Tenta pegar a API Key das configurações do Render primeiro, depois do usuário
        api_key = current_app.config.get('YOUTUBE_API_KEY') or current_user.youtube_api_key

        if not api_key:
            flash('API Key do YouTube não configurada.', 'warning')
        elif query:
            results = search_youtube_videos(
                api_key=api_key,
                query=query,
                published_after=published_after,
                min_views=min_views,
                max_views=max_views_val,
                min_subs=min_subs,
                max_subs=max_subs_val
            )

    return render_template('garimpo.html', 
                           results=results, 
                           query=query,
                           min_subs=min_subs,
                           max_subs=max_subs,
                           min_views=min_views,
                           max_views=max_views,
                           period_btn=period_btn)

@main.route('/promissores')
@login_required
def promissores():
    api_key = current_app.config.get('YOUTUBE_API_KEY') or current_user.youtube_api_key
    results = []
    if api_key:
        # Busca genérica para canais promissores
        results = search_youtube_videos(
            api_key=api_key,
            query="estratégia youtube",
            max_results=50,
            max_subs=50000
        )
        # Filtra apenas as melhores oportunidades
        results = [r for r in results if r.get('opportunity') in ['Ótima Oportunidade', 'Boa Oportunidade']]

    return render_template('promissores.html', results=results)

@main.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        new_password = request.form.get('new_password')
        
        if api_key:
            current_user.youtube_api_key = api_key
        
        if new_password:
            current_user.set_password(new_password)
            
        db.session.commit()
        flash('Configurações atualizadas com sucesso!', 'success')
        
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
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(id)
    if user.username == 'admin':
        flash('Não é possível deletar o administrador principal.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Usuário removido.', 'success')
    
    return redirect(url_for('main.admin_usuarios'))
