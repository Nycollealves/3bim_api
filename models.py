# models.py
#
# Modelos do SQLAlchemy: cada classe aqui representa uma TABELA do banco
# 'loja'. São eles que o SQLAlchemy usa tanto para gerar o SQL de
# CREATE TABLE (via Base.metadata.create_all) quanto para converter
# linhas do banco em objetos Python e vice-versa.

from sqlalchemy import Column, Integer, String, Float
from database import Base


class ProdutoDB(Base):
    """Mapeia a tabela 'produtos' (ver loja.sql)."""
    __tablename__ = 'produtos'

    # primary_key=True -> chave primária (AUTO_INCREMENT no MySQL)
    # index=True -> cria índice na coluna, acelera buscas por id
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    preco = Column(Float, nullable=False)
    quantidade = Column(Integer, nullable=False)


class FuncionarioDB(Base):
    """Mapeia a tabela 'funcionarios'."""
    __tablename__ = 'funcionarios'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cargo = Column(String(100), nullable=False)
    salario = Column(Float, nullable=False)
    departamento = Column(String(100), nullable=False)