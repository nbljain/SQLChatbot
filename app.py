import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from typing import Dict, List, Any

# Set page title and configuration
st.set_page_config(
    page_title="SQL Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API URL
API_BASE_URL = "http://localhost:8000"

def query_backend(endpoint: str, data: Dict = None, method: str = "GET") -> Dict:
    """Make a request to the backend API"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"API error: {str(e)}"}
    except ValueError as e:
        return {"success": False, "error": f"Invalid response from API: {str(e)}"}

def detect_chart_type(df: pd.DataFrame) -> str:
    """Detect suitable chart type based on dataframe content"""
    # Some basic heuristics for chart type detection
    num_columns = len(df.select_dtypes(include='number').columns)
    num_categorical = len(df.select_dtypes(include=['object', 'category']).columns)
    row_count = len(df)
    
    # For single numeric column with categories, use bar chart
    if num_columns == 1 and num_categorical >= 1:
        return "bar"
    
    # For 2+ numeric columns, use scatter
    if num_columns >= 2:
        return "scatter"
    
    # Time series data often has a datetime column
    datetime_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
    if datetime_cols and num_columns >= 1:
        return "line"
    
    # For 1 numeric column distribution
    if num_columns == 1 and num_categorical == 0:
        return "histogram"
    
    # Proportional data (percentages, parts of whole)
    if row_count < 10 and num_columns == 1:
        return "pie"
    
    # Default to bar chart
    return "bar"

def display_results(results: Dict[str, Any]) -> None:
    """Display query results in Streamlit"""
    if not results.get("success", False):
        st.error(results.get("error", "Unknown error occurred"))
        return
    
    # Display the SQL query
    with st.expander("Generated SQL Query", expanded=True):
        st.code(results["sql"], language="sql")
    
    # Process results
    data = results.get("data", [])
    if not data:
        st.info("Query executed successfully but returned no data.")
        return
    
    # Convert to dataframe
    df = pd.DataFrame(data)
    
    # Display data as table
    st.subheader("Results")
    st.dataframe(df, use_container_width=True)
    
    # Determine if we can create a visualization
    num_columns = len(df.select_dtypes(include='number').columns)
    if len(df) > 0 and num_columns > 0:
        st.subheader("Visualization")
        
        col1, col2 = st.columns([3, 1])
        
        # Auto-detect chart type
        suggested_chart = detect_chart_type(df)
        
        with col2:
            # Chart type selector
            chart_type = st.selectbox(
                "Chart type:",
                options=["bar", "line", "scatter", "pie", "histogram"],
                index=["bar", "line", "scatter", "pie", "histogram"].index(suggested_chart)
            )
            
            # Pick columns for X and Y axes
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            datetime_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
            
            # Default columns based on chart type
            x_default = 0
            if chart_type == "bar" and categorical_cols:
                x_options = categorical_cols + numeric_cols
                x_default = 0
            elif chart_type == "line" and datetime_cols:
                x_options = datetime_cols + numeric_cols + categorical_cols
                x_default = 0
            else:
                x_options = df.columns.tolist()
            
            x_axis = st.selectbox("X axis:", options=x_options, index=min(x_default, len(x_options)-1))
            
            if chart_type != "histogram" and chart_type != "pie":
                y_default = 0
                if numeric_cols and x_axis in numeric_cols:
                    # If x is numeric, pick a different numeric column for y if available
                    other_numeric = [col for col in numeric_cols if col != x_axis]
                    if other_numeric:
                        y_options = other_numeric
                    else:
                        y_options = numeric_cols
                else:
                    y_options = numeric_cols
                
                if not y_options:
                    y_options = df.columns.tolist()
                
                y_axis = st.selectbox("Y axis:", options=y_options, index=min(y_default, len(y_options)-1))
            
            # Color option for more complex charts
            if chart_type in ["scatter", "bar", "line"]:
                color_options = ["None"] + categorical_cols
                color_col = st.selectbox("Color by:", options=color_options)
                if color_col == "None":
                    color_col = None
        
        with col1:
            # Create the appropriate chart based on selection
            try:
                if chart_type == "bar":
                    fig = px.bar(df, x=x_axis, y=y_axis if chart_type != "pie" else None, 
                                color=color_col, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "line":
                    fig = px.line(df, x=x_axis, y=y_axis, color=color_col, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "scatter":
                    fig = px.scatter(df, x=x_axis, y=y_axis, color=color_col, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "pie":
                    # For pie charts, x_axis is the category and y_axis is the value
                    fig = px.pie(df, names=x_axis, values=numeric_cols[0] if numeric_cols else None, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "histogram":
                    fig = px.histogram(df, x=x_axis, height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            except Exception as e:
                st.error(f"Error creating visualization: {str(e)}")

def main():
    # Sidebar for database connection selection
    st.sidebar.title("Database Connections")
    
    # Get all available connections
    connections_resp = query_backend("/connections", method="GET")
    
    if connections_resp.get("success", False) == False and "connections" in connections_resp:
        connections = connections_resp["connections"]
    else:
        connections = []
    
    # Get active connection
    active_conn_resp = query_backend("/connections/active", method="GET")
    active_conn = None
    if active_conn_resp.get("success", False) == False and "connection" in active_conn_resp:
        active_conn = active_conn_resp["connection"]
    
    # Display available connections
    if connections:
        st.sidebar.subheader("Available Connections")
        for conn in connections:
            is_active = conn.get("is_active", False) or (active_conn and active_conn.get("name") == conn.get("name"))
            
            conn_label = f"{conn['display_name']} ({'Active' if is_active else 'Switch'})"
            if st.sidebar.button(conn_label, key=f"conn_{conn['name']}"):
                if not is_active:
                    # Switch to this connection
                    switch_resp = query_backend("/connections/switch", {"name": conn["name"]}, "POST")
                    if switch_resp.get("success", True):
                        st.toast(f"Switched to {conn['display_name']}")
                        st.rerun()
                    else:
                        st.sidebar.error(switch_resp.get("error", "Failed to switch connection"))
    
    # Option to add a new connection
    with st.sidebar.expander("Add New Connection"):
        conn_name = st.text_input("Connection Name (unique)", key="new_conn_name")
        conn_display = st.text_input("Display Name", key="new_conn_display")
        conn_desc = st.text_area("Description", key="new_conn_desc")
        conn_type = st.selectbox("Type", ["sqlite", "postgresql", "mysql", "databricks"], key="new_conn_type")
        conn_string = st.text_input("Connection String", key="new_conn_string", help="e.g., sqlite:///database.db or postgresql://user:password@localhost/dbname")
        
        if st.button("Add Connection"):
            if not conn_name or not conn_display or not conn_string:
                st.sidebar.error("Please fill in all required fields")
            else:
                new_conn_data = {
                    "name": conn_name,
                    "display_name": conn_display,
                    "description": conn_desc,
                    "type": conn_type,
                    "connection_string": conn_string
                }
                add_resp = query_backend("/connections/add", new_conn_data, "POST")
                if add_resp.get("success", True):
                    st.toast(f"Added new connection: {conn_display}")
                    st.rerun()
                else:
                    st.sidebar.error(add_resp.get("error", "Failed to add connection"))
    
    # Main content
    st.title("SQL Chatbot 🤖")
    st.markdown("Ask questions about your data in natural language.")
    
    # Display current connection info
    if active_conn:
        st.subheader(f"Connected to: {active_conn.get('display_name', 'Unknown')}")
        st.caption(active_conn.get('description', ''))
    
    # Query input
    query = st.text_area("Enter your question:", height=100, placeholder="e.g., Show me the total sales by product category for last month")
    
    if st.button("Ask"):
        if query:
            with st.spinner("Processing query..."):
                # Call the API with the query
                response = query_backend("/query", {"question": query}, "POST")
                display_results(response)
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()