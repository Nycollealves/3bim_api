from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import Base, engine, get_db

from models import ProdutoDB, FuncionarioDB

from schemas import (
    ProdutoCreate,
    ProdutoResponse,
    FuncionarioCreate,
    FuncionarioResponse
)

from fastapi.middleware.cors import CORSMiddleware


# Cria as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)





# GET /produtos
# Lista todos os produtos
@app.get("/produtos", response_model=list[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(ProdutoDB).all()


# POST /produtos
# Cria um novo produto
@app.post("/produtos", response_model=ProdutoResponse, status_code=201)
def criar_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db)
):
    novo_produto = ProdutoDB(**produto.dict())

    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)

    return novo_produto


# GET /produtos/{id}
# Busca um produto pelo ID
@app.get("/produtos/{produto_id}", response_model=ProdutoResponse)
def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    produto = db.query(ProdutoDB).filter(
        ProdutoDB.id == produto_id
    ).first()

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    return produto


# PUT /produtos/{id}
# Atualiza um produto
@app.put("/produtos/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    dados: ProdutoCreate,
    db: Session = Depends(get_db)
):
    produto = db.query(ProdutoDB).filter(
        ProdutoDB.id == produto_id
    ).first()

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    produto.nome = dados.nome
    produto.preco = dados.preco
    produto.quantidade = dados.quantidade

    db.commit()
    db.refresh(produto)

    return produto


# DELETE /produtos/{id}
# Remove um produto
@app.delete("/produtos/{produto_id}", status_code=204)
def remover_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    produto = db.query(ProdutoDB).filter(
        ProdutoDB.id == produto_id
    ).first()

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    db.delete(produto)
    db.commit()

    return



# GET /funcionarios
# Lista todos os funcionários
@app.get("/funcionarios", response_model=list[FuncionarioResponse])
def listar_funcionarios(db: Session = Depends(get_db)):
    return db.query(FuncionarioDB).all()


# POST /funcionarios
# Cria um novo funcionário
@app.post("/funcionarios", response_model=FuncionarioResponse, status_code=201)
def criar_funcionario(
    funcionario: FuncionarioCreate,
    db: Session = Depends(get_db)
):
    novo_funcionario = FuncionarioDB(**funcionario.dict())

    db.add(novo_funcionario)
    db.commit()
    db.refresh(novo_funcionario)

    return novo_funcionario


# GET /funcionarios/{id}
# Busca um funcionário pelo ID
@app.get(
    "/funcionarios/{funcionario_id}",
    response_model=FuncionarioResponse
)
def obter_funcionario(
    funcionario_id: int,
    db: Session = Depends(get_db)
):
    funcionario = db.query(FuncionarioDB).filter(
        FuncionarioDB.id == funcionario_id
    ).first()

    if funcionario is None:
        raise HTTPException(
            status_code=404,
            detail="Funcionário não encontrado"
        )

    return funcionario


# PUT /funcionarios/{id}
# Atualiza um funcionário
@app.put(
    "/funcionarios/{funcionario_id}",
    response_model=FuncionarioResponse
)
def atualizar_funcionario(
    funcionario_id: int,
    dados: FuncionarioCreate,
    db: Session = Depends(get_db)
):
    funcionario = db.query(FuncionarioDB).filter(
        FuncionarioDB.id == funcionario_id
    ).first()

    if funcionario is None:
        raise HTTPException(
            status_code=404,
            detail="Funcionário não encontrado"
        )

    funcionario.nome = dados.nome
    funcionario.cargo = dados.cargo
    funcionario.salario = dados.salario
    funcionario.departamento = dados.departamento

    db.commit()
    db.refresh(funcionario)

    return funcionario


# DELETE /funcionarios/{id}
# Remove um funcionário
@app.delete("/funcionarios/{funcionario_id}", status_code=204)
def remover_funcionario(
    funcionario_id: int,
    db: Session = Depends(get_db)
):
    funcionario = db.query(FuncionarioDB).filter(
        FuncionarioDB.id == funcionario_id
    ).first()

    if funcionario is None:
        raise HTTPException(
            status_code=404,
            detail="Funcionário não encontrado"
        )

    db.delete(funcionario)
    db.commit()

    return