# main.py
from utils.functions import clear_screen, confirm_action_yn

# Endpoints importados con nombres normalizados
from routes.endpoint_post_create_owner import run_post_owner
from routes.endpoint_get_list_owners import run_get_owners
from routes.endpoint_get_owner_by_doc import run_get_owner_by_doc
from routes.endpoint_put_update_owner import run_put_owner
from routes.endpoint_patch_update_contact import run_patch_contact
from routes.endpoint_delete_owner import run_delete_owner
from routes.endpoint_get_owner_pets import run_get_owner_pets
from routes.endpoint_get_search_owners import run_search_owners
from routes.endpoint_patch_update_status import run_patch_status

def main_menu():
    keep_running = True
    while keep_running:
        clear_screen()
        print("==========================================================")
        print("  SISTEMA CLÍNICA VETERINARIA — MÓDULO OWNERS (9 ENDPOINTS)")
        print("==========================================================")
        print("--- OPERACIONES CRUD OBLIGATORIAS ---")
        print("1. [POST]   Registrar nuevo propietario (confirmación S/N)")
        print("2. [GET]    Listar todos los propietarios (paginado)")
        print("3. [GET]    Consultar propietario por documento")
        print("4. [PUT]    Actualización total de propietario")
        print("5. [PATCH]  Actualizar datos de contacto (teléfono/dirección)")
        print("6. [DELETE] Eliminar propietario")
        print("\n--- OPERACIONES AVANZADAS (BONIFICACIÓN) ---")
        print("7. [GET]    Listar mascotas de un propietario (Relación 1:N)")
        print("8. [GET]    Buscar propietarios por nombre/apellido (LIKE)")
        print("9. [PATCH]  Cambiar estado (Borrado Lógico / Soft Delete)")
        print("0. [SALIR]  Cerrar la aplicación")
        print("==========================================================")
        
        choice = input("Seleccione una opción (0-9): ").strip()

        if choice == "1":
            run_post_owner()
        elif choice == "2":
            run_get_owners()
        elif choice == "3":
            run_get_owner_by_doc()
        elif choice == "4":
            run_put_owner()
        elif choice == "5":
            run_patch_contact()
        elif choice == "6":
            run_delete_owner()
        elif choice == "7":
            run_get_owner_pets()
        elif choice == "8":
            run_search_owners()
        elif choice == "9":
            run_patch_status()
        elif choice == "0":
            if confirm_action_yn("¿Está seguro de que desea salir del sistema?"):
                clear_screen()
                print("Sesión finalizada con éxito.")
                break
            else:
                continue
        else:
            input("Opción no válida. Presione ENTER para continuar...")
            continue

        keep_running = confirm_action_yn("¿Desea realizar alguna otra acción en el sistema?")

    clear_screen()
    print("¡Gracias por utilizar el sistema de la clínica veterinaria!")

if __name__ == "__main__":
    main_menu()