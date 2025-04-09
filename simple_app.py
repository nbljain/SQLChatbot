import streamlit as st
import requests
import pandas as pd

st.title("Simple SQL Query App")

# Backend API URL
API_URL = "http://127.0.0.1:8000/query"

# Input area
query = st.text_input("Enter your question:", "Show me the average salary by department")

if st.button("Run Query"):
    try:
        # Call the API
        st.write(f"Sending request to {API_URL}...")
        response = requests.post(API_URL, json={"question": query}, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        # Display result
        if result.get("success", False):
            st.success("Query executed successfully")
            
            # Show SQL
            st.subheader("Generated SQL")
            st.code(result.get("sql", ""), language="sql")
            
            # Show data
            st.subheader("Results")
            if result.get("data"):
                df = pd.DataFrame(result["data"])
                st.dataframe(df)
            else:
                st.info("No data returned")
        else:
            st.error(f"Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error: {str(e)}")