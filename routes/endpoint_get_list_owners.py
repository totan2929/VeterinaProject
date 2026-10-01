import sys
import os

# Configure system path to allow relative module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from database.db_connection import execute_multiple_query
from utils.functions import clear_screen, pause


def fetch_owners(limit=50, offset=0):
    """
    Fetches a paginated list of owners from the database.

    Parameters:
        limit (int): Maximum number of records to return (default is 50).
        offset (int): Number of records to skip for pagination (default is 0).

    Returns:
        list: A list of dictionaries containing owner information.
    """
    sql = """
        SELECT owner_id, doc_type, doc_number, first_name, last_name,
                birth_date, address, phone, email, status, created_at
        FROM owners
        ORDER BY owner_id ASC
        LIMIT %s OFFSET %s
    """
    return execute_multiple_query(sql, (limit, offset))


def run_get_owners():
    """
    Executes the main flow of the GET owners endpoint.
    Clears the terminal, performs the database query, prints the formatted JSON response,
    and handles potential database connection errors or unexpected exceptions.
    """
    # Clear console before displaying output
    clear_screen()
    
    try:
        # Retrieve owner records from the database
        records = fetch_owners()
        
        # Build successful HTTP 200 response payload
        response = {
            "status": 200,
            "total_records": len(records),
            "data": records
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
        # Handle unhandled unexpected errors
        error_response = {
            "status": 500,
            "error": "UnexpectedError",
            "detail": str(unexpected_err)
        }
        print(json.dumps(error_response, indent=2, ensure_ascii=False))

    finally:
        # Pause execution to allow viewing output before screen refresh/exit
        pause()


if __name__ == "__main__":
    run_get_owners()