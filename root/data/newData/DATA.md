# Medical Data Generation Documentation

This documentation describes the data files used and generated in the medical data processing system.

## Generated Output File

### procedimientos.csv
Contains the medical procedures assigned to patients based on their conditions and hospital encounters.

| Column Name | Description | Possible Values |
|------------|-------------|-----------------|
| Patient ID | Unique identifier for the patient | Any valid patient ID from input files |
| Nombre del procedimiento | Name of the medical procedure | - Terapia con broncodilatadores<br>- Rehabilitación pulmonar<br>- Oxigenoterapia<br>- Pruebas de función pulmonar<br>- Angiografía coronaria<br>- Intervención coronaria percutánea (ICP)<br>- Cirugía de bypass coronario<br>- Ecocardiograma<br>- Quimioterapia<br>- Radioterapia<br>- Resección quirúrgica<br>- Biopsia<br>- Psicoterapia<br>- Manejo de medicación<br>- Terapia electroconvulsiva (TEC)<br>- Terapia cognitivo-conductual (TCC)<br>- Terapia de estimulación cognitiva<br>- Terapia ocupacional<br>- Clínicas de memoria<br>- Yeso o férula<br>- Fijación quirúrgica<br>- Fisioterapia<br>- Reducción (manual o quirúrgica)<br>- Inmovilización<br>- Protocolo RICE<br>- Reposo y crioterapia<br>- Manejo del dolor<br>- Reparación quirúrgica<br>- Ortesis o férula<br>- Antibioticoterapia<br>- Hidratación parenteral<br>- Terapia antiemética<br>- Terapia trombolítica<br>- Trombectomía mecánica<br>- Rehabilitación<br>- Apendicectomía<br>- Antitusígenos<br>- Soporte nutricional<br>- Miringotomía<br>- Descongestionantes nasales<br>- Irrigación nasal<br>- Pastillas para la garganta<br>- Terapia antiviral<br>- Corticosteroides<br>- Cuidado de heridas<br>- Cuidados de soporte |
| Fecha | Date of the procedure | YYYY-MM-DD format |

## Input Files Used

### condiciones_pacientes.csv
Contains patient conditions and their start dates.

| Column Name | Description | Possible Values |
|------------|-------------|-----------------|
| Patient ID | Unique identifier for the patient | Any valid patient ID |
| Nombre de la condición | Name of the medical condition | - Enfermedad respiratoria crónica<br>- Enfermedad cardiovascular<br>- Neoplasmas<br>- Trastornos mentales<br>- Enfermedad de Alzheimer<br>- Fracturas<br>- Luxaciones<br>- Esguinces<br>- Contusiones<br>- Roturas de ligamentos y tendones<br>- Infección respiratoria aguda<br>- Gastroenteritis aguda<br>- Infarto agudo de miocardio<br>- Accidente cerebrovascular agudo<br>- Apendicitis aguda<br>- Bronquitis aguda<br>- Pancreatitis aguda<br>- Otitis media aguda<br>- Sinusitis aguda<br>- Faringitis aguda<br>- Meningitis aguda<br>- Neumonía aguda<br>- Cistitis aguda<br>- Celulitis aguda<br>- Hepatitis aguda |
| Fecha inicio | Start date of the condition | YYYY-MM-DD format |

### encuentros_hospitalarios.csv
Contains records of hospital encounters.

| Column Name | Description | Possible Values |
|------------|-------------|-----------------|
| Patient ID | Unique identifier for the patient | Any valid patient ID |
| Fecha inicio | Start date of the hospital encounter | YYYY-MM-DD format |
| Tipo de Encuentro | Diferentes tipos de encuentros | Hospitalización, Atención Primaria, Urgencias, Consultas Especializadas, Cirugía Ambulatoria

## Notes
- The procedures are assigned based on the patient's most recent condition at the time of the hospital encounter
- Procedure selection is weighted according to predefined probabilities for each condition
- All dates are in YYYY-MM-DD format
