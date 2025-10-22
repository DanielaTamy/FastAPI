# Banco de dados com SQLAlchemy e gerenciando migrações com Alembic

# SQL alchemy 
O SQLAlchemy é um ORM. Ele permite que você trabalhe com bancos de dados SQL de maneira mais natural aos programadores Python. Em vez de escrever consultas SQL cruas, você pode usar métodos e atributos Python para manipular seus registros de banco de dados.

```python
# instalar no terminal
poetry add sqlalchemy

# criar arquivo fast_zero/models.py
# registrando modelo de user no sqlalchemy
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_as_dataclass, registry, mapped_column
from sqlalchemy import func

table_registry = registry()


@mapped_as_dataclass(table_registry)
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

# test - criar arquivo tests/test_db.py
from fast_zero.models import User

def test_create_user():
    user = User(username='test', email='test@test.com', password='secret')

    assert user.password == 'secret'
```

`engine`: A 'Engine' do SQLAlchemy é o ponto de contato com o banco de dados, estabelecendo e gerenciando as conexões. Ela é instanciada através da função create_engine(), que recebe as credenciais do banco de dados, o endereço de conexão (URI) e configura o pool de conexões.

`session`: Quanto à persistência de dados e consultas ao banco de dados utilizando o ORM, a Session é a principal interface. Ela atua como um intermediário entre o aplicativo Python e o banco de dados, mediada pela Engine. A Session é encarregada de todas as transações, fornecendo uma API para conduzi-las.

```python
# atualizar o test_create_user com a engine
from sqlalchemy import create_engine
from fast_zero.models import User, table_registry

def test_create_user():
    engine = create_engine('sqlite:///database.db')

    table_registry.metadata.create_all(engine)

    user = User(username='test', email='test@test.com', password='secret')

    assert user.password == 'secret'

#criar fixture no conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.models import table_registry


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
```
create_engine('sqlite:///:memory:'): cria um mecanismo de banco de dados SQLite em memória usando SQLAlchemy. Este mecanismo será usado para criar uma sessão de banco de dados para nossos testes.

table_registry.metadata.create_all(engine): cria todas as tabelas no banco de dados de teste antes de cada teste que usa a fixture session.

with Session(engine) as session: cria uma sessão Session para que os testes possam se comunicar com o banco de dadosvia engine.

yield session: fornece uma instância de Session que será injetada em cada teste que solicita a fixture session. Essa sessão será usada para interagir com o banco de dados de teste.

table_registry.metadata.drop_all(engine): após cada teste que usa a fixture session, todas as tabelas do banco de dados de teste são eliminadas, garantindo que cada teste seja executado contra um banco de dados limpo.
```python
#session - atualiza test_db com session
from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    new_user = User(username='alice', password='secret', email='teste@test')
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == 'alice'))

    assert user.username == 'alice'
``` 
Temos um problema nesse teste que pode tornar ele complicado de validar. Validamos somente o nome alice, mas não validamos o objeto todo. Isso é um tanto quanto complicado. Pois para validar o objeto inteiro, precisamos saber a que horas ele foi criado, por conta do campo init=False

```python
#no mesmo arquivo

@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_handler)

    yield time

    event.remove(model, 'before_insert', fake_time_handler)
@pytest.fixture
def mock_db_time():
    return _mock_db_time



#instalar o pydantic settings no terminal
poetry add pydantic-settings

# criar arquivo settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict( 
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str

#criar .env na raiz do projeto
DATABASE_URL="sqlite:///database.db"


#adicionar ao gitignore o database
echo 'database.db' >> .gitignore
```
# Migrações
Banco de dados evolutivo

O banco acompanha as alterações do código

Reverter alterações no schema do banco

```bash
#instalar 
poetry add alembic

alembic init migrations
```

Configurando a migração automática
Vamos fazer algumas alterações no arquivo migrations/env.py para que nossa configurações de banco de dados sejam passadas ao alembic:

Importar as Settings do nosso arquivo settings.py e a table_registry dos nossos modelos.

Configurar a URL do SQLAlchemy para ser a mesma que definimos em Settings.

Verificar a existência do arquivo de configuração do Alembic e, se presente, lê-lo.

Definir os metadados de destino como table_registry.metadata, que é o que o Alembic utilizará para gerar automaticamente as migrações.

```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from fast_zero.models import table_registry
from fast_zero.settings import Settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option(
    'sqlalchemy.url', Settings().DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = table_registry.metadata



# criar a migração
#no terminal rodar:
# cria a migração create users table
alembic revision --autogenerate -m "create users table"

#se n funcionar - n preencher a parte do update
del database.db      # Windows
alembic stamp head   # marca que o Alembic está na revisão mais recente
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

exercicios
```python
#models.py
@mapped_as_dataclass(table_registry)
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )


#conftest.py
@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_handler)

    yield time

    event.remove(model, 'before_insert', fake_time_handler)


@pytest.fixture
def mock_db_time():
    return _mock_db_time

#atualizar onde tem relacionado ao novo campo update at
# gerar uma nova migração
alembic upgrade head
alembic revision --autogenerate -m "add updated_at to users"
alembic upgrade head
```