import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from database.db_connection import ejecutar_consulta_unica, ejecutar_operacion_escritura
from utils.functions import clear_screen, pause, confirm_action_yn, validate_doc_number, validate_status

def run_patch_status():
    clear_screen()
    try:
        print("=== GESTIÓN DE ESTADO DE PROPIETARIO (BORRADO LÓGICO) ===\n")
        doc_input = input("Digite el documento del propietario: ")
        doc_number = validate_doc_number(doc_input)

        owner_record = ejecutar_consulta_unica("SELECT owner_id, first_name, last_name, status FROM owners WHERE doc_number = %s", (doc_number,))
        if not owner_record:
            response = {"status": 404, "message": f"No se encontró propietario con documento {doc_number}."}
            print(json.dumps(response, indent=2, ensure_ascii=False))
            return

        print(f"\nPropietario: {owner_record['first_name']} {owner_record['last_name']}")
        print(f"Estado actual: {owner_record['status']}\n")

        new_status = validate_status(input("Digite el nuevo estado (Active / Inactive): "))

        if new_status == owner_record["status"]:
            print(json.dumps({"status": 200, "message": "El propietario ya se encuentra en ese estado.", "data": owner_record}, indent=2))
            return

        if not confirm_action_yn(f"¿Confirma cambiar el estado a '{new_status}'?"):
            canceled = {"status": 200, "message": "Operación cancelada.", "data": None}
            print(json.dumps(canceled, indent=2, ensure_ascii=False))
            return

        sql = "UPDATE owners SET status = %s WHERE doc_number = %s"
        affected_rows = ejecutar_operacion_escritura(sql, (new_status, doc_number))
        updated_owner = ejecutar_consulta_unica("SELECT owner_id, doc_number, first_name, last_name, status FROM owners WHERE doc_number = %s", (doc_number,))

        response = {
            "status": 200,
            "message": f"Estado del propietario actualizado a '{new_status}' exitosamente",
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
    run_patch_status()