from flask import Blueprint, request, jsonify
from db import get_connection
from utils.logger import registrar_log, iniciar_medicion, finalizar_medicion

cursos_bp = Blueprint("cursos_bp", __name__, url_prefix="/api/cursos")


# ============================
# VALIDACIÓN DE CAMPOS
# ============================
def validar_curso(data):
    errores = []
    if not data.get("codigo"):
        errores.append("El código es obligatorio.")
    if not data.get("nombre"):
        errores.append("El nombre es obligatorio.")
    
    creditos = data.get("creditos")
    if creditos is None or not isinstance(creditos, int) or creditos < 1 or creditos > 5:
        errores.append("Los créditos deben estar entre 1 y 5.")
    
    ciclo = data.get("ciclo")
    if ciclo is None or not isinstance(ciclo, int) or ciclo < 1 or ciclo > 10:
        errores.append("El ciclo debe estar entre 1 y 10.")
    
    return errores


# ============================
# GET: LISTAR CURSOS
# ============================
@cursos_bp.route("", methods=["GET"])
def listar_cursos():
    iniciar_medicion()
    registrar_log("cursos", "INFO", "=== INICIO: Listar cursos activos ===")

    conn = get_connection()
    if conn is None:
        registrar_log("cursos", "ERROR", "No se pudo conectar a la BD")
        finalizar_medicion()
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cursos WHERE activo = 1 ORDER BY ciclo, codigo")
        data = cursor.fetchall()

        registrar_log("cursos", "INFO", f"Cursos recuperados exitosamente: {len(data)} registros")
        registrar_log("cursos", "INFO", "=== FIN: Listar cursos activos ===")
        finalizar_medicion()
        return jsonify(data), 200

    except Exception as e:
        registrar_log("cursos", "ERROR", f"Excepción al listar cursos: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error interno al listar cursos"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# GET: OBTENER CURSO POR ID
# ============================
@cursos_bp.route("/<int:curso_id>", methods=["GET"])
def obtener_curso(curso_id):
    iniciar_medicion()
    registrar_log("cursos", "INFO", f"=== INICIO: Obtener curso ID={curso_id} ===")

    conn = get_connection()
    if conn is None:
        registrar_log("cursos", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de BD"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cursos WHERE id = %s AND activo = 1", (curso_id,))
        curso = cursor.fetchone()

        if curso is None:
            registrar_log("cursos", "WARN", f"Curso ID={curso_id} no encontrado o inactivo")
            finalizar_medicion()
            return jsonify({"error": "Curso no encontrado"}), 404

        registrar_log("cursos", "INFO", f"Curso ID={curso_id} recuperado: {curso['codigo']} - {curso['nombre']}")
        registrar_log("cursos", "INFO", f"=== FIN: Obtener curso ID={curso_id} ===")
        finalizar_medicion()
        return jsonify(curso), 200

    except Exception as e:
        registrar_log("cursos", "ERROR", f"Excepción al obtener curso: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error interno"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# POST: CREAR CURSO
# ============================
@cursos_bp.route("", methods=["POST"])
def crear_curso():
    iniciar_medicion()
    registrar_log("cursos", "INFO", "=== INICIO: Crear nuevo curso ===")

    data = request.get_json()
    if not data:
        registrar_log("cursos", "WARN", "Request sin datos JSON o datos inválidos")
        finalizar_medicion()
        return jsonify({"error": "Datos inválidos"}), 400

    errores = validar_curso(data)
    if errores:
        registrar_log("cursos", "WARN", f"Validación fallida al crear curso: {', '.join(errores)}")
        finalizar_medicion()
        return jsonify({"errores": errores}), 400

    conn = get_connection()
    if conn is None:
        registrar_log("cursos", "ERROR", "Error al conectar a BD")
        finalizar_medicion()
        return jsonify({"error": "Error al conectar BD"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cursos(codigo, nombre, creditos, ciclo, activo)
            VALUES (%s, %s, %s, %s, 1)
        """, (
            data["codigo"], data["nombre"], data["creditos"], data["ciclo"]
        ))
        conn.commit()

        nuevo_id = cursor.lastrowid
        registrar_log("cursos", "INFO", f"Curso creado exitosamente - ID={nuevo_id}, Código={data['codigo']}, Nombre={data['nombre']}")
        registrar_log("cursos", "INFO", "=== FIN: Crear nuevo curso ===")
        finalizar_medicion()

        return jsonify({"mensaje": "Curso creado", "id": nuevo_id}), 201

    except Exception as e:
        registrar_log("cursos", "ERROR", f"Excepción al crear curso: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error en BD"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# PUT: ACTUALIZAR CURSO
# ============================
@cursos_bp.route("/<int:curso_id>", methods=["PUT"])
def actualizar_curso(curso_id):
    iniciar_medicion()
    registrar_log("cursos", "INFO", f"=== INICIO: Actualizar curso ID={curso_id} ===")

    data = request.get_json()
    if not data:
        registrar_log("cursos", "WARN", "Request sin datos JSON")
        finalizar_medicion()
        return jsonify({"error": "Datos inválidos"}), 400

    errores = validar_curso(data)
    if errores:
        registrar_log("cursos", "WARN", f"Validación fallida al actualizar: {', '.join(errores)}")
        finalizar_medicion()
        return jsonify({"errores": errores}), 400

    conn = get_connection()
    if conn is None:
        registrar_log("cursos", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error BD"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cursos 
            SET codigo=%s, nombre=%s, creditos=%s, ciclo=%s
            WHERE id=%s
        """, (
            data["codigo"], data["nombre"], data["creditos"], data["ciclo"],
            curso_id
        ))
        conn.commit()

        if cursor.rowcount == 0:
            registrar_log("cursos", "WARN", f"Curso ID={curso_id} no encontrado para actualización")
            finalizar_medicion()
            return jsonify({"error": "Curso no encontrado"}), 404

        registrar_log("cursos", "INFO", f"Curso actualizado exitosamente - ID={curso_id}, Código={data['codigo']}")
        registrar_log("cursos", "INFO", f"=== FIN: Actualizar curso ID={curso_id} ===")
        finalizar_medicion()

        return jsonify({"mensaje": "Curso actualizado"}), 200

    except Exception as e:
        registrar_log("cursos", "ERROR", f"Excepción al actualizar curso: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error en BD"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# DELETE: ELIMINACIÓN LÓGICA
# ============================
@cursos_bp.route("/<int:curso_id>", methods=["DELETE"])
def eliminar_curso(curso_id):
    iniciar_medicion()
    registrar_log("cursos", "INFO", f"=== INICIO: Eliminar curso ID={curso_id} ===")

    conn = get_connection()
    if conn is None:
        registrar_log("cursos", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error BD"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE cursos SET activo = 0 WHERE id = %s", (curso_id,))
        conn.commit()

        if cursor.rowcount == 0:
            registrar_log("cursos", "WARN", f"Curso ID={curso_id} no encontrado para eliminación")
            finalizar_medicion()
            return jsonify({"error": "Curso no encontrado"}), 404

        registrar_log("cursos", "INFO", f"Curso marcado como inactivo exitosamente - ID={curso_id}")
        registrar_log("cursos", "INFO", f"=== FIN: Eliminar curso ID={curso_id} ===")
        finalizar_medicion()

        return jsonify({"mensaje": "Curso eliminado correctamente"}), 200

    except Exception as e:
        registrar_log("cursos", "ERROR", f"Excepción al eliminar curso: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error al eliminar curso"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# VALIDAR SI CURSO EXISTE (SERVICIO NUEVO)
# ============================
@cursos_bp.route("/validar/<int:curso_id>", methods=["GET"])
def validar_curso_existe(curso_id):
    """
    Servicio simple para validar si un curso existe.
    Usado por otros servicios (matrícula, evaluación).
    """
    iniciar_medicion()
    registrar_log("cursos", "INFO", f"=== VALIDAR: Curso ID={curso_id} ===")
    
    conn = get_connection()
    if conn is None:
        registrar_log("cursos", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error en BD"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, codigo, nombre, ciclo, creditos FROM cursos WHERE id=%s AND activo=1", (curso_id,))
        curso = cursor.fetchone()
        
        if curso:
            registrar_log("cursos", "INFO", f"Curso ID={curso_id} existe y está activo")
            finalizar_medicion()
            return jsonify({
                "existe": True,
                "curso": curso
            }), 200
        else:
            registrar_log("cursos", "WARN", f"Curso ID={curso_id} no encontrado")
            finalizar_medicion()
            return jsonify({
                "existe": False,
                "mensaje": "Curso no encontrado"
            }), 404
            
    except Exception as e:
        registrar_log("cursos", "ERROR", f"Error al validar curso: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": str(e)}), 500
        
    finally:
        cursor.close()
        conn.close()