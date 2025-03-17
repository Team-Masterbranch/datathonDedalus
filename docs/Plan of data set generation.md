# Data set extensión
## Resumen
Debido a gran cantidad de insonsistencias en los datos, hay que generar nuevo data set. He hablado con el mentor, y él me ha dicho que si, los datos que nos han dado son más ejemplo que los datos que tenemos que usar en el proyecto.

## Edad, Genero
- Hay que intentar mantener correlaciones. Por ejemplo: si hay más diabéticos entre pacientes mayores, eso debe ser cierto para data set generado. Si hay más mujeres que hombres con cierta condición, hay que respetar esa proporción. Ciertos condiciones solo deben aparecer entre hombres/mujeres.

## Geografía
- Países de EU, distribución proporcionada según población del país.

## Alergias
- El set original contiene poca variación, hay que añadir tipos de alergía (soja y otros, preguntar a algún LLM).

## Condiciones
- El set original contiene poca variación, hay que añadir tipos de condiciones (Arthritis, Enfermedad renal crónica y otros, preguntar a algún LLM).
- Diferenciar condiciones **crónicos** (Diabetes, Hypertension, Asthma, COPD) y **agudos** (Migraines, Pneumonia, Fractures).
- Investigar si añadir códigos es una buena idea o no.

## Medicaciones
- El set original contiene poca variación, hay que añadir tipos de medicationes.
- Debe ser hay que crear una correlación con Encuentros: para tener Medicación prescribido el paciente debe primero tener un Encuentro con doctor en la que se prescribe Medicación.

## Encuentros
- Evitar fechas superpuestas;
- Añadir información sobre encuentro. Por ejemplo, si hay "Hospitalización" debe ser una columna donde explica por que razón (¿crísis diabético o covid? es importante para construcción de cohorte). Hay que crear una correlación entre Condiciones y Encuentros (astmáticos deben tener hospitalizaciónes con el crísis de astma, etc).

## Procedimientos
- Probablemente hay que integrar con Encuentros. Si el paciente tenía algún Procedimiento médico, entonces, ha llegado al hospital, pues en un Encuentro.

# Idea como atacar el problema:

- Paso 1: crear una base grande (1.000.000 entradas) de personas: solo edad, genero, geografía, distribución según estadísticas de paises de EU.
- Paso 2: añadir aletoriamente alergías. Para ello:
  - 2.1 pedir a LLM la lista de alergías que deben aparecer en la BD para identificación de cohortes,
  - 2.2 según la estadística de cada alegría añadir cada alergía a la base. Eso es, si en EU hay 10% de población con alergía a polen, tomamos 100.000 entradas aleatoriamente y añadimos alergía a polen).
- Paso 3: lo mismo que con alergías, pero para condiciones crónicos. Aquí podemos añadir correlación con edad. Ejemplo: si en el mundo real entre gente de 0-25 años 5% tienen astma, y entre gente de 26+ años 10% tienen astma, hacemos script que va a travez de base generada en paso 1, comprueba edad, si es menor que 26 años añade Astma con 5% probabilidad, si es 26+ añade Astma con 10% probabilidad.
- Paso 4: añadir condiciones agudos. Como son agudos, deben ir con fecha. Además, los pacientes mayores van a tener más probabilidad de sufrir alguna condicion aguda a lo largo de su vida. La lista de condiciones: pedimos de LLM. Luego hay que hacer una simulación: cada año cada persona tiene X% (preguntar a LLM por cifras) probabilidad de tener Fractura. Pues hay que hacer script para eso que va a través de la base generada y simula, año por año, la vida de cada paciente. Si el script decide que este año este paciente tenia una rotura, añadimos la fecha: el año ya sabemos, el mes y la día aleatoriamente.
- Paso 5. Toda gente completamente sana (que no ha recibido ningún condición crónica o aguda ni alergía) suprimimos de la base.
- Paso 6. Simulación de encuentros. Para cada condición, aguda o crónica debe estár por lo menos un encuentro en BD. Para condiciónes agudos, la fecha de encuentro debe coincidir con la fecha de condición. Para los crónicos la fecha de primer encuentro generamos aleatoriamente en algún momento de la vida de paciente. Los condiciones crónicos pueden provocar más que un encuentro, para eso tenemos que hacer un script que va a ir año por año desde la fecha de primer encuentro hasta 2025 y añadir otros encuentros.
- Paso 7. Simulación de procedimientos. Procedimiento debe ser generado para cada encuentro. La mejor estratégia es usar LLM y preguntar cosas tipo: "El paciente de 45 años ha sido hospitalizado por el crísis astmático. ¿Qué procedimientos serán aplicables en ese caso?".
- Lo mismo para Medicamentos.

## Resumen:
- Pasos 1-5 podemos hacer sin usar LLM.
- Para los pasos 6 y 7 será muy difícil generar los datos sin uso de LLM. Hay que diseñar los scripts que van a generar a partir de los datos de cada paciente (edad, genero y condiciones agudos y crónicos) los encuentros y procedimientos plausables.