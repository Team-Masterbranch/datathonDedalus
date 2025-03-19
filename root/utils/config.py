import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'newData' / '100'
# DATA_DIR = PROJECT_ROOT / 'data'
LOGS_DIR = PROJECT_ROOT / 'logs'
TESTS_DIR = PROJECT_ROOT / 'tests'

PATIENT_ID_COLUMN = 'PacienteID'
PATIENT_ID_ALTERNATIVES = ['Patient ID', 'pacientes.ID', 'paciente_id', 'ID']  # Fallback column names

# Session directory
SESSION_BASE_DIR = DATA_DIR / 'session'

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

LLM_DEFAULT_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 150
LLM_TOP_P = 1.0
LLM_FREQUENCY_PENALTY = 0.0
LLM_PRESENCE_PENALTY = 0.0

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "INFO"
LOG_FILE_PATTERN = "app_{date}.log"

# CLI Configuration
CLI_PROMPT = "(Master Branch Bot) "
CLI_INTRO = "Welcome to the Healthcare Data Analysis System. Type 'help' for commands."

# Query Processing
MAX_CACHE_SIZE = 1000  # Maximum number of cached queries

# Schema configuration
UNIQUE_VALUES_THRESHOLD = 30  # Show all possible values if number of unique values is below this

# Visualization settings
CLI_CHART_WIDTH = 10
CLI_CHART_HEIGHT = 6
IMG_DPI = 300
IMG_FORMAT = 'png'


# LLM Logging Configuration
LLM_LOG_DIR = LOGS_DIR / 'llm'
LLM_LOG_FILE = LLM_LOG_DIR / 'llm_interactions.log'
LLM_LOG_SEPARATOR = "\n" + "="*80 + "\n"  # Separator between log entries

# Patient ID Configuration

