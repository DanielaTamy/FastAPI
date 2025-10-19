# Configurações de Ambiente 

## pyenv
ferramenta de gerenciamento de versões do Python -> permite alternar entre várias versões

**Comando de Instalação no terminal:**
```bash
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
``` 
Se aparecer uma mensagem sobre execução de scripts bloqueada, rode este comando antes:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Verificar se foi instalado com sucesso (reinicie o computador)
```bash
pyenv --version
```
Instalar versão 3.12:latest
```bash
pyenv install 3.12.10
```

## pipx
ferramenta para instalar e executar ferramentas Python globalmente no sistema. Cria um ambiente virtual e isola cada ferramenta dentro dele. 

**Comando de Instalação no terminal:**
```bash
pip install pipx
``` 
e para adicionar ao path:
```bash
pipx ensurepath
``` 
fechar e abrir o terminal novamente

## poetry
gerenciador de projetos para Python. Ele pode nos ajudar em diversas etapas do ciclo de desenvolvimento, como a instalação de versões específicas do Python, a criação e manutenção de projetos (incluindo a definição de estruturas de pastas, o gerenciamento de ambientes virtuais e a instalação de bibliotecas), além de permitir a publicação de pacotes e muito mais.

**Comando de Instalação no terminal:**
```bash
pipx install poetry
pipx inject poetry poetry-plugin-shell
``` 

# Criando um projeto

**Comando de criação no terminal:**
```bash
poetry new --flat fast_zero 
cd fast_zero
``` 
criara uma estrutura:
```bash
.
├── fast_zero
│  └── __init__.py
├── pyproject.toml
├── README.md
└── tests
   └── __init__.py
``` 

# Instalando o FastAPI

**Comando de criação no terminal:**
precisa estar na pasta que tem o .toml
```bash
poetry install
poetry add fastapi
``` 

# Olá mundo
na pasta fast_zero criar um app.py

```bash
# fastzero/app.py
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def read_root():
    return {'message': 'Olá Mundo!'}

``` 
para rodar deve ativar o ambiente virtual
```bash
poetry shell #ativa o venv
``` 
iniciar o servidor
```bash
fastapi dev fast_zero/app.py
``` 

para acessar a aplicação: http://localhost:8000

swagger: http://localhost:8000/docs

redoc: http://localhost:8000/redoc

# Instalando ferramentas de desenvolvimento

## Ruff
- Analisar o código de forma estática (Linter): Efetuar a verificação se estamos programando de acordo com boas práticas do python.
- Formatar o código (Formatter): Efetuar a verificação do código para padronizar um estilo de código pré-definido.

para instalar
```bash
poetry add --group dev ruff

#adicionar o pyproject.toml
[tool.ruff]
line-length = 79
extend-exclude = ['migrations']

[tool.ruff.lint]
preview = true
select = ['I', 'F', 'E', 'W', 'PL', 'PT']

[tool.ruff.format]
preview = true
quote-style = 'single'
``` 
testar:
```bash
ruff check . #verificar os termos que foram definidos
ruff format . #faz formatação do código com as boas práticas
``` 

## Pytest
- framework de testes, que usaremos para escrever e executar nossos testes
- O configuraremos para reconhecer o caminho base para execução dos testes na raiz do projeto

para instalar
```bash
poetry add --group dev pytest pytest-cov

#adicionar o pyproject.toml
[tool.pytest.ini_options]
pythonpath = "."
addopts = '-p no:warnings'

``` 
testar:
```bash
pytest --cov=fast_zero -vv
#ver a cobertura de teste
coverage html #se n abrir: start .\htmlcov\index.html
``` 


## taskpy
- executor de tarefas (task runner) complementar em nossa aplicação

para instalar
```bash
poetry add --group dev taskipy
# precisei mudar a versão do python no project.toml
# requires-python = ">=3.12,<4.0"


#adicionar o pyproject.toml
[tool.taskipy.tasks]
lint = 'ruff check'
pre_format = 'ruff check --fix'
format = 'ruff format'
run = 'fastapi dev fast_zero/app.py'
pre_test = 'task lint'
test = 'pytest -s -x --cov=fast_zero -vv'
post_test = 'coverage html'
``` 
- lint = 'ruff check' - Executa análise estática do código com Ruff (verifica erros de estilo, lint, etc.)
- pre_format = 'ruff check --fix' - Corrige automaticamente os problemas encontrados pelo Ruff
- format = 'ruff format' - Formata o código com Ruff (organiza indentação, espaços, etc.)
- run = 'fastapi dev fast_zero/app.py' - Roda o servidor FastAPI em modo de desenvolvimento
- pre_test = 'task lint' - Executa a tarefa de lint automaticamente antes de rodar os testes
- test = 'pytest -s -x --cov=fast_zero -vv' -  Roda os testes com pytest
- post_test = 'coverage html' - Gera um relatório HTML de cobertura após os testes


testar:
```bash
task run
task test
task format
``` 

# Testando o olá mundo
na pasta test cria um arquivo test_app.py

```bash
# tests/test_app.py
from http import HTTPStatus #importar para status code
from fastapi.testclient import TestClient
from fast_zero.app import app


def test_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)  # Arrange

    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert 
    assert response.json() == {'message': 'Olá Mundo!'}  # Asset

``` 
👉 O assert em testes serve para verificar se uma condição é verdadeira.

Se a condição for verdadeira, o teste passa ✅.
Se a condição for falsa, o teste falha ❌ e mostra uma mensagem de erro.

se o coverage ficar desatualizado: 
```bash 
coverage erase
coverage run -m pytest
coverage html
```

# Github
instalar ignr - para instalar o gitignore
```bash 
pipx install ignr
pipx run ignr -p python > .gitignore

```