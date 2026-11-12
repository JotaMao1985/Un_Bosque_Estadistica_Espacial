# Estadística Espacial (20929) · reglas para quien trabaje en este repo

Material HTML interactivo de un curso universitario, publicado en GitHub Pages desde
`Htmls_Espacial/`. Lo leen estudiantes: un error publicado es un error enseñado.

## Las dos normas duras

1. **Ninguna cifra a mano.** Toda cifra en pantalla sale de R (`precalculo/genera_*.R`) y la
   comprueban `precalculo/audita_capN.py` y `audita_texto_capN.py`.
2. **Ninguna cita de memoria.** No escribas un autor, un año, un título, una página, una sección,
   un DOI ni un ISBN que no hayas leído en esta sesión en la fuente o en `bibliografia/`. Una obra
   entra por Zotero (`Docencia › 20929 Estadística Espacial`) con su DOI o ISBN, buscado en la
   red. Una afirmación atribuida se contrasta contra un pasaje leído en un ejemplar local, y la
   verifica alguien que no la redactó. Lo que no se pueda contrastar se declara `propia` o
   `pendiente`: nunca se rellena. Wikipedia, blogs, salidas de IA y la memoria del modelo no
   respaldan nada. Procedimiento: `bibliografia/README.md`. Norma común de los cursos de El
   Bosque: `Bosque 2026/Vault/Estandar/Capa de fuentes.md`.

Una obra **sin ejemplar local** solo aparece como lectura recomendada (sin localizador) o como
cita de segunda mano (`data-via`), con el localizador de la obra que sí se leyó.

## Lo que rompe cosas

- **El HTML es un artefacto.** La prosa vive en `precalculo/ensambla_capN.py`; editar
  `Htmls_Espacial/*.html` a mano se pierde en el siguiente ensamblado.
- Cambiar `plantilla/plantilla-capitulo.html` obliga a reensamblar todos los documentos y a
  medir cada uno contra su tope de tamaño.
- El corpus de fuentes (PDF, texto por página, instantáneas web) vive fuera del repo, en
  `~/Documents/Trabajo 2026/Fuentes/20929/` (`precalculo/fuentes_config.py`). Nunca se copia al
  repo: es público. Los literales en `bibliografia/` no pasan de 25 palabras.
- `.gitignore` es de lista blanca: una carpeta nueva necesita su `!/carpeta/` y
  `git check-ignore -v`.
- Varias sesiones trabajan en worktrees de este repo a la vez: nunca matar procesos por nombre.

## Antes de dar algo por hecho

- `precalculo/audita_todo.sh --rapido` (minutos) y, para las fuentes,
  `python3 precalculo/audita_citas.py`.
- Lo visual se comprueba servido por HTTP (`preview_start {name:"espacial"}`), no por `file://`.

## Publicar

`git push` a `main` y el despliegue a Pages publican para los estudiantes: se consultan siempre
con Javier. Voz impersonal en la prosa expositiva.
