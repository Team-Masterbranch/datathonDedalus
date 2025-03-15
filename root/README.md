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
│   └── cohort.csv     # Latest cohort data
└── main.py            # Application entry point

Core Components
-------------
1. Application Service (application.py)
   - Main orchestrator of the system
   - Manages component lifecycle and interactions
   - Handles query processing pipeline

2. Data Management (data_manager.py)
   - Manages data loading and access
   - Handles cohort filtering and schema management
   - Provides data validation and access methods

3. Query Processing Pipeline:
   - Preparser (preparser.py): Initial query processing and caching
   - Parser (parser.py): Query structure analysis and LLM integration
   - Query Manager (query_manager.py): Query execution and cohort management

4. Visualization System:
   - Visualizer (visualizer.py): Chart generation and output management
   - Result Analyzer (result_analyzer.py): Analysis and visualization suggestions

5. LLM Integration (llm_handler.py):
   - Manages LLM service interactions
   - Handles prompt formatting and response processing

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
            start(): Start the application
            process_user_query(query: str, filter_current_cohort: bool): Process user queries
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
            validate_visualization_request(): Validate visualization requests

core.preparser
------------
First stage of query processing pipeline.

Classes:
    Preparser:
        Handles initial query processing and caching.

        Methods:
            process_query(): Process raw queries
            update_cache(): Update query cache
            _try_regex_match(): Attempt regex-based parsing

core.parser
---------
Query parsing and structure analysis component.

Classes:
    Parser:
        Converts preprocessed queries into structured format.

        Methods:
            process_with_llm(): Process query through LLM
            validate_criteria(): Validate query criteria structure

core.query_manager
---------------
Query execution and cohort management component.

Classes:
    QueryManager:
        Manages query execution and cohort filtering.

        Methods:
            execute_query(): Execute structured queries
            update_cohort(): Update current cohort based on query

core.visualizer
------------
Visualization generation component.

Classes:
    Visualizer:
        Creates visual representations of cohort data.

        Methods:
            create_visualizations(): Generate visualizations
            _create_visualization(): Create single visualization
            _save_plot(): Save generated plots

core.result_analyzer
-----------------
Results analysis and visualization suggestion component.

Classes:
    ResultAnalyzer:
        Analyzes query results and suggests visualizations.

        Methods:
            analyze_cohort(): Analyze cohort and suggest visualizations
            _generate_visualization_requests(): Generate visualization suggestions

core.llm_handler
-------------
LLM service integration component.

Classes:
    LLMHandler:
        Manages interactions with LLM service.

        Methods:
            process_query(): Process queries through LLM
            format_prompt(): Format prompts for LLM

Configuration
-----------
utils.config:
    System configuration parameters including:
    - Data paths
    - Logging settings
    - Visualization parameters
    - LLM configuration

Dependencies
-----------
  - Python 3.8+
  - pandas
  - matplotlib
  - seaborn
  - pytest (for testing)