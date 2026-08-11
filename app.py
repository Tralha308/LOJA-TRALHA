from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    dados = request.get_json()
    pergunta = dados.get("pergunta", "")

    if not pergunta:
        return jsonify({"resposta": "Digite uma pergunta."})

    try:
        resposta = client.responses.create(
            model="gpt-5-mini",
            instructions="""
Você é o assistente virtual da Tralha Studio.

A Tralha Studio trabalha com criação de:
- Flyers
- Logos
- Identidade visual

Responda de maneira simples, curta e educada.
Se perguntarem algo sobre a Tralha Studio, ajude o cliente.
Se não souber uma informação específica, diga que o cliente pode entrar em contato com o responsável.
""",
            input=pergunta
        )

        return jsonify({
            "resposta": resposta.output_text
        })

    except Exception as erro:
        print(erro)
        return jsonify({
            "resposta": "Desculpe, aconteceu um erro. Tente novamente."
        })

if __name__ == "__main__":
    app.run()