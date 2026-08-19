from fastapi import HTTPException


# GET /funcionarios/{id} -> consulta um funcionário pelo id no banco
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


# DELETE /funcionarios/{id} -> remove um funcionário do banco
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


# PUT /funcionarios/{id} -> atualiza um funcionário existente no banco
@app.put('/funcionarios/{funcionario_id}', response_model=FuncionarioResponse)
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
            detail='Funcionário não encontrado'
        )

    funcionario.nome = dados.nome
    funcionario.cargo = dados.cargo
    funcionario.salario = dados.salario
    funcionario.departamento = dados.departamento

    db.commit()
    db.refresh(funcionario)

    return funcionario