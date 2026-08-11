#!/bin/sh
# =====================================================================
# rscript.sh — el único modo correcto de invocar R en este proyecto
#
# Material de Estadística Espacial 2026-II (20929).
#
# Resuelve de una vez las DOS trampas del entorno, que hasta ahora había
# que recordar por separado en cada sesión:
#
#   1. El `Rscript` del PATH es Homebrew 4.6.0 y NO TIENE `sf`. El bueno
#      es el del framework 4.4-arm64, cuya ruta está en versiones.json.
#
#   2. `Rscript` arranca con LC_CTYPE=C, y en ese estado `jsonlite`
#      escribe las tildes como `<c3><b3>` **sin fallar**. Y no se puede
#      arreglar desde dentro del script: R parsea el archivo entero antes
#      de ejecutar su primera línea, así que para cuando `utf8.R` corre,
#      los literales acentuados ya se leyeron mal. Hay que arrancar el
#      proceso ya en UTF-8. Ver precalculo/utf8.R.
#
# Uso, desde la carpeta `Estadistica espacial/`:
#     precalculo/rscript.sh precalculo/genera_demo_auditoria.R
#     precalculo/rscript.sh -e 'cat(l10n_info()$`UTF-8`)'
# =====================================================================
set -eu

R_BUENO="/Library/Frameworks/R.framework/Versions/4.4-arm64/Resources/bin/Rscript"

if [ ! -x "$R_BUENO" ]; then
  echo "PARADO: no está $R_BUENO" >&2
  echo "        (el Rscript del PATH es Homebrew y no tiene sf)" >&2
  exit 1
fi

# Se elige la primera regional UTF-8 que el sistema tenga de verdad, en
# vez de dar por hecha `es_ES.UTF-8`: si no existe, `LC_ALL` apuntando a
# una regional inexistente deja a R en C otra vez y en silencio.
for loc in es_ES.UTF-8 en_US.UTF-8 C.UTF-8; do
  if locale -a 2>/dev/null | grep -qix "$(echo "$loc" | tr '[:upper:]' '[:lower:]')" \
     || locale -a 2>/dev/null | grep -qx "$loc"; then
    LC_ALL="$loc"
    break
  fi
done
: "${LC_ALL:=en_US.UTF-8}"
export LC_ALL
export LANG="$LC_ALL"

exec "$R_BUENO" "$@"
