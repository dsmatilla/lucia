#!/usr/bin/env python3
"""Construye la web de Lucía.

La idea es que Lucía solo tenga que dejar ficheros .html dentro de `paginas/`.
Este script los copia tal cual a `dist/` y escribe la portada con la lista de
todo lo que hay, para que lucia.srz.es no se quede en blanco.

No toca el HTML de nadie: lo que ella escriba se publica exactamente igual.

    python3 build.py        # construye dist/
    python3 build.py --ver  # construye y abre un servidor en localhost:8000
"""

import html
import pathlib
import re
import shutil
import subprocess
import sys

RAIZ = pathlib.Path(__file__).parent
ORIGEN = RAIZ / "paginas"
DESTINO = RAIZ / "dist"
DOMINIO = "lucia.srz.es"

# Ficheros de la raíz que también se publican.
SUELTOS = ["estilo.css", "plantilla.html", "404.html", "robots.txt"]

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def titulo_de(fichero):
    """El <title> de la página; si no lo tiene, el primer <h1>; si tampoco, el
    nombre del fichero con los guiones convertidos en espacios."""
    texto = fichero.read_text(encoding="utf-8", errors="replace")
    for patron in (r"<title[^>]*>(.*?)</title>", r"<h1[^>]*>(.*?)</h1>"):
        encontrado = re.search(patron, texto, re.S | re.I)
        if encontrado:
            limpio = re.sub(r"<[^>]+>", "", encontrado.group(1)).strip()
            if limpio:
                return html.unescape(limpio)
    return fichero.stem.replace("-", " ").replace("_", " ").capitalize()


def fecha_de(fichero):
    """Cuándo se subió, según el último commit que tocó el fichero.

    En GitHub Actions hace falta `fetch-depth: 0` en el checkout; sin todo el
    historial, git no sabe la fecha y entonces se usa la del fichero.
    """
    try:
        salida = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(fichero)],
            cwd=RAIZ, capture_output=True, text=True, timeout=10)
        iso = salida.stdout.strip()
        if iso:
            anio, mes, dia = iso[:10].split("-")
            return iso[:10], "%d de %s de %s" % (int(dia), MESES[int(mes) - 1], anio)
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    import datetime
    fecha = datetime.date.fromtimestamp(fichero.stat().st_mtime)
    return (fecha.isoformat(),
            "%d de %s de %d" % (fecha.day, MESES[fecha.month - 1], fecha.year))


def portada(paginas):
    """La lista de páginas, de la más reciente a la más antigua."""
    filas = ""
    for orden, enlace, titulo, fecha_larga in paginas:
        filas += (
            '    <li>\n'
            '      <a href="%s">%s</a>\n'
            '      <span class="fecha">%s</span>\n'
            '    </li>\n' % (html.escape(enlace), html.escape(titulo),
                             html.escape(fecha_larga)))
    if not filas:
        filas = ('    <li class="vacio">Todavía no hay nada por aquí. En cuanto '
                 'subas una página a la carpeta <code>paginas</code>, aparecerá '
                 'sola en esta lista.</li>\n')
    return """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Las páginas de Lucía</title>
<link rel="stylesheet" href="/estilo.css">
</head>
<body>
<main>
  <h1>Las páginas de Lucía</h1>
  <p class="intro">Trabajos, apuntes y lo que vaya haciendo para el instituto.</p>
  <ul class="indice">
%s  </ul>
</main>
</body>
</html>
""" % filas


def construir():
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    DESTINO.mkdir()

    # Todo lo que haya en paginas/ se copia tal cual, también las imágenes y
    # las subcarpetas.
    paginas = []
    if ORIGEN.is_dir():
        shutil.copytree(ORIGEN, DESTINO, dirs_exist_ok=True)
        for fichero in sorted(ORIGEN.rglob("*.html")):
            enlace = "/" + fichero.relative_to(ORIGEN).as_posix()
            orden, fecha_larga = fecha_de(fichero)
            paginas.append((orden, enlace, titulo_de(fichero), fecha_larga))

    for nombre in SUELTOS:
        suelto = RAIZ / nombre
        if suelto.exists():
            shutil.copy2(suelto, DESTINO / nombre)

    # El CNAME tiene que ir en lo que se publica o GitHub Pages pierde el
    # dominio propio en el siguiente despliegue.
    (DESTINO / "CNAME").write_text(DOMINIO + "\n", encoding="utf-8")

    # Si Lucía escribe su propia portada, manda la suya.
    if not (DESTINO / "index.html").exists():
        paginas.sort(reverse=True)
        (DESTINO / "index.html").write_text(portada(paginas), encoding="utf-8")
        print("portada generada con %d página(s)" % len(paginas))
    else:
        print("portada propia en paginas/index.html, no se genera ninguna")

    print("listo: %s" % DESTINO)


if __name__ == "__main__":
    construir()
    if "--ver" in sys.argv:
        import http.server
        import os
        os.chdir(DESTINO)
        print("\nAbre http://localhost:8000 (Ctrl+C para parar)")
        http.server.test(HandlerClass=http.server.SimpleHTTPRequestHandler,
                         port=8000, bind="127.0.0.1")
