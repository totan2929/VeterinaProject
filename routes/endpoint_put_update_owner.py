import sys
import os

# Configure system path to allow relative module imports from parent directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from database.db_connection import execute_single_query, execute_write_operation
from utils.functions import (
    clear_screen,
    pause,
    confirm_action_yn,
    validate_doc_number,
    validate_person_name,
    validate_address,
    validate_phone,
    validate_email,
    validate_status
)


def update_owner_by_document(doc_number: str, data: tuple) -> int:
    """
    Executes the SQL UPDATE query to modify all editable fields of an owner.

    Parameters:
        doc_number (str): Document number of the owner to update.
        data (tuple): Tuple containing (first_name, last_name, address, phone, email, status).

    Returns:
        int: Number of rows affected by the UPDATE operation.
    """
    # SQL query to update all fields of an existing owner by document number
    sql = """
        UPDATE owners
        SET first_name = %s, last_name = %s, address = %s, phone = %s, email = %s, status = %s
        WHERE doc_number = %s
    """
    # Unpack updated data fields and append the document number for the WHERE clause
    return execute_write_operation(sql, (*data, doc_number))


def run_put_owner() -> None:
    """
    Executes the main flow for the PUT endpoint (full owner update).
    Prompts for document search, captures new values, validates entries,
    requests Y/N confirmation, performs the database update, and prints JSON responses.
    """
    # Clear console before displaying output
    clear_screen()

    try:
        # Prompt user for the target owner's document number
        doc_input = input("Digite el número de documento del propietario a actualizar: ")
        doc_number = validate_doc_number(doc_input)

        # Check if the owner exists in the database
        current_owner = execute_single_query(
            "SELECT * FROM owners WHERE doc_number = %s", 
            (doc_number,)
        )

        # Handle case where owner does not exist (HTTP 404)
        if not current_owner:
            response = {
                "status": 404, 
                "message": f"Propietario con documento {doc_number} no existe en el sistema."
            }
            print(json.dumps(response, indent=2, ensure_ascii=False))
            return

        print(f"\nActualizando datos de: {current_owner['first_name']} {current_owner['last_name']}")

        # Capture and validate new data for each field
        first_name = validate_person_name(input("Nuevos nombres: "), "Nombres")
        last_name = validate_person_name(input("Nuevos apellidos: "), "Apellidos")
        address = validate_address(input("Nueva dirección: "))
        phone = validate_phone(input("Nuevo teléfono (10 dígitos): "))
        email = validate_email(input("Nuevo correo electrónico: "))
        status = validate_status(input("Estado (Active / Inactive): "))

        # Ask for confirmation before persisting changes to the database
        if not confirm_action_yn("¿Confirma la actualización total de este registro?"):
            canceled = {
                "status": 200, 
                "message": "Actualización cancelada por el usuario.", 
                "data": None
            }
            print(json.dumps(canceled, indent=2, ensure_ascii=False))
            return

        # Prepare update parameters
        update_data = (first_name, last_name, address, phone, email, status)

        # Execute database UPDATE query
        affected_rows = update_owner_by_document(doc_number, update_data)

        # Fetch the updated owner record to display in the response payload
        updated_owner = execute_single_query(
            "SELECT * FROM owners WHERE doc_number = %s", 
            (doc_number,)
        )

        # Build successful HTTP 200 response payload
        response = {
            "status": 200,
            "message": "Propietario actualizado exitosamente",
            "affected_rows": affected_rows,
            "data": updated_owner
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
    run_put_owner()
    