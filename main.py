# main.py
#
# API FastAPI com CRUD completo de Produtos e Funcionários.
#
# CORREÇÃO aplicada (ver Nota_Tecnica_Falha_Startup_MySQL_SW-II.md):
# Base.metadata.create_all(bind=engine) foi tirado do nível do módulo e
# movido para dentro de um evento de "startup". No código original, essa
# linha rodava assim que o Python importava main.py — inclusive quando
# quem importava era o test_produtos.py — e isso forçava uma conexão
# real com o MySQL mesmo em testes que usam MagicMock. Com a correção,
# a criação das tabelas só acontece quando a aplicação é de fato
# inicializada (uvicorn, ou TestClient usado como context manager),
# nunca durante a simples importação do módulo.

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


app = FastAPI()


@app.on_event("startup")
def criar_tabelas():
    """
    Executa Base.metadata.create_all APENAS quando a aplicação
    realmente sobe (startup do FastAPI/uvicorn), e não no momento em
    que o arquivo é importado. É isso que permite rodar os testes com
    o MySQL desligado, já que test_produtos.py cria o TestClient sem
    usar 'with', então o evento de startup nunca é disparado.
    """
    Base.metadata.create_all(bind=engine)


# CORS liberado para qualquer origem/método/cabeçalho — apropriado para
# desenvolvimento; em produção normalmente se restringe allow_origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PRODUTOS
# ============================================================

@app.get("/produtos", response_model=list[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    """GET /produtos — retorna todos os produtos cadastrados."""
    return db.query(ProdutoDB).all()


@app.post("/produtos", response_model=ProdutoResponse, status_code=201)
def criar_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db)
):
    """
    POST /produtos — cria um novo produto.
    produto.dict() converte o schema Pydantic (ProdutoCreate) em um
    dicionário, que é "explodido" com ** para preencher os argumentos
    do construtor de ProdutoDB (nome=..., preco=..., quantidade=...).
    """
    novo_produto = ProdutoDB(**produto.dict())

    db.add(novo_produto)      # marca o objeto para ser inserido
    db.commit()                # efetiva a inserção no banco
    db.refresh(novo_produto)   # recarrega o objeto (traz o 'id' gerado pelo MySQL)

    return novo_produto


@app.get("/produtos/{produto_id}", response_model=ProdutoResponse)
def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """GET /produtos/{id} — busca um produto específico; 404 se não existir."""
    produto = db.query(ProdutoDB).filter(
        ProdutoDB.id == produto_id
    ).first()

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    return produto


@app.put("/produtos/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    dados: ProdutoCreate,
    db: Session = Depends(get_db)
):
    """PUT /produtos/{id} — sobrescreve todos os campos do produto."""
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


@app.delete("/produtos/{produto_id}", status_code=204)
def remover_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """DELETE /produtos/{id} — remove o produto; 204 não retorna corpo."""
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


# ============================================================
# FUNCIONÁRIOS
# ============================================================

@app.get("/funcionarios", response_model=list[FuncionarioResponse])
def listar_funcionarios(db: Session = Depends(get_db)):
    """GET /funcionarios — retorna todos os funcionários cadastrados."""
    return db.query(FuncionarioDB).all()


@app.post("/funcionarios", response_model=FuncionarioResponse, status_code=201)
def criar_funcionario(
    funcionario: FuncionarioCreate,
    db: Session = Depends(get_db)
):
    """POST /funcionarios — cria um novo funcionário (mesmo padrão de criar_produto)."""
    novo_funcionario = FuncionarioDB(**funcionario.dict())

    db.add(novo_funcionario)
    db.commit()
    db.refresh(novo_funcionario)

    return novo_funcionario


@app.get(
    "/funcionarios/{funcionario_id}",
    response_model=FuncionarioResponse
)
def obter_funcionario(
    funcionario_id: int,
    db: Session = Depends(get_db)
):
    """GET /funcionarios/{id} — busca um funcionário específico; 404 se não existir."""
    funcionario = db.query(FuncionarioDB).filter(
        FuncionarioDB.id == funcionario_id
    ).first()

    if funcionario is None:
        raise HTTPException(
            status_code=404,
            detail="Funcionário não encontrado"
        )

    return funcionario


@app.put(
    "/funcionarios/{funcionario_id}",
    response_model=FuncionarioResponse
)
def atualizar_funcionario(
    funcionario_id: int,
    dados: FuncionarioCreate,
    db: Session = Depends(get_db)
):
    """PUT /funcionarios/{id} — sobrescreve todos os campos do funcionário."""
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


@app.delete("/funcionarios/{funcionario_id}", status_code=204)
def remover_funcionario(
    funcionario_id: int,
    db: Session = Depends(get_db)
):
    """DELETE /funcionarios/{id} — remove o funcionário; 204 não retorna corpo."""
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