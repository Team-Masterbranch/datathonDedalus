We are a team of two students and we are participating in a Datathlon competition. This competition has a very short time limit (few days).

The challenge is to develop a conversational agent that enables healthcare professionals to quickly and efficiently identify cohorts of patients with chronic diseases (diabetes, hypertension, COPD, etc.).

We have access to a pre-trained LLM (Claude 3 Sonnet via Amazon Bedrock) to build a conversational interface for healthcare professionals.
- **Tools Provided**:
    - API key for a proxy server (`litellm.dedalus.com`) to access Claude 3 Sonnet.
    - Example code using the OpenAI client library (configured to route requests to Bedrock).
    - There are strong hints to use ChatLiteLLM library.

We have an artificially created data set. Here is it's summary:
## **Database Overview**

**Purpose**: Track chronic/acute conditions, medications, encounters, procedures, and demographics for **33 patients** across Andalusia, Spain.  
**Temporal Scope**: Data spans **2010–2025**, with a focus on chronic disease management.  
**Key Gaps**: Missing provinces (Cádiz, Jaén), underrepresentation of specialist care, and limited chronic conditions (e.g., COPD, CKD).

---

### **1. `cohorte_pacientes.csv` (Patients)**

**Entries**: 33 patients  
**Columns**:

- `PacienteID`: Unique patient identifier.
    
- `Genero`: Gender (Masculino/Femenino).
    
- `Edad`: Age (19–84 years).
    
- `Provincia`: Province (6/8 Andalusian provinces).
    
- `Latitud`/`Longitud`: Geographic coordinates.
    

**Summary**: Demographics for 33 patients, mostly from Málaga (24%) and Córdoba (21%). Missing pediatric/geriatric diversity.

---

### **2. `cohorte_condiciones.csv` (Conditions)**

**Entries**: ~50  
**Columns**:

- `PacienteID`, `Fecha_inicio`, `Fecha_fin`: Condition timeline.
    
- `Codigo_SNOMED`: SNOMED-like codes (e.g., `C0020538` = Diabetes).
    
- `Descripcion`: Condition description (e.g., Diabetes tipo 2).
    

**Summary**: Focuses on **chronic conditions** (diabetes, hypertension) and acute issues (pneumonia, fractures). Missing CKD, COPD.

---

### **3. `cohorte_alegias.csv` (Allergies)**

**Entries**: ~75  
**Columns**:

- `PacienteID`, `Fecha_diagnostico`: Allergy diagnosis date.
    
- `Codigo_SNOMED`: Valid SNOMED codes (e.g., `91936005` = Pollen allergy).
    
- `Descripcion`: Allergy description.
    

**Summary**: Dominated by pollen, nut, and penicillin allergies. Missing severity data and regional allergens (e.g., olive pollen).

---

### **4. `cohorte_medicationes.csv` (Medications)**

**Entries**: ~80  
**Columns**:

- `PacienteID`, `Fecha de inicio`, `Fecha de fin`: Prescription dates.
    
- `Código`: ATC codes (e.g., `C09AA03` = Lisinopril).
    
- `Nombre`, `Dosis`, `Frecuencia`, `Vía de administración`: Drug details.
    

**Summary**: Covers antihypertensives, antidiabetics, and statins. Lacks newer therapies (e.g., SGLT2 inhibitors).

---

### **5. `cohorte_encuentros.csv` (Encounters)**

**Entries**: ~90  
**Columns**:

- `PacienteID`, `Tipo_encuentro`: Encounter type (Hospitalización/Urgencia/Atención Primaria).
    
- `Fecha_inicio`, `Fecha_fin`: Encounter dates.
    

**Summary**: Mostly hospitalizations and emergencies. Missing specialist visits (e.g., endocrinology) and preventive care.

---

### **6. `cohorte_procedimientos.csv` (Procedures)**

**Entries**: ~100  
**Columns**:

- `PacienteID`, `Fecha_inicio`, `Fecha_fin`: Procedure timeline.
    
- `Codigo_SNOMED`: Valid SNOMED codes (e.g., `303893007` = Brain MRI).
    
- `Descripcion`: Procedure description.
    

**Summary**: Focuses on acute procedures (e.g., sutures, X-rays). Lacks chronic care procedures (e.g., HbA1c tests, spirometry).

## **Goals**
- The agent should be capable of remembering the context to add or remove search criteria;
- it should be able to provide statistics of the selected cohort;
- it should be able to provide non-textual output (graphics, diagrams, etc).