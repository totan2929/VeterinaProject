# Mis_funciones.py
import os
import re
from datetime import datetime

# ---------------------------------------------------------------------------
# UTILIDADES DE TERMINAL Y FLUJO
# ---------------------------------------------------------------------------

def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")

def pausa():
    print("\nPresione cualquier tecla para continuar...")
    if os.name == "nt":
        os.system("pause > nul")
    else:
        os.system("read -n 1 -s -r -p ''")
        print()
    limpiar_pantalla()

def confirmar_accion_sn(mensaje):
    """
    Pregunta al usuario una confirmacion S/N (Requerimiento VET-0019).
    Retorna True si responde 'S', False si responde 'N'.
    """
    while True:
        respuesta = input(f"{mensaje} (S/N): ").strip().upper()
        if respuesta == "S":
            return True
        elif respuesta == "N":
            return False
        print("Opción inválida. Digite únicamente 'S' para Sí o 'N' para No.")

# ---------------------------------------------------------------------------
# VALIDADORES DE ENTRADA (Muestran mensaje de estructura incompleta)
# ---------------------------------------------------------------------------

def validar_tipo_documento(tipo_doc):
    tipos_validos = ("CC", "CE", "TI", "PASAPORTE")
    candidato = str(tipo_doc).strip().upper()
    if candidato not in tipos_validos:
        raise ValueError(
            f"El dato ingresado no tiene la estructura completa o requerida. "
            f"Debe seleccionar una de las siguientes opciones: {', '.join(tipos_validos)}."
        )
    return candidato

def validar_documento(documento):
    patron = r"^[A-Za-z0-9]{5,20}$"
    candidato = str(documento).strip()
    if not re.fullmatch(patron, candidato):
        raise ValueError(
            "El dato ingresado no tiene la estructura completa o requerida. "
            "El documento debe ser alfanumérico, sin espacios, con una longitud de 5 a 20 caracteres."
        )
    return candidato

def validar_nombre_persona(nombre, campo="Nombre"):
    patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,60}$"
    candidato = str(nombre).strip()
    if not re.fullmatch(patron, candidato):
        raise ValueError(
            f"El dato ingresado en '{campo}' no tiene la estructura completa o requerida. "
            f"Solo se admiten letras y espacios (entre 2 y 60 caracteres, sin números)."
        )
    return candidato

def validar_fecha_nacimiento(fecha_str):
    patron = r"^\d{4}-\d{2}-\d{2}$"
    candidato = str(fecha_str).strip()
    if not re.fullmatch(patron, candidato):
        raise ValueError(
            "El dato ingresado no tiene la estructura completa o requerida. "
            "La fecha debe cumplir el formato estricto AAAA-MM-DD (ejemplo: 1994-06-15)."
        )
    try:
        fecha_dt = datetime.strptime(candidato, "%Y-%m-%d").date()
        if fecha_dt > datetime.now().date():
            raise ValueError(
                "El dato ingresado no tiene la estructura completa o requerida. "
                "La fecha de nacimiento no puede ser una fecha futura."
            )
        return candidato
    except ValueError as error:
        raise ValueError(
            f"El dato ingresado no tiene la estructura completa o requerida. "
            f"Día o mes no válido en el calendario real: {error}"
        )

def validar_direccion(direccion):
    patron = r"^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ #\.\-,/º°ª']{5,100}$"
    candidato = str(direccion).strip()
    if not re.fullmatch(patron, candidato):
        raise ValueError(
            "El dato ingresado en dirección no tiene la estructura completa o requerida. "
            "Debe contener una nomenclatura vial válida de entre 5 y 100 caracteres."
        )
    return candidato

def validar_telefono(telefono):
    patron = r"^\d{10}$"
    candidato = str(telefono).strip()
    if not re.fullmatch(patron, candidato):
        raise ValueError(
            "El dato ingresado no tiene la estructura completa o requerida. "
            "El teléfono debe contener exactamente 10 dígitos numéricos."
        )
    return candidato

def validar_correo(correo):
    patron = r"^(?=.{10,70}$)[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,6}$"
    candidato = str(correo).strip().lower()
    if not re.fullmatch(patron, candidato):
        raise ValueError(
            "El dato ingresado no tiene la estructura completa o requerida. "
            "Debe ser un correo electrónico válido con formato usuario@dominio.extension (entre 10 y 70 caracteres)."
        )
    return candidato

def validar_estado(estado):
    estados_validos = ("Activo", "Inactivo")
    candidato = str(estado).strip().capitalize()
    if candidato not in estados_validos:
        raise ValueError(
            f"El dato ingresado no tiene la estructura completa o requerida. "
            f"El estado debe ser: {', '.join(estados_validos)}."
        )
    return candidato