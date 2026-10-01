import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from database.db_connection import ejecutar_consulta_unica, ejecutar_consulta_multiple
from utils.functions import clear_screen, pause, validate_doc_number

def fetch_owner(doc_number):
    sql = "SELECT owner_id, doc_type, doc_number, first_name, last_name, phone, email, status FROM owners WHERE doc_number = %s"
    return ejecutar_consulta_unica(sql, (doc_number,))

def fetch_owner_pets(owner_id):
    sql = """
        SELECT pet_id, name, species, breed, gender,
               estimated_birth_date, weight_kg, has_chip, is_alive
        FROM pets
        WHERE owner_id = %s
        ORDER BY pet_id ASC
    """
    return ejecutar_consulta_multiple(sql, (owner_id,))

def run_get_owner_pets():
    clear_screen()
    try:
        print("=== CONSULTA DE MASCOTAS POR PROPIETARIO ===\n")
        doc_input = input("Digite el documento del propietario: ")
        doc_number = validate_doc_number(doc_input)

        owner_record = fetch_owner(doc_number)
        if not owner_record:
            response = {
                "status": 404,
                "message": f"No existe propietario registrado con documento {doc_number}.",
                "data": None
            }
            print(json.dumps(response, indent=2, ensure_ascii=False))
            return

        pets_list = fetch_owner_pets(owner_record["owner_id"])
        
        result_payload = {
            "owner": owner_record,
            "total_pets": len(pets_list),
            "pets": pets_list
        }

        response = {
            "status": 200,
            "message": f"Se encontraron {len(pets_list)} mascota(s) asociadas",
            "data": result_payload
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
    run_get_owner_pets()