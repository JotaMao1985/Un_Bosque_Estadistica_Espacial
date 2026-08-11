#!/bin/sh
# =====================================================================
# prueba_reproducible.sh — ejecuta un generador dos veces y compara
#
# Material de Estadística Espacial 2026-II (20929). T1.1.
#
# Es el criterio de verificación que el plan le pone a T1.1: «ejecutar
# genera_cap1.R dos veces y comparar los JSON byte a byte (semilla
# fija)». Con semilla fija y sin nada que dependa del reloj, dos
# ejecuciones tienen que dar archivos idénticos. Si no lo dan, hay una
# fuente de aleatoriedad sin sembrar, un orden de recorrido que depende
# de una tabla hash, o una ruta absoluta colándose en la salida — y
# cualquiera de las tres rompe la reproducibilidad del material.
#
# LA ÚNICA EXCEPCIÓN, declarada: `meta.generado` guarda la fecha, así que
# dos ejecuciones a caballo de la medianoche diferirían en ese campo y en
# nada más. El guion informa de las dos cosas: la comparación cruda y la
# comparación ignorando esa línea. Un «idéntico salvo la fecha» es un
# aprobado; cualquier otra diferencia, no.
#
# Uso, desde la carpeta `Estadistica espacial/`:
#     precalculo/prueba_reproducible.sh precalculo/genera_cap1.R \
#         cap1_datos.json cap1_mapas.json
# =====================================================================
set -u

cd "$(dirname "$0")/.." || exit 1

GUION="${1:?falta el guion generador}"
shift
[ "$#" -ge 1 ] || { echo "falta al menos un archivo de salida" >&2; exit 1; }

SAL="precalculo/salidas"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "=================================================================="
echo "  Reproducibilidad de $GUION"
echo "=================================================================="

echo "\n  1/2 · primera ejecución"
precalculo/rscript.sh "$GUION" >/dev/null 2>&1 || {
  echo "  PARADO: la primera ejecución falló"; exit 1; }
for f in "$@"; do cp "$SAL/$f" "$TMP/$f.a"; done

echo "  2/2 · segunda ejecución"
precalculo/rscript.sh "$GUION" >/dev/null 2>&1 || {
  echo "  PARADO: la segunda ejecución falló"; exit 1; }

FALLOS=0
echo ""
for f in "$@"; do
  if cmp -s "$TMP/$f.a" "$SAL/$f"; then
    echo "  OK   $f — idéntico byte a byte ($(wc -c < "$SAL/$f" | tr -d ' ') bytes)"
  else
    # ¿La única diferencia es la fecha de generación?
    grep -v '"generado"' "$TMP/$f.a" > "$TMP/$f.a2"
    grep -v '"generado"' "$SAL/$f"  > "$TMP/$f.b2"
    if cmp -s "$TMP/$f.a2" "$TMP/$f.b2"; then
      echo "  OK   $f — idéntico salvo \"generado\" (la fecha; declarado)"
    else
      echo "  MAL  $f — DIFIERE en algo que no es la fecha:"
      diff "$TMP/$f.a2" "$TMP/$f.b2" | head -12 | sed 's/^/         /'
      FALLOS=$((FALLOS + 1))
    fi
  fi
done

echo ""
if [ "$FALLOS" -eq 0 ]; then
  echo "  REPRODUCIBLE"
else
  echo "  $FALLOS ARCHIVO(S) NO REPRODUCIBLE(S)"
fi
exit "$FALLOS"
