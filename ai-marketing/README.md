## AI Marketing

- `app` : Streamlit app run in Snowpark Container Services that interfaces with a locally hosted LLM via API and writes the results back to Snowflake tables. 
- `app/main.py`: App Homepage
- `app/extraordinary_events.json`: JSON file with system prompts for email generation.
- `app/pages/1_Generate_E-mails.py`: Streamlit page with interface for crafting prompts and reading generated emails
- `sql/setup.py`: Python script that uploads `extraordinary_events.csv` to Snowflake account and creates useful UDFs.
- `aimarketing/`: handful of utility functions.
- `pyproject.toml`: Allows `pip install -e .` for utility functions.

