import pytest
from views import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_details_page(client):
    # On teste avec une cagnotte qui existe (ex: 'Vacances')
    response = client.get("/pot/Vacances")
    assert response.status_code == 200
    assert b"<h1>Cagnotte : Vacances</h1>" in response.data