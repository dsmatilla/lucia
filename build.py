#!/usr/bin/env python3
"""Construye la web de Lucía.

La idea es que Lucía solo tenga que dejar ficheros .html dentro de `paginas/`,
cada uno en la carpeta de su asignatura. Este script los copia tal cual a
`dist/` y escribe sola la navegación:

    paginas/frances/examen-de-minou.html

        -> /                        portada con la lista de categorías
        -> /frances/                lista de las páginas de esa categoría
        -> /frances/examen-de-minou.html    la página, igual que la escribió

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

# Las carpetas se llaman en minúsculas y sin acentos para que las direcciones
# queden limpias, así que aquí está el nombre de verdad de las asignaturas
# habituales. Si falta alguna, se pone a mano con un `categoria.txt` dentro de
# la carpeta (ver NOMBRE_CATEGORIA) y no hace falta tocar este fichero.
NOMBRES = {
    "biologia-y-geologia": "Biología y Geología",
    "dibujo-tecnico": "Dibujo Técnico",
    "economia": "Economía",
    "educacion-fisica": "Educación Física",
    "educacion-plastica": "Educación Plástica",
    "filosofia": "Filosofía",
    "fisica-y-quimica": "Física y Química",
    "frances": "Francés",
    "geografia-e-historia": "Geografía e Historia",
    "informatica": "Informática",
    "ingles": "Inglés",
    "latin": "Latín",
    "lengua": "Lengua Castellana y Literatura",
    "lengua-castellana-y-literatura": "Lengua Castellana y Literatura",
    "matematicas": "Matemáticas",
    "musica": "Música",
    "religion": "Religión",
    "tecnologia": "Tecnología",
    "tutoria": "Tutoría",
    "valores-eticos": "Valores Éticos",
}

# Fichero opcional dentro de una carpeta con el nombre que debe mostrarse.
NOMBRE_CATEGORIA = "categoria.txt"

# Para ordenar las categorías alfabéticamente sin que los acentos manden la
# Ñ y la É al final de la lista.
SIN_ACENTOS = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")


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

    Con `--follow`, mover una página a la carpeta de su asignatura no le
    cambia la fecha: git sigue el rastro hasta donde estaba antes.

    En GitHub Actions hace falta `fetch-depth: 0` en el checkout; sin todo el
    historial, git no sabe la fecha y entonces se usa la del fichero.
    """
    try:
        salida = subprocess.run(
            ["git", "log", "-1", "--follow", "--format=%cI", "--", str(fichero)],
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


def nombre_de(carpeta):
    """Cómo se llama una categoría de cara al público."""
    propio = carpeta / NOMBRE_CATEGORIA
    if propio.is_file():
        for linea in propio.read_text(encoding="utf-8", errors="replace").splitlines():
            if linea.strip():
                return linea.strip()
    if carpeta.name in NOMBRES:
        return NOMBRES[carpeta.name]
    limpio = carpeta.name.replace("-", " ").replace("_", " ").strip()
    return limpio[:1].upper() + limpio[1:]


def paginas_en(carpeta, recursivo):
    """Las páginas de una carpeta, de la más reciente a la más antigua.

    Los `index.html` no se listan: son portadas, no trabajos.
    """
    ficheros = carpeta.rglob("*.html") if recursivo else carpeta.glob("*.html")
    encontradas = []
    for fichero in ficheros:
        if fichero.name == "index.html":
            continue
        orden, fecha_larga = fecha_de(fichero)
        encontradas.append((orden, titulo_de(fichero), fecha_larga,
                            "/" + fichero.relative_to(ORIGEN).as_posix()))
    encontradas.sort(reverse=True)
    return encontradas


def categorias_en(carpeta):
    """Las subcarpetas que tienen alguna página dentro, por orden alfabético.

    Una carpeta sin ningún .html no es una categoría: así `paginas/imagenes/`
    no aparece en la portada.
    """
    encontradas = []
    for sub in carpeta.iterdir():
        if not sub.is_dir() or sub.name.startswith("."):
            continue
        paginas = paginas_en(sub, recursivo=True)
        if not paginas:
            continue
        nombre = nombre_de(sub)
        encontradas.append((nombre.translate(SIN_ACENTOS).lower(),
                            nombre, sub.name, paginas))
    encontradas.sort()
    return encontradas


# Las páginas generadas ------------------------------------------------------

def envoltorio(titulo, cuerpo):
    """El esqueleto común de la portada y de los índices de categoría."""
    return """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>%s</title>
<link rel="stylesheet" href="/estilo.css">
</head>
<body>
<main>
%s</main>
</body>
</html>
""" % (html.escape(titulo), cuerpo)


def lista_de_paginas(paginas):
    filas = ""
    for _, titulo, fecha_larga, enlace in paginas:
        filas += (
            '    <li>\n'
            '      <a href="%s">%s</a>\n'
            '      <span class="fecha">%s</span>\n'
            '    </li>\n' % (html.escape(enlace), html.escape(titulo),
                             html.escape(fecha_larga)))
    return '  <ul class="indice">\n%s  </ul>\n' % filas


def lista_de_categorias(categorias):
    filas = ""
    for _, nombre, slug, paginas in categorias:
        cuantas = ("1 página" if len(paginas) == 1
                   else "%d páginas" % len(paginas))
        filas += (
            '    <li>\n'
            '      <a href="/%s/">%s</a>\n'
            '      <span class="meta">%s · la última, %s</span>\n'
            '    </li>\n' % (html.escape(slug), html.escape(nombre),
                             cuantas, html.escape(paginas[0][2])))
    return '  <ul class="indice">\n%s  </ul>\n' % filas


def portada(categorias, sueltas):
    cuerpo = ("  <h1>Las páginas de Lucía</h1>\n"
              "  <p class=\"intro\">Trabajos, apuntes y lo que vaya haciendo "
              "para el instituto.</p>\n")
    if categorias:
        cuerpo += lista_de_categorias(categorias)
    if sueltas:
        if categorias:
            cuerpo += "  <h2>Sin asignatura</h2>\n"
        cuerpo += lista_de_paginas(sueltas)
    if not categorias and not sueltas:
        cuerpo += ('  <ul class="indice">\n'
                   '    <li class="vacio">Todavía no hay nada por aquí. En '
                   'cuanto subas una página a una carpeta de '
                   '<code>paginas</code>, aparecerá sola en esta lista.</li>\n'
                   '  </ul>\n')
    return envoltorio("Las páginas de Lucía", cuerpo)


def indice_de_categoria(nombre, paginas):
    cuerpo = "  <h1>%s</h1>\n" % html.escape(nombre)
    cuerpo += lista_de_paginas(paginas)
    cuerpo += '  <a class="volver" href="/">← Todas las asignaturas</a>\n'
    return envoltorio("%s · Las páginas de Lucía" % nombre, cuerpo)


# La construcción ------------------------------------------------------------

def construir():
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    DESTINO.mkdir()

    categorias = []
    sueltas = []
    if ORIGEN.is_dir():
        # Todo lo que haya en paginas/ se copia tal cual, también las imágenes
        # y las subcarpetas. El categoria.txt no, que es solo para el índice.
        shutil.copytree(ORIGEN, DESTINO, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(NOMBRE_CATEGORIA))
        categorias = categorias_en(ORIGEN)
        sueltas = paginas_en(ORIGEN, recursivo=False)

    for nombre in SUELTOS:
        suelto = RAIZ / nombre
        if suelto.exists():
            shutil.copy2(suelto, DESTINO / nombre)

    # El CNAME tiene que ir en lo que se publica o GitHub Pages pierde el
    # dominio propio en el siguiente despliegue.
    (DESTINO / "CNAME").write_text(DOMINIO + "\n", encoding="utf-8")

    # Un índice por categoría, salvo que Lucía haya escrito el suyo.
    for _, nombre, slug, paginas in categorias:
        indice = DESTINO / slug / "index.html"
        if indice.exists():
            print("%s: índice propio, no se genera" % slug)
            continue
        indice.write_text(indice_de_categoria(nombre, paginas), encoding="utf-8")
        print("%s: %d página(s)" % (slug, len(paginas)))

    # Y la portada, salvo que también haya escrito la suya.
    if (DESTINO / "index.html").exists():
        print("portada propia en paginas/index.html, no se genera ninguna")
    else:
        (DESTINO / "index.html").write_text(portada(categorias, sueltas),
                                            encoding="utf-8")
        print("portada generada con %d categoría(s) y %d página(s) sin "
              "asignatura" % (len(categorias), len(sueltas)))

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
