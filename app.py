```python
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

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        mensagem = data.get("message", "").strip()

        if not mensagem:
            return jsonify({"error": "Digite uma mensagem."}), 400

        resposta = client.responses.create(
            model="gpt-5-mini",
            instructions=(
                "Você é o assistente oficial da TRALHA STUDIO. "
                "A Tralha Studio trabalha com flyers, logos, design "
                "e identidade visual. "
                "Responda em português do Brasil. "
                "Seja educado, direto e profissional. "
                "Se perguntarem sobre preços, diga que o valor depende "
                "do projeto e que devem entrar em contato para receber "
                "um orçamento. "
                "Se perguntarem como comprar, diga que devem entrar "
                "em contato com a Tralha Studio para solicitar um orçamento "
                "e combinar o pagamento. "
                "Não invente preços, prazos ou informações."
            ),
            input=mensagem
        )

        return jsonify({
            "response": resposta.output_text
        })

    except Exception as e:
        print("ERRO DA IA:", repr(e))
        return jsonify({
            "error": "Não consegui conectar com o assistente."
        }), 500


if __name__ == "__main__":
    app.run()
```
