import streamlit as st
import pandas as pd
import requests
import json
from typing import Dict, List, Any

# Set page configuration
st.set_page_config(
    page_title="SQL Chatbot",
    page_icon="💬",
    layout="wide"
)

# Backend API URL
BACKEND_URL = "http://localhost:8000"

# Function to fetch data from the backend API
def query_backend(endpoint: str, data: Dict = None, method: str = "GET") -> Dict:
    """Make a request to the backend API"""
    try:
        if method == "GET":
            response = requests.get(f"{BACKEND_URL}/{endpoint}")
        else:  # POST
            response = requests.post(f"{BACKEND_URL}/{endpoint}", json=data)
        
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return {"success": False, "error": str(e)}

# Function to display query results
def display_results(results: Dict[str, Any]) -> None:
    """Display query results in Streamlit"""
    if not results.get("success", False):
        st.error(f"Error: {results.get('error', 'Unknown error')}")
        return
    
    # Display the SQL query
    with st.expander("Generated SQL Query", expanded=True):
        st.code(results.get("sql", ""), language="sql")
    
    # Display the data results
    data = results.get("data", [])
    if data:
        st.subheader("Query Results")
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(data)
        
        # Add styling to the dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Show row count
        st.caption(f"Found {len(data)} {'row' if len(data) == 1 else 'rows'}")
    else:
        st.info("No data returned by the query.")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Main app layout
st.title("💬 SQL Chatbot")
st.subheader("Ask questions about your database in natural language")

# Sidebar with database info
with st.sidebar:
    st.header("Database Information")
    
    # Fetch and display table list
    if st.button("Refresh Database Schema"):
        with st.spinner("Fetching database schema..."):
            tables_response = query_backend("tables")
            
            if tables_response.get("tables"):
                st.session_state.tables = tables_response.get("tables", [])
                st.success(f"Found {len(st.session_state.tables)} tables in the database")
            else:
                st.error("Could not fetch database tables")
    
    # Display tables if available
    if hasattr(st.session_state, "tables") and st.session_state.tables:
        st.subheader("Database Tables")
        for table in st.session_state.tables:
            with st.expander(table):
                # Fetch schema for this table when the expander is clicked
                schema_resp = query_backend("schema", {"table_name": table}, method="POST")
                if schema_resp.get("schema", {}).get(table):
                    schema_data = schema_resp["schema"][table]
                    for col, type_info in schema_data.items():
                        st.text(f"• {col} ({type_info})")
                else:
                    st.text("Could not fetch schema")

# Display chat history
st.subheader("Chat History")
for i, chat in enumerate(st.session_state.chat_history):
    if chat["role"] == "user":
        st.markdown(f"**You**: {chat['content']}")
    else:
        if "sql" in chat:
            with st.chat_message("assistant"):
                st.markdown("**SQL Chatbot**:")
                with st.expander("Generated SQL", expanded=False):
                    st.code(chat["sql"], language="sql")
                
                if "data" in chat and chat["data"]:
                    df = pd.DataFrame(chat["data"])
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.caption(f"Found {len(chat['data'])} {'row' if len(chat['data']) == 1 else 'rows'}")
                elif "error" in chat:
                    st.error(chat["error"])
                else:
                    st.info("No data returned by the query.")
        else:
            st.markdown(f"**SQL Chatbot**: {chat['content']}")

# Input area
st.subheader("Ask a Question")
user_input = st.text_area("Enter your question in natural language:", 
                           "Show me all tables in the database", 
                           height=100)

if st.button("Submit Question"):
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Show loading spinner
        with st.spinner("Generating SQL and fetching results..."):
            # Query the backend
            result = query_backend("query", {"question": user_input}, method="POST")
            
            # Add response to chat history
            if result.get("success", False):
                chat_response = {
                    "role": "assistant",
                    "sql": result.get("sql", ""),
                    "data": result.get("data", [])
                }
            else:
                chat_response = {
                    "role": "assistant",
                    "content": "I couldn't process your query.",
                    "error": result.get("error", "Unknown error")
                }
            
            st.session_state.chat_history.append(chat_response)
        
        # Rerun to update the UI with new chat history
        st.rerun()
    else:
        st.warning("Please enter a question.")

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()

# Footer
st.markdown("---")
st.caption("SQL Chatbot powered by LangChain, FastAPI, and Streamlit")
