# Introdução ao desenvolvimento WEB
aplicações que funcionam em rede
- Dois ou mais dispositivos interconectados
- Local (LAN): como em sua casa ou em uma empresa
- Longa distância (WAN): Como diversos roteadores interconectados
- Mundial: como a própria internet

- Cliente - servidor
- Uvicorn - servidor da aplicação do FastAPI - servidor ASGI

## Códigos de respostas
- 1xx: informativo — utilizada para enviar informações para o cliente de que sua requisição foi recebida e está sendo processada.
- 2xx: sucesso — Indica que a requisição foi bem-sucedida (por exemplo, 200 OK, 201 Created).
- 3xx: redirecionamento — Informa que mais ações são necessárias para completar a requisição (por exemplo, 301 Moved Permanently, 302 Found).
- 4xx: erro no cliente — Significa que houve um erro na requisição feita pelo cliente (por exemplo, 400 Bad Request, 404 Not Found).
- 5xx: erro no servidor — Indica um erro no servidor ao processar a requisição válida do cliente (por exemplo, 500 Internal Server Error, 503 Service Unavailable).

## Códigos importantes para o curso

- 200 OK: a solicitação foi bem-sucedida. O significado exato depende do método HTTP utilizado na solicitação.
- 201 Created: a solicitação foi bem-sucedida e um novo recurso foi criado como resultado.
- 404 Not Found: o recurso solicitado não pôde ser encontrado, sendo frequentemente usado quando o recurso é inexistente.
- 422 Unprocessable Entity: usado quando a requisição está bem-formada, mas não pode ser seguida devido a erros semânticos. É comum em APIs ao validar dados de entrada.
- 500 Internal Server Error: quando existe um erro na nossa aplicação

## Pydantic
- uma camada de documentação, via OpenAPI
- validação dos modelos de entrada e saída da API
-  schemas 

criar um novo arquivo na pasta fast_zero
```bash
# fast_zero/schemas.py
from pydantic import BaseModel

#contratos
class Message(BaseModel):
    message: str
```

## Pydantic + FastAPI
Ao juntar o pydantic ao modelo de resposta, temos a garantia que a resposta seguirá esse formato e também documentará isso na API.
```bash
# fast_zero/app.py
from http import HTTPStatus

from fastapi import FastAPI

from fast_zero.schemas import Message

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}
```