from app.data.setup_sample_db import setup_employee_projects_db, setup_store_db

if __name__ == "__main__":
    print("Setting up sample databases...")
    
    # Set up the employee/projects database
    setup_employee_projects_db()
    
    # Set up the store database
    setup_store_db()
    
    print("\nDatabases setup complete. Restart the application to use the new databases.")