from flask import Blueprint, request, jsonify
from db import get_connection

evaluaciones_bp = Blueprint("evaluaciones_bp", __name__, url_prefix="/api/evaluaciones")

@evaluaciones_bp.route("", methods=["GET"])
def listar():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, CONCAT(a.nombre,' ',a.apellido) as alumno, c.nombre as curso, m.ciclo
            FROM evaluaciones e
            JOIN matriculas m ON e.id_matricula = m.id
            JOIN alumnos a ON m.id_alumno = a.id
            JOIN cursos c ON m.id_curso = c.id
            ORDER BY e.fecha_evaluacion DESC
        """)
        return jsonify(cursor.fetchall())
    finally:
        if conn: conn.close()

@evaluaciones_bp.route("/pendientes", methods=["GET"])
def pendientes():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.id as id_matricula, CONCAT(a.nombre,' ',a.apellido) as alumno,
                   c.nombre as curso, m.ciclo
            FROM matriculas m
            JOIN alumnos a ON m.id_alumno = a.id
            JOIN cursos c ON m.id_curso = c.id
            LEFT JOIN evaluaciones e ON m.id = e.id_matricula
            WHERE e.id IS NULL
        """)
        return jsonify(cursor.fetchall())
    finally:
        if conn: conn.close()

@evaluaciones_bp.route("", methods=["POST"])
def crear():
    data = request.get_json()
    nota = float(data['nota'])
    estado = "APROBADO" if nota >= 10.5 else "DESAPROBADO"
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Verificar si ya existe evaluación para esa matrícula
        cursor.execute("SELECT id FROM evaluaciones WHERE id_matricula=%s", (data['id_matricula'],))
        if cursor.fetchone():
            return jsonify({"error": "Esta matrícula ya tiene nota"}), 400

        cursor.execute("INSERT INTO evaluaciones(id_matricula, nota, aprobado) VALUES (%s, %s, %s)",
                       (data['id_matricula'], nota, 1 if nota>=10.5 else 0))
        
        cursor.execute("UPDATE matriculas SET estado=%s WHERE id=%s", (estado, data['id_matricula']))
        conn.commit()
        return jsonify({"mensaje": "Guardado"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@evaluaciones_bp.route("/<int:id>", methods=["PUT"])
def editar(id):
    data = request.get_json()
    nota = float(data['nota'])
    estado = "APROBADO" if nota >= 10.5 else "DESAPROBADO"
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Obtener id_matricula de esta evaluación
        cursor.execute("SELECT id_matricula FROM evaluaciones WHERE id=%s", (id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"error": "Evaluación no encontrada"}), 404
        
        id_matricula = row[0]
        
        # 2. Actualizar Evaluación
        cursor.execute("UPDATE evaluaciones SET nota=%s, aprobado=%s WHERE id=%s",
                       (nota, 1 if nota>=10.5 else 0, id))
        
        # 3. Actualizar Estado de Matrícula
        cursor.execute("UPDATE matriculas SET estado=%s WHERE id=%s", (estado, id_matricula))
        
        conn.commit()
        return jsonify({"mensaje": "Nota actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@evaluaciones_bp.route("/<int:id>", methods=["DELETE"])
def eliminar(id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_matricula FROM evaluaciones WHERE id=%s", (id,))
        row = cursor.fetchone()
        
        if row:
            # Restaurar estado de matrícula
            cursor.execute("UPDATE matriculas SET estado='MATRICULADO' WHERE id=%s", (row[0],))
        
        cursor.execute("DELETE FROM evaluaciones WHERE id=%s", (id,))
        conn.commit()
        return jsonify({"mensaje": "Eliminado"}), 200
    finally:
        if conn: conn.close()