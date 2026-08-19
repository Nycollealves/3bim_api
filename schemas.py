from pydantic import BaseModel


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