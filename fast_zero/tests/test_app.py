from http import HTTPStatus


def test_root_deve_retornar_ok_e_ola_mundo(client):
    # adiciona o cliente dps que cria a fixture como parametro
    # deleta depois que colocar a fixture
    # client = TestClient(app)  # Arrange

    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'message': 'Olá Mundo!'}  # Assert


def test_ola_deve_retornar_html_com_ola_mundo(client):
    # client = TestClient(app)  # Arrange

    response = client.get('/ola')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert '<h1> Olá Mundo </h1>' in response.text  # Assert


def test_create_user(client):
    # client = TestClient(app)
    response = client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secret',
        },
    )
    # voltou o status code correto?
    assert response.status_code == HTTPStatus.CREATED
    # validar userPublic
    assert response.json() == {
        'username': 'testuser',
        'email': 'test@example.com',
        'id': 1,
    }


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


def test_read_user(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'testuser',
        'email': 'test@example.com',
        'id': 1,
    }


def test_read_user_not_found(client):
    response = client.get('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND


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


def test_update_user_not_found(client):
    response = client.put(
        '/users/2',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_read_users_id(client):
    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.OK


def test_read_users_not_found(client):
    response = client.get('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_not_found(client):
    response = client.delete('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND
