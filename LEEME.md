# 📖 Frases Célebres — Sabiduría y Reflexión

Aplicación web (hecha con **Streamlit**, en Python) para **leer, buscar y compartir**
una colección de 100 reflexiones. Está optimizada para verse en el **celular**.

- Búsqueda con **lupa** y **tolerancia a errores** (fuzzy): encuentra frases aunque
  escribas con faltas de ortografía o sin acentos.
- **Resaltado** de las palabras encontradas.
- **Filtro por año** y **modo oscuro** 🌙.
- **Copiar / compartir** cada frase por WhatsApp o Telegram.
- **Favoritas** ⭐ que se **guardan en el navegador** (siguen ahí aunque cierres
  y vuelvas a abrir la app en el mismo dispositivo).

---

## 📁 Archivos del proyecto

| Archivo | Para qué sirve |
|---|---|
| `app.py` | La aplicación completa **y las 100 frases**. Aquí editas el contenido. |
| `requirements.txt` | Lista de librerías que la app necesita. |
| `LEEME.md` | Este manual. |

> Todo lo que tienes que tocar para **agregar o corregir frases** está en `app.py`.

---

## ✍️ 1. Cómo AGREGAR o CORREGIR frases

Las frases viven dentro de `app.py`, en una lista llamada **`REFLEXIONES`**.
Cada frase es una línea con este formato (los 3 campos siempre entre llaves `{ }`):

```python
{"numero": 5, "fecha": "01.02.03", "texto": "Yo tengo Confianza en el Señor; logren que Él la tengan en ustedes."},
```

- **numero** → el número de la reflexión (un número, sin comillas).
- **fecha** → la fecha, **entre comillas**. Si no tiene fecha, déjala vacía: `""`.
- **texto** → la frase, **entre comillas**.

### ➕ Agregar una frase nueva
1. Abre `app.py` con cualquier editor de texto (el Bloc de notas sirve, pero es
   mejor **VS Code** o **Notepad++**).
2. Busca la lista `REFLEXIONES = [`.
3. Ve hasta la **última frase** (la número 100) y, **después de su llave y la coma**,
   agrega tu línea nueva. Ejemplo:

```python
    {"numero": 100, "fecha": "24.01.05", "texto": "Me apoyaré en alguien..."},
    {"numero": 101, "fecha": "01.06.26", "texto": "Aquí va tu nueva reflexión."},
]
```
4. Guarda el archivo. ¡Listo!

### ✏️ Corregir una frase existente
1. Busca la frase por su número (por ejemplo `"numero": 22`).
2. Cambia lo que necesites dentro de las comillas de `"texto"` o `"fecha"`.
3. Guarda.

### ⚠️ Reglas de oro (para que no se rompa)
- Cada línea de frase **termina en coma** `,`.
- El texto va **entre comillas dobles** `"`. Si tu frase **contiene** una comilla
  doble, escríbela como `\"`. Ejemplo:
  `"texto": "Él dijo \"sí\" con firmeza."`.
  (Las tildes, ¿?, ¡!, ñ, etc. **no** dan problema, se escriben normal.)
- No borres los corchetes `[` del inicio ni `]` del final de la lista.
- Si tras editar la app muestra un error rojo, casi siempre es **una coma que falta**
  o **una comilla sin cerrar** en la línea que acabas de tocar.

> **Consejo:** si vas a hacer muchos cambios, guarda antes una copia de `app.py`
> (por ejemplo `app_respaldo.py`) por si acaso.

---

## 💻 2. Cómo PROBARLA en tu computadora (instalación local)

Solo se hace **una vez**.

1. Instala **Python 3** desde https://www.python.org/downloads/
   (en Windows, marca la casilla **“Add Python to PATH”** durante la instalación).
2. Descarga/copia esta carpeta del proyecto a tu PC.
3. Abre una terminal **dentro de la carpeta** del proyecto:
   - Windows: abre la carpeta, escribe `cmd` en la barra de direcciones y Enter.
4. Instala las librerías (una sola vez):

```bash
pip install -r requirements.txt
```

5. Arranca la app:

```bash
streamlit run app.py
```

Se abrirá sola en tu navegador en `http://localhost:8501`.
Cada vez que edites y guardes `app.py`, la app se **actualiza sola**
(arriba a la derecha aparece “Rerun / Always rerun”).

Para **detenerla**: en la terminal presiona `Ctrl + C`.

---

## ☁️ 3. Cómo SUBIRLA a internet (para verla desde el celular como app) — GRATIS

La forma más fácil y gratuita es **Streamlit Community Cloud**. Te da un enlace
público (ej. `https://tuapp.streamlit.app`) que puedes abrir en cualquier celular.

### Paso a paso
1. **Crea una cuenta gratis en GitHub**: https://github.com/signup
2. **Crea un repositorio nuevo** (botón *New*), ponle un nombre (ej. `frases-celebres`).
3. **Sube los archivos** del proyecto a ese repositorio
   (`app.py`, `requirements.txt`, `LEEME.md`).
   - En GitHub puedes usar el botón **“Add file → Upload files”** y arrastrarlos.
4. Entra a **https://share.streamlit.io** e inicia sesión con tu cuenta de GitHub.
5. Botón **“New app”** → elige tu repositorio, la rama `main` y el archivo `app.py`.
6. Presiona **Deploy**. Espera 1–2 minutos.
7. ¡Listo! Te queda un enlace público. **Ese enlace es tu app.**

> Cada vez que **actualices `app.py` en GitHub** (agregando o corrigiendo frases),
> la app en línea se **actualiza sola** en unos segundos.

---

## 📱 4. Cómo verla como una APP en el celular

Con el enlace público del paso anterior:

**En Android (Chrome):**
1. Abre el enlace en Chrome.
2. Toca el menú **⋮** (arriba a la derecha).
3. Elige **“Agregar a la pantalla de inicio”**.
4. Aparecerá un ícono como si fuera una app. Al abrirlo se ve a pantalla completa.

**En iPhone (Safari):**
1. Abre el enlace en Safari.
2. Toca el botón **Compartir** (el cuadro con la flecha ↑).
3. Elige **“Agregar a inicio”**.

---

## 🔗 5. Cómo COMPARTIRLA

- **Por enlace:** simplemente envía la dirección `https://...streamlit.app` por
  WhatsApp, correo, etc.
- **Con código QR:** entra a https://www.qr-code-generator.com, pega tu enlace y
  descarga el QR. Quien lo escanee con la cámara abre la app al instante.
- **Compartir una frase suelta:** dentro de la app, abre **“📋 Copiar / Compartir”**
  debajo de cada tarjeta y usa los botones de **WhatsApp** o **Telegram**.

---

## ⭐ Nota sobre las Favoritas

Las favoritas se guardan en el **localStorage del navegador** (mediante la librería
`streamlit-local-storage`). Esto significa que:

- Persisten aunque **recargues** la página o **cierres y vuelvas a abrir** la app.
- Se guardan **por dispositivo y por navegador**: las que marques en el celular no
  aparecen en la computadora (y viceversa), porque cada navegador tiene su propio
  almacenamiento.
- Si el usuario **borra los datos de navegación** del sitio, se pierden.

Marca/desmarca con el botón **☆ Favorita / ⭐ Quitar** de cada tarjeta, y usa el
interruptor **⭐ Favoritas** para ver solo las marcadas.

---

## 🆘 Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `streamlit no se reconoce como comando` | Falta instalar: `pip install -r requirements.txt`. |
| La app muestra un error rojo tras editar | Revisa la última línea que tocaste: coma o comilla faltante. |
| No aparece una frase que agregué | Verifica que la línea termina en coma y está **dentro** de los corchetes `[ ]`. |
| La búsqueda no encuentra algo | Prueba con menos palabras; tolera errores pero no frases muy largas. |

---

*Hecho con ❤️ y Streamlit.*
