# lucia.srz.es

Las páginas que Lucía va subiendo, publicadas en <https://lucia.srz.es>.

## Cómo subir una página

1. Entra en la carpeta **`paginas`** aquí arriba y, dentro, en la de la
   asignatura (por ejemplo `frances`).
2. Pulsa **Add file → Upload files** y arrastra tu `.html`.
3. Abajo del todo, **Commit changes**.

En un par de minutos está publicado. La carpeta y el nombre del fichero son la
dirección: `frances/examen-de-minou.html` se ve en
`lucia.srz.es/frances/examen-de-minou.html`.

## La navegación se escribe sola

No hay que añadir ningún enlace a mano:

- La portada (`lucia.srz.es`) lista las asignaturas, con cuántas páginas tiene
  cada una y la fecha de la última.
- Cada asignatura tiene su propia página (`lucia.srz.es/frances/`) con la lista
  de todo lo que hay dentro, de lo más nuevo a lo más viejo.
- El nombre con el que aparece cada página es su `<title>`.

### Para crear una asignatura nueva

Al subir el fichero, en el nombre escribe la carpeta delante con una barra:
`musica/trabajo-de-bach.html`. GitHub crea la carpeta sola y en el siguiente
despliegue aparece en la portada.

Las carpetas se llaman en minúsculas, sin acentos y con guiones en vez de
espacios, pero en la portada salen bien escritas: `geografia-e-historia` se
muestra como «Geografía e Historia». Si una asignatura sale con un nombre feo,
sube dentro de su carpeta un fichero `categoria.txt` con el nombre que quieras
en la primera línea; ese fichero no se publica, solo sirve para el índice.

Una carpeta sin ningún `.html` dentro no cuenta como asignatura, así que
`paginas/imagenes/` no aparece en la portada.

### Para empezar una página nueva

Copia [`plantilla.html`](plantilla.html), cámbiale el nombre y escribe dentro.
Trae ya lo necesario para que se vea bien en el móvil.

### Lo que llevan todas las páginas

Da igual lo distinta que sea cada página por dentro; así empiezan todas:

```html
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>El título que sale en el índice</title>
```

Lo demás (la dirección canónica, el icono, la tarjeta que se ve al compartir
el enlace por WhatsApp y el contador de visitas) se le añade solo a cada
página al publicar, así que no hay que pegar nada.

Lo único que merece la pena escribir a mano es el resumen, que es lo que sale
debajo del título en Google. Si no lo pones, se usa el primer párrafo:

```html
<meta name="description" content="Dos líneas diciendo de qué va la página.">
```

Y al final, antes de cerrar la página, el enlace de vuelta a la asignatura:

```html
<footer class="pie">
  <a href="./">← Francés</a>
  <span>lucia.srz.es</span>
</footer>
```

Si la página trae su propio diseño (de los que hace Claude, por ejemplo), el
`pie` se queda con sus colores; basta con copiar también el bloque `.pie` del
CSS de cualquiera de las páginas que ya están subidas.

### Imágenes

Van en `paginas/imagenes/` y se enlazan así:

```html
<img src="/imagenes/la-foto.jpg" alt="Lo que se ve en la foto">
```

### Dos cosas que ahorran disgustos

- **Nombres de fichero y de carpeta** en minúsculas, sin acentos, sin eñes y
  sin espacios: `examen-de-mates.html`, no `Exámen de Mates.html`.
- **Que no falte el `<title>`**, que es lo que sale en los índices y en la
  pestaña del navegador.

### Si prefieres tus propios índices

Sube un `index.html` a `paginas/` y manda el tuyo como portada; lo mismo dentro
de la carpeta de una asignatura. Donde haya un `index.html` propio no se genera
el automático.

## Para el que mantiene esto

Sitio estático sin dependencias: `build.py` copia `paginas/` a `dist/`, añade
los sueltos de la raíz (`estilo.css`, `plantilla.html`, `404.html`, `og.png`,
`favicon.ico`, `apple-touch-icon.png`), escribe el `CNAME` y genera la
portada, un índice por cada subcarpeta con páginas, el `robots.txt` y el
`sitemap.xml`.

Del HTML de Lucía no cambia nada: solo le añade, antes de cerrar el `<head>`,
las etiquetas que tienen que ser iguales en todo el sitio (canónica, Open
Graph, icono y el `<script>` de Umami). Si la página trae ya su `description`
o su `<meta robots>`, se sustituyen por los que toquen, para que la política
del sitio esté en un solo sitio y no en veinte ficheros.

```bash
python3 build.py         # construye dist/
python3 build.py --ver   # construye y sirve en http://localhost:8000
```

Los nombres bonitos de las asignaturas habituales están en el diccionario
`NOMBRES` de `build.py`; el `categoria.txt` de cada carpeta manda sobre él y
evita tener que tocar el código.

Cada push a `main` dispara `.github/workflows/deploy.yml`, que construye y
publica `dist/` en GitHub Pages. El checkout usa `fetch-depth: 0` porque las
fechas de los índices salen del último commit de cada fichero.

### Buscadores y visitas

La constante `INDEXAR` de `build.py` decide si el sitio sale en Google. Está
en `True`: el `robots.txt` lo permite todo y apunta al `sitemap.xml`, que se
regenera en cada despliegue con la fecha del último commit de cada página.
Poniéndola en `False` pasa lo contrario: `Disallow: /`, ningún sitemap y un
`<meta name="robots" content="noindex, nofollow">` en todas las páginas. No
hay que tocar nada más.

La página de error y la plantilla nunca se indexan, estén como estén las
cosas, y tampoco salen en el sitemap.

Las visitas se cuentan con [Umami](https://umami.srz.es) (website id
`5720d3a6-e3a4-4d32-97e0-332d6107a0f7`), que no usa cookies ni recoge datos
personales, así que no hace falta aviso de cookies.

La imagen que se ve al compartir un enlace (`og.png`) y los iconos están
hechos con Pillow; si hay que rehacerlos, es un script de quince líneas y no
una dependencia del despliegue: GitHub Actions solo ejecuta `build.py`, que
usa la biblioteca estándar y nada más.
