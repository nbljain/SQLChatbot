# SQL Chatbot

An intelligent SQL query translation and data exploration platform that transforms natural language questions into precise database queries and provides comprehensive data insights.

## Features

- **Natural Language to SQL**: Ask questions in plain English and get SQL queries
- **Interactive UI**: User-friendly Streamlit frontend with chat history
- **Data Visualization**: Automatic chart suggestions based on query results
- **Database Explorer**: Browse tables and schema information
- **Modular Architecture**: Organized codebase with separate backend and frontend

## Tech Stack

- **NLP**: LangChain for language processing with OpenAI integration
- **Backend**: FastAPI for robust API endpoints
- **Frontend**: Streamlit for interactive UI components
- **Database**: SQLite for data storage (easily configurable)
- **Visualization**: Plotly and Streamlit native charts
- **Structure**: Modular Python package organization

## Project Structure

```
├── src/                          # Source code
│   ├── backend/                  # API and NLP components
│   │   ├── api.py               # FastAPI endpoints
│   │   └── nlp.py               # LangChain integration
│   ├── database/                 # Database operations
│   │   └── db.py                # Database connection and queries
│   ├── frontend/                 # User interface
│   │   └── app.py               # Streamlit application
│   └── utils/                    # Utilities
│       └── db_init.py            # Database initialization
├── .streamlit/                   # Streamlit configuration
│   └── config.toml              # Server settings
├── main.py                       # Application entry point
└── sql_chatbot.db                # SQLite database
```

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. Clone the repository
2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key:
   ```
   export OPENAI_API_KEY="your-api-key"
   ```

### Running the Application

```
python main.py
```

This will:
1. Initialize the database with sample data (if needed)
2. Start the FastAPI backend on port 8000
3. Launch the Streamlit frontend on port 5000

## Usage

1. Access the application at http://localhost:5000
2. Ask natural language questions about the database
3. View the generated SQL query, results, and visualizations
4. Explore different visualization options
5. Browse the database schema in the sidebar

## Example Questions

- "Show me the average salary by department"
- "List all employees in the Engineering department"
- "What projects have budgets over $100,000?"
- "Find employees who are working on more than one project"
- "Show the total hours allocated to each project"

## Database Schema

The sample database includes:

- **employees**: Employee information (name, department, salary, etc.)
- **projects**: Project details (name, budget, timeline, etc.)
- **employee_projects**: Assignment of employees to projects

## License

This project is open source and available under the MIT License.