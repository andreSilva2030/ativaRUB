from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()  # Não precisa passar o nome do arquivo, ele busca .env por padrão

from config import Config
from database import db, migrate
from controllers import divisao_bandeira_controller
from controllers import lojas_controller  # Adicione esta linha

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    app.register_blueprint(divisao_bandeira_controller.bp)
    app.register_blueprint(lojas_controller.bp)  # Adicione esta linha
    
    @app.route('/')
    def index():
        return {'message': 'Ativa RUB - Gestao de rollout', 'status': 'online'}
    
    return app

app = create_app()