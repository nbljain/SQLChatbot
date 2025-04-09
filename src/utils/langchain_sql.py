import os
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from src.db.database import get_all_table_schemas

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

def setup_sql_chain():
    """Set up the LangChain chain for SQL generation"""
    llm = get_llm()
    
    # Add custom instructions to improve SQL generation
    custom_prompt = """
    You are a SQL expert. Given the user question, create only a SQL query that will answer the user's question.
    
    {schema}
    
    Consider using aliases to make complex queries more readable. 
    Use appropriate JOIN types and optimize the query for readability.
    Use proper filtering with WHERE clauses.
    Provide appropriate sorting with ORDER BY when needed.
    
    User Question: {question}
    
    SQL Query:
    """
    
    prompt = ChatPromptTemplate.from_template(custom_prompt)
    
    chain = create_sql_query_chain(llm, prompt)
    return chain

def generate_sql_query(user_question):
    """Generate SQL from natural language question"""
    try:
        # Get database schema
        schema = get_table_schema_string()
        
        # Set up chain
        chain = setup_sql_chain()
        
        # Generate SQL
        sql_query = chain.invoke({"schema": schema, "question": user_question})
        
        return {"success": True, "sql": sql_query}
    except Exception as e:
        return {"success": False, "error": str(e)}