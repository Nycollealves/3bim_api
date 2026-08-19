from sqlalchemy import Column, Integer, String, Float
from database import Base


class FuncionarioDB(Base):
    __tablename__ = 'funcionarios'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cargo = Column(String(100), nullable=False)
    salario = Column(Float, nullable=False)
    departamento = Column(String(100), nullable=False)