import os
from langchain_openai import ChatOpenAI
import json

from app.database.db_operations import get_all_table_schemas

def get_llm():
    """Initialize and return the language model"""
    # Get the OpenAI API key from environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Use the gpt-4o model, which works well for SQL generation
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    model = ChatOpenAI(
        temperature=0,
        model="gpt-4o",  # Use the gpt-4o model, which is newer and has better SQL generation capability
        api_key=api_key
    )
    
    return model

def get_table_schema_string():
    """Get database schema as a formatted string for the LLM prompt"""
    try:
        all_schemas = get_all_table_schemas()
        
        if not all_schemas:
            return "No tables found in the database."
        
        schema_text = []
        for table_name, columns in all_schemas.items():
            schema_text.append(f"Table: {table_name}")
            schema_text.append("Columns:")
            for col_name, col_type in columns.items():
                schema_text.append(f"  - {col_name} ({col_type})")
            schema_text.append("")  # Empty line between tables
        
        return "\n".join(schema_text)
    except Exception as e:
        print(f"Error getting schema string: {e}")
        return "Error: Could not retrieve database schema."

def generate_sql_query(user_question):
    """Generate SQL from natural language question"""
    try:
        # Get the database schema
        db_schema = get_table_schema_string()
        
        # Initialize the language model
        llm = get_llm()
        
        # Create a prompt that includes the database schema and instructions
        prompt = f"""You are an expert SQL assistant that translates natural language questions into SQL queries.
        
Database Schema:
{db_schema}

Your task is to generate a valid SQLite SQL query based on the user's question.
- Only generate a valid SQL query, don't include any explanations or commentary
- Don't use any tables or columns not listed in the schema
- If you can't create a valid query from the input, explain why instead of attempting to generate SQL
- Ensure your queries are efficient and properly formatted
- Use appropriate joins, aggregations, or filters as needed
- The generated SQL should be directly executable without modification
- Make sure to follow SQLite syntax (not PostgreSQL)

User question: {user_question}

SQL Query:"""
        
        # Generate the SQL with a direct call to the LLM
        response = llm.invoke(prompt)
        sql_query = response.content.strip()
        
        # Return successful result
        return {
            "success": True,
            "sql": sql_query
        }
    except Exception as e:
        print(f"Error generating SQL: {e}")
        return {
            "success": False,
            "error": f"Failed to generate SQL query: {str(e)}"
        }