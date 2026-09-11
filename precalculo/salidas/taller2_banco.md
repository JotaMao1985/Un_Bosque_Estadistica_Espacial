# El banco del Taller 2, legible desde fuera

Lo escribe `precalculo/ensambla_taller2.py` cada vez que construye el taller.
**No se edita a mano.**

Existe por el riesgo alto del §10 del `PLAN_Taller_2_Cap_4.md`: el parcial 2 cubre
los capítulos 4 y 5, y este banco se publica con el taller. Una pregunta repetida
entre los dos documentos es una respuesta ya publicada. Quien escriba el *blueprint*
del parcial (`PLAN_Parcial_Corte_2.md`, T1.1) tiene que leer esta lista y decidir:
evitarlas, o reutilizarlas **a propósito** y declararlo.

## Las 36 preguntas del banco

1. **[mód. 1 · La ventana es parte del estimador]** En los tres capítulos anteriores el dato traía su sitio puesto y lo que variaba era el valor. Aquí se invierte. Di qué es exactamente lo aleatorio en un patrón puntual, y qué cosa de los capítulos anteriores deja de existir cuando se invierte.
2. **[mód. 1 · Coordenadas sin ventana]** Alguien te entrega las coordenadas de un patrón y nada más. ¿Qué no puedes calcular todavía, y por qué no basta con dibujar un rectángulo alrededor de los puntos?
3. **[mód. 1 · Del punto al área]** Un mismo fenómeno se puede estudiar como patrón puntual o agregado a unidades areales. ¿Qué se pierde al pasar del primero al segundo, y qué se gana?
4. **[mód. 2 · Cuándo describe λ al patrón]** El estimador de λ es una división. ¿Bajo qué condición ese único número describe el patrón, y cómo comprobarías si se cumple sin correr ningún test?
5. **[mód. 2 · El índice de dispersión que no vale 1]** «Bajo Poisson el índice de dispersión vale 1» es falso en cuanto las celdas no miden lo mismo. Explica por qué, y di contra qué habría que compararlo en su lugar.
6. **[mód. 2 · Inhomogénea no es agregada]** Que λ dependa de la posición y que los puntos se atraigan producen mapas parecidos y son cosas distintas. Explica la diferencia y di por qué se confunden tanto.
7. **[mód. 3 · Qué mecanismo produce cada régimen]** Los tres regímenes son aleatorio, regular y agregado. Di qué mecanismo físico produce cada uno, y por qué «regular» no quiere decir «ordenado en cuadrícula».
8. **[mód. 3 · De dónde sale el denominador]** Clark-Evans divide la distancia media observada al vecino más próximo por la que daría el azar. ¿De dónde sale ese denominador, y qué tendría que pasar para que la división dejara de ser informativa?
9. **[mód. 3 · Agregado aquí, regular allá]** Un patrón puede estar agregado a una escala y ser regular a otra. ¿Qué le pasa entonces al índice de Clark-Evans, y qué habría que medir para verlo?
10. **[mód. 4 · Dos realizaciones, dos n]** Dos realizaciones del mismo proceso de Poisson homogéneo no tienen el mismo número de puntos. ¿Por qué, y qué error comete quien espera que sí?
11. **[mód. 4 · La firma de Poisson]** Que la media y la varianza del número de puntos valgan aproximadamente lo mismo es la firma de Poisson. ¿Por qué ninguna otra distribución de conteos hace eso, y cómo lo comprobarías simulando?
12. **[mód. 4 · Cuánto se mueve el azar]** Sobre realizaciones de CSR puro, el índice de Clark-Evans recorre un intervalo ancho y su media no cae exactamente en 1. Son dos hechos distintos: explica cada uno.
13. **[mód. 4 · Una nula que casi nunca es cierta]** CSR es la hipótesis nula de casi todo el capítulo, y en datos reales casi nunca se cumple. ¿Por qué se usa igual como referencia? ¿Qué se gana?
14. **[mód. 4 · Qué falla cuando falla]** Rechazar CSR no dice cuál de sus dos propiedades falla. Describe un patrón concreto donde falle una y otro donde falle la otra, y di cómo los distinguirías.
15. **[mód. 4 · «Se ve aleatorio»]** Un colega mira un mapa y dice que el patrón «se ve aleatorio». ¿Por qué eso no es un argumento, y qué es lo mínimo que habría que enseñar para convertirlo en uno?
16. **[mód. 5 · Contra qué se contrasta]** La hipótesis nula del test de cuadrantes no es «λ es constante». ¿Cuál es, y por qué esa diferencia cambia lo que puedes afirmar cuando rechazas?
17. **[mód. 5 · Los esperados de una celda recortada]** Cuando la ventana recorta las celdas, los esperados dejan de ser iguales entre sí. ¿De dónde salen entonces, y qué pasaría si los repartieras por igual de todos modos?
18. **[mód. 5 · El convenio del binado]** El binado de quadratcount es el de cut(): abierto por la izquierda, con el más bajo cerrado por los dos lados. ¿Por qué ese convenio puede mover el χ², y en qué clase de datos lo mueve más?
19. **[mód. 6 · Resolver contra suponer]** «La escala que más resuelve es la que rompe el supuesto.» Explica esa tensión y di qué hace con ella un analista honesto.
20. **[mód. 6 · El MAUP con otro nombre]** El tamaño del cuadrante y el tamaño de la unidad areal del capítulo 3 son el mismo problema. Di en qué son el mismo y en qué no.
21. **[mód. 6 · Qué falta en el pie]** ¿Qué tiene que aparecer siempre junto al resultado de un test de cuadrantes para que sea reproducible, y por qué sin eso el resultado está incompleto?
22. **[mód. 7 · Las dos y el borde]** G y F se estiman sobre una ventana finita, así que las dos sufren el efecto de borde. ¿Lo sufren igual? Di cuál se ve más afectada y por qué.
23. **[mód. 7 · Los sitios de F]** F se mide desde sitios cualesquiera de la ventana. ¿Cómo se eligen esos sitios en la práctica, y qué decisión del analista se esconde ahí?
24. **[mód. 7 · Misma G, distinta F]** Dos patrones tienen la misma G y distinta F. ¿Qué sabes de ellos? ¿Y si tuvieran la misma F y distinta G?
25. **[mód. 8 · Por qué se divide por λ]** K(r) es el número esperado de vecinos a distancia r o menos de un punto cualquiera, dividido por la intensidad. ¿Por qué se divide por la intensidad, y qué se consigue?
26. **[mód. 8 · La recta de Besag]** La transformación de Besag convierte una parábola en una recta. Si la información es la misma, ¿por qué importa para leer la curva?
27. **[mód. 8 · Los pesos del estimador]** El estimador de K lleva unos pesos que multiplican cada pareja de puntos. ¿Qué papel juegan, y qué estarías estimando si todos valieran 1?
28. **[mód. 9 · El anillo y el disco]** g(r) mira el anillo de radio r y K(r) el disco entero. ¿Qué gana g con eso, y qué pierde?
29. **[mód. 9 · La distancia a la que g vuelve a 1]** La distancia a la que g regresa a 1 se lee como una propiedad física del patrón. ¿Cuál es, y qué tendrías que ver en el mapa para confirmarla?
30. **[mód. 9 · Un máximo en el borde izquierdo]** En un patrón real, g puede no tener pico y alcanzar su máximo en el primer nodo del barrido. ¿Qué significa eso, y por qué NO es una escala característica?
31. **[mód. 10 · Lo que cuesta corregir]** Las tres correcciones clásicas corrigen, y no cuestan lo mismo. ¿Cuál es la cara, por qué lo es, y en qué clase de ventana se nota la diferencia?
32. **[mód. 10 · Descartar o pesar]** La corrección de borde descarta puntos y la de traslación los pesa. ¿Qué le pasa a la precisión del estimador con cada una, y por qué?
33. **[mód. 10 · Por qué crece con r]** El efecto de borde no pesa igual a todas las distancias. Explica qué fracción de los discos toca el borde a r pequeño y a r grande, y qué se sigue de ahí.
34. **[mód. 11 · Las simulaciones contra su propia banda]** Construyes una banda con simulaciones de CSR y después compruebas cuántas de esas MISMAS simulaciones se salen de ella en algún r. ¿Qué esperarías encontrar, y por qué?
35. **[mód. 11 · Dos resúmenes de la misma curva]** Un test de desviación global resume la curva entera en un número antes de compararla. Di qué resumen usa el dclf y cuál el MAD, y ante qué clase de desviación se separan.
36. **[mód. 11 · Simular con la misma ventana]** La envolvente simula CSR con la misma ventana y la misma intensidad que el patrón observado. ¿Por qué las dos cosas tienen que ser las mismas? ¿Qué pasaría si simularas sobre un rectángulo?

## Las 12 afirmaciones falsas de la refutación en vivo

Todas son FALSAS. Se leen en voz alta, una por estudiante.

1. **[mód. 5]** El test de cuadrantes contrasta la hipótesis de que λ es constante.
2. **[mód. 11]** La banda de una envolvente es un intervalo de confianza para la K verdadera del patrón observado.
3. **[mód. 4]** Si un patrón no rechaza el test de cuadrantes, se puede concluir que es CSR.
4. **[mód. 10]** Ignorar la corrección de borde le añade ruido a la estimación de K, pero no la sesga.
5. **[mód. 2]** El estimador n/|W| devuelve la intensidad en las unidades del fenómeno, sea cual sea el sistema de coordenadas.
6. **[mód. 7]** F(r) se calcula sobre los puntos del patrón, igual que G(r), pero midiendo hacia atrás.
7. **[mód. 8]** La transformación de Besag no es solo un cambio de forma: L detecta estructura que K no llega a ver.
8. **[mód. 10]** Las tres correcciones de borde devuelven la misma curva K; solo se diferencian en el tiempo de cómputo.
9. **[mód. 1]** En un patrón puntual el dato es la posición, así que los mismos puntos observados en dos ventanas distintas son el mismo patrón.
10. **[mód. 6]** El tamaño de la celda del test de cuadrantes es un detalle de implementación: el veredicto no depende de él.
11. **[mód. 9]** El máximo de g(r) señala el tamaño de los grumos del patrón.
12. **[mód. 3]** El índice de Clark-Evans mira todas las escalas del patrón a la vez.
