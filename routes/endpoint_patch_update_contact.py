import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from database.db_connection import execute_single_query, execute_write_operation
from utils.functions import (
    clear_screen,
    pause,
    confirm_action_yn,
    validate_doc_number,
    validate_phone,
    validate_address,
    validate_email
)

def run_patch_contact():
    clear_screen()
    try:
        print("=== ACTUALIZACIÓN PARCIAL DE CONTACTO (PATCH) ===\n")
        doc_input = input("Digite el documento del propietario: ")
        doc_number = validate_doc_number(doc_input)

        current_owner = execute_single_query("SELECT * FROM owners WHERE doc_number = %s", (doc_number,))
        if not current_owner:
            response = {"status": 404, "message": f"Propietario con documento {doc_number} no existe."}
            print(json.dumps(response, indent=2, ensure_ascii=False))
            return

        print(f"\nPropietario: {current_owner['first_name']} {current_owner['last_name']}")
        print(f"Teléfono actual: {current_owner['phone']}")
        print(f"Dirección actual: {current_owner['address']}")
        print(f"Correo actual: {current_owner['email']}\n")

        print("Presione ENTER para conservar el valor actual o ingrese el nuevo dato:")
        new_phone_input = input("Nuevo teléfono: ").strip()
        final_phone = validate_phone(new_phone_input) if new_phone_input else current_owner['phone']

        new_addr_input = input("Nueva dirección: ").strip()
        final_address = validate_address(new_addr_input) if new_addr_input else current_owner['address']

        new_mail_input = input("Nuevo correo: ").strip()
        final_email = validate_email(new_mail_input) if new_mail_input else current_owner['email']

        if not confirm_action_yn("¿Desea aplicar estos cambios de contacto?"):
            canceled = {"status": 200, "message": "Modificación cancelada por el usuario.", "data": None}
            print(json.dumps(canceled, indent=2, ensure_ascii=False))
            return

        sql = """
            UPDATE owners
            SET phone = %s, address = %s, email = %s
            WHERE doc_number = %s
        """
        affected_rows = execute_write_operation(sql, (final_phone, final_address, final_email, doc_number))
        updated_owner = execute_single_query("SELECT * FROM owners WHERE doc_number = %s", (doc_number,))

        response = {
            "status": 200,
            "message": "Datos de contacto actualizados exitosamente (PATCH)",
            "affected_rows": affected_rows,
            "data": updated_owner
        }
        print(json.dumps(response, indent=2, ensure_ascii=False, default=str))

    except ValueError as validation_err:
        error_response = {"status": 400, "error": "ValidationFailed", "detail": str(validation_err)}
        print(json.dumps(error_response, indent=2, ensure_ascii=False))
    except Exception as err_db:
        error_response = {"status": 500, "error": "DatabaseError", "detail": str(err_db)}
        print(json.dumps(error_response, indent=2, ensure_ascii=False))
    finally:
        pause()

if __name__ == "__main__":
    run_patch_contact()