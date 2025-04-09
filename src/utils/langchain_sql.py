import os
import json
import logging
import re
from langchain_openai import ChatOpenAI
from src.db.database import get_all_table_schemas, execute_sql_query

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        
        # Create a direct prompt for SQL generation and explanation
        prompt = f"""
        You are a SQL expert who also explains data in a clear and insightful way.
        
        TASK 1: Given the user question, create a SQL query that will answer the user's question.
        TASK 2: Provide a brief explanation, data insights, and follow-up questions based on the query.
        
        {schema}
        
        SQL GUIDANCE:
        - Use aliases to make complex queries more readable
        - Use appropriate JOIN types and optimize the query for readability
        - Use proper filtering with WHERE clauses
        - Provide appropriate sorting with ORDER BY when needed
        
        User Question: {user_question}
        
        Return your answer in the following format:
        
        ```sql
        -- Your SQL query here
        ```
        
        ```json
        {{
            "explanation": "Brief explanation of what the SQL query does and how it answers the question",
            "insights": "Data insights or interpretation advice to help understand the results",
            "follow_up_questions": ["Potential follow-up question 1", "Potential follow-up question 2"]
        }}
        ```
        """
        
        # Generate SQL and explanation with the model
        response = llm.invoke(prompt)
        response_content = response.content.strip()
        
        # Extract the SQL query and JSON data from the response
        sql_match = re.search(r"```sql\s+(.*?)\s+```", response_content, re.DOTALL)
        json_match = re.search(r"```json\s+(.*?)\s+```", response_content, re.DOTALL)
        
        # Initialize default values
        sql_query = ""
        explanation = "Query executed successfully."
        insights = "Here are the results of your query."
        follow_up_questions = []
        
        # Extract SQL if found
        if sql_match:
            sql_query = sql_match.group(1).strip()
        else:
            # Try to extract any SQL-like statement if no code block
            sql_match = re.search(r"SELECT\s+.*?;", response_content, re.DOTALL | re.IGNORECASE)
            if sql_match:
                sql_query = sql_match.group(0).strip()
            else:
                # Fallback: attempt to extract content between SQL and JSON blocks
                lines = response_content.split('\n')
                sql_lines = []
                in_sql_block = False
                
                for line in lines:
                    if line.strip() == "```sql":
                        in_sql_block = True
                        continue
                    elif line.strip() == "```" and in_sql_block:
                        in_sql_block = False
                        break
                    elif in_sql_block:
                        sql_lines.append(line)
                
                if sql_lines:
                    sql_query = '\n'.join(sql_lines).strip()
                else:
                    return {"success": False, "error": "Could not extract SQL query from the response"}
        
        # Extract JSON content if found
        if json_match:
            try:
                json_str = json_match.group(1).strip()
                json_data = json.loads(json_str)
                explanation = json_data.get("explanation", explanation)
                insights = json_data.get("insights", insights)
                follow_up_questions = json_data.get("follow_up_questions", follow_up_questions)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON from LLM response: {e}")
                # Continue with default values if JSON parsing fails
        
        # Check if we have a valid SQL query
        if not sql_query:
            return {"success": False, "error": "Failed to generate a valid SQL query"}
            
        # Clean and normalize the SQL query (remove any trailing/leading comments)
        sql_query = re.sub(r'^\s*--.*?\n', '', sql_query, flags=re.MULTILINE).strip()
        
        return {
            "success": True, 
            "sql": sql_query,
            "explanation": explanation,
            "insights": insights,
            "follow_up_questions": follow_up_questions
        }
    except Exception as e:
        logger.error(f"Error in SQL generation: {str(e)}")
        return {"success": False, "error": str(e)}