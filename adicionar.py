"""adicionar.py: coloca um episodio aprovado do Tonho na fila.
  python adicionar.py tonho02 2026-11-10T18:00:00-03:00
Copia tonho02/tonho02.mp4 e tonho02/cover.jpg e monta a legenda do Instagram
com a "Legenda" e as "Hashtags" de tonho02/post.md."""
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
FILA = os.path.join(HERE, "fila.json")
PROJETO = os.environ.get("EPISODIOS_DIR", os.path.dirname(HERE))


def legenda_do_post(texto):
    """Legenda + hashtags do post.md do Tonho (secoes **Legenda:** e **Hashtags:**)."""
    m = re.search(r"\*\*Legenda:\*\*\s*\n(.*?)\n\s*\n\*\*Hashtags:\*\*\s*(.+)", texto, re.S)
    if not m:
        return None
    corpo, tags = m.group(1).strip(), m.group(2).strip().splitlines()[0].strip()
    return f"{corpo}\n\n{tags}"


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    eid, quando = sys.argv[1], sys.argv[2]
    d = datetime.fromisoformat(quando)
    if d.tzinfo is None:
        sys.exit("Informe o fuso na data, por exemplo 2026-11-10T18:00:00-03:00")
    if d <= datetime.now(timezone.utc):
        sys.exit("Essa data ja passou.")

    pasta = os.path.join(PROJETO, eid)
    video, capa = os.path.join(pasta, f"{eid}.mp4"), os.path.join(pasta, "cover.jpg")
    for arq in (video, capa):
        if not os.path.exists(arq):
            sys.exit(f"Arquivo nao encontrado: {arq}")
    if os.path.getsize(video) > 100_000_000:
        sys.exit("O video passa de 100 MB.")
    with open(os.path.join(pasta, "post.md"), encoding="utf-8") as f:
        legenda = legenda_do_post(f.read())
    if not legenda:
        sys.exit("Nao achei '**Legenda:**' e '**Hashtags:**' no post.md.")
    if len(legenda) > 2200:
        sys.exit(f"Legenda com {len(legenda)} caracteres; o limite e 2200.")

    with open(FILA, encoding="utf-8") as f:
        dados = json.load(f)
    if any(i["id"] == eid for i in dados["itens"]):
        sys.exit(f"{eid} ja esta na fila.")
    destino = os.path.join(HERE, "fila", eid)
    os.makedirs(destino, exist_ok=True)
    shutil.copyfile(video, os.path.join(destino, "video.mp4"))
    shutil.copyfile(capa, os.path.join(destino, "capa.jpg"))
    dados["itens"].append({"id": eid, "quando": d.isoformat(), "status": "pendente", "legenda": legenda})
    dados["itens"].sort(key=lambda i: i["quando"])
    with open(FILA, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"na fila: {eid} em {d.isoformat()} ({len(legenda)} caracteres de legenda)")


if __name__ == "__main__":
    main()
