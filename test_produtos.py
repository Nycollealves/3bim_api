# test_produtos.py
#
# Testes unitários dos endpoints de Produtos usando MagicMock no lugar
# de uma sessão real do banco. A ideia central é: em vez de conectar de
# verdade no MySQL, "fingimos" que a sessão do SQLAlchemy (get_db) é um
# objeto MagicMock, e configuramos o que cada método dela deve devolver.
# Isso torna os testes rápidos e independentes do banco estar no ar.

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app, get_db
from models import ProdutoDB

# TestClient(app) simula requisições HTTP contra a aplicação FastAPI sem
# precisar subir um servidor de verdade (uvicorn). Importante: NÃO é
# usado como "with TestClient(app) as client", então o evento de
# "startup" do FastAPI (onde está o Base.metadata.create_all) nunca é
# disparado — por isso os testes funcionam mesmo com o MySQL desligado.
client = TestClient(app)


def test_listar_produtos_com_mock():
    """
    Testa GET /produtos.

    1. Cria um MagicMock que vai substituir a sessão do banco (Session).
    2. Configura a "cadeia" db.query(...).all() para devolver uma lista
       fixa com um único ProdutoDB, simulando o que o banco retornaria.
    3. Sobrescreve a dependência get_db do FastAPI: sempre que um
       endpoint pedir Depends(get_db), ele vai receber db_mock em vez
       de uma sessão real.
    4. Chama o endpoint via TestClient e verifica:
       - que a resposta HTTP foi 200 (sucesso)
       - que o JSON devolvido contém o produto simulado ("Teclado")
    5. Limpa a sobrescrita no final, para não vazar para outros testes.
    """
    db_mock = MagicMock()
    db_mock.query.return_value.all.return_value = [
        ProdutoDB(id=1, nome='Teclado', preco=89.90, quantidade=15)
    ]
    app.dependency_overrides[get_db] = lambda: db_mock

    resposta = client.get('/produtos')

    assert resposta.status_code == 200
    assert resposta.json()[0]['nome'] == 'Teclado'

    app.dependency_overrides.clear()


def test_criar_produto_com_mock():
    """
    Testa POST /produtos.

    O ponto mais importante deste teste é o `side_effect` em
    db_mock.refresh: no banco real, é o MySQL que atribui o `id`
    (AUTO_INCREMENT) ao produto no momento do commit/refresh. Como aqui
    a sessão inteira é um mock, nada disso acontece de verdade — então
    simulamos manualmente esse comportamento fazendo `simular_refresh`
    atribuir produto.id = 1 sempre que db.refresh(produto) for chamado
    dentro do endpoint `criar_produto`.

    Sem esse side_effect, o objeto criado ficaria com id=None, e o
    FastAPI falharia ao validar a resposta contra ProdutoResponse
    (que exige id: int), lançando um ResponseValidationError.

    Depois de chamar o endpoint, o teste confirma:
    - que a resposta HTTP foi 201 (criado)
    - que db.add() foi chamado exatamente uma vez (o produto foi
      "adicionado" à sessão)
    - que db.commit() foi chamado exatamente uma vez (a criação foi
      "efetivada")
    """
    db_mock = MagicMock()

    def simular_refresh(produto):
        produto.id = 1  # simula o banco atribuindo um id ao registro

    db_mock.refresh.side_effect = simular_refresh
    app.dependency_overrides[get_db] = lambda: db_mock

    novo_produto = {'nome': 'Monitor', 'preco': 799.90, 'quantidade': 5}
    resposta = client.post('/produtos', json=novo_produto)

    assert resposta.status_code == 201
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()

    app.dependency_overrides.clear()
