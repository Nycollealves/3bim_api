# schemas.py
#
# Schemas do Pydantic: definem o formato dos dados que ENTRAM (Create) e
# SAEM (Response) pela API. São diferentes dos modelos do SQLAlchemy
# (models.py) — aqueles descrevem o banco, estes descrevem o "contrato"
# JSON da API.

from pydantic import BaseModel


# ---------- Produtos ----------

class ProdutoBase(BaseModel):
    """Campos comuns a criação e resposta de um produto."""
    nome: str
    preco: float
    quantidade: int


class ProdutoCreate(ProdutoBase):
    """Corpo esperado no POST/PUT de /produtos (sem 'id', que é gerado pelo banco)."""
    pass


class ProdutoResponse(ProdutoBase):
    """Formato devolvido pela API: campos base + 'id'."""
    id: int

    class Config:
        # CORREÇÃO: no arquivo original esta classe 'Config' estava
        # solta no nível do módulo (fora de ProdutoResponse), então o
        # Pydantic simplesmente a ignorava — ela precisa estar ANINHADA
        # dentro do schema para ter efeito.
        #
        # from_attributes = True permite que o Pydantic monte o
        # ProdutoResponse diretamente a partir de um objeto ProdutoDB
        # (ex.: return produto, onde produto é ProdutoDB), lendo os
        # atributos do objeto em vez de exigir um dicionário.
        from_attributes = True


# ---------- Funcionários ----------

class FuncionarioCreate(BaseModel):
    """Corpo esperado no POST/PUT de /funcionarios."""
    nome: str
    cargo: str
    salario: float
    departamento: str


class FuncionarioResponse(BaseModel):
    """Formato devolvido pela API para um funcionário."""
    id: int
    nome: str
    cargo: str
    salario: float
    departamento: str

    class Config:
        from_attributes = True