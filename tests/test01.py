import requests

def test_addition_status_get():
    response = requests.get("http://localhost:8080/api?2+7")
    assert response.status_code == 200

def test_addition_encode_get():
    response = requests.get("http://localhost:8080/api?2+7")
    assert response.headers["Content-Type"] == "application/json"

def test_addition_get():
    response = requests.get("http://localhost:8080/api?2+7")
    response_body = response.json()
    assert response_body["result"] == "9"

def test_addition_status():
    response = requests.post("http://localhost:8080/api",data = {'op':'2+8'})
    assert response.status_code == 200

def test_addition_encode():
    response = requests.post("http://localhost:8080/api",data = {'op':'2+8'})
    assert response.headers["Content-Type"] == "application/json"

def test_addition():
    response = requests.post("http://localhost:8080/api",data = {'op':'2+8'})
    response_body = response.json()
    assert response_body["result"] == "10"

def test_subtraction():
    response = requests.post("http://localhost:8080/api",data = {'op':'8-2'})
    response_body = response.json()
    assert response_body["result"] == "6"

def test_multiplication():
    response = requests.post("http://localhost:8080/api",data = {'op':'8*8'})
    response_body = response.json()
    assert response_body["result"] == "64"

def test_division():
    response = requests.post("http://localhost:8080/api",data = {'op':'8*8'})
    response_body = response.json()
    assert response_body["result"] == "64"
