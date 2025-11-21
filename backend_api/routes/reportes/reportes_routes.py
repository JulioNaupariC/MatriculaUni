from flask import Blueprint, request, jsonify
from db import get_connection
from utils.logger import registrar_log, iniciar_medicion, finalizar_medicion

reportes_bp = Blueprint("reportes_bp", __name__, url_prefix="/api/reportes")


# ============================
# REPORTE 1: ALUMNOS POR CICLO
# ============================
@reportes_bp.route("/alumnos_ciclo", methods=["GET"])
def alumnos_por_ciclo():
    iniciar_medicion()
    registrar_log("reportes", "INFO", "=== INICIO: Reporte alumnos por ciclo ===")

    conn = get_connection()
    if conn is None:
        registrar_log("reportes", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de conexión"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.ciclo,
                   COUNT(DISTINCT m.id_alumno) as total_alumnos,
                   COUNT(m.id) as total_matriculas
            FROM matriculas m
            INNER JOIN alumnos a ON m.id_alumno = a.id
            GROUP BY m.ciclo
            ORDER BY m.ciclo
        """)
        data = cursor.fetchall()

        registrar_log("reportes", "INFO", f"Reporte generado: {len(data)} ciclos con alumnos")
        registrar_log("reportes", "INFO", "=== FIN: Reporte alumnos por ciclo ===")
        finalizar_medicion()
        return jsonify(data), 200

    except Exception as e:
        registrar_log("reportes", "ERROR", f"Excepción en reporte: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error al generar reporte"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# REPORTE 2: CURSOS MÁS DEMANDADOS
# ============================
@reportes_bp.route("/cursos_demandados", methods=["GET"])
def cursos_mas_demandados():
    iniciar_medicion()
    registrar_log("reportes", "INFO", "=== INICIO: Reporte cursos más demandados ===")

    conn = get_connection()
    if conn is None:
        registrar_log("reportes", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de conexión"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.codigo,
                   c.nombre as curso,
                   c.ciclo,
                   c.creditos,
                   COUNT(m.id) as total_matriculas,
                   COUNT(DISTINCT m.id_alumno) as alumnos_unicos
            FROM cursos c
            LEFT JOIN matriculas m ON c.id = m.id_curso
            WHERE c.activo = 1
            GROUP BY c.id, c.codigo, c.nombre, c.ciclo, c.creditos
            HAVING total_matriculas > 0
            ORDER BY total_matriculas DESC, c.nombre
        """)
        data = cursor.fetchall()

        registrar_log("reportes", "INFO", f"Reporte generado: {len(data)} cursos con matrículas")
        registrar_log("reportes", "INFO", "=== FIN: Reporte cursos más demandados ===")
        finalizar_medicion()
        return jsonify(data), 200

    except Exception as e:
        registrar_log("reportes", "ERROR", f"Excepción en reporte: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error al generar reporte"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# REPORTE 3: RENDIMIENTO ACADÉMICO
# ============================
@reportes_bp.route("/rendimiento", methods=["GET"])
def rendimiento_academico():
    iniciar_medicion()
    registrar_log("reportes", "INFO", "=== INICIO: Reporte rendimiento académico ===")

    conn = get_connection()
    if conn is None:
        registrar_log("reportes", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de conexión"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_evaluaciones,
                AVG(nota) as promedio_general,
                MAX(nota) as nota_maxima,
                MIN(nota) as nota_minima,
                SUM(CASE WHEN aprobado = 1 THEN 1 ELSE 0 END) as total_aprobados,
                SUM(CASE WHEN aprobado = 0 THEN 1 ELSE 0 END) as total_desaprobados,
                ROUND((SUM(CASE WHEN aprobado = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as porcentaje_aprobacion
            FROM evaluaciones
        """)
        estadisticas = cursor.fetchone()

        # Rendimiento por curso
        cursor.execute("""
            SELECT c.codigo,
                   c.nombre as curso,
                   COUNT(e.id) as evaluaciones,
                   AVG(e.nota) as promedio_nota,
                   SUM(CASE WHEN e.aprobado = 1 THEN 1 ELSE 0 END) as aprobados,
                   SUM(CASE WHEN e.aprobado = 0 THEN 1 ELSE 0 END) as desaprobados,
                   ROUND((SUM(CASE WHEN e.aprobado = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(e.id)), 2) as porcentaje_aprobacion
            FROM cursos c
            INNER JOIN matriculas m ON c.id = m.id_curso
            INNER JOIN evaluaciones e ON m.id = e.id_matricula
            GROUP BY c.id, c.codigo, c.nombre
            ORDER BY porcentaje_aprobacion DESC
        """)
        por_curso = cursor.fetchall()

        resultado = {
            "estadisticas_generales": estadisticas,
            "rendimiento_por_curso": por_curso
        }

        registrar_log("reportes", "INFO", f"Reporte generado: {len(por_curso)} cursos evaluados")
        registrar_log("reportes", "INFO", "=== FIN: Reporte rendimiento académico ===")
        finalizar_medicion()
        return jsonify(resultado), 200

    except Exception as e:
        registrar_log("reportes", "ERROR", f"Excepción en reporte: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error al generar reporte"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# NUEVO: NOTAS DE LOS 3 ÚLTIMOS CICLOS
# ============================
@reportes_bp.route("/notas_3_ultimos_ciclos", methods=["GET"])
def notas_3_ultimos_ciclos():
    iniciar_medicion()
    registrar_log("reportes", "INFO", "=== INICIO: Notas de 3 últimos ciclos ===")

    conn = get_connection()
    if conn is None:
        registrar_log("reportes", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de conexión"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Obtener los 3 últimos ciclos
        cursor.execute("""
            SELECT DISTINCT ciclo 
            FROM matriculas 
            ORDER BY ciclo DESC 
            LIMIT 3
        """)
        ultimos_ciclos = [row['ciclo'] for row in cursor.fetchall()]
        
        if not ultimos_ciclos:
            finalizar_medicion()
            return jsonify([]), 200
        
        # Obtener notas de esos ciclos
        placeholders = ','.join(['%s'] * len(ultimos_ciclos))
        cursor.execute(f"""
            SELECT m.ciclo,
                   CONCAT(a.nombre, ' ', a.apellido) as alumno,
                   c.codigo,
                   c.nombre as curso,
                   e.nota,
                   e.aprobado,
                   e.fecha_evaluacion
            FROM matriculas m
            INNER JOIN alumnos a ON m.id_alumno = a.id
            INNER JOIN cursos c ON m.id_curso = c.id
            LEFT JOIN evaluaciones e ON m.id = e.id_matricula
            WHERE m.ciclo IN ({placeholders})
            ORDER BY m.ciclo DESC, a.apellido, c.codigo
        """, tuple(ultimos_ciclos))
        
        data = cursor.fetchall()

        registrar_log("reportes", "INFO", f"Notas de 3 últimos ciclos: {len(data)} registros")
        registrar_log("reportes", "INFO", "=== FIN: Notas de 3 últimos ciclos ===")
        finalizar_medicion()
        return jsonify(data), 200

    except Exception as e:
        registrar_log("reportes", "ERROR", f"Excepción: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error al generar reporte"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# NUEVO: NOTAS DEL ÚLTIMO CICLO
# ============================
@reportes_bp.route("/notas_ultimo_ciclo", methods=["GET"])
def notas_ultimo_ciclo():
    iniciar_medicion()
    registrar_log("reportes", "INFO", "=== INICIO: Notas del último ciclo ===")

    conn = get_connection()
    if conn is None:
        registrar_log("reportes", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de conexión"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Obtener el último ciclo
        cursor.execute("""
            SELECT MAX(ciclo) as ultimo_ciclo 
            FROM matriculas
        """)
        result = cursor.fetchone()
        ultimo_ciclo = result['ultimo_ciclo']
        
        if not ultimo_ciclo:
            finalizar_medicion()
            return jsonify([]), 200
        
        # Obtener notas del último ciclo
        cursor.execute("""
            SELECT CONCAT(a.nombre, ' ', a.apellido) as alumno,
                   a.dni,
                   c.codigo,
                   c.nombre as curso,
                   c.creditos,
                   e.nota,
                   e.aprobado,
                   e.fecha_evaluacion
            FROM matriculas m
            INNER JOIN alumnos a ON m.id_alumno = a.id
            INNER JOIN cursos c ON m.id_curso = c.id
            LEFT JOIN evaluaciones e ON m.id = e.id_matricula
            WHERE m.ciclo = %s
            ORDER BY a.apellido, c.codigo
        """, (ultimo_ciclo,))
        
        data = cursor.fetchall()
        
        resultado = {
            "ciclo": ultimo_ciclo,
            "notas": data
        }

        registrar_log("reportes", "INFO", f"Notas del último ciclo ({ultimo_ciclo}): {len(data)} registros")
        registrar_log("reportes", "INFO", "=== FIN: Notas del último ciclo ===")
        finalizar_medicion()
        return jsonify(resultado), 200

    except Exception as e:
        registrar_log("reportes", "ERROR", f"Excepción: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error al generar reporte"}), 500

    finally:
        cursor.close()
        conn.close()


# ============================
# NUEVO: NOTAS POR CICLO (REPORTE GENERAL)
# ============================
@reportes_bp.route("/notas_por_ciclo", methods=["GET"])
def notas_por_ciclo():
    iniciar_medicion()
    registrar_log("reportes", "INFO", "=== INICIO: Notas por ciclo (general) ===")

    ciclo_param = request.args.get('ciclo')
    
    conn = get_connection()
    if conn is None:
        registrar_log("reportes", "ERROR", "Error de conexión a BD")
        finalizar_medicion()
        return jsonify({"error": "Error de conexión"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        if ciclo_param:
            # Notas de un ciclo específico
            cursor.execute("""
                SELECT CONCAT(a.nombre, ' ', a.apellido) as alumno,
                       c.codigo,
                       c.nombre as curso,
                       c.creditos,
                       e.nota,
                       CASE 
                           WHEN e.aprobado = 1 THEN 'APROBADO'
                           WHEN e.aprobado = 0 THEN 'DESAPROBADO'
                           ELSE 'SIN EVALUAR'
                       END as estado
                FROM matriculas m
                INNER JOIN alumnos a ON m.id_alumno = a.id
                INNER JOIN cursos c ON m.id_curso = c.id
                LEFT JOIN evaluaciones e ON m.id = e.id_matricula
                WHERE m.ciclo = %s
                ORDER BY a.apellido, c.codigo
            """, (ciclo_param,))
            data = cursor.fetchall()
            
            resultado = {
                "ciclo": int(ciclo_param),
                "total_registros": len(data),
                "notas": data
            }
        else:
            # Todos los ciclos con sus notas
            cursor.execute("""
                SELECT m.ciclo,
                       CONCAT(a.nombre, ' ', a.apellido) as alumno,
                       c.codigo,
                       c.nombre as curso,
                       c.creditos,
                       e.nota,
                       CASE 
                           WHEN e.aprobado = 1 THEN 'APROBADO'
                           WHEN e.aprobado = 0 THEN 'DESAPROBADO'
                           ELSE 'SIN EVALUAR'
                       END as estado
                FROM matriculas m
                INNER JOIN alumnos a ON m.id_alumno = a.id
                INNER JOIN cursos c ON m.id_curso = c.id
                LEFT JOIN evaluaciones e ON m.id = e.id_matricula
                ORDER BY m.ciclo, a.apellido, c.codigo
            """)
            data = cursor.fetchall()
            
            # Agrupar por ciclo
            por_ciclo = {}
            for row in data:
                ciclo = row['ciclo']
                if ciclo not in por_ciclo:
                    por_ciclo[ciclo] = []
                por_ciclo[ciclo].append(row)
            
            resultado = {
                "total_ciclos": len(por_ciclo),
                "total_registros": len(data),
                "por_ciclo": por_ciclo
            }

        registrar_log("reportes", "INFO", f"Reporte general generado: {len(data)} registros")
        registrar_log("reportes", "INFO", "=== FIN: Notas por ciclo (general) ===")
        finalizar_medicion()
        return jsonify(resultado), 200

    except Exception as e:
        registrar_log("reportes", "ERROR", f"Excepción: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": "Error al generar reporte"}), 500

    finally:
        cursor.close()
        conn.close()