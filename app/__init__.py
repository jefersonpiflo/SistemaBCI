from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bci.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from app.models.usuario import Usuario
    @login_manager.user_loader
    def load_user(id):
        return Usuario.query.get(int(id))

    # Registrar blueprints
    from app.routes import auth, dashboard, imovel, aliquotas, iptu, configuracoes
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(imovel.bp)
    app.register_blueprint(aliquotas.bp)
    app.register_blueprint(iptu.bp, url_prefix='/iptu')
    app.register_blueprint(configuracoes.bp)

    # Adicionar context processor para datetime
    @app.context_processor
    def utility_processor():
        return {'datetime': datetime}

    # Rota padrão
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))

    return app 
