# schemas.py
from pydantic import BaseModel

class ProdutoBase(BaseModel):
    nome: str
    preco: float
    quantidade: int
class ProdutoCreate(ProdutoBase):
    pass
class ProdutoResponse(ProdutoBase):
    id: int
class Config:
    from_attributes = True

class FuncionarioCreate(BaseModel):
    nome: str
    cargo: str
    salario: float
    departamento: str


class FuncionarioResponse(BaseModel):
    id: int
    nome: str
    cargo: str
    salario: float
    departamento: str

    class Config:
        from_attributes = True