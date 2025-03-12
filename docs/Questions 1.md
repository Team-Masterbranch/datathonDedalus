#### Data set extensión
##### Edad, Genero
- podemos suponer que la distribución de edad está buena y extendimos con la misma distribución?
##### Geografía
- Solo hay pacientes de Málaga, Córdoba, Almería, Huelva, Granada, Sevilla.
- No hay pacientes de Cádiz y Jaén.
- Ergo: incluimos Cádiz y Jaén en extensión? Otros provincias? Otros países?
##### Alergias
- En el set faltan muchos alergias bastante común: por ejemplo, soja o (que es importante para Andalucía) polen de olivas. ¿Mejor añadir los en la extensión o extender con los datos que tenemos?
- Podemos/tenemos que añadir columnas como gravedad, tipo de reacción, etc.
##### Medicationes
##### Conditions
- Mix of timestamps (`2023-11-21 10:18:27.267949`) and date-only entries (`2023-03-16`).
- no hay diferencia entre condiciones **crónicos** (Diabetes, Hypertension, Asthma, COPD) y **agudos** (Migraines, Pneumonia, Fractures). Es buena idea añadirlos?
- condiciones agudos (como Influenza) son irrelevantes para identificar cohortes crónicos. ¿Que hacer con eso?
- los códigos erróneos: por ejemplo, C0032285 es el código UMLS, no es SNOMED. ¿Tenemos que corregir esos errores?
- la misma pregunta que con alegrías: hay muchos condiciones bastante común (Arthritis, Enfermedad renal crónica ... ) que no están en el set.
##### Encuentros
- Hay pacientes sin encuentros (31-33);
- Fechas superpuestas;
- Falta información sobre encuentro. Por ejemplo, "Hospitalización" que es? Por que razón?
##### Procedimientos
- Muchos procedimientos (por ejemplo, suturas de heridas, extracciones dentales) son agudos e irrelevantes para las cohortes crónicas.
- No hay procedimientos antes de 2023
- Como siempre, podemos añadir más procedimientos (HbA1c testing, Spirometry).
- 