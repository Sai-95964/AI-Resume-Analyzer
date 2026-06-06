from app import app
resp = app.test_client().get('/')
data = resp.data.decode('utf-8')
print('FOUND' if '<div class="container">' in data else 'NOT FOUND')
print()  # newline
print(data[:400])
