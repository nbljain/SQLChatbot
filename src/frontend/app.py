import streamlit as st
import pandas as pd
import traceback
import json
import requests
from typing import Dict, List, Any, Optional

# === Configuration ===
API_URL = "http://localhost:8000"

# Set page title and layout
st.set_page_config(
    page_title="SQL Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Helper Functions ===
def query_backend(endpoint: str, data: Dict = None, method: str = "GET") -> Dict:
    """Make a request to the backend API"""
    url = f"{API_URL}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, timeout=30)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"API Error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"success": False, "error": f"Request Error: {str(e)}"}

def detect_chart_type(df: pd.DataFrame) -> str:
    """Detect suitable chart type based on dataframe content"""
    # Check if dataframe is empty
    if df.empty:
        return "none"
    
    # Get column types
    num_columns = df.select_dtypes(include=['number']).columns.tolist()
    cat_columns = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
    date_columns = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
    
    # No numeric columns means no visualization
    if not num_columns:
        return "none"
    
    # Check for time series data
    if date_columns and len(num_columns) >= 1:
        return "line"
    
    # If we have categorical and numeric columns, suggest bar chart
    if cat_columns and num_columns:
        # If categorical column has few unique values, use bar chart
        if len(df[cat_columns[0]].unique()) <= 10:
            return "bar"
    
    # If we have multiple numeric columns, suggest scatter plot
    if len(num_columns) >= 2:
        return "scatter"
    
    # If we have few rows and at least one categorical column, suggest bar
    if len(df) <= 20 and cat_columns:
        return "bar"
    
    # If we have multiple numeric columns and a categorical column, suggest grouped bar
    if len(num_columns) >= 2 and cat_columns:
        return "grouped_bar"
    
    # Default to histogram for a single numeric column
    if len(num_columns) == 1:
        return "histogram"
    
    # Default
    return "none"

def display_results(results: Dict[str, Any]) -> None:
    """Display query results in Streamlit"""
    if not results.get("success", False):
        st.error(results.get("error", "Unknown error"))
        return
    
    if not results.get("data"):
        st.info("No data returned by the query.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(results["data"])
    
    # Show data table
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Found {len(results['data'])} {'row' if len(results['data']) == 1 else 'rows'}")
    
    # Detect and show appropriate visualization
    if not df.empty:
        # Try to detect suitable chart type
        chart_type = detect_chart_type(df)
        
        # Convert any date-like strings to datetime
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col], errors='ignore')
                except:
                    pass
        
        # Convert numeric columns if stored as strings
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
        
        # Get numeric and categorical columns after conversion
        num_columns = df.select_dtypes(include=['number']).columns.tolist()
        cat_columns = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
        
        # Show visualization section
        st.subheader("Visualization")
        
        # Create visualization based on detected type
        if chart_type != "none" and num_columns:
            if chart_type == "bar" and cat_columns and num_columns:
                cat_col = cat_columns[0]
                num_col = num_columns[0]
                st.bar_chart(df.set_index(cat_col)[num_col])
            
            elif chart_type == "line" and num_columns:
                line_cols = num_columns[:3]  # Limit to first 3 numeric columns
                st.line_chart(df[line_cols])
            
            elif chart_type == "scatter" and len(num_columns) >= 2:
                x_col = num_columns[0]
                y_col = num_columns[1]
                fig = {
                    "data": [{"type": "scatter", "x": df[x_col], "y": df[y_col]}],
                    "layout": {"title": f"{y_col} vs {x_col}", "xaxis": {"title": x_col}, "yaxis": {"title": y_col}}
                }
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "grouped_bar" and cat_columns and len(num_columns) >= 2:
                cat_col = cat_columns[0]
                chart_data = df.set_index(cat_col)[num_columns[:3]]
                st.bar_chart(chart_data)
            
            elif chart_type == "histogram" and num_columns:
                num_col = num_columns[0]
                fig = {
                    "data": [{"type": "histogram", "x": df[num_col]}],
                    "layout": {"title": f"Distribution of {num_col}"}
                }
                st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            with st.expander("Data Statistics"):
                if num_columns:
                    st.write("Numeric Statistics")
                    st.dataframe(df[num_columns].describe())
        else:
            st.info("No suitable visualization detected for this data")

# === Initialize Session State ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === Sidebar ===
st.sidebar.title("Database Connections")

# Refresh connections list
if "connections" not in st.session_state:
    try:
        connections_response = query_backend("connections")
        if connections_response and "connections" in connections_response:
            st.session_state.connections = connections_response["connections"]
        else:
            st.sidebar.error("Failed to fetch database connections")
            st.session_state.connections = []
    except Exception as e:
        st.sidebar.error(f"Error fetching connections: {str(e)}")
        st.session_state.connections = []

# Get active connection
try:
    active_response = query_backend("connections/active")
    if active_response and "connection" in active_response:
        active_db = active_response["connection"]
        st.sidebar.subheader(f"Connected to: {active_db.get('display_name', 'Unknown')}")
        st.sidebar.write(active_db.get("description", ""))
    else:
        st.sidebar.warning("No active database connection")
except Exception as e:
    st.sidebar.error(f"Error getting active connection: {str(e)}")

# Tabs for connection management
switch_tab, add_tab, manage_tab = st.sidebar.tabs(["Switch", "Add New", "Manage"])

with switch_tab:
    if "connections" in st.session_state and st.session_state.connections:
        st.write("Switch Database Connection")
        
        # Create a list of connection display names with active one first
        connections = sorted(st.session_state.connections, 
                             key=lambda x: (not x.get("is_active", False), x.get("display_name", "")))
        conn_names = [c["display_name"] for c in connections]
        
        selected_conn = st.selectbox(
            "Select Database", 
            conn_names,
            index=0
        )
        
        # Find the connection details for the selected connection
        selected_conn_info = next((c for c in connections if c["display_name"] == selected_conn), None)
        
        if selected_conn_info and not selected_conn_info.get("is_active", False):
            if st.button("Switch Connection", type="primary", use_container_width=True):
                with st.spinner(f"Switching to {selected_conn}..."):
                    switch_resp = query_backend(
                        "connections/switch", 
                        {"name": selected_conn_info["name"]}, 
                        method="POST"
                    )
                    if switch_resp and switch_resp.get("success"):
                        st.success(switch_resp.get("message", "Connection switched successfully"))
                        # Refresh the connections list
                        if "connections" in st.session_state:
                            del st.session_state.connections
                        st.rerun()
                    else:
                        st.error(switch_resp.get("message", "Failed to switch connection"))
        elif selected_conn_info and selected_conn_info.get("is_active", False):
            st.info("This database is already active")
    else:
        st.write("No additional connections available")

with add_tab:
    st.write("Add New Database Connection")
    
    new_conn_name = st.text_input(
        "Connection Name (internal ID)", 
        help="Unique identifier for this connection (no spaces, lowercase)",
        key="new_conn_name"
    )
    
    new_conn_display = st.text_input(
        "Display Name", 
        help="Human-readable name for this connection",
        key="new_conn_display"
    )
    
    new_conn_desc = st.text_area(
        "Description", 
        help="Optional description of this database",
        key="new_conn_desc"
    )
    
    new_conn_type = st.selectbox(
        "Database Type",
        ["sqlite", "postgresql", "mysql", "oracle", "mssql"],
        key="new_conn_type"
    )
    
    # Help text for connection strings
    conn_string_help = {
        "sqlite": "sqlite:///database_file.db",
        "postgresql": "postgresql://user:password@host:port/dbname",
        "mysql": "mysql://user:password@host:port/dbname",
        "oracle": "oracle://user:password@host:port/dbname",
        "mssql": "mssql+pyodbc://user:password@host:port/dbname?driver=ODBC+Driver"
    }
    
    new_conn_string = st.text_input(
        "Connection String", 
        help=conn_string_help.get(new_conn_type, ""), 
        key="new_conn_string",
        type="password"  # Hide the connection string for security
    )
    
    if st.button("Add Connection"):
        if not new_conn_name or not new_conn_string:
            st.error("Name and connection string are required")
        else:
            new_conn = {
                "name": new_conn_name,
                "display_name": new_conn_display or new_conn_name,
                "description": new_conn_desc,
                "type": new_conn_type,
                "connection_string": new_conn_string
            }
            
            with st.spinner("Adding connection..."):
                try:
                    add_resp = query_backend("connections/add", new_conn, method="POST")
                    if add_resp and add_resp.get("success"):
                        st.success(add_resp.get("message", "Connection added successfully"))
                        # Clear the form
                        st.session_state.new_conn_name = ""
                        st.session_state.new_conn_display = ""
                        st.session_state.new_conn_desc = ""
                        st.session_state.new_conn_string = ""
                        # Refresh connections list
                        if "connections" in st.session_state:
                            del st.session_state.connections
                        st.rerun()
                    else:
                        st.error("Failed to add connection")
                except Exception as e:
                    st.error(f"Error adding connection: {str(e)}")

with manage_tab:
    st.write("Manage Existing Connections")
    if "connections" in st.session_state and st.session_state.connections:
        conn_to_delete = st.selectbox(
            "Select Connection to Remove", 
            [c["display_name"] for c in st.session_state.connections if c["name"] != "default"]
        )
        
        if conn_to_delete:
            conn_name = next((c["name"] for c in st.session_state.connections 
                            if c["display_name"] == conn_to_delete), None)
            
            if conn_name and st.button("Delete Connection", type="primary", use_container_width=True):
                with st.spinner(f"Deleting {conn_to_delete}..."):
                    try:
                        delete_resp = query_backend(f"connections/{conn_name}", method="DELETE")
                        if delete_resp and delete_resp.get("success"):
                            st.success(delete_resp.get("message", "Connection deleted successfully"))
                            # Refresh connections list
                            if "connections" in st.session_state:
                                del st.session_state.connections
                            st.rerun()
                        else:
                            st.error("Failed to delete connection")
                    except Exception as e:
                        st.error(f"Error deleting connection: {str(e)}")
    else:
        st.info("No connections available to delete")

# === Main Content ===
st.title("SQL Chatbot")
st.write("Ask questions about your database in natural language.")

# Database schema section
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
if "tables" in st.session_state and st.session_state.tables:
    with st.expander("Database Schema", expanded=False):
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
st.header("Chat History")
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
                    
                    # Show data table with expander
                    with st.expander("Data Results", expanded=True):
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        st.caption(f"Found {len(chat['data'])} {'row' if len(chat['data']) == 1 else 'rows'}")
                    
                    # Add a "Show Visualizations" button for each chat response
                    viz_key = f"viz_btn_{i}"
                    show_viz = False
                    
                    if st.button(f"Show Visualizations", key=viz_key):
                        show_viz = True
                    
                    if show_viz and not df.empty:
                        # Try to detect suitable chart type
                        chart_type = detect_chart_type(df)
                        
                        # Convert any date-like strings to datetime
                        for col in df.columns:
                            if df[col].dtype == 'object':
                                try:
                                    df[col] = pd.to_datetime(df[col], errors='ignore')
                                except:
                                    pass
                        
                        # Convert numeric columns if stored as strings
                        for col in df.columns:
                            if df[col].dtype == 'object':
                                try:
                                    df[col] = pd.to_numeric(df[col], errors='ignore')
                                except:
                                    pass
                        
                        # Get numeric and categorical columns after conversion
                        num_columns = df.select_dtypes(include=['number']).columns.tolist()
                        cat_columns = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
                        
                        # Create visualization based on detected type
                        if chart_type != "none" and num_columns:
                            if chart_type == "bar" and cat_columns and num_columns:
                                cat_col = cat_columns[0]
                                num_col = num_columns[0]
                                st.bar_chart(df.set_index(cat_col)[num_col])
                            
                            elif chart_type == "line" and num_columns:
                                line_cols = num_columns[:3]  # Limit to first 3 numeric columns
                                st.line_chart(df[line_cols])
                            
                            elif chart_type == "scatter" and len(num_columns) >= 2:
                                x_col = num_columns[0]
                                y_col = num_columns[1]
                                fig = {
                                    "data": [{"type": "scatter", "x": df[x_col], "y": df[y_col]}],
                                    "layout": {"title": f"{y_col} vs {x_col}", "xaxis": {"title": x_col}, "yaxis": {"title": y_col}}
                                }
                                st.plotly_chart(fig, use_container_width=True)
                            
                            elif chart_type == "grouped_bar" and cat_columns and len(num_columns) >= 2:
                                cat_col = cat_columns[0]
                                chart_data = df.set_index(cat_col)[num_columns[:3]]
                                st.bar_chart(chart_data)
                            
                            elif chart_type == "histogram" and num_columns:
                                num_col = num_columns[0]
                                fig = {
                                    "data": [{"type": "histogram", "x": df[num_col]}],
                                    "layout": {"title": f"Distribution of {num_col}"}
                                }
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # Show statistics
                            with st.expander("Data Statistics"):
                                if num_columns:
                                    st.write("Numeric Statistics")
                                    st.dataframe(df[num_columns].describe())
                        else:
                            st.info("No suitable visualization detected for this data")
                        
                elif "error" in chat:
                    st.error(chat["error"])
                else:
                    st.info("No data returned by the query.")
        else:
            st.markdown(f"**SQL Chatbot**: {chat['content']}")

# Input area
st.header("Ask a Question")
user_input = st.text_area("Enter your question in natural language:", 
                       "Show me all tables in the database", 
                       height=100)

if st.button("Submit Question"):
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Show loading spinner
        with st.spinner("Generating SQL and fetching results..."):
            try:
                # Query the backend
                result = query_backend("query", {"question": user_input}, method="POST")
                
                # Log raw response for debugging
                st.sidebar.write("Raw API Response:", result)
                
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
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")
                st.sidebar.error(f"Exception details: {traceback.format_exc()}")
                
                # Add error to chat history
                chat_response = {
                    "role": "assistant",
                    "content": "I encountered an error while processing your query.",
                    "error": str(e)
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