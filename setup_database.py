from app.data.setup_sample_db import setup_employee_projects_db, setup_store_db

if __name__ == "__main__":
    print("Setting up sample databases...")
    
    # Set up the employee/projects database
    if setup_employee_projects_db():
        print("✅ Employee/Projects database created successfully")
    else:
        print("❌ Error creating Employee/Projects database")
    
    # Set up the store database
    if setup_store_db():
        print("✅ Store database created successfully")
    else:
        print("❌ Error creating Store database")
        
    print("\nDatabase setup complete. You can now run the application.")
    print("Run the following command to start the application:")
    print("python -m fastapi_backend & streamlit run app.py")