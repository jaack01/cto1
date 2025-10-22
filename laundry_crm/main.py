from laundry_crm.database.database import initialize_database
from laundry_crm.config import DATABASE_FILE

def main():
    """Main function to initialize and run the CRM application."""
    # Initialize the database
    initialize_database(DATABASE_FILE)
    print(f"Database '{DATABASE_FILE}' initialized successfully.")

    # In the future, the main GUI loop will be started here.
    print("Laundry CRM application started.")

if __name__ == "__main__":
    main()
