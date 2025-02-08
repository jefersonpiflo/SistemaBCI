from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.usuario import Usuario
from app import db
from werkzeug.security import generate_password_hash

bp = Blueprint('auth', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Email ou senha inválidos', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        if 'senha_atual' in request.form:
            # Alteração de senha
            if current_user.check_senha(request.form['senha_atual']):
                if request.form['nova_senha'] == request.form['confirma_senha']:
                    current_user.set_senha(request.form['nova_senha'])
                    db.session.commit()
                    flash('Senha alterada com sucesso!', 'success')
                else:
                    flash('As senhas não conferem', 'danger')
            else:
                flash('Senha atual incorreta', 'danger')
        else:
            # Atualização de dados do perfil
            current_user.nome = request.form['nome']
            current_user.email = request.form['email']
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            
    return render_template('auth/perfil.html') 