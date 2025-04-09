# SQL Chatbot

An intelligent SQL query translation and data exploration platform that transforms natural language questions into precise database queries and provides comprehensive data insights.

## Features

- 🤖 Natural language to SQL conversion using OpenAI API and LangChain
- 📊 Interactive data visualizations with Streamlit and Plotly
- 💾 Support for multiple database connections (PostgreSQL and SQLite)
- 🔄 CSV import functionality with relationship maintenance
- 📈 Business insights and actionable recommendations from query results
- 🔗 Follow-up question suggestions for deeper data exploration

## Tech Stack

- LangChain for natural language processing
- OpenAI API for query translation and insights generation
- FastAPI for backend services
- Streamlit for interactive frontend
- PostgreSQL for database management
- Plotly for advanced data visualization
- Pandas for data manipulation

## Docker Setup

### Prerequisites

- Docker and Docker Compose installed on your system
- OpenAI API key (and optionally Anthropic API key)

### Quick Start

1. Clone this repository
2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API keys and database settings
4. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```
5. Access the application:
   - Streamlit frontend: http://localhost:5000
   - FastAPI backend: http://localhost:8000

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key (optional)
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: PostgreSQL database name

## Usage

1. Import sample data using the CSV import functionality
2. Ask questions in natural language about your data
3. Explore the generated SQL, data results, visualizations, and business insights
4. Follow suggested follow-up questions for deeper analysis

## Development Setup

If you want to run the application without Docker:

1. Install Python 3.11 or higher
2. Install dependencies:
   ```bash
   pip install -r docker-requirements.txt
   ```
3. Set up environment variables
4. Run the application:
   ```bash
   python -m src.main
   ```

## License

MIT