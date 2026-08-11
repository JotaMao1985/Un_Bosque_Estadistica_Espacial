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
#   5. audita_texto_*.py    — las cifras de la prosa, incluidas las de KaTeX
#   6. prueba_texto.py      — le inyecta defectos al auditor de prosa
#   7. cuenta_sitio.py      — los totales, contados y no recordados
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

# Va ANTES de los auditores de prosa y con su autoprueba dentro: cuesta
# 0,1 s y mira la causa del defecto que aquéllos vigilan por el resultado.
# El 61.7 del capítulo 1 pasó meses con los dos auditores en verde porque
# el índice de comparaciones absorbe una cifra de un decimal; esto no tiene
# índice ni tolerancia. Descubre los ensambladores solo, así que el capítulo
# 4 lo hereda sin tocar nada. Nació en T2.2.
paso "sin_aritmetica.py — ninguna cifra de la prosa se calcula fuera de R" \
     python3 precalculo/sin_aritmetica.py --prueba

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
