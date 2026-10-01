import sys
import os

# Configure system path to allow relative module imports from parent directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from database.db_connection import execute_single_query
from utils.functions import clear_screen, pause


def fetch_owner_by_document(doc_number: str) -> dict:
    """
    Fetches a single owner record from the database based on their document number.

    Parameters:
        doc_number (str): The identification document number to search for.

    Returns:
        dict: A dictionary containing the owner's data, or None if not found.
    """
    # SQL query to search for a specific owner by document number
    sql = """
        SELECT owner_id, doc_type, doc_number, first_name, last_name,
                birth_date, address, phone, email, status, created_at
        FROM owners
        WHERE doc_number = %s
    """
    # Execute single query returning one record matching the parameter
    return execute_single_query(sql, (doc_number,))


def run_get_owner_by_document():
    """
    Executes the interactive GET by document flow.
    Prompts the user for a document number, validates the input, queries the database,
    and returns an HTTP 200/404/500 formatted JSON response.
    """
    # Clear console before displaying output
    clear_screen()
    
    try:
        # Request document number input from user
        doc_number = input("Enter owner document number to search: ").strip()

        # Validate that the input is not empty
        if not doc_number:
            error_response = {
                "status": 400,
                "error": "BadRequest",
                "detail": "Data entered does not have the complete or required structure. Document number cannot be empty."
            }
            print(json.dumps(error_response, indent=2, ensure_ascii=False))
            return

        # Fetch the owner from the database
        owner = fetch_owner_by_document(doc_number)

        # Handle case where owner is not found (HTTP 404)
        if not owner:
            not_found_response = {
                "status": 404,
                "error": "NotFound",
                "detail": f"No owner found with document number '{doc_number}'."
            }
            print(json.dumps(not_found_response, indent=2, ensure_ascii=False))
            return

        # Build successful HTTP 200 response payload
        response = {
            "status": 200,
            "message": "Owner found successfully.",
            "data": owner
        }
        
        # Print serialized JSON response with proper formatting
        print(json.dumps(response, indent=2, ensure_ascii=False, default=str))

    except (PermissionError, ConnectionError, NameError, RuntimeError) as err_db:
        # Handle specific database or connection errors (HTTP 500)
        error_response = {
            "status": 500,
            "error": "DatabaseError",
            "detail": str(err_db)
        }
        print(json.dumps(error_response, indent=2, ensure_ascii=False))

    except Exception as unexpected_err:
        # Handle unhandled unexpected errors (HTTP 500)
        error_response = {
            "status": 500,
            "error": "UnexpectedError",
            "detail": str(unexpected_err)
        }
        print(json.dumps(error_response, indent=2, ensure_ascii=False))

    finally:
        # Pause execution to allow viewing output before screen refresh/exit
        pause()


# Execute the main function only when running this script directly
if __name__ == "__main__":
    run_get_owner_by_document()