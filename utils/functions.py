# ============================================================================
# FILE: utils/functions.py
# LAYER: 3 - Business Logic and Domain Validators
# PURPOSE: Sanitize, format, and validate user input integrity prior to
#          interacting with the database layer.
# ============================================================================
import os
import re
from datetime import datetime

# ---------------------------------------------------------------------------
# TERMINAL AND FLOW UTILITIES
# ---------------------------------------------------------------------------

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    print("\nPresione cualquier tecla para continuar...")
    if os.name == "nt":
        os.system("pause > nul")
    else:
        os.system("read -n 1 -s -r -p ''")
        print()
    clear_screen()

def confirm_action_yn(message):
    """Prompts the user for a Y/N (S/N) confirmation."""
    while True:
        response = input(f"{message} (S/N): ").strip().upper()
        if response == "S":
            return True
        elif response == "N":
            return False
        print("Opción inválida. Digite únicamente 'S' para Sí o 'N' para No.")

# ---------------------------------------------------------------------------
# DOMAIN VALIDATORS
# ---------------------------------------------------------------------------

def validate_doc_type(doc_type):
    valid_types = ("CC", "CE", "TI", "PASAPORTE", "PASSPORT")
    candidate = str(doc_type).strip().upper()
    if candidate not in valid_types:
        raise ValueError(
            f"El dato ingresado no tiene la estructura requerida. "
            f"Opciones válidas: {', '.join(valid_types)}."
        )
    return candidate

def validate_doc_number(doc_number):
    pattern = r"^[A-Za-z0-9]{5,20}$"
    candidate = str(doc_number).strip()
    if not re.fullmatch(pattern, candidate):
        raise ValueError(
            "El dato ingresado no tiene la estructura requerida. "
            "El documento debe ser alfanumérico, sin espacios, de 5 a 20 caracteres."
        )
    return candidate

def validate_person_name(name, field_name="Name"):
    pattern = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,60}$"
    candidate = str(name).strip()
    if not re.fullmatch(pattern, candidate):
        raise ValueError(
            f"El dato ingresado en '{field_name}' no tiene la estructura requerida. "
            f"Solo se admiten letras y espacios (2 a 60 caracteres)."
        )
    return candidate

def validate_birth_date(date_str):
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    candidate = str(date_str).strip()
    if not re.fullmatch(pattern, candidate):
        raise ValueError(
            "El dato ingresado no tiene la estructura requerida. "
            "La fecha debe cumplir el formato estricto AAAA-MM-DD (ej: 1994-06-15)."
        )
    try:
        parsed_date = datetime.strptime(candidate, "%Y-%m-%d").date()
        if parsed_date > datetime.now().date():
            raise ValueError(
                "El dato ingresado no tiene la estructura requerida. "
                "La fecha de nacimiento no puede ser futura."
            )
        return candidate
    except ValueError as err:
        raise ValueError(f"Día o mes no válido en el calendario real: {err}")

def validate_address(address):
    pattern = r"^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ #\.\-,/º°ª']{5,100}$"
    candidate = str(address).strip()
    if not re.fullmatch(pattern, candidate):
        raise ValueError(
            "El dato ingresado en dirección no tiene la estructura requerida. "
            "Debe contener entre 5 y 100 caracteres de nomenclatura vial."
        )
    return candidate

def validate_phone(phone):
    pattern = r"^\d{10}$"
    candidate = str(phone).strip()
    if not re.fullmatch(pattern, candidate):
        raise ValueError(
            "El dato ingresado no tiene la estructura requerida. "
            "El teléfono debe contener exactamente 10 dígitos numéricos."
        )
    return candidate

def validate_email(email):
    pattern = r"^(?=.{10,70}$)[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,6}$"
    candidate = str(email).strip().lower()
    if not re.fullmatch(pattern, candidate):
        raise ValueError(
            "El dato ingresado no tiene la estructura requerida. "
            "Debe ser un correo electrónico válido (10 a 70 caracteres)."
        )
    return candidate

def validate_status(status):
    valid_statuses = ("Active", "Inactive")
    candidate = str(status).strip().capitalize()
    if candidate not in valid_statuses:
        raise ValueError(
            f"El dato ingresado no tiene la estructura requerida. "
            f"Debe ser: {', '.join(valid_statuses)}."
        )
    return candidate