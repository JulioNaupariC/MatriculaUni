from flask import Blueprint, request, jsonify
from db import get_connection
from utils.logger import registrar_log, iniciar_medicion, finalizar_medicion

evaluaciones_bp = Blueprint("evaluaciones_bp", __name__, url_prefix="/api/evaluaciones")


# ============================
# GET: LISTAR TODAS LAS EVALUACIONES
# ============================
@evaluaciones_bp.route("", methods=["GET"])
def listar_evaluaciones():
    iniciar_medicion()
    registrar_log("evaluaciones", "INFO", "=== INICIO: Listar todas las evaluaciones ===")

    conn = get_connection()
    if conn is None:
        registrar_log("evaluaciones", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.id, e.id_matricula, e.nota, e.fecha_evaluacion, e.aprobado,
                   CONCAT(a.nombre, ' ', a.apellido) as alumno,
                   c.codigo as codigo_curso,
                   c.nombre as curso,
                   m.ciclo
            FROM evaluaciones e
            INNER JOIN matriculas m ON e.id_matricula = m.id
            INNER JOIN alumnos a ON m.id_alumno = a.id
            INNER JOIN cursos c ON m.id_curso = c.id
            ORDER BY e.fecha_evaluacion DESC
        """)
        data = cursor.fetchall()

        registrar_log("evaluaciones", "INFO", f"Evaluaciones recuperadas: {len(data)} registros")
        registrar_log("evaluaciones", "INFO", "=== FIN: Listar todas las evaluaciones ===")
        finalizar_medicion()
        return jsonify(data), 200

    except Exception as e:
        registrar_log("evaluaciones", "ERROR", f"Excepción al listar evaluaciones: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error interno al listar evaluaciones"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# GET: OBTENER EVALUACIÓN POR ID
# ============================
@evaluaciones_bp.route("/<int:evaluacion_id>", methods=["GET"])
def obtener_evaluacion(evaluacion_id):
    iniciar_medicion()
    registrar_log("evaluaciones", "INFO", f"=== INICIO: Obtener evaluación ID={evaluacion_id} ===")

    conn = get_connection()
    if conn is None:
        registrar_log("evaluaciones", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de BD"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, 
                   CONCAT(a.nombre, ' ', a.apellido) as alumno,
                   c.nombre as curso
            FROM evaluaciones e
            INNER JOIN matriculas m ON e.id_matricula = m.id
            INNER JOIN alumnos a ON m.id_alumno = a.id
            INNER JOIN cursos c ON m.id_curso = c.id
            WHERE e.id = %s
        """, (evaluacion_id,))
        evaluacion = cursor.fetchone()

        if evaluacion is None:
            registrar_log("evaluaciones", "WARN", f"Evaluación ID={evaluacion_id} no encontrada")
            finalizar_medicion()
            return jsonify({"error": "Evaluación no encontrada"}), 404

        registrar_log("evaluaciones", "INFO", f"Evaluación recuperada: ID={evaluacion_id}")
        registrar_log("evaluaciones", "INFO", f"=== FIN: Obtener evaluación ID={evaluacion_id} ===")
        finalizar_medicion()
        return jsonify(evaluacion), 200

    except Exception as e:
        registrar_log("evaluaciones", "ERROR", f"Excepción al obtener evaluación: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error interno"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# GET: LISTAR MATRÍCULAS SIN EVALUAR
# ============================
@evaluaciones_bp.route("/pendientes", methods=["GET"])
def listar_pendientes():
    iniciar_medicion()
    registrar_log("evaluaciones", "INFO", "=== INICIO: Listar matrículas sin evaluar ===")

    conn = get_connection()
    if conn is None:
        registrar_log("evaluaciones", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de BD"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.id as id_matricula,
                   m.id_alumno,
                   m.id_curso,
                   m.ciclo,
                   CONCAT(a.nombre, ' ', a.apellido) as alumno,
                   c.codigo as codigo_curso,
                   c.nombre as curso
            FROM matriculas m
            INNER JOIN alumnos a ON m.id_alumno = a.id
            INNER JOIN cursos c ON m.id_curso = c.id
            LEFT JOIN evaluaciones e ON m.id = e.id_matricula
            WHERE e.id IS NULL AND m.estado = 'MATRICULADO'
            ORDER BY m.fecha_matricula DESC
        """)
        data = cursor.fetchall()

        registrar_log("evaluaciones", "INFO", f"Matrículas pendientes de evaluación: {len(data)}")
        registrar_log("evaluaciones", "INFO", "=== FIN: Listar matrículas sin evaluar ===")
        finalizar_medicion()
        return jsonify(data), 200

    except Exception as e:
        registrar_log("evaluaciones", "ERROR", f"Excepción al listar pendientes: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error interno"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# POST: CREAR EVALUACIÓN
# ============================
@evaluaciones_bp.route("", methods=["POST"])
def crear_evaluacion():
    iniciar_medicion()
    registrar_log("evaluaciones", "INFO", "=== INICIO: Crear nueva evaluación ===")

    data = request.get_json()
    if not data:
        registrar_log("evaluaciones", "WARN", "Request sin datos JSON")
        finalizar_medicion()
        return jsonify({"error": "Datos inválidos"}), 400

    # Validar campos obligatorios
    if not data.get("id_matricula"):
        registrar_log("evaluaciones", "WARN", "Campo id_matricula faltante")
        finalizar_medicion()
        return jsonify({"error": "id_matricula es obligatorio"}), 400

    if data.get("nota") is None:
        registrar_log("evaluaciones", "WARN", "Campo nota faltante")
        finalizar_medicion()
        return jsonify({"error": "nota es obligatoria"}), 400

    nota = float(data["nota"])
    
    # Validar rango de nota
    if nota < 0 or nota > 20:
        registrar_log("evaluaciones", "WARN", f"Nota fuera de rango: {nota}")
        finalizar_medicion()
        return jsonify({"error": "La nota debe estar entre 0 y 20"}), 400

    conn = get_connection()
    if conn is None:
        registrar_log("evaluaciones", "ERROR", "Error al conectar a BD")
        finalizar_medicion()
        return jsonify({"error": "Error al conectar BD"}), 500

    try:
        cursor = conn.cursor()

        # Verificar que la matrícula existe
        cursor.execute("SELECT id, id_alumno, id_curso FROM matriculas WHERE id = %s", (data["id_matricula"],))
        matricula = cursor.fetchone()
        
        if matricula is None:
            registrar_log("evaluaciones", "WARN", f"Matrícula ID={data['id_matricula']} no existe")
            finalizar_medicion()
            return jsonify({"error": "La matrícula no existe"}), 404

        # Verificar que no tenga evaluación previa
        cursor.execute("SELECT id FROM evaluaciones WHERE id_matricula = %s", (data["id_matricula"],))
        if cursor.fetchone() is not None:
            registrar_log("evaluaciones", "WARN", f"Matrícula ID={data['id_matricula']} ya tiene evaluación")
            finalizar_medicion()
            return jsonify({"error": "Esta matrícula ya tiene una evaluación registrada"}), 400

        # Insertar evaluación
        cursor.execute("""
            INSERT INTO evaluaciones(id_matricula, nota)
            VALUES (%s, %s)
        """, (data["id_matricula"], nota))
        
        # Actualizar estado de matrícula según nota
        nuevo_estado = "APROBADO" if nota >= 10.5 else "DESAPROBADO"
        cursor.execute("""
            UPDATE matriculas SET estado = %s WHERE id = %s
        """, (nuevo_estado, data["id_matricula"]))
        
        conn.commit()

        nueva_id = cursor.lastrowid
        registrar_log("evaluaciones", "INFO", f"Evaluación creada - ID={nueva_id}, Matrícula={data['id_matricula']}, Nota={nota}, Estado={nuevo_estado}")
        registrar_log("evaluaciones", "INFO", "=== FIN: Crear nueva evaluación ===")
        finalizar_medicion()

        return jsonify({
            "mensaje": "Evaluación creada exitosamente",
            "id": nueva_id,
            "aprobado": nota >= 10.5,
            "estado": nuevo_estado
        }), 201

    except Exception as e:
        registrar_log("evaluaciones", "ERROR", f"Excepción al crear evaluación: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error en BD"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# DELETE: ELIMINAR EVALUACIÓN
# ============================
@evaluaciones_bp.route("/<int:evaluacion_id>", methods=["DELETE"])
def eliminar_evaluacion(evaluacion_id):
    iniciar_medicion()
    registrar_log("evaluaciones", "INFO", f"=== INICIO: Eliminar evaluación ID={evaluacion_id} ===")

    conn = get_connection()
    if conn is None:
        registrar_log("evaluaciones", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error BD"}), 500

    try:
        cursor = conn.cursor()
        
        # Obtener id_matricula antes de eliminar
        cursor.execute("SELECT id_matricula FROM evaluaciones WHERE id = %s", (evaluacion_id,))
        resultado = cursor.fetchone()
        
        if resultado is None:
            registrar_log("evaluaciones", "WARN", f"Evaluación ID={evaluacion_id} no encontrada")
            finalizar_medicion()
            return jsonify({"error": "Evaluación no encontrada"}), 404
        
        id_matricula = resultado[0]
        
        # Eliminar evaluación
        cursor.execute("DELETE FROM evaluaciones WHERE id = %s", (evaluacion_id,))
        
        # Volver matrícula a estado MATRICULADO
        cursor.execute("UPDATE matriculas SET estado = 'MATRICULADO' WHERE id = %s", (id_matricula,))
        
        conn.commit()

        registrar_log("evaluaciones", "INFO", f"Evaluación eliminada - ID={evaluacion_id}, Matrícula={id_matricula} regresó a MATRICULADO")
        registrar_log("evaluaciones", "INFO", f"=== FIN: Eliminar evaluación ID={evaluacion_id} ===")
        finalizar_medicion()

        return jsonify({"mensaje": "Evaluación eliminada correctamente"}), 200

    except Exception as e:
        registrar_log("evaluaciones", "ERROR", f"Excepción al eliminar evaluación: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error al eliminar evaluación"}), 500

    finally:
        cursor.close()
        conn.close()