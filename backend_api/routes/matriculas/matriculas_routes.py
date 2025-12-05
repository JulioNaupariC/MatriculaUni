from flask import Blueprint, request, jsonify
from db import get_connection
import requests

matriculas_bp = Blueprint("matriculas_bp", __name__, url_prefix="/api/matriculas")

# ============================
# FUNCIÓN AUXILIAR: VALIDAR CON SERVICIOS
# ============================
def validar_con_servicio(tipo, id_entidad, transaction_id):
    """
    Llama al servicio de validación en vez de consultar BD directa
    tipo: 'alumno' o 'curso'
    id_entidad: ID del alumno o curso
    transaction_id: ID para rastrear la transacción
    """
    try:
        url = f"http://127.0.0.1:5000/api/{tipo}s/validar/{id_entidad}"
        headers = {"X-Transaction-ID": transaction_id}
        
        respuesta = requests.get(url, headers=headers, timeout=5)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            return {"valido": True, "datos": datos}
        elif respuesta.status_code == 404:
            return {"valido": False, "mensaje": f"{tipo.capitalize()} no encontrado"}
        else:
            return {"valido": False, "mensaje": f"Error al validar {tipo}"}
            
    except requests.exceptions.Timeout:
        return {"valido": False, "mensaje": f"Timeout al validar {tipo}"}
    except Exception as e:
        return {"valido": False, "mensaje": f"Error de conexión: {str(e)}"}

# ============================
# SERVICIOS PARA REPORTES
# ============================
def servicio_rendimiento_alumno(alumno_id, filtro="TODOS"):
    """
    Retorna el historial académico del alumno agrupado por ciclo_matricula
    Incluye información de ciclo_original para detectar arrastres
    filtro: TODOS | ULTIMO | ULTIMOS_3
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        ciclos_filtrar = []
        params = [alumno_id]
        
        if filtro != "TODOS":
            limit = 1 if filtro == "ULTIMO" else 3
            cursor.execute("""
                SELECT DISTINCT ciclo_matricula 
                FROM matriculas 
                WHERE id_alumno=%s 
                ORDER BY ciclo_matricula DESC 
                LIMIT %s
            """, (alumno_id, limit))
            ciclos_filtrar = [r['ciclo_matricula'] for r in cursor.fetchall()]
            if not ciclos_filtrar: 
                return {}

        query = """
            SELECT 
                m.ciclo_matricula as ciclo,
                m.ciclo_original,
                c.codigo, 
                c.nombre as curso, 
                c.creditos,
                c.ciclo as ciclo_curso,
                m.intento,
                e.nota,
                CASE 
                    WHEN e.nota IS NULL THEN 'SIN NOTA' 
                    WHEN e.aprobado=1 THEN 'APROBADO' 
                    ELSE 'DESAPROBADO' 
                END as estado_curso,
                e.fecha_evaluacion
            FROM matriculas m
            JOIN cursos c ON m.id_curso = c.id
            LEFT JOIN evaluaciones e ON m.id = e.id_matricula
            WHERE m.id_alumno = %s
        """
        
        if ciclos_filtrar:
            placeholders = ','.join(['%s']*len(ciclos_filtrar))
            query += f" AND m.ciclo_matricula IN ({placeholders})"
            params.extend(ciclos_filtrar)
        
        query += " ORDER BY m.ciclo_matricula DESC, c.codigo ASC"
        cursor.execute(query, tuple(params))
        
        data = cursor.fetchall()
        agrupado = {}
        for row in data:
            c = row['ciclo']
            if c not in agrupado: 
                agrupado[c] = []
            agrupado[c].append(row)
        return agrupado
    finally:
        if conn: conn.close()

def servicio_reporte_alumnos_ciclo():
    """
    Retorna cantidad de alumnos y matrículas por ciclo_matricula
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.ciclo_matricula as ciclo, 
                   COUNT(DISTINCT m.id_alumno) as total_alumnos, 
                   COUNT(m.id) as total_matriculas 
            FROM matriculas m 
            GROUP BY m.ciclo_matricula 
            ORDER BY m.ciclo_matricula
        """)
        return cursor.fetchall()
    finally:
        if conn: conn.close()

# ============================
# LISTAR MATRÍCULAS
# ============================
@matriculas_bp.route("", methods=["GET"])
def listar_matriculas():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.id, m.id_alumno, m.id_curso, 
                   m.ciclo_original, m.ciclo_matricula, m.estado, m.intento,
                   CONCAT(a.nombre, ' ', a.apellido) as alumno, 
                   c.nombre as curso,
                   c.codigo
            FROM matriculas m
            JOIN alumnos a ON m.id_alumno = a.id
            JOIN cursos c ON m.id_curso = c.id
            ORDER BY m.fecha_matricula DESC
        """)
        return jsonify(cursor.fetchall()), 200
    finally:
        if conn: conn.close()

# ============================
# OBTENER UNA MATRÍCULA
# ============================
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

# ============================
# OBTENER CURSOS DISPONIBLES PARA MATRÍCULA
# ============================
@matriculas_bp.route("/cursos-disponibles/<int:alumno_id>", methods=["GET"])
def obtener_cursos_disponibles(alumno_id):
    """
    Retorna:
    - Cursos JALADOS (obligatorios)
    - Cursos DISPONIBLES del ciclo actual (opcionales)
    - Validaciones
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Validar alumno con servicio
        from utils.logger import generar_transaction_id
        transaction_id = generar_transaction_id()
        validacion = validar_con_servicio("alumno", alumno_id, transaction_id)

        if not validacion["valido"]:
            return jsonify({"error": validacion["mensaje"]}), 404

        ciclo_actual = validacion["datos"]["alumno"]["ciclo_actual"]
        
        # 2. Buscar cursos DESAPROBADOS (OBLIGATORIOS)
        cursor.execute("""
            SELECT DISTINCT
                c.id, c.codigo, c.nombre, c.creditos, c.ciclo as ciclo_original,
                m.intento as ultimo_intento,
                e.nota as ultima_nota
            FROM matriculas m
            JOIN cursos c ON m.id_curso = c.id
            JOIN evaluaciones e ON m.id = e.id_matricula
            WHERE m.id_alumno = %s 
              AND e.aprobado = 0
              AND m.id NOT IN (
                  SELECT m2.id FROM matriculas m2
                  JOIN evaluaciones e2 ON m2.id = e2.id_matricula
                  WHERE m2.id_alumno = %s 
                    AND m2.id_curso = c.id
                    AND e2.aprobado = 1
              )
            ORDER BY c.ciclo, c.codigo
        """, (alumno_id, alumno_id))
        
        cursos_jalados = cursor.fetchall()
        
        # 3. Contar cuántos cursos jalados hay
        total_jalados = len(cursos_jalados)
        cursos_disponibles_max = 6 - total_jalados
        
        # 4. Obtener cursos del ciclo actual que NO ha llevado o que aprobó
        cursor.execute("""
            SELECT c.id, c.codigo, c.nombre, c.creditos, c.ciclo as ciclo_original
            FROM cursos c
            WHERE c.ciclo = %s 
              AND c.activo = 1
              AND c.id NOT IN (
                  SELECT m.id_curso 
                  FROM matriculas m
                  WHERE m.id_alumno = %s 
                    AND m.estado = 'MATRICULADO'
              )
            ORDER BY c.codigo
        """, (ciclo_actual, alumno_id))
        
        cursos_disponibles = cursor.fetchall()
        
        # 5. Validar si puede matricularse
        puede_matricularse = True
        mensaje_validacion = ""
        
        if total_jalados >= 6:
            puede_matricularse = False
            mensaje_validacion = f"El alumno tiene {total_jalados} cursos desaprobados. Debe repetir algunos antes de avanzar."
        
        return jsonify({
            "ciclo_actual": ciclo_actual,
            "cursos_jalados": cursos_jalados,
            "total_jalados": total_jalados,
            "cursos_disponibles": cursos_disponibles,
            "cursos_disponibles_max": cursos_disponibles_max,
            "puede_matricularse": puede_matricularse,
            "mensaje_validacion": mensaje_validacion
        }), 200
        
    finally:
        if conn: conn.close()

# ============================
# CREAR MATRÍCULA FLEXIBLE
# ============================
@matriculas_bp.route("/flexible", methods=["POST"])
def crear_matricula_flexible():
    """
    Permite matricular al alumno en cursos específicos (máximo 6)
    Cursos jalados + cursos nuevos seleccionados
    """
    data = request.get_json()
    conn = get_connection()
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        alumno_id = data["id_alumno"]
        cursos_seleccionados = data["cursos"]  # Lista de IDs de cursos
        
        if not cursos_seleccionados or len(cursos_seleccionados) == 0:
            return jsonify({"error": "Debe seleccionar al menos un curso"}), 400
        
        if len(cursos_seleccionados) > 6:
            return jsonify({"error": "No puede matricularse en más de 6 cursos"}), 400
        
        # Validar alumno con servicio
        from utils.logger import generar_transaction_id, registrar_log, iniciar_medicion, finalizar_medicion
        
        transaction_id = generar_transaction_id()
        iniciar_medicion()
        registrar_log("matriculas", "INFO", f"=== INICIO: Crear matrícula flexible ===")
        registrar_log("matriculas", "INFO", f"Transaction ID generado: {transaction_id}")
        registrar_log("matriculas", "INFO", f"Alumno ID={alumno_id}, Cursos seleccionados: {len(cursos_seleccionados)}")
        
        validacion_alumno = validar_con_servicio("alumno", alumno_id, transaction_id)

        if not validacion_alumno["valido"]:
            registrar_log("matriculas", "ERROR", f"Alumno ID={alumno_id} no válido: {validacion_alumno['mensaje']}")
            finalizar_medicion()
            return jsonify({"error": validacion_alumno["mensaje"]}), 404

        ciclo_matricula = validacion_alumno["datos"]["alumno"]["ciclo_actual"]
        registrar_log("matriculas", "INFO", f"Alumno ID={alumno_id} validado. Ciclo actual: {ciclo_matricula}")
        
        # Insertar matrículas
        cursos_matriculados = []
        cursos_rechazados = []
        
        for curso_id in cursos_seleccionados:
            # Validar curso con servicio
            registrar_log("matriculas", "INFO", f"[{transaction_id}] Validando curso ID={curso_id}")
            validacion_curso = validar_con_servicio("curso", curso_id, transaction_id)
            
            if not validacion_curso["valido"]:
                cursos_rechazados.append({
                    "curso_id": curso_id,
                    "motivo": "Curso no encontrado"
                })
                registrar_log("matriculas", "WARN", f"Curso ID={curso_id} no encontrado")
                continue
            
            curso = validacion_curso["datos"]["curso"]
            ciclo_original = curso["ciclo"]
            registrar_log("matriculas", "INFO", f"[{transaction_id}] Curso {curso['codigo']} validado")
            
            # ===================================
            # VALIDACIÓN ANTI-DUPLICADO CRÍTICA
            # ===================================
            cursor.execute("""
                SELECT id FROM matriculas 
                WHERE id_alumno = %s 
                  AND id_curso = %s 
                  AND ciclo_matricula = %s
                  AND estado = 'MATRICULADO'
            """, (alumno_id, curso_id, ciclo_matricula))
            
            duplicado = cursor.fetchone()
            
            if duplicado:
                cursos_rechazados.append({
                    "curso_id": curso_id,
                    "codigo": curso["codigo"],
                    "nombre": curso["nombre"],
                    "motivo": "Ya está matriculado en este curso en el ciclo actual"
                })
                registrar_log("matriculas", "WARN", f"Curso {curso['codigo']} rechazado: ya matriculado")
                continue
            
            # Verificar si es repetición (obtener último intento)
            cursor.execute("""
                SELECT MAX(intento) as ultimo_intento
                FROM matriculas
                WHERE id_alumno = %s AND id_curso = %s
            """, (alumno_id, curso_id))
            
            resultado = cursor.fetchone()
            nuevo_intento = (resultado["ultimo_intento"] or 0) + 1
            
            # Insertar matrícula
            cursor.execute("""
                INSERT INTO matriculas (id_alumno, id_curso, ciclo_original, ciclo_matricula, intento, estado)
                VALUES (%s, %s, %s, %s, %s, 'MATRICULADO')
            """, (alumno_id, curso_id, ciclo_original, ciclo_matricula, nuevo_intento))
            
            cursos_matriculados.append({
                "codigo": curso["codigo"],
                "nombre": curso["nombre"],
                "ciclo_original": ciclo_original,
                "intento": nuevo_intento,
                "es_arrastre": ciclo_original != ciclo_matricula
            })
            
            registrar_log("matriculas", "INFO", f"Curso {curso['codigo']} matriculado - Intento {nuevo_intento}")
        
        conn.commit()
        
        registrar_log("matriculas", "INFO", f"✅ Matrícula completada: {len(cursos_matriculados)} cursos matriculados, {len(cursos_rechazados)} rechazados")
        registrar_log("matriculas", "INFO", f"=== FIN: Crear matrícula flexible ===")
        finalizar_medicion()
        
        respuesta = {
            "mensaje": f"✅ Matrícula procesada: {len(cursos_matriculados)} cursos matriculados",
            "ciclo_matricula": ciclo_matricula,
            "cursos_matriculados": cursos_matriculados
        }
        
        if cursos_rechazados:
            respuesta["advertencia"] = f"{len(cursos_rechazados)} cursos fueron rechazados"
            respuesta["cursos_rechazados"] = cursos_rechazados
        
        return jsonify(respuesta), 201
        
    except Exception as e:
        registrar_log("matriculas", "ERROR", f"Excepción en crear_matricula_flexible: {str(e)}")
        finalizar_medicion()
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# ============================
# ACTUALIZAR MATRÍCULA
# ============================
@matriculas_bp.route("/<int:id>", methods=["PUT"])
def actualizar_matricula(id):
    data = request.get_json()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE matriculas 
            SET estado=%s
            WHERE id=%s
        """, (data.get('estado', 'MATRICULADO'), id))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "No encontrado"}), 404

        conn.commit()
        return jsonify({"mensaje": "Actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# ============================
# ELIMINAR MATRÍCULA
# ============================
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