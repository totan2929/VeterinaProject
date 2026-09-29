import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from database.db_connection import (
    execute_write_operation_returning_id,
    execute_single_query
)
from utils.functions import (
    clear_screen,
    pause,
    confirm_action_yn,
    validate_doc_type,
    validate_doc_number,
    validate_person_name,
    validate_birth_date,
    validate_address,
    validate_phone,
    validate_email
)

def prompt_validated_field(field_prompt, validator_func, extra_param=None):
    while True:
        try:
            raw_input = input(f"{field_prompt}: ")
            if extra_param:
                return validator_func(raw_input, extra_param)
            return validator_func(raw_input)
        except ValueError as err:
            print(f"\n⚠️  {err}\nInténtelo nuevamente.\n")

def collect_owner_data():
    print("==============================================")
    print("        REGISTRO DE NUEVO PROPIETARIO         ")
    print("==============================================\n")
    
    doc_type = prompt_validated_field("Tipo Documento (CC, CE, TI, PASAPORTE)", validate_doc_type)
    doc_number = prompt_validated_field("Número de Documento", validate_doc_number)
    first_name = prompt_validated_field("Nombres", validate_person_name, "Nombres")
    last_name = prompt_validated_field("Apellidos", validate_person_name, "Apellidos")
    birth_date = prompt_validated_field("Fecha Nacimiento (AAAA-MM-DD)", validate_birth_date)
    address = prompt_validated_field("Dirección de residencia", validate_address)
    phone = prompt_validated_field("Teléfono celular (10 dígitos)", validate_phone)
    email = prompt_validated_field("Correo electrónico", validate_email)

    return (doc_type, doc_number, first_name, last_name, birth_date, address, phone, email)

def insert_owner(owner_data):
    sql = """
        INSERT INTO owners (
            doc_type, doc_number, first_name, last_name,
            birth_date, address, phone, email
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    _, new_id = execute_write_operation_returning_id(sql, owner_data)
    return new_id

def get_owner_by_id(owner_id):
    sql = """
        SELECT owner_id, doc_type, doc_number, first_name, last_name,
               birth_date, address, phone, email, status, created_at
        FROM owners WHERE owner_id = %s
    """
    return execute_single_query(sql, (owner_id,))

def run_post_owner():
    clear_screen()
    try:
        owner_data = collect_owner_data()
        
        print("\n--- RESUMEN DEL REGISTRO ---")
        print(f"Documento: {owner_data[0]} {owner_data[1]}")
        print(f"Propietario: {owner_data[2]} {owner_data[3]}")
        print(f"Contacto: {owner_data[6]} | {owner_data[7]}")
        print(f"Dirección: {owner_data[5]}\n")

        if not confirm_action_yn("¿Desea crear y registrar este propietario en la base de datos?"):
            canceled_response = {
                "status": 200,
                "message": "Operación cancelada por el usuario. No se registraron datos.",
                "data": None
            }
            print("\n" + json.dumps(canceled_response, indent=2, ensure_ascii=False))
            return

        new_id = insert_owner(owner_data)
        created_record = get_owner_by_id(new_id)

        response = {
            "status": 201,
            "message": "Propietario registrado exitosamente en MySQL",
            "data": created_record
        }
        print("\n" + json.dumps(response, indent=2, ensure_ascii=False, default=str))

    except (PermissionError, ConnectionError, NameError, RuntimeError) as err_db:
        error_response = {"status": 500, "error": "DatabaseError", "detail": str(err_db)}
        print(json.dumps(error_response, indent=2, ensure_ascii=False))
    except Exception as unexpected_err:
        error_response = {"status": 500, "error": "UnexpectedError", "detail": str(unexpected_err)}
        print(json.dumps(error_response, indent=2, ensure_ascii=False))
    finally:
        pause()

if __name__ == "__main__":
    run_post_owner()

