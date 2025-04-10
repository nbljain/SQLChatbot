# SQL Chatbot

An intelligent SQL query translation and data exploration platform that transforms natural language questions into precise database queries and provides comprehensive data insights.

## Features

- Natural language to SQL translation using LangChain and OpenAI
- Support for SQLite and other database connections
- Interactive data visualization with Plotly
- Multi-database connection management
- User-friendly Streamlit interface

## Project Structure

```
app/
  ├── api/           # FastAPI endpoints
  ├── data/          # Data initialization scripts
  ├── database/      # Database connection and operations
  ├── models/        # LLM integration and SQL generation
  ├── ui/            # UI components
  └── utils/         # Utility functions
```

## Setup

1. Ensure you have Python 3.8+ installed
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```
4. Initialize the sample databases:
   ```
   python setup_database.py
   ```

## Usage

1. Run the application:
   ```
   python -m fastapi_backend & streamlit run app.py
   ```
2. Open your browser and navigate to `http://localhost:5000`
3. Enter natural language questions about your data
4. View the generated SQL, results, and visualizations

## Example Queries

- "Show me all employees in the Engineering department"
- "What's the total budget for all projects?"
- "List the products with the highest stock quantity"
- "Show me total sales by product category"

## Adding New Database Connections

You can add connections to different databases through the UI or by editing the `app/data/db_config.json` file directly.

## Requirements

- langchain
- openai
- fastapi
- streamlit
- sqlalchemy
- pandas
- plotly
- uvicorn
- python-dotenv