from flask import Flask
from flask import request

app = Flask(__name__)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route("/checkonline")
def checkonline():
    return "ok"


@app.route("/upload", methods=['POST'])
def upload():
    with open("touched.log", "a") as w:
        w.write(request.data.decode("utf-8"))
        w.write("\n")

    return "ok"


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/kill")
def kill():
    shutdown_server()
    return "server shutting down..."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="18888")
