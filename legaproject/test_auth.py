import urllib.request
import json

data = {
    'usuario': 'testuser4',
    'nome_completo': 'Test User',
    'email': 'test4@example.com',
    'senha': 'testpass123',
    'dt_nasc': '2000-01-01',
    'telefone': '11999999996'
}
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/auth/cadastro',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
res = urllib.request.urlopen(req)
print('Cadastro:', res.getcode(), res.read().decode('utf-8'))

login_data = {
    'usuario': 'testuser4',
    'password': 'testpass123'
}
req2 = urllib.request.Request(
    'http://127.0.0.1:8000/api/auth/login',
    data=json.dumps(login_data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    res2 = urllib.request.urlopen(req2)
    print('Login:', res2.getcode(), res2.read().decode('utf-8'))
except Exception as e:
    print('Login falhou:', e)
