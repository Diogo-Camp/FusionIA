from flask import Flask, request, jsonify
from servidor_ia import ServidorIA
from config.modelos import validar_modelo
from config.personalidades import listar_personalidades

app = Flask(__name__)
ia = ServidorIA()

# @app.route("/conversar", methods=["POST"])
# def conversar():
#     data = request.json
#     print("🔍 Dados recebidos:", data)
#     mensagem = data.get("mensagem")
#     modelo = data.get("modelo")
#     personalidade = data.get("personalidade")
#
#
#     if modelo and not validar_modelo(modelo):
#         return jsonify({"erro": "Modelo inválido"}), 400
#
#     if personalidade and personalidade not in listar_personalidades():
#         return jsonify({"erro": "Personalidade não reconhecida"}), 400
#
#     ia.configurar(modelo=modelo, personalidade=personalidade)
#
#     resposta = ia.conversar(mensagem)
#     return jsonify({"resposta": resposta})
@app.route("/conversar", methods=["POST"])
def conversar():
    try:
        data = request.get_json(force=True)
        print("🔍 Dados recebidos:", data)

        mensagem = data.get("mensagem")
        modelo = data.get("modelo")
        personalidade = data.get("personalidade")

        if not mensagem:
            return jsonify({"erro": "Campo 'mensagem' é obrigatório."}), 400

        if modelo and not validar_modelo(modelo):
            return jsonify({"erro": f"Modelo inválido: {modelo}"}), 400

        if personalidade and personalidade not in listar_personalidades():
            return jsonify({"erro": f"Personalidade não reconhecida: {personalidade}"}), 400

        ia.configurar(modelo=modelo, personalidade=personalidade)
        resposta = ia.conversar(mensagem)
        return jsonify({"resposta": resposta})

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5000)
