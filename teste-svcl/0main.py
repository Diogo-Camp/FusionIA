from flask import Flask, request, jsonify
from servidor_ia import ServidorIA

app = Flask(__name__)
ia = ServidorIA()

@app.route("/conversar", methods=["POST"])
def conversar():
    data = request.json
    mensagem = data.get("mensagem")
    modelo = data.get("modelo")
    personalidade = data.get("personalidade")

    if modelo:
        ia.definir_modelo(modelo)
    if personalidade:
        try:
            ia.definir_personalidade(personalidade)
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    resposta = ia.conversar(mensagem)
    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run(port=5000)
