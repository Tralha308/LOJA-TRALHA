from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# Pega a chave que está nas Environment Variables do Render
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        mensagem = data.get("message", "").strip()

        if not mensagem:
            return jsonify({
                "error": "Digite uma mensagem."
            }), 400

        resposta = client.responses.create(
            model="gpt-5-mini",
            instructions="""
Você é o assistente oficial da TRALHA STUDIO.

A Tralha Studio trabalha com:
- Flyers
- Logos
- Design
- Identidade visual

Responda em português do Brasil.
Seja educado, direto e profissional.
Ajude os visitantes com dúvidas sobre os serviços da Tralha Studio.

Se perguntarem preço, diga que o valor depende do projeto
e que devem entrar em contato para receber um orçamento.

Não invente preços, prazos ou informações que não foram fornecidas.
""",
            input=mensagem
        )

        return jsonify({
            "response": resposta.output_text
        })

    except Exception as e:
        print("ERRO:", e)

        return jsonify({
            "error": "Não consegui responder agora. Tente novamente."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)