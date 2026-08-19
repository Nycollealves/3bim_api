from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import FuncionarioDB
from schemas import FuncionarioCreate, FuncionarioResponse
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


# GET /funcionarios
@app.get('/funcionarios', response_model=list[FuncionarioResponse])
def listar_funcionarios(db: Session = Depends(get_db)):
    return db.query(FuncionarioDB).all()


# POST /funcionarios
@app.post('/funcionarios', response_model=FuncionarioResponse, status_code=201)
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
@app.get('/funcionarios/{funcionario_id}', response_model=FuncionarioResponse)
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
            detail='Funcionário não encontrado'
        )

    return funcionario


# DELETE /funcionarios/{id}
@app.delete('/funcionarios/{funcionario_id}', status_code=204)
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
            detail='Funcionário não encontrado'
        )

    db.delete(funcionario)
    db.commit()

    return