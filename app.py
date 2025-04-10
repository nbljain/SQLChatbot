import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from typing import Dict, List, Any, Optional
import json
import time

# API base URL
API_URL = "http://localhost:8000"

def query_backend(endpoint: str, data: Dict = None, method: str = "GET", max_retries: int = 5) -> Dict:
    """Make a request to the backend API with retry logic"""
    url = f"{API_URL}{endpoint}"
    
    # Implement retry logic for backend connection
    retries = 0
    while retries < max_retries:
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                st.error(f"Unsupported HTTP method: {method}")
                return {"success": False, "error": f"Unsupported HTTP method: {method}"}
            
            return response.json()
        except requests.RequestException as e:
            retries += 1
            if retries >= max_retries:
                st.error(f"Error connecting to backend after {max_retries} attempts: {e}")
                return {"success": False, "error": f"Connection error: {e}"}
            
            # Wait before retrying (exponential backoff)
            time.sleep(min(2**retries, 10))
            
            # Show a warning on first retry
            if retries == 1:
                st.warning("Connecting to backend server... please wait.")
    
    return {"success": False, "error": "Failed to connect to backend service"}

def detect_chart_type(df: pd.DataFrame) -> str:
    """Detect suitable chart type based on dataframe content"""
    num_columns = len(df.select_dtypes(include=['number']).columns)
    cat_columns = len(df.select_dtypes(include=['object', 'category']).columns)
    
    if len(df.columns) <= 1:
        return "table"  # Default to table view for single column
    
    if num_columns >= 2:
        return "scatter"  # At least 2 numeric columns, scatter plot is possible
    
    if num_columns >= 1 and cat_columns >= 1:
        return "bar"  # One numeric and one categorical column
    
    if cat_columns >= 2:
        return "count"  # Multiple categorical columns
    
    return "table"  # Default to table

def display_results(results: Dict[str, Any]) -> None:
    """Display query results in Streamlit"""
    if not results or not results.get("success", False):
        st.error(f"Error: {results.get('error', 'Unknown error')}")
        return
    
    # Display the generated SQL query
    st.subheader("Generated SQL Query")
    st.code(results.get("sql", ""), language="sql")
    
    # Process and display the data
    data = results.get("data", [])
    if not data:
        st.info("No data returned from query.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Show raw data in table
    st.subheader("Data Table")
    st.dataframe(df)
    
    # Data visualization
    st.subheader("Data Visualization")
    
    # Only attempt visualization if there are enough rows
    if len(df) > 0:
        chart_type = detect_chart_type(df)
        
        # Get column names
        columns = df.columns.tolist()
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Only show visualization options if we have appropriate columns
        if len(numeric_columns) > 0:
            chart_types = ["Auto", "Bar", "Line", "Scatter", "Pie", "Histogram", "Box Plot"]
            selected_chart = st.selectbox("Select Chart Type", chart_types, index=0)
            
            if selected_chart == "Auto":
                selected_chart = chart_type
            
            # Column selection for visualization
            if len(numeric_columns) > 0:
                x_axis = st.selectbox("X-axis", columns, index=0)
                
                # Only show y-axis selection if there are numeric columns
                if len(numeric_columns) > 1:
                    y_axis = st.selectbox("Y-axis", numeric_columns, 
                                         index=0 if x_axis != numeric_columns[0] else 1)
                else:
                    y_axis = numeric_columns[0]
                
                # Only show color selection if there are categorical columns
                if len(categorical_columns) > 0:
                    color_col = st.selectbox("Color by", ["None"] + categorical_columns)
                    if color_col == "None":
                        color_col = None
                
                # Create the visualization
                if selected_chart == "Bar":
                    fig = px.bar(df, x=x_axis, y=y_axis, color=color_col, 
                                title=f"Bar Chart: {y_axis} by {x_axis}")
                    st.plotly_chart(fig)
                
                elif selected_chart == "Line":
                    fig = px.line(df, x=x_axis, y=y_axis, color=color_col,
                                 title=f"Line Chart: {y_axis} over {x_axis}")
                    st.plotly_chart(fig)
                
                elif selected_chart == "Scatter":
                    fig = px.scatter(df, x=x_axis, y=y_axis, color=color_col,
                                    title=f"Scatter Plot: {y_axis} vs {x_axis}")
                    st.plotly_chart(fig)
                
                elif selected_chart == "Pie":
                    fig = px.pie(df, values=y_axis, names=x_axis,
                                title=f"Pie Chart: {y_axis} distribution by {x_axis}")
                    st.plotly_chart(fig)
                
                elif selected_chart == "Histogram":
                    fig = px.histogram(df, x=x_axis, y=y_axis, color=color_col,
                                     title=f"Histogram: {x_axis}")
                    st.plotly_chart(fig)
                
                elif selected_chart == "Box Plot":
                    fig = px.box(df, x=x_axis, y=y_axis, color=color_col,
                               title=f"Box Plot: {y_axis} by {x_axis}")
                    st.plotly_chart(fig)
            else:
                st.info("Not enough numeric columns for visualization.")
        else:
            st.info("No numeric columns available for visualization.")
    else:
        st.info("Not enough data for visualization.")

def main():
    st.set_page_config(
        page_title="SQL Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("Natural Language SQL Chatbot")
    st.markdown("Ask questions about your data in plain English")
    
    # Check if API is available
    try:
        health_check = requests.get(f"{API_URL}/")
        if health_check.status_code != 200:
            st.error(f"Backend API is not responding correctly. Status code: {health_check.status_code}")
            st.stop()
    except requests.RequestException:
        st.error("Cannot connect to backend API. Please make sure the backend service is running.")
        st.stop()
    
    # Get available tables
    tables_response = query_backend("/tables")
    if tables_response:
        tables = tables_response.get("tables", [])
        
        # Display schema information
        with st.expander("Database Schema Information"):
            if tables:
                schema_response = query_backend("/schema", method="POST", data={})
                if schema_response and schema_response.get("schema"):
                    schema_data = schema_response.get("schema", {})
                    
                    for table_name, table_schema in schema_data.items():
                        st.subheader(f"Table: {table_name}")
                        schema_df = pd.DataFrame(
                            [(col, data_type) for col, data_type in table_schema.items()],
                            columns=["Column", "Type"]
                        )
                        st.dataframe(schema_df)
            else:
                st.info("No tables found in the database.")
    
    # Query input
    st.subheader("Ask a question about your data")
    
    # Example queries
    example_queries = [
        "Show me all employees",
        "What is the average performance score by department?",
        "List employees with performance scores above 4.0",
        "How many employees are there in each department?",
        "Find the employee with the highest performance score",
        "Show me all review scores in the Engineering department"
    ]
    
    # Show example queries as buttons
    st.write("Example questions:")
    cols = st.columns(3)
    for i, query in enumerate(example_queries):
        col_idx = i % 3
        if cols[col_idx].button(query, key=f"example_{i}"):
            st.session_state.query = query
    
    # Text input for query
    query = st.text_input("Enter your question:", key="query")
    
    if st.button("Run Query") or query:
        if query:
            with st.spinner("Generating SQL and fetching results..."):
                # Send query to backend
                results = query_backend("/query", data={"question": query}, method="POST")
                
                # Display results
                if results:
                    display_results(results)
                else:
                    st.error("No results returned from backend.")
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()