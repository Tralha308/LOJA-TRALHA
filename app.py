from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    mensagem = data.get("message", "").strip()

    if not mensagem:
        return jsonify({"reply": "Digite uma mensagem."})

    mensagem_lower = mensagem.lower()

    # Respostas automáticas, SEM OpenAI
    if any(x in mensagem_lower for x in ["oi", "olá", "ola", "hello"]):
        resposta = "Olá! 👋 Seja bem-vindo à TRALHA STUDIO! Como posso te ajudar?"

    elif "preço" in mensagem_lower or "preco" in mensagem_lower:
        resposta = "Temos logos por R$40, flyers por R$30 e banners por R$25. 💛"

    elif "logo" in mensagem_lower:
        resposta = "Claro! Trabalhamos com criação de logos personalizados. O valor é R$40."

    elif "flyer" in mensagem_lower:
        resposta = "Criamos flyers personalizados. O valor é R$30."

    elif "banner" in mensagem_lower:
        resposta = "Também fazemos banners personalizados. O valor é R$25."

    elif "pedido" in mensagem_lower or "encomenda" in mensagem_lower:
        resposta = "Para fazer um pedido, fale com a nossa equipe pelo contato disponível no site."

    elif "contato" in mensagem_lower:
        resposta = "Você pode entrar em contato conosco através dos canais disponíveis no site."

    else:
        resposta = "Entendi! 👀 Para falar diretamente com a equipe da TRALHA STUDIO, envie sua mensagem pelo contato do site."

    return jsonify({"reply": resposta})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)