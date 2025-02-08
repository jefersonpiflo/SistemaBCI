from flask import Blueprint, send_file
from flask_login import login_required
from app.models.imovel import Imovel
from app.utils.pdf_generator import DocumentoGenerator
from datetime import datetime

bp = Blueprint('documentos', __name__)

@bp.route('/documentos/bci/<int:imovel_id>')
@login_required
def gerar_bci(imovel_id):
    imovel = Imovel.query.get_or_404(imovel_id)
    generator = DocumentoGenerator()
    pdf_buffer = generator.gerar_bci(imovel)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'BCI_{imovel.inscricao_imobiliaria}_{datetime.now().strftime("%Y%m%d")}.pdf'
    ) 