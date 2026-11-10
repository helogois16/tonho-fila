"""publicar.py: publica no Instagram o Reel da fila que chegou na hora. Roda sozinho no GitHub Actions.

Regras de seguranca:
- publica um Reel por execucao;
- confere se o token e da conta certa antes de postar;
- nunca repete um post: se a confirmacao se perder, marca "conferir" e para;
- nao posta com mais de 6 horas de atraso.

Ambiente: IG_TOKEN, PUBLIC_BASE (endereco publico da pasta), IG_USERNAME (opcional).
Saida 1 quando algo precisa de atencao: o GitHub avisa por e-mail."""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
FILA = os.path.join(HERE, "fila.json")
API = os.environ.get("IG_API_BASE", "https://graph.instagram.com").rstrip("/")
ATRASO_MAX = timedelta(hours=6)
TENTATIVAS_MAX = 3
ESPERA_S = float(os.environ.get("IG_POLL_SECONDS", "10"))
ESPERA_MAX_S = 600


class ErroApi(Exception):
    pass


def chamar(metodo, caminho, params):
    """Chama a API sem nunca imprimir a URL, porque o token vai nos parametros."""
    dados = urllib.parse.urlencode({**params, "access_token": os.environ["IG_TOKEN"]})
    url = f"{API}/{caminho}"
    if metodo == "GET":
        req = urllib.request.Request(f"{url}?{dados}")
    else:
        req = urllib.request.Request(url, data=dados.encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        corpo = e.read().decode("utf-8", "replace")[:500].replace(os.environ["IG_TOKEN"], "***")
        raise ErroApi(f"HTTP {e.code}: {corpo}") from None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise ErroApi(f"falha de rede: {type(e).__name__}") from None


def conferir_arquivo(url, tipo):
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            ct = r.headers.get("Content-Type", "")
    except (urllib.error.URLError, TimeoutError) as e:
        raise ErroApi(f"arquivo inacessivel: {url} ({type(e).__name__})") from None
    if not ct.startswith(tipo):
        raise ErroApi(f"tipo errado em {url}: {ct}")


def salvar(dados):
    tmp = FILA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, FILA)


def agora():
    return datetime.now(timezone.utc)


def publicar(item, dados, base):
    video = f"{base}/fila/{item['id']}/video.mp4"
    capa = f"{base}/fila/{item['id']}/capa.jpg"
    conferir_arquivo(video, "video/")
    conferir_arquivo(capa, "image/")

    uid, nome = identificar()
    esperado = os.environ.get("IG_USERNAME", "deuruimtonho")
    if nome.lower() != esperado.lower():
        raise ErroApi(f"token de outra conta: {nome}")

    cont = chamar("POST", f"{uid}/media", {
        "media_type": "REELS", "video_url": video, "cover_url": capa,
        "caption": item["legenda"], "share_to_feed": "true",
    })["id"]
    limite = time.monotonic() + ESPERA_MAX_S
    while True:
        st = chamar("GET", cont, {"fields": "status_code,status"})
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise ErroApi(f"o Instagram recusou o video: {st}")
        if time.monotonic() > limite:
            raise ErroApi("o Instagram demorou demais para processar o video")
        time.sleep(ESPERA_S)

    # Daqui em diante, nunca tentar de novo sozinho: o post pode ter saido.
    item["status"] = "enviando"
    salvar(dados)
    try:
        res = chamar("POST", f"{uid}/media_publish", {"creation_id": cont})
    except ErroApi as e:
        item["status"] = "conferir"
        item["erro"] = str(e)
        salvar(dados)
        print(f"ATENCAO: {item['id']}: confira no Instagram se saiu. Nao vou repetir. {e}")
        return False
    item.update(status="publicado", media_id=res.get("id"), publicado_em=agora().isoformat())
    item.pop("erro", None)
    salvar(dados)
    print(f"publicado: {item['id']} (media {res.get('id')})")
    return True


def identificar():
    """Devolve (id da conta do Instagram, nome de usuario) para o token atual.
    Com IG_USER_ID (token de usuario do sistema), pergunta pela conta; senao, usa /me."""
    ig = os.environ.get("IG_USER_ID", "").strip()
    if ig:
        conta = chamar("GET", ig, {"fields": "id,username"})
        return conta["id"], conta.get("username", "")
    conta = chamar("GET", "me", {"fields": "user_id,username"})
    return conta["user_id"], conta.get("username", "")


def conferir():
    """So confere o token, nos dois enderecos da API, sem publicar nada."""
    global API
    ok = False
    for base in ("https://graph.facebook.com", "https://graph.instagram.com"):
        API = base
        try:
            uid, nome = identificar()
            print(f"token OK em {base}: conta @{nome} (id {uid})")
            ok = True
        except (ErroApi, KeyError) as e:
            print(f"nao funcionou em {base}: {e}")
    return 0 if ok else 1


def main():
    if "--conferir" in sys.argv:
        return conferir()
    with open(FILA, encoding="utf-8") as f:
        dados = json.load(f)
    # Um "enviando" que sobrou significa que a execucao anterior morreu no meio.
    travados = [i for i in dados["itens"] if i["status"] == "enviando"]
    if travados:
        for i in travados:
            i["status"] = "conferir"
        salvar(dados)
        print("ATENCAO: confira no Instagram se saiu:", ", ".join(i["id"] for i in travados))
        return 1

    agora_ = agora()
    vencidos = sorted((i for i in dados["itens"] if i["status"] == "pendente"
                       and datetime.fromisoformat(i["quando"]) <= agora_), key=lambda i: i["quando"])
    if not vencidos:
        print("nada para publicar agora")
        return 0
    item = vencidos[0]
    if agora_ - datetime.fromisoformat(item["quando"]) > ATRASO_MAX:
        item["status"] = "atrasado"
        salvar(dados)
        print(f"ATENCAO: {item['id']} passou de 6 h de atraso e nao foi postado. Escolha outra data.")
        return 1
    try:
        return 0 if publicar(item, dados, os.environ["PUBLIC_BASE"].rstrip("/")) else 1
    except ErroApi as e:
        item["tentativas"] = item.get("tentativas", 0) + 1
        item["erro"] = str(e)
        if item["tentativas"] >= TENTATIVAS_MAX:
            item["status"] = "erro"
        salvar(dados)
        print(f"ATENCAO: {item['id']}: tentativa {item['tentativas']} falhou: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
