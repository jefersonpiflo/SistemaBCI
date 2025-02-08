from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.vistoria import Vistoria, FotoVistoria
from app.models.imovel import Imovel
from app import db
from datetime import datetime
import os

bp = Blueprint('vistoria', __name__)

@bp.route('/vistorias')
@login_required
def index():
    vistorias = Vistoria.query.order_by(Vistoria.data_agendada.desc()).all()
    return render_template('vistoria/index.html', vistorias=vistorias)

@bp.route('/vistoria/agendar/<int:imovel_id>', methods=['GET', 'POST'])
@login_required
def agendar(imovel_id):
    imovel = Imovel.query.get_or_404(imovel_id)
    
    if request.method == 'POST':
        data_agendada = datetime.strptime(request.form['data_agendada'], '%Y-%m-%dT%H:%M')
        vistoria = Vistoria(
            imovel_id=imovel.id,
            fiscal_id=current_user.id,
            data_agendada=data_agendada,
            observacoes=request.form.get('observacoes')
        )
        db.session.add(vistoria)
        db.session.commit()
        
        flash('Vistoria agendada com sucesso!', 'success')
        return redirect(url_for('vistoria.index'))
    
    return render_template('vistoria/agendar.html', imovel=imovel)

@bp.route('/vistoria/<int:id>/realizar', methods=['GET', 'POST'])
@login_required
def realizar(id):
    vistoria = Vistoria.query.get_or_404(id)
    
    if request.method == 'POST':
        vistoria.data_realizada = datetime.now()
        vistoria.status = 'realizada'
        vistoria.situacao_construcao = request.form['situacao_construcao']
        vistoria.conformidade_projeto = 'conformidade' in request.form
        vistoria.irregularidades = request.form.get('irregularidades')
        
        # Processar fotos
        fotos = request.files.getlist('fotos')
        for foto in fotos:
            if foto.filename:
                filename = secure_filename(foto.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                foto.save(filepath)
                
                foto_vistoria = FotoVistoria(
                    vistoria_id=vistoria.id,
                    arquivo=filename,
                    descricao=request.form.get('descricao_foto')
                )
                db.session.add(foto_vistoria)
        
        db.session.commit()
        flash('Vistoria realizada com sucesso!', 'success')
        return redirect(url_for('vistoria.visualizar', id=vistoria.id))
    
    return render_template('vistoria/realizar.html', vistoria=vistoria)

@bp.route('/vistoria/<int:id>')
@login_required
def visualizar(id):
    vistoria = Vistoria.query.get_or_404(id)
    return render_template('vistoria/visualizar.html', vistoria=vistoria) 