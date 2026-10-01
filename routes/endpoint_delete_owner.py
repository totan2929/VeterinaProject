import sys
import os

# Configure system path to allow relative module imports from parent directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from database.db_connection import execute_single_query, execute_write_operation
from utils.functions import clear_screen, pause, confirm_action_yn, validate_doc_number


def delete_owner_by_document(doc_number: str) -> int:
    """
    Executes the SQL DELETE query to remove an owner record by document number.

    Parameters:
        doc_number (str): The document number of the owner to be deleted.

    Returns:
        int: Number of rows affected by the DELETE operation.
    """
    # SQL query to physically delete an owner record from the database
    sql = "DELETE FROM owners WHERE doc_number = %s"
    return execute_write_operation(sql, (doc_number,))


def run_delete_owner() -> None:
    """
    Executes the main flow for the DELETE endpoint.
    Prompts for document number, validates input, checks record existence,
    requests Y/N confirmation, performs deletion, and outputs JSON responses.
    """
    # Clear console before displaying output
    clear_screen()

    try:
        # Prompt user for the target owner's document number
        doc_input = input("Digite el número de documento del propietario a eliminar: ")
        doc_number = validate_doc_number(doc_input)

        # Check if the owner exists in the database prior to deletion
        owner_record = execute_single_query(
            "SELECT * FROM owners WHERE doc_number = %s", 
            (doc_number,)
        )

        # Handle case where owner does not exist (HTTP 404)
        if not owner_record:
            response = {
                "status": 404, 
                "message": f"No se encontró propietario con documento {doc_number}."
            }
            print(json.dumps(response, indent=2, ensure_ascii=False))
            return

        # Display warning message before confirmation
        print(f"\n  ATENCIÓN: Se eliminará al propietario: {owner_record['first_name']} {owner_record['last_name']}")

        # Ask for confirmation before performing permanent deletion
        if not confirm_action_yn("¿Está completamente seguro de eliminar este registro permanentemente?"):
            canceled = {
                "status": 200, 
                "message": "Eliminación cancelada.", 
                "data": None
            }
            print(json.dumps(canceled, indent=2, ensure_ascii=False))
            return

        # Execute database DELETE query
        affected_rows = delete_owner_by_document(doc_number)

        # Build successful HTTP 200 response payload
        response = {
            "status": 200,
            "message": f"Propietario con documento {doc_number} eliminado satisfactoriamente",
            "deleted_record": owner_record,
            "affected_rows": affected_rows
        }
        # Print serialized JSON response with proper formatting
        print(json.dumps(response, indent=2, ensure_ascii=False, default=str))

    except ValueError as validation_err:
        # Handle data validation errors (HTTP 400)
        error_response = {
            "status": 400, 
            "error": "ValidationFailed", 
            "detail": str(validation_err)
        }
        print(json.dumps(error_response, indent=2, ensure_ascii=False))

    except Exception as err_db:
        # Handle database connection or execution errors (HTTP 500)
        error_response = {
            "status": 500, 
            "error": "DatabaseError", 
            "detail": str(err_db)
        }
        print(json.dumps(error_response, indent=2, ensure_ascii=False))

    finally:
        # Pause execution to allow viewing output before screen refresh/exit
        pause()


# Execute the main function only when running this script directly
if __name__ == "__main__":
    run_delete_owner()