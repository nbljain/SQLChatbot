import os
from langchain_openai import ChatOpenAI
from src.db.database import get_all_table_schemas, execute_sql_query

def get_llm():
    """Initialize and return the language model"""
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Use gpt-4o model for better SQL generation
    return ChatOpenAI(temperature=0, openai_api_key=openai_api_key, model="gpt-4o")
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user

def get_table_schema_string():
    """Get database schema as a formatted string for the LLM prompt"""
    schemas = get_all_table_schemas()
    
    schema_str = "Database Schema:\n"
    for table_name, columns in schemas.items():
        schema_str += f"Table: {table_name}\n"
        for col_name, col_type in columns.items():
            schema_str += f"  {col_name} ({col_type})\n"
        schema_str += "\n"
    
    return schema_str

def generate_sql_query(user_question):
    """Generate SQL from natural language question"""
    try:
        # Get database schema
        schema = get_table_schema_string()
        
        # Set up the LLM
        llm = get_llm()
        
        # Create a direct prompt for SQL generation
        prompt = f"""
        You are a SQL expert. Given the user question, create only a SQL query that will answer the user's question.
        
        {schema}
        
        Consider using aliases to make complex queries more readable. 
        Use appropriate JOIN types and optimize the query for readability.
        Use proper filtering with WHERE clauses.
        Provide appropriate sorting with ORDER BY when needed.
        
        User Question: {user_question}
        
        Return ONLY the SQL query without any additional text or explanations.
        
        SQL Query:
        """
        
        # Generate SQL directly with the model
        response = llm.invoke(prompt)
        
        # Extract the SQL query from the response and clean up any markdown formatting
        sql_query = response.content.strip()
        
        # Remove markdown code block formatting if present
        if sql_query.startswith("```sql"):
            sql_query = sql_query[7:]  # Remove ```sql
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]  # Remove ```
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]  # Remove trailing ```
            
        # Clean and normalize the SQL
        sql_query = sql_query.strip()
        
        return {"success": True, "sql": sql_query}
    except Exception as e:
        return {"success": False, "error": str(e)}