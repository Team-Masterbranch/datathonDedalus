We are a team of two students and we are participating in a Datathlon competition. This competition has a very short time limit (few days).

The challenge is to develop a conversational agent that enables healthcare professionals to quickly and efficiently identify cohorts of patients with chronic diseases (diabetes, hypertension, COPD, etc.).

We have access to a pre-trained LLM (Claude 3 Sonnet via Amazon Bedrock) to build a conversational interface for healthcare professionals.
**Tools Provided**:
    - API key for a proxy server (`litellm.dedalus.com`) to access Claude 3 Sonnet.
    - Example code using the OpenAI client library (configured to route requests to Bedrock).
    - There are strong hints to use ChatLiteLLM library.

Here is a project structure summary so far:

# Project Structure

/project-root
│
├── /data                # Raw CSV files
│   ├── pacientes.csv
│   ├── condiciones.csv
│   ├── alergias.csv
│   ├── medicationes.csv
│   ├── encuentros.csv
│   └── procedimientos.csv
│
├── /core
│   ├── llm_handler.py     # LLM interface & prompts
│   ├── data_loader.py     # Data merging/cleaning
│   ├── query_parser.py    # NL → SQL-like filters
│   ├── context_manager.py # Session state tracking
│   └── viz_generator.py   # Charts/stats generation
│
├── /utils
│   ├── config.py          # API keys, paths
│   ├── logger.py          # Logging setup
│   └── validation.py      # Query sanitization
│
├── /interface
│   ├── cli.py             # CLI with questionary
│   └── webui.py           # Streamlit (optional)
│
├── tests/                 # Pytest unit tests
├── requirements.txt       # Python dependencies
└── main.py                # Launch script

# Dataset Specifications
1. cohorte_pacientes.csv (Patients)
Column (ES) English Type    Description
PacienteID  PatientID   str Unique identifier
Genero  Gender  str Masculino/Femenino
Edad    Age int 19-84 years
Provincia   Province    str 6 Andalusian provinces
Latitud Latitude    float   Geographic coordinate
Longitud    Longitude   float   Geographic coordinate

2. cohorte_condiciones.csv (Conditions)
Column (ES) English Type    Description
PacienteID  PatientID   str Foreign key
Fecha_inicio    StartDate   date    Condition onset
Fecha_fin   EndDate date    Resolution date
Codigo_SNOMED   SNOMEDCode  str Clinical code
Descripcion Description str e.g., "Diabetes tipo 2"

3. cohorte_alergias.csv (Allergies)
Column (ES) English Type    Description
PacienteID  PatientID   str Foreign key
Fecha_diagnostico   DiagnosisDate   date    Allergy identification
Codigo_SNOMED   SNOMEDCode  str e.g., 91936005 (Pollen)
Descripcion Description str Allergy details

4. cohorte_medicationes.csv (Medications)
Column (ES) English Type    Description
PacienteID  PatientID   str Foreign key
Fecha de inicio StartDate   date    Prescription start
Fecha de fin    EndDate date    Prescription end
Código  ATC Code    str e.g., C09AA03
Nombre  Name    str Drug name
Dosis   Dose    str e.g., "10 mg"
Frecuencia  Frequency   str e.g., "Diario"
Vía de administración   Route   str Oral, IV, etc.

5. cohorte_encuentros.csv (Encounters)
Column (ES) English Type    Description
PacienteID  PatientID   str Foreign key
Tipo_encuentro  EncounterType   str Hospitalización/Urgencia/Atención Primaria
Fecha_inicio    StartDate   date    Encounter start
Fecha_fin   EndDate date    Encounter end

6. cohorte_procedimientos.csv (Procedures)
Column (ES) English Type    Description
PacienteID  PatientID   str Foreign key
Fecha_inicio    StartDate   date    Procedure start
Fecha_fin   EndDate date    Procedure end
Codigo_SNOMED   SNOMEDCode  str e.g., 303893007 (Brain MRI)
Descripcion Description str Procedure details

# Core Module Specifications
1. **llm_handler.py**
This module acts as the interface between the application and the Claude 3 Sonnet LLM. It is responsible for:
- Natural Language Understanding (NLU): 
  - Parsing user queries in Spanish/English into structured filters (e.g., "Show diabetic patients over 50" → {"condition": "Diabetes", "age": [50, None]}).
  - Handling medical terminology translation (e.g., "high blood pressure" → "Hypertension").

- Response Generation:
  - Generating natural language summaries of query results (e.g., "Found 12 patients with diabetes and hypertension").
  - Suggesting relevant visualizations based on the data (e.g., "Would you like to see an age distribution chart?").

- Prompt Engineering:
  - Maintaining a system prompt that defines the LLM's role and capabilities.
  - Formatting user queries with context (e.g., current filters, previous results) for coherent conversations.

2. data_loader.py
This module handles all data ingestion, preprocessing, and merging. Its responsibilities include:
- Data Loading:
  - Reading CSV files into Pandas DataFrames.
  - Ensuring consistent column naming and data types across tables.

- Data Cleaning:
  - Handling missing values (e.g., setting Fecha_fin to 2025-12-31 for ongoing conditions).
  - Standardizing date formats and ensuring temporal consistency.

- Data Merging:
  - Performing left joins on PacienteID to create a unified patient record.
  - Preserving all patient records even if some tables lack matching entries.
- Preprocessing:
  - Creating derived fields (e.g., age groups, duration of conditions).
  - Mapping SNOMED/ATC codes to human-readable descriptions.

3. query_parser.py
This module translates structured filters (from the LLM) into executable queries on the dataset. It provides:

- Filter Application:
  - Applying criteria like age ranges, gender, province, and condition presence to the dataset.
  - Handling temporal filters (e.g., "Conditions active during 2020-2022").

- Query Validation:
  - Ensuring filters are valid (e.g., age ranges are numeric, dates are in the correct format).
  - Providing fallback behavior for ambiguous or invalid queries.

- Performance Optimization:
  - Using vectorized Pandas operations for efficient filtering.
  - Caching frequently used queries to reduce computation time.

4. context_manager.py
This module maintains the state of the conversation and user-defined filters. Its functionality includes:

- Filter Management:
  - Storing active filters (e.g., age, gender, conditions) in a stack for undo/redo functionality.
  - Merging new filters with existing ones (e.g., adding "hypertension" to an existing "diabetes" filter).

- Session State:
  - Tracking the current cohort of patients being analyzed.
  - Storing visualization preferences (e.g., default chart type).

- Context Preservation:
  - Maintaining a history of user interactions for coherent multi-turn conversations.
  - Resetting context after a session timeout or explicit user request.

5. viz_generator.py
This module generates visualizations and statistical summaries of the data. It provides:

- Chart Generation:
  - Creating common visualizations like age/gender pyramids, medication timelines, and comorbidity networks.
  - Supporting multiple chart types (e.g., bar charts, line charts, heatmaps) via Plotly/Matplotlib.

- Statistical Summaries:
  - Calculating cohort metrics (e.g., average age, condition prevalence).
  - Generating frequency distributions for categorical variables (e.g., encounter types, provinces).

- Customization:
  - Allowing users to customize visualizations (e.g., color schemes, chart titles).
  - Exporting charts as images or interactive HTML files.

# Technical Specifications
## LLM Configuration
- Model: Claude 3 Sonnet via Amazon Bedrock
- Temperature: 0.3 (for medical accuracy)
- Max Tokens: 4096

## Data Processing
- Merge Strategy: Left joins preserving all patient records
- Date Handling: Timezone-naive (assume local time)
- Missing Data: Explicit Unknown category for empty fields

## Query Capabilities
- Temporal: "Conditions active during X period"
- Geographic: "Patients within 50km of Málaga"
- Clinical: "On medication X for >6 months"

## Visualization Types
- Demographic distributions (age/gender/province)
- Medication timelines
- Comorbidity networks
- Encounter frequency heatmaps


# Next Development Steps
- Implement DataLoader with full table merging
- Build basic CLI interface with filter display
- Create SNOMED code mapping dictionary
- Develop first visualization template (age/gender pyramid)
