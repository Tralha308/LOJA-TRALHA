import hmac
import os
import secrets

from datetime import timedelta
from functools import wraps

from flask import (
    Flask,
    abort,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__, static_folder=None)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1
)


SECRET_KEY = os.environ.get("SECRET_KEY")
SITE_USERNAME = os.environ.get("SITE_USERNAME")
SITE_PASSWORD = os.environ.get("SITE_PASSWORD")


if not SECRET_KEY or not SITE_USERNAME or not SITE_PASSWORD:
    raise RuntimeError(
        "Configure SECRET_KEY, SITE_USERNAME e SITE_PASSWORD no Render."
    )


app.config.update(
    SECRET_KEY=SECRET_KEY,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    MAX_CONTENT_LENGTH=16 * 1024
)


limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "60 per hour"],
    storage_uri="memory://"
)


def login_required(pagina):
    @wraps(pagina)
    def protegida(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))

        return pagina(*args, **kwargs)

    return protegida


def criar_token_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)

    return session["csrf_token"]


@app.context_processor
def enviar_token():
    return {
        "csrf_token": criar_token_csrf
    }


@app.before_request
def obrigar_https():
    protocolo = request.headers.get("X-Forwarded-Proto", "https")

    if protocolo != "https":
        endereco_seguro = request.url.replace(
            "http://",
            "https://",
            1
        )

        return redirect(endereco_seguro, code=301)


@app.after_request
def adicionar_seguranca(resposta):
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["X-Frame-Options"] = "DENY"
    resposta.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )
    resposta.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    resposta.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    resposta.headers["Cache-Control"] = "no-store, private"
    resposta.headers["Pragma"] = "no-cache"

    return resposta


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if session.get("authenticated"):
        return redirect(url_for("inicio"))

    erro = None

    if request.method == "POST":
        token_enviado = request.form.get("csrf_token", "")
        token_correto = session.get("csrf_token", "")

        if (
            not token_correto
            or not hmac.compare_digest(
                token_enviado,
                token_correto
            )
        ):
            abort(400)

        usuario_digitado = request.form.get("username", "")
        senha_digitada = request.form.get("password", "")

        usuario_correto = hmac.compare_digest(
            usuario_digitado,
            SITE_USERNAME
        )

        senha_correta = hmac.compare_digest(
            senha_digitada,
            SITE_PASSWORD
        )

        if usuario_correto and senha_correta:
            session.clear()
            session["authenticated"] = True
            session.permanent = True

            return redirect(url_for("inicio"))

        erro = "Usuário ou senha incorretos."

    return render_template(
        "login.html",
        error=erro
    )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    token_enviado = request.form.get("csrf_token", "")
    token_correto = session.get("csrf_token", "")

    if (
        not token_correto
        or not hmac.compare_digest(
            token_enviado,
            token_correto
        )
    ):
        abort(400)

    session.clear()

    return redirect(url_for("login"))


@app.route("/")
@login_required
def inicio():
    return render_template("index.html")


@app.route(
    "/static/<path:filename>",
    endpoint="static"
)
@login_required
def arquivos_protegidos(filename):
    return send_from_directory(
        "static",
        filename
    )


@app.errorhandler(429)
def tentativas_excedidas(erro):
    return make_response(
        render_template(
            "login.html",
            error=(
                "Muitas tentativas. "
                "Aguarde um minuto e tente novamente."
            )
        ),
        429
    )


@app.errorhandler(404)
def pagina_inexistente(erro):
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )