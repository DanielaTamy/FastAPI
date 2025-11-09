# Autenticação e Autorização com tokens JWT 

importar 
```
poetry add "pwdlib[argon2]"
```

criar um arquivo security.py na pasta de fast_zero
```python
from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


```

alterar o endpoint de cadastro para armazenar o hash da senha
```python

from fast_zero.security import get_password_hash

# app.py
@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user
```

alterar o endpoint de update
```python

@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
):
    # ...
        db_user.username = user.username
        db_user.password = get_password_hash(user.password)
        db_user.email = user.email
        session.commit()
        session.refresh(db_user)

        return db_user
```

## Autenticação
criando endpoint /token

importar 
```
poetry add python-multipart
```
```python

# app.py
from fastapi.security import OAuth2PasswordRequestForm, verify_password

@app.post('/token')
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password'
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password'
        )
```

### Token JWT
JWT (Json Web Token) é uma forma de assinatura do servidor.

O payload e as claims
{
    "sub": "teste@test.com",
    "exp": 1690258153
}
Onde as chaves deste exemplo:

sub: identifica o "assunto" (subject), basicamente uma forma de identificar o cliente. Pode ser um id, um uuid, email, ...
exp: tempo de expiração do token. O backend vai usar esse dado para validar se o token ainda é válido ou existe a necessidade de uma atualização do token.

Existem diversas bibliotecas para geração de tokens, usemos o pyjwt.
IMPORTAR
```
poetry add pyjwt
```

O schema do token
```python
# schemas.py
class Token(BaseModel):
    access_token: str  # O token JWT que vamos gerar
    token_type: str    # O modelo que o cliente deve usar para Autorização
```

A geração do token
```python
#security.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from jwt import encode

SECRET_KEY = 'your-secret-key'  # Isso é privisório, vamos ajustar!
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()

    # Adiciona um tempo de 30 minutos para expiração
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})

    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

Testando a geração de tokens
```python
# criar o tests/test_security.py
from jwt import decode

from fast_zero.security import create_access_token, SECRET_KEY


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=['HS256'])

    assert decoded['test'] == data['test']
    assert 'exp' in decoded  # Testa se o valor de exp foi adicionado ao token

```

importar
```
poetry add tzdata

```

De volta ao endpoint /token
```python

# app.py
from fast_zero.schemas import ..., Token, ...
from fast_zero.security import create_access_token, ...

@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    # ...
    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}
```

Testando o endpoint /token
```python

# test_app.py
from http import HTTPStatus


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token

#user fixture no conftest.py
from fast_zero.security import get_password_hash
@pytest.fixture
def user(session):
    password = 'testtest'
    user = User(
        username='test',             # ← ajustar
        email='test@test.com',
        password=get_password_hash('testtest'),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password

    return user
```

Autorização
A ideia por trás da autorização é garantir que somente pessoas autorizadas possam executar determinadas operações. Como:

Alterar (PUT): Queremos garantir que o cliente possa alterar somente sua conta
Deletar: Queremos garantir que o cliente possa deletar somente a sua conta

Agora que temos os tokens, podemos garantir que só clientes com uma conta já criada e logada possam ter acesso aos endpoints.

Listar: Somente se estiver logado
Deletar: Somente se a conta for sua
Alterar: Somente se a conta for sua

```python
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi import Depends


from fast_zero.database import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    ...
```


Só com essa exigência de receber o token, podemos aplicar isso em nosso endpoint de listagem.
```python
@app.get('/users/', response_model=UserList)
def list_users(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    database = session.scalars(select(User)).all()
    return {'users': database}


    # current_user=Depends(get_current_user),
    # colocar isso no update e no delete

#no conftest.py
@pytest.fixture
def token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


# test_app.py
def test_read_users(client: TestClient, token):
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'test',
                'email': 'test@test.com',
            },
        ],
    }
```

em security.py
```python
from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session
import jwt


from fast_zero.database import get_session
from fast_zero.models import User

def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
): 
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        subject_email = payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception

    user = session.scalar(
        select(User).where(User.email == subject_email)
    )

    if not user:
        raise credentials_exception

    return user
```

Com isso podemos alterar os endpoints para depender do usuário corrente:
```python
@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    try:
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )

```


Alteração do teste
```python

def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@test.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@test.com',
        'id': 1,
    }

def test_update_integrity_error(client, user, token):
    # Inserindo fausto
    client.post(
        '/users',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    # Alterando o user das fixture para fausto - inserir
    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }

```

O endpoint de DELETE
```python
@app.delete('/users/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )
    # ...
#Atualização do teste de DELETE
def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
```

atualizar esse test
```python

def test_update_user_not_found(client, user, token):
    response = client.put(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_user_not_found(client, user, token):
    response = client.delete('/users/2',
                             headers={'Authorization': f'Bearer {token}'},)
    assert response.status_code == HTTPStatus.FORBIDDEN
```

Teste para token inválido
```python
# test_security.py
from http import HTTPStatus

def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}

```


exercicios
```python
#test_security.py
def test_get_current_user_not_found__exercicio(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_does_not_exists__exercicio(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
```