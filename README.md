# SQL Chatbot

An intelligent SQL query translation platform that leverages AI to convert natural language questions into precise database queries, providing an intuitive and interactive data exploration experience.

## Features

- Natural language to SQL translation
- Interactive data visualization
- Database schema exploration
- Query history tracking
- Automatic data loading

## Technology Stack

- **Backend**: FastAPI for API endpoints
- **Frontend**: Streamlit for interactive UI
- **Database**: SQLite for data storage
- **NLP**: LangChain integration with OpenAI
- **Visualization**: Plotly and Streamlit charts

## Installation and Setup

### Local Development

1. Clone this repository
2. Set up your environment:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r dependencies.txt
```

3. Set up environment variables:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_openai_api_key
```

4. Run the application:

```bash
python main.py
```

### Docker Deployment

1. Build and run using Docker Compose:

```bash
# Set your OpenAI API key in the environment
export OPENAI_API_KEY=your_openai_api_key

# Start the service
docker-compose up -d
```

2. Access the application:
   - Streamlit UI: http://localhost:5000
   - FastAPI endpoints: http://localhost:8000

## Usage

1. Open the Streamlit interface at http://localhost:5000
2. Click "Refresh Database Schema" to load table information
3. Enter natural language questions in the text area, such as:
   - "Show me all employees in the Engineering department"
   - "What is the average salary by department?"
   - "Which projects have the highest budgets?"
4. View query results and explore visualizations
5. Use the visualization tabs to view different chart types

## Sample Questions

Here are some sample questions you can ask:

- "Show me all tables in the database"
- "List all employees sorted by salary in descending order"
- "What is the average salary by department?"
- "Show me the projects with budgets over $100,000"
- "Count the number of employees in each department"
- "Find all employees working on more than one project"
- "Which department has the highest total budget for its projects?"
- "List employees hired after 2020"

## Project Structure

- `app.py` - Streamlit frontend application
- `fastapi_backend.py` - FastAPI backend server
- `database.py` - Database connection and queries
- `langchain_sql.py` - NLP processing and SQL generation
- `init_db.py` - Automatic database initialization
- `main.py` - Application entry point

## License

This project is licensed under the MIT License - see the LICENSE file for details.