#!/usr/bin/env python3
"""
audita_texto_base.py — el núcleo compartido de los auditores de prosa

Material de Estadística Espacial 2026-II (20929). T0.5.

POR QUÉ UN NÚCLEO Y NO DIEZ COPIAS.

En Diseño de Experimentos cada capítulo tiene su `audita_texto_capN.py`
autónomo, de 370 a 677 líneas, nacidos de copiar el anterior. Salió caro:
**cinco de ellos retiraban las fórmulas de KaTeX ANTES de extraer los
números**, de modo que ninguna cifra escrita dentro de una fórmula se
auditaba jamás. Entre el 18 % y el 29 % de los decimales de cada capítulo
publicado vivían en ese punto ciego, y solo se descubrió al construir el
arnés de inyección del sexto. Un fallo en el núcleo, replicado por
copia-pega, se convierte en cinco fallos que hay que encontrar cinco
veces.

Aquí la maquinaria vive una vez. Cada capítulo aporta un archivo corto
que declara **qué** hay que comprobar, no **cómo**:

    from audita_texto_base import Auditor
    a = Auditor(capitulo="capitulo-1-....html", var_entorno="CAP1_HTML",
                jsons=["cap1_datos.json", "cap1_soluciones.json"],
                estructurales={...})
    a.cifras(); a.temario([...]); a.fuentes([...])
    a.accesibilidad(); a.geomapas(); a.enlaces(); a.codificacion()
    a.coherencia(cadenas=[...], ordenes=[...]); a.peso()
    sys.exit(a.cierre())

QUÉ MIRA CADA COMPROBACIÓN, Y POR QUÉ NINGUNA SOBRA

  · `cifras`      — las cifras que el AUTOR escribió en la prosa, que es
                    donde no mira ni el precálculo ni `verifica_bloques.py`.
                    **Incluye las de dentro de KaTeX.**
  · `temario`     — que el capítulo cubra lo que promete.
  · `fuentes`     — que las citas sigan ahí.
  · `accesibilidad` — lienzos, desplegables, quiz, pestañas, tablas.
  · `geomapas`    — familia NUEVA de este curso: los cortes de clase, la
                    leyenda y la geometría de un `.geomapa` viven en JSON
                    dentro del `<script>`, donde el auditor de prosa no
                    entra. Es un punto ciego que DOE no tenía, y ya se
                    cobró una pieza en T0.3: `dibuja()` repintaba el
                    lienzo y no la leyenda, así que **el mapa cambiaba y
                    los rótulos mentían**, con el componente pareciendo
                    perfecto.
  · `codificacion` — familia NUEVA: bytes crudos `<c3><b3>`. Encontrado
                    en T0.5 en un JSON ya publicado de T0.4. `jsonlite`
                    los escribe sin fallar cuando R arranca fuera de
                    UTF-8. Ver `utf8.R`.
  · `enlaces`     — que ningún enlace local apunte al vacío.
  · `coherencia`  — que las tildes y los símbolos lleguen enteros.

EL PUNTO CIEGO QUE SE HEREDA, MEDIDO Y NO DISIMULADO

`indexa_comparaciones` mete en el conjunto de conocidos las razones y los
excesos porcentuales entre cifras publicadas. Sin eso habría cientos de
falsos positivos —el texto compara todo el rato— pero el conjunto se
infla, y una cifra inventada de pocos decimales cae dentro por azar.
`mide_punto_ciego.py` lo cuantifica sobre ESTE material. La consecuencia
operativa, decidida en T0.5: **toda cifra de la que el texto argumenta se
publica con CINCO decimales**. Es lo que hace que la garantía sea real en
vez de estadística.
"""
from __future__ import annotations

import html as html_mod
import itertools
import json
import os
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
# `Htmls_Espacial/` mientras se escribe; `sitio/estadistica-espacial/`
# cuando la Fase 7 publique.
CARPETAS = [RAIZ / "sitio" / "estadistica-espacial", RAIZ / "Htmls_Espacial"]

# LAS DOS FORMAS EN QUE UNA TILDE SOBREVIVE ROTA A UN GENERADOR.
#
# `<c3><b3>` es la de T0.5: `jsonlite` escribiendo los BYTES crudos del
# UTF-8 cuando R arranca con LC_CTYPE=C. Ver A.10 y `utf8.R`.
#
# `<U+00E9>` es la otra, y la encontró T3.3 con los capítulos 2 y 3 ya
# publicados. Es la notación con que R imprime un carácter que su regional
# no sabe representar, y `jsonlite` la escribe igual de callada. **No la
# cazaba nada**: el patrón de arriba exige dos dígitos en MINÚSCULA, y
# aquí hay una `U`, un `+` y cuatro en mayúscula.
#
# Y es la peor de las dos, porque no se ve. `<c3><b3>` llega al navegador
# como texto y salta a la vista; `<U+00E1>` tiene forma de ETIQUETA, así
# que el analizador de HTML se lo traga entero y la letra **desaparece**:
# la tabla del módulo 2 del capítulo 3 se leía «Bogot, D.C.», «Medelln»,
# «Atlntico», «Bolvar», «Ccuta». Ni un error en consola, ni un carácter
# raro; solo palabras a las que les falta una letra. Un capítulo puede
# publicarse así y dar 130/0, que es exactamente lo que pasó.
MOJIBAKE_RE = re.compile(r"<[0-9a-f]{2}>|<U\+[0-9A-Fa-f]{4,6}>")

# El tope de peso de un capítulo, y qué es de verdad.
#
# NO es un presupuesto de contenido. Empezó en 550 KB y se fue subiendo a
# 560 y a 680 cada vez que un capítulo chocaba con él —una marca de agua
# levantada bajo presión, no un número diseñado—, y en T1.1 llegó a decidir
# el material: se iban a recortar comentarios del código para ganar 1,3 KB.
# Un capítulo es un HTML autocontenido que un estudiante descarga una vez;
# medio megabyte no es un problema para nadie, y los tres CDN que carga
# pesan más que él. Decisión de Javier del 2026-08-06: manda el contenido.
#
# Lo que la comprobación SÍ hace, y por eso no se retira, es dar la alarma
# ante un ensamblado desbocado: en T0.5 el ensamblador escribió un archivo
# más grande que la plantilla, con el motor mutilado, e informó «limpio».
#
# El margen no es libre, y conviene saberlo antes de volver a tocar este
# número: `prueba_texto.py` tumba la comprobación inyectando +312 KB de
# comentario, así que el tope tiene que quedar **por encima del tamaño
# actual y por debajo de tamaño + 312 KB** o el arnés se queda ciego. Esa
# es la cota que hace que 700 no sea arbitrario —el capítulo más gordo, el
# 3, va por 622— y es el propio arnés quien la vigila: subirlo de más lo
# pone rojo. El fixture de demostración conserva su tope aparte, más bajo,
# porque su archivo es la mitad.
TOPE_KB = 700.0


def busca_capitulo(nombre: str) -> pathlib.Path:
    for d in CARPETAS:
        p = d / nombre
        if p.exists():
            return p
    sys.exit(f"PARADO: no encuentro {nombre} en {[str(d) for d in CARPETAS]}")


class Auditor:
    def __init__(self, capitulo: str, var_entorno: str, jsons: list[str],
                 estructurales: set[str] | None = None,
                 presupuesto_geomapa_kb: float = 120.0,
                 json_mapas: str | None = None):
        """`json_mapas` es el JSON de geometría del capítulo, y va APARTE.

        Los cortes de clase que el HTML incrusta salen de ahí y no del JSON
        de cifras, así que sin este parámetro la comprobación «cada corte
        está en el precálculo» no podía pasar nunca — daba MAL sobre dos
        mapas correctos. Pero el archivo de geometría no puede entrar por
        `jsons`: trae decenas de miles de coordenadas cuantizadas, y
        meterlas en el índice de cifras conocidas convertiría casi
        cualquier número de cuatro dígitos de la prosa en «respaldado».
        Se indexan **solo los cortes**, y solo los usa `geomapas()`.
        """
        # `prueba_texto.py` apunta la variable de entorno a una COPIA con
        # defectos inyectados. El capítulo publicado no se toca nunca.
        #
        # La carpeta CANÓNICA se guarda aparte de la ruta que se lee: los
        # enlaces relativos hay que resolverlos donde el capítulo vive de
        # verdad, no donde esté la copia. Con la copia en un temporal,
        # resolverlos contra su padre daba «2 enlaces rotos» en el control
        # del arnés —un falso positivo que tumbaba la prueba entera antes
        # de inyectar nada—.
        canonica = busca_capitulo(capitulo)
        self.carpeta = canonica.parent
        env = os.environ.get(var_entorno)
        self.ruta = pathlib.Path(env) if env else canonica
        self.doc = self.ruta.read_text(encoding="utf-8")
        self.estructurales = set(estructurales or ())
        self.presupuesto_geomapa_kb = presupuesto_geomapa_kb
        self.fallos: list[str] = []
        self.comprobaciones = 0

        self._extrae_prosa()
        self._indexa(jsons)

        # Los cortes del JSON de mapas, en un índice propio.
        self.cortes_precalculo: set[str] = set()
        if json_mapas:
            p = SALIDAS / json_mapas
            if not p.exists():
                sys.exit(f"PARADO: falta el precálculo de mapas {p}")
            def recoge(o):
                if isinstance(o, dict):
                    for k, v in o.items():
                        if k == "cortes" and isinstance(v, list):
                            for c in v:
                                self.cortes_precalculo.add(
                                    f"{abs(float(c)):.6f}".rstrip("0").rstrip("."))
                        else:
                            recoge(v)
                elif isinstance(o, list):
                    for v in o:
                        recoge(v)
            recoge(json.loads(p.read_text(encoding="utf-8")))

    # -----------------------------------------------------------------
    def exige(self, ok: bool, que: str, detalle: str = "") -> bool:
        self.comprobaciones += 1
        print(f"  {'OK ' if ok else 'MAL'}  {que:<62} {detalle}")
        if not ok:
            self.fallos.append(f"{que} {detalle}")
        return bool(ok)

    # -----------------------------------------------------------------
    def _extrae_prosa(self) -> None:
        """Separa la prosa del motor, del código y del marcado.

        El orden importa y es la lección cara de DOE: las fórmulas de
        KaTeX **no** se retiran antes de extraer los números. La versión
        que las retiraba dejaba sin auditar casi un tercio de los
        decimales publicados.
        """
        doc = self.doc
        cuerpo = doc[:doc.rindex("\n  <script>")]
        cuerpo = re.sub(r"<style>.*?</style>", " ", cuerpo, flags=re.S)
        cuerpo = re.sub(r"<script[^>]*>.*?</script>", " ", cuerpo, flags=re.S)
        cuerpo = re.sub(r"<!--.*?-->", " ", cuerpo, flags=re.S)
        self.cuerpo = cuerpo

        # Los bloques de código salen: ya los cubre verifica_bloques.py, y
        # dejarlos metería `dep$desercion` como si fuera una cifra.
        prosa = re.sub(r"<pre>.*?</pre>", " ", cuerpo, flags=re.S)
        prosa = re.sub(r"<code[^>]*>.*?</code>", " ", prosa, flags=re.S)
        con_formulas = prosa
        prosa = re.sub(r"\$\$.*?\$\$", " ", prosa, flags=re.S)
        prosa = re.sub(r"\$[^$]*\$", " ", prosa)
        prosa = re.sub(r"<svg.*?</svg>", " ", prosa, flags=re.S)

        # DOS versiones, y la diferencia es deliberada: para buscar FRASES
        # las etiquetas se vuelven espacio; para extraer NÚMEROS se vuelven
        # una MARCA que no es espacio —así `<td>3</td><td>4</td>` no da
        # «34»— y las fórmulas se conservan.
        marcada = re.sub(r"<[^>]+>", " ¦ ", con_formulas)
        marcada = html_mod.unescape(marcada)
        marcada = marcada.replace("\\,", "").replace("\\;", "").replace("\\!", "")
        marcada = re.sub(r"\\[a-zA-Z]+", " ¦ ", marcada)
        marcada = re.sub(r"[{}$^_\\&]", " ¦ ", marcada)

        prosa = re.sub(r"<[^>]+>", " ", prosa)
        prosa = html_mod.unescape(prosa)
        self.prosa_txt = re.sub(r"\s+", " ", prosa)
        self.texto_plano = self.prosa_txt.lower()

        # Un TERCER texto, para buscar temas: la prosa **con el contenido
        # de los `<code>` en línea**, sin los bloques `<pre>`.
        #
        # Hace falta porque media docena de temas de este curso se llaman
        # como una función y el material los nombra dentro de `<code>`:
        # `zero.policy`, `poly2nb`, `st_transform`, `nb2listw`. Buscándolos
        # solo en la prosa, la comprobación de cobertura daba MAL sobre un
        # capítulo que sí los cubría — un falso positivo, que gasta la
        # confianza en el auditor tan rápido como un falso negativo la
        # traiciona.
        con_code = re.sub(r"<pre>.*?</pre>", " ", cuerpo, flags=re.S)
        con_code = re.sub(r"<[^>]+>", " ", con_code)
        self.texto_con_codigo = re.sub(
            r"\s+", " ", html_mod.unescape(con_code)).lower()

        # La coma seguida de espacio NUNCA es separador decimal aquí, pero
        # al quitar los espacios pegaría las dos cifras de una referencia
        # —«Biometrics 2, 110-114» daría «2,110»— y el auditor denunciaría
        # un número que nadie escribió. Se corta antes.
        marcada = marcada.replace(", ", " ¦ ")
        n = marcada.replace("\xa0", "").replace(" ", "")
        # Junta los millares separados por un espacio fino: «4 096» es un
        # número, no un 4 y un 96.
        #
        # El `\b` final que había aquí NO valía, y lo destapó el capítulo 1
        # (T1.2): tras quitar los espacios normales, «4 096 celdas» queda
        # como «4<fino>096celdas», y ahí no hay frontera de palabra después
        # del 096 —le sigue una letra—, así que el colapso no ocurría y el
        # auditor denunciaba «096» y «632» como cifras sin respaldo. Tres
        # falsos positivos sobre un capítulo correcto, que es la forma más
        # rápida de que alguien deje de leer el informe. Con una mirada
        # negativa a un dígito funciona en los dos casos.
        n = re.sub(r"(?<!\d)\d{1,3}(?:\s+\d{3})+(?!\d)",
                   lambda m: re.sub(r"\s+", "", m.group(0)), n)
        self.prosa_n = n
        self.crudos = re.findall(r"\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?", n)

    # -----------------------------------------------------------------
    def _indexa(self, jsons: list[str]) -> None:
        self.conocidos: set[str] = set()
        # Los valores TAL CUAL los escribió R, sin razones ni diferencias.
        # `conocidos` mezcla los tres tipos a propósito —el texto compara
        # todo el rato— y esa mezcla es la que hace que una cifra de pocos
        # decimales caiga dentro por azar. Guardarlos aparte permite
        # preguntar la versión estricta: ¿hay un valor de R detrás de esto?
        self.brutos: list[float] = []
        self.datos = {}
        for nombre in jsons:
            p = SALIDAS / nombre
            if not p.exists():
                sys.exit(f"PARADO: falta el precálculo {p}")
            obj = json.loads(p.read_text(encoding="utf-8"))
            self.datos[nombre] = obj
            self._indexa_obj(obj)
            self._recorre_comparables(obj)
            self._indexa_derivadas(obj)
            self._recoge_brutos(obj)

    def _recoge_brutos(self, o) -> None:
        if isinstance(o, dict):
            for v in o.values():
                self._recoge_brutos(v)
        elif isinstance(o, list):
            for v in o:
                self._recoge_brutos(v)
        elif isinstance(o, bool) or o is None:
            return
        elif isinstance(o, (int, float)) and o == o:
            self.brutos.append(float(o))

    def _indexa_obj(self, o) -> None:
        c = self.conocidos
        if isinstance(o, dict):
            for v in o.values():
                self._indexa_obj(v)
        elif isinstance(o, list):
            for v in o:
                self._indexa_obj(v)
        elif isinstance(o, bool) or o is None:
            return
        elif isinstance(o, (int, float)) and o == o:
            for d in range(0, 11):
                v = round(abs(float(o)), d)
                c.add(f"{v:.{d}f}")
                c.add(f"{v:.{d}f}".rstrip("0").rstrip("."))
            # porcentajes: el texto escribe 39.32 % donde el JSON guarda 0.393187
            for d in range(0, 5):
                p = round(abs(float(o)) * 100, d)
                c.add(f"{p:.{d}f}")
                c.add(f"{p:.{d}f}".rstrip("0").rstrip("."))
            # notación científica de los valores diminutos. Solo por debajo
            # de 1e-3, para no meter la mantisa de cualquier cifra grande en
            # el conjunto y quitarle filo a la regla (lección del cap. 3 de DOE).
            a = abs(float(o))
            if 0 < a < 1e-3:
                for d in range(0, 7):
                    m = f"{a:.{d}e}".split("e")[0]
                    c.add(m)
                    c.add(m.rstrip("0").rstrip("."))
        elif isinstance(o, str):
            junto = re.sub(r"(?<=\d)[\s  ](?=\d{3}\b)", "", o)
            for x in re.findall(r"\d+(?:\.\d+)?", junto):
                c.add(x)
            for x in re.findall(r"\d[\d ]{4,}\d", o):
                c.add(x.replace(" ", ""))

    def _indexa_comparaciones(self, valores) -> None:
        """Razones, excesos porcentuales y factores entre cifras publicadas.

        El material compara todo el rato —«cae el 83 %», «un factor de
        4.21»—. Esas cifras no están en el JSON pero salen de dos que sí,
        así que son legítimas, y calcularlas aquí es mejor que mantener
        una lista blanca a mano, que es justo lo que este guion existe
        para evitar. El coste está medido en `mide_punto_ciego.py`.
        """
        nums = [float(v) for v in valores
                if isinstance(v, (int, float)) and not isinstance(v, bool) and v]
        for x, y in itertools.permutations(nums, 2):
            if y == 0:
                continue
            self._indexa_obj(x / y)
            self._indexa_obj(100 * (x / y - 1))
            self._indexa_obj(100 * (x - y) / y)

    def _recorre_comparables(self, o) -> None:
        if isinstance(o, dict):
            escalares = [v for v in o.values()
                         if isinstance(v, (int, float)) and not isinstance(v, bool)]
            if len(escalares) >= 2:
                self._indexa_comparaciones(escalares)
            listas = {k: v for k, v in o.items()
                      if isinstance(v, list) and v
                      and all(isinstance(z, (int, float)) and not isinstance(z, bool)
                              for z in v)}
            if len(listas) >= 2:
                largo = min(len(v) for v in listas.values())
                for pos in range(min(largo, 80)):
                    self._indexa_comparaciones([v[pos] for v in listas.values()])
            for v in o.values():
                self._recorre_comparables(v)
        elif isinstance(o, list):
            for v in o:
                self._recorre_comparables(v)

    def _indexa_derivadas(self, o) -> None:
        """Cantidades que el texto cita legítimamente sin que el JSON las
        guarde: diferencias, sumas y repartos porcentuales dentro de una
        misma lista de cifras."""
        if isinstance(o, dict):
            for v in o.values():
                if (isinstance(v, list) and v
                        and all(isinstance(z, (int, float)) and not isinstance(z, bool)
                                for z in v)):
                    self._indexa_obj(max(v) - min(v))
                    self._indexa_obj(sum(v))
                    if len(v) <= 9:
                        for i, j in itertools.permutations(range(len(v)), 2):
                            self._indexa_obj(v[i] - v[j])
                    suma = sum(v)
                    if suma:
                        for x in v:
                            self._indexa_obj(100 * x / suma)
                self._indexa_derivadas(v)
        elif isinstance(o, list):
            for v in o:
                self._indexa_derivadas(v)

    # =================================================================
    # Las familias de comprobación
    # =================================================================
    def cifras(self) -> None:
        print("\n=== Las cifras del texto corrido (y de las fórmulas) ======")
        desconocidas = []
        for crudo in self.crudos:
            v = crudo.replace(",", ".")
            if v in self.estructurales or crudo in self.estructurales:
                continue
            if v in self.conocidos or v.rstrip("0").rstrip(".") in self.conocidos:
                continue
            # Un entero pequeño del discurso («los tres tipos de dato») no
            # es un resultado. El corte está en 12 porque por debajo de ahí
            # el material cuenta módulos, capítulos y semanas.
            if "." not in v and len(v) <= 2 and int(v) <= 12:
                continue
            desconocidas.append(crudo)
        self.exige(not desconocidas,
                   "toda cifra de la prosa sale del precálculo",
                   f"{len(self.crudos)} cifras leídas"
                   + ("" if not desconocidas
                      else f" · SIN RESPALDO: {sorted(set(desconocidas))[:14]}"))

        # La regla de T0.5, medida en mide_punto_ciego.py: por debajo de
        # CINCO decimales el índice de comparaciones absorbe buena parte de
        # las perturbaciones de un dígito. Se AVISA, no se tumba: hay cifras
        # con pocos decimales que son legítimas (un conteo, un porcentaje
        # redondo, el año de una cita). Convertirlo en fallo llenaría el
        # informe de ruido y acabaría enseñando a ignorarlo.
        #
        # PERO UN NÚMERO NO ES UNA PISTA. Hasta T2.2 esto imprimía solo el
        # recuento —13, 50 y 72 en los tres capítulos— y con eso nadie podía
        # hacer nada. Y había algo que mirar: el «61.7» del capítulo 1 llevaba
        # meses ahí dentro, calculado en el ensamblador y sin existir en ningún
        # JSON, con esta misma línea diciendo «13» todos los días.
        #
        # El triaje que las vuelve accionables: ¿hay algún valor BRUTO del
        # JSON que, redondeado a los decimales publicados, dé esta cifra? Si
        # lo hay, es una cita redondeada de algo que R calculó. Si no, solo la
        # respalda una cantidad derivada del índice —una razón, una
        # diferencia—, que es un respaldo mucho más flojo y es donde vivía el
        # 61.7. De 135 renglones se pasa a 7, que sí se pueden mirar.
        pocos = sorted({c for c in self.crudos
                        if "." in c and 1 <= len(c.split(".")[1]) <= 4
                        and c.replace(",", ".") not in self.estructurales})
        flojas = []
        for c in pocos:
            d = len(c.split(".")[1])
            v = float(c.replace(",", "."))
            if not any(round(abs(b), d) == v for b in self.brutos):
                flojas.append(c)
        print(f"  ---  {len(pocos)} cifras con menos de 5 decimales en la prosa "
              f"(el auditor las protege peor; ver mide_punto_ciego.py)")
        print(f"  ---  de ellas, {len(pocos) - len(flojas)} redondean un valor del JSON; "
              f"{len(flojas)} solo las respalda algo derivado"
              + (f": {flojas}" if flojas else ""))

    # NOTA (T2.2): la comprobación hermana de ésta —«ninguna cifra de la
    # prosa se calcula en el ensamblador»— NO vive aquí, y la decisión tiene
    # razón. Este auditor mira el HTML publicado; aquella mira el FUENTE del
    # ensamblador, así que es una guarda de compilación y está en
    # `ensambla_capN.py` (`sin_aritmetica_en_la_prosa`). Ahí falla antes de
    # publicar, el inventario de `prueba_ensambla_cap1.py` la recoge sola y
    # se puede inyectar parcheando la copia del ensamblador, que es
    # maquinaria que ya existe. Las dos atacan el mismo defecto —el 61.7—
    # por sus dos extremos: ésta el resultado, aquélla la causa.

    def temario(self, debe_cubrir: list[tuple[str, str]]) -> None:
        print("\n=== Cobertura del temario =================================")
        for que, clave in debe_cubrir:
            self.exige(clave.lower() in self.texto_con_codigo, f"cubre: {que}")

    def fuentes(self, citas: list[str]) -> None:
        print("\n=== Las fuentes citadas ===================================")
        for cita in citas:
            self.exige(cita.lower() in self.texto_plano, f"cita a {cita}")

    def afirmaciones(self, frases: list[tuple[str, str]]) -> None:
        print("\n=== Lo que el capítulo no puede dejar de decir ============")
        for que, clave in frases:
            self.exige(clave.lower() in self.texto_plano, que)

    # -----------------------------------------------------------------
    def accesibilidad(self) -> None:
        print("\n=== Accesibilidad =========================================")
        canvas = re.findall(r"<canvas[^>]*>", self.cuerpo)
        con_etiqueta = [c for c in canvas if "aria-label" in c]
        self.exige(bool(canvas) and len(canvas) == len(con_etiqueta),
                   "todo <canvas> del marcado lleva aria-label",
                   f"{len(con_etiqueta)} de {len(canvas)}")
        self.exige(bool(canvas) and all('role="img"' in c for c in canvas),
                   'todo <canvas> lleva role="img"')

        botones = re.findall(
            r'<button[^>]*class="(?:derivacion|ejercicio)-boton"[^>]*>', self.cuerpo)
        self.exige(bool(botones)
                   and all("aria-expanded" in b and "aria-controls" in b for b in botones),
                   "los desplegables declaran aria-expanded y aria-controls",
                   f"{len(botones)} botones")

        # El marcado del quiz. La regresión que en DOE vivió del capítulo 6
        # al 8 sin que la viera nadie: `.quiz-marcador` aplanado DENTRO de
        # `.quiz-resumen`. El marcado seguía siendo válido, las clases
        # estaban todas, la consola limpia — y el contador en vivo y el
        # botón «Reiniciar» no se veían NUNCA, porque el motor arranca cada
        # pasada con `resumen.innerHTML = ''` y el contador acababa
        # escribiendo en un nodo desconectado.
        # TODOS los bloques de quiz, no el primero.
        #
        # La versión anterior usaba `re.search`, así que miraba solo uno. Con
        # el capítulo 1 eso dejó de valer: trae DOS —la diagnóstica de
        # entrada y la del cierre—, y el arnés lo destapó de la manera más
        # cruda posible: se le rompió el marcado del segundo quiz al
        # auditor y el auditor informó «0 fallos». Comprobar el primero y
        # dar por buenos los demás es la misma trampa de alcance que en
        # T0.5 hacía que dos comprobaciones fueran incapaces de fallar.
        quices = [m.group(0) for m in re.finditer(
            r'^(?P<ind>[ ]*)<div class="quiz" data-quiz="[^"]*">\n.*?\n(?P=ind)</div>\n',
            self.cuerpo, re.S | re.M)]
        declarados = len(re.findall(r'data-quiz="[^"]*"', self.cuerpo))
        self.exige(bool(quices), "el capítulo trae su bloque de autoevaluación",
                   f"{len(quices)} bloques")
        self.exige(len(quices) == declarados,
                   "  y TODOS los data-quiz tienen su bloque bien formado",
                   f"{len(quices)} bien formados de {declarados} declarados")
        for k, quiz in enumerate(quices, 1):
            suf = "" if len(quices) == 1 else f" (quiz {k})"
            res = re.search(r'<div class="quiz-resumen"([^>]*)>(.*?)</div>', quiz, re.S)
            self.exige(res is not None and 'role="status"' in res.group(1),
                       f'el .quiz-resumen se anuncia con role="status"{suf}')
            self.exige(res is not None and not res.group(2).strip(),
                       f"el .quiz-resumen viene vacío, que es lo que el motor espera{suf}")
            marc = re.search(r'<div class="quiz-marcador">(.*?)</div>', quiz, re.S)
            self.exige(marc is not None
                       and 'class="quiz-conteo"' in marc.group(1)
                       and 'class="quiz-reiniciar"' in marc.group(1),
                       f"el contador y «Reiniciar» viven en .quiz-marcador, FUERA "
                       f"de .quiz-resumen{suf}")

        n_tablist = self.cuerpo.count('role="tablist"')
        n_tabs = self.cuerpo.count('class="code-tabs"')
        self.exige(n_tablist >= n_tabs and n_tabs > 0,
                   "cada bloque de pestañas declara role=tablist",
                   f"{n_tablist} tablist / {n_tabs} code-tabs")
        self.exige(self.cuerpo.count("<caption") >= 1,
                   "las tablas de datos traen su <caption>",
                   str(self.cuerpo.count("<caption")))
        self.exige(self.cuerpo.count('scope="row"') >= 1
                   and self.cuerpo.count('scope="col"') >= 2,
                   "las cabeceras de las tablas declaran su scope")

    # -----------------------------------------------------------------
    def geomapas(self) -> None:
        """La familia propia de este curso.

        Un `.geomapa` es un lienzo cuyos datos, cortes y leyenda viven en
        JSON dentro del `<script>`. El auditor de prosa corta el documento
        antes del script, así que sin esto **nada** miraría ahí. Y ya se
        cobró una pieza en T0.3: `dibuja()` repintaba el lienzo pero no la
        leyenda, de modo que al mover un control el mapa cambiaba y los
        rótulos de las clases seguían diciendo lo de antes. El componente
        se veía perfecto.
        """
        print("\n=== El componente .geomapa ================================")
        usados = re.findall(r'data-geomapa="([^"]+)"', self.cuerpo)
        registrados = re.findall(r"GEOMAPAS\['([^']+)'\]\s*=", self.doc)
        if not usados:
            print("  ---  el capítulo no usa .geomapa; nada que comprobar")
            return

        faltan = sorted(set(usados) - set(registrados))
        self.exige(not faltan, "todo data-geomapa tiene su registro en GEOMAPAS",
                   f"{len(set(usados))} usados, {len(set(registrados))} registrados"
                   + ("" if not faltan else f" · SIN REGISTRO: {faltan}"))

        pesos = 0.0
        for ident in sorted(set(usados) & set(registrados)):
            spec = self._json_de_geomapa(ident)
            if spec is None:
                print(f"  ---  '{ident}': la fuente es una función (simulador); "
                      f"sus cortes los comprueba el auditor del capítulo")
                continue
            pesos += len(json.dumps(spec, ensure_ascii=False).encode("utf-8")) / 1024

            modo = spec.get("modo")
            self.exige(bool(modo), f"'{ident}' declara su modo", str(modo))

            # QUÉ SE LE EXIGE A CADA MODO, y por qué esto no es una
            # relajación de la comprobación anterior (T1.2).
            #
            # La primera versión exigía cortes de clase a TODO mapa. Eso
            # valía mientras el único sujeto era un coropleto de
            # demostración, y deja de valer con el capítulo 1: un patrón
            # puntual coloreado por una marca CATEGÓRICA —las 578 muertes
            # de Snow por bomba más próxima— no clasifica nada, así que no
            # tiene cortes ni debe tenerlos. Exigírselos habría dado MAL
            # sobre un mapa correcto, y un auditor que denuncia lo que está
            # bien se acaba desactivando, que es la peor forma de perderlo.
            #
            # Así que la regla se afina en vez de aflojarse: **el que
            # clasifica tiene que traer los cortes de R, y el que colorea
            # por categoría tiene que traer sus niveles**. Ningún mapa se
            # queda sin nada que comprobar.
            if modo in ("poligonos", "rejilla"):
                self.exige("cortes" in spec and bool(spec["cortes"]),
                           f"'{ident}' ({modo}) trae los cortes calculados en R",
                           f"{len(spec.get('cortes', []))} cortes")
            elif modo == "puntos" and spec.get("marcas") is not None:
                tipo = spec.get("marcas_tipo")
                # Sin `marcas_tipo` el navegador tendría que ADIVINAR si
                # trece enteros son categorías o una escala. Adivinar bien
                # casi siempre es el modo de fallo de este proyecto.
                self.exige(tipo in ("categoria", "numero"),
                           f"'{ident}' declara de qué tipo es su marca",
                           str(tipo))
                if tipo == "categoria":
                    niv = spec.get("niveles") or []
                    marcas = [m for m in spec["marcas"] if isinstance(m, (int, float))]
                    self.exige(bool(niv), f"  y '{ident}' trae los niveles de la marca",
                               f"{len(niv)} niveles")
                    fuera = [m for m in marcas if not (1 <= m <= len(niv))]
                    self.exige(bool(niv) and not fuera,
                               f"  y cada código de marca cae dentro de los niveles",
                               "" if not fuera else f"{len(fuera)} fuera de rango")

            # Los cortes, si los hay, tienen que ser LOS del precálculo, no
            # unos cualesquiera: es lo que impide que alguien los recalcule
            # en JS «para que salgan más redondos» y el mapa deje de decir
            # lo que R midió.
            if spec.get("cortes"):
                respaldo = self.conocidos | self.cortes_precalculo
                sin_respaldo = [c for c in spec["cortes"]
                                if f"{abs(float(c)):.6f}".rstrip("0").rstrip(".")
                                not in respaldo
                                and f"{abs(float(c)):.4f}".rstrip("0").rstrip(".")
                                not in respaldo]
                self.exige(not sin_respaldo,
                           f"  y cada corte de '{ident}' está en el precálculo",
                           "" if not sin_respaldo else f"SIN RESPALDO: {sin_respaldo}")

            n_decl = spec.get("n")
            if n_decl is not None:
                # Un mapa de puntos no tiene `geom` ni `valor`: su tamaño
                # está en `pts`, que va en pares. Sin esta rama la
                # comprobación pasaba por `real == 0` —o sea, no comprobaba
                # nada— sobre los seis mapas de puntos del capítulo 1.
                if modo == "puntos" and spec.get("pts"):
                    real = len(spec["pts"]) // 2
                else:
                    real = len(spec.get("geom") or spec.get("valor") or [])
                self.exige(real == 0 or real == n_decl,
                           f"  y el n de '{ident}' coincide con la geometría",
                           f"n = {n_decl}, geometrías = {real}")
                if modo == "puntos" and spec.get("marcas") is not None:
                    self.exige(len(spec["marcas"]) == n_decl,
                               f"  y hay una marca por punto en '{ident}'",
                               f"{len(spec['marcas'])} marcas para {n_decl} puntos")

        # OJO CON EL ALCANCE, y esto lo destapó el propio arnés de
        # inyección: la primera versión preguntaba `"tabla:" in self.doc` y
        # `"etiqueta:" in self.doc`. Las dos cadenas aparecen en el
        # COMENTARIO de documentación del motor —
        #   //   GEOMAPAS['id'] = { fuente, alto, paleta, etiqueta, tabla }
        # — así que las dos comprobaciones daban OK pasara lo que pasara.
        # Eran **incapaces de fallar**, y sobre el informe se leían igual
        # que las que sí comprueban algo. Ahora se miran solo DENTRO de
        # los registros.
        bloques = [b for b in (self._bloque_de_geomapa(i)
                               for i in sorted(set(registrados))) if b]
        con_etiqueta = sum(bool(re.search(r"\betiqueta\s*:", b)) for b in bloques)
        con_tabla = sum(bool(re.search(r"\btabla\s*:", b)) for b in bloques)
        self.exige(con_etiqueta >= 1, "al menos un mapa declara su etiqueta accesible",
                   f"{con_etiqueta} de {len(bloques)} registros")
        self.exige(con_tabla >= 1, "al menos un mapa trae su tabla de respaldo plegable",
                   f"{con_tabla} de {len(bloques)} registros")
        self.exige(pesos <= self.presupuesto_geomapa_kb,
                   "la geometría cabe en el presupuesto",
                   f"{pesos:.1f} KB de {self.presupuesto_geomapa_kb:.0f} KB")
        # Los cortes NO se calculan en el navegador. Si alguien mete un
        # Fisher-Jenks en JS, además de reimplementarlo mal introduciría un
        # TERCER convenio de empates junto a los dos de classInt y
        # mapclassify (anexo A.2).
        self.exige("classInt" in self.doc or "classint" in self.doc.lower(),
                   "el capítulo declara que los cortes los calcula classInt")

    def _bloque_de_geomapa(self, ident: str) -> str:
        """El texto completo del registro `GEOMAPAS['ident'] = { … };`.

        Hace falta porque buscar `etiqueta:` o `tabla:` en el documento
        entero da OK siempre: el comentario de documentación del motor las
        nombra. Alcance equivocado = comprobación que no puede fallar.
        """
        m = re.search(r"GEOMAPAS\['" + re.escape(ident) + r"'\]\s*=\s*", self.doc)
        if not m:
            return ""
        i = self.doc.index("{", m.end()) if "{" in self.doc[m.end():m.end() + 200] else -1
        if i < 0:
            return ""
        return self.doc[i:self._fin_de_llave(i) + 1]

    def _fin_de_llave(self, i: int) -> int:
        """Índice de la llave que cierra la que abre en `i`, saltando las
        que viven dentro de una cadena."""
        prof, j, en_cadena, comilla, esc = 0, i, False, "", False
        while j < len(self.doc):
            ch = self.doc[j]
            if en_cadena:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == comilla:
                    en_cadena = False
            elif ch in "\"'`":
                en_cadena, comilla = True, ch
            elif ch == "{":
                prof += 1
            elif ch == "}":
                prof -= 1
                if prof == 0:
                    return j
            j += 1
        return len(self.doc) - 1

    def _json_de_geomapa(self, ident: str):
        """Extrae el literal JSON de `fuente:` de un registro de GEOMAPAS.

        Devuelve None si la fuente es una función —el caso de los
        simuladores, que cambian de dato al mover un control—.
        """
        m = re.search(r"GEOMAPAS\['" + re.escape(ident) + r"'\]\s*=\s*\{", self.doc)
        if not m:
            return None
        f = re.compile(r"fuente:\s*").search(self.doc, m.end())
        if not f:
            return None
        i = f.end()
        if self.doc[i] != "{":
            return None          # `() => DEMO.x` o similar
        prof, j, en_cadena, esc = 0, i, False, False
        while j < len(self.doc):
            ch = self.doc[j]
            if en_cadena:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    en_cadena = False
            elif ch == '"':
                en_cadena = True
            elif ch == "{":
                prof += 1
            elif ch == "}":
                prof -= 1
                if prof == 0:
                    break
            j += 1
        try:
            return json.loads(self.doc[i:j + 1])
        except json.JSONDecodeError:
            return None

    # -----------------------------------------------------------------
    def soluciones(self, json_soluciones: str) -> None:
        """Cada celda de las tablas de solución, contra su valor del JSON.

        POR QUÉ HACE FALTA, y es una lección de T0.2. Las cifras de esas
        tablas las cubría solo `cifras()`, que compara contra un índice
        grande de valores conocidos. `mide_punto_ciego.py` midió lo que eso
        deja pasar: con cinco decimales se le cuela el 4,63 % de las
        perturbaciones de un dígito, pero con un ENTERO —sin decimales que
        lo hagan único— el índice lo absorbe casi siempre. Mientras las
        tablas publicaban «359.00000» el problema no se veía; al arreglar el
        tipo y escribir «359», seis cifras del capítulo 1 y quince del 2
        pasaron al régimen mal protegido.

        La salida NO es volver a los cinco decimales sobre un conteo. Es
        dejar de depender de un índice para algo que se puede comprobar
        EXACTO: aquí se lee el número tal y como salió al HTML y se
        contrasta con el del JSON, uno a uno. Un índice responde «ese número
        existe en alguna parte»; esto responde «ESTA celda dice lo que su
        paso dice», que es la pregunta que importaba desde el principio.

        La comparación es de ida y vuelta a propósito: se reinterpreta la
        cadena publicada como número en vez de re-generar el formato. Si
        replicara aquí la regla del ensamblador, se estaría comprobando a sí
        misma y daría verde ante cualquier transcripción rota.
        """
        print("\n=== Las tablas de solución, celda a celda =================")
        obj = self.datos.get(json_soluciones)
        if obj is None:
            p = SALIDAS / json_soluciones
            obj = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

        ejercicios = [v for k, v in obj.items()
                      if k.startswith("e") and isinstance(v, dict) and "pasos" in v]
        # Las filas publicadas: paso -> texto de la celda.
        #
        # LA CELDA no puede contener un `</td>`, y no es un detalle: una
        # tabla de varias columnas —como la de `st_set_crs` del capítulo 2,
        # con «vértices movidos» y «máximo desplazamiento» en la misma
        # fila— dejaría que un `.*?` perezoso emparejara el encabezado con
        # el `<td>` de la SEGUNDA columna. Así esas filas no casan, que es
        # lo correcto: no son pasos de solución.
        #
        # Y LA CLAVE tampoco puede contener un `</th>`, que es la mitad que
        # faltaba y encontró T3.3. El `(.*?)` del encabezado no estaba
        # acotado a su propia fila: con `re.S`, ante una tabla de varias
        # columnas el motor no falla ahí, sino que **sigue tragando** —
        # párrafos, simuladores, bloques de código enteros— hasta dar con
        # el primer `</th><td>…</td></tr>` de una sola columna que haya más
        # abajo en el documento. Ese, que es una fila de solución legítima,
        # quedaba absorbido dentro de la clave y desaparecía del índice.
        #
        # Se cobró UNA fila en cada capítulo publicado: «Muertes y bombas
        # leídas» en el 1, tres en el 2, «Cuantiles vs. Head/tails» en el 3
        # y «Sedes en el perímetro urbano» en el 4. En los tres primeros el
        # paso perdido no era numérico y el auditor no tenía nada que
        # contrastar, así que informó verde; en el cuarto sí lo era y por
        # eso saltó. La forma de fallo es la peor: el recuento «N de N» se
        # leía completo porque el denominador contaba pasos del JSON, no
        # filas del HTML.
        filas = dict(re.findall(
            r'<tr><th scope="row">((?:(?!</th>).)*)</th>'
            r'<td>((?:(?!</td>).)*)</td></tr>',
            self.doc, re.S))

        def leer(txt):
            """El número que un humano lee en la celda, o None si no lo es."""
            t = re.sub(r"<[^>]+>", "", txt)
            # U+202F (el fino de `ent()`), U+00A0 (el de &nbsp;) y el normal
            # son indistinguibles en el editor: se escriben por punto de
            # código para que una copia no se lleve el que falte.
            for e in ("\u202f", "\u00a0", "\u2009", " "):
                t = t.replace(e, "")
            t = t.replace("−", "-").replace(",", ".")
            try:
                return float(t)
            except ValueError:
                return None

        revisadas = comparadas = 0
        malas = []
        for e in ejercicios:
            for p in e["pasos"]:
                v, paso = p["valor"], html_mod.unescape(str(p["paso"]))
                if isinstance(v, bool) or not isinstance(v, (int, float)):
                    continue
                revisadas += 1
                celda = next((c for k, c in filas.items()
                              if html_mod.unescape(re.sub(r"<[^>]+>", "", k)).strip() == paso.strip()),
                             None)
                if celda is None:
                    malas.append(f"«{paso[:40]}» no aparece en ninguna tabla")
                    continue
                leido = leer(celda)
                if leido is None:
                    malas.append(f"«{paso[:40]}» publica «{celda[:20]}», que no es un número")
                    continue
                comparadas += 1
                # La tolerancia se lee de la CELDA, no se asume. Publicar
                # con tres decimales y con cinco son dos promesas distintas,
                # y el auditor no tiene por qué saber de antemano cuál se
                # hizo: cuenta los decimales que hay y exige que el valor
                # del JSON, redondeado a esos mismos, salga idéntico. Con
                # una tolerancia fija en su lugar, un 1.61169 escrito donde
                # tocaba 1.61168 se colaba por ocho millonésimas.
                pub = re.sub(r"<[^>]+>", "", celda)
                dec = len(pub.split(".")[-1].strip()) if "." in pub else 0
                if round(float(v), dec) != round(leido, dec):
                    malas.append(f"«{paso[:40]}» publica {leido} y el JSON dice {v}")

        self.exige(not malas and comparadas > 0,
                   "cada celda de solución dice lo que su JSON dice",
                   f"{comparadas} de {revisadas} celdas numéricas contrastadas"
                   + ("" if not malas else f" · MAL: {malas[:4]}"))

    # -----------------------------------------------------------------
    def codificacion(self) -> None:
        """Bytes crudos donde debería haber una tilde.

        Encontrado en T0.5, y no era hipotético: `saber11_20224_cifras.json`
        de T0.4 llevaba «Educaci<c3><b3>n profesional completa». `jsonlite`
        escribe eso, sin fallar, cuando R arranca con LC_CTYPE=C. Un
        capítulo que incruste ese JSON publica el destrozo.
        """
        print("\n=== Codificación ==========================================")
        crudos = MOJIBAKE_RE.findall(self.doc)
        self.exige(not crudos,
                   "ninguna tilde rota <xx> ni <U+XXXX> en el documento",
                   "" if not crudos else f"{len(crudos)} apariciones: "
                                         f"{sorted(set(crudos))[:8]}")
        self.exige("charset=\"utf-8\"" in self.doc.lower()
                   or "charset=utf-8" in self.doc.lower(),
                   "el documento declara UTF-8")
        # El reemplazo U+FFFD es la otra cara: ahí la tilde ya se perdió.
        self.exige("�" not in self.doc,
                   "ningún carácter de reemplazo U+FFFD")

    # -----------------------------------------------------------------
    def enlaces(self) -> None:
        """Los enlaces locales, y la comprobación que SE ARMA SOLA.

        La versión anterior hacía `exige(not rotos)`, y con cero enlaces
        locales `rotos` está vacío: **pasaba en verde sin haber comprobado
        nada**. Sobre el informe eso se lee exactamente igual que una
        comprobación que sí verificó algo, que es la definición de
        comprobación imaginaria de T0.5.

        Y el capítulo 1 tenía cero, por un motivo legítimo: el sitio no
        existe todavía —la portada es T7.1—, así que no hay adónde
        enlazar. El problema no es del capítulo, es que la comprobación no
        tiene sujeto.

        Poner aquí un mínimo a mano —«exige al menos un enlace»— habría
        obligado a acordarse de subirlo en la Fase 7, y lo que hay que
        recordar se olvida. En vez de eso, la comprobación **mira la
        carpeta**: en cuanto aparezca al lado un `index.html` u otro
        capítulo, exige que este capítulo enlace a alguno. Hoy no hay
        ninguno y se dice en voz alta; el día que lo haya, muerde sin que
        nadie toque una línea.
        """
        print("\n=== Enlaces ===============================================")
        # SOBRE EL CUERPO, NO SOBRE EL DOCUMENTO, y lo destapó T3.3 al
        # reensamblar los capítulos 2 y 3 sobre una plantilla que estrena
        # el resumen de repaso del quiz. Ese resumen construye sus enlaces
        # con una plantilla de JavaScript:
        #
        #     `<a href="${r.href}">${r.etiqueta}</a>`
        #
        # y buscando sobre `self.doc` —que incluye el `<script>` final—
        # `${r.href}` casaba como enlace local y se denunciaba como roto.
        # Un falso positivo sobre material correcto, y de los caros: habría
        # aparecido en los cuatro capítulos en cuanto alguien los
        # reensamblara, con el auditor señalando una cadena que no es una
        # ruta sino código.
        #
        # `self.cuerpo` es el documento sin `<style>`, sin `<script>` y sin
        # comentarios, pero CON las `<template>` de los módulos, que es
        # donde viven los enlaces que un lector puede pulsar. No se pierde
        # cobertura: lo que sale del alcance es código, no marcado.
        todos = re.findall(r'href="([^"#]+)"', self.cuerpo)
        locales = [h for h in todos
                   if not h.startswith(("http", "mailto", "data:", "#"))]
        rotos = [h for h in locales if not (self.carpeta / h).exists()]

        # Los bancos de prueba (`prueba-*.html`) NO cuentan como material
        # publicado: enlazar el capítulo de un estudiante a un fixture
        # sería peor que no enlazarlo a nada.
        hermanos = sorted(
            p.name for p in self.carpeta.glob("*.html")
            if p.name != self.ruta.name and not p.name.startswith("prueba-")
            and (p.name == "index.html" or p.name.startswith("capitulo-")))

        if locales:
            self.exige(not rotos, "todo enlace local apunta a un archivo que existe",
                       f"{len(locales)} locales, {len(rotos)} rotos"
                       + ("" if not rotos else f": {rotos}"))
        else:
            print("  ---  el capítulo no tiene enlaces LOCALES, así que la "
                  "comprobación de enlaces rotos NO tiene sujeto")

        # Y la exclusión SIMÉTRICA, que se me olvidó y cazó el arnés: un
        # banco de pruebas no es material del curso, así que tampoco tiene
        # que enlazar con el sitio. La primera versión excluía los
        # `prueba-*` como DESTINO pero no como SUJETO, y en cuanto existió
        # el capítulo 1 el fixture de T0.5 empezó a fallar su control —y
        # con el control caído, sus 36 inyecciones dejaron de probar nada—.
        es_material = not self.ruta.name.startswith("prueba-")

        if hermanos and es_material:
            apunta = [h for h in locales if h.split("/")[-1] in hermanos]
            self.exige(bool(apunta),
                       "el capítulo enlaza con el resto del sitio",
                       f"{len(apunta)} de {len(hermanos)} hermanos publicados"
                       + ("" if apunta else f"; hay {hermanos} y no enlaza a ninguno"))
        elif not es_material:
            print("  ---  es un banco de pruebas, no material del curso: no se "
                  "le exige enlazar con el sitio")
        else:
            print(f"  ---  no hay otro capítulo ni index.html en "
                  f"{self.carpeta.name}/: nada con lo que enlazar todavía "
                  f"(la portada es T7.1). Esta comprobación se arma sola "
                  f"en cuanto exista el primero.")
        self.exige(self.doc.count("<template") == self.doc.count("</template>"),
                   "las plantillas abren y cierran",
                   f"{self.doc.count('<template')} / {self.doc.count('</template>')}")

    # -----------------------------------------------------------------
    def coherencia(self, cadenas: list[str], ordenes: list[str]) -> None:
        """Si el locale se rompe, las tildes no desaparecen: se convierten
        en otra cosa. La comprobación útil es exigir cadenas concretas
        intactas, no buscar «caracteres raros»."""
        print("\n=== Coherencia del documento ==============================")
        for cadena in cadenas:
            self.exige(cadena in self.doc, f"el texto conserva «{cadena}» intacto")
        for orden in ordenes:
            self.exige(orden in self.doc, f"el material usa «{orden}»")

    def peso(self, kb: float = TOPE_KB) -> None:
        """Alarma contra un ensamblado desbocado, no presupuesto de contenido.

        Sin argumento usa el tope de la casa; el razonamiento y la cota que
        lo ata al arnés de inyección están en `TOPE_KB`.
        """
        tam = self.ruta.stat().st_size
        self.exige(tam <= kb * 1024, f"el capítulo no se ha desbocado (tope {kb:.0f} KB)",
                   f"{tam/1024:.0f} KB ({100*tam/(kb*1024):.0f} %)")

    # -----------------------------------------------------------------
    def cierre(self) -> int:
        print("\n=== Cierre ================================================")
        print(f"\n  {self.comprobaciones} comprobaciones · {len(self.fallos)} fallos")
        if self.fallos:
            print("\n  FALLOS:")
            for f in self.fallos:
                print(f"   - {f}")
            return 1
        print("  Auditoría del texto limpia.\n")
        return 0
