import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from database.db_connection import execute_single_query, execute_write_operation
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
    validate_email,
    validate_status
)

def prompt_optional_field(prompt_label, current_value, validator_func, extra_arg=None):
    """
    Solicita un dato. Si el usuario presiona ENTER sin escribir nada,
    mantiene el valor actual. Si ingresa texto, lo valida en bucle.
    """
    while True:
        raw_input = input(f"{prompt_label} [{current_value}]: ").strip()
        if not raw_input:
            return current_value
        try:
            if extra_arg:
                return validator_func(raw_input, extra_arg)
            return validator_func(raw_input)
        except ValueError as err:
            print(f"\n⚠️  {err}\nInténtelo nuevamente o presione [ENTER] para mantener el valor actual.\n")

def run_patch_contact():
    clear_screen()
    try:
        print("==========================================================")
        print("    ACTUALIZACIÓN PARCIAL DE PROPIETARIO (PATCH)")
        print("==========================================================\n")
        
        doc_input = input("Digite el número de documento del propietario a modificar: ").strip()
        doc_number = validate_doc_number(doc_input)

        current_owner = execute_single_query(
            "SELECT * FROM owners WHERE doc_number = %s", 
            (doc_number,)
        )
        if not current_owner:
            response = {
                "status": 404, 
                "message": f"Propietario con documento {doc_number} no existe en el sistema.",
                "data": None
            }
            print(json.dumps(response, indent=2, ensure_ascii=False))
            return

        print("\n--- DATOS ACTUALES REGISTRADOS ---")
        print(f"Tipo Doc:      {current_owner['doc_type']}")
        print(f"Documento:     {current_owner['doc_number']}")
        print(f"Nombres:       {current_owner['first_name']}")
        print(f"Apellidos:     {current_owner['last_name']}")
        print(f"F. Nacimiento: {current_owner['birth_date']}")
        print(f"Teléfono:      {current_owner['phone']}")
        print(f"Dirección:     {current_owner['address']}")
        print(f"Correo:        {current_owner['email']}")
        print(f"Estado:        {current_owner['status']}")
        print("\nInstrucción: Ingrese el nuevo valor o presione [ENTER] para conservar el actual.\n")

        # Captura y validación de cada atributo
        final_doc_type = prompt_optional_field(
            "Tipo Documento", current_owner['doc_type'], validate_doc_type
        )
        final_first_name = prompt_optional_field(
            "Nombres", current_owner['first_name'], validate_person_name, "Nombres"
        )
        final_last_name = prompt_optional_field(
            "Apellidos", current_owner['last_name'], validate_person_name, "Apellidos"
        )
        final_birth_date = prompt_optional_field(
            "Fecha Nacimiento (AAAA-MM-DD)", str(current_owner['birth_date']), validate_birth_date
        )
        final_phone = prompt_optional_field(
            "Teléfono (10 dígitos)", current_owner['phone'], validate_phone
        )
        final_address = prompt_optional_field(
            "Dirección de residencia", current_owner['address'], validate_address
        )
        final_email = prompt_optional_field(
            "Correo electrónico", current_owner['email'], validate_email
        )
        final_status = prompt_optional_field(
            "Estado (Active / Inactive)", current_owner['status'], validate_status
        )

        print("\n--- RESUMEN DE CAMBIOS ---")
        print(f"Tipo Doc:      {final_doc_type}")
        print(f"Nombres:       {final_first_name}")
        print(f"Apellidos:     {final_last_name}")
        print(f"F. Nacimiento: {final_birth_date}")
        print(f"Teléfono:      {final_phone}")
        print(f"Dirección:     {final_address}")
        print(f"Correo:        {final_email}")
        print(f"Estado:        {final_status}\n")

        if not confirm_action_yn("¿Desea aplicar estos cambios parciales en la base de datos?"):
            canceled = {
                "status": 200, 
                "message": "Actualización cancelada por el usuario. No se modificó ningún dato.", 
                "data": None
            }
            print(json.dumps(canceled, indent=2, ensure_ascii=False))
            return

        sql = """
            UPDATE owners
            SET doc_type = %s,
                first_name = %s,
                last_name = %s,
                birth_date = %s,
                phone = %s,
                address = %s,
                email = %s,
                status = %s
            WHERE doc_number = %s
        """
        
        affected_rows = execute_write_operation(
            sql, 
            (
                final_doc_type,
                final_first_name,
                final_last_name,
                final_birth_date,
                final_phone,
                final_address,
                final_email,
                final_status,
                doc_number
            )
        )
        
        updated_owner = execute_single_query(
            "SELECT * FROM owners WHERE doc_number = %s", 
            (doc_number,)
        )

        response = {
            "status": 200,
            "message": "Propietario actualizado parcialmente con éxito (PATCH)",
            "affected_rows": affected_rows,
            "data": updated_owner
        }
        print(json.dumps(response, indent=2, ensure_ascii=False, default=str))

    except ValueError as validation_err:
        error_response = {
            "status": 400, 
            "error": "ValidationFailed", 
            "detail": str(validation_err)
        }
        print(json.dumps(error_response, indent=2, ensure_ascii=False))
    except Exception as err_db:
        error_response = {
            "status": 500, 
            "error": "DatabaseError", 
            "detail": str(err_db)
        }
        print(json.dumps(error_response, indent=2, ensure_ascii=False))
    finally:
        pause()

if __name__ == "__main__":
    run_patch_contact()