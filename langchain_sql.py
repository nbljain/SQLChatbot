import os
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from database import get_all_table_schemas

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL_NAME = "gpt-4o"

# Initialize the LLM
def get_llm():
    """Initialize and return the language model"""
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
        
    return ChatOpenAI(
        temperature=0,
        model=MODEL_NAME,
        api_key=api_key
    )

def get_table_schema_string():
    """Get database schema as a formatted string for the LLM prompt"""
    schema_dict = get_all_table_schemas()
    
    if not schema_dict:
        return "No tables found in the database."
    
    schema_str = "Database Schema:\n"
    
    for table_name, columns in schema_dict.items():
        schema_str += f"Table: {table_name}\n"
        schema_str += "Columns:\n"
        
        for col_name, col_type in columns.items():
            schema_str += f"  - {col_name} ({col_type})\n"
        
        schema_str += "\n"
    
    return schema_str

def setup_sql_chain():
    """Set up the LangChain chain for SQL generation"""
    llm = get_llm()
    
    # Get database schema
    schema_str = get_table_schema_string()
    
    # Define the system prompt with the database schema
    system_template = """You are an expert SQL assistant that translates natural language questions into SQL queries.
    
{schema}

Your task is to generate a valid PostgreSQL SQL query based on the user's question.
- Only generate a valid SQL query, don't include any explanations or commentary
- Don't use any tables or columns not listed in the schema
- If you can't create a valid query from the input, explain why instead of attempting to generate SQL
- Ensure your queries are efficient and properly formatted
- Use appropriate joins, aggregations, or filters as needed
- The generated SQL should be directly executable without modification
"""
    
    # Create the chat prompt template
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{question}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        human_message_prompt
    ])
    
    # Create the chain
    chain = LLMChain(
        llm=llm,
        prompt=chat_prompt,
        verbose=True
    )
    
    return chain

def generate_sql_query(user_question):
    """Generate SQL from natural language question"""
    try:
        chain = setup_sql_chain()
        schema = get_table_schema_string()
        
        if "No tables found" in schema:
            return {
                "success": False,
                "error": "No database tables found. Please ensure your database is properly configured and contains data."
            }
        
        # Generate SQL query
        result = chain.invoke({"schema": schema, "question": user_question})
        generated_sql = result["text"].strip()
        
        # Clean up the SQL - remove markdown formatting if present
        if generated_sql.startswith("```"):
            # Remove markdown code block syntax
            lines = generated_sql.split("\n")
            # Remove the first line if it contains ```
            if "```" in lines[0]:
                lines = lines[1:]
            # Remove the last line if it contains ```
            if lines and "```" in lines[-1]:
                lines = lines[:-1]
            generated_sql = "\n".join(lines).strip()
        
        # Further cleanup: remove "sql" if it appears alone on the first line
        lines = generated_sql.split("\n")
        if lines and lines[0].strip().lower() in ["sql", "postgresql", "psql"]:
            lines = lines[1:]
            generated_sql = "\n".join(lines).strip()
        
        # Check if it's a valid SQL query
        # If the LLM explained why it can't generate SQL, handle that case
        if (
            "cannot generate" in generated_sql.lower() or
            "unable to create" in generated_sql.lower() or
            "can't create" in generated_sql.lower() or 
            "i can't" in generated_sql.lower()
        ):
            return {
                "success": False,
                "error": generated_sql
            }
        
        return {
            "success": True, 
            "sql": generated_sql
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating SQL query: {str(e)}"
        }
