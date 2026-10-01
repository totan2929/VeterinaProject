import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from database.db_connection import ejecutar_consulta_multiple
from utils.functions import clear_screen, pause

def search_owners_by_keyword(keyword):
    sql = """
        SELECT owner_id, doc_type, doc_number, first_name, last_name, phone, email, status
        FROM owners
        WHERE first_name LIKE %s OR last_name LIKE %s
        ORDER BY first_name ASC
        LIMIT 20
    """
    param = f"%{keyword}%"
    return ejecutar_consulta_multiple(sql, (param, param))

def run_search_owners():
    clear_screen()
    try:
        print("=== BÚSQUEDA DE PROPIETARIOS POR NOMBRE/APELLIDO ===\n")
        keyword = input("Digite nombre o apellido a buscar (mínimo 2 letras): ").strip()
        
        if len(keyword) < 2:
            raise ValueError("El criterio de búsqueda debe tener al menos 2 caracteres.")

        matches = search_owners_by_keyword(keyword)

        response = {
            "status": 200,
            "search_keyword": keyword,
            "matches_found": len(matches),
            "data": matches
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
    run_search_owners()