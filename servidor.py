from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def inicio():
    return "Hello Word!"
def iniciar():
    app.run(host = "0.0.0.0", port = 8080)

def manter_ativo():
    t = Thread(target = iniciar)
    t.start()
