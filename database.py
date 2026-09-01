# database.py
#
# Responsável por configurar a conexão com o banco MySQL e fornecer
# o mecanismo de sessão que os endpoints do FastAPI usam para falar
# com o banco.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# String de conexão no formato: mysql+pymysql://usuario:senha@host/nome_do_banco
# 'root' sem senha e 'localhost' são valores típicos de ambiente de
# desenvolvimento local (XAMPP/WAMP, phpMyAdmin, etc.).
DATABASE_URL = 'mysql+pymysql://root:@localhost/loja'

# engine: objeto do SQLAlchemy que sabe COMO conversar com o MySQL
# (usa o driver PyMySQL). Ele não abre conexão sozinho — a conexão real
# só acontece quando algo pede uma sessão (SessionLocal()) ou quando
# Base.metadata.create_all(bind=engine) é chamado.
engine = create_engine(DATABASE_URL)

# SessionLocal: fábrica de sessões. Cada chamada a SessionLocal() cria
# uma sessão nova e independente, ligada ao engine acima.
# - autocommit=False: nada é salvo no banco até um db.commit() explícito.
# - autoflush=False: o SQLAlchemy não envia mudanças pendentes para o
#   banco antes de cada query, dando mais controle sobre quando isso ocorre.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: classe da qual todos os modelos (ProdutoDB, FuncionarioDB, ...)
# herdam. É ela que dá ao SQLAlchemy o "mapa" das tabelas para gerar
# o Base.metadata.create_all(...) mais adiante.
Base = declarative_base()


def get_db():
    """
    Dependência do FastAPI (usada com Depends(get_db) nos endpoints).

    Abre UMA sessão de banco por requisição, entrega essa sessão para o
    endpoint (yield db) e, quando a requisição termina — com sucesso ou
    com erro —, o bloco 'finally' garante que a sessão seja fechada.

    É justamente essa dependência que os testes substituem
    (app.dependency_overrides[get_db] = lambda: db_mock) para trocar o
    banco real por um MagicMock durante os testes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()