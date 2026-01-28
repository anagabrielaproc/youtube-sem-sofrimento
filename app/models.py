from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    youtube_api_key = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    youtube_id = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    thumbnail = db.Column(db.String(500))
    subscribers = db.Column(db.Integer)
    video_count = db.Column(db.Integer)
    view_count = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime)
    is_promising = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Novos campos para a planilha estratégica
    score = db.Column(db.Float, default=0.0)
    opportunity_label = db.Column(db.String(50))
