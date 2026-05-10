### SLIDE 1 — Título
- El IPC mide una persona promedio que no existe
- Hoy presento por qué eso importa

"Buenas, mi nombre es Javier Spina y el nodo que voy a presentar se llama Inflación heterogénea y poder adquisitivo en Argentina. La pregunta que motiva el trabajo es simple: cuando los precios suben, ¿todos pierden por igual? La respuesta corta es que no, y eso es lo que voy a tratar de mostrar hoy."

#### Título → Introducción
> "Para entender por qué me hago esa pregunta, arranco por algo que todos vivimos."


### SLIDE 2 — Introducción

- Inflación: todos la conocemos, pocos la miden bien
- El IPC promedia canastas distintas
- El que gasta en alimentos y el que gasta en alquiler no enfrentan la misma inflación

"Para arrancar, algo que todos conocemos. La inflación en Argentina no es una novedad — es persistente, recurrente, aparece en las noticias, en las paritarias, en la charla cotidiana. Pero hay algo que el debate público suele pasar por alto: el índice que usamos para medirla, el IPC, pondera el gasto de un hogar promedio que en realidad no existe. Porque quien gasta la mitad de su sueldo en alimentos tiene una experiencia de inflación completamente distinta a quien gasta esa misma proporción en servicios o alquiler. El IPC los trata igual. Y eso es un problema."

#### Introducción → Contexto
> "Este no es un problema nuevo ni menor — tiene raíces históricas y una dimensión distributiva que el debate público suele ignorar."


### SLIDE 3 — Contexto
- Historia de inflación y shocks: el paisaje económico de las últimas décadas
- Las canastas son distintas según quién sos y dónde vivís
- En alta inflación pierden más los pobres, en baja inflación el IPC los invisibiliza — en los dos escenarios salen perdiendo
- El INDEC mide con canastas de 2004, la actualización no se implementó
- Hay sectores que sistemáticamente pierden y otros que ganan, pero no sabemos quiénes ni cuánto

"Argentina tiene una historia larga de alta inflación y shocks económicos. Pero el problema no es solo macroeconómico — tiene una dimensión distributiva que el debate público suele ignorar. Una trabajadora informal del NOA no gasta igual que un profesional en Cuyo. Sus canastas son distintas, y evolucionan de forma distinta. Y hay algo más: los sectores de menores ingresos pierden en los dos escenarios. En alta inflación porque sus canastas suben más rápido. En baja inflación porque el IPC está construido sobre canastas de 2004 que no los representan — y la actualización prevista no se implementó. El resultado es que hay sectores que sistemáticamente pierden poder adquisitivo y otros que ganan, pero no sabemos quiénes son ni cuánto. Los datos existen. La pregunta es cómo usarlos."

#### Contexto → Ejemplos
> "Para hacer esto concreto, pensemos en personas reales."


### SLIDE 4 — Ejemplos y casos de uso
- Cuatro personas, cuatro canastas, un solo IPC
- Mencioná brevemente la motivación docente
- Dejá la pregunta retórica de la slide flotar un segundo antes de avanzar

"Para hacer esto concreto, pensemos en cuatro personas. Una trabajadora informal del NOA cuyo gasto dominante son los alimentos — el rubro que más subió en los últimos años. Un empleado formal en Patagonia, donde el peso de vivienda y servicios es distinto al resto del país por las tarifas regionales. Un docente universitario en CABA, que además de alimentos tiene un gasto importante en alquiler — un rubro que explotó post-2022. Y un profesional independiente en Cuyo, con mayor proporción del gasto en servicios y esparcimiento. El IPC oficial es el mismo para los cuatro. ¿Tiene sentido?"
[pausa breve]
"Esta última pregunta, dicho sea de paso, es lo que originalmente me motivó a estudiar el tema — la discusión sobre los salarios docentes en Argentina me hizo ver que el problema era más amplio."


#### Ejemplos → Definición
> "Estos cuatro casos no son excepciones — son la regla. Y eso nos lleva a la pregunta central del trabajo."



### SLIDE 5 — Definición del problema
- La pregunta central: inflación real por perfil de trabajador
- Deflactar con un único IPC distorsiona el diagnóstico
- El ML no es un adorno: es lo que permite descubrir los perfiles desde los datos

"Entonces la pregunta central del trabajo es: ¿cuál es la tasa de inflación real que enfrenta cada perfil de trabajador argentino, y qué tan vulnerable es su situación cuando se mide con ese índice en lugar del IPC oficial? El argumento es que deflactar salarios con un único IPC distorsiona quién pierde y cuánto. Cada trabajador tiene su propia canasta, su propia inflación. Y la propuesta metodológica es usar clustering — técnicas de machine learning — para descubrir esos perfiles desde los datos, en lugar de asumirlos de antemano."





#### Definición → Papers
> "Esta pregunta no la inventé yo — hay una literatura que la trabaja, y sobre esa me apoyo."



### SLIDE 6 — Selección de papers
- Jaravel: lo mismo pero en EEUU, la desigualdad real es 45% mayor que la nominal
- Lódola et al.: Argentina, alta inflación, comportamiento anti-rico
- Deaton: por qué la EPH sirve para hacer esto metodológicamente


"El trabajo se apoya en tres referencias. La principal es Jaravel, de 2024, que construye índices de precios distribuidos por perfil sociodemográfico para Estados Unidos y muestra que la desigualdad real creció un 45% más rápido de lo que indica el IPC oficial. El antecedente argentino directo es Lódola, Busso y Cerimedo, que construyeron un IPC por decil para Argentina en períodos de alta inflación y encontraron que la inflación tuvo un comportamiento anti-rico — los más pobres sufrieron más de lo que el índice oficial reconocía. Y el fundamento metodológico para trabajar con cohortes a lo largo del tiempo es Deaton, de 1985, que desarrolló la técnica de pseudo-panel sobre encuestas de corte transversal repetidas — que es exactamente lo que es la EPH."


#### Papers → Cierre
> "Eso es todo. Quedo abierto a preguntas."
