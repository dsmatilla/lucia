# lucia.srz.es

Las páginas que Lucía va subiendo, publicadas en <https://lucia.srz.es>.

## Cómo subir una página

1. Entra en la carpeta **`paginas`** aquí arriba.
2. Pulsa **Add file → Upload files** y arrastra tu `.html`.
3. Abajo del todo, **Commit changes**.

En un par de minutos está publicado. El nombre del fichero es la dirección:
`trabajo-historia.html` se ve en `lucia.srz.es/trabajo-historia.html`.

La portada (`lucia.srz.es`) se escribe sola con la lista de todo lo que haya en
`paginas`, de lo más nuevo a lo más viejo, usando el `<title>` de cada página
como nombre. No hay que añadir el enlace a mano.

### Para empezar una página nueva

Copia [`plantilla.html`](plantilla.html), cámbiale el nombre y escribe dentro.
Trae ya lo necesario para que se vea bien en el móvil.

### Imágenes

Van en `paginas/imagenes/` y se enlazan así:

```html
<img src="/imagenes/la-foto.jpg" alt="Lo que se ve en la foto">
```

### Dos cosas que ahorran disgustos

- **Nombres de fichero** en minúsculas, sin acentos, sin eñes y sin espacios:
  `examen-de-mates.html`, no `Exámen de Mates.html`.
- **Que no falte el `<title>`**, que es lo que sale en la portada y en la
  pestaña del navegador.

### Si prefieres tu propia portada

Sube un `index.html` a `paginas/` y manda el tuyo; entonces no se genera la
lista automática.

## Para el que mantiene esto

Sitio estático sin dependencias: `build.py` copia `paginas/` a `dist/`, añade
los sueltos de la raíz (`estilo.css`, `plantilla.html`, `404.html`,
`robots.txt`), escribe el `CNAME` y genera la portada. No modifica el HTML que
haya escrito nadie.

```bash
python3 build.py         # construye dist/
python3 build.py --ver   # construye y sirve en http://localhost:8000
```

Cada push a `main` dispara `.github/workflows/deploy.yml`, que construye y
publica `dist/` en GitHub Pages. El checkout usa `fetch-depth: 0` porque las
fechas del índice salen del último commit de cada fichero.

El `robots.txt` pide a los buscadores que no indexen nada, y las páginas llevan
`<meta name="robots" content="noindex, nofollow">`. La web es pública igual
—cualquiera con la dirección la ve—, pero no sale en Google. Para cambiarlo,
quita la línea `Disallow` y el `<meta>`.
