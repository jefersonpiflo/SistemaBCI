from app import create_app, db
from app.models.usuario import Usuario
from app.models.imovel import Imovel
from app.models.vistoria import Vistoria
from app.models.aliquota import Aliquota
from app.models.auditoria import LogAuditoria
from app.models.configuracao_boleto import ConfiguracaoBoleto

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Usuario': Usuario,
        'Imovel': Imovel,
        'Vistoria': Vistoria,
        'Aliquota': Aliquota,
        'LogAuditoria': LogAuditoria,
        'ConfiguracaoBoleto': ConfiguracaoBoleto
    }

if __name__ == '__main__':
    with app.app_context():
        # Criar o banco de dados se não existir
        db.create_all()
        
        # Criar usuário admin se não existir
        if not Usuario.query.filter_by(email='admin@bci.com').first():
            admin = Usuario(
                nome='Administrador',
                email='admin@bci.com',
                tipo='admin'
            )
            admin.set_senha('admin123')
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True) 
