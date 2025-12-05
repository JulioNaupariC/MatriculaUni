from flask import Blueprint, request, jsonify
from db import get_connection
from utils.logger import generar_transaction_id, registrar_log, iniciar_medicion, finalizar_medicion
import requests

evaluaciones_bp = Blueprint("evaluaciones_bp", __name__, url_prefix="/api/evaluaciones")

# ============================
# FUNCIÓN AUXILIAR: VALIDAR MATRÍCULA CON SERVICIO
# ============================
def validar_matricula_con_servicio(id_matricula, transaction_id):
    """
    Llama al servicio de matrícula para validar que existe
    id_matricula: ID de la matrícula
    transaction_id: ID para rastrear la transacción
    """
    try:
        url = f"http://127.0.0.1:5000/api/matriculas/{id_matricula}"
        headers = {"X-Transaction-ID": transaction_id}
        
        respuesta = requests.get(url, headers=headers, timeout=5)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            return {"valido": True, "datos": datos}
        elif respuesta.status_code == 404:
            return {"valido": False, "mensaje": "Matrícula no encontrada"}
        else:
            return {"valido": False, "mensaje": "Error al validar matrícula"}
            
    except requests.exceptions.Timeout:
        return {"valido": False, "mensaje": "Timeout al validar matrícula"}
    except Exception as e:
        return {"valido": False, "mensaje": f"Error de conexión: {str(e)}"}

# ============================
# LISTAR EVALUACIONES
# ============================
@evaluaciones_bp.route("", methods=["GET"])
def listar():
    iniciar_medicion()
    registrar_log("evaluaciones", "INFO", "=== INICIO: Listar evaluaciones ===")
    
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, 
                   CONCAT(a.nombre,' ',a.apellido) as alumno, 
                   c.nombre as curso, 
                   c.codigo,
                   m.ciclo_original,
                   m.ciclo_matricula,
                   m.intento
            FROM evaluaciones e
            JOIN matriculas m ON e.id_matricula = m.id
            JOIN alumnos a ON m.id_alumno = a.id
            JOIN cursos c ON m.id_curso = c.id
            ORDER BY e.fecha_evaluacion DESC
        """)
        
        evaluaciones = cursor.fetchall()
        registrar_log("evaluaciones", "INFO", f"Evaluaciones recuperadas: {len(evaluaciones)} registros")
        registrar_log("evaluaciones", "INFO", "=== FIN: Listar evaluaciones ===")
        finalizar_medicion()
        
        return jsonify(evaluaciones)
    except Exception as e:
        registrar_log("evaluaciones", "ERROR", f"Error al listar evaluaciones: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# ============================
# LISTAR MATRÍCULAS PENDIENTES DE EVALUACIÓN
# ============================
@evaluaciones_bp.route("/pendientes", methods=["GET"])
def pendientes():
    iniciar_medicion()
    registrar_log("evaluaciones", "INFO", "=== INICIO: Listar matrículas pendientes ===")
    
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.id as id_matricula, 
                   CONCAT(a.nombre,' ',a.apellido) as alumno,
                   c.codigo,
                   c.nombre as curso, 
                   m.ciclo_original,
                   m.ciclo_matricula,
                   m.intento
            FROM matriculas m
            JOIN alumnos a ON m.id_alumno = a.id
            JOIN cursos c ON m.id_curso = c.id
            LEFT JOIN evaluaciones e ON m.id = e.id_matricula
            WHERE e.id IS NULL AND m.estado = 'MATRICULADO'
            ORDER BY m.ciclo_matricula, a.apellido
        """)
        
        pendientes = cursor.fetchall()
        registrar_log("evaluaciones", "INFO", f"Matrículas pendientes: {len(pendientes)} registros")
        registrar_log("evaluaciones", "INFO", "=== FIN: Listar matrículas pendientes ===")
        finalizar_medicion()
        
        return jsonify(pendientes)
    except Exception as e:
        registrar_log("evaluaciones", "ERROR", f"Error al listar pendientes: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# ============================
# OBTENER EVALUACIÓN POR ID
# ============================
@evaluaciones_bp.route("/<int:id>", methods=["GET"])
def obtener(id):
    """Obtener una evaluación específica por ID"""
    iniciar_medicion()
    registrar_log("evaluaciones", "INFO", f"=== INICIO: Obtener evaluación ID={id} ===")
    
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, 
                   CONCAT(a.nombre,' ',a.apellido) as alumno, 
                   c.nombre as curso, 
                   c.codigo,
                   m.ciclo_original,
                   m.ciclo_matricula
            FROM evaluaciones e
            JOIN matriculas m ON e.id_matricula = m.id
            JOIN alumnos a ON m.id_alumno = a.id
            JOIN cursos c ON m.id_curso = c.id
            WHERE e.id = %s
        """, (id,))
        
        evaluacion = cursor.fetchone()
        
        if not evaluacion:
            registrar_log("evaluaciones", "WARN", f"Evaluación ID={id} no encontrada")
            finalizar_medicion()
            return jsonify({"error": "Evaluación no encontrada"}), 404
        
        registrar_log("evaluaciones", "INFO", f"Evaluación ID={id} recuperada exitosamente")
        registrar_log("evaluaciones", "INFO", f"=== FIN: Obtener evaluación ID={id} ===")
        finalizar_medicion()
        
        return jsonify(evaluacion), 200
    except Exception as e:
        registrar_log("evaluaciones", "ERROR", f"Error al obtener evaluación: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# ============================
# CREAR EVALUACIÓN
# ============================
@evaluaciones_bp.route("", methods=["POST"])
def crear():
    data = request.get_json()
    
    # Validar datos de entrada
    if not data or 'id_matricula' not in data or 'nota' not in data:
        return jsonify({"error": "Faltan campos obligatorios: id_matricula, nota"}), 400
    
    try:
        nota = float(data['nota'])
    except ValueError:
        return jsonify({"error": "La nota debe ser un número válido"}), 400
    
    if nota < 0 or nota > 20:
        return jsonify({"error": "La nota debe estar entre 0 y 20"}), 400
    
    # Generar Transaction ID y iniciar logging
    transaction_id = generar_transaction_id()
    iniciar_medicion()
    registrar_log("evaluaciones", "INFO", "=== INICIO: Crear evaluación ===")
    registrar_log("evaluaciones", "INFO", f"Transaction ID generado: {transaction_id}")
    registrar_log("evaluaciones", "INFO", f"Matrícula ID={data['id_matricula']}, Nota={nota}")
    
    # Validar matrícula con servicio
    registrar_log("evaluaciones", "INFO", f"[{transaction_id}] Validando matrícula ID={data['id_matricula']}")
    validacion = validar_matricula_con_servicio(data['id_matricula'], transaction_id)
    
    if not validacion["valido"]:
        registrar_log("evaluaciones", "ERROR", f"Matrícula ID={data['id_matricula']} no válida: {validacion['mensaje']}")
        finalizar_medicion()
        return jsonify({"error": validacion["mensaje"]}), 404
    
    registrar_log("evaluaciones", "INFO", f"[{transaction_id}] Matrícula ID={data['id_matricula']} validada exitosamente")
    
    estado = "APROBADO" if nota >= 10.5 else "DESAPROBADO"
    registrar_log("evaluaciones", "INFO", f"Estado calculado: {estado}")
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Verificar si ya existe evaluación para esa matrícula
        cursor.execute("SELECT id FROM evaluaciones WHERE id_matricula=%s", (data['id_matricula'],))
        if cursor.fetchone():
            registrar_log("evaluaciones", "WARN", f"Matrícula ID={data['id_matricula']} ya tiene evaluación")
            finalizar_medicion()
            return jsonify({"error": "Esta matrícula ya tiene nota registrada"}), 400

        # Insertar evaluación
        cursor.execute("INSERT INTO evaluaciones(id_matricula, nota, aprobado) VALUES (%s, %s, %s)",
                       (data['id_matricula'], nota, 1 if nota>=10.5 else 0))
        
        # Actualizar estado de matrícula
        cursor.execute("UPDATE matriculas SET estado=%s WHERE id=%s", (estado, data['id_matricula']))
        
        conn.commit()
        
        registrar_log("evaluaciones", "INFO", f"✅ Evaluación creada: Matrícula={data['id_matricula']}, Nota={nota}, Estado={estado}")
        registrar_log("evaluaciones", "INFO", "=== FIN: Crear evaluación ===")
        finalizar_medicion()
        
        return jsonify({"mensaje": "Evaluación guardada correctamente"}), 201
        
    except Exception as e:
        conn.rollback()
        registrar_log("evaluaciones", "ERROR", f"Excepción al crear evaluación: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": f"Error al guardar evaluación: {str(e)}"}), 500
    finally:
        if conn: conn.close()

# ============================
# ACTUALIZAR EVALUACIÓN
# ============================
@evaluaciones_bp.route("/<int:id>", methods=["PUT"])
def editar(id):
    data = request.get_json()
    
    if not data or 'nota' not in data:
        return jsonify({"error": "Falta el campo 'nota'"}), 400
    
    try:
        nota = float(data['nota'])
    except ValueError:
        return jsonify({"error": "La nota debe ser un número válido"}), 400
    
    if nota < 0 or nota > 20:
        return jsonify({"error": "La nota debe estar entre 0 y 20"}), 400
    
    iniciar_medicion()
    registrar_log("evaluaciones", "INFO", f"=== INICIO: Actualizar evaluación ID={id} ===")
    registrar_log("evaluaciones", "INFO", f"Nueva nota={nota}")
    
    estado = "APROBADO" if nota >= 10.5 else "DESAPROBADO"
    aprobado = 1 if nota >= 10.5 else 0
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Obtener id_matricula de esta evaluación
        cursor.execute("SELECT id_matricula FROM evaluaciones WHERE id=%s", (id,))
        row = cursor.fetchone()
        
        if not row:
            registrar_log("evaluaciones", "WARN", f"Evaluación ID={id} no encontrada")
            finalizar_medicion()
            return jsonify({"error": "Evaluación no encontrada"}), 404
        
        id_matricula = row[0]
        
        # Actualizar Evaluación
        cursor.execute(
            "UPDATE evaluaciones SET nota=%s, aprobado=%s WHERE id=%s",
            (nota, aprobado, id)
        )
        
        # Actualizar Estado de Matrícula
        cursor.execute(
            "UPDATE matriculas SET estado=%s WHERE id=%s", 
            (estado, id_matricula)
        )
        
        conn.commit()
        
        registrar_log("evaluaciones", "INFO", f"✅ Evaluación ID={id} actualizada: Nota={nota}, Estado={estado}")
        registrar_log("evaluaciones", "INFO", f"=== FIN: Actualizar evaluación ID={id} ===")
        finalizar_medicion()
        
        return jsonify({"mensaje": "Nota actualizada correctamente"}), 200
        
    except Exception as e:
        conn.rollback()
        registrar_log("evaluaciones", "ERROR", f"Error al actualizar evaluación: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": f"Error al actualizar evaluación: {str(e)}"}), 500
    finally:
        if conn: conn.close()

# ============================
# ELIMINAR EVALUACIÓN
# ============================
@evaluaciones_bp.route("/<int:id>", methods=["DELETE"])
def eliminar(id):
    iniciar_medicion()
    registrar_log("evaluaciones", "INFO", f"=== INICIO: Eliminar evaluación ID={id} ===")
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_matricula FROM evaluaciones WHERE id=%s", (id,))
        row = cursor.fetchone()
        
        if not row:
            registrar_log("evaluaciones", "WARN", f"Evaluación ID={id} no encontrada")
            finalizar_medicion()
            return jsonify({"error": "Evaluación no encontrada"}), 404
        
        id_matricula = row[0]
        
        # Restaurar estado de matrícula
        cursor.execute("UPDATE matriculas SET estado='MATRICULADO' WHERE id=%s", (id_matricula,))
        
        # Eliminar evaluación
        cursor.execute("DELETE FROM evaluaciones WHERE id=%s", (id,))
        
        conn.commit()
        
        registrar_log("evaluaciones", "INFO", f"✅ Evaluación ID={id} eliminada, matrícula ID={id_matricula} restaurada")
        registrar_log("evaluaciones", "INFO", f"=== FIN: Eliminar evaluación ID={id} ===")
        finalizar_medicion()
        
        return jsonify({"mensaje": "Evaluación eliminada correctamente"}), 200
        
    except Exception as e:
        conn.rollback()
        registrar_log("evaluaciones", "ERROR", f"Error al eliminar evaluación: {str(e)}")
        finalizar_medicion()
        return jsonify({"error": f"Error al eliminar evaluación: {str(e)}"}), 500
    finally:
        if conn: conn.close()