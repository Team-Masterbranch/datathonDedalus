
#### Cosas raras
- Códigos que están en los datos no coinciden con la descripción de los códigos que da Copilot.
- Tablas no están sorteadas por ID. No se, creo que es ok.

#### Columnas
##### cohorte_alegias.csv
- PacienteID
- Fecha_diagnostico
- Codigo_SNOMED
- Descripcion: que alergia es: lactosa, polen etc.
##### cohorte_condiciones.csv
- PacienteID,
- Fecha_inicio,
- Fecha_fin,
- Codigo_SNOMED,
- Descripcion: el nombre de la condición, por ejemplo, Astma, Diabetes tipo 2, Neumonía etc.
Notas: es raro que hay "Diabetes tipo 2" pero no hay "Diabetes tipo 1". A lo mejor, hay que añadir datos y ampliar la variedad de diagnosis.
##### cohorte_encuentros.csv
- PacienteID,
- Tipo_encuentro,
- Fecha_inicio,
- Fecha_fin
##### cohorte_medicationes.csv
- PacienteID,
- Fecha de inicio,
- Fecha de fin,
- Código,
- Nombre,
- Dosis,
- Frecuencia,
- Vía de administración
##### cohorte_pacientes.csv
- PacienteID,
- Genero,
- Edad,
- Provincia,
- Latitud,
- Longitud
##### cohorte_procedimientos.csv
- PacienteID,
- Fecha_inicio,
- Fecha_fin,
- Codigo_SNOMED,
- Descripcion
