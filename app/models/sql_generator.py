import os
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
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

def setup_sql_chain():
    """Set up the LangChain chain for SQL generation"""
    try:
        llm = get_llm()
        
        # Get the database schema
        db_schema = get_table_schema_string()
        
        # Create a custom prompt that includes the database schema and instructions
        prompt = ChatPromptTemplate.from_template(
            """You are a SQL expert. Given the following database schema and a question, 
            your job is to write a SQL query that answers the question.
            
            Database Schema:
            {db_schema}
            
            Instructions:
            - Always use valid SQLite syntax
            - Use only the tables and columns provided in the schema
            - Add comments to explain complex parts of the query
            - For any aggregated results, use clear aliases
            - Do not use placeholders for table names or column names
            - Your response should contain only the SQL query, nothing else
            - The database is case-insensitive
            
            User Question: {question}
            
            SQL Query:"""
        )
        
        # Create the SQL chain
        chain = create_sql_query_chain(llm, prompt)
        
        return chain, db_schema
    except Exception as e:
        print(f"Error setting up SQL chain: {e}")
        return None, str(e)

def generate_sql_query(user_question):
    """Generate SQL from natural language question"""
    try:
        chain, db_schema = setup_sql_chain()
        
        if not chain:
            return {
                "success": False,
                "error": f"Failed to initialize language model: {db_schema}"
            }
        
        # Generate the SQL query using the chain
        sql_query = chain.invoke({
            "question": user_question,
            "db_schema": db_schema
        })
        
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