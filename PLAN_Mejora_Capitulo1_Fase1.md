---
tipo: plan
curso: "[[20929 Estadística Espacial]]"
capitulo: "[[20929-01 Datos espaciales y la primera ley]]"
fecha: 2026-11-13
estado: aprobado por Javier el 2026-11-13 (D1–D12 como se recomiendan)
---

# Plan — Mejora del capítulo 1 · Datos espaciales y la primera ley (Fase 1)

**Objetivo:** dejar el capítulo 1 correcto, con sus fuentes contrastadas, con un hilo que cierre lo que
abre, con gráficas que digan lo que la prosa dice y con práctica para cada objetivo. Es la primera
aplicación de la capa de fuentes ([[Capa de fuentes]], Fase GD, commits `660c176`–`34cf546`) a un
capítulo entero, y el molde para los capítulos 2–7.

Sustituye al `PLAN_Mejora_Capitulo1.md` de agosto: lo que aquel dejó abierto (prueba de aleatorización
de Snow, envolvente del correlograma, paneles de deducción, los seis mapas del módulo 2) entra aquí, y una
de sus tareas (T3.2.1, el encuadre de la «equicorrelación») se descarta porque el diagnóstico la tumba.

## 1. El hueco — diagnóstico del 2026-11-13

Cinco lecturas independientes, cada una con su lente y sin conocer las otras. Detalle, con línea y
evidencia, en `diagnostico_cap1/` (fuera de git).

| # | Lente (modelo) | Qué se encontró | Detalle |
|---|---|---|---|
| C1 | Corrección y ecuaciones (Opus) | **37 hallazgos: 7 errores** (2 altos), 20 imprecisiones, 7 lagunas, 3 de notación | `par_academico.md` |
| C2 | Fuentes (Sonnet) | **127 afirmaciones exigen fuente** (+7 del piloto): 54 alta, 55 media, 18 baja. 54 con pasaje, 26 que el corpus **matiza**, 3 que **contradice**, 44 sin pasaje | `fuentes.md`, `fuentes_inventario.tsv` |
| C3 | Hilo (Opus) | El arco no se cierra; M3 son dos módulos; M8–M9 cortan el hilo; ρ, W y «rezago» con varios sentidos; código colombiano no ejecutable desde fuera; crónica de producción en la prosa. **129 min declarados, ~156 reales** (~215 con ejercicios) | `lector_estudiante.md` |
| C4 | Gráficas (Opus) | 10 simuladores, 13 mapas, 9 Chart.js: todos dibujan y todos los controles responden. **27 hallazgos** (5 altos); seis reglas de plantilla/ensamblador explican la mitad | `graficas.md`, `capturas/` |
| C5 | Práctica (Opus) | **18 hallazgos.** E3 no se sostiene; Q4 con un distractor cierto; E2–E4 dependen de datos no publicados; la autoevaluación no toca M2, M5, M8 ni M11; la correcta es la más larga en 4 preguntas | `ejercicios.md` |

**Comprobado por la sesión maestra** (no se le cree a un subagente):
- **C1-18/19 y P-01 son el mismo error, hallado por dos lecturas distintas.** Con varianzas iguales,
  Var(Z̄) = σ²/n·(1+(n−1)ρ̄) es una identidad: la fórmula de n_eff es exacta con ρ̄, la correlación media
  entre pares, no un supuesto de «equicorrelación». Y el «ρ estimado» de `genera_cap1.R:715-800`
  (I de Moran por bandas hasta 800 km, centrada en la media muestral) está atado algebraicamente a
  −1/(n−1) si cubre todos los pares: la razón 6,88 «implícito/estimado» es un artefacto del estimador.
  **Se cae el argumento central del módulo 5, el ejercicio 3 y una pregunta del preparcial 1.**
- **G-02:** `milC` usa `es-CO` (miles con punto) en un capítulo con punto decimal: «2.621» se lee 2,6
  (`ensambla_cap1.py:2454`).
- **Numata «contradice»: no.** Son dos publicaciones de la serie: `spatstat.data` cita la parte IV (1961),
  la de los datos; Baddeley cita la VI (1964). Se aclara en la prosa, no se cambia el año.

## 2. Restricciones verificadas

- **El HTML es artefacto:** todo cambio va en `precalculo/genera_cap1.R` → JSON → `ensambla_cap1.py`;
  `audita_cap1.py`, `audita_texto_cap1.py`, `prueba_ensambla_cap1.py` y `audita_citas.py` en verde al
  cerrar cada ronda. Tope del capítulo: 720 KB (hoy 701 KB). Cambiar la plantilla obliga a reensamblar los
  13 documentos y medir sus topes.
- **El cap. 1 se reutiliza en otros documentos.** El preparcial 1 (`genera_preparcial1.R:145-148`,
  `ensambla_preparcial1.py:553-576`) enseña el mismo encuadre equivocado. El Taller 1 ya se calificó: no se
  regenera. Lo que los caps. 2–7 dicen del cap. 1 es cierto (C3) y no cambia con este plan salvo donde se
  diga.
- **Este worktree no tiene `datos/`:** las rondas que regeneran cifras corren `genera_cap1.R` contra la
  copia principal, o se le copia `datos/` (memoria «Worktrees y la carpeta `datos/`»).
- **Nada se publica sin tu visto bueno**; el repo es público.

## 3. Decisiones propuestas

Cada una lleva mi recomendación; las decides tú.

- **D1 · Cinco rondas, en este orden:** R1 errores → R2 gráficas → R3 estructura y hilo → R4 fuentes →
  R5 práctica. Cada ronda cierra con auditores en verde, revisión visual a 1280 y 375 px, commit y tu visto
  bueno.
- **D2 · Publicar R1 en cuanto esté**, sin esperar al resto: hoy el módulo 5 enseña un argumento falso.
  *Recomendado.*
- **D3 · Módulo 5, reescrito sobre lo verdadero:** la fórmula de n_eff es exacta con ρ̄; ρ̄ no se puede
  estimar con una sola realización (puente al módulo 6); el n_eff del titular sale del remuestreo por
  bloques, como ya hace. Se retiran el «ρ estimado», la razón 6,88 y el 331,7. *Recomendado.*
- **D4 · El preparcial 1 se corrige en la misma ronda** (la pregunta del ρ implícito y su
  retroalimentación), porque es material de estudio publicado. *Recomendado.*
- **D5 · Deducciones en paneles plegables** (`.derivacion`, como el de Clark–Evans): Var(Z̄) → n_eff
  exacta; E[I] = −1/(n−1); la identidad que fija el promedio de pares en −1/(n−1); y la ergodicidad del
  módulo 6, que hoy no aparece (C1-22). Gehlke–Biehl solo si entra su ejemplar (R4).
- **D6 · Notación del curso:** ventana = *W* (convención de Baddeley y `spatstat`) y matriz de pesos =
  **W** en negrita (caps. 6–7); ρ(h) correlación a distancia h, ρ̄ correlación media entre pares; el
  glosario del módulo 11 se corrige para no contradecir al capítulo. La alternativa es renombrar la
  ventana a 𝒲 en todo el curso. *Recomiendo la negrita: no obliga a tocar los caps. 4–7.*
- **D7 · Fuera la crónica de producción** de la prosa («la primera versión de este módulo», «el auditor»,
  «en la fase anterior»…). Va a los comentarios del ensamblador.
- **D8 · No renumerar módulos.** Se mueven contenidos y transiciones (Clark–Evans queda en el M3 con
  su propio subtítulo y una remisión explícita del cap. 4; M8–M9 ganan entrada y salida) y se corrigen las
  duraciones declaradas con la estimación medida.
- **D9 · Código ejecutable desde fuera:** publicar un extracto mínimo de los datos que usa el capítulo
  (como en los Talleres: `entrega/datos/cap1_*.gpkg`, producido por R) y cambiar los bloques y ejercicios
  para que lo lean. La alternativa es declarar esos bloques como demostración no reproducible.
  *Recomiendo publicar el extracto.*
- **D10 · Fuentes:** contrastar las 54 de prioridad alta y las 55 de media; las 18 de baja se reescriben
  como propias, se retiran o suben. Las 26 que el corpus matiza se corrigen en la prosa antes de citarlas.
  Los 11 «Bivand §» y el «Cressie §1.3» del glosario pierden el localizador mientras no haya ejemplar.
- **D11 · Gráficas:** las seis reglas compartidas (R-A…R-F) se arreglan **en la plantilla** y se
  reensamblan los 13 documentos; los arreglos específicos del cap. 1 van en el cap. 1. Se hacen tres
  gráficas nuevas que enseñan lo que hoy solo se dice: la prueba de aleatorización de Snow (nulo de E1),
  la envolvente nula del correlograma (M3) y los cien intervalos de confianza (M4).
- **D12 · Quién hace qué** (el método que funcionó en Series): una sola sesión escribe el capítulo en cada
  ronda; un redactor por ronda (subagente Fable 5.2) y un verificador de contexto limpio que no redactó
  (Opus 5.5); las fuentes las verifica Sonnet 5.5, con Opus en lo dudoso; las cifras las recalcula R y la
  sesión maestra las recomprueba antes de dar nada por bueno.

## 4. Tareas

| # | Ronda | Tarea | Tam. | Depende |
|---|---|---|---|---|
| T1.1 | R1 | M5 reescrito según D3: n_eff exacta con ρ̄, ρ̄ no estimable, sin «ρ estimado» ni razón 6,88; `genera_cap1.R` E.1 y sus auditores (`audita_cap1.py`, `prueba_auditor_cap1.py`) | L | — |
| T1.2 | R1 | E3 replanteado sobre lo que sí se puede medir (el remuestreo por bloques), con su solución en R | M | T1.1 |
| T1.3 | R1 | Preparcial 1: la pregunta y la retroalimentación del ρ implícito (D4) | M | T1.1 |
| T1.4 | R1 | Los otros 5 errores de C1 (ventana frente a recorte en el M2; variograma teórico en h entero; browniano; Thiessen; insesgadez de la media) y Q4 | M | — |
| T1.5 | R1 | Formato de cifras: `milC` sin separador ambiguo, `1\,000` crudo, el «5 %» que es 5,76 % (G-01, G-02, C1-20) | S | — |
| T1.6 | R1 | Las 20 imprecisiones de C1, una por una | M | T1.1–T1.5 |
| T2.1 | R2 | Plantilla: reglas R-A…R-F (banda del marcador, formato, paleta de `.geomapa`, opciones de Chart.js, alto en el teléfono, suelo de letra en px CSS); reensamblar los 13 documentos | M | R1 |
| T2.2 | R2 | Cap. 1: borde de Bogotá, río del Mosa, rejilla 28×28 frente a 16×16, eje del R², bandas del correlograma a su distancia real, paletas divergentes centradas | M | T2.1 |
| T2.3 | R2 | Los seis mapas del M2: controles, lectura al pasar, teclado y «Describir el mapa» (Fase 4 de agosto) | M | T2.1 |
| T2.4 | R2 | Tres gráficas nuevas (D11), con sus datos desde R | L | R1 |
| T3.1 | R3 | El arco: el M12 (o el cierre del M10) vuelve a la pregunta del M1 con las cifras del capítulo | M | R1 |
| T3.2 | R3 | Notación (D6) en prosa, fórmulas, glosario y código; «rezago» con un solo sentido; la I de Moran no es una correlación | M | R1 |
| T3.3 | R3 | Paneles de deducción (D5) y la ergodicidad en el M6 | M | T1.1 |
| T3.4 | R3 | Transiciones (M2→M3, M3→M4, M7→M8, M9→M10), Clark–Evans con su subtítulo, crónica de producción fuera (D7), duraciones medidas | M | T3.1 |
| T3.5 | R3 | Código ejecutable desde fuera (D9) y la instalación del entorno que el syllabus pide en la semana 1 | M | decisión D9 |
| T4.1 | R4 | Biblioteca: Cressie (1993), Tobler (1970), Gehlke y Biehl (1934), Clark y Evans (1954) por la biblioteca | M | tú |
| T4.2 | R4 | Corregir las 26 que el corpus matiza; contrastar alta y media (109), marcar, citar y registrar | L | R3, T4.1 |
| T4.3 | R4 | Pie de referencias de la plantilla generado desde Zotero (hoy manual, dice Baddeley 2015) | S | T2.1 |
| T5.1 | R5 | Quiz: preguntas para M2, M5 y M8; longitudes iguales; V/F sin absolutos delatores; D1 al módulo correcto; D6 coherente con Q8 | M | R3 |
| T5.2 | R5 | Ejercicios: E1 con su nulo (aleatorización), E2 y E3 con la respuesta pedida en la tabla y con código; 3–4 ejercicios nuevos con datos publicados (N1–N6 de `ejercicios.md`) | L | R3, T2.4 |

## 5. Criterios de aceptación

- Ningún hallazgo de prioridad alta de C1–C5 sin cerrar o declarar; cada uno anotado con su ronda.
- `audita_cap1.py`, `audita_texto_cap1.py`, `prueba_auditor_cap1.py`, `prueba_ensambla_cap1.py`,
  `audita_citas.py --cierre` (sin `pendiente` en alta y media) y `verifica_bloques.py` en verde; el
  preparcial 1 con su auditor en verde.
- Cada ronda: un verificador independiente sobre el diff; capturas a 1280 y 375 px sin desbordes.
- Duraciones declaradas dentro de ±15 % de la estimación medida.

## 6. Riesgos

| Riesgo | Mitigación |
|---|---|
| El cambio del M5 arrastra cifras a otros documentos | El preparcial 1 entra en R1; `grep` de cada campo retirado del JSON en todo `precalculo/` antes de borrarlo |
| La plantilla cambia los 13 documentos | Reensamblado general en R2 con topes medidos, como en el cap. 7 |
| El arreglo crea un error nuevo | Verificador que no redactó en cada ronda (en Series encontró 7 problemas en lo «corregido») |
| Sin ejemplares, R4 se queda corta | Lo que no se pueda contrastar queda `pendiente` con motivo, nunca rellenado |
| Otra sesión toca el cap. 1 a la vez | Una sola sesión escribe el capítulo; comprobar ramas abiertas (coma decimal, mapas descritos) antes de cada ronda |

## 7. Preguntas abiertas

1. ¿Apruebas D1–D12, o cambias alguna?
2. D9: ¿publicamos el extracto de datos del capítulo (unos MB en `entrega/datos/`)?
3. Hay dos ramas sin fusionar que tocan el cap. 1, comprobado el 2026-11-13: la coma decimal
   (`5b2590a`, en `claude/goofy-spence-03c9b5`) y los mapas descritos (`claude/mapas-descritos`, 7 commits;
   `05b34e2` ya pone «Describir el mapa» en los trece mapas del cap. 1, que es parte de T2.3).
   *Recomiendo integrarlas antes de R1*: si no, cada ronda las deja más lejos de fusionar.
4. ¿Puedes conseguir por la biblioteca Cressie (1993), Tobler (1970), Gehlke y Biehl (1934) y Clark y
   Evans (1954)?

## 8. Enlaces

- Diagnóstico: `diagnostico_cap1/` (par_academico, fuentes, lector_estudiante, graficas, ejercicios).
- Capa de fuentes: `bibliografia/README.md`, `bibliografia/contraste/cap1.yml`.
- Plan anterior: `PLAN_Mejora_Capitulo1.md` (agosto).
