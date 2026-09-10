# =====================================================================
# ESTE ARCHIVO SE GUARDA EN UTF-8 **CON BOM**. NO SE LO QUITES.
#
# Windows PowerShell 5.1 —el que trae Windows de serie, no el 7— lee los
# `.ps1` como Windows-1252 salvo que encuentre el BOM. Sin él, cada tilde
# de los mensajes de abajo sale rota y el guion NO falla:
#
#     PARADO: no se ve 'precalculo\utf8.R' desde aquA-.
#     EstA?s en: C:\curso\precalculo
#
# Medido en un Windows 11 de verdad, no deducido. Y es el mismo patrón que
# persigue `utf8.R` desde el otro lado: la operación que devuelve algo
# plausible en vez de fallar. La salida alternativa —escribir los mensajes
# sin tildes— es la que este proyecto ya rechazó una vez, cuando
# `casos_territoriales.json` esquivó el problema poniendo «Choco» y
# «Belen de Bajira»: un síntoma disfrazado de decisión.
#
# Muchos editores de Mac y Linux guardan UTF-8 sin BOM por defecto. Si
# tocas este archivo desde uno, comprueba que sigue empezando por EF BB BF.
# La guarda de abajo lo dice en voz alta si se pierde.
# =====================================================================

# =====================================================================
# rscript.ps1 — el modo correcto de invocar R en este proyecto, en Windows
#
# Material de Estadística Espacial 2026-II (20929).
#
# Hermano de `rscript.sh`, y NO hace lo mismo. La diferencia es el punto:
# de las dos trampas que resuelve el `.sh`, en Windows una cambia de
# forma y la otra desaparece.
#
#   1. EL R EQUIVOCADO — cambia de forma.
#
#      En macOS hay dos R y solo una tiene `sf`, así que el `.sh` codifica
#      la ruta de la buena. En Windows el problema no es que sobre un R:
#      es que **`Rscript.exe` no está en el `PATH`** —el instalador de
#      CRAN no lo añade— y que pueden convivir varias versiones bajo
#      `C:\Program Files\R\`. Cada versión tiene **su propia biblioteca de
#      usuario**, así que arrancar la 4.6 cuando `sf` se instaló bajo la
#      4.4 da «there is no package called 'sf'» sin que nada explique por
#      qué. Por eso este envoltorio BUSCA el R y prefiere la versión con
#      la que se congeló el material, que lee de `versiones.json` en vez
#      de repetirla aquí: si el material se regenera con otra R, el
#      envoltorio la sigue solo.
#
#   2. LA CODIFICACIÓN — desaparece, y por eso este archivo no la promete.
#
#      Aquí no hay nada que fijar. Desde R 4.2 la compilación UCRT de
#      Windows usa UTF-8 como codificación nativa, así que `Rscript` NO
#      arranca en `LC_CTYPE=C` como en macOS. Y si la máquina fuera vieja,
#      este envoltorio tampoco podría arreglarlo: `LC_ALL=es_ES.UTF-8` no
#      es sintaxis de Windows —las regionales se llaman
#      `Spanish_Colombia.utf8`— y apuntar a una inexistente deja a R en C
#      otra vez y **en silencio**, que es exactamente el fallo que se
#      persigue.
#
#      Así que la comprobación se queda donde ya vive y sabe parar:
#      `utf8.R`, que corre como primera línea de cada generador. Este
#      archivo no verifica UTF-8. Lo verifica `utf8.R`.
#
#   3. EL DIRECTORIO — una tercera que el `.sh` no tiene.
#
#      Todo generador sourcea `precalculo/utf8.R` como ruta relativa a la
#      carpeta del curso. Corriéndolo desde `precalculo\`, el error que
#      sale es «no se puede abrir la conexión» sobre un archivo que sí
#      existe, y se pierde un rato entendiéndolo. Se comprueba antes de
#      arrancar R.
#
# ---------------------------------------------------------------------
# Uso, desde la carpeta `Estadistica espacial`:
#
#     .\precalculo\rscript.ps1 precalculo\genera_cap1.R
#
# LA PRIMERA VEZ PowerShell SE VA A NEGAR. No es un fallo del archivo: es
# la directiva de ejecución, que por defecto bloquea todo `.ps1`, y más si
# el repositorio se bajó como ZIP —Windows le pone la «marca de la web» a
# cada archivo que viene de fuera—. Cualquiera de estas sirve:
#
#     Unblock-File .\precalculo\rscript.ps1
#     Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#
#   ...o invocarlo sin tocar nada, que no deja rastro en la máquina:
#     powershell -ExecutionPolicy Bypass -File .\precalculo\rscript.ps1 precalculo\genera_cap1.R
#
# Para fijar un R concreto y saltarse la búsqueda:
#     $env:R_ESPACIAL = 'C:\Program Files\R\R-4.4.1\bin\Rscript.exe'
#
# AVISO SOBRE `-e`: PowerShell 5.1 estropea las comillas al pasárselas a
# un programa nativo, y además el acento grave es su carácter de escape,
# así que l10n_info()$`UTF-8` no sobrevive escrito tal cual. Para una
# línea suelta usa [["UTF-8"]] y comillas simples por fuera; para algo más
# largo, escríbelo en un `.R` y pasa el archivo.
# =====================================================================

# AQUI NO HAY param(), Y ES DELIBERADO.
#
# La versión con `[Parameter(ValueFromRemainingArguments)]` parecía la
# correcta y rompía el uso mejor documentado del `.sh`:
#
#     .\precalculo\rscript.ps1 -e 'cat(1)'
#     #> Parameter cannot be processed because the parameter name 'e' is
#     #>   ambiguous. Possible matches include: -ErrorAction -ErrorVariable.
#
# Basta un solo atributo `[Parameter()]` para que PowerShell trate el
# guion como «avanzado» y le añada los parámetros comunes de cmdlet. A
# partir de ahí `-e` deja de ser un argumento para R y pasa a ser un
# prefijo ambiguo de dos parámetros de PowerShell. Sin `param()` no hay
# parámetros declarados, no hay comunes que heredar, y todo lo que llegue
# cae en `$args` tal cual, que es justo lo que hace `exec "$@"` en el .sh.
$Guion = @($args)

# Nada de Set-StrictMode: este guion tiene que sobrevivir a máquinas que
# no se pueden probar desde aquí, y en modo estricto un `$null` benigno
# —una variable de entorno que no existe, una clave del registro vacía—
# se vuelve error fatal. Las comprobaciones van explícitas, una a una.
$ErrorActionPreference = 'Stop'

# LA CODIFICACIÓN TIENE DOS CAPAS, Y EL BOM SOLO ARREGLA UNA.
#
# El BOM de arriba resuelve cómo PowerShell LEE este archivo. Pero la
# consola de Windows sigue ESCRIBIENDO en una página de códigos heredada
# —437 o 850 según la instalación— que no tiene tildes, así que los
# mensajes salían igual de rotos, solo que de otra manera: con el BOM
# puesto, «aquí» pasó de «aquA-» (dos caracteres mal leídos) a «aqu?» (un
# carácter bien leído que la consola no sabe pintar). Dos fallos distintos
# con el mismo aspecto, y arreglar el primero no toca el segundo.
#
# Medido en un Windows 11 real, en ese orden y por ese camino.
try {
  [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false
} catch {
  # Si la consola no deja cambiarla, se sigue: un mensaje con los acentos
  # rotos es peor que uno con acentos, pero mucho mejor que no arrancar.
}

# Comprueba lo que de verdad importa —que los literales de ESTE archivo se
# hayan leído como UTF-8— en vez del nombre de una codificación. Si el BOM
# se perdió, PowerShell 5.1 leyó 'ó' como los dos caracteres 'Ã³' y esto
# vale 2. Avisa y sigue: un mensaje con tildes rotas es feo, pero parar el
# precálculo entero por ello sería peor que el defecto.
if ('ó'.Length -ne 1) {
  [Console]::Error.WriteLine(
    "rscript.ps1: OJO, este archivo perdió su BOM UTF-8 y PowerShell lo " +
    "leyó como Windows-1252; los acentos de los mensajes van a salir rotos. " +
    "Vuelve a guardarlo como UTF-8 con BOM.")
}

function Parar([string] $mensaje) {
  [Console]::Error.WriteLine("PARADO: $mensaje")
  exit 1
}

function Avisar([string] $mensaje) {
  [Console]::Error.WriteLine("rscript.ps1: $mensaje")
}

# ---------------------------------------------------------------------
# 3. El directorio, primero: es lo más barato de comprobar y lo que más
#    veces muerde.
# ---------------------------------------------------------------------
if (-not (Test-Path -LiteralPath 'precalculo\utf8.R')) {
  $curso = Split-Path -Parent $PSScriptRoot
  $msg = @"
no se ve 'precalculo\utf8.R' desde aquí.

        Estás en:            $((Get-Location).Path)
        La carpeta del curso es: $curso

        Los generadores resuelven sus source() contra la carpeta del
        curso, no contra la suya. Hay que invocarlos desde ella:

            cd '$curso'
            .\precalculo\rscript.ps1 precalculo\genera_cap1.R
"@
  Parar $msg
}

# ---------------------------------------------------------------------
# 1. El R. Se juntan todos los candidatos y luego se elige, en vez de
#    quedarse con el primero que aparezca: cuál es el bueno depende de la
#    versión, y eso no se sabe hasta tenerlos todos.
# ---------------------------------------------------------------------
$candidatos = New-Object System.Collections.Generic.List[string]

if ($env:R_ESPACIAL) {
  if (-not (Test-Path -LiteralPath $env:R_ESPACIAL)) {
    Parar "R_ESPACIAL apunta a '$env:R_ESPACIAL', que no existe."
  }
  $candidatos.Add((Resolve-Path -LiteralPath $env:R_ESPACIAL).Path)
}
else {
  # El registro es donde mira RStudio, y lo escribe el instalador de CRAN.
  # La clave raíz trae la instalación «actual» y cada subclave una versión.
  foreach ($raiz in @('HKLM:\SOFTWARE\R-core\R', 'HKLM:\SOFTWARE\R-core\R64',
                      'HKCU:\SOFTWARE\R-core\R', 'HKCU:\SOFTWARE\R-core\R64')) {
    # -ErrorAction aquí no es adorno: con $ErrorActionPreference = 'Stop',
    # consultar una unidad HKLM: que no existe LANZA en vez de devolver
    # falso. En Windows siempre existe, así que no se notaría; fuera de
    # Windows el envoltorio moriría antes de poder decir nada útil.
    if (-not (Test-Path $raiz -ErrorAction SilentlyContinue)) { continue }
    $claves = @($raiz)
    $claves += @(Get-ChildItem $raiz -ErrorAction SilentlyContinue |
                 ForEach-Object { $_.PSPath })
    foreach ($clave in $claves) {
      $prop = Get-ItemProperty -Path $clave -Name InstallPath -ErrorAction SilentlyContinue
      if ($prop -and $prop.InstallPath) {
        $exe = Join-Path $prop.InstallPath 'bin\Rscript.exe'
        if (Test-Path -LiteralPath $exe) { $candidatos.Add($exe) }
      }
    }
  }

  # Y las rutas por defecto del instalador, por si el registro no dice nada.
  # NO es un caso raro: instalado en silencio (/VERYSILENT) el instalador de
  # CRAN no escribe la clave, y además cae en `Program Files (x86)` y no en
  # `Program Files`, porque su Inno Setup es de 32 bits. Comprobado en un
  # Windows 11 real: registro vacío, R en (x86), y esta lista es lo único
  # que quedaba para encontrarlo.
  #
  # `LOCALAPPDATA` es el caso del que no tiene permisos de administrador
  # —una máquina de universidad, un portátil corporativo—: ahí el
  # instalador no puede escribir en Program Files y se va al perfil del
  # usuario sin avisar de que ha cambiado de sitio.
  $bases = @()
  foreach ($pf in @($env:ProgramFiles, ${env:ProgramFiles(x86)}, $env:LOCALAPPDATA)) {
    if ($pf) { $bases += (Join-Path $pf 'R'); $bases += (Join-Path $pf 'Programs\R') }
  }
  $bases += 'C:\R'
  foreach ($base in $bases) {
    if (-not (Test-Path -LiteralPath $base)) { continue }
    Get-ChildItem -LiteralPath $base -Directory -Filter 'R-*' -ErrorAction SilentlyContinue |
      ForEach-Object {
        $exe = Join-Path $_.FullName 'bin\Rscript.exe'
        if (Test-Path -LiteralPath $exe) { $candidatos.Add($exe) }
      }
  }

  # El PATH va de último: si alguien lo añadió a mano, que no gane por eso.
  $enPath = Get-Command 'Rscript.exe' -ErrorAction SilentlyContinue
  if ($enPath) { $candidatos.Add($enPath.Source) }
}

$candidatos = @($candidatos | Sort-Object -Unique)

if ($candidatos.Count -eq 0) {
  $msg = @"
no encontré ningún Rscript.exe.

        Busqué en el registro (HKLM y HKCU, SOFTWARE\R-core\R),
        en '$env:ProgramFiles\R\R-*\bin\' y en el PATH.

        Instala R desde https://cran.r-project.org/bin/windows/base/
        —hace falta 4.2 o superior por lo del UTF-8, y el material se
        congeló con la 4.4— o fija la ruta a mano:

            `$env:R_ESPACIAL = 'C:\Program Files\R\R-4.4.1\bin\Rscript.exe'
"@
  Parar $msg
}

# ---------------------------------------------------------------------
# Cuál de todos. La versión congelada sale de versiones.json y no de una
# constante escrita aquí: dos sitios que dicen la misma cifra terminan
# discrepando, y este envoltorio sería el que se entera tarde.
# ---------------------------------------------------------------------
$fijada = $null
if (Test-Path -LiteralPath 'precalculo\versiones.json') {
  try {
    $r = (Get-Content -LiteralPath 'precalculo\versiones.json' -Raw |
          ConvertFrom-Json).r
    if ($r -match '(\d+)\.(\d+)\.(\d+)') { $fijada = [version] $Matches[0] }
  }
  catch {
    Avisar "no pude leer versiones.json ($($_.Exception.Message)); sigo sin preferencia de versión."
  }
}

$conVersion = @($candidatos | ForEach-Object {
  $v = $null
  if ($_ -match 'R-(\d+\.\d+\.\d+)') { $v = [version] $Matches[1] }
  [pscustomobject] @{ exe = $_; v = $v }
})

$elegido = $null
if ($fijada) {
  $elegido = @($conVersion | Where-Object { $_.v -eq $fijada })[0]
  if (-not $elegido) {
    $elegido = @($conVersion |
                 Where-Object { $_.v -and $_.v.Major -eq $fijada.Major -and $_.v.Minor -eq $fijada.Minor } |
                 Sort-Object v -Descending)[0]
  }
}
if (-not $elegido) {
  $elegido = @($conVersion | Where-Object { $_.v } | Sort-Object v -Descending)[0]
}
if (-not $elegido) { $elegido = $conVersion[0] }

# ---------------------------------------------------------------------
# Se habla solo cuando hay algo que decir. Con un único R y siendo el
# congelado, callar es lo correcto: el `.sh` tampoco saluda. Pero si hay
# varios, o si el que va a correr no es el del material, eso tiene que
# verse — con una biblioteca de usuario por versión, «me cogió otra R» se
# manifiesta como «no existe sf», que no se parece en nada a su causa.
# ---------------------------------------------------------------------
if ($candidatos.Count -gt 1) {
  Avisar "hay $($candidatos.Count) instalaciones de R en esta máquina; uso $($elegido.exe)"
}
if ($fijada -and $elegido.v -and $elegido.v -ne $fijada) {
  Avisar "OJO: el material se congeló con R $fijada y vas a correr R $($elegido.v)."
  Avisar "     Las cifras publicadas salieron de la otra. Si algo no cuadra, empieza por aquí."
}

& $elegido.exe @Guion
exit $LASTEXITCODE
