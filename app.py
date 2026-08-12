```python
from flask import Flask, render_template, request, jsonify, session, redirect
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# ==============================
# CONFIGURAÇÕES
# ==============================

app.secret_key = os.environ.get("SECRET_KEY", "trilha-studio-chave-secreta")

SENHA_ADMIN = os.environ.get("ADMIN_PASSWORD", "123456")

# ==============================
# BANCO SIMPLES DO CHAT
# ==============================

mensagens = []

# ==============================
# SITE PRINCIPAL
# ==============================

@app.route("/")
def index():
    return render_template("index.html")


# ==============================
# ENVIAR MENSAGEM DO VISITANTE
# ==============================

@app.route("/chat/enviar", methods=["POST"])
def enviar_mensagem():

    dados = request.get_json()

    mensagem = dados.get("mensagem", "").strip()

    if not mensagem:
        return jsonify({
            "erro": "Mensagem vazia"
        }), 400

    visitante_id = session.get("visitante_id")

    if not visitante_id:
        visitante_id = str(uuid.uuid4())
        session["visitante_id"] = visitante_id

    nova_mensagem = {
        "id": str(uuid.uuid4()),
        "visitante_id": visitante_id,
        "remetente": "visitante",
        "mensagem": mensagem,
        "data": datetime.now().strftime("%H:%M")
    }

    mensagens.append(nova_mensagem)

    return jsonify({
        "sucesso": True
    })


# ==============================
# PEGAR MENSAGENS DO VISITANTE
# ==============================

@app.route("/chat/mensagens")
def pegar_mensagens():

    visitante_id = session.get("visitante_id")

    if not visitante_id:
        return jsonify([])

    resultado = [
        m for m in mensagens
        if m["visitante_id"] == visitante_id
    ]

    return jsonify(resultado)


# ==============================
# LOGIN DO ADMIN
# ==============================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        senha = request.form.get("senha")

        if senha == SENHA_ADMIN:
            session["admin"] = True
            return redirect("/admin")

        return render_template(
            "admin.html",
            erro="Senha incorreta!"
        )

    if not session.get("admin"):
        return render_template("admin.html", login=True)

    return render_template(
        "admin.html",
        login=False
    )


# ==============================
# MENSAGENS DO ADMIN
# ==============================

@app.route("/admin/mensagens")
def admin_mensagens():

    if not session.get("admin"):
        return jsonify({
            "erro": "Não autorizado"
        }), 401

    return jsonify(mensagens)


# ==============================
# ADMIN RESPONDE
# ==============================

@app.route("/admin/responder", methods=["POST"])
def admin_responder():

    if not session.get("admin"):
        return jsonify({
            "erro": "Não autorizado"
        }), 401

    dados = request.get_json()

    visitante_id = dados.get("visitante_id")
    mensagem = dados.get("mensagem", "").strip()

    if not visitante_id or not mensagem:
        return jsonify({
            "erro": "Dados inválidos"
        }), 400

    nova_mensagem = {
        "id": str(uuid.uuid4()),
        "visitante_id": visitante_id,
        "remetente": "admin",
        "mensagem": mensagem,
        "data": datetime.now().strftime("%H:%M")
    }

    mensagens.append(nova_mensagem)

    return jsonify({
        "sucesso": True
    })


# ==============================
# LOGOUT
# ==============================

@app.route("/admin/logout")
def logout():

    session.pop("admin", None)

    return redirect("/admin")


# ==============================
# INICIAR SERVIDOR
# ==============================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
```
