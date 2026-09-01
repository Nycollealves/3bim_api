# main.py
# COMENTÁRIO: Cabeçalho do arquivo original indicando o nome do módulo.
#
# COMENTÁRIO: Linha em branco para separação visual.
#
# API FastAPI com CRUD completo de Produtos e Funcionários.
# COMENTÁRIO: Descrição breve do propósito do módulo.
#
# CORREÇÃO aplicada (ver Nota_Tecnica_Falha_Startup_MySQL_SW-II.md):
# COMENTÁRIO: Comentário explicando uma correção técnica aplicada neste arquivo.
# Base.metadata.create_all(bind=engine) foi tirado do nível do módulo e
# COMENTÁRIO: Detalhe sobre movimentação da criação de tabelas para startup.
# movido para dentro de um evento de "startup". No código original, essa
# COMENTÁRIO: Continuação da explicação da correção.
# linha rodava assim que o Python importava main.py — inclusive quando
# COMENTÁRIO: Explica o problema de execução durante importação.
# quem importava era o test_produtos.py — e isso forçava uma conexão
# COMENTÁRIO: Continua a explicação sobre efeitos em testes.
# real com o MySQL mesmo em testes que usam MagicMock. Com a correção,
# COMENTÁRIO: Finaliza a explicação sobre a correção aplicada.
# a criação das tabelas só acontece quando a aplicação é de fato
# COMENTÁRIO: Observação sobre quando a criação de tabelas ocorre agora.
# inicializada (uvicorn, ou TestClient usado como context manager),
# COMENTÁRIO: Exemplos de quando o evento de startup é disparado.
# nunca durante a simples importação do módulo.
# COMENTÁRIO: Conclusão do bloco de comentário técnico.

from fastapi import FastAPI, Depends, HTTPException
# COMENTÁRIO: Importa FastAPI (app), Depends para injeção de dependências e HTTPException para erros HTTP.
from sqlalchemy.orm import Session
# COMENTÁRIO: Importa a classe Session do SQLAlchemy para tipagem das dependências do DB.

from database import Base, engine, get_db
# COMENTÁRIO: Importa Base (metadados/ORM), engine (conexão) e get_db (dependência para sessão DB).

from models import ProdutoDB, FuncionarioDB
# COMENTÁRIO: Importa os modelos ORM para Produto e Funcionário definidos em models.py.

from schemas import (
    ProdutoCreate,
    ProdutoResponse,
    FuncionarioCreate,
    FuncionarioResponse
)
# COMENTÁRIO: Importa esquemas Pydantic para validação/serialização de entrada e saída.

from fastapi.middleware.cors import CORSMiddleware
# COMENTÁRIO: Importa middleware CORS para permitir requisições cross-origin.


app = FastAPI()
# COMENTÁRIO: Instancia a aplicação FastAPI.


@app.on_event("startup")
def criar_tabelas():
    # """
    # Executa Base.metadata.create_all APENAS quando a aplicação
    # realmente sobe (startup do FastAPI/uvicorn), e não no momento em
    # que o arquivo é importado. É isso que permite rodar os testes com
    # o MySQL desligado, já que test_produtos.py cria o TestClient sem
    # usar 'with', então o evento de startup nunca é disparado."""
    # COMENTÁRIO: Define um handler para o evento de startup que cria as tabelas.
    Base.metadata.create_all(bind=engine)
# COMENTÁRIO: Chama SQLAlchemy para criar todas as tabelas com base nos modelos e no engine.


# CORS liberado para qualquer origem/método/cabeçalho — apropriado para
# COMENTÁRIO: Comentário explicativo sobre a configuração CORS a seguir.
# desenvolvimento; em produção normalmente se restringe allow_origins.
# COMENTÁRIO: Observação sobre diferenciação entre dev e produção.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# COMENTÁRIO: Adiciona o middleware CORS permitindo todas as origens, métodos e cabeçalhos.


# ============================================================
# PRODUTOS
# ============================================================
# COMENTÁRIO: Separador visual indicando início da seção de endpoints de Produtos.

@app.get("/produtos", response_model=list[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    """GET /produtos — retorna todos os produtos cadastrados."""
    # COMENTÁRIO: Define rota GET para listar todos os produtos, usando dependência para sessão DB.
    return db.query(ProdutoDB).all()
# COMENTÁRIO: Executa query para retornar todos os objetos ProdutoDB.


@app.post("/produtos", response_model=ProdutoResponse, status_code=201)
def criar_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db)
):
    # """
    # POST /produtos — cria um novo produto.
    # produto.dict() converte o schema Pydantic (ProdutoCreate) em um
    # dicionário, que é "explodido" com ** para preencher os argumentos
    # do construtor de ProdutoDB (nome=..., preco=..., quantidade=...).
    # """
    # COMENTÁRIO: Define rota POST para criar produto; espera um ProdutoCreate e uma sessão DB.
    novo_produto = ProdutoDB(**produto.dict())
# COMENTÁRIO: Instancia ProdutoDB passando os campos do schema como kwargs.

    db.add(novo_produto)      # marca o objeto para ser inserido
    # COMENTÁRIO: Adiciona o novo objeto à sessão do SQLAlchemy.
    db.commit()                # efetiva a inserção no banco
    # COMENTÁRIO: Faz commit da transação, persistindo o novo registro.
    db.refresh(novo_produto)   # recarrega o objeto (traz o 'id' gerado pelo MySQL)
    # COMENTÁRIO: Atualiza a instância com valores gerados pelo DB (ex.: id autoincrement).

    return novo_produto
# COMENTÁRIO: Retorna o objeto recém-criado, que será serializado pelo Pydantic.


@app.get("/produtos/{produto_id}", response_model=ProdutoResponse)
def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """GET /produtos/{id} — busca um produto específico; 404 se não existir."""
    # COMENTÁRIO: Define rota GET para obter produto por ID.
    produto = db.query(ProdutoDB).filter(
        ProdutoDB.id == produto_id
    ).first()
# COMENTÁRIO: Faz query filtrando por id e retorna o primeiro resultado (ou None).

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )
    # COMENTÁRIO: Se não encontrar, levanta HTTPException 404 com mensagem.

    return produto
# COMENTÁRIO: Retorna o produto encontrado.


@app.put("/produtos/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    dados: ProdutoCreate,
    db: Session = Depends(get_db)
):
    # """PUT /produtos/{id} — sobrescreve todos os campos do produto."""
    # COMENTÁRIO: Define rota PUT para atualizar um produto por ID com dados do schema.
    produto = db.query(ProdutoDB).filter(
        ProdutoDB.id == produto_id
    ).first()
# COMENTÁRIO: Busca o produto a ser atualizado.

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )
    # COMENTÁRIO: Se não existir, retorna 404.

    produto.nome = dados.nome
    produto.preco = dados.preco
    produto.quantidade = dados.quantidade
    # COMENTÁRIO: Atualiza os campos do objeto com os valores recebidos.

    db.commit()
    db.refresh(produto)
    # COMENTÁRIO: Persiste as alterações e atualiza a instância com valores do DB.

    return produto
# COMENTÁRIO: Retorna o produto atualizado.


@app.delete("/produtos/{produto_id}", status_code=204)
def remover_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """DELETE /produtos/{id} — remove o produto; 204 não retorna corpo."""
    # COMENTÁRIO: Define rota DELETE para remover um produto por ID.
    produto = db.query(ProdutoDB).filter(
        ProdutoDB.id == produto_id
    ).first()
# COMENTÁRIO: Busca o produto para exclusão.

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )
    # COMENTÁRIO: Se não encontrado, retorna 404.

    db.delete(produto)
    db.commit()
    # COMENTÁRIO: Remove o objeto e faz commit da transação.

    return
# COMENTÁRIO: Retorna sem corpo (204 No Content).


# ============================================================
# FUNCIONÁRIOS
# ============================================================
# COMENTÁRIO: Separador visual indicando início da seção de endpoints de Funcionários.

@app.get("/funcionarios", response_model=list[FuncionarioResponse])
def listar_funcionarios(db: Session = Depends(get_db)):
    """GET /funcionarios — retorna todos os funcionários cadastrados."""
    # COMENTÁRIO: Define rota GET para listar todos os funcionários.
    return db.query(FuncionarioDB).all()
# COMENTÁRIO: Retorna todos os registros FuncionarioDB.


@app.post("/funcionarios", response_model=FuncionarioResponse, status_code=201)
def criar_funcionario(
    funcionario: FuncionarioCreate,
    db: Session = Depends(get_db)
):
    """POST /funcionarios — cria um novo funcionário (mesmo padrão de criar_produto)."""
    # COMENTÁRIO: Define rota POST para criar novo funcionário.
    novo_funcionario = FuncionarioDB(**funcionario.dict())
# COMENTÁRIO: Instancia FuncionarioDB com campos do schema recebido.

    db.add(novo_funcionario)
    db.commit()
    db.refresh(novo_funcionario)
    # COMENTÁRIO: Adiciona, persiste e atualiza a instância com valores do DB.

    return novo_funcionario
# COMENTÁRIO: Retorna o funcionário criado.


@app.get(
    "/funcionarios/{funcionario_id}",
    response_model=FuncionarioResponse
)
def obter_funcionario(
    funcionario_id: int,
    db: Session = Depends(get_db)
):
    """GET /funcionarios/{id} — busca um funcionário específico; 404 se não existir."""
    # COMENTÁRIO: Define rota GET para obter funcionário por ID.
    funcionario = db.query(FuncionarioDB).filter(
        FuncionarioDB.id == funcionario_id
    ).first()
# COMENTÁRIO: Busca o funcionário correspondente ao id.

    if funcionario is None:
        raise HTTPException(
            status_code=404,
            detail="Funcionário não encontrado"
        )
    # COMENTÁRIO: Levanta 404 quando não encontra o registro.

    return funcionario
# COMENTÁRIO: Retorna o funcionário encontrado.


@app.put(
    "/funcionarios/{funcionario_id}",
    response_model=FuncionarioResponse
)
def atualizar_funcionario(
    funcionario_id: int,
    dados: FuncionarioCreate,
    db: Session = Depends(get_db)
):
    # """PUT /funcionarios/{id} — sobrescreve todos os campos do funcionário."""
    # COMENTÁRIO: Define rota PUT para atualizar funcionário por ID.
    funcionario = db.query(FuncionarioDB).filter(
        FuncionarioDB.id == funcionario_id
    ).first()
# COMENTÁRIO: Busca o funcionário a ser atualizado.

    if funcionario is None:
        raise HTTPException(
            status_code=404,
            detail="Funcionário não encontrado"
        )
    # COMENTÁRIO: Retorna 404 se não existir.

    funcionario.nome = dados.nome
    funcionario.cargo = dados.cargo
    funcionario.salario = dados.salario
    funcionario.departamento = dados.departamento
    # COMENTÁRIO: Atualiza os campos do modelo com os dados recebidos.

    db.commit()
    db.refresh(funcionario)
    # COMENTÁRIO: Persiste e atualiza a instância.

    return funcionario
# COMENTÁRIO: Retorna o funcionário atualizado.


@app.delete("/funcionarios/{funcionario_id}", status_code=204)
def remover_funcionario(
    funcionario_id: int,
    db: Session = Depends(get_db)
):
    # """DELETE /funcionarios/{id} — remove o funcionário; 204 não retorna corpo."""
    # COMENTÁRIO: Define rota DELETE para remover funcionário por ID.
    funcionario = db.query(FuncionarioDB).filter(
        FuncionarioDB.id == funcionario_id
    ).first()
# COMENTÁRIO: Busca o funcionário a ser deletado.

    if funcionario is None:
        raise HTTPException(
            status_code=404,
            detail="Funcionário não encontrado"
        )
    # COMENTÁRIO: Se não existir, levanta HTTPException 404.

    db.delete(funcionario)
    db.commit()
    # COMENTÁRIO: Deleta o objeto e confirma a transação.

    return
# COMENTÁRIO: Retorna sem conteúdo (204 No Content).
