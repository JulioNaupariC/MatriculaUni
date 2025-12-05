from flask import Blueprint, request, jsonify
from db import get_connection
from utils.logger import registrar_log, iniciar_medicion, finalizar_medicion

alumnos_bp = Blueprint("alumnos_bp", __name__, url_prefix="/api/alumnos")
print("⚡ CARGANDO ARCHIVO DE ALUMNOS DESDE ESTE BACKEND ⚡")


# ============================
# VALIDACIÓN DE CAMPOS
# ============================
def validar_alumno(data):
    errores = []

    # ============================
    # VALIDACIÓN DE NOMBRE (solo letras)
    # ============================
    if not data.get("nombre"):
        errores.append("El nombre es obligatorio.")
    else:
        # Permitimos espacios, pero no números ni símbolos
        if not data["nombre"].replace(" ", "").isalpha():
            errores.append("El nombre solo puede contener letras (sin números).")

    # ============================
    # VALIDACIÓN DE APELLIDO (solo letras)
    # ============================
    if not data.get("apellido"):
        errores.append("El apellido es obligatorio.")
    else:
        if not data["apellido"].replace(" ", "").isalpha():
            errores.append("El apellido solo puede contener letras (sin números).")

    # ============================
    # VALIDACIÓN DE DNI
    # ============================
    if not data.get("dni"):
        errores.append("El DNI es obligatorio.")
    else:
        dni_str = str(data["dni"])
        if not dni_str.isdigit():
            errores.append("El DNI solo puede contener números.")
        elif len(dni_str) != 8:
            errores.append("El DNI debe tener exactamente 8 dígitos.")

    # ============================
    # VALIDACIÓN DE EDAD (mínimo 16 años)
    # ============================
    edad = data.get("edad")
    if edad is None or edad == "":
        errores.append("La edad es obligatoria.")
    else:
        try:
            edad_int = int(edad)
            if edad_int < 16:
                errores.append("La edad mínima para matricularse es 16 años.")
        except ValueError:
            errores.append("La edad debe ser un número válido.")

    # ============================
    # VALIDACIÓN DE TELÉFONO
    # ============================
    telefono = data.get("telefono")
    if telefono:
        telefono_str = str(telefono)

        if not telefono_str.isdigit():
            errores.append("El teléfono solo puede contener números.")

        if len(telefono_str) != 9:
            errores.append("El teléfono debe tener exactamente 9 dígitos.")

        if not telefono_str.startswith("9"):
            errores.append("El teléfono debe iniciar con 9.")

    # ============================
    # VALIDACIÓN DE CICLO ACTUAL (1-10)
    # ============================
    ciclo_actual = data.get("ciclo_actual")
    if ciclo_actual is not None and ciclo_actual != "":
        try:
            ciclo_int = int(ciclo_actual)
            if ciclo_int < 1 or ciclo_int > 10:
                errores.append("El ciclo actual debe estar entre 1 y 10.")
        except ValueError:
            errores.append("El ciclo actual debe ser un número válido.")

    return errores


# ============================
# GET: LISTAR ALUMNOS
# ============================
@alumnos_bp.route("", methods=["GET"])
def listar_alumnos():
    iniciar_medicion()
    registrar_log("alumnos", "INFO", "=== INICIO: Listar alumnos activos ===")

    conn = get_connection()
    if conn is None:
        registrar_log("alumnos", "ERROR", "No se pudo conectar a la BD")
        finalizar_medicion()
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alumnos WHERE activo = 1")
        data = cursor.fetchall()

        registrar_log("alumnos", "INFO", f"Alumnos recuperados exitosamente: {len(data)} registros")
        registrar_log("alumnos", "INFO", "=== FIN: Listar alumnos activos ===")
        finalizar_medicion()
        return jsonify(data), 200

    except Exception as e:
        registrar_log("alumnos", "ERROR", f"Excepción al listar alumnos: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error interno al listar alumnos", "detalle": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# GET: OBTENER ALUMNO POR ID
# ============================
@alumnos_bp.route("/<int:alumno_id>", methods=["GET"])
def obtener_alumno(alumno_id):
    iniciar_medicion()
    registrar_log("alumnos", "INFO", f"=== INICIO: Obtener alumno ID={alumno_id} ===")

    conn = get_connection()
    if conn is None:
        registrar_log("alumnos", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error en BD"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alumnos WHERE id = %s AND activo = 1", (alumno_id,))
        alumno = cursor.fetchone()

        if alumno is None:
            registrar_log("alumnos", "WARN", f"Alumno ID={alumno_id} no encontrado o inactivo")
            finalizar_medicion()
            return jsonify({"error": "Alumno no encontrado"}), 404

        registrar_log("alumnos", "INFO", f"Alumno ID={alumno_id} recuperado: {alumno['nombre']} {alumno['apellido']}")
        registrar_log("alumnos", "INFO", f"=== FIN: Obtener alumno ID={alumno_id} ===")
        finalizar_medicion()
        return jsonify(alumno), 200

    except Exception as e:
        registrar_log("alumnos", "ERROR", f"Excepción al obtener alumno: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error interno", "detalle": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# POST: CREAR ALUMNO
# ============================
@alumnos_bp.route("", methods=["POST"])
def crear_alumno():
    iniciar_medicion()
    registrar_log("alumnos", "INFO", "=== INICIO: Crear nuevo alumno ===")

    data = request.get_json()
    if not data:
        registrar_log("alumnos", "WARN", "Request sin datos JSON o datos inválidos")
        finalizar_medicion()
        return jsonify({"error": "Datos inválidos"}), 400

    errores = validar_alumno(data)
    if errores:
        registrar_log("alumnos", "WARN", f"Validación fallida al crear alumno: {', '.join(errores)}")
        finalizar_medicion()
        return jsonify({"errores": errores}), 400

    conn = get_connection()
    if conn is None:
        registrar_log("alumnos", "ERROR", "Error al conectar a BD")
        finalizar_medicion()
        return jsonify({"error": "Error en BD"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alumnos(nombre, apellido, edad, dni, correo, telefono, ciclo_actual, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
        """, (
            data["nombre"], data["apellido"], data.get("edad"), data["dni"],
            data.get("correo"), data.get("telefono"), data.get("ciclo_actual", 1)
        ))
        conn.commit()

        nuevo_id = cursor.lastrowid
        registrar_log("alumnos", "INFO", f"Alumno creado exitosamente - ID={nuevo_id}, DNI={data['dni']}, Nombre={data['nombre']} {data['apellido']}")
        registrar_log("alumnos", "INFO", "=== FIN: Crear nuevo alumno ===")
        finalizar_medicion()

        return jsonify({"mensaje": "Alumno creado", "id": nuevo_id}), 201

    except Exception as e:
        registrar_log("alumnos", "ERROR", f"Excepción al crear alumno: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error en BD", "detalle": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# PUT: ACTUALIZAR ALUMNO
# ============================
@alumnos_bp.route("/<int:alumno_id>", methods=["PUT"])
def actualizar_alumno(alumno_id):
    iniciar_medicion()
    registrar_log("alumnos", "INFO", f"=== INICIO: Actualizar alumno ID={alumno_id} ===")

    data = request.get_json()
    if not data:
        registrar_log("alumnos", "WARN", "Request sin datos JSON")
        finalizar_medicion()
        return jsonify({"error": "Datos inválidos"}), 400

    errores = validar_alumno(data)
    if errores:
        registrar_log("alumnos", "WARN", f"Validación fallida al actualizar alumno: {', '.join(errores)}")
        finalizar_medicion()
        return jsonify({"errores": errores}), 400

    conn = get_connection()
    if conn is None:
        registrar_log("alumnos", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error en BD"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alumnos 
            SET nombre=%s, apellido=%s, edad=%s, dni=%s, correo=%s, telefono=%s, ciclo_actual=%s
            WHERE id=%s
        """, (
            data["nombre"], data["apellido"], data.get("edad"), data["dni"],
            data.get("correo"), data.get("telefono"), data.get("ciclo_actual", 1),
            alumno_id
        ))
        conn.commit()

        if cursor.rowcount == 0:
            registrar_log("alumnos", "WARN", f"Alumno ID={alumno_id} no encontrado para actualización")
            finalizar_medicion()
            return jsonify({"error": "Alumno no encontrado"}), 404

        registrar_log("alumnos", "INFO", f"Alumno actualizado exitosamente - ID={alumno_id}, Nombre={data['nombre']} {data['apellido']}")
        registrar_log("alumnos", "INFO", f"=== FIN: Actualizar alumno ID={alumno_id} ===")
        finalizar_medicion()

        return jsonify({"mensaje": "Alumno actualizado"}), 200

    except Exception as e:
        registrar_log("alumnos", "ERROR", f"Excepción al actualizar alumno: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error en BD", "detalle": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# DELETE: ELIMINACIÓN LÓGICA
# ============================
@alumnos_bp.route("/<int:alumno_id>", methods=["DELETE"])
def eliminar_alumno(alumno_id):
    iniciar_medicion()
    registrar_log("alumnos", "INFO", f"=== INICIO: Eliminar alumno ID={alumno_id} ===")

    conn = get_connection()
    if conn is None:
        registrar_log("alumnos", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error en BD"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE alumnos SET activo = 0 WHERE id = %s", (alumno_id,))
        conn.commit()

        if cursor.rowcount == 0:
            registrar_log("alumnos", "WARN", f"Alumno ID={alumno_id} no encontrado para eliminación")
            finalizar_medicion()
            return jsonify({"error": "Alumno no encontrado"}), 404

        registrar_log("alumnos", "INFO", f"Alumno marcado como inactivo exitosamente - ID={alumno_id}")
        registrar_log("alumnos", "INFO", f"=== FIN: Eliminar alumno ID={alumno_id} ===")
        finalizar_medicion()

        return jsonify({"mensaje": "Alumno eliminado correctamente"}), 200

    except Exception as e:
        registrar_log("alumnos", "ERROR", f"Excepción al eliminar alumno: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error al eliminar alumno", "detalle": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# VALIDAR SI ALUMNO EXISTE (SERVICIO NUEVO)
# ============================
@alumnos_bp.route("/validar/<int:alumno_id>", methods=["GET"])
def validar_alumno_existe(alumno_id):
    """
    Servicio simple para validar si un alumno existe.
    Usado por otros servicios (matrícula, evaluación).
    """
    iniciar_medicion()
    registrar_log("alumnos", "INFO", f"=== VALIDAR: Alumno ID={alumno_id} ===")
    
    conn = get_connection()
    if conn is None:
        registrar_log("alumnos", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error en BD"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, apellido, ciclo_actual FROM alumnos WHERE id=%s AND activo=1", (alumno_id,))
        alumno = cursor.fetchone()
        
        if alumno:
            registrar_log("alumnos", "INFO", f"Alumno ID={alumno_id} existe y está activo")
            finalizar_medicion()
            return jsonify({
                "existe": True,
                "alumno": alumno
            }), 200
        else:
            registrar_log("alumnos", "WARN", f"Alumno ID={alumno_id} no encontrado")
            finalizar_medicion()
            return jsonify({
                "existe": False,
                "mensaje": "Alumno no encontrado"
            }), 404
            
    except Exception as e:
        registrar_log("alumnos", "ERROR", f"Error al validar alumno: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": str(e)}), 500
        
    finally:
        cursor.close()
        conn.close()