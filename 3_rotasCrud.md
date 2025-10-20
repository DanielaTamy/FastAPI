# Rotas CRUD

# Pydantic
responsabilidade de entender os schemas de contrato e validação para saber se os dados estão no formato do schema

# Rota post `(/users/)`
```bash
#adicionar a classe do pydantic no schemas.py
from pydantic import BaseModel, EmailStr

class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

#adicionar rota post para criar usuario em app.py
@app.post('/users/', response_model=UserSchema)
def create_user(user: UserSchema):
    return user

#adicionar o classPublic (não aparece a senha neste schema)
class UserPublic(BaseModel):
    username: str
    email: EmailStr

#alterar a rota post para a saída com userPublic e adicionar o status code 201 para sucesso
@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    return user

```

anotações:

1️⃣ response_model

- O que é: É o modelo de dados que FastAPI usa para validar e serializar a resposta.

- Tipo: Geralmente um Pydantic model.

- Função:

    - Garante que a resposta terá o formato esperado.

    - Remove campos extras que não estão no modelo.

    - Ajuda na documentação automática (OpenAPI/Swagger).

2️⃣response_class

- O que é: Define o tipo de resposta HTTP que a rota retorna.

- Tipo: Uma subclasse de fastapi.responses.Response (como HTMLResponse, JSONResponse, PlainTextResponse, etc.).

- Função:

    - Define o conteúdo bruto da resposta.

    - Útil quando você quer retornar HTML, arquivos, imagens ou texto simples.

# Criando um banco de dados
para fins de estudo
```python
#no app.py depois de app = FastAPI()
database = []

#adicionar um id no UserPublic no schema.py
class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr

#criar uma classe provisório - userDB:
#herda de userSchema - vai ter user, email, password e id
class UserDB(UserSchema):
    id: int

#faz todos os imports no app.py
from fast_zero.schemas import Message, UserSchema, UserPublic, UserDB

#rota post com bd falso

@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = UserDB(id=len(database) + 1, **user.model_dump())

    database.append(user_with_id)
    return user_with_id


# fazer test
def test_create_user():
    client = TestClient(app)
    response = client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secret',
        },
    )
    #voltou o status code correto?
    assert response.status_code == HTTPStatus.CREATED
    #validar userPublic
    assert response.json() == {
        'username': 'testuser',
        'email': 'test@example.com',
        'id': 1,
    }
```

# DRY - don't repeat yourself 
a linha client = TestClient(app) está repetida na primeira linha dos dois testes que fizemos
```python
# criar uma fixture que retorna nosso client
import pytest
from fastapi.testclient import TestClient
from fast_zero.app import app

@pytest.fixture
def client():
    return TestClient(app)

#corrige em todos os testes
def test_root_deve_retornar_ok_e_ola_mundo(client): #adiciona o cliente dps que cria a fixture
    # deleta depois que colocar a fixture
    # client = TestClient(app)  # Arrange

    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'message': 'Olá Mundo!'}  # Assert

#as fixtures ficam em arquivo chamado conftest.py dentro da pasta tests - adiciona o codigo lá
import pytest
from fastapi.testclient import TestClient
from fast_zero.app import app

@pytest.fixture
def client():
    return TestClient(app)
#quando excluir do test_app, tirar as dependencia n necessárias

```

# Rota get `(/users/)`
mostrar todos os recursos que já estão cadastrados na base
```python
# rota get (endpoint)
@app.get('/users/', response_model=UserList)
def read_users():
    return {'users': database}

#schema para N users - retorna sem a senha
class UserList(BaseModel):
    users: list[UserPublic]

#importar em app.py
from fast_zero.schemas import Message, UserDB, UserPublic, UserSchema, UserList

#testar no tests/test_app.py
def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'testuser',
                'email': 'test@example.com',
            }
        ]
    }
```


# Rota put `(/users/)`
atualizar registros 
```python
# rota get (endpoint)
@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema):
    if user_id > len(database) or user_id < 1:
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    user_with_id = UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = user_with_id 

    return user_with_id

# {user_id}: cria uma "variável" na url
# user_id: int: diz que esse valor vai ser validado como um inteiro

#importar
from fastapi import FastAPI, HTTPException

#schema para N users - retorna sem a senha
class UserList(BaseModel):
    users: list[UserPublic]

#importar em app.py
from fast_zero.schemas import Message, UserDB, UserPublic, UserSchema, UserList

#testar no tests/test_app.py
def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': 1,
    }
```


# Rota delete `(/users/)`
atualizar registros 
```python
# rota delete (endpoint)
@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    del database[user_id - 1]
    return {'message': 'User deleted'}


#testar no tests/test_app.py
def test_delete_user(client):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}

```


# exercícios
1. Escrever um teste para o erro de 404 (NOT FOUND) para o endpoint de PUT;
```python
def test_update_user_not_found(client):
    response = client.put('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND

```
2. Escrever um teste para o erro de 404 (NOT FOUND) para o endpoint de DELETE;

```python
def test_delete_user_not_found(client):
    response = client.delete('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND

```
3. Crie um endpoint GET para pegar um único recurso como users/{id} e faça seus testes para 200 e 404.
```python
@app.get('/users/{user_id}', response_model=UserPublic)
def read_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    return database[user_id - 1]

#tests
def test_read_users_not_found(client):
    response = client.get('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
#colocar o test antes do test do deleted 
```