# -*- coding: utf-8 -*-
"""
Frases Célebres - Sabiduría y Reflexión
=======================================
Aplicación web (Streamlit) para leer, visualizar y buscar dentro de una
colección de 100 reflexiones. Optimizada para pantallas de teléfono.

Ejecutar:  streamlit run app.py
"""

import re
import random
import unicodedata
import urllib.parse
import streamlit as st

# ---------------------------------------------------------------------------
# Motor de búsqueda difusa (fuzzy).
# Se usa "thefuzz" si está instalado; si no, se cae de forma automática a
# "difflib" (librería estándar de Python), de modo que la app siga
# funcionando aunque falte la dependencia opcional.
# ---------------------------------------------------------------------------
try:
    from thefuzz import fuzz

    def _ratio(a, b):
        return int(fuzz.ratio(a, b))
except Exception:  # pragma: no cover - camino de respaldo
    import difflib

    def _ratio(a, b):
        return int(difflib.SequenceMatcher(None, a, b).ratio() * 100)


# ---------------------------------------------------------------------------
# Persistencia de favoritas en el navegador (localStorage).
# Se usa el componente "streamlit-local-storage" (puro frontend, sin backend).
# Patrón correcto: se CARGA con getItem al inicio y se GUARDA con setItem desde
# un callback (nunca llamar st.rerun() tras setItem, o la escritura no llega a
# ejecutarse). Si la librería no está instalada, la app sigue funcionando y las
# favoritas duran solo la sesión actual.
# ---------------------------------------------------------------------------
try:
    from streamlit_local_storage import LocalStorage
    _LS_OK = True
except Exception:
    LocalStorage = None
    _LS_OK = False

LS_KEY = "frases_celebres_favoritas"


def _parse_favs(texto):
    """Convierte '1,2,3' en un conjunto de enteros."""
    favs = set()
    for tok in (texto or "").split(","):
        tok = tok.strip()
        if tok.isdigit():
            favs.add(int(tok))
    return favs


def _favs_a_texto(favs):
    return ",".join(str(n) for n in sorted(favs))


# ---------------------------------------------------------------------------
# BASE DE DATOS (100 reflexiones extraídas del manuscrito original).
# Estructura de cada registro: numero, fecha, texto.
# ---------------------------------------------------------------------------
REFLEXIONES = [
    {"numero": 1, "fecha": "04.01.2004", "texto": "El Discípulo de Jesús el Cristo tiene Visión, Conocicierto, Habilidad, Santidad."},
    {"numero": 2, "fecha": "28.12.03", "texto": "El Temor a Enseñar es un profundo y escondido miedo a Obedecer."},
    {"numero": 3, "fecha": "04.01.2004", "texto": "La gente orgullosa siempre quiere buscar su orgullo en el corazón de los demás."},
    {"numero": 4, "fecha": "25.01.04", "texto": "Obediencia implica Acción; la Fe es Espiritual y es dada por Dios; la Madurez Espiritual es Perfección."},
    {"numero": 5, "fecha": "01.02.03", "texto": "Yo tengo Confianza en el Señor; logren que Él la tengan en ustedes."},
    {"numero": 6, "fecha": "01.02.03", "texto": "La Profecía es la Esperanza del corazón de Dios."},
    {"numero": 7, "fecha": "01.02.03", "texto": "El hombre natural no pretende espiritualizar los negocios, más busca negociar lo Espiritual."},
    {"numero": 8, "fecha": "01.02.03", "texto": "El Espíritu no tiene color."},
    {"numero": 9, "fecha": "01.02.03", "texto": "El mundo no necesita que tú le sigas la corriente, sino que necesita que tú le saques de esa corriente."},
    {"numero": 10, "fecha": "01.02.03", "texto": "Los Dones y los Talentos de Dios deben ser Administrados en Obediencia."},
    {"numero": 11, "fecha": "09.03.03", "texto": "Todo libro que tomo para leer es bueno, provechoso y ungido cuando me lleva a buscar la Biblia."},
    {"numero": 12, "fecha": "09.03.03", "texto": "El Espíritu del Padre está donde están los Hijos."},
    {"numero": 13, "fecha": "09.03.03", "texto": "Oficios del Espíritu Santo: Dirigir, Escoger, Enseñar, Testificar, Reprender, Comunicar."},
    {"numero": 14, "fecha": "09.03.03", "texto": "Vivir en lo que se me ha Develado y, así mismo, se me dará más Develación."},
    {"numero": 15, "fecha": "09.03.03", "texto": "El dinero nos gusta porque es útil, más no necesario."},
    {"numero": 16, "fecha": "16.03.03", "texto": "No hablar de las cosas viejas, para que no resucite el hombre viejo; hablar de las cosas Nuevas que hizo el Señor en mi vida."},
    {"numero": 17, "fecha": "29.03.03", "texto": "No ofrecer promesas a Dios, ofrecerle mi vida. Nuestra ofrenda es la Santidad, Pureza; que nuestro testimonio toque a otras personas."},
    {"numero": 18, "fecha": "12.04.03", "texto": "Podemos condenar las prácticas, más no personas."},
    {"numero": 19, "fecha": "16.04.03", "texto": "La ley no perfecciona a nadie; no toda ofrenda la recibe Dios; es recibida por Dios por la Actitud de mi Corazón."},
    {"numero": 20, "fecha": "16.04.03", "texto": "El fin de la ley es Cristo."},
    {"numero": 21, "fecha": "20.04.03", "texto": "El Amor de Dios llena nuestro Corazón, porque el Espíritu Santo Habita en mí."},
    {"numero": 22, "fecha": "27.04.03", "texto": "Ofrenda Agradable al Señor Uno: con corazón limpio.Dos: en Secreto.Tres: Voluntariamente.Cuatro: Generosamente.Cinco: con Amor y por Amor."},
    {"numero": 23, "fecha": "05.05.03", "texto": "Aliado es el tiempo; el tiempo muestra todo lo que hay en el corazón."},
    {"numero": 24, "fecha": "05.05.03", "texto": "Misericordia quiero, más no sacrificio; Obediencia quiero, más no sacrificio."},
    {"numero": 25, "fecha": "05.05.03", "texto": "Un Hijo de Dios todo lo convierte en Bendición."},
    {"numero": 26, "fecha": "06.05.03", "texto": "Remanente, lo que Dios ha guardado para Él mismo."},
    {"numero": 27, "fecha": "06.05.03", "texto": "Si no cumples tus promesas, Dios te partirá las piernas."},
    {"numero": 28, "fecha": "06.05.03", "texto": "Cuando el hombre de Dios es Perdonado, se levanta en Humildad y sin altivez."},
    {"numero": 29, "fecha": "06.05.03", "texto": "El Reino de los Cielos, aquí en la tierra, es la Iglesia."},
    {"numero": 30, "fecha": "06.05.03", "texto": "Es muy fácil cumplir el tiempo, sin cumplir en el tiempo. (Aitofel)"},
    {"numero": 31, "fecha": "20.06.03", "texto": "La Obra del Señor no se detiene."},
    {"numero": 32, "fecha": "20.06.03", "texto": "Nada podemos contra la Verdad, sino por medio de la Verdad."},
    {"numero": 33, "fecha": "22.06.03", "texto": "Mi mejor Ofrenda es mi vida en Santidad."},
    {"numero": 34, "fecha": "23.06.03", "texto": "Muchas veces Dios esconde las cosas colocándolas muy cerquita."},
    {"numero": 35, "fecha": "14.09.03", "texto": "La Fe nace en mi corazón; por la Fe Agradó a Dios; la Fe es del Espíritu, quien se enseñorea de mi mente, emociones, pensamientos y Alma. La Fe es Nacer de Nuevo; por la Fe Bendecimos."},
    {"numero": 36, "fecha": "21.09.03", "texto": "Sin Identidad Espiritual no soy nadie. ¿Cómo adquiero esa Identidad? Haciéndome Hijo."},
    {"numero": 37, "fecha": "27.11.03", "texto": "¿Cómo podremos mantener la Salvación? en Fe Haciendo estas cosas no resbalaremos jamás. Salmos 15:1-5."},
    {"numero": 38, "fecha": "27.11.03", "texto": "La Salvación es igual a Obediencia. ¿Para qué me salvó Dios? Para ir en pos de las almas, para Salvar a otros. ¿Para qué nos llamó? Para anunciar a Jesús el Cristo. ¿Cuándo empezó a manifestarse mi Salvación? Cuando recibimos a Cristo en nuestro corazón. ¿Dónde está la salvación? Está en mi espíritu, en mi Obediencia."},
    {"numero": 39, "fecha": "05.09.03", "texto": "El que está en la simiente de Dios no peca. Irreprensible: persona íntegra, no tiene nada de qué ser acusado."},
    {"numero": 40, "fecha": "12.10.03", "texto": "Garra de FALOPIO: F, falsedad en la doctrina; A, arrogancia; L, liviandad; O, ostentación de una falsa salvación; P, perversión de lo recto; I, ignorancia espiritual; O, oscuridad."},
    {"numero": 41, "fecha": "12.10.03", "texto": "El encargo de Dioses: no retroceder en la Fe, Valorar lo que he recibido."},
    {"numero": 42, "fecha": "15.10.03", "texto": "Salmo 23:1: el Señor es mi Pastor, no desfalleceré."},
    {"numero": 43, "fecha": "19.10.03", "texto": "Cristianesco: aquel que quiere imitar lo que hacen los Cristianizados."},
    {"numero": 44, "fecha": "19.10.03", "texto": "Apostasía: volver atrás, retroceder en la Fe."},
    {"numero": 45, "fecha": "05.11.03", "texto": "Iglesia, somos todos aquellos que nos congregamos en el Nombre de Jesús el Cristo en cualquier lugar. Yo soy parte de la Iglesia."},
    {"numero": 46, "fecha": "16.11.03", "texto": "Denominación no es del pueblo de Dios; de “no”, no es; nación, pueblo."},
    {"numero": 47, "fecha": "19.11.03", "texto": "Mi más grande necesidad. Mi mayor necesidad es Jesús el Cristo; si lo tengo a Él, todo lo demás viene por añadidura."},
    {"numero": 48, "fecha": "26.11.03", "texto": "Primero el Obrero, después la Obra. Palabra más importante: primeramente, el Caminar con El Señor."},
    {"numero": 49, "fecha": "03.12.03", "texto": "Todo mal que te acontece cuando verdaderamente has buscado a Dios es de parte de Dios."},
    {"numero": 50, "fecha": "03.12.03", "texto": "Cobertura es saber realmente que la Sangre de Cristo me Cubre."},
    {"numero": 51, "fecha": "05.12.03", "texto": "Revelar: Jesús El Cristo no se revela por cuanto Él estaba desde antes. Develar: por cuanto tenían un velo en la ley y al quitar ese velo se descubre."},
    {"numero": 52, "fecha": "29.12.03", "texto": "Importancia de Congregarnos como Iglesia de Jesús El Cristo. Tendremos: Crecicierto Espiritual, Unidad en El Espíritu, no dar lugar al enemigo, alabanza para Dios."},
    {"numero": 53, "fecha": "28.12.03", "texto": "La Salvación es Profética."},
    {"numero": 54, "fecha": "04.01.04", "texto": "La obra Evangelizadora se hace en el terreno del diablo, no dentro de las frías paredes de una congregación."},
    {"numero": 55, "fecha": "04.01.04", "texto": "La Iglesia estira su pie hacia el mundo, no para caminar en él, sino para conquistar a los que están en él."},
    {"numero": 56, "fecha": "27.07.04", "texto": "Encargo de Dios para la Iglesia: no avergonzarse del Evangelio, sufrir por el Evangelio, defender el Evangelio, Perseverar en el Evangelio, Predicar el Evangelio."},
    {"numero": 57, "fecha": "02.02.03", "texto": "La Profecía es la Esperanza del Corazón de Dios,"},
    {"numero": 58, "fecha": "02.02.03", "texto": "El mundo no necesita que tú le sigas la corriente, sino que necesita que tú le saques de esa corriente."},
    {"numero": 59, "fecha": "02.02.03", "texto": "Los Dones y las Vocaciones de Dios deben de ser Administradas en Obediencia,"},
    {"numero": 60, "fecha": "02.02.03", "texto": "Yo tengo confianza en el Señor; logren que Él la tengan ustedes,"},
    {"numero": 61, "fecha": "09.03.03", "texto": "Todo libro que tomo para leerme es bueno, provechoso y ungido cuando me lleva a buscar a Dios,"},
    {"numero": 62, "fecha": "09.09.03", "texto": "El Espíritu del Padre está donde están los Hijos,"},
    {"numero": 63, "fecha": "14.03.03", "texto": "La plata nos gusta porque es útil, más no necesaria,"},
    {"numero": 64, "fecha": "23.03.03", "texto": "No hablar de las cosas viejas para que no resucite el hombre viejo; hablar de las cosas nuevas que hizo el Señor en mi vida,"},
    {"numero": 65, "fecha": "21.05.03", "texto": "Es muy fácil cumplir el tiempo sin cumplir en el tiempo,"},
    {"numero": 66, "fecha": "06.09.03", "texto": "Un buen Obrero es el que hace que más alcance las metas."},
    {"numero": 67, "fecha": "17.08.03", "texto": "La fe nace en mi corazón; por la fe agrado a Dios, la fe es del Espíritu. La fe es nacer de nuevo; por la fe Bendecimos."},
    {"numero": 68, "fecha": "17.08.03", "texto": "La Palabra que yo hablo o leo también me escucha porque es de doble filo, es Viva y Eficaz."},
    {"numero": 69, "fecha": "17.08.03", "texto": "Es mejor tener y no necesitar que necesitar y no tener."},
    {"numero": 70, "fecha": "31.03.04", "texto": "Hay momentos en que la Semilla, la Palabra, se sale de la tierra, el corazón."},
    {"numero": 71, "fecha": "10.04.04", "texto": "Mi mejor ofrenda a Dios es mi vida en Santidad."},
    {"numero": 72, "fecha": "10.04.04", "texto": "Los métodos son del hombre y me separan de Dios, y los Principios son de Dios para vida Eterna."},
    {"numero": 73, "fecha": "10.04.04", "texto": "Lo bueno es enemigo de lo Mejor."},
    {"numero": 74, "fecha": "10.04.04", "texto": "Enseñamos con el vivir, no con el hablar, pues la Humildad se ve, no se escucha."},
    {"numero": 75, "fecha": "02.05.04", "texto": "El saber que tenemos una Salvación en Esperanza será lo que nos va a Sostener."},
    {"numero": 76, "fecha": "02.05.04", "texto": "El poder del Cristianizado está en la Oración."},
    {"numero": 77, "fecha": "02.05.04", "texto": "Cuando llegue ese Bendito, Sublime y Glorioso momento en que entiendas que, por Dios, que por Jesús El Cristo vives, entonces solo querrás Vivir para Él."},
    {"numero": 78, "fecha": "02.05.04", "texto": "Solo podré Permanecer en El Señor si Él Permanece en mí, pero el Señor solo Permanecerá en mí si yo Permanezco en Él. 1 Juan 4:15-16."},
    {"numero": 79, "fecha": "02.05.04", "texto": "Vivir en lo que se me ha Develado, y así mismo se me dará más."},
    {"numero": 80, "fecha": "02.05.04", "texto": "Tu Prosperidad Espiritual no se verá en lo que vistes o en lo que comes, sino en tu mirar."},
    {"numero": 81, "fecha": "02.05.04", "texto": "Sufres más de lo que quieres porque no sufres como Dios quiere."},
    {"numero": 82, "fecha": "02.05.04", "texto": "Tres formas de desobedecer a Dios: 1. haciendo lo malo; 2. dejando de hacer lo bueno; 3. haciendo lo excelente quitando la gloria a Dios."},
    {"numero": 83, "fecha": "02.05.04", "texto": "Contra el enemigo solo sirve la Santidad y la Presencia de Dios."},
    {"numero": 84, "fecha": "02.05.04", "texto": "La Obra de Dios no necesita dinero, no depende de él. La Obra de Dios necesita hombres y mujeres Consagrados."},
    {"numero": 85, "fecha": "03.01.04", "texto": "En la juventud se quiere volar sin saber que, al ser adulto, solo se aprende a caminar, y cuando está entrado en edad se aprende a reposar (Salmos 46:10)."},
    {"numero": 86, "fecha": "", "texto": "Acepto que me he equivocado, pero no acepto quedarme en ello."},
    {"numero": 87, "fecha": "2004", "texto": "La única manera que no volvamos al pasado, hablar del pasado, es que no vuelvan al pasado."},
    {"numero": 88, "fecha": "2004", "texto": "No es lo mismo darse a Dios por vencido que darse a Dios para Vencer."},
    {"numero": 89, "fecha": "", "texto": "Tú debes meterte en la Escritura para que la Escritura se meta en ti."},
    {"numero": 90, "fecha": "", "texto": "Si hoy nutres tu espíritu con la Palabra de Dios, mañana no andarás en debilidad."},
    {"numero": 91, "fecha": "24.01.05", "texto": "Las Promesas son Recompensas por guardar los Principios."},
    {"numero": 92, "fecha": "24.01.05", "texto": "Cuando uno es Humilde se Humilla, y cuando uno se Humilla puede llegar a ser Humilde."},
    {"numero": 93, "fecha": "24.01.05", "texto": "Responsabilidad: es Hacer las cosas, no porque Dios las manda, sino Como Dios las manda."},
    {"numero": 94, "fecha": "24.01.05", "texto": "Si luego de haber recibido una Enseñanza o Predicación no amerita, o no me mueve a Escudriñar la Escritura, es porque tú eres del diablo o la predicación o enseñanza no era de Dios."},
    {"numero": 95, "fecha": "24.01.05", "texto": "Dios es El Dios del orden, porque no hay otro Dios."},
    {"numero": 96, "fecha": "24.01.05", "texto": "Muchas veces la Verdad de Cristo puede enceguecerte."},
    {"numero": 97, "fecha": "24.01.05", "texto": "Muchas veces, para ayudar a un Hermano a Caminar en Cristo, debo quitar a otro."},
    {"numero": 98, "fecha": "", "texto": "Quiero la mano de Dios, así sea para golpearme."},
    {"numero": 99, "fecha": "", "texto": "Es mejor caer en las manos de Dios que en las manos del hombre."},
    {"numero": 100, "fecha": "24.01.05", "texto": "Me apoyaré en alguien siempre y cuando ese alguien se apoye en la Palabra de Dios."},
]


# ---------------------------------------------------------------------------
# Utilidades de texto
# ---------------------------------------------------------------------------
def normaliza(texto):
    """Minúsculas y sin acentos, para comparar de forma tolerante."""
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto


SIN_FECHA = "Sin fecha"


def anio_de(fecha):
    """Devuelve el año (str) de una fecha del manuscrito, o SIN_FECHA."""
    if not fecha:
        return SIN_FECHA
    partes = re.split(r"[.\-/]", fecha)
    y = partes[-1].strip()
    if len(y) == 2:          # '03' -> '2003', '04' -> '2004'
        y = "20" + y
    return y if y.isdigit() else SIN_FECHA


UMBRAL_PALABRA = 80   # % de similitud para considerar dos palabras "parecidas"
UMBRAL_FRASE = 62     # % mínimo para que una reflexión aparezca en resultados


def palabra_coincide(palabra_texto, palabra_query):
    """¿Se parece 'palabra_texto' a 'palabra_query'? (substring o fuzzy)."""
    pt, pq = normaliza(palabra_texto), normaliza(palabra_query)
    if len(pq) < 2:
        return pt == pq
    if pq in pt or pt in pq:
        return True
    return _ratio(pt, pq) >= UMBRAL_PALABRA


def puntua(query, texto):
    """Devuelve una puntuación 0-100 de qué tan bien 'query' casa con 'texto'."""
    qn, tn = normaliza(query), normaliza(texto)
    if not qn:
        return 100
    if qn in tn:                      # coincidencia exacta de la frase completa
        return 100

    q_words = qn.split()
    t_words = tn.split()
    if not q_words or not t_words:
        return _ratio(qn, tn)

    # Para cada palabra buscada tomamos su mejor coincidencia dentro del texto.
    puntajes = []
    for qw in q_words:
        mejor = max((_ratio(qw, tw) for tw in t_words), default=0)
        if any((qw in tw) or (tw in qw) for tw in t_words):
            mejor = max(mejor, 92)
        puntajes.append(mejor)

    por_palabra = sum(puntajes) / len(puntajes)
    return int(max(por_palabra, _ratio(qn, tn)))


def _escape(texto):
    return (
        texto.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def resalta(texto, query):
    """Envuelve en <mark> las palabras del texto que coinciden con la búsqueda."""
    if not query.strip():
        return _escape(texto)

    q_words = [w for w in query.split() if w.strip()]
    # Dividimos conservando separadores (espacios, signos de puntuación).
    piezas = re.split(r"(\w+)", texto, flags=re.UNICODE)
    salida = []
    for pieza in piezas:
        if pieza and re.match(r"\w+$", pieza, flags=re.UNICODE):
            if any(palabra_coincide(pieza, qw) for qw in q_words):
                salida.append("<mark>" + _escape(pieza) + "</mark>")
            else:
                salida.append(_escape(pieza))
        else:
            salida.append(_escape(pieza))
    return "".join(salida)


# ---------------------------------------------------------------------------
# Configuración de la página (móvil primero)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Frases Célebres",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Estado de sesión --------------------------------------------------------
if "azar" not in st.session_state:
    st.session_state.azar = None
if "favoritos" not in st.session_state:
    st.session_state.favoritos = set()
if "_fav_touched" not in st.session_state:
    st.session_state._fav_touched = False   # ¿el usuario ya tocó una favorita?
if "_fav_pendiente" not in st.session_state:
    st.session_state._fav_pendiente = None  # texto por guardar en localStorage

_localS = LocalStorage() if _LS_OK else None

# CARGA: mientras el usuario no interactúe, las favoritas reflejan el navegador.
# Así, al abrir la app se recuperan las guardadas (getItem puede tardar un
# refresco en responder; la librería re-ejecuta el script cuando el valor llega).
if _localS is not None and not st.session_state._fav_touched:
    guardadas = _localS.getItem(LS_KEY)
    # getItem puede devolver un valor transitorio (int/None) mientras el
    # componente carga; solo se adopta cuando llega un texto real.
    if isinstance(guardadas, str):
        st.session_state.favoritos = _parse_favs(guardadas)


def alternar_favorita(num):
    """Callback del botón ⭐: alterna la favorita y programa su guardado."""
    favs = set(st.session_state.favoritos)
    if num in favs:
        favs.discard(num)
    else:
        favs.add(num)
    st.session_state.favoritos = favs
    st.session_state._fav_touched = True
    # "none" representa "sin favoritas": la librería no persiste cadenas vacías,
    # y _parse_favs("none") devuelve un conjunto vacío al recargar.
    st.session_state._fav_pendiente = _favs_a_texto(favs) or "none"


# GUARDADO: si hay un cambio pendiente, se persiste en el navegador. Se hace en
# el flujo normal (no en el callback) para que el componente pueda ejecutarse.
if _localS is not None and st.session_state._fav_pendiente is not None:
    _localS.setItem(LS_KEY, st.session_state._fav_pendiente, key="ls_fav_set")
    st.session_state._fav_pendiente = None

# --- Controles superiores ---------------------------------------------------
anios = sorted({anio_de(r["fecha"]) for r in REFLEXIONES},
               key=lambda a: (a == SIN_FECHA, a))
opciones_anio = ["Todos"] + anios

col_a, col_b = st.columns([2, 1])
with col_a:
    anio_sel = st.selectbox("📅 Filtrar por año", opciones_anio, index=0)
with col_b:
    oscuro = st.toggle("🌙 Oscuro", value=False)

col_c, col_d = st.columns([2, 1])
with col_c:
    if st.button("🎲 Reflexión al azar", use_container_width=True):
        st.session_state.azar = random.choice(REFLEXIONES)["numero"]
with col_d:
    solo_fav = st.toggle("⭐ Favoritas", value=False)

# --- Paleta según el tema ---------------------------------------------------
if oscuro:
    C = {
        "bg": "#15131f", "card": "#211d31", "border": "#332d4a",
        "text": "#ece9f7", "titulo": "#efeaff", "sub": "#a99fce",
        "num_bg": "#8f74ff", "num_fg": "#ffffff", "fecha": "#9a92b5",
        "mark_bg": "#7c5cff", "mark_fg": "#ffffff",
        "input_bg": "#211d31", "input_fg": "#ece9f7", "muted": "#a99fce",
    }
else:
    C = {
        "bg": "#faf9fe", "card": "#ffffff", "border": "#ece9f5",
        "text": "#2b2b3a", "titulo": "#2c2350", "sub": "#7a7398",
        "num_bg": "#7c5cff", "num_fg": "#ffffff", "fecha": "#9a92b5",
        "mark_bg": "#fff3a3", "mark_fg": "#3a2f00",
        "input_bg": "#ffffff", "input_fg": "#2b2b3a", "muted": "#7a7398",
    }

st.markdown(
    """
    <style>
      .stApp { background: %(bg)s; }
      .block-container { padding-top: 1.1rem; padding-bottom: 3rem;
                         max-width: 640px; }
      header[data-testid="stHeader"] { background: transparent; }

      .app-titulo { text-align:center; margin: 0 0 .15rem 0;
                    font-size: 1.6rem; font-weight: 800; color: %(titulo)s; }
      .app-subtitulo { text-align:center; margin:0 0 1rem 0;
                       color:%(sub)s; font-size:.95rem; letter-spacing:.5px; }

      .card { background: %(card)s; border: 1px solid %(border)s;
              border-left: 5px solid %(num_bg)s;
              border-radius: 16px; padding: 16px 18px; margin: 12px 0 4px 0;
              box-shadow: 0 4px 14px rgba(60,40,120,.06); }
      .card-top { display:flex; justify-content:space-between;
                  align-items:center; margin-bottom:.5rem; }
      .card-num { background:%(num_bg)s; color:%(num_fg)s; font-weight:700;
                  font-size:.78rem; padding:3px 11px; border-radius:999px; }
      .card-fecha { color:%(fecha)s; font-size:.78rem; }
      .card-texto { color:%(text)s; font-size:1.06rem; line-height:1.55; }

      mark { background: %(mark_bg)s; color:%(mark_fg)s; padding:0 2px;
             border-radius:4px; }

      .contador { color:%(muted)s; font-size:.88rem; margin:.2rem 0 .2rem 2px; }
      .vacio { text-align:center; color:%(muted)s; padding: 2.5rem 1rem; }

      div[data-testid="stTextInput"] input { font-size:1.05rem;
             padding:.65rem .8rem; border-radius:12px;
             background:%(input_bg)s; color:%(input_fg)s; }

      /* Etiquetas y expander legibles en ambos temas */
      label, .stSelectbox label, .stToggle label { color:%(sub)s !important; }
      details summary, .streamlit-expanderHeader { color:%(sub)s !important; }
    </style>
    """ % C,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-titulo">📖 Frases Célebres</div>',
            unsafe_allow_html=True)
st.markdown('<div class="app-subtitulo">Sabiduría y Reflexión · 100 reflexiones</div>',
            unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Barra de búsqueda (con lupa)
# ---------------------------------------------------------------------------
query = st.text_input(
    label="Buscar",
    value="",
    placeholder="🔍  Escribe una palabra o frase…",
    label_visibility="collapsed",
)

# ---------------------------------------------------------------------------
# Reflexión al azar (banner destacado)
# ---------------------------------------------------------------------------
def dibuja_tarjeta(r, query, destacada=False):
    """Dibuja una tarjeta + botón de favorita + opciones de compartir."""
    num = r["numero"]
    es_fav = num in st.session_state.favoritos
    fecha = r["fecha"] if r["fecha"] else "s/f"
    texto_html = resalta(r["texto"], query)
    estrella = "⭐ " if es_fav else ""
    borde = "border:2px dashed %s;" % C["num_bg"] if destacada else ""
    st.markdown(
        '<div class="card" style="' + borde + '">'
        '<div class="card-top">'
        '<span class="card-num">' + estrella + 'Reflexión ' + str(num) + '</span>'
        '<span class="card-fecha">📅 ' + fecha + '</span>'
        '</div>'
        '<div class="card-texto">' + texto_html + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    col_f, col_e = st.columns([1.1, 3])
    with col_f:
        etiqueta = "⭐ Quitar" if es_fav else "☆ Favorita"
        st.button(etiqueta, key="fav_%d_%s" % (num, destacada),
                  use_container_width=True,
                  on_click=alternar_favorita, args=(num,))
    with col_e:
        texto_plano = '"' + r["texto"] + '"\n— Reflexión ' + str(num)
        if r["fecha"]:
            texto_plano += " (" + r["fecha"] + ")"
        with st.expander("📋 Copiar / Compartir"):
            st.caption("Usa el icono de copiar (arriba a la derecha del recuadro):")
            st.code(texto_plano, language=None)
            wa = "https://wa.me/?text=" + urllib.parse.quote(texto_plano)
            tg = "https://t.me/share/url?url=&text=" + urllib.parse.quote(texto_plano)
            st.markdown(
                "[💬 WhatsApp](%s) &nbsp;·&nbsp; [✈️ Telegram](%s)" % (wa, tg)
            )


if st.session_state.azar is not None:
    r_azar = next((x for x in REFLEXIONES
                   if x["numero"] == st.session_state.azar), None)
    if r_azar:
        st.markdown('<div class="contador">🎲 Reflexión al azar</div>',
                    unsafe_allow_html=True)
        dibuja_tarjeta(r_azar, "", destacada=True)
        if st.button("✖ Ocultar al azar"):
            st.session_state.azar = None
            st.rerun()
        st.markdown("<hr style='opacity:.15'>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Filtrado: favoritas -> año -> búsqueda -> orden por relevancia
# ---------------------------------------------------------------------------
base = REFLEXIONES
if solo_fav:
    base = [r for r in base if r["numero"] in st.session_state.favoritos]
if anio_sel != "Todos":
    base = [r for r in base if anio_de(r["fecha"]) == anio_sel]

if query.strip():
    resultados = []
    for r in base:
        score = puntua(query, r["texto"])
        if score >= UMBRAL_FRASE:
            resultados.append((score, r))
    resultados.sort(key=lambda x: (-x[0], x[1]["numero"]))
    lista = [r for _, r in resultados]
    detalle = ' para <b>"' + _escape(query) + '"</b>'
else:
    lista = base
    detalle = "" if anio_sel == "Todos" else " del año " + anio_sel

st.markdown(
    '<div class="contador">🔎 ' + str(len(lista))
    + ' reflexión(es)' + detalle + '</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Render de las tarjetas
# ---------------------------------------------------------------------------
if not lista:
    if solo_fav and not st.session_state.favoritos:
        mensaje = ("☆ Aún no tienes favoritas.<br>"
                   "Marca reflexiones con el botón <b>☆ Favorita</b>.")
    else:
        mensaje = ("😕 No se encontraron reflexiones parecidas.<br>"
                   "Intenta con otra palabra u otro año.")
    st.markdown('<div class="vacio">' + mensaje + '</div>',
                unsafe_allow_html=True)
else:
    for r in lista:
        dibuja_tarjeta(r, query)
