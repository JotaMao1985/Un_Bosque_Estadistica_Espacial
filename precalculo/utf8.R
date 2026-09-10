# =====================================================================
# utf8.R — la guarda de codificación que todo generador debe cargar
#
# Material de Estadística Espacial 2026-II (20929).
#
# EL PROBLEMA, encontrado en T0.5 y que venía de antes.
#
# `Rscript` arranca con `LC_CTYPE=C` salvo que el entorno diga otra cosa.
# En ese estado R no sabe que sus cadenas son UTF-8:
#
#     Sys.getlocale("LC_CTYPE")   #> "C"
#     l10n_info()$`UTF-8`         #> FALSE
#     Encoding("Deserción")       #> "unknown"
#     nchar("Deserción")          #> 10   (bytes, no caracteres)
#     jsonlite::toJSON("Deserción")
#     #> ["Deserci<c3><b3>n"]
#
# Es decir: **`jsonlite` escribe los bytes crudos entre corchetes angulares
# y no falla**. El JSON es sintácticamente válido, el script termina con
# éxito, y la tilde llega al navegador convertida en `<c3><b3>`.
#
# Ya había hecho daño antes de encontrarse: `saber11_20224_cifras.json`
# de T0.4 llevaba cuatro etiquetas corrompidas —«Educaci<c3><b3>n
# profesional completa» entre ellas—, que son justo los niveles de
# educación de la madre con los que el material mide la falacia
# ecológica. Y `casos_territoriales.json` esquivó el problema escribiendo
# «Belen de Bajira» y «Choco» sin tildes, que es un síntoma disfrazado de
# decisión.
#
# Es el mismo patrón que el `iconv` de A.7, el `"" == "Si"` de A.8 y el
# `sprintf("%05d", NA)` de A.9: **la operación que devuelve algo plausible
# en vez de fallar**. Por eso esta guarda **para** en vez de avisar. Un
# generador que no puede escribir tildes no debe escribir nada.
#
# POR QUÉ ESTA GUARDA RECHAZA EN VEZ DE REPARAR — y costó descubrirlo.
#
# La primera versión llamaba a `Sys.setlocale("LC_CTYPE", "es_ES.UTF-8")`
# y daba el problema por resuelto. **No lo resuelve.** R **parsea el
# archivo entero antes de ejecutar su primera línea**, así que cuando el
# `source()` de esta guarda se ejecuta, los literales acentuados del
# script que la llamó YA se leyeron bajo `LC_CTYPE=C` y están marcados
# como «unknown». Cambiar la configuración regional después no los
# rescata.
#
# El síntoma es de los peores: la guarda informaba «UTF-8 verificado» —su
# propia prueba pasaba, porque los literales de ESTE archivo sí se
# parsearon después— y el JSON seguía saliendo con `<c3><b3>`. Una guarda
# que se autoaprueba es peor que no tener guarda.
#
# Por eso ahora comprueba el estado **de arranque** del proceso y para.
#
# Uso, como PRIMERA línea de todo `genera_*.R` y `datos_*.R`:
#
#     source("precalculo/utf8.R")
#
# Y se invoca SIEMPRE con el envoltorio de la plataforma, que resuelve
# de una vez el R correcto:
#
#     precalculo/rscript.sh   precalculo/genera_loquesea.R    (macOS)
#     .\precalculo\rscript.ps1 precalculo\genera_loquesea.R    (Windows)
#
# Los dos NO hacen lo mismo, y conviene saberlo antes de leer el mensaje
# de parada de abajo. En macOS el `.sh` **fija** la regional, porque
# `Rscript` arranca en `LC_CTYPE=C`. En Windows no hay nada que fijar
# —desde R 4.2 la compilación UCRT ya es UTF-8 nativa— y tampoco se
# podría: `LC_ALL=es_ES.UTF-8` no es sintaxis de allí. Por eso allí el
# remedio no es un envoltorio sino una versión de R, y por eso esta
# guarda tiene que decir cosas distintas según dónde corra: mandar a
# alguien a `rscript.sh` desde Windows es mandarlo a un archivo que no
# existe.
# =====================================================================

local({
  if (!isTRUE(l10n_info()$`UTF-8`)) {
    # Con `-e` no hay ningún .R en commandArgs, y el mensaje terminaba
    # diciendo «rscript.sh NA»: una instrucción que no se puede copiar.
    args  <- commandArgs(trailingOnly = FALSE)
    guion <- args[grepl("\\.R$", args)][1]
    if (is.na(guion)) guion <- ""

    remedio <- if (.Platform$OS.type == "windows") {
      paste0(
        "  En Windows esto no lo arregla ningún envoltorio: es la versión de R.\n",
        "  Desde R 4.2 la compilación UCRT usa UTF-8 como codificación nativa,\n",
        "  así que si estás viendo esto tu R es anterior a 4.2, o no es UCRT.\n",
        "  Instala R 4.4 desde https://cran.r-project.org/bin/windows/base/\n",
        "  y vuelve a correr:\n\n",
        "      .\\precalculo\\rscript.ps1 ", guion, "\n\n",
        "  (LC_ALL=es_ES.UTF-8 no sirve aquí: las regionales de Windows se\n",
        "   llaman Spanish_Colombia.utf8, y apuntar a una que no existe deja\n",
        "   a R en C otra vez y en silencio.)")
    } else {
      paste0(
        "  Hay que arrancar el proceso ya en UTF-8:\n\n",
        "      precalculo/rscript.sh ", guion, "\n\n",
        "  (o  LC_ALL=es_ES.UTF-8 Rscript ...)")
    }

    stop("PARADO: R arrancó con LC_CTYPE = \"", Sys.getlocale("LC_CTYPE"),
         "\", que no es UTF-8.\n",
         "  En ese estado jsonlite escribe las tildes como <c3><b3> y NO falla:\n",
         "    jsonlite::toJSON(\"Deserción\")  #> [\"Deserci<c3><b3>n\"]\n",
         "  y el material saldría corrompido en silencio.\n\n",
         "  No se arregla desde aquí: R parsea el archivo ENTERO antes de\n",
         "  ejecutar nada, así que tus literales acentuados ya se leyeron mal.\n\n",
         remedio,
         call. = FALSE)
  }

  # La prueba de humo va sobre el efecto que importa —lo que jsonlite
  # ESCRIBE—, no sobre el nombre de la configuración regional. Un locale
  # con nombre correcto y comportamiento roto ya nos ha pasado.
  muestra <- jsonlite::toJSON("Deserción — Chocó, Bogotá D.C.", auto_unbox = TRUE)
  if (grepl("<[0-9a-f]{2}>", muestra)) {
    stop("PARADO: la configuración regional dice ser UTF-8 (",
         Sys.getlocale("LC_CTYPE"), ") pero jsonlite sigue escribiendo bytes crudos:\n  ",
         muestra, call. = FALSE)
  }
  message("utf8.R: LC_CTYPE = ", Sys.getlocale("LC_CTYPE"), " (UTF-8 verificado al arranque)")
})
