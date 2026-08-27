#!/bin/sh
# =====================================================================
# audita_todo.sh — pasa el arnés entero de una vez
#
# Material de Estadística Espacial 2026-II (20929). T0.5.
#
# Existe por una razón práctica: una herramienta que hay que recordar
# invocar con cuatro órdenes distintas se deja de invocar. Esto es lo que
# se ejecuta antes de dar por cerrado cualquier capítulo.
#
#   1. audita_capN.py       — el PRECÁLCULO, recalculado en Python
#   2. prueba_auditor_capN  — le inyecta defectos a ese auditor
#   3. prueba_ensambla_capN — le inyecta defectos a las guardas del ENSAMBLADOR
#   4. verifica_bloques.py  — ejecuta los bloques y contrasta sus `#>`
#   5. campos_vivos.py      — ningún campo de courseData se declara sin leerse
#   6. audita_texto_*.py    — las cifras de la prosa, incluidas las de KaTeX
#   7. prueba_texto.py      — le inyecta defectos al auditor de prosa
#   8. cuenta_sitio.py      — los totales, contados y no recordados
#
# Los TALLERES corren por un bucle propio (C8 del Taller 1): no son
# capítulos —sin quiz, sin ejercicios guiados, y con una familia de
# comprobación que los capítulos no tienen— y meterlos en el bucle de
# `capN` habría exigido que fingieran serlo.
#
# Los PREPARCIALES, por un tercer bucle, y por la misma razón elevada al
# cuadrado: no enseñan contenido nuevo (no son capítulos) y no se
# califican ni se individualizan (no son talleres). Además traen dos
# comprobaciones que no existen en ningún otro sitio: un ALCANCE
# verificable —qué módulos entran y cuáles no, leído del HTML publicado— y
# una familia de SINCRONÍA, que compara cada cifra reutilizada contra la
# ruta del capítulo de la que salió. Esa segunda es la razón de fondo de
# que esto exista: el día que se regenere un capítulo y una cifra se mueva,
# el preparcial queda mintiendo sin que nada más lo diga, porque su propio
# JSON sigue siendo internamente coherente (§12.4 del plan).
#
# El paso 3 es de T1.3.n y cubre un hueco que llevaba abierto desde T1.2: las
# guardas de compilación miran **el hueco entre archivos** —entre el dato y el
# cableado que lo dibuja—, que es donde los auditores no llegan y donde han
# salido los últimos defectos. Corre incluso con `--rapido` porque cuesta 2 s.
#
# El orden importa dos veces: el precálculo va antes que la prosa porque
# la prosa se compara CONTRA el precálculo —auditar un texto contra un
# JSON equivocado es auditar nada—, y cada arnés de inyección va justo
# detrás de su auditor, porque si el arnés falla el verde del auditor no
# significa nada.
#
# Los pasos 1 y 2 solo corren si el capítulo ya tiene precálculo; así
# esto sirve igual mientras se van añadiendo capítulos.
#
# Uso, desde la carpeta `Estadistica espacial/`:
#     precalculo/audita_todo.sh
#     precalculo/audita_todo.sh --rapido    (se salta los arneses de inyección)
# Devuelve distinto de cero si algo falla.
# =====================================================================
set -u

cd "$(dirname "$0")/.." || exit 1
FALLOS=0
RAPIDO=0
[ "${1:-}" = "--rapido" ] && RAPIDO=1

# El auditor del precálculo necesita geopandas, libpysal y esda: es el de
# geo_env, no `python3` a secas. La ruta la congeló T0.1.
PY_GEO="$(python3 -c 'import json;print(json.load(open("precalculo/versiones_py.json"))["ejecutable"])' 2>/dev/null)"
[ -x "${PY_GEO:-}" ] || PY_GEO=python3

paso() {
  echo ""
  echo "================================================================"
  echo "  $1"
  echo "================================================================"
  shift
  if "$@"; then
    echo "  --> OK"
  else
    echo "  --> FALLA"
    FALLOS=$((FALLOS + 1))
  fi
}

for N in 1 2 3 4 5 6 7 8 9 10; do
  [ -f "precalculo/salidas/cap${N}_datos.json" ] || continue
  [ -f "precalculo/audita_cap${N}.py" ] || continue
  paso "precálculo del capítulo ${N} · audita_cap${N}.py (Python, independiente)" \
       "$PY_GEO" "precalculo/audita_cap${N}.py"
  if [ "$RAPIDO" -eq 0 ] && [ -f "precalculo/prueba_auditor_cap${N}.py" ]; then
    paso "precálculo del capítulo ${N} · prueba_auditor_cap${N}.py (inyección)" \
         python3 "precalculo/prueba_auditor_cap${N}.py"
  fi
  # El arnés del ENSAMBLADOR sí corre con --rapido, y a propósito: cuesta
  # 2 s, no 10 min. El ensamblador tarda 0,05 s, así que inyectarle 40
  # defectos y trazarlo entero sigue siendo más barato que UNA pasada del
  # auditor del precálculo. Gatearlo solo serviría para no correrlo nunca, y
  # sus guardas son las que vigilan el hueco entre el dato y el cableado que
  # lo dibuja — donde han aparecido los tres últimos defectos del capítulo 1.
  if [ -f "precalculo/prueba_ensambla_cap${N}.py" ]; then
    paso "compilación del capítulo ${N} · prueba_ensambla_cap${N}.py (inyección)" \
         python3 "precalculo/prueba_ensambla_cap${N}.py"
  fi
done

# Los TALLERES, que no son capítulos y por eso no caben en el bucle de
# arriba: no tienen ejercicios guiados ni autoevaluación, su HTML no se
# llama `capitulo-*`, y su auditor comprueba una familia entera que los
# capítulos no tienen —que el enunciado no filtre la respuesta—.
#
# El bucle es propio y descubre igual que el otro: el día que haya un
# taller 2, lo hereda sin tocar nada. Sin esto, el Taller 1 habría nacido
# fuera del arnés, que es justo lo que C8 existe para impedir.
for N in 1 2 3 4; do
  [ -f "precalculo/salidas/taller${N}_datos.json" ] || continue
  [ -f "precalculo/audita_taller${N}.py" ] || continue
  paso "precálculo del taller ${N} · audita_taller${N}.py (Python, independiente)" \
       "$PY_GEO" "precalculo/audita_taller${N}.py"
  if [ "$RAPIDO" -eq 0 ] && [ -f "precalculo/prueba_auditor_taller${N}.py" ]; then
    paso "precálculo del taller ${N} · prueba_auditor_taller${N}.py (inyección)" \
         python3 "precalculo/prueba_auditor_taller${N}.py"
  fi
done

# Los PREPARCIALES. El bucle descubre igual que los otros dos: el día que
# haya un preparcial del Corte II, lo hereda sin tocar una línea.
for N in 1 2 3 4; do
  [ -f "precalculo/salidas/preparcial${N}_datos.json" ] || continue
  [ -f "precalculo/audita_preparcial${N}.py" ] || continue
  paso "precálculo del preparcial ${N} · audita_preparcial${N}.py (Python, independiente)" \
       "$PY_GEO" "precalculo/audita_preparcial${N}.py"
  # El arnés del ALCANCE corre siempre, también con --rapido, por la misma
  # razón que `prueba_ensambla_capN`: cuesta 0,06 s. Y vigila algo que
  # ningún otro paso mira — que la frontera del temario siga donde el plan
  # la puso (D1). Si un capítulo publica un módulo más, el alcance del
  # preparcial cambia en silencio y sus 30 módulos dejan de ser 30.
  if [ -f "precalculo/prueba_alcance_preparcial${N}.py" ]; then
    paso "alcance del preparcial ${N} · prueba_alcance_preparcial${N}.py (inyección)" \
         python3 "precalculo/prueba_alcance_preparcial${N}.py"
  fi
  if [ "$RAPIDO" -eq 0 ] && [ -f "precalculo/prueba_auditor_preparcial${N}.py" ]; then
    paso "precálculo del preparcial ${N} · prueba_auditor_preparcial${N}.py (inyección)" \
         python3 "precalculo/prueba_auditor_preparcial${N}.py"
  fi
done

# Va ANTES de los auditores de prosa y con su autoprueba dentro: cuesta
# 0,1 s y mira la causa del defecto que aquéllos vigilan por el resultado.
# El 61.7 del capítulo 1 pasó meses con los dos auditores en verde porque
# el índice de comparaciones absorbe una cifra de un decimal; esto no tiene
# índice ni tolerancia. Descubre los ensambladores solo, así que el capítulo
# 4 lo hereda sin tocar nada. Nació en T2.2.
paso "sin_aritmetica.py — ninguna cifra de la prosa se calcula fuera de R" \
     python3 precalculo/sin_aritmetica.py --prueba

# Del 2026-08-14, y por la misma razón que el de arriba: mira el CONTRATO
# entre el dato y quien lo pinta, que es donde no llega ninguna comprobación
# de comportamiento. `courseData` declaraba tres campos que la barra lateral
# no leía, y por eso su esquema pudo partirse en dos —capítulo 1 con
# `shortTitle`, capítulos 2 y 3 con `subtitle`— sin que nada lo dijera.
# Descubre los documentos solo, bancos y talleres incluidos: fue justo el
# banco hecho a mano en T0.3 el que quedó atrás cuando se arregló.
paso "campos_vivos.py — ningún campo de courseData se declara y no se lee" \
     python3 precalculo/campos_vivos.py --prueba

# Del 2026-08-18, y de la misma familia que los dos de arriba: mira el CSS que
# el navegador llega a LEER, no el que está escrito. El injerto de T0.2 dejó dos
# `*/` huérfanos en la plantilla, y un `*/` huérfano no se descarta: se lleva por
# delante la regla siguiente. `.glosario-notacion` y `.rubrica` llevaban desde
# entonces sin existir en las seis páginas, con el contenedor de la rúbrica del
# Taller 1 pintándose sin caja. Ninguna comprobación de comportamiento podía
# verlo —el componente aparece y funciona— y el navegador tampoco avisa.
paso "comentarios_cerrados.py — ningún \`*/\` suelto se lleva una regla por delante" \
     python3 precalculo/comentarios_cerrados.py --prueba

paso "verifica_bloques.py — los bloques de código y sus #>" \
     python3 precalculo/verifica_bloques.py --todos

paso "audita_texto_demo.py — las cifras de la prosa del fixture" \
     sh -c 'cd precalculo && python3 audita_texto_demo.py'

# Los auditores de prosa de los capítulos, uno por capítulo escrito. Se
# recorren igual que los del precálculo: así esto sigue sirviendo mientras
# se van añadiendo capítulos, sin tocar el guion cada vez.
for N in 1 2 3 4 5 6 7 8 9 10; do
  [ -f "precalculo/audita_texto_cap${N}.py" ] || continue
  paso "audita_texto_cap${N}.py — las cifras de la prosa del capítulo ${N}" \
       sh -c "cd precalculo && python3 audita_texto_cap${N}.py"
done

# Y los auditores de prosa de los talleres, por el mismo bucle propio.
for N in 1 2 3 4; do
  [ -f "precalculo/audita_texto_taller${N}.py" ] || continue
  paso "audita_texto_taller${N}.py — las cifras de la prosa del taller ${N}" \
       sh -c "cd precalculo && python3 audita_texto_taller${N}.py"
done

# Y los de los preparciales. Hoy este bucle no encuentra nada y se salta
# entero: `audita_texto_preparcial1.py` es P3.1 y no está escrita. Está
# puesto ya a propósito, para que el día que nazca entre al arnés sin que
# nadie tenga que acordarse de volver aquí — que es exactamente el defecto
# que C8 del Taller 1 existe para no repetir.
for N in 1 2 3 4; do
  [ -f "precalculo/audita_texto_preparcial${N}.py" ] || continue
  paso "audita_texto_preparcial${N}.py — las cifras de la prosa del preparcial ${N}" \
       sh -c "cd precalculo && python3 audita_texto_preparcial${N}.py"
done

if [ "$RAPIDO" -eq 0 ]; then
  paso "prueba_texto.py — el arnés de inyección de la prosa" \
       python3 precalculo/prueba_texto.py
fi

paso "cuenta_sitio.py — los totales" \
     python3 precalculo/cuenta_sitio.py

echo ""
echo "================================================================"
if [ "$FALLOS" -eq 0 ]; then
  echo "  ARNÉS COMPLETO EN VERDE"
else
  echo "  $FALLOS PASO(S) EN ROJO"
fi
echo "================================================================"
exit "$FALLOS"
