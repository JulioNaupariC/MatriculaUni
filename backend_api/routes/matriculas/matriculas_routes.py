from flask import Blueprint, request, jsonify
from db import get_connection
from utils.logger import registrar_log, iniciar_medicion, finalizar_medicion

matriculas_bp = Blueprint("matriculas_bp", __name__, url_prefix="/api/matriculas")

# ============================
# SERVICIOS (Lógica)
# ============================
def servicio_rendimiento_alumno(alumno_id, filtro="TODOS"):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        ciclos_filtrar = []
        params = [alumno_id]
        
        if filtro != "TODOS":
            limit = 1 if filtro == "ULTIMO" else 3
            cursor.execute("SELECT DISTINCT ciclo FROM matriculas WHERE id_alumno=%s ORDER BY ciclo DESC LIMIT %s", (alumno_id, limit))
            ciclos_filtrar = [r['ciclo'] for r in cursor.fetchall()]
            if not ciclos_filtrar: return {}

        query = """
            SELECT m.ciclo, c.codigo, c.nombre as curso, c.creditos, e.nota,
                   CASE WHEN e.nota IS NULL THEN 'SIN NOTA' WHEN e.aprobado=1 THEN 'APROBADO' ELSE 'DESAPROBADO' END as estado_curso,
                   e.fecha_evaluacion
            FROM matriculas m
            JOIN cursos c ON m.id_curso = c.id
            LEFT JOIN evaluaciones e ON m.id = e.id_matricula
            WHERE m.id_alumno = %s
        """
        if ciclos_filtrar:
            placeholders = ','.join(['%s']*len(ciclos_filtrar))
            query += f" AND m.ciclo IN ({placeholders})"
            params.extend(ciclos_filtrar)
        
        query += " ORDER BY m.ciclo DESC, c.codigo ASC"
        cursor.execute(query, tuple(params))
        
        data = cursor.fetchall()
        agrupado = {}
        for row in data:
            c = row['ciclo']
            if c not in agrupado: agrupado[c] = []
            agrupado[c].append(row)
        return agrupado
    finally:
        if conn: conn.close()

def servicio_reporte_alumnos_ciclo():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT m.ciclo, COUNT(DISTINCT m.id_alumno) as total_alumnos, COUNT(m.id) as total_matriculas FROM matriculas m GROUP BY m.ciclo ORDER BY m.ciclo")
        return cursor.fetchall()
    finally:
        if conn: conn.close()

# ============================
# RUTAS CRUD
# ============================
@matriculas_bp.route("", methods=["GET"])
def listar_matriculas():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.id, m.id_alumno, m.id_curso, m.ciclo, m.estado,
                   CONCAT(a.nombre, ' ', a.apellido) as alumno, c.nombre as curso
            FROM matriculas m
            JOIN alumnos a ON m.id_alumno = a.id
            JOIN cursos c ON m.id_curso = c.id
            ORDER BY m.fecha_matricula DESC
        """)
        return jsonify(cursor.fetchall()), 200
    finally:
        if conn: conn.close()

@matriculas_bp.route("/<int:id>", methods=["GET"])
def obtener_matricula(id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM matriculas WHERE id=%s", (id,))
        row = cursor.fetchone()
        return jsonify(row) if row else (jsonify({"error": "No encontrado"}), 404)
    finally:
        if conn: conn.close()

@matriculas_bp.route("", methods=["POST"])
def crear_matricula():
    data = request.get_json()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Validar duplicado exacto
        cursor.execute("SELECT id FROM matriculas WHERE id_alumno=%s AND id_curso=%s AND ciclo=%s", 
                      (data['id_alumno'], data['id_curso'], data['ciclo']))
        if cursor.fetchone(): return jsonify({"error": "El alumno ya está en este curso"}), 400
        
        cursor.execute("INSERT INTO matriculas(id_alumno, id_curso, ciclo, estado) VALUES (%s,%s,%s,'MATRICULADO')",
                       (data['id_alumno'], data['id_curso'], data['ciclo']))
        conn.commit()
        return jsonify({"mensaje": "Matrícula creada"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@matriculas_bp.route("/<int:id>", methods=["PUT"])
def actualizar_matricula(id):
    data = request.get_json()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Permitimos actualizar Curso y Ciclo (Si hubo error al matricular)
        cursor.execute("""
            UPDATE matriculas 
            SET id_curso=%s, ciclo=%s
            WHERE id=%s
        """, (data['id_curso'], data['ciclo'], id))
        
        if cursor.rowcount == 0:
            # A veces rowcount es 0 si los datos son iguales, pero verificamos existencia
            cursor.execute("SELECT id FROM matriculas WHERE id=%s", (id,))
            if not cursor.fetchone():
                return jsonify({"error": "No encontrado"}), 404

        conn.commit()
        return jsonify({"mensaje": "Actualizado correctamente"}), 200
    except Exception as e:
        registrar_log("matriculas", "ERROR", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@matriculas_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_matricula(id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matriculas WHERE id=%s", (id,))
        conn.commit()
        return jsonify({"mensaje": "Eliminado"}), 200
    finally:
        if conn: conn.close()