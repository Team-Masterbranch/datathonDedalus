
# **Project Style Guide**

## **1. General Principles**
- **Readability**: Code should be easy to read and understand. Use meaningful variable names and avoid overly complex expressions.
- **Consistency**: Follow consistent naming conventions, formatting, and patterns throughout the codebase.
- **Modularity**: Break down functionality into small, reusable modules or functions.
- **Documentation**: Document all functions, classes, and modules using docstrings. Include inline comments where necessary to explain complex logic.
- **Error Handling**: Use appropriate error handling to ensure the application is robust and provides meaningful feedback to users.

---

## **2. Code Formatting**
- **Indentation**: Use 4 spaces per indentation level (no tabs).
- **Line Length**: Limit lines to 79 characters for code and 72 for docstrings/comments.
- **Blank Lines**:
  - Use two blank lines to separate top-level functions and classes.
  - Use one blank line to separate methods within a class or logical sections within a function.
- **Imports**:
  - Group imports in the following order, separated by a blank line:
    1. Standard library imports.
    2. Third-party library imports.
    3. Local application/library imports.
  - Use absolute imports instead of relative imports.
  - Example:
    ```python
    import os
    import sys

    import pandas as pd
    import numpy as np

    from core.llm_handler import LLMHandler
    ```

---

## **3. Naming Conventions**
- **Variables and Functions**: Use `snake_case` (e.g., `patient_id`, `calculate_age`).
- **Constants**: Use `UPPER_SNAKE_CASE` (e.g., `MAX_AGE`, `DEFAULT_PROVINCE`).
- **Classes**: Use `PascalCase` (e.g., `DataLoader`, `QueryParser`).
- **Files and Directories**: Use `snake_case` for file and directory names (e.g., `llm_handler.py`, `data_loader.py`).

---

## **4. Documentation**
- **Docstrings**: Use Google-style docstrings for all public functions, classes, and modules.
  - Example:
    ```python
    def calculate_age(birth_date, current_date):
        """
        Calculate the age of a patient based on their birth date.

        Args:
            birth_date (datetime.date): The patient's birth date.
            current_date (datetime.date): The current date.

        Returns:
            int: The calculated age.
        """
        return (current_date - birth_date).days // 365
    ```
- **Inline Comments**: Use comments sparingly to explain *why* something is done, not *what* is being done (the code should be self-explanatory).

---

## **5. Error Handling**
- Use `try-except` blocks to handle expected exceptions.
- Log errors using the `logger` module for debugging and traceability.
- Provide user-friendly error messages for unexpected issues.
- Example:
  ```python
  try:
      data = pd.read_csv(file_path)
  except FileNotFoundError:
      logger.error(f"File not found: {file_path}")
      raise ValueError("The specified file does not exist.")
  ```

---

## **6. Testing**
- Write unit tests for all core functionality using `pytest`.
- Place tests in the `/tests` directory, mirroring the structure of the main codebase.
- Use descriptive test function names (e.g., `test_calculate_age_valid_input`).
- Example:
  ```python
  def test_calculate_age_valid_input():
      from core.data_loader import calculate_age
      from datetime import date

      birth_date = date(1990, 1, 1)
      current_date = date(2023, 1, 1)
      assert calculate_age(birth_date, current_date) == 33
  ```

---

## **7. Logging**
- Use the `logger` module for all logging.
- Log levels:
  - `DEBUG`: Detailed information for debugging.
  - `INFO`: General runtime events (e.g., starting a process).
  - `WARNING`: Indicate potential issues.
  - `ERROR`: Log errors that affect functionality.
  - `CRITICAL`: Severe errors that may prevent the application from running.
- Example:
  ```python
  import logging

  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)

  logger.info("Data loading started.")
  ```

---

## **8. Data Handling**
- **DataFrames**: Use `pandas` for all data manipulation. Avoid modifying DataFrames in place unless necessary.
- **Column Naming**: Use consistent column names across all datasets (e.g., `PacienteID` should always be referred to as `patient_id` in code).
- **Missing Data**: Handle missing data explicitly (e.g., use `pd.NA` or a placeholder like `Unknown`).

---

## **9. LLM Interaction**
- **Prompt Engineering**:
  - Use clear and concise prompts.
  - Include examples in the system prompt to guide the LLM’s behavior.
  - Example:
    ```python
    system_prompt = """
    You are a medical assistant helping healthcare professionals identify patient cohorts.
    Your task is to parse user queries into structured filters and generate summaries.
    Example:
    - User: "Show diabetic patients over 50."
    - Output: {"condition": "Diabetes", "age": [50, None]}
    """
    ```
- **Temperature**: Set the temperature to `0.3` for deterministic and accurate responses.
- **Max Tokens**: Limit responses to 4096 tokens to avoid excessive output.

---

## **10. Visualization**
- Use `Plotly` for interactive visualizations and `Matplotlib` for static charts.
- Ensure all visualizations are labeled clearly (e.g., axis labels, titles).
- Example:
  ```python
  import plotly.express as px

  def plot_age_distribution(data):
      fig = px.histogram(data, x="age", title="Age Distribution of Patients")
      fig.update_layout(xaxis_title="Age", yaxis_title="Count")
      return fig
  ```

---

## **11. Git Workflow**
- **Branching**: Use feature branches for new functionality (e.g., `feature/llm-integration`).
- **Commits**: Write clear, concise commit messages in the present tense (e.g., "Add data loading functionality").

---

## **12. Tools and Libraries**
- **Required Libraries**: List all dependencies in `requirements.txt` with pinned versions.
  - Example:
    ```
    pandas==2.0.3
    plotly==5.15.0
    streamlit==1.26.0
    ```
- **Linting**: Use `flake8` or `black` for code formatting and linting.
- **Environment**: Use a virtual environment (e.g., `venv` or `conda`) to manage dependencies.