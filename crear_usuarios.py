"""
=========================================================
crear_usuarios.py  —  Script de administración (uso único)
=========================================================
Crea las cuentas de acceso al dashboard. Se corre UNA VEZ
(o cada vez que necesites añadir/cambiar una cuenta).

CÓMO USARLO:
  1. Edita la lista USUARIOS de abajo con tus cuentas reales
     y sus contraseñas.
  2. Asegúrate de tener la variable DATABASE_URL disponible
     (la misma de Supabase). En local puedes exportarla, o
     correr este script donde ya exista.
  3. Ejecuta:  python crear_usuarios.py
  4. Cuando termine, BORRA las contraseñas de este archivo
     (o borra el archivo) para no dejarlas escritas.

ROLES válidos:
  "admin"    -> puede cargar/procesar datos y consultar
  "consulta" -> solo puede ver el reporte

SEGURIDAD:
  Las contraseñas se guardan CIFRADAS (bcrypt) en la base.
  Nunca se guardan en texto plano. Aun así, no dejes este
  archivo con contraseñas reales en el repositorio de GitHub.
"""

import db

# =========================================================
# EDITA AQUÍ TUS CUENTAS
# formato:  ("usuario", "contraseña", "rol")
# =========================================================

USUARIOS = [
    # --- ADMINS (cargan y consultan) ---
    ("admin1", "Liderza2026-1", "admin"),
    ("admin2", "Liderza2026-2", "admin"),

    # --- CONSULTA (solo ven) ---
    ("LID1", "Liderza2026-3", "consulta"),
    ("LID2", "Liderza2026-4", "consulta"),
    ("LID3", "Liderza2026-5", "consulta"),
    ("LID4", "Liderza2026-6", "consulta"),
    ("LID5", "Liderza2026-7", "consulta"),
    ("LID6", "Liderza2026-8", "consulta"),
    ("LID7", "Liderza2026-9", "consulta"),
]


def main():
    db.inicializar_esquema()  # asegura que la tabla usuarios existe
    creados = 0
    for usuario, password, rol in USUARIOS:
        if password == "CAMBIA-ESTA-CLAVE":
            print(f"  [SALTADO] '{usuario}': falta poner su contraseña real.")
            continue
        if rol not in ("admin", "consulta"):
            print(f"  [ERROR] '{usuario}': rol '{rol}' inválido (usa admin o consulta).")
            continue
        db.crear_usuario(usuario, password, rol)
        print(f"  [OK] Usuario '{usuario}' creado/actualizado con rol '{rol}'.")
        creados += 1
    print(f"\nListo. {creados} cuenta(s) procesada(s).")
    print("Recuerda: borra las contraseñas de este archivo ahora.")


if __name__ == "__main__":
    main()