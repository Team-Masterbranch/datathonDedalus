Healthcare Data Analysis System
=============================

A modular system for analyzing healthcare data through natural language queries,
data visualization, and cohort analysis.

Project Structure
---------------
root/
├── core/               # Core system modules
├── interface/          # User interface modules
├── tests/             # Test modules
├── utils/             # Utility modules and configurations
├── data/              # Data storage
│   ├── img/           # Generated visualizations
│   ├── temp/          # Temporary files
│   ├── cache.json     # Query cache
│   └── cohort.csv     # Latest cohort data
└── main.py            # Application entry point

Core Components
-------------
1. Application Service (application.py)
   - Main orchestrator of the system
   - Manages component lifecycle and interactions
   - Handles GUI initialization and event processing
   - Manages cache persistence

2. Data Management (data_manager.py)
   - Manages data loading and access
   - Handles cohort filtering and schema management
   - Provides data validation and access methods
   - Formats schema for display

3. Query Processing Pipeline:
   - Preparser (preparser.py): Initial query processing and LRU caching
   - Parser (parser.py): Query structure analysis and LLM integration
   - Query Manager (query_manager.py): Query execution and cohort management

4. Context Management:
   - Context Manager (context_manager.py): Manages conversation history
   - Handles message storage and retrieval
   - Maintains conversation context for LLM

5. User Interface:
   - GUI (gui.py): Graphical user interface implementation
   - Provides visual representation of data and interactions
   - Handles user input and displays results

6. LLM Integration (llm_handler.py):
   - Manages LLM service interactions
   - Handles prompt formatting and response processing
   - Supports multi-message context processing

Module Documentation
------------------

core.application
---------------
The main application service layer that coordinates all system components.

Classes:
    Application:
        Main application class that orchestrates system components.

        Methods:
            __init__(): Initialize application components
            start(): Start the application and initialize cache
            process_user_query(query: str): Process user queries
            shutdown(): Clean shutdown of application
            run_tests(): Execute system tests

core.data_manager
---------------
Centralized data management component for clinical datasets.

Classes:
    DataManager:
        Handles data loading, cleaning, filtering and schema management.

        Methods:
            __init__(data_path: str): Initialize with data directory
            load_csv_files(): Load and combine CSV data
            apply_filter(query: Query): Apply filter to current cohort
            get_current_schema(): Get schema for current cohort
            format_schema_to_string(): Format schema for display

core.preparser
------------
First stage of query processing pipeline with LRU caching.

Classes:
    Preparser:
        Handles initial query processing and caching.

        Methods:
            process_query(): Process raw queries
            update_cache(): Update LRU cache
            save_cache_to_file(): Persist cache to disk
            load_cache_from_file(): Load cache from disk

core.parser
---------
Query parsing and structure analysis component.

Classes:
    Parser:
        Converts preprocessed queries into structured format.

        Methods:
            process_message(): Process single query through LLM
            process_messages(): Process multiple messages with context
            validate_criteria(): Validate query criteria structure

core.context_manager
-----------------
Conversation context management component.

Classes:
    ContextManager:
        Manages conversation history and context.

        Methods:
            add_user_message(): Add message to context
            get_user_messages(): Get all user messages
            clear_context(): Clear conversation history

interface.gui
-----------
Graphical user interface component.

Classes:
    GUI:
        Manages visual interface and user interactions.

        Methods:
            run(): Start GUI event loop
            display_message(): Show message in chat
            update_cohort_info(): Update cohort statistics
            add_history_entry(): Add to query history

Configuration
-----------
utils.config:
    System configuration parameters including:
    - Data paths
    - Logging settings
    - Cache configuration
    - LLM settings
    - GUI parameters

Dependencies
-----------
  - Python 3.8+
  - pandas
  - matplotlib
  - seaborn
  - tkinter
  - pytest (for testing)
  - asyncio
