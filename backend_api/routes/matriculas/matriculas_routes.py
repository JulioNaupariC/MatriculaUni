from flask import Blueprint, request, jsonify
from db import get_connection
from utils.logger import registrar_log, iniciar_medicion, finalizar_medicion

matriculas_bp = Blueprint("matriculas_bp", __name__, url_prefix="/api/matriculas")


# ============================
# GET: LISTAR TODAS LAS MATRÍCULAS
# ============================
@matriculas_bp.route("", methods=["GET"])
def listar_matriculas():
    iniciar_medicion()
    registrar_log("matriculas", "INFO", "=== INICIO: Listar todas las matrículas ===")

    conn = get_connection()
    if conn is None:
        registrar_log("matriculas", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.id, m.id_alumno, m.id_curso, m.ciclo, m.fecha_matricula, m.estado,
                   CONCAT(a.nombre, ' ', a.apellido) as alumno,
                   c.nombre as curso,
                   c.codigo as codigo_curso
            FROM matriculas m
            INNER JOIN alumnos a ON m.id_alumno = a.id
            INNER JOIN cursos c ON m.id_curso = c.id
            ORDER BY m.fecha_matricula DESC
        """)
        data = cursor.fetchall()

        registrar_log("matriculas", "INFO", f"Matrículas recuperadas: {len(data)} registros")
        registrar_log("matriculas", "INFO", "=== FIN: Listar todas las matrículas ===")
        finalizar_medicion()
        return jsonify(data), 200

    except Exception as e:
        registrar_log("matriculas", "ERROR", f"Excepción al listar matrículas: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error interno al listar matrículas"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# GET: OBTENER MATRÍCULA POR ID
# ============================
@matriculas_bp.route("/<int:matricula_id>", methods=["GET"])
def obtener_matricula(matricula_id):
    iniciar_medicion()
    registrar_log("matriculas", "INFO", f"=== INICIO: Obtener matrícula ID={matricula_id} ===")

    conn = get_connection()
    if conn is None:
        registrar_log("matriculas", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de BD"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.*, 
                   CONCAT(a.nombre, ' ', a.apellido) as alumno,
                   c.nombre as curso
            FROM matriculas m
            INNER JOIN alumnos a ON m.id_alumno = a.id
            INNER JOIN cursos c ON m.id_curso = c.id
            WHERE m.id = %s
        """, (matricula_id,))
        matricula = cursor.fetchone()

        if matricula is None:
            registrar_log("matriculas", "WARN", f"Matrícula ID={matricula_id} no encontrada")
            finalizar_medicion()
            return jsonify({"error": "Matrícula no encontrada"}), 404

        registrar_log("matriculas", "INFO", f"Matrícula recuperada: ID={matricula_id}")
        registrar_log("matriculas", "INFO", f"=== FIN: Obtener matrícula ID={matricula_id} ===")
        finalizar_medicion()
        return jsonify(matricula), 200

    except Exception as e:
        registrar_log("matriculas", "ERROR", f"Excepción al obtener matrícula: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error interno"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# POST: CREAR MATRÍCULA
# ============================
@matriculas_bp.route("", methods=["POST"])
def crear_matricula():
    iniciar_medicion()
    registrar_log("matriculas", "INFO", "=== INICIO: Crear nueva matrícula ===")

    data = request.get_json()
    if not data:
        registrar_log("matriculas", "WARN", "Request sin datos JSON")
        finalizar_medicion()
        return jsonify({"error": "Datos inválidos"}), 400

    # Validar campos obligatorios
    if not data.get("id_alumno"):
        registrar_log("matriculas", "WARN", "Campo id_alumno faltante")
        finalizar_medicion()
        return jsonify({"error": "id_alumno es obligatorio"}), 400

    if not data.get("id_curso"):
        registrar_log("matriculas", "WARN", "Campo id_curso faltante")
        finalizar_medicion()
        return jsonify({"error": "id_curso es obligatorio"}), 400

    if not data.get("ciclo"):
        registrar_log("matriculas", "WARN", "Campo ciclo faltante")
        finalizar_medicion()
        return jsonify({"error": "ciclo es obligatorio"}), 400

    conn = get_connection()
    if conn is None:
        registrar_log("matriculas", "ERROR", "Error al conectar a BD")
        finalizar_medicion()
        return jsonify({"error": "Error al conectar BD"}), 500

    try:
        cursor = conn.cursor()

        # Verificar que el alumno existe
        cursor.execute("SELECT id FROM alumnos WHERE id = %s AND activo = 1", (data["id_alumno"],))
        if cursor.fetchone() is None:
            registrar_log("matriculas", "WARN", f"Alumno ID={data['id_alumno']} no existe o está inactivo")
            finalizar_medicion()
            return jsonify({"error": "El alumno no existe"}), 404

        # Verificar que el curso existe
        cursor.execute("SELECT id FROM cursos WHERE id = %s AND activo = 1", (data["id_curso"],))
        if cursor.fetchone() is None:
            registrar_log("matriculas", "WARN", f"Curso ID={data['id_curso']} no existe o está inactivo")
            finalizar_medicion()
            return jsonify({"error": "El curso no existe"}), 404

        # Verificar que no esté matriculado en el mismo curso y ciclo
        cursor.execute("""
            SELECT id FROM matriculas 
            WHERE id_alumno = %s AND id_curso = %s AND ciclo = %s
        """, (data["id_alumno"], data["id_curso"], data["ciclo"]))
        
        if cursor.fetchone() is not None:
            registrar_log("matriculas", "WARN", f"Matrícula duplicada - Alumno={data['id_alumno']}, Curso={data['id_curso']}, Ciclo={data['ciclo']}")
            finalizar_medicion()
            return jsonify({"error": "El alumno ya está matriculado en este curso para este ciclo"}), 400

        # Insertar matrícula
        cursor.execute("""
            INSERT INTO matriculas(id_alumno, id_curso, ciclo, estado)
            VALUES (%s, %s, %s, 'MATRICULADO')
        """, (data["id_alumno"], data["id_curso"], data["ciclo"]))
        conn.commit()

        nuevo_id = cursor.lastrowid
        registrar_log("matriculas", "INFO", f"Matrícula creada - ID={nuevo_id}, Alumno={data['id_alumno']}, Curso={data['id_curso']}, Ciclo={data['ciclo']}")
        registrar_log("matriculas", "INFO", "=== FIN: Crear nueva matrícula ===")
        finalizar_medicion()

        return jsonify({"mensaje": "Matrícula creada exitosamente", "id": nuevo_id}), 201

    except Exception as e:
        registrar_log("matriculas", "ERROR", f"Excepción al crear matrícula: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error en BD"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# DELETE: ELIMINAR MATRÍCULA
# ============================
@matriculas_bp.route("/<int:matricula_id>", methods=["DELETE"])
def eliminar_matricula(matricula_id):
    iniciar_medicion()
    registrar_log("matriculas", "INFO", f"=== INICIO: Eliminar matrícula ID={matricula_id} ===")

    conn = get_connection()
    if conn is None:
        registrar_log("matriculas", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error BD"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matriculas WHERE id = %s", (matricula_id,))
        conn.commit()

        if cursor.rowcount == 0:
            registrar_log("matriculas", "WARN", f"Matrícula ID={matricula_id} no encontrada")
            finalizar_medicion()
            return jsonify({"error": "Matrícula no encontrada"}), 404

        registrar_log("matriculas", "INFO", f"Matrícula eliminada - ID={matricula_id}")
        registrar_log("matriculas", "INFO", f"=== FIN: Eliminar matrícula ID={matricula_id} ===")
        finalizar_medicion()

        return jsonify({"mensaje": "Matrícula eliminada correctamente"}), 200

    except Exception as e:
        registrar_log("matriculas", "ERROR", f"Excepción al eliminar matrícula: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error al eliminar matrícula"}), 500

    finally:
        cursor.close()
        conn.close()